from llvmlite import ir

import uc_new_block

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
        self.index = 0
        self.current_block = None
        self.builder = None
        self.functions = []
        self.values = {}
        self.stack = {}
        self.blocks = {}

    def find_block(self, label):
        for block in self.module.functions:
            for blck in block.blocks:
                if blck.name == label:
                    return blck
        return None



    def build_alloc(self, instruction):
        memory_space = instruction.split(' ')[1]
        val = self.builder.alloca(to_type(instruction.split(' ')[0].split('_')[1]), name=instruction.split(' ')[1][1:])
        self.stack[memory_space] = val
        # self.values[memory_space] = val

    def build_load(self, instruction):
        i = instruction.split(' ')
        ptr = self.stack.get(i[1])
        # if isinstance(ptr, ir.Constant):
        #     self.values[i[2]] = ptr
        # else:
        self.stack[i[2]] = self.builder.load(ptr)
        # self.values[i[2]] = self.values[i[1]]
        # self.stack[i[2]] = self.stack[i[1]]


    def build_store(self, instruction):
        i = instruction.split(' ')
        value = self.values.get(i[1])
        ptr = self.stack.get(i[2])
        self.builder.store(value, ptr)
        self.stack[i[1]] = ptr
        self.values[i[2]] = value

    def build_literal(self, instruction):
        inst = instruction.split(' ')
        type = to_type(inst[0].split('_')[1])
        const = ir.Constant(type, inst[1])
        # supposed to store a pointer to the register... think it's useless for us
        self.stack[inst[2]] = const
        self.values[inst[2]] = const

    def build_add(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        self.values[inst[3]] = self.builder.add(lhs, rhs)

    def build_return(self, instruction):
        i = instruction.split(' ')
        position = self.stack.get(i[1])
        self.builder.ret(position)

    def build_jump(self, instruction):
        inst = instruction.split(' ')
        an = self.find_block(inst[len(inst) - 1][1:])
        self.builder.branch(an)

    def build_cbranch(self, instruction):
        inst = instruction.split(' ')
        func = self.functions[len(self.functions) - 1]
        pred = self.values.get(inst[1])
        iftrue = self.find_block(inst[3][1:])
        iffalse = self.find_block(inst[5][1:])
        self.builder.cbranch(pred, iftrue, iffalse)

    def build_gt(self, instruction):
        inst = instruction.split(' ')
        lhs = self.values.get(inst[1])
        rhs = self.values.get(inst[2])
        self.values[inst[3]] = self.builder.icmp_signed('>', lhs, rhs)

    def build_ge(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        self.values[inst[3]] = self.builder.icmp_signed('>=', lhs, rhs)

    def build_lt(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        # a = self.builder.load(lhs)
        # b = self.builder.load(rhs)
        self.values[inst[3]] = self.builder.icmp_signed('<', lhs, rhs)

    def build_global_int(self, instruction):
        pass

    def build_global_string(self, instruction):
        pass

    def append_instructions(self, instructions):

        for inst in instructions:
            if len(inst.split(' ')) == 1:
                self.current_block = self.find_block(inst)
                self.builder = ir.IRBuilder(self.current_block)
            elif inst.startswith('\ndefine'):
                self.builder = ir.IRBuilder(self.find_block(inst.split(' ')[1][1:]))
            elif inst.startswith('alloc_'):
                getattr(self, "build_"+inst[:5])(inst)
            elif inst.startswith('global_int'):
                getattr(self, "build_" + inst[:10])(inst)
            elif inst.startswith('global_string'):
                getattr(self, "build_" + inst[:13])(inst)
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
            elif inst.startswith('ge_'):
                getattr(self, 'build_' + inst[:2])(inst)
            elif inst.startswith('lt_'):
                getattr(self, 'build_' + inst[:2])(inst)
            elif inst.startswith('cbranch'):
                getattr(self, 'build_' + inst[:7])(inst)
            elif inst.startswith('add_'):
                getattr(self, 'build_' + inst[:3])(inst)
            else:
                print("DEU RUIM")

    def append_block(self, function, block):
        b = self.find_block(block.label)
        if b is None:
            b = function.append_basic_block(block.label)
            self.blocks[block.label] = b
        else:
            self.builder.goto_block(b)
        self.current_block = block

    def resolve_block(self, function, block):
        if block is None:
            return
        elif self.find_block(block.label) is not None:
            return
        elif isinstance(block, uc_new_block.ConditionBlock):
           b = function.append_basic_block(block.label)
           self.resolve_block(function, block.taken)
           self.resolve_block(function, block.fall_through)
        else:
            b = function.append_basic_block(block.label)
            self.resolve_block(function, block.next_block)
        self.blocks[block.label] = b
        self.builder = ir.IRBuilder(b)

    def preparation(self, function_blocks):
        '''
        Receives the list of blocks from the same function, and initialize them regarding their LLVM function and IRBuilder
        '''

        function_decl = function_blocks[0].instructions[0].split(' ')
        function = function_decl[1][1:]
        func_type = function_decl[0].split('_')[1]
        func_args = function_decl[2:]
        args = []
        if len(func_args) >= 2:
            for arg_type in range(0, len(func_args) - 1, 2):
                args.append(to_type(func_args[arg_type]))
        fnty = ir.FunctionType(to_type(func_type), args)
        fn = ir.Function(self.module, fnty, function)
        self.functions.append(fn)
        return fn

    def resolve_function(self, blocks):
        function = self.preparation(blocks)
        for block in blocks:
            self.builder = ir.IRBuilder()
            self.resolve_block(function, block)

    def resolve_global(self, global_blocks):
        for block in global_blocks:
            self.append_instructions(block.instructions)



    def generate_code(self, function_blocks):
        '''
        Receive all blocks on a list of lists and convert the respective instructions to LLVM IR
        '''

        if function_blocks[0][0].label == 'global':
            self.resolve_global(function_blocks[0])
            function_blocks = function_blocks[1:]
        for function in function_blocks:
            self.resolve_function(function)

        '''
        This chunck of code represents a way to populate instructions recursively iterating each block
        '''
        # for function in function_blocks:
        #     for block in function:
        #         label = block.label
        #         if block.label.startswith('%'):
        #             label = block.label[1:]
        #         self.builder = ir.IRBuilder(self.find_block(label))
        #         self.append_instructions(block.instructions)

        '''
        This chunck of code represents a way to populate instructions iterating all of them accordingly to the current block
        '''
        instructions = []
        for function in function_blocks:
            for block in function:
                for ins in block.instructions:
                    instructions.append(ins)

        self.append_instructions(instructions)


        '''
        Workaround to test label positioning
        '''

