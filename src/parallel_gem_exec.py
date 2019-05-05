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

JOBS_TRACKING_FILE = "job_tracker.txt"

class parallel_gem_exec():
    def __init__(self,parallel_jobs,form_dict,output_dir,numof_processes_avaialable = 1):
        self.parallel_jobs = parallel_jobs
        self.numof_processes_avaialable = numof_processes_avaialable
        self.processes_list = []
        self.processes_num_list = []
        self.processes_available_list = self.processes_list
        self.jobs_remain = len(parallel_jobs)
        self.job_iterator = 0
        self.gem5_dir_str = form_dict[BUILD_DIR]
        self.gem5_exec_file_str = form_dict[GEM5_EXECUTE_FILE]
        self.output_dir = output_dir
        self.cpp_process_pid_list = [-1]*numof_processes_avaialable
        self.jobs_tracker = os.path.join(self.output_dir, JOBS_TRACKING_FILE)


    def allocate_jobs_to_processes(self):
        self.jobs_track_file = open(self.jobs_tracker, "a+")
        self.clear_finished_processes()
        while self.available_processes_Q() and self.jobs_remain > 0 and self.job_iterator<len(self.parallel_jobs):
            self.processes_num_list.append(self.assign_proc_num())
            self.processes_num_list[-1]
            self.parallel_jobs[self.job_iterator]
            self.parallel_jobs[self.job_iterator].set_processs_id(self.processes_num_list[-1])
            job = self.parallel_jobs[self.job_iterator]
            command_string = self.build_command_string(job)
            print("Job name: " + job.experiment_name)
            print("Command executed: " + command_string)
            cpp_process = Popen(command_string, cwd=self.gem5_dir_str, stdout=PIPE, shell=True, preexec_fn=None)
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

    def kill_all_processes(self):
        for proc in self.processes_list:
            if proc.is_alive:
                os.kill(proc.pid,signal.SIGKILL)
        os.system("killall gem5.opt")
        self.jobs_remain = 0
        self.parallel_jobs = []

    def task(self,job,process):
        children = self.get_children_processes(process)
        at_least_one_alive = True
        while at_least_one_alive:
            time.sleep(0.5)
            parent_alive = psutil.pid_exists(process.pid)
            one_of_children_alive = False
            for child_proc in children:
                if psutil.pid_exists(child_proc.pid):
                    one_of_children_alive = True
            at_least_one_alive = parent_alive or one_of_children_alive

    def get_children_processes(self,parent_proc):
        try:
            parent = psutil.Process(parent_proc.pid)
        except psutil.NoSuchProcess:
            return
        return parent.children(recursive=True)

    def build_command_string(self,job):
        time.sleep(1)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%m-%d-%Y_%H-%M-%S')
        command_string = ""
        #adding gem5 exec file
        command_string += self.gem5_exec_file_str
        #adding output dir as job name:
        command_string += " --outdir="+self.output_dir+"/p-"+str(job.get_pid())+"_"+job.experiment_name+"_"+st+" "
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
                self.jobs_remain -= 1
                self.cpp_process_pid_list[self.processes_num_list[idx]] = -1
            else:
                survived_clear.append(proc)
                survived_clear_nums.append(self.processes_num_list[idx])
        self.processes_list = survived_clear
        self.processes_num_list = survived_clear_nums

    def get_jobs_tracker_filename(self):
        return os.path.join(self.output_dir,JOBS_TRACKING_FILE)

    # Getters
    def get_jobs_remained(self):
        return self.jobs_remain

    def get_processes_cpu_usage(self):
        processes_cpu_usage_list = list(range(0,self.numof_processes_avaialable))
        for idx,proc_attr in enumerate(processes_cpu_usage_list):
            processes_cpu_usage_list[idx] = (idx,0)
        for idx,pid in enumerate(self.cpp_process_pid_list):
            cpu_usage = 0
            if pid!=-1 :
                if(psutil.pid_exists(pid)):
                    p = psutil.Process(pid)
                    sub_p = subprocess.Popen("top -b -n 1 -p %d -d 10 | tail -n 1 | head -n 1 | awk '{print $1, $9}'" % pid,
                                                     shell=True,stdout=subprocess.PIPE)
                    cpu_percentage = sub_p.stdout.read()
                    #time.sleep(0.1)
                    if len(cpu_percentage) > 1:
                        try:
                            cpu_usage = int(float(cpu_percentage.decode("utf-8").replace("\n", "").split(" ")[1]))
                        except ValueError:
                            cpu_usage = 0
                    else:
                        cpu_usage = 0
                if idx < len(self.processes_num_list):
                    processes_cpu_usage_list[self.processes_num_list[idx]]=((self.processes_num_list[idx],cpu_usage))
        return processes_cpu_usage_list


    # Checks

    def jobs_remained_Q(self):
        return self.jobs_remain > 0

    def available_processes_Q(self):
        return len(self.processes_list) < self.numof_processes_avaialable