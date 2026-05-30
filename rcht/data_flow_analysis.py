import sys
import json
from get_basic_blocks import get_basic_blocks, get_cfg
from typing import Dict, Any, List
import copy
from collections import defaultdict

class ReachingDefinitionsAnalysis:
    def __init__(self, IR):
        self.IR = IR
    def analyze(self):
        BB_IR = get_basic_blocks(self.IR)
        ADJ = get_cfg(self.IR)
        analysis = {}
        for function in BB_IR["functions"]:
            fname = function["name"]
            analysis[fname] = {}
            IN : Dict[str, set] = defaultdict(set)
            OUT : Dict[str, set] = defaultdict(set)
            block_names : List[str] = []
            name_to_index : Dict[str, int] = {}

            # initial values: function arguments
            initial_value = set()
            for arg in function.get("args", []):
                initial_value.add((arg["name"], -1)) # -1 means function argument

            instr_counter = 0
            LAST_DEF : Dict[str, Dict[str, int]] = {} # last definition of every variable in a basic block

            # string to integer basic block conversion
            for block in function["blocks"]:
                bname = block["name"]
                analysis[fname][bname] = {}
                block_names.append(bname)
                name_to_index[bname] = len(block_names) - 1
                LAST_DEF[bname] = {}
                for instr in block["instrs"]:
                    if instr.get("dest"):
                        LAST_DEF[bname][instr["dest"]] = instr_counter
                    instr_counter += 1

            # initialize
            IN[block_names[0]] = copy.copy(initial_value)
            for block in block_names:
                OUT[block] = copy.copy(initial_value)

            int_adj = [[] for _ in range(len(block_names))]
            preds = [[] for _ in range(len(block_names))]

            # integer adjacency list
            for src, dests in ADJ[fname].items():
                int_adj[name_to_index[src]] = [name_to_index[d] for d in dests]
                for d in dests:
                    preds[name_to_index[d]].append(name_to_index[src])

            # print(int_adj)

            # worklist algorithm
            worklist = list(range(len(block_names)))
            while len(worklist):
                b = worklist.pop()
                IN[block_names[b]] = copy.copy(initial_value) if b == 0 else set()
                # merge
                for in_index in preds[b]:
                    IN[block_names[b]] |= OUT[block_names[in_index]]

                prev_out = copy.copy(OUT[block_names[b]])

                # transfer
                # NEW_DEFS \cup (in_b - KILL_b)
                OUT[block_names[b]] = {defn for defn in IN[block_names[b]] if defn[0] not in LAST_DEF[block_names[b]].keys()}
                for var, instr_no in LAST_DEF[block_names[b]].items():
                    OUT[block_names[b]].add((var, instr_no))

                # convergence
                if prev_out != OUT[block_names[b]]:
                    for next_ind in int_adj[b]:
                        if next_ind not in worklist:
                            worklist.append(next_ind)

            for bname, val in IN.items():
                analysis[fname][bname]["in"] = list(map(str, val))
            for bname, val in OUT.items():
                analysis[fname][bname]["out"] = list(map(str, val))

        return analysis




if __name__=='__main__':
    IR = json.load(sys.stdin)
    print(json.dumps(ReachingDefinitionsAnalysis(IR).analyze(), indent=4))
