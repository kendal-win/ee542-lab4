#!/usr/bin/env python3

import sys
#from collections import defaultdict

#counts = defaultdict(int)
current_char = None
current_count = 0


for line in sys.stdin:
    char_code, val = line.rstrip('\n').split('\t')
    char_code = int(char_code)
    val = int(val)

    if char_code == current_char:
        current_count += val
    else:
        if current_char is not None:
            print(f"{chr(current_char)}\t{current_count}")

        current_char = char_code
        current_count = val

if current_char is not None:
    print(f"{chr(current_char)}\t{current_count}")

    