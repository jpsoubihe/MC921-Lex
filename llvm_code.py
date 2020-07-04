from llvmlite import ir

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
        self.functions = []

    def preparation(self, function_blocks):
        '''
        Receives the list of blocks from the same function, and initialize them regarding their LLVM function and IRBuilder
        '''

        function = function_blocks[0].instructions[0].split(' ')[1][1:]

        fnty = ir.FunctionType(ir.IntType(32), [ir.IntType(32)])
        ir.Function(self.module, fnty, function)
        self.functions.append(function_blocks[0].instructions[0].split(' ')[1])


    def generate_code(self, blocks):
        '''
        Receive all blocks on a list of lists and convert the respective instructions to LLVM IR
        '''
        for function in blocks:
            self.preparation(function)