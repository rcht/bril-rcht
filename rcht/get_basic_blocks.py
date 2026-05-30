# Usage: python get_basic_blocks.py < bril_ir_json_file
# prints and names the basic blocks 

import json
import sys
from copy import copy

def get_basic_blocks(IR):
    IR_BB = copy(IR)
    IR_BB['functions'] = []
    for function in IR['functions']:
        IR_BB['functions'].append(copy(function))
        IR_BB['functions'][-1]['blocks'] = []
        count = 0
        current_block = []
        num_instructions = len(function['instrs'])
        for index, instr in enumerate(function['instrs']):
            # if label then end the current block and start a new one
            if instr.get("label") and current_block:
                IR_BB['functions'][-1]['blocks'].append(
                    {"instrs": current_block[:], 
                     "name": f"bb{count}"}
                )
                count += 1
                current_block= []

            current_block.append(copy(instr))

            # if branch, jump or ret then end the block
            END_TYPES = ['br', 'jmp', 'ret']
            if instr.get("op", "") in END_TYPES:
                IR_BB['functions'][-1]['blocks'].append(
                    {"instrs": current_block[:], 
                     "name": f"bb{count}"}
                )
                count += 1
                current_block= []
                continue

            # if last instruction then end the block
            if index < num_instructions - 1:
                continue
            IR_BB['functions'][-1]['blocks'].append(
                {"instrs": current_block[:], 
                 "name": f"bb{count}"}
            )
            count += 1
            current_block= []
    return IR_BB

def get_cfg(IR):
    '''
    function to adjacency map
    '''
    func_to_adj = {}
    BB = get_basic_blocks(IR)
    for function in BB['functions']:
        adj = {}
        # label to basic block mapping
        label_to_bb = {}
        for block in function['blocks']:
            adj[block['name']] = []
            for instr in block['instrs']:
                if instr.get("label"):
                    label_to_bb[instr.get("label")] = block["name"]
        # target labels add to adjacency list
        num_blocks = len(function['blocks'])
        for ind, block in enumerate(function['blocks']):
            terminator = block['instrs'][-1]
            if terminator.get("op") in ['jmp', 'br', 'ret']:
                for label in terminator.get("labels", []):
                    mapped_block = label_to_bb[label]
                    if mapped_block not in adj[block['name']]:
                        adj[block['name']].append(mapped_block)
                continue
            # add the next block if not a jump
            if ind < num_blocks - 1 and function['blocks'][ind + 1]['name'] not in adj[block['name']]:
                adj[block['name']].append(function['blocks'][ind + 1]['name'])
        func_to_adj[function["name"]] = adj
    return func_to_adj

if __name__ == '__main__':
    IR = json.load(sys.stdin)
    print("Basic blocks\n----- ------\n")
    print(json.dumps(get_basic_blocks(IR), indent=4))
    print("\nControl Flow Graphs\n------- ---- ------\n")
    print(json.dumps(get_cfg(IR), indent=4))
    pass
