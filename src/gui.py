import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from files_management import *

from src.files_management import CONFIG_FILE

BUTTON_ENDING_ROW = 4

files_form_fill_dict = dict()

def gui_build():

    def action_open_config_file():
        filename = filedialog.askopenfilename()
        config_file_textbox.config(state=NORMAL)
        config_file_textbox.insert(END, filename)
        config_file_textbox.config(state=DISABLED)
        files_form_fill_dict[CONFIG_FILE] = filename

    def action_gem5_execute_file():
        filename = filedialog.askopenfilename()
        gem5_exec_file_textbox.config(state=NORMAL)
        gem5_exec_file_textbox.insert(END, filename)
        gem5_exec_file_textbox.config(state=DISABLED)
        print(selected_debug_mode.get())
        files_form_fill_dict[GEM5_EXECUTE_FILE] = filename

    def action_output_file():
        filename = filedialog.askopenfilename()
        output_file_textbox.config(state=NORMAL)
        output_file_textbox.insert(END, filename)
        output_file_textbox.config(state=DISABLED)
        files_form_fill_dict[OUTPU_FILE] = filename

    def action_run():
        correctness_check(files_form_fill_dict)
        print(selected_debug_mode.get())

    if tkinter.TclVersion < 8.5:
        print("Please install python3-tk using apt install.")
        print("Exiting")
        return

    window = Tk()

    window.title("Welcome to gem5 GUI app")

    window.geometry('800x500')
    window.resizable(FALSE, FALSE)

    rows_count = 0
    rows_count = rows_count + 1

    ######### Text Box ##########
    config_file_textbox = Text(window, width=60, height=1, state=DISABLED)
    gem5_exec_file_textbox = Text(window, width=60, height=1, state=DISABLED)
    output_file_textbox = Text(window, width=60, height=1, state=DISABLED)

    config_file_textbox.grid(row=rows_count, column=2)
    rows_count += 1
    gem5_exec_file_textbox.grid(row=rows_count, column=2)
    rows_count += 1
    output_file_textbox.grid(row=rows_count, column=2)

    ###### Debug Mode Radio Buttons ######
    SeperatorLabel = Label(window, text=" ")
    DebugModesLabel = Label(window, text="Debug Modes:")
    SeperatorLabel2 = Label(window, text=" ")

    selected_debug_mode = IntVar()
    RADIO_BUTTON_WIDTH = 10
    rbutt_acitivty = Radiobutton(window, width=RADIO_BUTTON_WIDTH, text="Activity", value=1,
                                 variable=selected_debug_mode)
    rbutt_branch = Radiobutton(window, width=RADIO_BUTTON_WIDTH, text="Branch", value=2, variable=selected_debug_mode)
    rbutt_minorcpu = Radiobutton(window, width=RADIO_BUTTON_WIDTH, text="MinorCPU", value=3,
                                 variable=selected_debug_mode)
    rbutt_decode = Radiobutton(window, width=RADIO_BUTTON_WIDTH, text="Decode", value=4, variable=selected_debug_mode)

    rows_starting_idx = BUTTON_ENDING_ROW
    columns_starting_idx = 0
    SeperatorLabel.grid(row=rows_starting_idx, column=0)
    rows_starting_idx += 1
    DebugModesLabel.grid(row=rows_starting_idx, column=0)
    rows_starting_idx += 1
    SeperatorLabel2.grid(row=rows_starting_idx, column=0)
    rows_starting_idx += 1
    rbutt_acitivty.grid(row=rows_starting_idx, column=0)
    rbutt_branch.grid(row=rows_starting_idx, column=1)
    rows_starting_idx += 1
    rbutt_minorcpu.grid(row=rows_starting_idx, column=0)
    rbutt_decode.grid(row=rows_starting_idx, column=1)
    rows_starting_idx += 1

    ######### Buttons ##########

    # btn1 = Button(window, text="Click Me", command=clicked)
    SeperatorLabel_exit_run = Label(window, text=" ")

    button_config_file = Button(window, text='Config File', command=action_open_config_file)
    button_gem5_exec = Button(window, text='gem5 Exec', command=action_gem5_execute_file)
    button_output_file = Button(window, text='Output File', command=action_output_file)

    button_exit = Button(window, text='Exit', command=window.destroy)
    button_run = Button(window, text='Run', command=action_run)

    button_config_file.grid(row=1, column=1)
    button_gem5_exec.grid(row=2, column=1)
    button_output_file.grid(row=3, column=1)

    SeperatorLabel_exit_run.grid(row=49)
    button_run.grid(row=50, column=30)
    button_exit.grid(row=50,column=0)

    window.mainloop()

    return True