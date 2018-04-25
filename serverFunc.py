import re

def validate_email(addr):
    if len(addr) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\."
                    "([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",addr) != None:
            return 1
    return 0

def format_space(st):
    if re.match(r'^\s+$',st):
        return(0)
    args = re.split(r'\s+',st)
    length = len(args)
    if len(args[0])==0:
        args.pop(0)
        length=length-1
    if len(args[length-1])==0:
        args.pop(length-1)
        length=length-1
    format_st = args[0]
    i=1
    while i<length:
        format_st = format_st+" "+args[i]
        i = i+1
    return format_st