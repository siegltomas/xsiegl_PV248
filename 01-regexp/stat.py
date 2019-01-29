#!/usr/bin/env python3

import sys
import re

# delete years in brackets
def delete_years(str_with_years):
    delete = False
    str_without_years = "" 
    for c in str_with_years:
        if c == '(':
            delete = True 
        elif c == ')':
            delete = False
        elif not delete:
            str_without_years += c
    return str_without_years
            
def add_to_dict(dictionary, item):
    if item in dictionary:
        dictionary[item] += 1
    else:
        dictionary[item] = 1

def get_century(s):
#    year = ""
#    if "th century" in s:
#        for c in s:
#            if c in "0123456789":
#                year += c
#        if len(year) > 0:
#            return int(year)
#        else:
#            return 0
#
#    for c in s:
#        if c in "0123456789":
#            year += c
#        elif len(year) != 4:
#            year = ""
#        else:
#            break
#    if len(year) != 4:
#        return 0

    if "th century" in s: # XXth century
        r = re.compile(r"(.*)(\d{2})(th century)")
        m = r.match(s)
        if m:
            century = int(m.group(2))
            return century
        else:
            return 0
    else: # year = 4-digits
        r = re.compile(r"(.*)(\d{4})")
        m = r.match(s)
        if m:
            year = int(m.group(2))
            century = ((year - 1) // 100) + 1
            return century
        else:
            return 0

# Prints how many pieces(songs) a composer composed.
def pieces_by_composer():
    dictionary = {}
    for line in file:
        if "Composer:" in line:
            s = line.replace("Composer:", " ")
            composer_list = s.split(";")
            for item in composer_list:
                item = delete_years(item)
                add_to_dict(dictionary, item.strip())
    for item in sorted(dictionary):
        if str(item) == "":
            continue
        s = str(item) + ": " + str(dictionary[item])
        print(s.strip())

# Prints how many pieces(songs) were composed in given century.
def pieces_by_century():
    dictionary = {}
    for line in file:
        if "Composition Year:" in line:
            century = get_century(line)
            if century == 0:
                continue
            add_to_dict(dictionary, century)
    for item in sorted(dictionary):
        s = str(item) + "th century: " + str(dictionary[item])
        print(s.strip())

# start
if len(sys.argv) < 3:
    print("argv error: not enough program arguments")
    print("invocation: ./stat.py ./file ./option")
    sys.exit()

option = sys.argv[2]
file = open(sys.argv[1], 'r')

# command line options
if option.lower() == "composer":
    pieces_by_composer()
elif option.lower() == "century":
    pieces_by_century()
else:
    print("invalid option")

file.close();
