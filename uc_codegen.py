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

oper_ops = {"+=": "add", "-=": "sub", "/=": "div", "*=": "mult", "%/": "mod"}

bool_ops = ["eq", "ne", "lt", "le", "gt", "ge", "and", "or", "not"]


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

    def new_temp(self, varname):
        """
        Create a new temporary variable of a given scope (function name).
        """
        if self.fname.peek() not in self.versions:
            self.versions[self.fname.peek()] = {}
            self.versions[self.fname.peek()]['number'] = 0
            self.versions[self.fname.peek()]['vars'] = {}
        if varname not in self.versions[self.fname.peek()]['vars']:
            for fname in self.fname.all():
                if varname in self.versions[fname]['vars'] and fname != self.fname.peek():
                    name = self.versions[fname]['vars'][varname]
                    if isinstance(name, int):
                        name = '%' + name.__str__()
                    return name
            self.versions[self.fname.peek()]['vars'][varname] = self.versions[self.fname.peek()]['number']
            self.versions[self.fname.peek()]['number'] += 1
        name = self.versions[self.fname.peek()]['vars'][varname]
        if isinstance(name, int):
            name = '%' + name.__str__()
        return name

    def new_global(self, varname):
        if varname not in self.versions['global']['vars']:
            self.versions['global']['vars'][varname] = '@' + varname
        return self.versions['global']['vars'][varname]

    # Node visitor methods

    def visit_ArrayDecl(self, node):
        str_info = self.func_and_var_types['.str.%d' % (self.str_count - 1)]
        inst = ('alloc_' + str_info['type'] + str_info['size'], node.id)
        self.code.append(inst)
        inst = ('store_' + str_info['type'] + str_info['size'], self.new_global('.str.%d' % (self.str_count - 1)), node.id)
        self.code.append(inst)

    def visit_Assert(self, node):
        if isinstance(node.expr, ast.BinaryOp):
            self.visit(node.expr)
        inst = ('cbranch', self.new_temp('binop%d' % node.expr.id), self.new_temp('assert%d_label_1' % self.const_count), self.new_temp('assert%d_label_2' % (self.const_count + 1)))
        self.code.append(inst)

        inst = (self.new_temp('assert%d_label_1' % self.const_count)[1:],)
        self.code.append(inst)
        inst = ('jump', self.new_temp('assert%d_label_1' % (self.const_count + 2)))
        self.code.append(inst)

        inst = (self.new_temp('assert%d_label_2' % (self.const_count + 1))[1:],)
        self.code.append(inst)
        inst = ('global_string', self.new_global('.str.%d' % self.str_count), 'assertion_fail on %s:%s' % (node.coord.line, node.coord.column))
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
        if isinstance(node.rvalue, ast.BinaryOp):
            if isinstance(node.rvalue.left, ast.Constant):
                type = node.rvalue.left.type
            elif isinstance(node.rvalue.left, ast.ID):
                type = self.func_and_var_types[node.rvalue.left.name]
            if node.op in oper_ops:
                self.visit_LoadLocation(node.lvalue)
                inst = (oper_ops[node.op] + '_' + type, self.new_temp('binop%d' % node.rvalue.id),
                        node.lvalue.id, self.new_temp('const%d' % self.const_count))
                self.code.append(inst)
                inst = ('store_' + type, self.new_temp('const%d' % self.const_count), self.new_temp(node.lvalue.name))
            else:
                inst = ('store_' + type, self.new_temp('binop%d' % node.rvalue.id), self.new_temp(node.lvalue.name))
        elif isinstance(node.rvalue, ast.FuncCall):
            inst = ('store_' + self.func_and_var_types[node.rvalue.name.name],
                    self.new_temp('call_%s_%d' % (node.rvalue.name.name, node.rvalue.id)),
                    self.new_temp(node.lvalue.name))
        elif isinstance(node.rvalue, ast.UnaryOp):
            inst = ('store_' + self.func_and_var_types[node.lvalue.name],
                    node.rvalue.id,
                    self.new_temp(node.lvalue.name))
        elif isinstance(node.rvalue, ast.Constant):
            inst = ('store_' + node.rvalue.type, node.rvalue.id, self.new_temp(node.lvalue.name))
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
            opcode = binary_ops[node.op] + "_" + self.func_and_var_types[node.left.name]
            if binary_ops[node.op] in bool_ops:
                self.func_and_var_types[node.id.__str__()] = 'bool'
            else:
                if isinstance(node.left, ast.ID):
                    self.func_and_var_types[node.id.__str__()] = self.func_and_var_types[node.left.name]
                else:
                    self.func_and_var_types[node.id.__str__()] = node.left.type
            left = node.left.id

        if isinstance(node.right, ast.BinaryOp):
            right = self.new_temp('binop%d' % node.right.id)
        else:
            # if isinstance(node.right, ast.ID):
            #     self.func_and_var_types[node.id.__str__()] = self.func_and_var_types[node.right.name]
            # else:
            #     self.func_and_var_types[node.id.__str__()] = node.right.type
            right = node.right.id

        inst = (opcode, right, left, target)
        self.code.append(inst)

        # Store location of the result on the node
        node.gen_location = target

    def visit_Compound(self, node):
        for item in node.block_items:
            self.visit(item)

    def visit_Constant(self, node):
        # Create a new temporary variable name
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

    def visit_Decl(self, node):
        if isinstance(node.type, ast.FuncDecl):
            self.visit(node.type)
        elif isinstance(node.type, ast.ArrayDecl):
            if node.init is not None:
                type = node.type.type.type.names[0]
                if type == 'char':
                    type = 'string'
                    self.func_and_var_types['.str.%d' % self.str_count] = {'type': 'char', 'size': '_' + str(len(node.init.value))}
                    inst = ('global_' + type, self.new_global('.str.%d' % self.str_count), node.init.value)
                else:
                    init = self.visit(node.init)
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
                node.type.id = self.new_temp(node.name.name)
                self.str_count += 1
                self.global_code.append(inst)
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
                inst = ('store_' + self.func_and_var_types[node.init.name.name], self.new_temp('call_%s_%d' % (node.init.name.name, node.init.id)), target)
                self.code.append(inst)
            elif isinstance(node.init, ast.ID):
                self.visit(node.init)
                inst = ('store_' + self.func_and_var_types[node.init.name], node.init.id, target)
                self.code.append(inst)

    def visit_For(self, node):
        for_count = self.const_count
        self.new_temp('for%d_label1' % for_count)
        self.new_temp('for%d_label2' % (for_count + 1))
        self.new_temp('for%d_label3' % (for_count + 2))
        self.const_count += 3

        if node.init is not None:
            for decl in node.init.decls:
                self.visit(decl)
        inst = (self.new_temp('for%d_label1' % for_count)[1:], )
        self.code.append(inst)

        if node.cond is not None:
            self.visit(node.cond)

        inst = ('cbranch', self.new_temp('binop%d' % node.cond.id),
                self.new_temp('for%d_label2' % (for_count + 1)),
                self.new_temp('for%d_label3' % (for_count + 2)))
        self.code.append(inst)
        inst = (self.new_temp('for%d_label2' % (for_count + 1))[1:],)
        self.code.append(inst)

        print(node.stmt)
        self.visit(node.stmt)
        if node.next is not None:
            self.visit(node.next)
        inst = ('jump', self.new_temp('for%d_label1' % for_count))
        self.code.append(inst)

        inst = (self.new_temp('for%d_label3' % (for_count + 2))[1:],)
        self.code.append(inst)

    def visit_FuncCall(self, node):
        for arg in node.args.exprs:
            self.visit_LoadLocation(arg)
            if isinstance(arg, ast.ID):
                inst = ('param_' + self.func_and_var_types[arg.name], arg.id)
                self.code.append(inst)
            elif isinstance(arg, ast.Constant):
                inst = ('param_' + arg.type, arg.id)
                self.code.append(inst)
        target = self.new_temp('call_%s_%d' % (node.name.name, self.const_count))
        node.id = self.const_count
        self.const_count += 1
        inst = ('call', node.name.name, target)
        self.code.append(inst)

    def visit_FuncDecl(self, node):
        if node.args is not None:
            for arg in node.args.params:
                self.new_temp(self.fname.peek() + '_' + arg.name.name)
            self.new_temp(self.fname.peek() + '_return')
            self.visit(node.args)
            for arg in node.args.params:
                inst = ('store_' + arg.type.type.names[0], self.new_temp(self.fname.peek() + '_' + arg.name.name), self.new_temp(arg.name.name))
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
            self.code.append(inst)

    def visit_GlobalDecl(self, node):
        self.func_and_var_types[node.decl.name.name] = node.decl.type.type.names[0]

        target = self.new_global(node.decl.name.name)
        inst = ('global_' + node.decl.type.type.names[0], target, node.decl.init.value)
        self.global_code.append(inst)

    def visit_ID(self, node):
        self.visit_LoadLocation(node)

    def visit_InitList(self, node):
        initlist = []
        for expr in node.exprs:
            if isinstance(expr, ast.InitList):
                initlist.append(self.visit(expr))
            else:
                type = node.exprs[0].type
                initlist.append(eval(type)(expr.value))
        return initlist

    def visit_LoadLocation(self, node):
        if isinstance(node, ast.Return):
            if isinstance(node.expr, ast.Constant):
                return_place = self.new_temp(self.fname.peek() + '_return')
                target = self.new_temp('const%d' % self.const_count)
                node.expr.id = self.const_count
                self.const_count += 1
                inst = ('load_' + node.expr.type, return_place, target)
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
            self.const_count +=1
            origin = self.new_temp(node.name)
            inst = ('load_' + self.func_and_var_types[node.name], origin, node.id)
            self.code.append(inst)
        elif isinstance(node, ast.Constant):
            self.visit(node)

    # def visit_ParamList(self, node):
    #

    def visit_PrintStatement(self, node):
        # Visit the expression
        self.visit(node.expr)

        # Create the opcode and append to list
        inst = ('print_' + node.expr.type.name, node.expr.gen_location)
        self.code.append(inst)

    def visit_Program(self, node):
        # 1. Visit all of the global declarations
        # 2. Record the associated symbol table
        for decl in node.gdecls:
            if isinstance(decl, ast.FuncDef):
                self.fname.push(decl.decl.name.name)
                self.visit(decl)
                self.versions[self.fname.pop()] = {}
            else:
                self.visit(decl)

        for line in self.global_code:
            print(line)
        for line in self.code:
            print(line)

    def visit_Return(self, node):
        if isinstance(node.expr, ast.Constant):
            self.visit(node.expr)
            inst = ('store_' + node.expr.type, node.expr.id, self.new_temp(self.fname.peek() + '_return'))
            self.code.append(inst)
        elif isinstance(node.expr, ast.BinaryOp):
            self.visit(node.expr)
            inst = ('store_' + self.func_and_var_types[self.fname.peek()], self.new_temp('binop%d' % node.expr.id), self.new_temp(self.fname.peek() + '_return'))
            self.code.append(inst)

        inst = ('jump', self.new_temp(self.fname.peek() + '_label'))
        self.code.append(inst)
        inst = (self.new_temp(self.fname.peek() + '_label')[1:],)
        self.code.append(inst)
        if node.expr is not None:
            self.visit_LoadLocation(node)
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

    def visit_NoneType(self, node):
        pass
