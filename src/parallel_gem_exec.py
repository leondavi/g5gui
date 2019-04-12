from parallel_gem_parser import *
from multiprocessing import Process

class parallel_gem_exec():
    def __init__(self,parallel_jobs,gem5_dir,numof_processes_avaialable = 1):
        self.parallel_jobs = parallel_jobs
        self.gem5_dir = gem5_dir
        self.numof_processes_avaialable = numof_processes_avaialable
        self.processes_list = []
        self.processes_available_list = self.processes_list
        self.jobs_remain = len(parallel_jobs)
        self.job_iterator = 0

    def allocate_jobs_to_processes(self):
        self.clear_finished_processes()
        while self.available_processes_Q() and self.jobs_remain > 0 :
            newProc = Process(target=self.task)
            self.job_iterator += 1
            self.processes_list.append(newProc)
            newProc.start()

    def task(self):
        pass


    def clear_finished_processes(self):
        survived_clear = []
        for idx,proc in enumerate(self.processes_list):
            proc.join(timeout=0)
            if not proc.is_alive():
                self.jobs_remain -= 1
            else:
                survived_clear.append(proc)
        self.processes_list = survived_clear


    # Getters
    def get_jobs_remained(self):
        return self.jobs_remain

    # Checks

    def jobs_remained_Q(self):
        return self.jobs_remain > 0

    def available_processes_Q(self):
        return len(self.processes_list) < self.numof_processes_avaialable