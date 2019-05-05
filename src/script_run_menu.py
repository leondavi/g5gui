import tkinter as tk # Pyth
from sqlite3 import OptimizedUnicode

from tkinter import messagebox
from tkinter import filedialog
from scrframe import *
from definitions import *
from demopanels import MsgPanel, SeeDismissPanel
from parallel_gem_exec import *
import time
import threading
from support import *
import math
from win_post_proccessing import  *

SCRIPT_RUN_MENU_WINSIZE = "800x750"
USER_PROPERTIES_FILE = "script_prop"

DEFAULT_OUTPUT_DIR = "statistics"
PATH_TO_SCRIPT = 1
OUTPUT_DIR = 2


class ScritptRunWin:
    def __init__(self,window,previous_win_form):
        self.parent_window = window
        self.curr_row = 1
        self.dict_properties = dict()
        self.form_dict = previous_win_form


        #Load params
        if check_file_exist(USER_PROPERTIES_FILE):
            self.dict_properties = load_obj(USER_PROPERTIES_FILE)
        else:
            # Init default params
            self.dict_properties[PATH_TO_SCRIPT] = ""
            self.dict_properties[OUTPUT_DIR] = DEFAULT_OUTPUT_DIR

        self.jobs_tracker = os.path.join(self.dict_properties[OUTPUT_DIR], JOBS_TRACKING_FILE)


    def generate_sub_window(self):

        if self.form_dict_is_valid_Q():
            self.window = self.create_window("Gem5 script runner *.gem", SCRIPT_RUN_MENU_WINSIZE)
            self.window.resizable(FALSE, FALSE)
            self.frameTop = Frame( self.window,height=200)
            self.frameScale = Frame( self.window,height=100)
            self.frameMiddle = Frame( self.window,height=200)
            self.frameBottom = Frame( self.window,height=200)

            self.frameTop.grid(row=1)
            self.frameScale.grid(row=2)
            self.frameMiddle.grid(row=3)
            self.frameBottom.grid(row=4)

            #top frame widgets
            cur_row = 0
            cur_row = self.add_file_browser_and_textbar(self.frameTop,cur_row)
            MsgPanel(self.frameTop, ["Default config file: "+self.config_file_str], row=cur_row, column=0)
            #add scale of processes frame
            self.add_process_amount_bar(self.frameScale)
            #middle fram widgets
            cur_row = 0
            cur_row = self.add_buttons(self.frameMiddle)
            #TODO load number of parallel processes
            #bottom frame widgets
        else:
            messagebox.showerror("Error", "One of the file is incomplete")

    def form_dict_is_valid_Q(self):
        all_keys_exists = True
        for i in range(1,NUM_OF_KEYS):
            all_keys_exists = all_keys_exists and dict_check_key(self.form_dict,i)

        if all_keys_exists:
            self.config_file_str = self.form_dict[CONFIG_FILE]
            self.gem5_build_dir_str = self.form_dict[BUILD_DIR]
            self.gem5_exec_str = self.form_dict[GEM5_EXECUTE_FILE]
            return True

        return False

    def add_file_browser_and_textbar(self,frame,row):
        MsgPanel(frame,["Choose script file to run multiple gem5 tests"],row,0)
        self.txtBox = Text(frame, width=80, height=1, state=NORMAL)
        self.txtBox.delete(1.0,END)
        self.txtBox.insert(END,self.dict_properties[PATH_TO_SCRIPT])
        self.txtBox['state'] = DISABLED
        self.BrowseButton = Button(frame, text='Browse', command = lambda: self.browse(self.window,self.txtBox,PATH_TO_SCRIPT))
        row+=1
        self.txtBox.grid(row=row,column=0,padx=5)
        self.BrowseButton.grid(row=row,column=1)
        row+=1
        MsgPanel(frame, ["Choose output folder or mark the default statistics"], row,0 )
        self.txtBoxOutputDir = Text(frame, width=80, height=1, state=NORMAL)
        self.txtBoxOutputDir.delete(1.0, END)
        if OUTPUT_DIR not in self.dict_properties.keys():
            self.dict_properties[OUTPUT_DIR] = DEFAULT_OUTPUT_DIR
        self.txtBoxOutputDir.insert(END, self.dict_properties[OUTPUT_DIR])
        self.txtBoxOutputDir['state'] = DISABLED
        self.BrowseButtonOutputDir = Button(frame, text='Browse', command=lambda: self.browse(self.window, self.txtBoxOutputDir,OUTPUT_DIR,True))
        self.default_out_dir_var = IntVar()
        self.default_out_dir_var.set(0)
        self.DefaultOutdirCheckButton = Checkbutton(frame,text="Default Dir",variable=self.default_out_dir_var,command=self.default_dir_checkbutton_action)
        row += 1
        self.txtBoxOutputDir.grid(row=row, column=0, padx=5)
        self.BrowseButtonOutputDir.grid(row=row, column=1)
        row += 1
        self.DefaultOutdirCheckButton.grid(row=row,column=0)
        row += 1
        return row

    def default_dir_checkbutton_action(self):
        if self.default_out_dir_var.get() == 1:
            self.BrowseButtonOutputDir['state'] = DISABLED
        else:
            self.BrowseButtonOutputDir['state'] = NORMAL

    def add_process_amount_bar(self,frame):
        cur_row = 0
        MsgPanel(frame, ["Select # of processes:"],row=cur_row,column=1)
        cur_row += 1
        slider = IntVar()
        slider.set(1)
        self.processes_available = 1
        self.processes_label = Label(frame, textvariable=slider).grid(row=cur_row, column=1)
        cur_row += 1
        self.processes_scale = Scale(frame, from_=1, to_=8, length=300,variable = slider,command = lambda x: self.discrete_scale(slider)).grid(row=cur_row,column=1)

    def add_buttons(self,frame):

        cur_row = 0
        self.RunButton = Button(frame, text='Run', command = self.action_run)
        self.RunButton.grid(row=cur_row,column=1,pady=5)
        self.StopButton = Button(frame, text='Stop', command = self.action_stop)
        self.StopButton.grid(row=cur_row,column=2,pady=5)
        self.PostProcessingButton = Button(frame, text='Post Processing', command=self.action_post_processing)
        self.PostProcessingButton.grid(row=cur_row, column=0, pady=5)
        cur_row += 1
        self.remained_job_text = StringVar()
        self.remained_job_text.set("Remained jobs: -")
        self.remained_jobs_label = Label(frame,textvariable=self.remained_job_text)
        self.remained_jobs_label.grid(row=cur_row, column=1, pady=2)
        cur_row += 1
        return cur_row

    def discrete_scale(self, slider):
        value = slider.get()
        newvalue = min(range(1, 9), key=lambda x: abs(x - float(value)))
        slider.set(newvalue)
        self.processes_available = newvalue


    def add_progress_bar(self,frame,row,column,process_id):
        name_frame = MsgPanel(frame,["P-"+str(process_id)],row,column)
        row+=1
        progress_var = DoubleVar()
        progress_var.set(0)
        pb = Progressbar(frame,mode='determinate',length=200,variable=progress_var,maximum=100)
        pb.grid(row=row,column=column,pady=5,padx=5)
        return (process_id,pb,progress_var)


    def create_window(self, new_window_name, sizes):
        t = tk.Toplevel(self.parent_window)
        t.wm_title(new_window_name)
        # t.wm_geometry(sizes)
        t.geometry(sizes)
        #  l = tk.Label(t, text="This is window #%s" % self.counter)
        #  l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        return t

    def browse(self,window,textBox,dict_attr,dir_mode=False):
        if dir_mode :
            path = filedialog.askdirectory()
            self.dict_properties[dict_attr] = path
        else:
            path = filedialog.askopenfile(parent=window,mode='rb',title='Choose script file')
            self.dict_properties[dict_attr] = path.name
        save_obj(self.dict_properties,USER_PROPERTIES_FILE)
        #updating textbox
        textBox['state'] = NORMAL
        textBox.delete(1.0, END)
        textBox.insert(END, self.dict_properties[dict_attr])
        textBox['state'] = DISABLED

    def action_stop(self):
        self.stop = True
        self.pge.kill_all_processes()

    def action_post_processing(self):
        ppw = PostProcessingRunWin(self.window,self.dict_properties,self.jobs_tracker)
        ppw.generate_sub_window()

        pass

    def action_run(self):
        self.stop = False
        pgp_p = pgp_parser(self.dict_properties[PATH_TO_SCRIPT],self.gem5_build_dir_str)
        res = pgp_p.parse()
        if res == ERROR_DEF :
            messagebox.showerror("Error","Only pgp files are supported")
        jobs_count = len(pgp_p.get_parallel_jobs())
        self.progress_bars = []
        for i in range(0,self.processes_available):
            self.progress_bars.append(self.add_progress_bar(self.frameBottom, 2*int(math.floor(i/2)), i % 2,i))
        out_dir = os.path.join(self.gem5_build_dir_str,DEFAULT_OUTPUT_DIR)
        if self.default_out_dir_var.get() == 0:
            out_dir=self.dict_properties[OUTPUT_DIR]
        self.pge = parallel_gem_exec(pgp_p.get_parallel_jobs(),self.form_dict,out_dir,self.processes_available)
        self.remained_job_text.set("Remained jobs:" + str(self.pge.get_jobs_remained()))
        self.thread = threading.Thread(target=self.jobs_processing, args=[self.pge])
        self.thread.start()

    def jobs_processing(self,pge):
        while pge.get_jobs_remained() > 0 and not self.stop:
            pge.allocate_jobs_to_processes()
            pge.clear_finished_processes()
            self.remained_job_text.set("Remained jobs:" + str(pge.get_jobs_remained()))
            #updating cpu processes usage bars
            bars_cpu_usage_list = pge.get_processes_cpu_usage()
            for bar in bars_cpu_usage_list:
                self.progress_bars[bar[0]][2].set(bar[1])
            time.sleep(0.1)
            #print("in while")
        self.remained_job_text.set("Remained jobs: 0")
        print("stopped")
        for bar in self.progress_bars:
            bar[2].set(0)