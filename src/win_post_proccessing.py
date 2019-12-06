import tkinter as tk
from builtins import list
from contextlib import redirect_stderr

from PIL.Image import NORMAL
import json
from definitions import *
from files_management import *
from scrframe import *
import pandas as pd
import re
from support import *
import time

USER_PROPERTIES_FILE = "post_proc_prop"
OUTPUT_DIR = 2
ATTRIBUTES_TO_EXTRACT_LIST = 3

SCRIPT_RUN_MENU_WINSIZE = "700x500"

CSV_FILE_NAME = "stats_combined_results"

JOB_TRACK_ATTRIBUTES = ["-num-threads","--binary"]


class rows_of_data_to_pandasDF():
    def __init__(self, list_of_rows):
        self.list_unique_attributes_post = []
        self.list_unique_attributes_experiment = []
        for row in list_of_rows:
            self.list_unique_attributes_post = list(set(self.list_unique_attributes_post + row.post_proc_attributes))
            self.list_unique_attributes_experiment = list(
                set(self.list_unique_attributes_experiment + row.experiment_attributes))

        merged_attributes = self.list_unique_attributes_post + self.list_unique_attributes_experiment
        self.dfobj = pd.DataFrame(columns=merged_attributes)

        for row in list_of_rows:
            dict_to_add = dict()
            for attr in merged_attributes:
                dict_to_add[attr] = "x"
            for i, attr in enumerate(row.post_proc_attribtues_val):
                dict_to_add[row.post_proc_attributes[i]] = attr

            for i, attr in enumerate(row.experiment_attributes_val):
                dict_to_add[row.experiment_attributes[i]] = attr

            self.dfobj = self.dfobj.append(dict_to_add,ignore_index=True)

    def get_pandasDF(self):
        return self.dfobj


class row_of_data():
    def __init__(self):
        self.post_proc_attributes = []
        self.post_proc_attribtues_val = []
        self.experiment_attributes = []
        self.experiment_attributes_val = []

