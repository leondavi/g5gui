
import ast
import os

ERROR_DEF = -1
SUCCESS_DEF = 0

#Supported lists combinations attributes:
DEBUG_FLAG_ATTR = "--debug-flag"
CONFIG_FILE_ATTR = "config"
NUM_THREADS_ATTR = "--num-threads"
BINARY_ATTR = "--binary"
BINARY_DIR_ATTR = "binary_dir"
list_of_combination_supported_attribute = [DEBUG_FLAG_ATTR,CONFIG_FILE_ATTR,NUM_THREADS_ATTR,BINARY_ATTR,BINARY_DIR_ATTR]

class pgp_parser:

    def __init__(self,filename,gem5_folder):
        self.filename = filename
        self.gem5_folder = gem5_folder

    def parse(self):
        if self.filename.endswith(".pgp"):
            parallel_jobs_dict = dict()
            with open(self.filename) as f:
                data = ast.literal_eval(f.read())
        else:
            return ERROR_DEF
        self.parallel_jobs = []
        for idx,job in enumerate(data):
            if type(job[DEBUG_FLAG_ATTR]) is not list:
                job[DEBUG_FLAG_ATTR] = [job[DEBUG_FLAG_ATTR]]
            if type(job[CONFIG_FILE_ATTR]) is not list:
                job[CONFIG_FILE_ATTR] = [job[CONFIG_FILE_ATTR]]
            if type(job[NUM_THREADS_ATTR]) is not list:
                job[NUM_THREADS_ATTR] = [job[NUM_THREADS_ATTR]]
            if BINARY_ATTR in job.keys():
                if type(job[BINARY_ATTR]) is not list:
                    job[BINARY_ATTR] = [job[BINARY_ATTR]]
            if BINARY_DIR_ATTR in job.keys():
                job[BINARY_ATTR] = self.parse_binaries_from_given_directory(job[BINARY_DIR_ATTR])
            #More attributes that doesn't support lists combination
            other_attr_list = []
            for key,val in job.items():
                if key not in list_of_combination_supported_attribute:
                    other_attr_list+=[key,val]
            self.parallel_jobs+=self.jobs_combinations_creator(idx,job[DEBUG_FLAG_ATTR],job[CONFIG_FILE_ATTR],job[NUM_THREADS_ATTR],job[BINARY_ATTR],other_attr_list)

    def jobs_combinations_creator(self,exp_id,debug_l,config_l,num_threads_l,binary_l,other_attr_list):
        parallel_jobs = []
        for debug_attr in debug_l:
            for config_attr in config_l:
                 for num_thread_attr in num_threads_l:
                    for binary_attr in binary_l:
                        new_job = p_job(experiment_name=str(exp_id)+"_t-"+num_thread_attr+"_"+os.path.splitext(config_attr)[0].split("/")[-1]+"_"+os.path.splitext(binary_attr)[0].split("/")[-1])
                        new_job.add_common_attributes(debug_attr,config_attr,num_thread_attr,binary_attr,other_attr_list)

                        parallel_jobs.append(new_job)
        return parallel_jobs

    def parse_binaries_from_given_directory(self,dir):
        files = []
        path = os.path.join(self.gem5_folder,dir)
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                files.append(os.path.join(r, file))
        return files

    def get_parallel_jobs(self):
        return self.parallel_jobs

class p_job:
    def __init__(self, processs_id = 0,experiment_name="exp",attributes = []):
        self.pid = processs_id
        self.experiment_name = experiment_name
        self.config_file = ""
        self.attributes = attributes

    def add_common_attributes(self,debug_attr,config_attr,num_thread_attr,binary_attr,other_attributes):
        self.attributes = []
        self.config_file = config_attr
        self.debug_flag = debug_attr
        self.attributes+=[NUM_THREADS_ATTR,num_thread_attr,BINARY_ATTR,binary_attr]
        self.attributes+=other_attributes

    # setters
    def set_processs_id(self,processs_id):
        self.pid = processs_id

    def set_experiment_name(self,experiment_name):
        self.experiment_name = experiment_name

    def set_attributes(self,attributes):
        self.attributes = attributes

    def set_config_file(self,config_file):
        self.config_file = config_file

    def set_debug_flag(self,value):
        self.debug_flag = value

    #getters

    def get_pid(self):
        return self.pid