import re


#TODO: strings
def tokenize_string (statement):
    statement = re.sub ('\s+', ' ', statement)
    tokens = statement.split (' ')
    while '' in tokens:
        tokens.remove ('')
    return tokens


def parse_statement (statement):
    tokens = tokenize_string (statement)
    cmd = tokens.pop(0)
    return cmd, tokens


def parse_file (infile):
    if type (infile) == str:
        infile = open (infile, "rb")
    assert type (infile) == file, repr(infile)+" is not a file or valid filename!"
    
    line = infile.readline()
    while line != '':
        cmd, tokens = parse_statement (line)
        while len(tokens) and tokens[len(tokens)-1] == "\\":
            tokens.pop()
            line = infile.readline()
            assert line != '', "premature EOF!"
            tokens += tokenize_string (line)
        line = infile.readline()
        yield [cmd, tokens]
    
    infile.close()


