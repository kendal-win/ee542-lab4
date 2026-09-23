#!/usr/bin/env python3

import sys
from collections import defaultdict

counts = defaultdict(int)

#does local aggregation inside each mapper

for line in sys.stdin:
    for char in line.rstrip('\n'):
        counts[ord(char)] += 1

for char_code, count in counts.items():
    print(f"{char_code}\t{count}")


        