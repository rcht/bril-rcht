# Local Value Numbering
# ----- ----- ---------
# Does various things, such as copy propagation, CSE, constant folding, etc.

import sys
import json
from get_basic_blocks import get_basic_blocks
from dead_code_elimination import eliminate_dead_code
from typing import List, Tuple, Dict, Any

class Identity:
    def __init__(self, vname: int) -> None:
        self.vname = vname
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Identity):
            return False
        return self.vname == value.vname

class Constant:
    def __init__(self, value: int):
        self.value = value
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Constant):
            return False
        return value.value == self.value

class BinaryOp:
    def __init__(self, op_name: str, vname1: int, vname2: int) -> None:
        self.vname1 = vname1
        self.vname2 = vname2
        self.op_name = op_name
        if op_name in ["mul", "add"] and vname1 > vname2:
            tmp = vname1
            self.vname1 = vname2
            self.vname2 = tmp
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, BinaryOp):
            return False
        return self.vname1 == value.vname1 and self.vname2 == value.vname2

def opify(cloud: Dict[str, int], instr : dict):
    if instr["op"] == "const":
        return Constant(instr["value"])
    elif len(instr["args"]) == 2:
        return BinaryOp(
            op_name=instr["op"],
            vname1=cloud[instr["args"][0]],
            vname2=cloud[instr["args"][1]]
        )
    elif instr["op"] == "id":
        return Identity(cloud[instr["args"][0]])
    else:
        return None

def fold(table: List[Tuple[int, Any, str]], rep):
    if isinstance(rep, Identity):
        return rep.vname
    elif isinstance(rep, BinaryOp):
        arg0_rep = canonical_row(table, rep.vname1)[1]
        arg1_rep = canonical_row(table, rep.vname2)[1]
        if isinstance(arg0_rep, Constant) and isinstance(arg1_rep, Constant):
            if rep.op_name == "add":
                return Constant(arg0_rep.value + arg1_rep.value)
            elif rep.op_name == "mul":
                return Constant(arg0_rep.value * arg1_rep.value)
            elif rep.op_name == "sub":
                return Constant(arg0_rep.value - arg1_rep.value)
            elif rep.op_name == "div":
                return Constant(arg0_rep.value // arg1_rep.value)
            else:
                print("op not implemented")
                exit(1)
        else:
            return rep
    elif isinstance(rep, Constant):
        return rep
    return None

def canonical_home(table: List[Tuple[int, Any, str]], number):
    for row in table:
        if row[0] == number:
            return row[2]
    print("canon not found")
    exit(1)

def canonical_row(table: List[Tuple[int, Any, str]], number):
    for row in table:
        if row[0] == number:
            return row
    print("canon not found")
    exit(1)

def home_find(table: List[Tuple[int, Any, str]], obj) -> int | None:
    for row in table:
        if obj == row[1]:
            return row[0]
    return None

def local_value_numbering(IR: dict) -> dict:
    BB_IR = get_basic_blocks(IR)
    for function in BB_IR["functions"]:
        function["instrs"] = []
        for block in function["blocks"]:
            table : List[Tuple[int, Any, str]] = []
            cloud : Dict[str, int] = {}
            unknown_counter = (-1)
            known_counter = 1
            arg_set = set()
            for instr in block["instrs"]:
                for arg in instr.get("args", []):
                    arg_set.add(arg)
            for arg in arg_set:
                cloud[arg] = unknown_counter
                table.append( (unknown_counter, None, arg) )
                unknown_counter -= 1
            for instr in block["instrs"]:
                # print(instr, cloud)
                # print(table)
                if instr.get("type") != "int":
                    # simply replace args with canon
                    if "args" in instr:
                        instr["args"] = [canonical_home(table, cloud[a]) for a in instr["args"]]
                    function["instrs"].append(instr)
                    continue
                # opify -> fold -> emit
                rep = opify(cloud, instr)
                if rep == None:
                    print("oops. unknown int op")
                    exit(1)

                rep = fold(table, rep)

                # emit
                if isinstance(rep, int):
                    # only cloud changes
                    cloud[instr["dest"]] = rep
                    # emit id instruction
                    function["instrs"].append(
                        {"type": "int", "op": "id", "dest": instr["dest"], "args": [canonical_home(table, rep)]}
                    )
                elif isinstance(rep, Identity):
                    copied: int = rep.vname
                    cloud[instr["dest"]] = copied
                    function["instrs"].append(
                        {"type": "int", "op": "id", "dest": instr["dest"], "args": [canonical_home(table, copied)]}
                    )
                    print("WARN: this should not happen")
                elif rep == None:
                    print("NoneType folded")
                    exit(1)
                else:
                    home = home_find(table, rep)
                    if home == None:
                        cloud[instr["dest"]] = known_counter
                        if isinstance(rep, BinaryOp):
                            function["instrs"].append({
                                "type": "int",
                                "op": rep.op_name,
                                "dest": instr["dest"],
                                "args": [canonical_home(table, rep.vname1), canonical_home(table, rep.vname2)]
                            })
                        elif isinstance(rep, Constant):
                            function["instrs"].append({
                                "type": "int",
                                "op": "const",
                                "dest": instr["dest"],
                                "value": rep.value
                            })
                        else:
                            # just replace the args i guess?
                            print("what type did i miss :(")
                            exit(1)
                        table.append( (known_counter, rep, instr["dest"]) )
                        known_counter += 1
                    else:
                        cloud[instr["dest"]] = home
                        


        del function["blocks"]


    return BB_IR

if __name__=='__main__':
    IR = json.load(sys.stdin)
    if len(sys.argv) >= 2 and sys.argv[1] == '-d':
        print(json.dumps(eliminate_dead_code(local_value_numbering(IR)),indent=4))
    else:
        print(json.dumps(local_value_numbering(IR),indent=4))
