from symbolTable import SymbolTable

import ast
import uctype
# from uc import subscribe_errors


class NodeVisitor(object):
    """ A base NodeVisitor class for visiting uc_ast nodes.
        Subclass it and define your own visit_XXX methods, where
        XXX is the class name you want to visit with these
        methods.
        For example:
        class ConstantVisitor(NodeVisitor):
            def __init__(self):
                self.values = []
            def visit_Constant(self, node):
                self.values.append(node.value)
        Creates a list of values of all the constant nodes
        encountered below the given node. To use it:
        cv = ConstantVisitor()
        cv.visit(node)
        Notes:
        *   generic_visit() will be called for AST nodes for which
            no visit_XXX method was defined.
        *   The children of nodes for which a visit_XXX was
            defined will not be visited - if you need this, call
            generic_visit() on the node.
            You can use:
                NodeVisitor.generic_visit(self, node)
        *   Modeled after Python's own AST visiting facilities
            (the ast module of Python 3.0)
    """

    _method_cache = None

    def visit(self, node):
        """ Visit a node.
        """

        if self._method_cache is None:
            self._method_cache = {}

        visitor = self._method_cache.get(node.__class__.__name__, None)
        if visitor is None:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            self._method_cache[node.__class__.__name__] = visitor

        return visitor(node)

    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        for c in node:
            # (c)
            self.visit(c)

    # def visit_NoneType(self, node):
    #     print("entrou")





