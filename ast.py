
import sys

def _repr(obj):
    """
    Get the representation of an object, with dedicated pprint-like format for lists.
    """
    if isinstance(obj, list):
        return '[' + (',\n '.join((_repr(e).replace('\n', '\n ') for e in obj))) + '\n]'
    else:
        return repr(obj)


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
            self.visit(c)

class Node(object):
    """ Abstract base class for AST nodes.
    """


    def __repr__(self):
        """ Generates a python representation of the current node
        """
        result = self.__class__.__name__ + '('
        indent = ''
        separator = ''
        for name in self.__slots__[:-1]:
            result += separator
            result += indent
            result += name + '=' + (_repr(getattr(self, name)).replace('\n', '\n  ' + (' ' * (len(name) + len(self.__class__.__name__)))))
            separator = ','
            indent = ' ' * len(self.__class__.__name__)
        result += indent + ')'
        return result

    def children(self):
        """ A sequence of all children that are Nodes
        """
        pass

    def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False, showcoord=False, _my_node_name=None):
        """ Pretty print the Node and all its attributes and children (recursively) to a buffer.
            buf:
                Open IO buffer into which the Node is printed.
            offset:
                Initial offset (amount of leading spaces)
            attrnames:
                True if you want to see the attribute names in name=value pairs. False to only see the values.
            nodenames:
                True if you want to see the actual node names within their parents.
            showcoord:
                Do you want the coordinates of each Node to be displayed.
        """
        lead = ' ' * offset
        if nodenames and _my_node_name is not None:
            buf.write(lead + self.__class__.__name__ + ' <' + _my_node_name + '>: ')
        else:
            buf.write(lead + self.__class__.__name__ + ': ')

        if self.attr_names:
            if attrnames:
                nvlist = [(n, getattr(self, n)) for n in self.attr_names if getattr(self, n) is not None]
                attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ', '.join('%s' % v for v in vlist)
            buf.write(attrstr)

        if showcoord:
            if self.coord:
                buf.write('%s' % self.coord)
        buf.write('\n')
        for (child_name, child) in self.children():
            child.show(buf, offset + 4, attrnames, nodenames, showcoord, child_name)


class Coord(object):
    """ Coordinates of a syntactic element. Consists of:
            - Line number
            - (optional) column number, for the Lexer
    """
    __slots__ = ('line', 'column')

    def __init__(self, line, column=None):
        self.line = line
        self.column = column

    def __str__(self):
        if self.line:
            coord_str = "   @ %s:%s" % (self.line, self.column)
        else:
            coord_str = ""
        return coord_str


