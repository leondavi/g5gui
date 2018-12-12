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
    def __init__(self,window):
        self.config_file = ""
        self.gem5_exec_file = ""
        self.parent_window = window

#Setters
    def set_config_file(self,config_file_name):
        self.config_file = config_file_name

    def set_gem5_exec(self, file_path):
        self.gem5_exec_file = file_path
#Getters
    def get_config_file_name(self):
        return self.config_file

    def get_gem5_exec_file_name(self):
        return self.gem5_exec_file

    def generate_config_paramsSet_window(self):
        if not self.config_file:  # check if string empty
            messagebox.showerror("Can't set params", "Config file wasn't loaded!")
        else:
            self.params_window = self.create_window("config file - parameters set", PARAMS_WINDOW_SIZE)

    # return instance of new window

    def create_window(self, new_window_name, sizes):
        t = tk.Toplevel(self.parent_window)
        t.wm_title(new_window_name)
        # t.wm_geometry(sizes)
        t.geometry(sizes)
        #  l = tk.Label(t, text="This is window #%s" % self.counter)
        #  l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        return t