class Visitor(NodeVisitor):


    def extract_types(self, param_list):
        type = []
        for p in param_list.params:
            type.append(self.symtab.lookup(p.name.name).typename)
        return type

    def check_params(self, params_reg, params_actual):
        to_type = self.extract_types(params_reg)
        return to_type == params_actual

    '''
    Program visitor class. This class uses the visitor pattern. You need to define methods
    of the form visit_NodeName() for each kind of AST node that you want to process.
    Note: You will need to adjust the names of the AST nodes if you picked different names.
    '''

    def __init__(self):
        # Initialize the symbol table
        self.symtab = SymbolTable()
        self.functions = {}
        self.error_vector = []

        # Add built-in type names (int, float, char) to the symbol table
        # self.symtab.add("int", uctype.IntType)
        # self.symtab.add("float",uctype.float_type)
        # self.symtab.add("char",uctype.char_type)

    def print_error(self):
        if len(self.error_vector) > 0:
            for i in self.error_vector:
                print(i)

    def error(self, message):
        self.error_vector.append("Error: " + message)


    def visit_Program(self, node):
        # 1. Visit all of the global declarations
        # 2. Record the associated symbol table
        self.symtab.begin_scope()
        for _decl in node.gdecls:
            self.visit(_decl)
        self.symtab.end_scope()

    def visit_GlobalDecl(self, node):
        type = self.visit(node.decl)

    def visit_Decl(self, node):
        type = self.visit(node.type)
        if isinstance(node.type, ast.ArrayDecl):
            if node.type.dim is not None and node.init is not None:
                if node.type.dim.value != str(len(node.init.exprs)):
                    if node.coord is not None:
                        self.error("size mismatch on initialization" + str(node.coord))
                    else:
                        self.error("size mismatch on initialization")

            if type == 'int':
                self.symtab.add(node.name.name, uctype.IntArrayType)
            elif type == 'float':
                self.symtab.add(node.name.name, uctype.FloatArrayType)
            elif type == 'char':
                self.symtab.add(node.name.name, uctype.CharArrayType)

            init = self.visit(node.init)
            if init is not None:
                if init != type:
                    if init == 'string' and type == 'char':
                        pass
                    else:
                        self.error("initializer mismatch" + str(node.coord))

        elif isinstance(node.type, ast.FuncDecl):
            if type == 'int':
                self.symtab.add(node.name.name, uctype.IntType)
            elif type == 'float':
                self.symtab.add(node.name.name, uctype.FloatType)
            elif type == 'char':
                self.symtab.add(node.name.name, uctype.CharType)
            elif type == 'void':
                self.symtab.add(node.name.name, uctype.VoidType)
            else:
                self.error("invalid type" + str(node.coord))

            init = self.visit(node.init)
            if init is not None:
                if init != type:
                    self.error("initializer mismatch" + str(node.coord))
        else:
            if type == 'int':
                self.symtab.add(node.name.name, uctype.IntType)
            elif type == 'float':
                self.symtab.add(node.name.name, uctype.FloatType)
            elif type == 'char':
                self.symtab.add(node.name.name, uctype.CharType)
            elif type == 'void':
                self.symtab.add(node.name.name, uctype.VoidType)
            else:
                self.error("invalid type" + str(node.coord))

            init = self.visit(node.init)
            if init is not None:
                if init != type:
                    self.error("initializer mismatch" + str(node.coord))

        return type

    def visit_VarDecl(self, node):
        node1 = self.visit(node.declname)
        node2 = self.visit(node.type)
        if node2 == "int":
            return 'int'
        elif node2 == "char":
            return 'char'
        elif node2 == "float":
            return 'float'
        elif node2 == "void":
            return 'void'
        else:
            self.error("variable {} has an invalid type : ".format(node1.name) + str(node.coord))

    def visit_Type(self, node):
        return node.names[0]

    def visit_BinaryOp(self, node):
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type is not None and right_type is not None:
            if left_type == right_type:
                if uctype.constant_type(left_type).binary_ops.__contains__(node.op) is False:
                    if uctype.constant_type(left_type).rel_ops.__contains__(node.op):
                        return "boolean"
                    else:
                        self.error("binary operation not supported" + str(node.coord))
                        return None
            else:
                self.error("type mismatch on binary operation" + str(node.coord))

        return left_type

    def visit_Assignment(self, node):
        # ## 1. Make sure the location of the assignment is defined
        # sym = self.symtab.lookup(node.location)
        # assert sym, "Assigning to unknown sym"
        # ## 2. Check that the types match
        # self.visit(node.value)
        # assert sym.type == node.value.type, "Type mismatch in assignment"
        left_value = self.visit(node.lvalue)
        right_value = self.visit(node.rvalue)
        if left_value is None:
            self.error("{} undeclared".format(node.lvalue.name) + str(node.coord))
            return None
        if right_value is None:
            self.error("{} undeclared".format(node.rvalue.name) + str(node.coord))
            return None
        if left_value != right_value:
            self.error("cannot assign {} to {}".format(right_value, left_value) + str(node.coord))
            return None
        else:
            if uctype.constant_type(left_value).assign_ops.__contains__(node.op):
                return left_value
            else:
                return None

    def visit_ID(self, node):
        type = self.symtab.lookup(node.name)
        if type is not None:
            return type.typename
        else:
            return None

    def visit_NoneType(self, node):
        pass

    def visit_Cast(self, node):
        type = self.visit(node.to_type)
        self.visit(node.expr)
        return type

    def visit_Constant(self, node):
        return node.type

    def visit_Break(self, node):
        pass

    def visit_Assert(self, node):
        type = self.visit(node.expr)
        # if type != None:
        # #     return 'boolean'
        # else:
        #     return None

    def visit_Print(self, node):
        if isinstance(node.expr, ast.ArrayRef):
            name = self.visit(node.expr)
            if name is None:
                self.error("variable {} not declared".format(node.expr.name) + str(node.coord))
                return None
            index = self.visit(node.expr.subscript)
            if index is None:
                self.error("variable {} not declared".format(node.expr.subscript.name) + str(node.coord))
                return None
        pass

    def visit_Read(self, node):
        self.visit(node.expr)

    def visit_If(self, node):
        # self.symtab.begin_scope()
        self.visit(node.cond)
        self.visit(node.iftrue)
        self.visit(node.iffalse)
        # self.symtab.end_scope()

    def visit_FuncDef(self, node):
        self.symtab.begin_scope()
        # type = self.visit(node.spec)
        if node.decl.type.args is not None:
            self.functions[node.decl.name.name] = node.decl.type.args
        self.visit(node.decl)
        if node.decl is not None:
            for _decl in node.decl:
                self.visit(_decl)
            # self.functions[node.decl.name.name] = node.decl.type
        self.visit(node.body)
        func_name = node.decl.name.name

        # else:
        #     print("ENROLA")
        self.symtab.end_scope()

    def visit_While(self, node):
        # self.symtab.begin_scope()
        self.visit(node.cond)
        self.visit(node.stmt)
        # self.symtab.end_scope()

    def visit_Compound(self, node):
        self.symtab.begin_scope()
        for _decl in node.block_items:
            self.visit(_decl)
        self.symtab.end_scope()

    def visit_DeclList(self, node):
        for _decl in node.decls:
            self.visit(_decl)

    def visit_For(self, node):
        self.symtab.begin_scope()
        self.visit(node.init)
        self.visit(node.cond)
        self.visit(node.next)
        self.visit(node.stmt)
        self.symtab.end_scope()

    def visit_EmptyStatement(self, node):
        pass

    def visit_Return(self, node):
        type = self.visit(node.expr)

    def visit_UnaryOp(self, node):
        type = self.visit(node.expr)
        if type is None:
            self.error("variable {} not declared".format(node.expr.name) + str(node.coord))
            return None
        if uctype.constant_type(type).unary_ops.__contains__(node.op) is False:
            self.error("unaryOp {} not supported".format(node.op) + str(node.coord))
            return None
        else:
            return type

    def visit_ExprList(self, node):
        type = []
        for _decl in node.exprs:
            type.append(self.visit(_decl))
        return type

    def visit_FuncCall(self, node):
        func_type = self.visit(node.name)
        args = self.visit(node.args)
        if node.name.name is not None:
            check = self.check_params(self.functions[node.name.name], args)
            if check is False:
                self.error("wrong func call" + str(node.coord))

        return func_type

    def visit_InitList(self, node):
        type = None
        for _decl in node.exprs:
            init_type = self.visit(_decl)
            if type is None:
                type = init_type
            else:
                if type != init_type:
                    # uc.error(node.coord, "teste")
                    self.error("type mismatch on initializer list" + str(node.coord))
                    return None
        return type

    def visit_ParamList(self, node):
        for _decl in node.params:
            self.visit(_decl)

    def visit_FuncDecl(self, node):
        self.visit(node.args)
        type = self.visit(node.type)
        return type

    def visit_ArrayRef(self, node):
        name = self.visit(node.name)
        if name is None:
            self.error("variable {} not declared".format(node.name.name) + str(node.coord))
            return None
        subscript = self.visit(node.subscript)
        if subscript is None:
            self.error("invalid array index" + str(node.coord))
            return name
        elif subscript != 'int':
            self.error("array index must be of type int" + str(node.coord))

        if name == 'float_array' or name == 'float':
            return 'float'
        elif name == 'int_array' or name == 'int':
            return 'int'
        elif name == 'char_array' or name == 'char':
            return 'char'

    def visit_ArrayDecl(self, node):
        type = self.visit(node.type)
        self.visit(node.dim)
        return type