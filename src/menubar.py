from tkinter import Menu
from tkinter import IntVar
from definitions import *
from files_management import *
from functools import partial
import params_set_window as psw

MENUBAR_DICT_SAVED_FILE = os.path.join(os.pardir, "dictmbr.data")
SELECTED_DEBUG_MODE = 1

class Menubar:


    def __init__(self,window):
        self.parms_window_inst = psw.ParamsSetWindow(window)
        self.menubar = Menu(window)
        self.dictionary = dict()
        self.selected_debug_mode = IntVar()
        #loading from file if existed
        if check_file_exist(MENUBAR_DICT_SAVED_FILE):
            self.dictionary = load_obj(MENUBAR_DICT_SAVED_FILE)
            self.selected_debug_mode.set(self.dictionary.get(SELECTED_DEBUG_MODE,0))

        self.generate_menubar(window)
        window.config(menu=self.menubar)

    def func_nothing(self):
        return

    def generate_menubar(self,window):
        self.menubar.add_cascade(label="File", menu=self.generate_filemenu(window))
        self.menubar.add_cascade(label="Debug Modes",menu=self.generate_debug_modes_menu(window))
        self.menubar.add_cascade(label="Config Opt",menu=self.generate_config_menu(window))

    def generate_filemenu(self,window):
        filemenu = Menu(window, tearoff=0)
        filemenu.add_command(label="Properties", command=self.func_nothing)
        filemenu.add_command(label="Save", command=self.func_nothing)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=window.quit)
        return filemenu

    def generate_debug_modes_menu(self,window):
        debugMenu = Menu(window,tearoff=0)
        radio_buttons_vec = []
        for index in range(0, len(DebugModes)):
            debugMenu.add_radiobutton(label=DebugModes[index], value=index,variable=self.selected_debug_mode, command=self.save_selection)
        return debugMenu

    def generate_config_menu(self,window):
        filemenu = Menu(window,tearoff=0)
        filemenu.add_command(label="params set", command = self.parms_window_inst.generate_config_paramsSet_window)
        return filemenu

    def save_selection(self):
        self.dictionary[SELECTED_DEBUG_MODE] = self.selected_debug_mode.get()
        save_obj(self.dictionary,MENUBAR_DICT_SAVED_FILE)

    def get_debug_mode_selection(self):
        return self.selected_debug_mode.get()

    #Setters
    def set_config_file(self,config_file_name):
        self.parms_window_inst.set_config_file(config_file_name)


