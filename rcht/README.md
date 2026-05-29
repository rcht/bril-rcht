## 1. Basic Block Extraction

Done, aside from speculative execution.

## 2. Trivial Dead Code Elimination

Done, but the code relies on the basic block code being correct

## 3. Local Value Numbering

Passes implemented:
- Copy Propagation
- Common Subexpression Elimination (with commutativity)
- Constant Folding

There is an issue, though. When a variable is updated, its old entry in the local value table should be removed. Probably a quick fix....
