import os
try:
    import Tkinter as tk
    from Queue import Queue, Empty
except ImportError:
    import tkinter as tk # Python 3
    from queue import Queue, Empty # Python 3
    from tkinter import *
    from tkinter import filedialog
    from tkinter.ttk import *
    from tkinter import messagebox

from threading import Thread
from files_management import *
from definitions import *

from consoleCommands import ConsoleDisplay

GUI_VERSION = 0.1
BUTTON_ENDING_ROW = 4

def update_dict(Dictionary,Key,Value):
        Dictionary[Key] = Value

def show_filename_in_textbox(txtbox,filename):
    txtbox.config(state=NORMAL)
    txtbox.delete(1.0, END)
    txtbox.insert(END, filename)
    txtbox.config(state=DISABLED)


def gui_build():

    files_form_fill_dict = dict()
    def on_closing():
        save_obj(selected_debug_mode.get(),RADIO_SELECITON_FILE)
        window.destroy()

    def action_open_config_file():
        filename = filedialog.askopenfilename(initialdir=files_form_fill_dict.get(CONFIG_FILE,os.getcwd()))
        show_filename_in_textbox(config_file_textbox,filename)
        update_dict(files_form_fill_dict, CONFIG_FILE, filename)
        save_obj(files_form_fill_dict, SETTINGS_FILE)

    def action_gem5_execute_file():
        filename = filedialog.askopenfilename(initialdir=files_form_fill_dict.get(GEM5_EXECUTE_FILE,os.getcwd()))
        show_filename_in_textbox(gem5_exec_file_textbox,filename)
        print(selected_debug_mode.get())
        update_dict(files_form_fill_dict, GEM5_EXECUTE_FILE, filename)
        save_obj(files_form_fill_dict, SETTINGS_FILE)

    def action_output_file():
        filename = filedialog.asksaveasfilename(initialdir=files_form_fill_dict.get(OUTPUT_FILE,os.getcwd()))
        show_filename_in_textbox(output_file_textbox,filename)
        update_dict(files_form_fill_dict,OUTPUT_FILE,filename)
        save_obj(files_form_fill_dict, SETTINGS_FILE)

    def action_build_dir():
        dirname = filedialog.askdirectory(initialdir=files_form_fill_dict.get(BUILD_DIR,os.getcwd()))
        show_filename_in_textbox(gem5_build_dir_textbox, dirname)
        update_dict(files_form_fill_dict, BUILD_DIR, dirname)
        save_obj(files_form_fill_dict, SETTINGS_FILE)

    def action_build():
        save_obj(selected_debug_mode.get(), RADIO_SELECITON_FILE)
        console_disp.subprocess_cmd(files_form_fill_dict[BUILD_DIR], "scons build/RISCV/gem5.opt -j4")
        t = Thread(target=disable_buttons_thread)
        t.daemon = True  # close pipe if GUI process exits
        t.start()

    def disable_buttons_thread():
        button_run['state'] = DISABLED
        button_build['state'] = DISABLED
        while console_disp.get_command_process_active():
            pass
        button_build['state'] = NORMAL
        button_run['state'] = NORMAL

    def action_run():
        save_obj(selected_debug_mode.get(), RADIO_SELECITON_FILE)
        if correctness_check(files_form_fill_dict):
            save_obj(files_form_fill_dict,SETTINGS_FILE)
            console_disp.subprocess_cmd(files_form_fill_dict[BUILD_DIR], generate_run_string(selected_debug_mode.get()))
            t = Thread(target=disable_buttons_thread)
            t.daemon = True  # close pipe if GUI process exits
            t.start()
        else:
            messagebox.showinfo("Running Error","One or more files are missing or invalid!")
        #generate_run_string(selected_debug_mode.get())

    def action_stop():
        console_disp.kill_command_process()

    def generate_run_string(radio_but_res):
        last_radio_but_select = radio_but_res
        gem5_command = "."+files_form_fill_dict[GEM5_EXECUTE_FILE].replace(files_form_fill_dict[BUILD_DIR],"")
        output_file_command = files_form_fill_dict.get(OUTPUT_FILE,"")
        debug_command = DEBUG_OPTION + "=" + DebugModes[radio_but_res]
        if DebugModes[radio_but_res] == "No_Debug":
            debug_command = ""
        if DebugModes[radio_but_res] == "All_Traces": #TODO
            pass
        config_command = files_form_fill_dict[CONFIG_FILE].replace(files_form_fill_dict[BUILD_DIR],"")[1:]
        return gem5_command+" "+debug_command+" "+config_command+" | tee "+output_file_command

    window = Tk()
    window.protocol("WM_DELETE_WINDOW", on_closing)

    window.title("gem5 GUI app ver-"+str(GUI_VERSION))

    window.geometry('720x600')
    window.resizable(FALSE, FALSE)

    top_frame = Frame(window,height=200)
    top_frame.grid(row=1, column=0)
    middle_frame = Frame(window, height=5)
    middle_frame.grid(row=2, column=0)
    bottom_frame = Frame(window,height=200)
    bottom_frame.grid(row=3, column=0)


    rows_count = 0
    rows_count = rows_count + 1

    ######### Text Box ##########
    config_file_textbox = Text(top_frame, width=80, height=1, state=DISABLED)
    gem5_exec_file_textbox = Text(top_frame, width=80, height=1, state=DISABLED)
    output_file_textbox = Text(top_frame, width=80, height=1, state=DISABLED)
    gem5_build_dir_textbox = Text(top_frame, width=80, height=1, state=DISABLED)
    console_output_textbox = Text(bottom_frame,width=100,height=20, state=DISABLED)

    config_file_textbox.grid(row=rows_count, column=1)
    rows_count += 1
    gem5_exec_file_textbox.grid(row=rows_count, column=1)
    rows_count += 1
    output_file_textbox.grid(row=rows_count, column=1)
    rows_count += 1
    gem5_build_dir_textbox.grid(row=rows_count,column=1)

    console_output_textbox.grid(row=1,column=0)

    ###### Debug Mode Radio Buttons ######
    SeperatorLabel = Label(top_frame, text=" ")
    DebugModesLabel = Label(top_frame, text="Debug Modes:")
    SeperatorLabel2 = Label(top_frame, text=" ")
    ConsoleOutputLabel = Label(bottom_frame, text="Console output:")

    ConsoleOutputLabel.grid(row=0,column=0)

    selected_debug_mode = IntVar()
    last_radio_but_select = 0
    if check_file_exist(RADIO_SELECITON_FILE):
        last_radio_but_select = load_obj(RADIO_SELECITON_FILE)
        last_radio_but_select = 0 if last_radio_but_select==None else last_radio_but_select
        selected_debug_mode.set(last_radio_but_select)



    RADIO_BUTTON_WIDTH = 10 #Definition

    radio_buttons_vec = []
    for index in range (0,len(DebugModes)):
        radio_buttons_vec.append(Radiobutton(top_frame, width=RADIO_BUTTON_WIDTH, text=DebugModes[index], value=index, variable=selected_debug_mode))




    ######### Buttons ##########

    # btn1 = Button(window, text="Click Me", command=clicked)
    SeperatorLabel_exit_run = Label(window, text=" ")

    button_config_file = Button(top_frame, text='Config File', command=action_open_config_file)
    button_gem5_exec = Button(top_frame, text='gem5 Exec', command=action_gem5_execute_file)
    button_output_file = Button(top_frame, text='Output File', command=action_output_file)
    button_build_dir = Button(top_frame, text='gem5 Dir', command=action_build_dir)

    button_run = Button(middle_frame, text='Run', command=action_run)
    button_build = Button(middle_frame, text='Build', command=action_build)
    button_stop = Button(middle_frame, text='Stop', command=action_stop)

    ###### Buttons grid allocation #######
    rows_starting_idx = 1

    button_config_file.grid(row=rows_starting_idx, column=0)
    rows_starting_idx += 1
    button_gem5_exec.grid(row=rows_starting_idx, column=0)
    rows_starting_idx += 1
    button_output_file.grid(row=rows_starting_idx, column=0)
    rows_starting_idx += 1
    button_build_dir.grid(row=rows_starting_idx,column=0)
    rows_starting_idx += 1

    ###### RadioButtons grid allocation #######
    SeperatorLabel.grid(row=rows_starting_idx, column=0)  # Seperator
    rows_starting_idx += 1
    DebugModesLabel.grid(row=rows_starting_idx, column=0)  # Debug mode title
    rows_starting_idx += 1
    SeperatorLabel2.grid(row=rows_starting_idx, column=0)
    rows_starting_idx += 1

    cols_idx = 0
    # Radio buttons locations set:
    for idx, radiobutt in enumerate(radio_buttons_vec):
        radiobutt.grid(row=rows_starting_idx, column=cols_idx)
        if (idx % 2 == 1):
            rows_starting_idx += 1
        cols_idx = (cols_idx + 1) % 2

    RUN_AND_EXIT_BUTTONS_ROWS = 0 #Definition

    button_run.grid(row=RUN_AND_EXIT_BUTTONS_ROWS,column=10)
    button_build.grid(row=RUN_AND_EXIT_BUTTONS_ROWS,column=11)
    button_stop.grid(row=RUN_AND_EXIT_BUTTONS_ROWS,column=12)

    # loading dictionary if existed
    if check_file_exist(SETTINGS_FILE):
        files_form_fill_dict = load_obj(SETTINGS_FILE)
        show_filename_in_textbox(config_file_textbox,files_form_fill_dict.get(CONFIG_FILE,""))
        show_filename_in_textbox(gem5_exec_file_textbox,files_form_fill_dict.get(GEM5_EXECUTE_FILE,""))
        show_filename_in_textbox(output_file_textbox,files_form_fill_dict.get(OUTPUT_FILE,""))
        show_filename_in_textbox(gem5_build_dir_textbox, files_form_fill_dict.get(BUILD_DIR,""))

    console_disp = ConsoleDisplay(bottom_frame,console_output_textbox)


    window.mainloop()

    return True