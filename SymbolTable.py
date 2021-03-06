
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
        self.scope_ind = 0

    def lookup(self, a):
        return self.symtab.get(a)

    def check_scope(self, key):
        for a in self.undo.items:
            if a[0] == key:
                return False
            if a == '*':
                return True
        return True

    def add(self, k, v):
        if k in self.symtab.keys():
            # if self.symtab.
            # print("actual = " + a + " -> " +str(self.symtab.get(a)))
            # flag = self.check_scope(k)
            # if flag is False:
            #     return flag
            self.undo.push((k, self.symtab.get(k)))
        self.symtab[k] = v
        self.undo.push((k, self.symtab.get(k)))
        print("\nADD:")
        for a in self.symtab.keys():
            print(a + " -> " + str(self.symtab[a]), end=" | ")
        print()
        return True
        # print()
        # print("UNDO:")
        # for b in self.undo.items:
        #     if b is '*':
        #         print(b, end=" | ")
        #     else:
        #         print(b[0] + " -> " + str(b[1]), end=" | ")
        # print()
        # print("symtab = " + str(self.symtab.__str__()))
        # print("undo = " + str(self.undo.size()))


    def begin_scope(self):
        scope_ind = self.symtab.__sizeof__()
        self.undo.push('*')
        return self.undo.size()

    def end_scope(self):
        if self.undo.isEmpty() is False:
            # var = self.undo.pop()
            while self.undo.isEmpty() is False:
                var = self.undo.pop()
                if var == '*':
                    break
                self.symtab[var[0]] = var[1]
                # print("replacing with " + str(var[0]) + " -> " + str(self.symtab[var[0]]))
        for a in self.symtab.keys():
            print(a + " -> " + str(self.symtab[a]), end=" | ")
        print()
        # print(self.symtab)

    def __str__(self):
        return str(self.symtab)

