def string_to_bool (string):
    return (string.upper() in ["TRUE", "YES"] or (string.isdigit() and int(string))) and True or False

def bool_to_string (boolval):
    return boolval and "true" or "false"
