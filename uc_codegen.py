import ast
from uc_semantic import NodeVisitor

binary_ops = {
    "+": "add",
    "-": "sub",
    "*": "mul",
    "/": "div",
    "%": "mod",
    "==": "eq",
    "!=": "ne",
    "<": "lt",
    ">": "gt",
    "<=": "le",
    ">=": "ge",
    "&&": "and",
    "||": "or",
    "!": "not"
}

cast_types = {"int": "si", "float": "fp"}

oper_ops = {"+=": "add", "-=": "sub", "/=": "div", "*=": "mul", "%/": "mod"}

bool_ops = ["eq", "ne", "and", "or", "not"]


class ScopeStack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)

    def all(self):
        return self.items

    def __str__(self):
        for i in self.items:
            print(i)


class GenerateCode(NodeVisitor):
    """
    Node visitor class that creates 3-address encoded instruction sequences.
    """

    def __init__(self):
        super(GenerateCode, self).__init__()
        self.waiting_for_label = []
        # version dictionary for temporaries
        self.fname = ScopeStack()  # We use the function name as a key
        self.fname.push('global')
        self.versions = {'global': {'vars': {}, 'number': 0}}
        # The generated code (list of tuples)
        # The generated code (list of tuples)
        self.code = []
        self.global_code = []
        self.func_and_var_types = {}
        self.str_count = 0
        self.const_count = 0

    def new_temp(self, varname, isDeclaring=False):
        """
        Create a new temporary variable of a given scope (function name).
        """
        if self.fname.peek() not in self.versions:
            self.versions[self.fname.peek()] = {}
            self.versions[self.fname.peek()]['number'] = 0
            self.versions[self.fname.peek()]['vars'] = {}
        if varname not in self.versions[self.fname.peek()]['vars']:
            if varname in self.versions['global']['vars'] and not isDeclaring:
                name = self.versions['global']['vars'][varname]
                if isinstance(name, int):
                    name = '%' + name.__str__()
                return name
            self.versions[self.fname.peek()]['vars'][varname] = self.versions[self.fname.peek()]['number']
            self.versions[self.fname.peek()]['number'] += 1
        name = self.versions[self.fname.peek()]['vars'][varname]
        if isinstance(name, int):
            name = '%' + name.__str__()
        return name

    def break_label(self):
        v = self.versions[self.fname.peek()]['vars']
        c = None
        for i in v.keys():
            if i.startswith('for') or i.startswith('while'):
                c = v[i]
        return c

    def new_global(self, varname):
        if varname not in self.versions['global']['vars']:
            self.versions['global']['vars'][varname] = '@' + varname
        return self.versions['global']['vars'][varname]

    # Node visitor methods

    def visit_ArrayDecl(self, node):
        if node.dim is not None:
            str_info = self.func_and_var_types['array%d' % (self.const_count - 1)]
        else:
            str_info = self.func_and_var_types['.str.%d' % (self.str_count - 1)]
        inst = ('alloc_' + str_info['type'] + str_info['size'], node.id)
        self.code.append(inst)
        if node.dim is None:
            inst = ('store_' + str_info['type'] + str_info['size'],
                    self.new_global('.str.%d' % (self.str_count - 1)),
                    node.id)
            self.code.append(inst)

    def visit_ArrayRef(self, node):
        name = node.name
        while isinstance(name, ast.ArrayRef):
            name = name.name
        name = name.name
        sizes = self.func_and_var_types[name]['size'].split('_')[1:]
        type = self.func_and_var_types[name]['type']
        if len(sizes) != 1 and type != 'string':
            next = node
            mults = []
            self.visit(next.subscript)
            if isinstance(next.subscript, ast.BinaryOp):
                sub_id = self.new_temp('binop%d' % next.subscript.id)
            else:
                sub_id = next.subscript.id
            mults.append(sub_id)
            next = node.name
            for size in sizes[:-(len(sizes)):-1]:
                lit = self.const_count
                self.const_count += 1
                inst = ('literal_int', size, self.new_temp('const%d' % lit))
                self.code.append(inst)
                self.visit(next.subscript)
                if isinstance(next.subscript, ast.BinaryOp):
                    sub_id = self.new_temp('binop%d' % next.subscript.id)
                else:
                    sub_id = next.subscript.id
                inst = ('mul_int', self.new_temp('const%d' % lit), sub_id, self.new_temp(self.const_count))
                self.code.append(inst)
                mults.append(self.const_count)
                self.const_count += 1
                next = node.name
            next_id = mults[0]
            for mult in mults[1:]:
                inst = ('add_int', next_id, self.new_temp(mult), self.new_temp(self.const_count))
                self.code.append(inst)
                next_id = self.new_temp(self.const_count)
                self.const_count += 1
            sub_id = next_id
        else:
            self.visit(node.subscript)
            if isinstance(node.subscript, ast.BinaryOp):
                sub_id = self.new_temp('binop%d' % node.subscript.id)
            else:
                sub_id = node.subscript.id
        if type == 'string':
            type = 'char'
        inst = ('elem_' + type, self.new_temp(name), sub_id, self.new_temp('array_ref_%d' % self.const_count))
        self.code.append(inst)
        if node.id != 'no_load':
            array_access = self.new_temp('array_access_%d' % self.const_count)
            inst = ('load_' + type + '_*', self.new_temp('array_ref_%d' % self.const_count), array_access)
            self.code.append(inst)
            node.id = array_access
        else:
            node.id = self.new_temp('array_ref_%d' % self.const_count)
        self.const_count += 1

    def visit_Assert(self, node):
        self.visit(node.expr)
        if isinstance(node.expr, ast.BinaryOp):
            inst = ('cbranch',
                    self.new_temp('binop%d' % node.expr.id),
                    self.new_temp('assert%d_label_1' % self.const_count),
                    self.new_temp('assert%d_label_2' % (self.const_count + 1)))
            self.code.append(inst)
        elif isinstance(node.expr, ast.ID):
            literal = self.const_count
            self.const_count += 1
            type = self.func_and_var_types[node.expr.name]
            if type == 'int':
                check = 0
            elif type == 'float':
                check = 0.0
            else:
                check = ''
            inst = ('literal_' + type, check, self.new_temp('assert_const_%d' % literal))
            self.code.append(inst)
            bool_id = self.const_count
            self.const_count += 1
            inst = ('ne_' + type, node.expr.id, self.new_temp('assert_const_%d' % literal), self.new_temp('assert_bool_%d' % bool_id))
            self.code.append(inst)
            inst = ('cbranch',
                    self.new_temp('assert_bool_%d' % bool_id),
                    self.new_temp('assert%d_label_1' % self.const_count),
                    self.new_temp('assert%d_label_2' % (self.const_count + 1)))
            self.code.append(inst)

        inst = (self.new_temp('assert%d_label_1' % self.const_count)[1:],)
        self.code.append(inst)
        inst = ('jump', self.new_temp('assert%d_label_1' % (self.const_count + 2)))
        self.code.append(inst)

        inst = (self.new_temp('assert%d_label_2' % (self.const_count + 1))[1:],)
        self.code.append(inst)
        inst = ('global_string', self.new_global('.str.%d' % self.str_count),
                'assertion_fail on %s:%s' % (node.coord.line, node.coord.column))
        self.global_code.append(inst)
        inst = ('print_string', self.new_global('.str.%d' % self.str_count))
        self.code.append(inst)
        inst = ('jump', self.new_temp(self.fname.peek() + '_label'))
        self.code.append(inst)

        inst = (self.new_temp('assert%d_label_1' % (self.const_count + 2))[1:],)
        self.code.append(inst)

        self.const_count += 3

    def visit_Assignment(self, node):
        self.visit(node.rvalue)
        pointer_modifier = ''
        if isinstance(node.lvalue, ast.ArrayRef):
            node.lvalue.id = 'no_load'
            self.visit(node.lvalue)
            lvalue_name = node.lvalue.name
            while not isinstance(lvalue_name, ast.ID):
                lvalue_name = lvalue_name.name
            lvalue_name = lvalue_name.name
            target = node.lvalue.id
            pointer_modifier = '_*'
        else:
            lvalue_name = node.lvalue.name
            target = self.new_temp(lvalue_name)
            # target = '%' + lvalue_name
        if isinstance(node.rvalue, ast.BinaryOp):
            if isinstance(node.rvalue.left, ast.Constant):
                type = node.rvalue.left.type
            elif isinstance(node.rvalue.left, ast.ID):
                type = self.func_and_var_types[node.rvalue.left.name]
            elif isinstance(node.rvalue.left, ast.BinaryOp):
                type = self.func_and_var_types[node.rvalue.left.left.name]
            elif isinstance(node.rvalue.left, ast.ArrayRef):
                type = self.func_and_var_types[node.rvalue.left.name.name.name]['type']
            if node.op in oper_ops:
                self.visit_LoadLocation(node.lvalue)
                inst = (oper_ops[node.op] + '_' + type, self.new_temp('binop%d' % node.rvalue.id),
                        node.lvalue.id, self.new_temp('const%d' % self.const_count))
                self.code.append(inst)
                inst = ('store_' + type + pointer_modifier, self.new_temp('const%d' % self.const_count), target)
                self.const_count += 1
            else:
                # ToDo: Total despair! This could end very badly
                type = 'int'
                inst = ('store_' + type + pointer_modifier, self.new_temp('binop%d' % node.rvalue.id), target)
        elif isinstance(node.rvalue, ast.FuncCall):
            inst = ('store_' + self.func_and_var_types[node.rvalue.name.name] + pointer_modifier,
                    self.new_temp('call_%s_%d' % (node.rvalue.name.name, node.rvalue.id)), target)
        elif isinstance(node.rvalue, ast.UnaryOp):
            inst = ('store_' + self.func_and_var_types[lvalue_name] + pointer_modifier,
                    node.rvalue.id,
                    target)
        elif isinstance(node.rvalue, ast.Constant):
            if node.op in oper_ops:
                self.visit_LoadLocation(node.lvalue)
                inst = (oper_ops[node.op] + '_' + node.rvalue.type, node.lvalue.id,
                        node.rvalue.id, self.new_temp('const%d' % self.const_count))
                self.code.append(inst)
                inst = (
                    'store_' + node.rvalue.type + pointer_modifier, self.new_temp('const%d' % self.const_count), target)
                self.const_count += 1
            else:
                inst = ('store_' + node.rvalue.type + pointer_modifier, node.rvalue.id, target)
        elif isinstance(node.rvalue, ast.Cast):
            inst = ('store_' + node.rvalue.to_type.names[0] + pointer_modifier, node.rvalue.id, target)
        elif isinstance(node.rvalue, ast.ID):
            inst = ('store_' + self.func_and_var_types[node.rvalue.name] + pointer_modifier, node.rvalue.id, target)
        elif isinstance(node.rvalue, ast.ArrayRef):
            rvalue_name = node.rvalue.name
            while not isinstance(rvalue_name, ast.ID):
                rvalue_name = rvalue_name.name
            rvalue_name = rvalue_name.name
            type = self.func_and_var_types[rvalue_name]['type']
            if type == 'string':
                type = 'char'
            inst = ('store_' + type + pointer_modifier, node.rvalue.id, target)
        self.code.append(inst)

    def visit_BinaryOp(self, node):
        # Visit the left and right expressions
        self.visit(node.right)
        self.visit(node.left)

        # Make a new temporary for storing the result
        target = self.new_temp('binop%d' % self.const_count)
        node.id = self.const_count
        self.const_count += 1

        # Create the opcode and append to list

        if isinstance(node.left, ast.BinaryOp):
            left = self.new_temp('binop%d' % node.left.id)
            opcode = binary_ops[node.op] + "_" + self.func_and_var_types[node.left.id.__str__()]
            if binary_ops[node.op] in bool_ops:
                self.func_and_var_types[node.id.__str__()] = 'bool'
            else:
                self.func_and_var_types[node.id.__str__()] = self.func_and_var_types[node.left.id.__str__()]
        else:
            if isinstance(node.left, ast.FuncCall):
                opcode = binary_ops[node.op] + "_" + self.func_and_var_types[node.left.name.name]
            elif isinstance(node.left, ast.ArrayRef):
                name = node.left.name
                while not isinstance(name, ast.ID):
                    name = name.name
                name = name.name
                opcode = binary_ops[node.op] + "_" + self.func_and_var_types[name]['type']
            elif isinstance(node.left, ast.Constant):
                opcode = binary_ops[node.op] + "_" + node.left.type
            else:
                opcode = binary_ops[node.op] + "_" + self.func_and_var_types[node.left.name]
            if binary_ops[node.op] in bool_ops:
                self.func_and_var_types[node.id.__str__()] = 'bool'
            else:
                if isinstance(node.left, ast.ID):
                    self.func_and_var_types[node.id.__str__()] = self.func_and_var_types[node.left.name]
                elif isinstance(node.left, ast.FuncCall):
                    self.func_and_var_types[node.id.__str__()] = self.func_and_var_types[node.left.name.name]
                elif isinstance(node.left, ast.ArrayRef):
                    self.func_and_var_types[node.id.__str__()] = self.func_and_var_types[node.left.name.name.name]['type']
                else:
                    self.func_and_var_types[node.id.__str__()] = node.left.type
            if isinstance(node.left, ast.FuncCall):
                left = self.new_temp('call_%s_%d' % (node.left.name.name, node.left.id))
            else:
                left = node.left.id

        if isinstance(node.right, ast.BinaryOp):
            right = self.new_temp('binop%d' % node.right.id)
        elif isinstance(node.right, ast.FuncCall):
            right = self.new_temp('call_%s_%d' % (node.right.name.name, node.right.id))
        else:
            # if isinstance(node.right, ast.ID):
            #     self.func_and_var_types[node.id.__str__()] = self.func_and_var_types[node.right.name]
            # else:
            #     self.func_and_var_types[node.id.__str__()] = node.right.type
            right = node.right.id

        inst = (opcode, left, right, target)
        self.code.append(inst)

    def visit_Cast(self, node):
        self.visit(node.expr)
        if isinstance(node.expr, ast.ID):
            og_type = cast_types[self.func_and_var_types[node.expr.name]]
        to_type = cast_types[node.to_type.names[0]]
        inst = (og_type + 'to' + to_type, node.expr.id, self.new_temp('cast%d' % self.const_count))
        self.code.append(inst)
        node.id = self.new_temp('cast%d' % self.const_count)
        self.const_count += 1

    def visit_Compound(self, node):
        for item in node.block_items:
            self.visit(item)

    def visit_Constant(self, node):
        # Create a new temporary variable name
        if node.type != 'string':
            target = self.new_temp('const%d' % self.const_count)
            self.const_count += 1

            # Make the SSA opcode and append to list of generated instructions
            type = node.type
            if type == 'int':
                inst = ('literal_int', int(node.value), target)
            elif type == 'float':
                inst = ('literal_float', float(node.value), target)
            else:
                inst = ('literal_char', node.value[1:-1], target)
            self.code.append(inst)

            # Save the name of the temporary variable where the value was placed
            node.id = target
        else:
            type = 'string'
            self.func_and_var_types['.str.%d' % self.str_count] = {'type': 'char',
                                                                   'size': '_' + str(len(node.value))}
            inst = ('global_' + type, self.new_global('.str.%d' % self.str_count), node.value)
            self.global_code.append(inst)
            node.id = self.new_global('.str.%d' % self.str_count)
            self.str_count += 1

    def visit_Decl(self, node):
        if isinstance(node.type, ast.FuncDecl):
            self.visit(node.type)
        elif isinstance(node.type, ast.ArrayDecl):
            if node.init is not None:
                if isinstance(node.init, ast.Constant):
                    type = 'string'
                    size = str(len(node.init.value))
                    self.func_and_var_types['.str.%d' % self.str_count] = {'type': 'char', 'size': '_' + size}
                    inst = ('global_' + type, self.new_global('.str.%d' % self.str_count), node.init.value)
                else:
                    init, type = self.visit(node.init)
                    full_size = len(init)
                    size = ''
                    next = init[0]
                    while hasattr(next, '__len__'):
                        full_size *= len(next)
                        size = size + '_' + str(len(next))
                        next = next[0]
                    size = '_' + str(full_size) + size
                    self.func_and_var_types['.str.%d' % self.str_count] = {'type': type, 'size': size}
                    inst = ('global_' + type + size, self.new_global('.str.%d' % self.str_count), init)
                self.str_count += 1
                self.global_code.append(inst)

                self.func_and_var_types[node.name.name] = {'type': type, 'size': size}
            else:
                type = node.type
                while not isinstance(type, ast.Type):
                    type = type.type
                type = type.names[0]
                size = '_' + node.type.dim.value
                next = node.type.type
                while isinstance(next, ast.ArrayDecl):
                    size = size + '_' + next.dim.value
                    next = next.type
                self.func_and_var_types['array%d' % self.const_count] = {'type': type, 'size': size}
                self.func_and_var_types[node.name.name] = {'type': type, 'size': size}
                self.const_count += 1
            node.type.id = self.new_temp(node.name.name)
            self.visit(node.type)
        else:
            target = self.new_temp(node.name.name)
            node.type.id = target
            if isinstance(node.type, ast.VarDecl):
                self.func_and_var_types[node.name.name] = node.type.type.names[0]
            self.visit(node.type)
            # store optional init val
            if isinstance(node.init, ast.Constant):
                self.visit(node.init)
                inst = ('store_' + node.init.type, node.init.id, target)
                self.code.append(inst)
            elif isinstance(node.init, ast.FuncCall):
                self.visit(node.init)
                inst = ('store_' + self.func_and_var_types[node.init.name.name],
                        self.new_temp('call_%s_%d' % (node.init.name.name, node.init.id)), target)
                self.code.append(inst)
            elif isinstance(node.init, ast.ID):
                self.visit(node.init)
                inst = ('store_' + self.func_and_var_types[node.init.name], node.init.id, target)
                self.code.append(inst)

    def visit_ExprList(self, node):
        for expr in node.exprs:
            self.visit(expr)

    def visit_Break(self, node):
        # self.waiting_for_label.append(len(self.code))
        inst = ('jump', '%' + str(self.break_label()))
        self.code.append(inst)

    def visit_For(self, node):
        for_count = self.const_count
        self.new_temp('for%d_label1' % for_count)
        self.new_temp('for%d_label2' % (for_count + 1))
        self.new_temp('for%d_label3' % (for_count + 2))
        self.const_count += 3

        if isinstance(node.init, ast.ExprList):
            for expr in node.init.exprs:
                t = self.visit(expr)
                if t == 'break':
                    return
        elif isinstance(node.init, ast.DeclList):
            for decl in node.init.decls:
                t = self.visit(decl)
                if t == 'break':
                    return
        else:
            self.visit(node.init)
        inst = (self.new_temp('for%d_label1' % for_count)[1:],)
        self.code.append(inst)

        if node.cond is not None:
            self.visit(node.cond)

        inst = ('cbranch', self.new_temp('binop%d' % node.cond.id),
                self.new_temp('for%d_label2' % (for_count + 1)),
                self.new_temp('for%d_label3' % (for_count + 2)))
        self.code.append(inst)
        inst = (self.new_temp('for%d_label2' % (for_count + 1))[1:],)
        self.code.append(inst)

        self.visit(node.stmt)
        if node.next is not None:
            self.visit(node.next)
        inst = ('jump', self.new_temp('for%d_label1' % for_count))
        self.code.append(inst)

        inst = (self.new_temp('for%d_label3' % (for_count + 2))[1:],)
        self.code.append(inst)

    def visit_FuncCall(self, node):
        for arg in node.args.exprs:
            if isinstance(arg, ast.BinaryOp):
                self.visit(arg)
            else:
                self.visit_LoadLocation(arg)
            if isinstance(arg, ast.ID):
                inst = ('param_' + self.func_and_var_types[arg.name], arg.id)
                self.code.append(inst)
            elif isinstance(arg, ast.Constant):
                inst = ('param_' + arg.type, arg.id)
                self.code.append(inst)
            elif isinstance(arg, ast.BinaryOp):
                inst = ('param_' + self.func_and_var_types[arg.id.__str__()], self.new_temp('binop%d' % arg.id))
                self.code.append(inst)
        target = self.new_temp('call_%s_%d' % (node.name.name, self.const_count))
        node.id = self.const_count
        self.const_count += 1
        inst = ('call', '@' + node.name.name, target)
        self.code.append(inst)

    def visit_FuncDecl(self, node):
        if node.args is not None:
            for arg in node.args.params:
                self.new_temp(self.fname.peek() + '_' + arg.name.name, True)
            self.new_temp(self.fname.peek() + '_return')
            self.visit(node.args)
            for arg in node.args.params:
                inst = ('store_' + arg.type.type.names[0], self.new_temp(self.fname.peek() + '_' + arg.name.name), arg.id)
                self.code.append(inst)
        else:
            self.new_temp(self.fname.peek() + '_return')
        self.new_temp(self.fname.peek() + '_label')

    def visit_FuncDef(self, node):
        self.func_and_var_types[node.decl.name.name] = node.decl.type.type.type.names[0]
        inst = ('define', '@' + node.decl.name.name)
        self.code.append(inst)
        self.visit(node.decl)
        self.visit(node.body)
        if not isinstance(node.body.block_items[-1], ast.Return):
            inst = (self.new_temp(self.fname.peek() + '_label')[1:],)
            if self.code.__contains__(inst) is False:
                self.code.append(inst)
            # self.code.append(inst)

    def visit_GlobalDecl(self, node):
        for decl in node.decls:
            if isinstance(decl.type, ast.FuncDecl):
                type = decl.type.type.type.names[0]
                self.func_and_var_types[decl.name.name] = type
                value = decl.name.name
                target = self.new_global(decl.name.name)
                inst = ('global_' + type, target, value)
                self.global_code.append(inst)
            elif isinstance(decl.type, ast.ArrayDecl):
                if isinstance(decl.init, ast.Constant):
                    type = 'string'
                    size = str(len(decl.init.value))
                    self.func_and_var_types[decl.name.name] = {'type': 'char', 'size': '_' + size}
                    inst = ('global_' + type, self.new_global(decl.name.name), decl.init.value)
                else:
                    init, type = self.visit(decl.init)
                    full_size = len(init)
                    size = ''
                    next = init[0]
                    while hasattr(next, '__len__'):
                        full_size *= len(next)
                        size = size + '_' + str(len(next))
                        next = next[0]
                    size = '_' + str(full_size) + size
                    self.func_and_var_types[decl.name.name] = {'type': type, 'size': size}
                    inst = ('global_' + type + size, self.new_global(decl.name.name), init)
                self.str_count += 1
                self.global_code.append(inst)
            else:
                type = decl.type.type.names[0]
                self.func_and_var_types[decl.name.name] = type
                if type == 'int':
                    value = int(decl.init.value)
                elif type == 'float':
                    value = float(decl.init.value)
                else:
                    value = decl.init.value
                target = self.new_global(decl.name.name)
                inst = ('global_' + type, target, value)
                self.global_code.append(inst)

    def visit_ID(self, node):
        self.visit_LoadLocation(node)

    def visit_If(self, node):
        if_count = self.const_count
        self.new_temp('if%d_label1' % if_count)
        self.new_temp('if%d_label2' % (if_count + 1))
        self.const_count += 2
        self.visit(node.cond)

        inst = ('cbranch', self.new_temp('binop%d' % node.cond.id), self.new_temp('if%d_label1' % if_count),
                self.new_temp('if%d_label2' % (if_count + 1)))
        self.code.append(inst)
        inst = (self.new_temp('if%d_label1' % if_count)[1:],)
        self.code.append(inst)

        t = self.visit(node.iftrue)
        if t == 'break':
            return 'break'

        inst = (self.new_temp('if%d_label2' % (if_count + 1))[1:],)
        self.code.append(inst)

        if node.iffalse is not None:
            t = self.visit(node.iffalse)
            if t == 'break':
                return 'break'

    def visit_InitList(self, node):
        initlist = []
        type = None
        for expr in node.exprs:
            if isinstance(expr, ast.InitList):
                init, type = self.visit(expr)
                initlist.append(init)
            else:
                type = node.exprs[0].type
                initlist.append(eval(type)(expr.value))
        return initlist, type

    def visit_LoadLocation(self, node):
        if isinstance(node, ast.Return):
            if isinstance(node.expr, ast.Constant):
                return_place = self.new_temp(self.fname.peek() + '_return')
                target = self.new_temp('const%d' % self.const_count)
                node.expr.id = self.const_count
                self.const_count += 1
                inst = ('load_' + node.expr.type, return_place, target)
                self.code.append(inst)
            elif isinstance(node.expr, ast.ID):
                return_place = self.new_temp(self.fname.peek() + '_return')
                target = self.new_temp('const%d' % self.const_count)
                node.expr.id = self.const_count
                self.const_count += 1
                inst = ('load_' + self.func_and_var_types[node.expr.name], return_place, target)
                self.code.append(inst)
            elif isinstance(node.expr, ast.BinaryOp):
                return_place = self.new_temp(self.fname.peek() + '_return')
                target = self.new_temp('const%d' % self.const_count)
                node.expr.id = self.const_count
                self.const_count += 1
                inst = ('load_' + self.func_and_var_types[self.fname.peek()], return_place, target)
                self.code.append(inst)
        elif isinstance(node, ast.ID):
            node.id = self.new_temp('load_' + node.name + '_%d' % self.const_count)
            self.const_count += 1
            origin = self.new_temp(node.name)
            type = self.func_and_var_types[node.name]
            if isinstance(type, dict):
                type = type['type']
            inst = ('load_' + type, origin, node.id)
            self.code.append(inst)
        elif isinstance(node, ast.Constant):
            self.visit(node)

    def visit_ParamList(self, node):
        for param in node.params:
            self.func_and_var_types[param.name.name] = param.type.type.names[0]
            param.id = self.new_temp(param.name.name, True)
            inst = ('alloc_' + param.type.type.names[0], param.id)
            self.code.append(inst)

    def visit_Print(self, node):
        # Visit the expression
        self.visit(node.expr)
        # if isinstance(node, ast.ID):
        if isinstance(node.expr, ast.Constant):
            inst = ('print_' + node.expr.type, node.expr.id)
            self.code.append(inst)
        elif isinstance(node.expr, ast.ID):
            type = self.func_and_var_types[node.expr.name]
            if isinstance(type, dict):
                type = type['type']
            inst = ('print_' + type, node.expr.id)
            self.code.append(inst)
        elif isinstance(node.expr, ast.ExprList):
            for expr in node.expr:
                if isinstance(expr, ast.Constant):
                    inst = ('print_' + expr.type, expr.id)
                    self.code.append(inst)
                elif isinstance(expr, ast.ID):
                    inst = ('print_' + self.func_and_var_types[expr.name], expr.id)
                    self.code.append(inst)
                elif isinstance(expr, ast.ArrayRef):
                    name = expr.name
                    while not isinstance(name, ast.ID):
                        name = name.name
                    name = name.name
                    type = self.func_and_var_types[name]['type']
                    if type == 'string':
                        type = 'char'
                    inst = ('print_' + type, expr.id)
                    self.code.append(inst)
        elif isinstance(node.expr, ast.ArrayRef):
            name = node.expr.name
            while isinstance(name, ast.ArrayRef):
                name = name.name
            name = name.name
            type = self.func_and_var_types[name]['type']
            inst = ('print_' + type, node.expr.id)
            self.code.append(inst)
        elif node.expr is None:
            inst = ('print_void',)
            self.code.append(inst)

    def visit_Program(self, node):
        # 1. Visit all of the global declarations
        # 2. Record the associated symbol table
        for decl in node.gdecls:
            if isinstance(decl, ast.FuncDef):
                self.fname.push(decl.decl.name.name)
                self.visit(decl)
                self.versions[self.fname.pop()] = {}
                # dot = CFG(decl.decl.name.name)
                # dot.view(decl.cfg)
            else:
                self.visit(decl)

            # if isinstance(_decl, FuncDef):
            #     dot = CFG(_decl.decl.name.name)
            #     dot.view(_decl.cfg)

        self.global_code.extend(self.code)
        # for line in self.global_code:
        #     print(line)
        return self.global_code

    def visit_Read(self, node):
        for expr in node.expr:
            if isinstance(expr, ast.ID):
                inst = ('read_' + self.func_and_var_types[expr.name], self.new_temp('const%d' % self.const_count))
                self.code.append(inst)
                inst = ('store_' + self.func_and_var_types[expr.name], self.new_temp('const%d' % self.const_count),
                        self.new_temp(expr.name))
                self.code.append(inst)
                self.const_count += 1
            elif isinstance(expr, ast.ArrayRef):
                self.visit(expr)
                name = expr.name
                while not isinstance(name, ast.ID):
                    name = name.name
                name = name.name
                inst = ('read_' + self.func_and_var_types[name]['type'], self.new_temp('const%d' % self.const_count))
                self.code.append(inst)
                inst = ('store_' + self.func_and_var_types[name]['type'], self.new_temp('const%d' % self.const_count),
                        self.new_temp(name))
                self.code.append(inst)
                self.const_count += 1

    def visit_Return(self, node):
        if isinstance(node.expr, ast.Constant):
            self.visit(node.expr)
            inst = ('store_' + node.expr.type, node.expr.id, self.new_temp(self.fname.peek() + '_return'))
            self.code.append(inst)
        elif isinstance(node.expr, ast.BinaryOp):
            self.visit(node.expr)
            inst = ('store_' + self.func_and_var_types[self.fname.peek()], self.new_temp('binop%d' % node.expr.id),
                    self.new_temp(self.fname.peek() + '_return'))
            self.code.append(inst)
        elif isinstance(node.expr, ast.ID):
            inst = ('store_' + self.func_and_var_types[self.fname.peek()], self.new_temp(node.expr.name),
                    self.new_temp(self.fname.peek() + '_return'))
            self.code.append(inst)

        inst = ('jump', self.new_temp(self.fname.peek() + '_label'))
        self.code.append(inst)
        inst = (self.new_temp(self.fname.peek() + '_label')[1:],)
        if self.code.__contains__(inst) is False:
            self.code.append(inst)
        if node.expr is not None:
            self.visit_LoadLocation(node)
            if self.func_and_var_types[self.fname.peek()] == 'void':
                inst = ('return_' + self.func_and_var_types[self.fname.peek()],)
            else:
                inst = ('return_' + self.func_and_var_types[self.fname.peek()], self.new_temp('const%d' % node.expr.id))
        else:
            inst = ('return_void',)
        self.code.append(inst)

    def visit_UnaryOp(self, node):
        if isinstance(node.expr, ast.ID):
            self.visit_LoadLocation(node.expr)
            if node.op == '++' or node.op == 'p++':
                inst = ('literal_' + self.func_and_var_types[node.expr.name],
                        1, self.new_temp('const%d' % self.const_count))
                self.code.append(inst)
                inst = ('add_' + self.func_and_var_types[node.expr.name],
                        node.expr.id, self.new_temp('const%d' % self.const_count),
                        self.new_temp('const%d' % (self.const_count + 1)))
                self.code.append(inst)
                inst = ('store_' + self.func_and_var_types[node.expr.name],
                        self.new_temp('const%d' % (self.const_count + 1)),
                        self.new_temp(node.expr.name))
                self.code.append(inst)
                if node.op == '++':
                    node.id = self.new_temp('const%d' % (self.const_count + 1))
                else:
                    node.id = node.expr.id
                self.const_count += 2

    def visit_VarDecl(self, node):
        # allocate on stack memory
        inst = ('alloc_' + node.type.names[0], node.id)
        self.code.append(inst)

    # def visit_UnaryOp(self, node):
    #     self.visit(node.left)
    #     target = self.new_temp()
    #     # opcode = unary_ops[node.op] + "_" + node.left.type.name
    #     # inst = (opcode, node.left.gen_location)
    #     # self.code.append(inst)
    #     node.gen_location = target

    def visit_While(self, node):
        while_count = self.const_count
        self.new_temp('while%d_label1' % while_count)
        self.new_temp('while%d_label2' % (while_count + 1))
        self.new_temp('while%d_label3' % (while_count + 2))
        self.const_count += 3

        inst = (self.new_temp('while%d_label1' % while_count)[1:],)
        self.code.append(inst)

        if node.cond is not None:
            self.visit(node.cond)

        if isinstance(node.cond, ast.BinaryOp):
            inst = ('cbranch', self.new_temp('binop%d' % node.cond.id),
                    self.new_temp('while%d_label2' % (while_count + 1)),
                    self.new_temp('while%d_label3' % (while_count + 2)))
        else:
            inst = ('cbranch', node.cond.id, self.new_temp('while%d_label2' % (while_count + 1)),
                    self.new_temp('while%d_label3' % (while_count + 2)))
        self.code.append(inst)
        inst = (self.new_temp('while%d_label2' % (while_count + 1))[1:],)
        self.code.append(inst)

        self.visit(node.stmt)

        inst = ('jump', self.new_temp('while%d_label1' % while_count))
        self.code.append(inst)

        inst = (self.new_temp('while%d_label3' % (while_count + 2))[1:],)
        self.code.append(inst)

    def visit_NoneType(self, node):
        pass