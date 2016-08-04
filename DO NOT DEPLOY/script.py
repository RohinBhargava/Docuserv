from collections import OrderedDict
import re

fik = open('classes', 'r')
p = dict()
q = dict()

for i in fik:
    gutted = re.split('\.|[0-1]00 Units', i)
    splitted = gutted[0].split()
    if splitted[0].strip() not in p:
        p[splitted[0].strip()] = set()
        q[splitted[0].strip()] = set()
    if splitted[1].strip() not in p[splitted[0]]:
        p[splitted[0]].add(splitted[1].strip())
        q[splitted[0]].add((splitted[1].strip(), gutted[1].strip()))

ordered = OrderedDict(sorted(q.items()))

for i in ordered:
    ordered[i] = sorted(ordered[i])

print(ordered)
