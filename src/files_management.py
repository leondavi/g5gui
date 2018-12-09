import pickle
import os

CONFIG_FILE = 1
GEM5_EXECUTE_FILE = 2
OUTPUT_FILE = 3
BUILD_DIR = 4

SETTINGS_FILE = os.path.join(os.pardir, "files_dict")

#files_form_fill_dict["action_config"] = filename
#files_form_fill_dict["action_gem5_execute"] = filename
#files_form_fill_dict["output_file"] = filename


def correctness_check(files_dictionary):
    res = False if len(files_dictionary) < 3 else True
    if CONFIG_FILE in files_dictionary.keys():
        res &= check_file_ending(files_dictionary[CONFIG_FILE],"py")
        res &= isinstance(files_dictionary[CONFIG_FILE],str)
    else:
        return False
    if GEM5_EXECUTE_FILE in files_dictionary.keys():
        res &= files_dictionary[GEM5_EXECUTE_FILE].endswith("gem5.opt")
        res &= isinstance(files_dictionary[GEM5_EXECUTE_FILE],str)
    else:
        return False
    if OUTPUT_FILE in files_dictionary.keys():
        if files_dictionary.get(OUTPUT_FILE,"") == "":
            return False
        res &= isinstance(files_dictionary[OUTPUT_FILE],str)
    else:
        return False

    res = res if OUTPUT_FILE in files_dictionary.keys() else False

    return res

# Inputs: filename and file type string without dot
def check_file_ending(filename, filetype):
    if filename.endswith("."+filetype):
        return True
    return False

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    try:
        with open(name + '.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def check_file_exist(name):
    try:
        return os.path.isfile(SETTINGS_FILE+ '.pkl')
    except FileNotFoundError:
        return None
