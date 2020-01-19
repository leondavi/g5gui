from itertools import product

from parallel_gem_parser import *
from multiprocessing import Process
from subprocess import Popen,PIPE
import psutil
import os
import time
import signal
from files_management import *
import datetime
import subprocess
import time
from time import gmtime, strftime

STATS_FILE = "stats.txt"
JOBS_TRACKING_FILE = "job_tracker.txt"

class parallel_gem_exec():
    def __init__(self,parallel_jobs,form_dict,output_dir,numof_processes_avaialable = 1):
        self.parallel_jobs = parallel_jobs
        self.numof_processes_avaialable = numof_processes_avaialable
        self.processes_list = []
        self.processes_num_list = []
        self.processes_available_list = self.processes_list
        self.job_iterator = 0
        self.gem5_dir_str = form_dict[BUILD_DIR]
        self.gem5_exec_file_str = form_dict[GEM5_EXECUTE_FILE]
        self.output_dir = output_dir
        self.cpp_process_pid_list = [-1]*numof_processes_avaialable
        self.jobs_tracker = os.path.join(self.output_dir, JOBS_TRACKING_FILE)
        self.still_processing = False


    def allocate_jobs_to_processes(self):
        os.makedirs(os.path.dirname(self.jobs_tracker),exist_ok=True)
        if os.path.isfile(self.jobs_tracker):
            self.jobs_track_file = open(self.jobs_tracker, "a+")
        else: #doesn't exist
            self.jobs_track_file = open(self.jobs_tracker, "w+")
        self.clear_finished_processes()
        while self.available_processes_Q() and self.job_iterator<len(self.parallel_jobs):
            self.processes_num_list.append(self.assign_proc_num())
            self.processes_num_list[-1]
            self.parallel_jobs[self.job_iterator]
            self.parallel_jobs[self.job_iterator].set_processs_id(self.processes_num_list[-1])
            job = self.parallel_jobs[self.job_iterator]
            command_string = self.build_command_string(job)
            print("Job name: " + job.experiment_name)
            print("Command executed: " + command_string)
            cpp_process = Popen(command_string, cwd=self.gem5_dir_str,stdout=subprocess.DEVNULL, shell=True, preexec_fn=None)
            time.sleep(0.3)
            children = self.get_children_processes(cpp_process)
            for child in children:
                child_p_name = psutil.Process(child.pid).name()
                if "gem5" in child_p_name:
                    self.cpp_process_pid_list[job.get_pid()] = child.pid
            monitor_proc = Process(target=self.task,args=[job,cpp_process])
            self.job_iterator += 1
            self.processes_list.append(monitor_proc)
            monitor_proc.start()
            self.jobs_track_file.write(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" job: "+job.experiment_name+" cmd: "+command_string+"\n")
        self.jobs_track_file.close()
        self.update_jobs_status()

    def update_jobs_status(self):
        for job in self.parallel_jobs:
            if self.check_stats_file_valid(job):
                job.set_state_done()
            else:
                job.set_state_failed()


    def kill_all_processes(self):
        for proc in self.processes_list:
            if proc.is_alive:
                children = self.get_children_processes(proc)
                if children != None:
                    for child_proc in children:
                        if psutil.pid_exists(child_proc.pid):
                            os.kill(child_proc.pid,signal.SIGKILL)
                os.kill(proc.pid,signal.SIGKILL)
        os.system("killall gem5.opt")
        self.parallel_jobs = []

    def task(self,job,process):
        at_least_one_alive = True
        while at_least_one_alive:
            time.sleep(0.5)
            children = self.get_children_processes(process)
            parent_alive = psutil.pid_exists(process.pid)
            one_of_children_alive = False
            if children != None:
                for child_proc in children:
                    if psutil.pid_exists(child_proc.pid):
                        one_of_children_alive = True
            if isinstance(children,list):
                if len(children) == 0:
                    os.kill(process.pid, signal.SIGKILL)
                    parent_alive = False
            at_least_one_alive = parent_alive or one_of_children_alive
        print("Exp {} of was finished".format(job.experiment_name))

    @staticmethod
    def check_stats_file_valid(job):
        stats_file = os.path.join(job.get_output_dir(),STATS_FILE)
        if os.path.exists(stats_file):
            if os.stat(stats_file).st_size == 0:
                return False
            return True
        return False

    def get_children_processes(self,parent_proc):
        try:
            parent = psutil.Process(parent_proc.pid)
        except psutil.NoSuchProcess:
            return
        return parent.children(recursive=True)

    def build_command_string(self,job):
        time.sleep(1)
        ts = time.time()
        st = ""#datetime.datetime.fromtimestamp(ts).strftime('%m-%d-%Y_%H-%M-%S')
        command_string = ""
        #adding gem5 exec file
        command_string += self.gem5_exec_file_str
        #adding output dir as job name:
        output_path = self.output_dir+"/"+job.experiment_name
        command_string += " --outdir="+output_path #+"_"+st+" "
        job.set_output_dir(output_path) #+"_"+st+" "
        if job.debug_flag != "x":
            command_string += " --debug-flag="+job.debug_flag+" "
        command_string += " " + job.config_file+" "
        adding_symbol = " "
        for field in job.attributes:
            if adding_symbol == "=":
                adding_symbol = " "
            else:
                adding_symbol = "="
            command_string+=field
            command_string+=adding_symbol
        return command_string


    def assign_proc_num(self):
        proc_num = 0
        process_num_list_sorted = self.processes_num_list
        process_num_list_sorted.sort()
        while(proc_num in process_num_list_sorted):
            proc_num += 1
        return proc_num

    def clear_finished_processes(self):
        survived_clear = []
        survived_clear_nums = []
        for idx,proc in enumerate(self.processes_list):
            proc.join(timeout=0)
            if not proc.is_alive():
                self.cpp_process_pid_list[self.processes_num_list[idx]] = -1
                for job in self.parallel_jobs:
                    if job.get_pid() == self.processes_num_list[idx]:
                        job.set_processs_id(None)
            else:
                survived_clear.append(proc)
                survived_clear_nums.append(self.processes_num_list[idx])
        self.processes_list = survived_clear
        self.processes_num_list = survived_clear_nums

    def get_jobs_tracker_filename(self):
        return os.path.join(self.output_dir,JOBS_TRACKING_FILE)

    # Getters
    def get_jobs_remained(self):
        remained = len(self.parallel_jobs)-self.job_iterator
        if remained < 0:
            return 0
        return len(self.parallel_jobs)-self.job_iterator

    def get_still_processing(self):
        return self.still_processing
    def get_processes_cpu_usage(self):
        processes_cpu_usage_list = list(range(0,self.numof_processes_avaialable))
        for idx,proc_attr in enumerate(processes_cpu_usage_list):
            processes_cpu_usage_list[idx] = (idx,0)
        cpu_usage_acc = 0
        for idx,pid in enumerate(self.cpp_process_pid_list):
            cpu_usage = 0
            if pid!=-1 :
                if(psutil.pid_exists(pid)):
                    proc_pid = psutil.Process(pid)
                    try:
                        proc_pid.cpu_percent(interval=None)
                        proc_data = {"pid": proc_pid.pid,
                        "status": proc_pid.status(),
                        "percent_cpu_used": proc_pid.cpu_percent(interval=0.2),
                        "percent_memory_used": proc_pid.memory_percent()}
                    except (psutil.ZombieProcess, psutil.AccessDenied, psutil.NoSuchProcess):
                        proc_data = None

                    if proc_data != None:#len(cpu_percentage) > 1:
                        cpu_usage = proc_data["percent_cpu_used"]
                 
                if idx < len(self.processes_num_list):
                    processes_cpu_usage_list[self.processes_num_list[idx]]=((self.processes_num_list[idx],cpu_usage))
            cpu_usage_acc = cpu_usage_acc + cpu_usage
        if cpu_usage_acc > 0:
            self.still_processing = True
        else:
            self.still_processing = False
        return processes_cpu_usage_list # process ids [which id] --> tuple (process id,cpu usage)

    def get_job_by_process_id(self,p_idx):
        if p_idx == None:
            return None
        if len(p_idx) > 0:
            for job in self.parallel_jobs:
                if job.get_pid() == p_idx[0]:
                    return job
        return None

    def get_num_of_processes(self):
        return self.numof_processes_avaialable

    def get_output_dir(self):
        return self.output_dir

    # Checks

    def jobs_remained_Q(self):
        return self.job_iterator < len(self.parallel_jobs)

    def available_processes_Q(self):
        return len(self.processes_list) < self.numof_processes_avaialable