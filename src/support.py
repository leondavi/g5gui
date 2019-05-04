def dict_check_key(dict, key):
    if key in dict.keys():
        return True
    else:
        return False


def dict_update_key_multival(dict,key,val):
    if dict_check_key(dict,key):
        dict[key].append(val)
    else:
        dict[key] = [val]
    return dict


def dict_remove_val_by_key_multival(dict,key,val):
    if dict_check_key(dict, key):
        if val in dict[key]:
            dict[key].remove(val)
    return dict