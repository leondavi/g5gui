from parallel_gem_parser import *
from multiprocessing import Process
from subprocess import Popen,PIPE
import psutil
import os
import time
import signal
from files_management import *
import datetime

class parallel_gem_exec():
    def __init__(self,parallel_jobs,form_dict,numof_processes_avaialable = 1):
        self.parallel_jobs = parallel_jobs
        self.numof_processes_avaialable = numof_processes_avaialable
        self.processes_list = []
        self.processes_num_list = []
        self.processes_available_list = self.processes_list
        self.jobs_remain = len(parallel_jobs)
        self.job_iterator = 0
        self.gem5_dir_str = form_dict[BUILD_DIR]
        self.gem5_exec_file_str = form_dict[GEM5_EXECUTE_FILE]

    def allocate_jobs_to_processes(self):
        self.clear_finished_processes()
        while self.available_processes_Q() and self.jobs_remain > 0 :
            newProc = Process(target=self.task,args=[self.parallel_jobs[self.job_iterator]])
            self.job_iterator += 1
            self.processes_list.append(newProc)
            self.processes_num_list.append(self.assign_proc_num())
            newProc.start()

    def kill_all_processes(self):
        for proc in self.processes_list:
            if proc.is_alive:
                os.kill(proc.pid,signal.SIGKILL)
        os.system("killall gem5.opt")

    def task(self,job):
        command_string = self.build_command_string(job)
        process = Popen(command_string, cwd=self.gem5_dir_str, stdout=PIPE, shell=True, preexec_fn=os.setsid)
        print("Job name: "+job.experiment_name)
        print("Command executed: "+command_string)
        alive = process.poll() == None
        while alive:
            time.sleep(0.5)
            alive = process.poll() == None


    def build_command_string(self,job):
        time.sleep(1)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%m-%d-%Y_%H-%M-%S')
        command_string = ""
        #adding gem5 exec file
        command_string += self.gem5_exec_file_str
        #adding output dir as job name:
        command_string += " --outdir=statistics/"+job.experiment_name+"_"+st+" "
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
        while(proc_num in self.processes_num_list):
            proc_num += 1
        return proc_num

    def clear_finished_processes(self):
        survived_clear = []
        survived_clear_nums = []
        for idx,proc in enumerate(self.processes_list):
            proc.join(timeout=0)
            if not proc.is_alive():
                self.jobs_remain -= 1
            else:
                survived_clear.append(proc)
                survived_clear_nums.append(self.processes_num_list[idx])
        self.processes_list = survived_clear
        self.processes_num_list = survived_clear_nums


    # Getters
    def get_jobs_remained(self):
        return self.jobs_remain

    def get_processes_cpu_usage(self):
        processes_cpu_usage_list = []
        for idx,proc in enumerate(self.processes_list):
            cpu_usage = 0
            if(psutil.pid_exists(proc.pid)):
                p = psutil.Process(proc.pid)
                cpu_usage = p.cpu_percent()
                if cpu_usage == None:
                    cpu_usage = 0
                else:
                    cpu_usage = 100
            processes_cpu_usage_list.append((self.processes_num_list[idx],cpu_usage))
        return processes_cpu_usage_list


    # Checks

    def jobs_remained_Q(self):
        return self.jobs_remain > 0

    def available_processes_Q(self):
        return len(self.processes_list) < self.numof_processes_avaialable