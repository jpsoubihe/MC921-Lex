import sys


class Node(object):
    """
    Base class example for the AST nodes.

    By default, instances of classes have a dictionary for attribute storage.
    This wastes space for objects having very few instance variables.
    The space consumption can become acute when creating large numbers of instances.

    The default can be overridden by defining __slots__ in a class definition.
    The __slots__ declaration takes a sequence of instance variables and reserves
    just enough space in each instance to hold a value for each variable.
    Space is saved because __dict__ is not created for each instance.
    """
    __slots__ = ()

    def children(self):
        """ A sequence of all children that are Nodes. """
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

    # def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False, showcoord=False, _my_node_name=None):
    #     """ Pretty print the Node and all its attributes and children (recursively) to a buffer.
    #         buf:
    #             Open IO buffer into which the Node is printed.
    #         offset:
    #             Initial offset (amount of leading spaces)
    #         attrnames:
    #             True if you want to see the attribute names in name=value pairs. False to only see the values.
    #         nodenames:
    #             True if you want to see the actual node names within their parents.
    #         showcoord:
    #             Do you want the coordinates of each Node to be displayed.
    #     """
    #     lead = ' ' * offset
    #     if nodenames and _my_node_name is not None:
    #         buf.write(lead + self.__class__.__name__ + ' <' + _my_node_name + '>: ')
    #     else:
    #         buf.write(lead + self.__class__.__name__ + ': ')
    #
    #     if self.attr_names:
    #         if attrnames:
    #             nvlist = [(n, getattr(self, n)) for n in self.attr_names if getattr(self, n) is not None]
    #             attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
    #         else:
    #             vlist = [getattr(self, n) for n in self.attr_names]
    #             attrstr = ', '.join('%s' % v for v in vlist)
    #         buf.write(attrstr)
    #
    #     if showcoord:
    #         if self.coord:
    #             buf.write('%s' % self.coord)
    #     buf.write('\n')
    #
    #     for (child_name, child) in self.children():
    #         child.show(buf, offset + 4, attrnames, nodenames, showcoord, child_name)


class GlobalDecl(Node):
    __slots__ = ('decl', 'coord')

    def __init__(self, decl, coord=None):
        self.decl = decl
        self.coord = coord
        print("GlobalDecl")

    def children(self):
        nodelist = []
        if self.decl is not None: nodelist.append(('decl', self.decl))
        return tuple(nodelist)

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
        if self.first is not None: nodelist.append(("type", self.first))
        if self.second is not None: nodelist.append(("declarator", self.second))
        if self.third is not None: nodelist.append(("compound", self.third))
        print(nodelist)
        return tuple(nodelist)


class Type(Node):
    __slots__ = ('names', 'coord')

    def __init__(self, names):
        self.names = names
        self.coord = None
        print("Type")

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('names',)


class ID(Node):
    __slots__ = ('name', 'coord')

    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name', )


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

    attr_names = ()


class Break(Node):
    __slots__ = ('coord')

    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

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


class If(Node):
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
        nodelist.append(('statement', self.statement2))
        return tuple(nodelist)

    attr_names = ()


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

    attr_names = ('value', 'type')


class Cast(Node):
    __slots__ = ('cast', 'coord')

    def __init__(self, cast, coord=None):
        self.cast = cast
        self.coord = coord

    def children(self):
        nodelist = []
        nodelist.append(('cast', self.cast))
        return tuple(nodelist)

    attr_names = ()
