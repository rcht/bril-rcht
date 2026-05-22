import json
# import time
from copy import copy
import sys
IR = json.load(sys.stdin)

PREV_IR = copy(IR)
OPT_IR = {}

# remove variables unused in destination registers

while True:
    OPT_IR = copy(PREV_IR)
    OPT_IR['functions'] = []

    for function in PREV_IR['functions']:
        OPT_IR['functions'].append(copy(function))
        OPT_IR['functions'][-1]['instrs'] = []
        used = set()
        for instr in function["instrs"]:
            for var in instr.get("args", []):
                used.add(var)
        for instr in function["instrs"]:
            if instr.get('dest') and instr['dest'] not in used:
                continue
            else:
                OPT_IR['functions'][-1]['instrs'].append(copy(instr))

    
    if OPT_IR == PREV_IR:
        break

    PREV_IR = copy(OPT_IR)


print(json.dumps(OPT_IR))
