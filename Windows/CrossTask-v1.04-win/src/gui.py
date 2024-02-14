# CrossTask Team
# Developers: @zlElo and @DarkGloves
# Licensed under GPL 3.0


###########
# MODULES #
###########
from customtkinter import *
import customtkinter
from tkinter import Menu, Label
import tkinter as tk
from src.widgets import *
from src.popups.about_developer import DevelopersPopup
from PIL import Image
from src.popups.about_program import AboutPopup
from src.settings.settings import SettingsWindow
from src.popups.process_info import ProcessInfo
from tkinter import PhotoImage
import psutil
import os
import threading
import time
import platform
from PIL import Image
import re
import json


#########
# Icons # https://lucide.dev <3
#########
class Icons():
    def __init__(self, size:tuple) -> None:
        self.refresh_list = CTkImage(Image.open(os.path.join(os.getcwd(), 'img', 'light', 'refresh_list.png')), Image.open(os.path.join(os.getcwd(), 'img', 'dark', 'refresh_list.png')), size=size)
        self.refresh = CTkImage(Image.open(os.path.join(os.getcwd(), 'img', 'light', 'refresh.png')), Image.open(os.path.join(os.getcwd(), 'img', 'dark', 'refresh.png')), size=size)
        self.skull = CTkImage(Image.open(os.path.join(os.getcwd(), 'img', 'light', 'skull.png')), Image.open(os.path.join(os.getcwd(), 'img', 'dark', 'skull.png')), size=size)
        self.debug = CTkImage(Image.open(os.path.join(os.getcwd(), 'img', 'light', 'debug.png')), Image.open(os.path.join(os.getcwd(), 'img', 'dark', 'debug.png')), size=size)

