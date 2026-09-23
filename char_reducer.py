#!/usr/bin/env python3

import sys
from collections import defaultdict

counts = defaultdict(int)

for line in sys.stdin:
    char, val = linerstrip('\n').split('\t')
    counts[char] += int(val)

for char, count in counts.items():
    print(f"{char}\t{count}")
    