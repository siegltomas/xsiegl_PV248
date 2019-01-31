#!/usr/bin/env python3

import sys
import re
from numpy import linalg
lowercase_letters = "abcdefghijklmnopqrstuvwxyz"

def read_input():
    if len(sys.argv) < 2:
        print("argv error: not enough program arguments")
        print("invocation: ./eqn.py input_file")
        sys.exit()

    coef_matrix = []
    aug_matrix = []
    right_side = []
    var_set = set()

    file = open(sys.argv[1], 'r')
    for line in file:
        (coef_row, aug_row, eqn_set) = process_eqn(line)
        coef_matrix.append(coef_row)
        aug_matrix.append(aug_row)
        right_side.append(aug_row[len(aug_row) - 1])
        var_set = var_set.union(eqn_set)
    file.close()
    return (coef_matrix, aug_matrix, right_side, var_set)

def process_eqn(line):
    coef_row = [ 0 for i in range(len(lowercase_letters)) ]
    aug_row = [ 0 for i in range(len(lowercase_letters) + 1) ]
    eqn_set = set()

    line = line.strip()
    print("line:" + line) # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    r = re.compile(r"(.*)=(.*)")
    m = r.match(line)
    if m:
        right_string = m.group(2)
        right_string = right_string.strip()
        print("right_string:" + right_string) # !!!!!!!!!!!!!!!!!!!!!
        const = int(right_string)

        coef_line = m.group(1)
        coef_line = coef_line.strip()
        print("coef_line:" + coef_line) # !!!!!!!!!!!!!!!!!!!!!
        tokens = coef_line.split(" ")
        tokens.insert(0, "+") # operator coef operator coef ...
        sign = None
        coef = None
        print("tokens:", tokens) # !!!!!!!!!!!!!!!!!!!!!1
        for token in tokens:
            token = token.strip()
            if token == "":
                continue
            if sign != None:
                r = re.compile(r"(\d*)(\w)")
                m = r.match(token)
                if m:
                    str_coef = m.group(1)
                    str_coef = str_coef.strip()
                    if str_coef == "":
                        str_coef = "1"
                    print("str_coef:", str_coef) # !!!!!!!!!!!!!!!!!!!!!1
                    coef = sign * int(str_coef)
                    var = m.group(2)
                    var = var.strip()
                    print("var:", var) # !!!!!!!!!!!!!!!!!!!!!1
                    coef_row[ord(var) - ord("a")] = coef
                    aug_row[ord(var) - ord("a")] = coef
                    eqn_set.add(var)
                    print("eqn_set:", eqn_set) # !!!!!!!!!!!!!!!!!!!!!
                else:
                    print("This should not happen: re.compile - token")
                sign = None
            elif "-" in token:
                sign = -1
            else:
                sign = 1
        aug_row[len(aug_row) - 1] = const
    else: 
        print("This should not happen: re.compile - =")
    return (coef_row, aug_row, eqn_set)

def reverse_string(s):
    s_reversed = ""
    for c in s:
        s_reversed = c + s_reversed
    return s_reversed

def del_col_in_matrix(matrix, col):
    for row in matrix:
        del row[col]
    return matrix

def matrix_to_square_matrix(matrix, var_set):
    lowercase_reverse = reverse_string(lowercase_letters)
    for var in lowercase_reverse:
        if var not in var_set:
            matrix = del_col_in_matrix(matrix, ord(var) - ord("a"))
    return matrix

def main():
    (coef_matrix, aug_matrix, right_side, var_set) = read_input()
    print("coef_matrix:", coef_matrix) # !!!!!!!!!!!!!!!!!!!!!
    print("aug_matrix:", aug_matrix) # !!!!!!!!!!!!!!!!!!!!!
    print("right_side:", right_side) # !!!!!!!!!!!!!!!!!!!!!
    print("var_set:", var_set) # !!!!!!!!!!!!!!!!!!!!!

    coef_matrix = matrix_to_square_matrix(coef_matrix, var_set)
    aug_matrix = matrix_to_square_matrix(aug_matrix, var_set)
    print("square coef_matrix:", coef_matrix) # !!!!!!!!!!!!!!!!!!!!!
    print("square aug_matrix:", aug_matrix) # !!!!!!!!!!!!!!!!!!!!!

    coef_rank = linalg.matrix_rank(coef_matrix)
    aug_rank = linalg.matrix_rank(aug_matrix)
    var_count = len(var_set)

    print("coef_rank:", coef_rank) # !!!!!!!!!!!!!!!!!!!!!
    print("aug_rank:", aug_rank) # !!!!!!!!!!!!!!!!!!!!!
    print("var_count:", var_count) # !!!!!!!!!!!!!!!!!!!!!

    if coef_rank != aug_rank:
        print("no solution")
    elif coef_rank == var_count:
        result = list(linalg.solve(coef_matrix, right_side))
        for c in lowercase_letters:
            if c in var_set:
                print(


    else:
        print("solution space dimension: " + str(var_count - coef_rank))

'''
        var_result = []
        for i, var in enumerate(all_variables_ordered.items()):
            var_result.append(var[0] + ' = ' + str(x[i]))

        print('solution: ' + ', '.join(var_result))
'''


# start
main()

#####################################################################