#######
# GUI #
#######
class GUI(CTk):
    def __init__(self):
        super().__init__()
        # window configuration
        self.title('CrossTask')
        self.geometry("450x630")

        # platform check for window icon
        operating_system = platform.system()
        if  operating_system == 'Windows':
            self.iconbitmap(os.path.join(os.getcwd(), 'img', 'bitmap.ico'))
        elif operating_system == 'Linux':
            pass
        else:
            # setup macos window icon 
            img = tk.Image("photo", file="content/logo_crosstask-removebg.png")
            self.tk.call('wm','iconphoto', self._w, img)

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
        
        self.rowconfigure((0), weight=1)
        self.columnconfigure((0), weight=1)
        
        # tabview
        self.tabview = CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky=NSEW, padx=10, pady=10)
        self.tabview.add('Processes')
        self.tabview.add('Performance')
        self.tabview.set('Processes')

        # menubar
        self.menubar = Menu(self)       
        self.config(menu=self.menubar) 

        # menubar - file
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Reload", command=lambda: _update())
        self.filemenu.add_command(label="Settings", command=lambda: SettingsWindow().grab_set())
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # menubar - about
        self.aboutmenu = Menu(self.menubar, tearoff=0)
        self.aboutmenu.add_command(label="Developers", command=lambda : DevelopersPopup().grab_set())
        self.aboutmenu.add_command(label="About", command=lambda: AboutPopup().grab_set())
        self.menubar.add_cascade(label="Help", menu=self.aboutmenu)
        
        # vars
        self._mode = self._get_appearance_mode()
        self.autoupdate = True
        self.startup = True
        self.countProcesses = 0
        self.processListVar = StringVar(value=['Process list'])
        self._processesTab('Processes')
        self._performanceTab('Performance')
        currentTabAction = threading.Thread(target=self.__current_tab_action)
        currentTabAction.daemon = True
        currentTabAction.start() 

        def _update():
            self.autoupdate = True

    def _processesTab(self, tabName:str):
        self.tabview.tab(tabName).rowconfigure((0, 2), weight=1)
        self.tabview.tab(tabName).rowconfigure((1), weight=5)
        self.tabview.tab(tabName).columnconfigure((0,1), weight=1)
        self.searchbar = CTkEntry(self.tabview.tab(tabName), font=('Arial', 20), height=50) 

        class button_pallette(CTkFrame):
            def __init__(self, master, listBox:ScrollableListbox, processListVar, title):
                super().__init__(master, width=0, height=0, corner_radius=20)
                self.rowconfigure((0), weight=1)
                self.columnconfigure((0,1,2), weight=1)
                self.listBox = listBox
                self.killBtn = CTkButton(self, text='', image=Icons((20, 20)).skull, command=self._killProcess, width=0, height=0)
                self.restartBtn = CTkButton(self, text='', image=Icons((20, 20)).refresh, command=lambda: self._restartProcess(processListVar, title), width=0, height=0)
                self.copyPIDBtn = CTkButton(self, text='', image=Icons((20, 20)).debug, command=self._copyPID, width=0, height=0)
                self.killBtn.grid(row=0, column=0, sticky=NSEW)
                self.restartBtn.grid(row=0, column=1, sticky=NSEW)
                self.copyPIDBtn.grid(row=0, column=2, sticky=NSEW)
                
            def _killProcess(self):
                psutil.Process(int(re.findall(r'\((.*?)\)', self.listBox.List.get(self.listBox.List.curselection()))[0])).kill()

            def _restartProcess(self, processListVar, title):
                title('CrossTask - refreshing...')
                proc_list = []
                for process in psutil.process_iter(['pid', 'name', 'username']):
                    item = proc_list.append(f'{process.info["name"]} ({process.info["pid"]})')

                # collect informations about processes
                proc_list_length = len(proc_list)
                print(f'[log] Processes: {proc_list_length}')
                self.countProcesses = proc_list_length

                processListVar.set(proc_list)
                title('CrossTask')

            def _copyPID(self):
                selected_index = self.listBox.List.curselection()
                if selected_index:
                    selected_item = self.listBox.List.get(selected_index)
                ProcessInfo(selected_item, re.findall(r'\((.*?)\)', selected_item)[0])

        self.processList = ScrollableListbox(self.tabview.tab(tabName), self._get_appearance_mode(), self.processListVar)

        self.button_pallette = button_pallette(self.tabview.tab(tabName), self.processList, self.processListVar, self.title)

        self.searchbar.grid(row=0, column=0, sticky='EW', padx=30, pady=10, columnspan=2)
        self.processList.grid(row=1, column=0, sticky='NSEW', padx=30, pady=10, columnspan=2)
        self.searchbar.bind("<Return>", self.__search_process_list)
        self.button_pallette.grid(row=2, column=1, sticky=NE, padx=40)        
        

    def _performanceTab(self, tabName:str):
        frame = CTkScrollableFrame(self.tabview.tab(tabName))
        frame.columnconfigure((0), weight=1)
        frame.grid(row=0, column=0, sticky=NSEW, padx=5, pady=5)
        self.tabview.tab(tabName).rowconfigure(0, weight=1)  # Configure row weight
        self.tabview.tab(tabName).columnconfigure(0, weight=1)  # Configure column weight

        # CPU
        self.cpu_frame = self.__performanceBaseFrame('CPU Usage', frame)
        self.cpu_frame.grid(row=0, column=0, sticky=NSEW, padx=10, pady=20)
        
        # RAM
        self.ram_frame = self.__performanceBaseFrame('Memory Usage', frame)
        self.ram_frame.grid(row=1, column=0, sticky=NSEW, padx=10, pady=20)
        
        # DISK
        for index, disk in enumerate(psutil.disk_partitions()):
            try:
                tmpFrame = self.__performanceBaseFrame(f'Disk Usage ( {disk.mountpoint} )', frame)
                tmpFrame.grid(row=2+index, column=0, sticky=NSEW, padx=10, pady=20)
                tmpFrame.bar.set(psutil.disk_usage(disk.mountpoint).percent/100)
                tmpFrame.text.configure(text=f'{psutil.disk_usage(disk.mountpoint).percent}%')
            except PermissionError:
                pass

    def __performanceBaseFrame(self, title:str, master):
        frame = CTkFrame(master, corner_radius=10)
        frame.rowconfigure((0,1), weight=1)
        frame.columnconfigure((0), weight=4)
        frame.columnconfigure((1), weight=1)
        CTkLabel(frame, text=title, font=('Arial', 16)).grid(row=0, column=0, sticky=W, padx=10, pady=10)
        frame.bar = CTkProgressBar(frame)
        frame.bar.set(0)
        frame.bar.grid(row=1, column=0, sticky=EW, padx=10, pady=(0, 20))
        frame.text = CTkLabel(frame, text='--', font=('Arial', 16))
        frame.text.grid(row=0, column=1, rowspan=2)
        return frame
    
    def __update_performance_info(self):
        while self.autoupdate == True and self.tabview.get() == 'Performance':
            cpuUsage = psutil.cpu_percent(interval=1)
            ramUsage = psutil.virtual_memory().percent
            self.cpu_frame.bar.set(cpuUsage/100)
            self.cpu_frame.text.configure(text=f'{cpuUsage}%')
            self.ram_frame.bar.set(ramUsage/100)
            self.ram_frame.text.configure(text=f'{ramUsage}%')

    def __update_process_list(self):
        while self.autoupdate == True and self.tabview.get() == 'Processes':
            proc_list = []
            for process in psutil.process_iter(['pid', 'name', 'username']):
                proc_list.append(f'{process.info["name"]} ({process.info["pid"]})')
                        
            proc_list_length = len(proc_list)
            print(f'[log] Processes: {proc_list_length}')
            self.countProcesses = proc_list_length

            if self.startup == True:
                background_image, image_label, loading_label = self.__loadingProcessesSplash() # activate loading splash
            
            # update gui process list
            self.processListVar.set(proc_list)

            if self.startup == True:
                image_label.destroy()
                loading_label.destroy()
                background_image.__del__()

            # set update to false and destroy loading splash, update gui
            self.autoupdate = False
            self.startup = False

            self.update()
            
    def __search_process_list(self, *args):
        matchstr = self.searchbar.get()
        proc_list_search = []
        process_names = []
        for process in psutil.process_iter(['pid', 'name', 'username']):
            proc_list_search.append(f'{process.info["name"]} ({process.info["pid"]})')
            if matchstr.lower() in process.name().lower(): # If lowercase search matches with lowercase result
                process_names.append(f'{process.name()} ({process.pid})')

        # If no process with this search was found, insert "No matching result found"
        if not process_names:
            self.processListVar.set(["No matching result found!"])
            return
        
        self.processListVar.set(process_names)

    def __current_tab_action(self):
        # For optimisation: depending on the tab the user is it starts/stops the actions on it, making the program lightweight
        while(True):
            currentTab = self.tabview.get()
            if currentTab == 'Performance':
                self.autoupdate = True
                update_thread = threading.Thread(target=self.__update_performance_info)
                update_thread.daemon = True
                update_thread.start() 
                update_thread.join()
               
            if currentTab == 'Processes':
                if self.autoupdate == True:    
                    update_thread = threading.Thread(target=self.__update_process_list)
                    update_thread.daemon = True
                    update_thread.start() 
                    update_thread.join()
                    if self.processList.List.get(0) == None:
                        self.button_pallette.killBtn.configure(state='disabled')
                        self.button_pallette.copyPIDBtn.configure(state='disabled')
                        self.button_pallette.restartBtn.configure(state='disabled')
                elif self.button_pallette.killBtn._state == 'disabled':
                    self.button_pallette.killBtn.configure(state='normal')
                    self.button_pallette.copyPIDBtn.configure(state='normal')
                    self.button_pallette.restartBtn.configure(state='normal')
            time.sleep(0.25)

    def __loadingProcessesSplash(self):
        self.update()
        x = self.winfo_rootx()
        y = self.winfo_rooty()
        
        background_image = PhotoImage(file="content/logo_crosstask-removebg.png")
        image_label = Label(self, image=background_image, text='')
        image_label.place(x=0, y=1, relwidth=1, relheight=1)
        loading_label = Label(self, text=f"Loading {self.countProcesses} processes...", font=("Arial", 15))
        loading_label.place(relx=0.205, rely=0.96, anchor="center")        
        # load blurred picture
        self.update()

        return background_image, image_label, loading_label

    def __killProcessBtn(self):
        print(self.processList.List.get(self.processList.List.curselection()))