import os
import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from tkinter import messagebox
from files_management import *
from definitions import *

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

    def action_open_config_file():
        filename = filedialog.askopenfilename()
        show_filename_in_textbox(config_file_textbox,filename)
        update_dict(files_form_fill_dict, CONFIG_FILE, filename)

    def action_gem5_execute_file():
        filename = filedialog.askopenfilename()
        show_filename_in_textbox(gem5_exec_file_textbox,filename)
        print(selected_debug_mode.get())
        update_dict(files_form_fill_dict, GEM5_EXECUTE_FILE, filename)

    def action_output_file():
        filename = filedialog.asksaveasfilename()
        show_filename_in_textbox(output_file_textbox,filename)
        update_dict(files_form_fill_dict,OUTPUT_FILE,filename)

#############################
#   R U N   M E T H O D     #
#############################
    def action_run():
        if correctness_check(files_form_fill_dict):
            save_obj(files_form_fill_dict,SETTINGS_FILE)
        else:
            messagebox.showinfo("Running Error","One or more files are missing or invalid!")
        print(selected_debug_mode.get())

    if tkinter.TclVersion < 8.5:
        print("Please install python3-tk using apt install.")
        print("Exiting")
        return


    window = Tk()

    window.title("gem5 GUI app ver-"+str(GUI_VERSION))

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

    radio_buttons_vec = []
    for index in range (0,len(DebugModes)):
        radio_buttons_vec.append(Radiobutton(window, width=RADIO_BUTTON_WIDTH, text=DebugModes[index], value=index, variable=selected_debug_mode))

    rows_starting_idx = BUTTON_ENDING_ROW
    SeperatorLabel.grid(row=rows_starting_idx, column=0) #Seperator
    rows_starting_idx += 1
    DebugModesLabel.grid(row=rows_starting_idx, column=0) #Debug mode title
    rows_starting_idx += 1
    SeperatorLabel2.grid(row=rows_starting_idx, column=0)
    rows_starting_idx += 1

    cols_idx = 0
    #Radio buttons locations set:
    for idx,radiobutt in enumerate(radio_buttons_vec):
        radiobutt.grid(row=rows_starting_idx, column=cols_idx)
        if (idx % 2 == 1):
            rows_starting_idx+=1
        cols_idx = (cols_idx + 1) % 2

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

    # loading dictionary if existed
    if check_file_exist(SETTINGS_FILE):
        files_form_fill_dict = load_obj(SETTINGS_FILE)
        show_filename_in_textbox(config_file_textbox,files_form_fill_dict[CONFIG_FILE])
        show_filename_in_textbox(gem5_exec_file_textbox,files_form_fill_dict[GEM5_EXECUTE_FILE])
        show_filename_in_textbox(output_file_textbox,files_form_fill_dict[OUTPUT_FILE])

    window.mainloop()

    return True