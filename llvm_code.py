from llvmlite import ir

import uc_new_block

int_type = ir.IntType(32)
float_type = ir.DoubleType()
void_type = ir.VoidType()
bool_type = ir.IntType(1)
char_type = ir.IntType(8)


def make_bytearray(buf):
    # Make a byte array constant from *buf*.
    b = bytearray(buf)
    n = len(b)
    return ir.Constant(ir.ArrayType(ir.IntType(8), n), b)


def to_type(type):
    if type == 'int':
        return int_type
    elif type == 'float':
        return float_type
    elif type == 'void':
        return void_type
    elif type == 'char':
        return char_type
    elif type == 'bool':
        return bool_type

class LLVM_builder():

    def __init__(self, module):
        self.module = module
        self.index = 0
        self.current_block = None
        self.current_function = None
        self.builder = None
        self.params = []
        self.functions = []
        self.values = {}
        self.stack = {}
        self.blocks = {}

    def find_block(self, label, scope=None):
        to_see = self.module.functions
        if scope is not None:
            for function in self.module.functions:
                if function.name == scope:
                    to_see = [function]
        for block in to_see:
            for blck in block.blocks:
                if blck.name == label:
                    return blck
        return None

    def find_function(self, function_name):
        for function in self.module.functions:
            if function_name == function.name:
                return function

    #
    # Start of method builders
    #

    def build_add(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        if lhs.type == float_type:
            self.stack[inst[3]] = self.builder.fadd(lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]
        else:
            self.stack[inst[3]] = self.builder.add(lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]

    def build_alloc(self, instruction):
        memory_space = instruction.split(' ')[1]
        type = to_type(instruction.split(' ')[0].split('_')[1])
        if isinstance(type, ir.VoidType) is False:
            arraySeparator = instruction.split(' ')[0].split('_')
            type = to_type(arraySeparator[1])
            if len(arraySeparator) >= 3:
                type = ir.ArrayType(type, int(arraySeparator[2]))
            val = self.builder.alloca(type, name=instruction.split(' ')[1][1:])
            self.stack[memory_space] = val
        # self.values[memory_space] = val

    def build_and(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        self.stack[inst[3]] = self.builder.and_(lhs, rhs)
        self.values[inst[3]] = self.stack[inst[3]]

    def build_call(self, instruction):
        inst = instruction.split(' ')
        function_name = inst[1][1:]
        target = inst[2]
        self.stack[target] = self.builder.call(self.find_function(function_name), self.params)
        self.params = []

    def build_cbranch(self, instruction):
        inst = instruction.split(' ')
        func = self.functions[len(self.functions) - 1]
        pred = self.values.get(inst[1])
        iftrue = self.find_block(inst[3][1:], self.current_function)
        iffalse = self.find_block(inst[5][1:], self.current_function)
        self.builder.cbranch(pred, iftrue, iffalse)

    def build_div(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        if isinstance(lhs.type, ir.IntType):
            self.stack[inst[3]] = self.builder.sdiv(lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]
        else:
            self.stack[inst[3]] = self.builder.fdiv(lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]

    def build_eq(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        if isinstance(lhs.type, ir.IntType):
            self.stack[inst[3]] = self.builder.icmp_signed('==', lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]
        else:
            self.stack[inst[3]] = self.builder.fcmp_ordered('==', lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]

    def build_fptosi(self, instruction):
        i = instruction.split(' ')
        value = self.stack.get(i[1])
        floatvar = self.builder.fptosi(value, ir.IntType(32))
        self.stack[i[2]] = floatvar

    def build_ge(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        self.values[inst[3]] = self.builder.icmp_signed('>=', lhs, rhs)

    def build_global_int(self, instruction):
        # Get or create a (LLVM module-)global constant with *name* or *value*.
        # if the first part of the instruction has more than two separators, i.e global_int_5, then it's an array
        linkage = 'internal'
        inst = instruction.split(' ')
        type = to_type(inst[0].split('_')[1])
        arraySeparator = instruction.split(' ')[0].split('_')
        value = inst[2]
        if len(arraySeparator) == 3:
            type = ir.ArrayType(type, int(arraySeparator[2]))
            value = []
            for i in range(2, len(inst) - 1):
                curVal = inst[i].replace(',', '').replace('[', '').replace(']', '')
                value.append(int(curVal))
        elif len(arraySeparator) > 3:
            numberOfArrays = 1
            for i in range(3, len(arraySeparator)):
                numberOfArrays *= int(arraySeparator[i])
            arrayInitializator = list(filter(''.__ne__, instruction.split('[')[3:]))
            for i, array in enumerate(arrayInitializator):
                arrayInitializator[i] = array.replace(']', '').split(' ')[:-1]
                for j, subarray in enumerate(arrayInitializator[i]):
                    arrayInitializator[i][j] = int(subarray.replace(',', ''))
            arrays = []
            for array in arrayInitializator:
                newArrayType = ir.ArrayType(to_type('int'), len(array))
                newArray = ir.Constant(newArrayType, array)
                arrays.append(newArray)
            for i in reversed(range(3, len(arraySeparator) - 1)):
                size = int(arraySeparator[i])
                newArrays = []
                for I in range(0, len(arrays), size):
                    currentArrays = []
                    for j in range(I, I + size):
                        currentArrays.append(arrays[j])
                    newArrayType = ir.ArrayType(arrays[0].type, len(currentArrays))
                    newArray = ir.Constant(newArrayType, currentArrays)
                    newArrays.append(newArray)
                arrays = newArrays
            type = ir.ArrayType(arrays[0].type, len(arrays))
            value = arrays
        val = ir.Constant(type, value)
        mod = self.module
        data = ir.GlobalVariable(mod, val.type, name=inst[1][1:])
        data.linkage = linkage
        data.global_constant = True
        data.initializer = val
        self.stack[inst[1]] = val

    def build_global_string(self, instruction):
        inst = instruction.split(' ')
        name = inst[1][1:]
        st = inst[2]
        char_array = make_bytearray((st + "\00").encode("utf-8"))
        global_value = ir.GlobalVariable(self.module, char_array.type, name)
        global_value.initializer = char_array
        global_value.global_constant = True
        self.stack[inst[1]] = char_array

    def build_gt(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        self.values[inst[3]] = self.builder.icmp_signed('>', lhs, rhs)

    def build_jump(self, instruction):
        inst = instruction.split(' ')
        an = self.find_block(inst[len(inst) - 1][1:], self.current_function)
        self.builder.branch(an)

    def build_le(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        if isinstance(lhs.type, ir.IntType):
            self.stack[inst[3]] = self.builder.icmp_signed('<=', lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]
        else:
            self.stack[inst[3]] = self.builder.fcmp_ordered('<=', lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]

    def build_literal(self, instruction):
        inst = instruction.split(' ')
        type = to_type(inst[0].split('_')[1])
        const = ir.Constant(type, inst[1])
        self.values[inst[2]] = const
        self.stack[inst[2]] = const

    def build_lt(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        self.values[inst[3]] = self.builder.icmp_signed('<', lhs, rhs)

    def build_load(self, instruction):
        i = instruction.split(' ')
        if i[1].startswith('@'):
            g_values = self.module.global_values
            for variable in g_values:
                if isinstance(variable, ir.GlobalVariable):
                    if variable.name == i[1][1:]:
                        ptr = variable
                        self.values[i[2]] = variable
        else:
            ptr = self.stack.get(i[1])
        if isinstance(ptr, ir.Constant):
            self.values[i[2]] = ptr
        # else:
        self.stack[i[2]] = self.builder.load(ptr)
        if self.values.keys().__contains__(i[1]):
            self.values[i[2]] = self.values[i[1]]
        # self.stack[i[2]] = self.stack[i[1]]

    def build_mod(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        if isinstance(lhs.type, ir.IntType):
            self.stack[inst[3]] = self.builder.srem(lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]
        else:
            self.stack[inst[3]] = self.builder.frem(lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]

    def build_mul(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        if isinstance(lhs.type, ir.IntType):
            self.stack[inst[3]] = self.builder.mul(lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]
        else:
            self.stack[inst[3]] = self.builder.fmul(lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]

    def build_ne(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        if isinstance(lhs.type, ir.IntType):
            self.values[inst[3]] = self.builder.icmp_signed('!=', lhs, rhs)

        else:
            self.values[inst[3]] = self.builder.fcmp_ordered('!=', lhs, rhs)

    def build_not(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        self.stack[inst[3]] = self.builder.not_(lhs, rhs)

    def build_or(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        self.stack[inst[3]] = self.builder.or_(lhs, rhs)

    def build_param(self, instruction):
        inst = instruction.split(' ')
        parameter = self.stack[inst[1]]
        self.params.append(parameter)

    def build_return(self, instruction):
        i = instruction.split(' ')
        if instruction == 'return_void':
            self.builder.ret_void()
        else:
            position = self.stack.get(i[1])
            if self.current_block.is_terminated:
                pass
            else:
                self.builder.ret(position)

    def build_store(self, instruction):
        i = instruction.split(' ')
        value = self.values.get(i[1])
        ptr = self.stack.get(i[2])
        '''
            The intention here is to maintain the logic implemented even if the operation stores a global value, 
            then, before we build the operation we check if value can be used in builder.store(value, pointer) 
        '''
        if isinstance(value, ir.GlobalVariable):
            value = value.initializer
        if value is None:
            f = self.find_function(self.current_function)
            if f is not None:
                for arg in f.args:
                    if arg.name == i[1][1:]:
                        value = arg
        candidate = self.builder.store(value, ptr)
        if candidate.type == void_type:
            self.stack[i[1]] = ptr
        else:
            self.stack[i[1]] = candidate
        self.values[i[2]] = value

    def build_sitofp(self, instruction):
        i = instruction.split(' ')
        value = self.stack.get(i[1])
        floatvar = self.builder.sitofp(value, ir.DoubleType())
        self.stack[i[2]] = floatvar

    def build_sub(self, instruction):
        inst = instruction.split(' ')
        lhs = self.stack.get(inst[1])
        rhs = self.stack.get(inst[2])
        if isinstance(lhs.type, ir.IntType):
            self.stack[inst[3]] = self.builder.sub(lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]
        else:
            self.stack[inst[3]] = self.builder.fsub(lhs, rhs)
            self.values[inst[3]] = self.stack[inst[3]]

    #
    # End of method builders
    #

    def _cio(self, fname, format, *target):
        # Make global constant for string format
        mod = self.builder.module
        fmt_bytes = make_bytearray((format + '\00').encode('ascii'))
        global_fmt = self._global_constant(mod, mod.get_unique_name('.fmt'), fmt_bytes)
        fn = mod.get_global(fname)
        ptr_fmt = self.builder.bitcast(global_fmt, ir.IntType(8).as_pointer())
        return self.builder.call(fn, [ptr_fmt] + list(target))

    def _build_print(self, val_type, target):
        if target:
            # get the object assigned to target
            _value = self.stack[target]
            if val_type == 'int':
                self._cio('printf', '%d', _value)
            elif val_type == 'float':
                self._cio('printf', '%.2f', _value)
            elif val_type == 'char':
                self._cio('printf', '%c', _value)
            elif val_type == 'string':
                self._cio('printf', '%s', _value)
        else:
            self._cio('printf', '\n')

    def build_print(self, instruction):
        inst = instruction.split(' ')
        val_type = to_type(inst[0].split('_')[1])
        self._build_print(val_type, inst[1])

    def append_instructions(self, instructions):
        for inst in instructions:
            if len(inst.split(' ')) == 1:
                if inst == 'return_void':
                    self.build_return(inst)
                self.current_block = self.find_block(inst, self.current_function)
                self.builder = ir.IRBuilder(self.current_block)
            elif inst.startswith('\ndefine'):
                self.current_function = inst.split(' ')[1][1:]
                self.builder = ir.IRBuilder(self.find_block(inst.split(' ')[1][1:]))
            elif len(inst.split('_')) == 1:
                splitInst = inst.split(' ')
                getattr(self, "build_" + splitInst[0])(inst)
            else:
                splitInst = inst.split('_')
                if splitInst[0] == 'global':
                    type = splitInst[1].split(' ')[0]
                    getattr(self, "build_global_" + type)(inst)
                else:
                    getattr(self, "build_" + splitInst[0])(inst)

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
        elif self.find_block(block.label, block.function) is not None:
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
        """
        Receives the list of blocks from the same function, and initialize them regarding their LLVM function and IRBuilder
        """

        function_decl = function_blocks[0].instructions[0].split(' ')
        function = function_decl[1][1:]
        func_type = function_decl[0].split('_')[1]
        func_args = function_decl[2:]
        args_ty = []
        args = []
        if len(func_args) >= 2:
            for arg_type in range(0, len(func_args) - 1, 2):
                args_ty.append(to_type(func_args[arg_type]))
                args.append(func_args[arg_type + 1].split(',')[0])
        fnty = ir.FunctionType(to_type(func_type), args_ty)
        fn = ir.Function(self.module, fnty, function)
        for ind in range(0, len(fn.args)):
            fn.args[ind].name = args[ind][1:]
        self.functions.append(fn)
        return fn

    def resolve_function(self, blocks):
        function = self.preparation(blocks)
        self.current_function = function.name
        for block in blocks:
            self.builder = ir.IRBuilder()
            self.resolve_block(function, block)

    def resolve_global(self, global_blocks):
        self.current_function = 'global'
        for block in global_blocks:
            b = self.find_block(block.label)
            self.builder = ir.IRBuilder(b)
            self.append_instructions(block.instructions)

    def generate_code(self, function_blocks):
        """
        Receive all blocks on a list of lists and convert the respective instructions to LLVM IR
        """

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

        self.current_function = 'global'
        self.append_instructions(instructions)