class Program(Node):
    __slots__ = ('gdecls', 'coord')

    def __init__(self, gdecls, coord=None):
        self.gdecls = gdecls
        self.coord = coord
        print("Program")

    def children(self):
        nodelist = []
        for i, child in enumerate(self.gdecls or []):
            nodelist.append(("gdecls[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in (self.gdecls or []):
            yield child

    attr_names = ()


class GlobalDecl(Node):
    __slots__ = ('decl', 'coord')

    def __init__(self, decl, coord=None):
        self.decl = decl
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.decl or []):
            nodelist.append(("decl[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in (self.decls or []):
            yield child

    attr_names = ()


class BinaryOp(Node):
    __slots__ = ('op', 'lvalue', 'rvalue', 'coord')

    def __init__(self, op, left, right, coord=None):
        self.op = op
        self.lvalue = left
        self.rvalue = right
        self.coord = coord
        # print(right)

    def children(self):
        nodelist = []
        if self.lvalue is not None: nodelist.append(("lvalue", self.lvalue))
        if self.rvalue is not None: nodelist.append(("rvalue", self.rvalue))
        # print(nodelist)
        return tuple(nodelist)

    attr_names = ('op',)


class EmptyStatement(Node):
    __slots__ = 'coord'

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return

    attr_names = ()


class FuncDef(Node):
    __slots__ = ('first', 'second', 'third', 'coord')

    def __init__(self, type, declarator, compound, coord=None):
        self.first = type
        self.second = declarator
        self.third = compound
        self.coord = None
        print("FuncDef")

    def children(self):
        nodelist = []
        if self.first is not None: nodelist.append(("first", self.first))
        if self.second is not None: nodelist.append(("declarator", self.second))
        if self.third is not None: nodelist.append(("compound", self.third))
        print(nodelist)
        return tuple(nodelist)

    def __iter__(self):
        if self.first is not None:
            yield self.first
        if self.second is not None:
            yield self.second
        if self.third is not None:
            yield self.third


class FuncDecl(Node):
    __slots__ = ('args', 'type', 'coord')
    def __init__(self, args, type, coord=None):
        self.args = args
        self.type = type
        self.coord = coord

    def children(self):
        nodelist = []
        if self.args is not None: nodelist.append(("args", self.args))
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ()

class If(Node):
    __slots__ = ('expression', 'if_statement', 'else_statement', 'coord')

    def __init__(self, expression, if_statement, else_statement=None, coord=None):
        self.expression = expression
        self.if_statement = if_statement
        self.else_statement = else_statement
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expression is not None:
            nodelist.append(('expression', self.expression))
        if self.if_statement is not None:
            nodelist.append(('if_statement', self.if_statement))
        if self.else_statement is not None:
            nodelist.append(('else_statement', self.else_statement))

    def __iter__(self):
        if self.expression is not None:
            yield self.expression
        if self.if_statement is not None:
            yield self.if_statement
        if self.else_statement is not None:
            yield self.else_statement


class Type(Node):
    __slots__ = ('names', 'coord')

    def __init__(self, names, coord):
        self.names = names
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return
        yield

    attr_names = ('names', )


class ID(Node):
    __slots__ = ('name', 'coord')

    def __init__(self, name,  coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return

    attr_names = ('name',)


class Compound(Node):
    __slots__ = ('declaration_list', 'statement_list', 'coord')

    def __init__(self, declaration_list, statement_list, coord=None):
        self.declaration_list = declaration_list
        self.statement_list = statement_list
        self.coord = coord

    def children(self):
        nodelist = []
        if self.declaration_list is not None: nodelist.append(('declaration', self.declaration_list))
        if self.declaration_list is not None: nodelist.append(('declaration', self.statement_list))
        return tuple(nodelist)

    attr_names = ()



class Read(Node):
    __slots__ = ('argument_expression', 'coord')

    def __init__(self, argument_expression, coord=None):
        self.argument_expression = argument_expression
        self.coord = coord

    def children(self):
        nodelist = [('argument_expression', self.argument_expression)]
        return tuple(nodelist)

    attr_names = ()


class Print(Node):
    __slots__ = ('expression', 'coord')

    def __init__(self, expression, coord=None):
        self.expression = expression
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expression is not None: nodelist.append(('expression', self.expression))
        return tuple(nodelist)

    attr_names = ()


class Assert(Node):
    __slots__ = ('expression', 'coord')

    def __init__(self, expression, coord=None):
        self.expression = expression
        self.coord = coord

    def children(self):
        nodelist = [('expression', self.expression)]
        return tuple(nodelist)

    def __iter__(self):
        if self.expression is not None: yield self.expression

    attr_names = ()


class Return(Node):
    __slots__ = ('expression', 'coord')

    def __init__(self, expression, coord=None):
        self.expression = expression
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expression is not None: nodelist.append(('expression', self.expression))
        return tuple(nodelist)

    def __iter__(self):
        if self.expression is not None:
            yield self.expression

    attr_names = ()


class Break(Node):
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return

    attr_names = ()


class For(Node):
    __slots__ = ('first', 'second', 'third', 'fourth', 'fifth', 'coord')

    def __init__(self, first, second, third, fourth, fifth, coord=None):
        self.first = first
        self.second = second
        self.third = third
        self.fourth = fourth
        self.fifth = fifth
        self.coord = coord

    def children(self):
        nodelist = []
        if self.first is not None: nodelist.append(('first', self.first))
        if self.second is not None: nodelist.append(('second', self.second))
        if self.third is not None: nodelist.append(('third', self.third))
        if self.fourth is not None: nodelist.append(('fourth', self.fourth))
        if self.fifth is not None: nodelist.append(('fifth', self.fifth))
        return tuple(nodelist)

    def children(self):
        nodelist = []
        for i, child in enumerate(self.first or self.second or self.third or self.fourth or self.fifth or []):
            nodelist.append(("name[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        return
        yield

    attr_names = ()


class While(Node):
    __slots__ = ('expression', 'statement', 'coord')

    def __init__(self, expression, statement, coord=None):
        self.expression = expression
        self.statement = statement
        self.coord = coord

    def children(self):
        nodelist = []
        nodelist.append(('expression', self.expression))
        nodelist.append(('statement', self.statement))
        return tuple(nodelist)

    attr_names = ()


class IF(Node):
    __slots__ = ('expression', 'statement1', 'statement2', 'coord')

    def __init__(self, expression, statement1, statement2, coord=None):
        self.expression = expression
        self.statement1 = statement1
        self.statement2 = statement2
        self.coord = coord

    def children(self):
        nodelist = []
        nodelist.append(('expression', self.expression))
        nodelist.append(('statement1', self.statement1))
#         nodelist.append(('statement', self.statement2))
#         return tuple(nodelist)
#
#     attr_names = ()


class Assignment(Node):
    __slots__ = ('expression', 'op', 'assignment', 'coord')

    def __init__(self, expression, op, assignment, coord=None):
        self.expression = expression
        self.op = op
        self.assignment = assignment
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expression is not None: nodelist.append(('expression', self.expression))
        if self.assignment is not None: nodelist.append(('assignment', self.assignment))
        return tuple(nodelist)

    def __iter__(self):
        if self.expression is not None: yield self.expression
        if self.assignment is not None: yield self.assignment

    attr_names = ('op', )


class ParamList(Node):
    __slots__ = ('first', 'second', 'coord')

    def __init__(self, first, second, coord=None):
        self.first = first
        self.second = second
        self.coord = coord

    def children(self):
        nodelist = []
        nodelist.append(('first', self.first))
        if self.second is not None: nodelist.append(('second', self.second))
        return tuple(nodelist)

    attr_names = ('op', )


class InitList(Node):
    __slots__ = ('first', 'second', 'coord')

    def __init__(self, first, second, coord=None):
        self.first = first
        self.second = second
        self.coord = coord

    def children(self):
        nodelist = []
        nodelist.append(('first', self.first))
        if self.second is not None: nodelist.append(('second', self.second))
        return tuple(nodelist)

    attr_names = ()


# attribute type implementation is a good question
class Constant(Node):
    __slots__ = ('type', 'value', 'coord')

    def __init__(self, type, value, coord=None):
        self.type = type
        self.value = value
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    # def __iter__(self):
    #     if self.type is not None: yield self.type
    #     if self.value is not None: yield self.value

    attr_names = ('type', 'value')


class Cast(Node):
    __slots__ = ('cast', 'coord')

    def __init__(self, cast, coord=None):
        self.cast = cast
        self.coord = coord

    def children(self):
        nodelist = []
        nodelist.append(('cast', self.cast))
        return tuple(nodelist)

    def __iter__(self):
        if self.cast is not None: yield self.cast

    attr_names = ()


class Decl(Node):
    __slots__ = ('name', 'type', 'initializer', 'coord')

    def __init__(self, name, type, initializer, coord=None):
        self.name = name
        self.type = type
        self.initializer = initializer
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(('type', self.type))
        if self.initializer is not None: nodelist.append(('initializer', self.initializer))
        return tuple(nodelist)

    def __iter__(self):
        if self.type is not None:
            yield self.type
        if self.initializer is not None:
            yield self.initializer

    attr_names = ('name', )

class VarDecl(Node):
    __slots__ = ('declname', 'type', 'coord')

    def __init__(self, declname, type, coord=None):
        self.declname = declname
        self.type = type
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    # def __iter__(self):
    #     if self.type is not None:
    #         yield self.type

    attr_names = ()


class FuncCall(Node):
    __slots__ = ('name', 'args', 'coord')

    def __init__(self,  name, args, coord=None):
        self.name = name
        self.args = args
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(('name', self.name))
        if self.args is not None: nodelist.append(('args', self.args))
        return tuple(nodelist)

    def __iter__(self):
        if self.name is not None:
            yield self.name
        if self.args is not None:
            yield self.args

    attr_names = ()


class ArrayDecl(Node):
    __slots__ = ('type', 'num', 'coord')

    def __init__(self,  type, num, coord=None):
        self.type = type
        self.num = num
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(('type', self.type))
        if self.num is not None: nodelist.append(('num', self.num))
        return tuple(nodelist)

    def __iter__(self):
        if self.type is not None:
            yield self.type
        if self.num is not None:
            yield self.num

    attr_names = ()


class ArrayRef(Node):
    __slots__ = ('name', 'coord')

    def __init__(self,  name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(('name', self.name))
        return tuple(nodelist)

    def __iter__(self):
        if self.name is not None:
            yield self.name

    attr_names = ()


class ExprList(Node):
    __slots__ = ('expression', 'coord')

    def __init__(self,  expression, coord=None):
        self.expression = expression
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expression is not None: nodelist.append(('expression', self.expression))
        return tuple(nodelist)

    def __iter__(self):
        if self.expression is not None:
            yield self.expression

    attr_names = ()

class DeclList(Node):
    __slots__ = ('decls', 'coord')

    def __init__(self, decls, coord=None):
        self.decls = decls
        self.coord = coord

    def children(self):
        nodelist = []
        if self.decls is not None: nodelist.append(('decls', self.decls))
        return tuple(nodelist)

    def __iter__(self):
        if self.decls is not None:
            yield self.decls

    attr_names = ()

