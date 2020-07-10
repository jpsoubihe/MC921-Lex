# An example of how to create basic blocks



def format_instruction(t):
    # Auxiliary method to pretty print the instructions
    # t is the tuple that contains one instruction
    op = t[0]
    if len(t) > 1:
        if op.startswith("define"):
            return f"\n{op} {t[1]} " + ', '.join(list(' '.join(el) for el in t[2]))
        else:
            _str = "" #if op.startswith('global') else "  "
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
        self.visited = False

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
        self.taken_visited = False
        self.fall_through_visited = False


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


class New_Block_Visitor(BlockVisitor):
    def __init__(self, instructions):
        self.index = 0
        self.instructions = instructions
        self.blocks = []
        self.current_block = None
        self.blocks_global = []
        self.falls = {}

    def beautify_label(self, label):
        if label.startswith('%') or label.startswith('@'):
            return label[1:]
        return label

    def find_block(self, label):
        for block in self.blocks_global:
            if block.label == label:
                return block
        return None

    def add_to_global(self, block):
        for b in self.blocks_global:
            if b.label == block.label:
                return block
        self.blocks_global.append(block)
        return block

    def migrate_to_cond(self, block):
        b = ConditionBlock(self.beautify_label(block.label))
        self.blocks_global.pop(self.blocks_global.index(block))
        self.blocks_global.append(b)
        return b

    def resolve(self, block):
        while self.index < len(self.instructions):
            inst = self.instructions[self.index]
            if len(inst) == 1:
                if self.falls.keys().__contains__(inst[0]):
                    self.falls.pop(inst[0])
                    return block

            if inst[0].startswith('define'):
                b = self.add_to_global(BasicBlock(inst[1][1:]))
                self.index += 1
                block = self.resolve(b)

            elif inst[0].startswith('jump'):
                b = self.add_to_global(BasicBlock(inst[1][1:]))
                block.next_block = b
                self.index += 1
                block = self.resolve(b)
                return block

            elif inst[0].startswith('cbranch'):
                b = self.migrate_to_cond(block)
                block.next_block = b
                self.index += 1
                b.taken = self.add_to_global(BasicBlock(inst[2][1:]))
                b.fall_through = self.add_to_global(BasicBlock(inst[3][1:]))
                self.falls[b.fall_through.label] = b.fall_through.label
                self.resolve(b.taken)
                self.resolve(b.fall_through)
                return block
            else:
                self.index += 1

    def populate(self, block):
        while self.index < len(self.instructions):
            inst = self.instructions[self.index]

            if len(inst) == 1:
                if inst[0].startswith('return') is False:
                    block = self.find_block(inst[0])
                block.instructions.append(inst)
                self.index += 1

            elif inst[0].startswith('define'):
                block = self.find_block(inst[1][1:])
                block.instructions.append(inst)
                self.index += 1

            elif inst[0].startswith('jump'):
                block.instructions.append(inst)
                self.index += 1

            elif inst[0].startswith('cbranch'):
                block.instructions.append(inst)
                self.index += 1

            else:
                block.instructions.append(inst)
                self.index += 1

    def sanitize_block(self, block):
        alrt = False
        for instruction in block.instructions:
            if alrt:
                i = block.instructions.pop()
                while i != instruction:
                    i = block.instructions.pop()
                # block.instructions.append(i)
            elif instruction.startswith('jump'):
                if block.instructions.index(instruction) < len(block.instructions) - 1:
                    alrt = True


    def segment_functions(self):
        for blcks in self.blocks_global:
            blcks.predecessors = list(dict.fromkeys(blcks.predecessors))
            for instructions in range(len(blcks.instructions)):
                blcks.instructions[instructions] = format_instruction(blcks.instructions[instructions])
        function_blocks = []
        return_blocks = []
        for block in self.blocks_global:
            if len(block.instructions) == 0:
                pass
            else:
                first_instruction = block.instructions[0]
                isFunction = False
                if isinstance(first_instruction, str):
                    isFunction = first_instruction.find('define') != -1
                if not isFunction:
                    function_blocks.append(block)
                else:
                    if len(function_blocks) > 0:
                        return_blocks.append(function_blocks)
                    function_blocks = [block]
        return_blocks.append(function_blocks)
        return return_blocks

    def divide(self):
        b = self.add_to_global(BasicBlock('global'))
        self.current_block = b
        while self.index < len(self.instructions):
            self.resolve(b)
            if self.index < len(self.instructions):
                b = self.add_to_global(BasicBlock(self.instructions[self.index][0]))

        self.index = 0
        self.populate(self.find_block('global'))
        functions = self.segment_functions()

        for function in functions:
            for blcks in function:
                self.sanitize_block(blcks)
        return functions



