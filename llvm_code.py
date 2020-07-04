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
        self.builder = None
        self.functions = []

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
        self.functions.append(function_blocks[0].instructions[0].split(' ')[1])
        return fn
        # self.builder = ir.IRBuilder(fn.append_basic_block(function))

    def build_alloc(self, instruction):
        self.builder.alloca(ir.IntType(32), name=instruction.split(' ')[3])

    def append_instructions(self, instructions):
        for inst in instructions:
            if inst[2:].startswith('alloc_'):
                self.build_alloc(inst)

    def append_block(self, function, block):
        if isinstance(block, uc_block.BasicBlock):
            self.builder = ir.IRBuilder(function.append_basic_block(block.label))


    def generate_code(self, blocks):
        '''
        Receive all blocks on a list of lists and convert the respective instructions to LLVM IR
        '''

        for function in blocks:
            func = self.preparation(function)
            for block in function:
                self.append_block(func, block)
                self.append_instructions(block.instructions)