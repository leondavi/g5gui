
CONFIG_FILE = 1
GEM5_EXECUTE_FILE = 2
OUTPUT_FILE = 3


#files_form_fill_dict["action_config"] = filename
#files_form_fill_dict["action_gem5_execute"] = filename
#files_form_fill_dict["output_file"] = filename


def correctness_check(files_dictionary):
    res = True
    Q = check_file_ending("x.py","py")
    if CONFIG_FILE in files_dictionary.keys():
        res &= check_file_ending(files_dictionary[CONFIG_FILE],"py")
    if GEM5_EXECUTE_FILE in files_dictionary.keys():
        res &= files_dictionary[GEM5_EXECUTE_FILE].endswith("gem5.opt")
    return res

# Inputs: filename and file type string without dot
def check_file_ending(filename, filetype):
    if filename.endswith("."+filetype):
        return True
    return False