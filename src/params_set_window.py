import tkinter as tk # Pyth
from tkinter import messagebox
# on 3
from queue import Queue, Empty # Python 3
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from tkinter import messagebox

PARAMS_WINDOW_SIZE = "300x600"


class ParamsSetWindow:
    def __init__(self):
        self.config_file = ""

#Setters
    def set_config_file(self,config_file_name):
        self.config_file = config_file_name
#Getters
    def get_config_file_name(self):
        return self.config_file

config_params_set_window = ParamsSetWindow()

def params_set_window(window):
    config_file = config_params_set_window.get_config_file_name()
    if not config_file: #check if string empty
        messagebox.showerror("Can't set params","Config file wasn't loaded!")
    else:
        params_window = create_window(window,"config file - parameters set",PARAMS_WINDOW_SIZE)
#return instance of new window
def create_window(window,new_window_name,sizes):
    t = tk.Toplevel()
    t.wm_title(new_window_name)
   # t.wm_geometry(sizes)
    t.geometry(sizes)
  #  l = tk.Label(t, text="This is window #%s" % self.counter)
  #  l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
    return t

