import tkinter as tk # Pyth
from files_management import *
from tkinter import messagebox
from tkinter import filedialog
import subprocess
from scrframe import *
from definitions import *
from demopanels import MsgPanel, SeeDismissPanel

SCRIPT_RUN_MENU_WINSIZE = "800x500"
USER_PROPERTIES_FILE = "script_prop"

PATH_TO_SCRIPT = 1


class ScritptRunWin:
    def __init__(self,window):
        self.parent_window = window
        self.curr_row = 1
        self.dict_properties = dict()

        #Load params
        if check_file_exist(USER_PROPERTIES_FILE):
            self.dict_properties = load_obj(USER_PROPERTIES_FILE)
        # Init default params
        else:
            self.dict_properties[PATH_TO_SCRIPT] = ""


    def generate_sub_window(self):
        self.window = self.create_window("Gem5 script runner *.gem", SCRIPT_RUN_MENU_WINSIZE)
        self.window.resizable(FALSE, FALSE)
        self.frameTop = Frame( self.window,height=200)
        self.frameMiddle = Frame( self.window,height=200)
        self.frameBottom = Frame( self.window,height=200)

        self.frameTop.grid(row=1)
        self.frameMiddle.grid(row=2)
        self.frameBottom.grid(row=3)

        self.add_file_browser_and_textbar(self.frameTop)
        self.add_buttons(self.frameMiddle)
        #TODO load number of parallel processes
        self.add_progress_bar( self.frameBottom,self.curr_row,0,0)

    def add_file_browser_and_textbar(self,frame):
        MsgPanel(self.window,["Choose script file to run multiple gem5 tests"],0,0)
        self.txtBox = Text(frame, width=80, height=1, state=NORMAL)
        self.txtBox.delete(1.0,END)
        self.txtBox.insert(END,self.dict_properties[PATH_TO_SCRIPT])
        self.txtBox['state'] = DISABLED
        self.BrowseButton = Button(frame, text='Browse', command = lambda: self.browse(self.window,self.txtBox))

        self.txtBox.grid(row=self.curr_row,column=0)
        self.BrowseButton.grid(row=self.curr_row,column=1)
        self.curr_row += 1

    def add_buttons(self,frame):
        cur_row = 0
        slider = IntVar()
        self.processes_label = Label(frame, textvariable=slider).grid(row=cur_row, column=1)
        cur_row += 1
        self.processes_scale = Scale(frame, from_=0, to_=8, length=300,variable=slider).grid(row=cur_row,column=1)
        self.RunButton = Button(frame, text='Run', command = self.action_run)
        self.RunButton.grid(row=self.curr_row,column=0)
        self.curr_row += 2
        pass

    def add_progress_bar(self,frame,row,column,process_id):
        name_frame = MsgPanel(frame,["Process #: "+str(process_id)],0)
        pb = Progressbar(frame,mode='determinate',length=300)
        pb.grid(row=1,column=column,pady=5)
        return (process_id,pb)


    def create_window(self, new_window_name, sizes):
        t = tk.Toplevel(self.parent_window)
        t.wm_title(new_window_name)
        # t.wm_geometry(sizes)
        t.geometry(sizes)
        #  l = tk.Label(t, text="This is window #%s" % self.counter)
        #  l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        return t

    def browse(self,window,textBox):
        filename = filedialog.askopenfile(parent=window,mode='rb',title='Choose script file')
        self.dict_properties[PATH_TO_SCRIPT] = filename.name
        save_obj(self.dict_properties,USER_PROPERTIES_FILE)
        #updating textbox
        textBox['state'] = NORMAL
        textBox.delete(1.0, END)
        textBox.insert(END, self.dict_properties[PATH_TO_SCRIPT])
        textBox['state'] = DISABLED


    def action_run(self):
        pass