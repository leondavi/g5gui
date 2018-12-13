import tkinter as tk # Pyth
from files_management import *
from tkinter import messagebox
import subprocess
from scrframe import *
from definitions import *


PARAMS_WINDOW_SIZE = "500x600"
DEFAULT_VALUE = "Default Value"


class ParamsSetWindow:
    def __init__(self,window,filesfromfill_dict):
        self.dictionary = filesfromfill_dict
        self.parent_window = window
        self.last_config_name = None
        self.edited_params = dict()

    def generate_config_paramsSet_window(self):
        check_files = check_config_file_correctness(self.dictionary) and check_gem_opt_file_correctness(self.dictionary)
        if self.last_config_name is None:
            self.last_config_name = self.dictionary[CONFIG_FILE]
        elif self.last_config_name != self.dictionary[CONFIG_FILE]:
            self.config_changed_case() #erase the dictionaries

        if not check_files:  # check if string empty
            messagebox.showerror("Can't set params", "Config file wasn't loaded!")
        else:
            self.params_window = self.create_window("Config File Parameters Set", PARAMS_WINDOW_SIZE)
            self.params_window.resizable(FALSE, FALSE)

            subproc_res = subprocess.run([self.dictionary[GEM5_EXECUTE_FILE]+" "+self.dictionary[CONFIG_FILE]+" -h"],
                                         stdout=subprocess.PIPE,shell=True)

            self.params_dict = self.extract_params_list(subproc_res.stdout.decode())

            self.scrolled_frame = VerticalScrolledFrame(self.params_window)
            self.scrolled_frame.pack(expand=1)

            self.params_labels_dict = dict()
            self.params_entries_dict = dict()
            row = 0
            col = 0
            for key,value in self.params_dict.items():
                self.params_labels_dict[key] = Label(self.scrolled_frame.interior,text=str(key),borderwidth=5)
                self.params_entries_dict[key] = Entry(self.scrolled_frame.interior)
                self.params_entries_dict[key].insert(END,str(self.params_dict[key]))
                #buttons.append(Button(self.scrolled_frame.interior, text="Button " + str(i)))
                self.params_labels_dict[key].grid(row=row,column=col)
                self.params_entries_dict[key].grid(row=row,column=col+1)
                row+=1

            update_button = Button(self.params_window, text='Update Params', command=self.update_button,width=20)
            update_button.pack(side=BOTTOM)
            self.params_window.mainloop()

    # return instance of new window

    def config_changed_case(self):
        self.params_labels_dict.clear()
        self.params_entries_dict.clear()
        self.params_dict.clear()

    def update_button(self):
        self.edited_params.clear()
        for key, entry in self.params_entries_dict.items():
            if entry.get() != DEFAULT_VALUE:
                self.edited_params[key] = entry.get()

    def generate_params_command_string(self):
        final_str = ""
        for key, entry in self.edited_params.items():
            final_str=final_str+str(key)+"="+str(entry)+" "
        return final_str

    def create_window(self, new_window_name, sizes):
        t = tk.Toplevel(self.parent_window)
        t.wm_title(new_window_name)
        # t.wm_geometry(sizes)
        t.geometry(sizes)
        #  l = tk.Label(t, text="This is window #%s" % self.counter)
        #  l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        return t

    def extract_params_list(self,stdout_res):
        lines = stdout_res.splitlines(stdout_res.count('\n'))
        params_dict = dict()
        for line in lines:
            if line.find("--") != NEGNULL:
                words = line.split()
                for word in words:
                    if word.find("--") != NEGNULL:
                        param_val_list = word.split("=")[0]
                        params_dict[param_val_list] = DEFAULT_VALUE

        return params_dict

