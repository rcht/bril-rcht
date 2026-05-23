import json
# import time
from copy import copy
import sys
# from get_basic_blocks import get_basic_blocks
IR = json.load(sys.stdin)

PREV_IR = copy(IR)
OPT_IR = {}


while True:
    OPT_IR = copy(PREV_IR)
    OPT_IR['functions'] = []

    # remove variables unused in destination registers
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


    # remove unused assigns from each basic block

    # this code fails one of the tests in the suite related to speculative execution because the basic block extractor can't handle that. thus i am removing it from here but i keep it commented as progress.
    '''
    IR_BB = get_basic_blocks(OPT_IR)

    for i in range(len(OPT_IR['functions'])):
        OPT_IR['functions'][i]['instrs'] = []

    for func_index, function in enumerate(IR_BB['functions']):
        for block in function['blocks']:
            instrs_include = list(range(len(block['instrs'])))
            last_used = {} # dest -> instruction number mapping
            for index, instr in enumerate(block['instrs']):
                # check if used
                for arg in instr.get('args', []):
                    if arg in last_used:
                        last_used.pop(arg)
                # check if assigned
                if instr.get('dest'):
                    dest = instr['dest']
                    if dest in last_used:
                        instrs_include.remove(last_used[dest])
                    last_used[dest] = index
            OPT_IR['functions'][func_index]['instrs'].extend([block['instrs'][i] for i in instrs_include])
    '''


    if OPT_IR == PREV_IR:
        break

    PREV_IR = copy(OPT_IR)


print(json.dumps(OPT_IR))
