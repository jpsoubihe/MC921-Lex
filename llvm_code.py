from llvmlite import ir

import uc_block

int_type = ir.IntType(32)
float_type = ir.FloatType()
void_type = ir.VoidType

def to_type(type):
    if type == 'int':
        return int_type
    elif type == 'float':
        return float_type
    elif type == 'void':
        return void_type

class LLVM_builder():

    def __init__(self, module):
        self.module = module
        self.current_block = None
        self.builder = None
        self.functions = []
        self.values = {}
        self.stack = {}
        self.blocks = {}

    def find_block(self, label):
        for block in self.module.functions[len(self.module.functions) - 1].basic_blocks:
            if block.name == label:
                return block
        return None

    def preparation(self, function_blocks):
        '''
        Receives the list of blocks from the same function, and initialize them regarding their LLVM function and IRBuilder
        '''

        function_decl = function_blocks[0].instructions[0].split(' ')
        function = function_decl[1][1:]
        func_type = function_decl[0].split('_')[1]
        func_args = function_decl[2:]
        args = []
        if len(func_args) > 2:
            for arg_type in range(0, len(func_args) - 1, 2):
                args.append(to_type(func_args[arg_type]))
        fnty = ir.FunctionType(to_type(func_type), args)
        fn = ir.Function(self.module, fnty, function)
        self.functions.append(fn)
        return fn
        # self.builder = ir.IRBuilder(fn.append_basic_block(function))

    def build_alloc(self, instruction):
        memory_space = instruction.split(' ')[1]
        self.stack[memory_space] = self.builder.alloca(ir.IntType(32), name=instruction.split(' ')[1][1:])

    def build_load(self, instruction):
        i = instruction.split(' ')
        ptr = self.stack.get(i[1])
        self.builder.load(ptr, i[2][1:])
        self.stack[i[2]] = self.stack[i[1]]
        self.values[i[2]] = ptr

    def build_store(self, instruction):
        i = instruction.split(' ')
        value = self.values.get(i[1])
        ptr = self.stack.get(i[2])
        self.builder.store(value, ptr)
        self.values[i[2]] = value

    def build_literal(self, instruction):
        inst = instruction.split(' ')
        const = ir.Constant(to_type(inst[0].split('_')[1]), inst[1])
        self.values[inst[2]] = const

    def build_return(self, instruction):
        i = instruction.split(' ')
        position = self.values.get(i[1])
        self.builder.ret(self.builder.load(position))

    def build_jump(self, instruction):
        inst = instruction.split(' ')
        an = self.find_block(inst[2][1:])
        self.builder.branch(an)
        # self.builder.position_at_end(an)

    def build_cbranch(self, instruction):
        inst = instruction.split(' ')
        func = self.functions[len(self.functions) - 1]
        pred = self.values.get(inst[1])

        iftrue = self.find_block(inst[3][1:])
        iffalse = self.find_block(inst[5])
        self.builder.cbranch(pred, iftrue, iffalse)



    def build_gt(self, instruction):
        inst = instruction.split(' ')
        lhs = self.values.get(inst[1])
        rhs = self.values.get(inst[2])
        self.values[inst[3]] = self.builder.icmp_signed('>', lhs, rhs)




    def append_instructions(self, instructions):
        for inst in instructions:
            if inst.startswith('alloc_'):
                getattr(self, "build_"+inst[:5])(inst)
            elif inst.startswith('store_'):
                getattr(self, "build_"+inst[:5])(inst)
            elif inst.startswith('load_'):
                getattr(self, "build_"+inst[:4])(inst)
            elif inst.startswith('literal_'):
                getattr(self, "build_" + inst[:7])(inst)
            elif inst.startswith('return_'):
                getattr(self, 'build_' + inst[:6])(inst)
            elif inst.startswith('jump'):
                getattr(self, 'build_' + inst[:4])(inst)
            elif inst.startswith('gt_'):
                getattr(self, 'build_' + inst[:2])(inst)
            # elif inst.startswith('cbranch'):
            #     getattr(self, 'build_' + inst[:7])(inst)

    def append_block(self, function, block):
        # if isinstance(block, uc_block.BasicBlock):
        b = self.find_block(block.label)
        if b is None:
            b = function.append_basic_block(block.label)
            # self.builder = ir.IRBuilder(b)
            self.blocks[block.label] = b
        else:
            self.builder.goto_block(b)
        self.current_block = block
        # elif isinstance(block, uc_block.ConditionBlock):
        #     self.builder = ir.IRBuilder(function.append_con(block.label))
        #     self.current_block = block

    def resolve_block(self, block):
        name = block.label
        if self.find_block(block.label) is None:
            bl = self.module.functions[len(self.module.functions) - 1].append_basic_block(block.label)
            self.builder = ir.IRBuilder(bl)
            # if isinstance(block, uc_block.BasicBlock):
            #     self.resolve_basic_block(block)
            # else:
            #     self.resolve_condition_block(block)

    def resolve_basic_block(self, block):
        # self.append_instructions(block.instructions)
        if block.next_block is not None:
            self.resolve_block(block.next_block)

    def resolve_condition_block(self, block):
        # self.append_instructions(block.instructions)
        self.resolve_block(block.fall_through)
        self.resolve_block(block.taken)


    def resolve_function(self, function):
        self.preparation(function)
        self.resolve_block(function[0])


    def generate_code(self, function_blocks):
        '''
        Receive all blocks on a list of lists and convert the respective instructions to LLVM IR
        '''

        for function in function_blocks:
            self.preparation(function)
            for block in function:
                self.resolve_block(block)
        for function in function_blocks:
            for block in function:
                self.builder = ir.IRBuilder(self.find_block(block.label))
                self.append_instructions(block.instructions)


        a = 3
            # func = self.preparation(function)
            # self.append_block(func, function[0])
            # for block in function:
            #     self.append_instructions(function, block.instructions)