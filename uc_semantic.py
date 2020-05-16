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

    def extract_func_type(self, node):
        if isinstance(node, ast.FuncDecl):
            return node.type.type.names[0]

    def extract_types(self, param_list):
        type = []
        for p in param_list.params:
            type.append(self.symtab.lookup(p.name.name).typename)
        return type

    def check_params(self, params_reg, params_actual):
        to_type = self.extract_types(params_reg)
        return to_type == params_actual

    def search_return(self, body):
        for i in body.block_items:
            # if isinstance(i, ast.If):

            # if isinstance(i, ast.If):

            if isinstance(i, ast.Return):
                return self.visit(i.expr)

    '''
    Program visitor class. This class uses the visitor pattern. You need to define methods
    of the form visit_NodeName() for each kind of AST node that you want to process.
    Note: You will need to adjust the names of the AST nodes if you picked different names.
    '''

    def __init__(self):
        # Initialize the symbol table
        self.symtab = SymbolTable()
        self.functions = {}
        self.function_type = {}
        self.error_vector = []

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
            init = self.visit(node.init)
            if init is not None:
                if init != type:
                    assert init == 'string' and type == 'char', "initializer mismatch {} {}{}".format(type, init, str(node.coord))

        elif isinstance(node.type, ast.FuncDecl):
            init = self.visit(node.init)
            if init is not None:
                assert init == type, "initializer mismatch" + str(node.coord)

        return type

    def visit_VarDecl(self, node):
        type = node.type.names[0]

        if type == uctype.IntType.typename:
            self.symtab.add(node.declname.name, uctype.IntType)
        elif type == uctype.FloatType.typename:
            self.symtab.add(node.declname.name, uctype.FloatType)
        elif type == uctype.CharType.typename:
            self.symtab.add(node.declname.name, uctype.CharType)
        elif type == uctype.VoidType.typename:
            self.symtab.add(node.declname.name, uctype.VoidType)
        else:
            assert False, "invalid type" + str(node.coord)

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
            assert False, "variable {} has an invalid type : ".format(node1.name) + str(node.coord)

    def visit_Type(self, node):
        return node.names[0]

    def visit_BinaryOp(self, node):
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        assert left_type is not None,  "{} undeclared".format(node.left.name) + str(node.coord)
        assert right_type is not None, "{} undeclared".format(node.right.name) + str(node.coord)
        assert left_type == right_type, "type mismatch on binary operation" + str(node.coord)

        assert uctype.constant_type(left_type).binary_ops.__contains__(node.op) or \
               uctype.constant_type(left_type).rel_ops.__contains__(node.op), "binary operation not supported" + str(node.coord)

        if uctype.constant_type(left_type). rel_ops.__contains__(node.op):
            return "boolean"

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
        assert left_value != None, "{} undeclared".format(node.lvalue.name) + str(node.coord)
        assert right_value != None, "{} undeclared".format(node.rvalue.name) + str(node.coord)
        assert left_value == right_value, "cannot assign {} to {}".format(right_value, left_value) + str(node.coord)
        assert uctype.constant_type(left_value).assign_ops.__contains__(node.op),\
            "assignment operation not supported for variables {}".format(left_value) + str(node.coord)
        return left_value

    def visit_ID(self, node):
        type = self.symtab.lookup(node.name)
        if type is not None:
            return type.typename
        else:
            return None

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

    def visit_Print(self, node):
        if isinstance(node.expr, ast.ArrayRef):
            name = self.visit(node.expr)
            assert name is not  None,  "variable {} not declared".format(node.expr.name) + str(node.coord)
            index = self.visit(node.expr.subscript)
            assert index is not None, "variable {} not declared".format(node.expr.subscript.name) + str(node.coord)
        elif isinstance(node.expr, ast.ID):
            name = self.visit(node.expr)
            assert name is not None, "variable {} not declared".format(node.expr.name) + str(node.coord)


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
            # self.function_type[node.decl.name.name] = self.extract_func_type(node.decl.type)
        self.visit(node.body)
        # func_type = self.symtab.lookup(node.decl.name.name)
        # if func_type != uctype.VoidType:
        #     assert func_type.typename == self.search_return(node.body), "wrong return type on function {}".format(node.decl.name.name)
        self.symtab.end_scope()

    def visit_NoneType(self, node):
        pass

    def visit_While(self, node):
        self.visit(node.cond)
        self.visit(node.stmt)

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
        print()

    def visit_UnaryOp(self, node):
        type = self.visit(node.expr)

        assert type is not None, "variable {} not declared".format(node.expr.name) + str(node.coord)
        assert uctype.constant_type(type).unary_ops.__contains__(node.op) is True, "unaryOp {} not supported".format(node.op) + str(node.coord)

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
            assert check is True, "wrong call to function {}".format(node.name.name) + str(node.coord)

        return func_type

    def visit_InitList(self, node):
        type = None
        for _decl in node.exprs:
            init_type = self.visit(_decl)
            if type is None:
                type = init_type
            else:
                assert type == init_type, "type mismatch on initializer list" + str(node.coord)
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
        assert name is not None, "variable {} not declared".format(node.name.name) + str(node.coord)
        subscript = self.visit(node.subscript)
        assert subscript is not None, "invalid array index" + str(node.coord)
        assert subscript == uctype.IntType.typename, "array index must be of type int" + str(node.coord)

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