
class UndoStack:
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

    def __str__(self):
        for i in self.items:
            print(i)


class SymbolTable(object):
    '''
    Class representing a symbol table.  It should provide functionality
    for adding and looking up nodes associated with identifiers.
    '''
    def __init__(self):
        self.symtab = {}
        self.undo = UndoStack()

    def lookup(self, a):
        return self.symtab.get(a)

    def add(self, a, v):
        if a in self.symtab.keys():
            # print("actual = " + str(self.symtab.get(a)))
            self.undo.push((a, v))
        self.symtab[a] = v
        # print("symtab = " + str(self.symtab.__str__()))
        # print("undo = " + str(self.undo.size()))


    def begin_scope(self):
        return self.undo.size()

    def end_scope(self, scope_len):
        repeated = self.undo.size() - scope_len
        while self.undo.size() > scope_len:
            var = self.undo.pop()
            self.symtab[var[0]] = var[1]
            print("replacing = " + str(self.symtab[var[0]]))

    def __str__(self):
        return str(self.symtab)

