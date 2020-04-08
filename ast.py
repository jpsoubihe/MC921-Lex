
class Program():
    __slots__ = ('gdecls', 'coord')

    def __init__(self, gdecls, coord=None):
        self.gdecls = gdecls
        self.coord = coord
        print(gdecls)

    def children(self):
        nodelist = []
        for i, child in enumerate(self.gdecls or []):
            nodelist.append(("gdecls[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class GlobalDecl():
    __slots__ = ('declaration')

    def __init__(self, decl):
        self.declaration = decl
        print("decl")

    def children(self):
        nodelist = []
        if self.declaration is not None: nodelist.append(("declaration", self.declaration))
        return tuple(nodelist)


class BinaryOp():
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


class EmptyStatement():
    __slots__ = 'empty'

    def __init__(self):
        self.empty = None

    def children(self):
        return None


class FuncDef():
    __slots__ = ('first', 'second', 'third')

    def __init__(self, type, declarator, compound):
        self.first = type
        self.second = declarator
        self.third = compound
        print("FuncDef")


    def children(self):
        nodelist = []
        if self.first is not None: nodelist.append(("type", self.first))
        if self.second is not None: nodelist.append(("declarator", self.second))
        if self.third is not None: nodelist.append(("compound", self.third))
        print(nodelist)
        return tuple(nodelist)


class Decl():
    __slots__ = ('name', 'type', 'declarator_list')

    def __init__(self, name, type, declarator_list):
        self.name = name
        self.type = type
        self.declarator_list = declarator_list
        print(name)
