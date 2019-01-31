#!/usr/bin/env python3

import sys
import scorelib

# start
if len(sys.argv) < 2:
    print("argv error: not enough program arguments")
    print("invocation: ./test.py ./file")
    sys.exit()

for print_instance in scorelib.load(sys.argv[1])
    print_instance.format()
    print("\n")
