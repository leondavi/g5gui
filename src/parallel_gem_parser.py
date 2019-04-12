
import ast

ERROR_DEF = -1
SUCCESS_DEF = 0
EXP_NAME_ATTR = "Experiment Name"
CONFIG_FILE_ATTR = "Config File"

class pgp_parser:

    def __init__(self,filename):
        self.filename = filename

    def parse(self):
        if self.filename.endswith(".pgp"):
            parallel_jobs_dict = dict()
            with open(self.filename) as f:
                data = ast.literal_eval(f.read())
        else:
            return ERROR_DEF
        self.parallel_jobs = []
        for idx,job in enumerate(data):
            new_job = p_job(idx)
            attributes_list = []
            for key, value in job.items():
                if key == EXP_NAME_ATTR:
                    new_job.set_experiment_name(value)
                elif key == CONFIG_FILE_ATTR:
                    new_job.set_config_file(value)
                else:
                    attributes_list.append(key)
                    attributes_list.append(value)
            new_job.set_attributes(attributes_list)
            self.parallel_jobs.append(new_job)
        return SUCCESS_DEF

    def get_parallel_jobs(self):
        return self.parallel_jobs

class p_job:
    def __init__(self, processs_id = 0,experiment_name="exp",attributes = []):
        self.pid = processs_id
        self.experiment_name = experiment_name
        self.config_file = ""
        self.attributes = attributes

    # setters
    def set_processs_id(self,processs_id):
        self.pid = processs_id

    def set_experiment_name(self,experiment_name):
        self.experiment_name = experiment_name

    def set_attributes(self,attributes):
        self.attributes = attributes

    def set_config_file(self,config_file):
        self.config_file = config_file