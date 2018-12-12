import tkinter as tk # Pyth
from files_management import *
from tkinter import messagebox
import subprocess

PARAMS_WINDOW_SIZE = "300x600"


class ParamsSetWindow:
    def __init__(self,window,filesfromfill_dict):
        self.dictionary = filesfromfill_dict
        self.parent_window = window

    def generate_config_paramsSet_window(self):
        check_files = check_config_file_correctness(self.dictionary) and check_gem_opt_file_correctness(self.dictionary)
        if not check_files:  # check if string empty
            messagebox.showerror("Can't set params", "Config file wasn't loaded!")
        else:
            self.params_window = self.create_window("config file - parameters set", PARAMS_WINDOW_SIZE)
            subproc_res = subprocess.run([self.dictionary[GEM5_EXECUTE_FILE]+" "+self.dictionary[CONFIG_FILE]+" -h"], stdout=subprocess.PIPE,shell=True)
            print(subproc_res.stdout)
            subproc_res.stdout.decode()#recommended, check with utf-8 also


    # return instance of new window

    def create_window(self, new_window_name, sizes):
        t = tk.Toplevel(self.parent_window)
        t.wm_title(new_window_name)
        # t.wm_geometry(sizes)
        t.geometry(sizes)
        #  l = tk.Label(t, text="This is window #%s" % self.counter)
        #  l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        return t


