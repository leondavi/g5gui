
import sys
from subprocess import Popen,PIPE
from threading import Thread
from itertools import islice
import logging
from tkinter import *


try:
    from queue import Queue, Empty
    import Tkinter as tk
except ImportError:
    from queue import Queue, Empty  # Python 3
    import tkinter as tk # Python 3


class Gem5ConsoleCommands:

    def build(self,scons_dir,textbox_output):
        return 0

    def optgem5(self,gem5_exec,debug_mode,config_file,output_file):
        return 0

def iter_except(function, exception):

    try:
        while True:
            yield function()
    except exception:
        return

class ConsoleDisplay:
    def __init__(self, tk_frame, tk_textbox_output):
        self.tk_frame = tk_frame
        self.tk_txt_out = tk_textbox_output
        self.process = None
        # launch thread to read the subprocess output
        #   (put the subprocess output into the queue in a background thread,
        #    get output from the queue in the GUI thread.
        #    Output chain: process.readline -> queue -> label)
        self.output = ""

    def get_command_process_active(self):
        if self.process.poll()==None:
            return True
        return False

    def subprocess_cmd(self,workingdir,command):
        self.output=""
        if isinstance(workingdir,str) and isinstance(command,str):
            self.process = Popen(command,cwd=workingdir, stdout=PIPE, shell=True)
        else:
            logging.error("Error, working dir or command aren't string type")
        #proc_stdout = self.process.communicate()[0].strip()
        #print(proc_stdout)
        q = Queue(maxsize=1024)  # limit output buffering (may stall subprocess)
        t = Thread(target=self.reader_thread, args=[q])
        t.daemon = True  # close pipe if GUI process exits
        t.start()

        self.update(q)  # start update loop

    def reader_thread(self, q):
        """Read subprocess output and put it into the queue."""
        try:
            with self.process.stdout as pipe:
                for line in iter(pipe.readline, b''):
                    q.put(line)
        finally:
            q.put(None)

    def update(self, q):
        """Update GUI with items from the queue."""
        for line in iter_except(q.get_nowait, Empty): # display all content
            if line is None:
                self.tk_frame.after(500, self.update, q)  # schedule next update
                return
            else:
                #self.tk_txt_out['text'] = line # update GUI
               # self.tk_txt_out.insert(END,line)
                self.insert_line_to_output(line,18)
                self.show_filename_in_textbox(self.tk_txt_out,self.output)
                break # display no more than one line per 40 milliseconds

        self.tk_frame.after(40, self.update, q) # schedule next update

    def quit(self):
        self.process.kill() # exit subprocess if GUI is closed (zombie!)
        self.tk_frame.destroy()

    def show_filename_in_textbox(self,txtbox, filename):
        txtbox.config(state=NORMAL)
        txtbox.delete(1.0, END)
        txtbox.insert(END, filename)
        txtbox.config(state=DISABLED)

    def insert_line_to_output(self,line,max_lines):
        self.output += line.decode()
        diff_lines = self.output.count('\n') - max_lines
        if diff_lines > 0:
            self.output="\n".join(self.output.split("\n")[diff_lines:])
