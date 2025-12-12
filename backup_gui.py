#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import os
import zipfile
from datetime import datetime
import threading

# LOGS
def log_od(origens, destino):
    agora = datetime.now().strftime("%Y-%m-%d")
    agora_completo = datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_path= f"backup{agora}.log" 
    
    if os.path.exists(log_path):
        with open(log_path, "a") as file:
            for origem in origens:
                file.write(f"{origem} >> {destino} {agora_completo}\n")
    else:
         with open(log_path, "a") as file:
            for origem in origens:
                file.write(f"{origem} >> {destino} {agora_completo}\n")
        
def log_concluido():
    agora = datetime.now().strftime("%Y-%m-%d")
    agora_completo = datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_path= f"backup{agora}.log"
    
    # Append de concluído no arquivo de log
    if os.path.exists(log_path):
        with open(log_path, "a") as file:
            file.write(f"Backup concluído com sucesso {agora_completo}\n")

def log_erro():
    agora = datetime.now().strftime("%Y-%m-%d")
    agora_completo = datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_path= f"backup{agora}.log"

    if os.path.exists(log_path):
        with open(log_path, "a") as file:
            file.write(f"Erro ao fazer backup  {agora_completo}\n")


# FUNÇÕES AUXILIARES
def selecionar_diretorio(entry, callback=None):
    dialog = Gtk.FileChooserDialog(
        title="Selecione uma pasta",
        parent=window,
        action=Gtk.FileChooserAction.SELECT_FOLDER
    )

    dialog.add_buttons(
        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OPEN, Gtk.ResponseType.OK
    )

    resposta = dialog.run()

    if resposta == Gtk.ResponseType.OK:
        caminho = dialog.get_filename()

        # >>> Marcamos que o texto será alterado pelo código
        entry._mudou_por_codigo = True

        entry.set_text(caminho)

        if callback:
            callback()

    dialog.destroy()


def entry_detectou_origem(entry):
    if getattr(entry, "_mudou_por_codigo", False):
        entry._mudou_por_codigo = False
        return

    texto = entry.get_text().strip()
    if not texto:
        return

    if getattr(entry, "_ja_processou", False):
        return

    entry._ja_processou = True
    adicionar_campo_origem()




def adicionar_campo_origem():
    linha = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    entry = Gtk.Entry()
    btn = Gtk.Button(label="Selecionar")
    
    # Conecta por botão ou por box
    entry.connect("changed", entry_detectou_origem)
    btn.connect("clicked", lambda w: selecionar_diretorio(entry, adicionar_campo_origem))

    linha.pack_start(entry, True, True, 0)
    linha.pack_start(btn, False, False, 0)

    box_origens.pack_start(linha, False, False, 0)
    window.show_all()


# BACKUP EM THREAD

def fazer_backup_thread(origens, destino):
    try:
        arquivos_list = []

        # Contar todos os arquivos
        for origem in origens:
            if not os.path.isdir(origem):
                GLib.idle_add(lbl_status.set_text, f"Origem inválida: {origem}")
                return
            for raiz, dirs, files in os.walk(origem):
                for arquivo in files:
                    arquivos_list.append((origem, os.path.join(raiz, arquivo)))

        total_arquivos = len(arquivos_list)
        if total_arquivos == 0:
            GLib.idle_add(lbl_status.set_text, "Nenhum arquivo para backup.")
            return

        agora = datetime.now().strftime("%Y-%m-%d")
        zip_path = os.path.join(destino, f"backup{agora}.zip")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for i, (origem, caminho_abs) in enumerate(arquivos_list, 1):
                caminho_rel = os.path.relpath(caminho_abs, os.path.dirname(origem))
                zipf.write(caminho_abs, caminho_rel)
                
                # Atualiza progresso
                frac = i / total_arquivos
                GLib.idle_add(progressbar.set_fraction, frac)
                GLib.idle_add(progressbar.set_text, f"{int(frac*100)}%")

        GLib.idle_add(lbl_status.set_text, f"Backup concluído: {zip_path}")
        GLib.idle_add(progressbar.set_fraction, 0)
        GLib.idle_add(progressbar.set_text, "")
        log_concluido()

    except Exception as e:
        GLib.idle_add(lbl_status.set_text, f"Erro: {e}")
        log_erro()


def fazer_backup(widget):
    destino = entry_destino.get_text().strip()
    if not destino or not os.path.isdir(destino):
        lbl_status.set_text("Destino inválido.")
        return

    origens = []
    for linha in box_origens.get_children():
        if isinstance(linha, Gtk.Box):
            for item in linha.get_children():
                if isinstance(item, Gtk.Entry):
                    caminho = item.get_text().strip()
                    if caminho:
                        origens.append(caminho)
                        
    if not origens:
        lbl_status.set_text("Nenhuma pasta de origem selecionada.")
        return
    # Log origem-destino
    log_od(origens, destino)
    # Executa backup em thread para não travar a GUI
    threading.Thread(target=fazer_backup_thread, args=(origens, destino), daemon=True).start()

# INICIALIZAÇÃO DA GUI

builder = Gtk.Builder()
builder.add_from_file("main_window.ui")  # 

window = builder.get_object("MainWindow")
window.connect("destroy", Gtk.main_quit)

# Campo destino
entry_destino = builder.get_object("entry_destino")
btn_destino = builder.get_object("btn_destino")
btn_destino.connect("clicked", lambda w: selecionar_diretorio(entry_destino))

# Box de origens
box_origens = builder.get_object("box_origens")
adicionar_campo_origem()  # Primeiro campo de origem

# Botão de backup
btn_backup = builder.get_object("btn_backup")
btn_backup.connect("clicked", fazer_backup)

# Label de status
lbl_status = builder.get_object("lbl_status")

# Barra de progresso
progressbar = builder.get_object("progressbar_backup")
progressbar.set_fraction(0)
progressbar.set_text("")

# Mostra janela
window.show_all()
Gtk.main()
