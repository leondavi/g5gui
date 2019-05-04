import tkinter as tk
from files_management import *
from scrframe import *
import pandas as pd
import re
from support import *

USER_PROPERTIES_FILE = "post_proc_prop"
OUTPUT_DIR = 2
ATTRIBUTES_TO_EXTRACT_LIST = 3

SCRIPT_RUN_MENU_WINSIZE = "700x500"

JOB_TRACK_ATTRIBUTES = ["-num-threads","--binary"]


class PostProcessingRunWin():
    def __init__(self, window, previous_win_form,jobs_tracker_file):
        self.parent_window = window
        self.curr_row = 1
        self.dict_properties = dict()
        self.output_dir = previous_win_form[OUTPUT_DIR]
        self.jobs_tracker_file = jobs_tracker_file

        # Load params
        if check_file_exist(USER_PROPERTIES_FILE):
            self.dict_properties = load_obj(USER_PROPERTIES_FILE)
        else:
            # Init default params
            self.dict_properties[ATTRIBUTES_TO_EXTRACT_LIST] = []

    def generate_sub_window(self):
        self.window = self.create_window("Post Processing Statistics Extractor", SCRIPT_RUN_MENU_WINSIZE)
        self.frameTop = Frame(self.window, height=200)
        self.frameMiddle = Frame(self.window, height=200)
        self.frameBottom = Frame(self.window, height=100)

        self.frameTop.grid(row=0)
        self.frameMiddle.grid(row=1)
        self.frameBottom.grid(row=2)

        self.text_entry_label = Label(self.frameTop,text="Enter attributes to extract from stats (comma seperated e.g ipc,commits,...)").grid(row=0)
        self.txt_box = Text(self.frameTop,height=20,width=80)
        self.txt_box.grid(row=1)
        seperator = ','
        self.set_text_textbox(self.txt_box,seperator.join(self.dict_properties[ATTRIBUTES_TO_EXTRACT_LIST]))



        self.generate_button = Button(self.frameTop,text="Generate",command=self.action_generate).grid(row=2)

    def set_text_textbox(self,txtbox,value):
        txtbox.delete(1.0, tk.END)
        txtbox.insert(tk.END, value)

    def action_generate(self):
        self.retrieve_input_from_txtbox()
        extractor = stats_extractor(self.output_dir,self.dict_properties[ATTRIBUTES_TO_EXTRACT_LIST],self.jobs_tracker_file )
        extractor.generate_csv()


    def retrieve_input_from_txtbox(self):
        inputValue = self.txt_box.get("1.0", "end-1c")
        self.dict_properties[ATTRIBUTES_TO_EXTRACT_LIST] = inputValue.split(",")
        save_obj(self.dict_properties,USER_PROPERTIES_FILE)
        print(inputValue)

    def create_window(self, new_window_name, sizes):
        t = tk.Toplevel(self.parent_window)
        t.wm_title(new_window_name)
        # t.wm_geometry(sizes)
        t.geometry(sizes)
        #  l = tk.Label(t, text="This is window #%s" % self.counter)
        #  l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        return t


STATS_FILE = "stats.txt"

class stats_extractor():
  #Recursively check all subfolder in root_dir for stats
    def __init__ (self,root_dir,attributes_to_extract,jobs_tracker_file):
        self.stats_files_list = []
        self.root_dir = root_dir
        self.attributes_to_extract = attributes_to_extract
        self.jobs_tracker_file = jobs_tracker_file

    def generate_csv(self):

        jobs_dict = dict()
        # Loading jobs from jobs tracker
        track_file_fo = open(self.jobs_tracker_file,"r")
        for line in track_file_fo.readlines():
            attributes_in_line = line.split()
            jobs_dict_key = "" #should be the outdir
            for param_attribute in attributes_in_line:
                pattern = re.compile("--+\w+=")
                pattern2 = re.compile("(--\w+)-+\w+=")
                if pattern.match(param_attribute) or pattern2.match(param_attribute):
                    param = param_attribute.split("=")
                    if param[0]=="--outdir":
                        jobs_dict_key = param[-1]
                    elif param[0]=="--binary":
                        app = param[1].split("/")[-1]
                        dict_update_key_multival(jobs_dict,jobs_dict_key,(param[0],app))
                    else:
                        dict_update_key_multival(jobs_dict,jobs_dict_key,(param[0],param[1]))

        table_headers = ["threads","app"]+self.attributes_to_extract
        data = pd.DataFrame(columns=table_headers)

        # getting all stats files
        for root, directories, filenames in os.walk(self.root_dir):
            # for directory in directories:
            #     print(os.path.join(root, directory))

            for filename in filenames:
                if filename == "stats.txt":
                    #Tuple: (directory,fullpathtofile,stats_attr)
                    self.stats_files_list.append(os.path.join(root,filename))
                    current_attributes = self.extract_stats_attributes(self.stats_files_list[-1])
                    #generate table row





    def extract_stats_attributes(self,filename):
        attributes_list = []
        fo = open(filename,"r")
        lines = fo.readlines()
        dots_pattern = re.compile("^\w+(\.\w+)*$")
        for line in lines:
            for attribute in self.attributes_to_extract:
                if attribute in line:
                    if dots_pattern.match(attribute):
                        attribute_last = attribute.split(".")[-1]
                        attributes_list.append((attribute_last,line.split()[1]))
                    else:
                        attributes_list.append((attribute, line.split()[1]))

        return attributes_list