import graphviz
from graphviz import Digraph

from uc_block import Block


def format_instruction(t):
    # Auxiliary method to pretty print the instructions
    op = t[0]
    if len(t) > 1:
        if op == "define":
            return f"\n{op} {t[1]}"
        else:
            _str = "" if op.startswith('global') else "  "
            if op == 'jump':
                _str += f"{op} label {t[1]}"
            elif op == 'cbranch':
                _str += f"{op} {t[1]} label {t[2]} label {t[3]}"
            elif op == 'global_string':
                _str += f"{op} {t[1]} \'{t[2]}\'"
            elif op.startswith('return'):
                _str += f"{op} {t[1]}"
            else:
                for _el in t:
                    _str += f"{_el} "
            return _str
    elif op == 'print_void' or op == 'return_void':
        return f"  {op}"
    else:
        return f"{op}"

class CFG(object):

    def __init__(self, fname):
        self.fname = fname
        self.g = Digraph('g', filename=fname + '.gv', node_attr={'shape': 'record'})

    def visit_BasicBlock(self, block):
        # Get the label as node name
        _name = block.label
        if _name:
            # get the formatted instructions as node label
            _label = "{" + _name + ":\l\t"
            for _inst in block.instructions:
                _label += format_instruction(_inst) + "\l\t"
            _label += "}"
            self.g.node(_name, label=_label)
            if block.next_block:
                self.g.edge(_name, block.next_block.label)
        else:
            # Function definition. An empty block that connect to the Entry Block
            self.g.node(self.fname, label=None, _attributes={'shape': 'ellipse'})
            self.g.edge(self.fname, block.next_block.label)

    def visit_ConditionBlock(self, block):
        # Get the label as node name
        _name = block.label
        # get the formatted instructions as node label
        _label = "{" + _name + ":\l\t"
        for _inst in block.instructions:
            _label += format_instruction(_inst) + "\l\t"
        _label +="|{<f0>T|<f1>F}}"
        self.g.node(_name, label=_label)
        self.g.edge(_name + ":f0", block.taken.label)
        self.g.edge(_name + ":f1", block.fall_through.label)

    def view(self, blocks):
        block = blocks[0]
        count = 0
        while isinstance(block, Block) and count < 10:
            name = "visit_%s" % type(block).__name__
            if hasattr(self, name):
                getattr(self, name)(block)
            if isinstance(block.next_block, list):
                for i in block.next_block:
                    name = "visit_%s" % type(i).__name__
                    if hasattr(self, name):
                        getattr(self, name)(i)
            block = block.next_block
            if block is None and len(blocks) - 1 > count:
                block = blocks[count]
            count += 1
        # You can use the next stmt to see the dot file
        # print(self.g.source)
        self.g.view()