class PostProcessingRunWin():
    def __init__(self, window, previous_win_form,jobs_list):
        self.parent_window = window
        self.curr_row = 1
        self.dict_properties = dict()
        self.output_dir = previous_win_form[OUTPUT_DIR]
        self.jobs_list = jobs_list

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

        self.label_txtvar = StringVar()
        self.generate_button = Button(self.frameMiddle,text="Generate",command=self.action_generate)
        self.generate_button.grid(row=2,column=0,padx=2)
        self.generate_failure_pgp = Button(self.frameMiddle, text="Generate Failures pgp", command=self.action_generate_failures_pgp)
        self.generate_failure_pgp.grid(row=2,column=1,padx=2)
        self.generate_status_label = Label(self.frameTop,textvar=self.label_txtvar).grid(row=3)
        self.label_txtvar.set("Ready")

    def set_text_textbox(self,txtbox,value):
        txtbox.delete(1.0, tk.END)
        txtbox.insert(tk.END, value)

    def action_generate(self):
        self.retrieve_input_from_txtbox()
        extractor = stats_extractor(self.output_dir,self.dict_properties[ATTRIBUTES_TO_EXTRACT_LIST],self.jobs_list )
        extractor.generate_csv()
        self.generate_button.config(state = DISABLED)
        time.sleep(3)
        self.generate_button.config(state = NORMAL)
        self.label_txtvar.set("Generated")

    def action_generate_failures_pgp(self):
        pgp_list = []
        self.jobs_list
        for i,job in enumerate(self.jobs_list):
            if job.is_state_failed():
                pgp_list.append(job.job_to_dict_format())
        with open(os.path.join(self.output_dir,FILENAME_PGP_FAILURES),'w') as fout:
            json.dump(pgp_list,fout)

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
    def __init__ (self,root_dir,attributes_to_extract,jobs_list):
        self.stats_files_list = []
        self.root_dir = root_dir
        self.attributes_to_extract = attributes_to_extract
        self.jobs_list = jobs_list

    def generate_csv(self):

        jobs_dict = dict()
        params_headers = []
        first_file_flag = True
        # Loading jobs from jobs tracker
        # track_file_fo = open(self.jobs_tracker_file,"r")
        # for line in track_file_fo.readlines():
        #     attributes_in_line = line.split()
        #     jobs_dict_key = "" #should be the outdir
        #     for param_attribute in attributes_in_line:
        #         pattern = re.compile("--+\w+=")
        #         pattern2 = re.compile("(--\w+)-+\w+=")
        #         if pattern.match(param_attribute) or pattern2.match(param_attribute):
        #             param = param_attribute.split("=")
        #             if param[0]=="--outdir":
        #                 jobs_dict_key = param[-1].split("/")[-1]
        #             elif param[0]=="--binary":
        #                 app = param[1].split("/")[-1]
        #                 dict_update_key_multival(jobs_dict,jobs_dict_key,(param[0],app))
        #             else:
        #                 dict_update_key_multival(jobs_dict,jobs_dict_key,(param[0],param[1]))
        #                 if first_file_flag:
        #                     params_headers.append(param[0])
        #     first_file_flag = False


        reduced_attributees = []
        for attr in self.attributes_to_extract:
            reduced_attributees.append(attr.split(".")[-1])

        table_headers = params_headers+reduced_attributees
        df = pd.DataFrame(columns=table_headers)

        rows = []
        for job in self.jobs_list:
            r_dat = row_of_data()
            if job.is_state_done():
                stats_file = os.path.join(job.get_output_dir(),"stats.txt")
                current_attributes = self.extract_stats_attributes(stats_file)
                if (len(current_attributes) > 0):
                    for attr in current_attributes:
                        r_dat.post_proc_attributes.append(attr[0])
                        r_dat.post_proc_attribtues_val.append(attr[1])
                r_dat.experiment_attributes.append("state")
                r_dat.experiment_attributes_val.append("D")
            else:
                r_dat.experiment_attributes.append("state")
                r_dat.experiment_attributes_val.append("F")

            for key,val in job.job_to_dict_format().items():
                r_dat.experiment_attributes.append(key)
                r_dat.experiment_attributes_val.append(val)

            rows.append(r_dat)

        df_convert_obj = rows_of_data_to_pandasDF(rows)
        df = df_convert_obj.get_pandasDF()

    #     # getting all stats files
    #     for root, directories, filenames in os.walk(self.root_dir):
    #         # for directory in directories:
    #         #     print(os.path.join(root, directory))
    #
    #         for filename in filenames:
    #             if filename == "stats.txt":
    #                 #Tuple: (directory,fullpathtofile,stats_attr)
    #                 self.stats_files_list.append(os.path.join(root,filename))
    #                 current_attributes = self.extract_stats_attributes(self.stats_files_list[-1])
    #                 curr_dir = root.split("/")[-1]
    #                 if (len(current_attributes) > 0) and (curr_dir in jobs_dict.keys()):
    #                     row_list = []
    #                     #generate table row
    #                     list_of_param_attributes = jobs_dict[curr_dir]
    #                     for attribute in list_of_param_attributes:
    #                         row_list.append(attribute[1])
    #                     tmplist = [0]*len(self.attributes_to_extract)
    #                     for attribute in current_attributes:
    #                         tmplist[self.attributes_to_extract.index(attribute[0])] = attribute[1]
    #                     row_list+=tmplist
    # #modDfObj = dfObj.append(pd.Series(['Raju', 21, 'Bangalore', 'India'], index=dfObj.columns ), ignore_index=True)
    #                     df = df.append(pd.Series(row_list,index=df.columns),ignore_index=True)

        df.to_csv(os.path.join(self.root_dir,CSV_FILE_NAME)+".csv")





    def extract_stats_attributes(self,filename):
        attributes_list = []
        fo = open(filename,"r")
        lines = fo.readlines()
        dots_pattern = re.compile("^\w+(\.\w+)*$")
        for line in lines:
            for attribute in self.attributes_to_extract:
                if attribute in line:
                    if dots_pattern.match(attribute):
                        attributes_list.append((attribute,line.split()[1]))
                    else:
                        attributes_list.append((attribute,line.split()[1]))

        return attributes_list

