import ast

from SymbolTable import SymbolTable

import uctype


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
            # print(c)
            self.visit(c)

    # def visit_NoneType(self, node):
    #     print("entrou")


error_vector = []


class Visitor(NodeVisitor):

    def print_error(self):
        if len(error_vector) > 0:
            for i in error_vector:
                print(i)

    def error(self, message):
        error_vector.append("Error: " + message)

    '''
    Program visitor class. This class uses the visitor pattern. You need to define methods
    of the form visit_NodeName() for each kind of AST node that you want to process.
    Note: You will need to adjust the names of the AST nodes if you picked different names.
    '''

    def __init__(self):
        # Initialize the symbol table
        self.symtab = SymbolTable()

        # Add built-in type names (int, float, char) to the symbol table
        # self.symtab.add("int", uctype.IntType)
        # self.symtab.add("float",uctype.float_type)
        # self.symtab.add("char",uctype.char_type)

    def visit_Program(self, node):
        # 1. Visit all of the global declarations
        # 2. Record the associated symbol table
        self.symtab.begin_scope()
        for _decl in node.gdecls:
            self.visit(_decl)
        self.symtab.end_scope()

    def visit_GlobalDecl(self, node):
        for _decl in node.decls:
            self.visit(_decl)

    def visit_Decl(self, node):
        type = self.visit(node.type)
        if isinstance(node.type, ast.ArrayDecl):
            if type == 'int':
                self.symtab.add(node.name.name, uctype.IntArrayType)
            elif type == 'float':
                self.symtab.add(node.name.name, uctype.FloatArrayType)
            elif type == 'char':
                self.symtab.add(node.name.name, uctype.CharArrayType)
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
                self.error("invalid type")
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
                self.error("invalid type")

            init = self.visit(node.init)
            if init is not None:
                if init != type:
                    self.error("initializer mismatch")

        # if isinstance(node.type, ast.FuncDecl):
        #     if type != self.symtab.lookup(node.type.type.declname.name):
        #         self.error("wrong func {} type association".format(node.name.name))
        #  elif isinstance(node.type, ast.VarDecl):
        #      type_reg = self.symtab.lookup(node.type.declname.name)
        #      if type != self.symtab.lookup(node.type.declname.name):
        #          self.error("wrong variable type association")
        #  elif isinstance(node.type, ast.ArrayDecl):
        #      type_reg = self.symtab.lookup(node.type.type.declname.name)
        #      if type_reg.typename is not None:
        #          if type_reg == uctype.CharType:
        #              if isinstance(node.init, ast.BinaryOp):
        #                  if node.init.left.type == 'char' is False or node.init.right.type == 'char' is False:
        #                      self.error("error")
        #          elif node.init is not None:
        #              if isinstance(node.init, ast.Constant):
        #                  pass
        #              else:
        #                  for i in node.init.exprs:
        #                      if i.type != type_reg.typename:
        #                          self.error("Error: element on the array is not correct")
        #      else:
        #          self.error("Error. Variable {} not defined".format(node.type.type.declname.name))

    def visit_VarDecl(self, node):
        node1 = self.visit(node.declname)
        node2 = self.visit(node.type)
        if node2 == "int":
            # self.symtab.add(node1.name, uctype.IntType)
            return 'int'
        elif node2 == "char":
            # self.symtab.add(node1.name, uctype.CharType)
            # return uctype.CharType
            return 'char'
        elif node2 == "float":
            # self.symtab.add(node1.name, uctype.FloatType)
            # return uctype.FloatType
            return 'float'
        elif node2 == "void":
            # self.symtab.add(node1.name, uctype.VoidType)
            # return uctype.VoidType
            return 'void'
        else:
            self.error("variable {} has an invalid type : ".format(node1.name))

    def visit_Type(self, node):
        return node.names[0]

    def visit_BinaryOp(self, node):
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        if left_type == right_type:
            if uctype.constant_type(left_type).binary_ops.__contains__(node.op) is False:
                self.error("binary operation not supported")
                return None
        else:
            self.error("type mismatch on binary operation")

        return left_type

    def visit_Assignment(self, node):
        # ToDo: TYPECHECKING
        # ## 1. Make sure the location of the assignment is defined
        # sym = self.symtab.lookup(node.location)
        # assert sym, "Assigning to unknown sym"
        # ## 2. Check that the types match
        # self.visit(node.value)
        # assert sym.type == node.value.type, "Type mismatch in assignment"
        self.visit(node.lvalue)
        self.visit(node.rvalue)

    def visit_ID(self, node):
        type = self.symtab.lookup(node.name)
        if type is not None:
            return type.typename
        else:
            return None

    def visit_NoneType(self, node):
        pass

    def visit_Cast(self, node):
        self.visit(node.new_type)
        self.visit(node.expr)

    def visit_Constant(self, node):
        return node.type

    def visit_Break(self, node):
        pass

    def visit_Assert(self, node):
        self.visit(node.expr)

    def visit_Print(self, node):
        pass

    def visit_Read(self, node):
        self.visit(node.expr)

    def visit_If(self, node):
        self.symtab.begin_scope()
        self.visit(node.cond)
        self.visit(node.iftrue)
        self.visit(node.iffalse)
        self.symtab.end_scope()

    def visit_FuncDef(self, node):
        # type = self.visit(node.spec)
        self.visit(node.decl)
        self.visit(node.body)
        if node.param_decls is not None:
            for _decl in node.param_decls:
                self.visit(_decl)

    def visit_While(self, node):
        self.symtab.begin_scope()
        self.visit(node.cond)
        self.visit(node.statement)
        self.symtab.end_scope()

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
        self.visit(node.initial)
        self.visit(node.cond)
        self.visit(node.next)
        self.visit(node.statement)
        self.symtab.end_scope()

    def visit_EmptyStatement(self, node):
        pass

    def visit_Return(self, node):
        self.visit(node.expr)

    def visit_UnaryOp(self, node):
        self.visit(node.expr)

    def visit_ExprList(self, node):
        for _decl in node.exprs:
            self.visit(_decl)

    def visit_FuncCall(self, node):
        self.visit(node.name)
        self.visit(node.args)

    def visit_InitList(self, node):
        for _decl in node.exprs:
            self.visit(_decl)

    def visit_ParamList(self, node):
        for _decl in node.params:
            self.visit(_decl)

    def visit_FuncDecl(self, node):
        self.visit(node.args)
        type = self.visit(node.type)
        return type

    def visit_ArrayRef(self, node):
        self.visit(node.name)
        self.visit(node.subscript)

    def visit_ArrayDecl(self, node):
        type = self.visit(node.type)
        self.visit(node.dim)
        return type
