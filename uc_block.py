# An example of how to create basic blocks




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


class Block(object):
    def __init__(self, label):
        self.label = label  # Label that identifies the block
        self.instructions = []  # Instructions in the block
        self.predecessors = []  # List of predecessors
        self.next_block = None  # Link to the next block

    def append(self, instr):
        self.instructions.append(instr)

    def __iter__(self):
        return iter(self.instructions)


class BasicBlock(Block):
    '''
    Class for a simple basic block.  Control flow unconditionally
    flows to the next block.
    '''

    def __init__(self, label):
        super(BasicBlock, self).__init__(label)
        self.branch = None  # Not necessary the same as next_block in the linked list


class ConditionBlock(Block):
    """
    Class for a block representing an conditional statement.
    There are two branches to handle each possibility.
    """

    def __init__(self, label):
        super(ConditionBlock, self).__init__(label)
        self.taken = None
        self.fall_through = None


class BlockVisitor(object):
    '''
    Class for visiting basic blocks.  Define a subclass and define
    methods such as visit_BasicBlock or visit_IfBlock to implement
    custom processing (similar to ASTs).
    '''

    def visit(self, block):
        while isinstance(block, Block):
            name = "visit_%s" % type(block).__name__
            if hasattr(self, name):
                getattr(self, name)(block)
            block = block.next_block

class Block_Visitor(BlockVisitor):
    def __init__(self, instructions):
        self.instructions = instructions
        self.blocks = []
        self.current_block = None
        self.blocks_global = []

    def find_block(self, label):
        for block in self.blocks_global:

            if block.label.endswith(label):
                    return block
            # else:
            #     if block.label is label:
            #         return block
        return None

    def add_to_global(self, block):
        for b in self.blocks_global:
            if b.label == block.label:
                b = block
                return block
        self.blocks_global.append(block)

    def migrate_to_cond(self, label):
        block = ConditionBlock(label)
        self.current_block.next_block = block
        block.predecessors = self.current_block
        # block.instructions = self.current_block.instructions
        # block.predecessors = self.current_block.predecessors
        # self.blocks_global.pop(self.blocks_global.index(self.current_block))
        self.current_block = block
        self.blocks_global.append(self.current_block)


    def divide(self):
        for i in self.instructions:
            # BASIC BLOCK [BEGGINING FUNCTION]
            if i[0] == 'define':

                function_block = BasicBlock(i[1])
                self.current_block = function_block
                self.add_to_global(function_block)

            # BASIC BLOCK [BEGGINING LABEL]
            elif len(i) is 1:
                target_block = self.find_block(i[0])
                if target_block is None:
                    target_block = BasicBlock(i[0])
                    target_block.predecessors.append(self.current_block)
                if self.current_block.instructions[len(self.current_block.instructions) - 1][0] != 'jump':
                    self.current_block.next_block = target_block
                self.current_block = self.add_to_global(target_block)


            # BASIC BLOCK [UNCONDITIONAL JUMP]
            elif i[0] is 'jump':
                next_block = self.find_block(i[1])
                if next_block is None:
                    next_block = BasicBlock(i[1])
                    self.add_to_global(next_block)
                    # blocks_global.append(self.current_block)
                self.current_block.next_block = next_block
                next_block.predecessors.append(self.current_block)
                # self.current_block = next_block

            elif i[0] == 'cbranch':
                self.migrate_to_cond(i[1])
                c_block = self.current_block

                c_block.taken = self.find_block(i[2])
                if c_block.taken is None:
                    c_block.taken = BasicBlock(i[2])
                    self.blocks_global.append(c_block.taken)
                if c_block.taken.predecessors.__contains__(c_block) is False:
                    c_block.taken.predecessors.append(c_block)

                c_block.fall_through = self.find_block(i[3])
                if c_block.fall_through is None:
                    c_block.fall_through = BasicBlock(i[3])
                    self.blocks_global.append(c_block.fall_through)
                if c_block.fall_through.predecessors.__contains__(c_block) is False:
                    c_block.fall_through.predecessors.append(c_block)
                # c_block.next_block = [c_block.taken, c_block.fall_through]
                self.current_block = c_block

            if self.current_block is not None:
                self.current_block.instructions.append(i)
        self.current_block.next_block = None



        for blcks in self.blocks_global:
            # if isinstance(blcks,ConditionBlock):
            #      = blcks.fall_through.next_block blcks.taken.next_block
            #     blcks.fall_through.next_block.predecessors.append(blcks.taken)
            for instructions in range(len(blcks.instructions)):
                blcks.instructions[instructions] = format_instruction(blcks.instructions[instructions])
            print(blcks.instructions)
        return self.blocks_global
