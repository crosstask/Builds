# CrossTask Team
# Developers: @zlElo and @DarkGloves
# Licensed under GPL 3.0

from customtkinter import *
import tkinter as tk
import platform
import os
import psutil
import customtkinter
import json


class ProcessInfo(CTkToplevel):
    def __init__(self, process_name, process_id):
        super().__init__()
        self.geometry('350x230')
        self.resizable(False, False)
        self.title(f'Process [{process_id}]')

        # read settings
        doc_path = os.path.join(os.path.expanduser('~'), 'Documents')
        with open(f'{doc_path}/CrossTask/Settings/settings.json', 'r') as f:
            data = json.load(f)
            theme = data['theme']
        f.close()
        
        if theme == "System":
            customtkinter.set_appearance_mode("system")
        elif theme == "Dark":
            customtkinter.set_appearance_mode("dark")
        elif theme == "White":
            customtkinter.set_appearance_mode("white")

        # Process Label
        name_label = CTkLabel(self, text=f'Process:     {process_name}')
        name_label.pack(padx=10, pady=25)

        # cpu usage of process
        cpu_frame = CTkFrame(self)
        cpu_frame.pack()
        cpu_usage_label = CTkLabel(cpu_frame, text='CPU usage')
        cpu_usage_label.pack()
        cpu_usage = CTkProgressBar(cpu_frame)
        cpu_usage.pack(padx=10, pady=5)

        # ram usage of process
        ram_frame = CTkFrame(self)
        ram_frame.pack(pady=18)
        ram_usage_label = CTkLabel(ram_frame, text='RAM usage')
        ram_usage_label.pack()
        ram_usage = CTkProgressBar(ram_frame)
        ram_usage.pack(padx=10, pady=5)

        # platform check for window icon
        operating_system = platform.system()
        if  operating_system == 'Windows':
            self.after(200, lambda: self.iconbitmap(os.path.join(os.getcwd(), 'img', 'bitmap.ico')))
        elif operating_system == 'Linux':
            pass
        else:
            # setup macos window icon
            img = tk.Image("photo", file="content/logo_crosstask-removebg.png")
            self.after(200, lambda: self.tk.call('wm','iconphoto', self._w, img))

        # start stat reloading
        self.after(200, lambda: self._update_stats(process_id, cpu_usage, ram_usage, cpu_usage_label, ram_usage_label))

    def _update_stats(self, process_id, cpu_usage, ram_usage, cpu_usage_label, ram_usage_label):
        p = psutil.Process(int(process_id))
        process_mem = p.memory_percent()
        process_cpu = p.cpu_percent(interval=1)

        # cpu updater
        cpu_usage_label.configure(text=f'{round(process_cpu, 1)}% CPU usage')
        cpu_usage.set(process_cpu/100)

        # ram updater
        ram_usage_label.configure(text=f'{round(process_mem, 1)}% RAM usage')
        ram_usage.set(process_mem/100)
