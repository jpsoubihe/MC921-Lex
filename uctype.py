class uCType(object):
    '''
    Class that represents a type in the uC language.  Types
    are declared as singleton instances of this type.
    '''
    def __init__(self, typename, rel_ops=set(), binary_ops=set(), unary_ops=set(), assign_ops=set()):
        '''
        You must implement yourself and figure out what to store.
        '''
        self.typename = typename
        self.unary_ops = unary_ops or set()
        self.binary_ops = binary_ops or set()
        self.rel_ops = rel_ops or set()
        self.assign_ops = assign_ops or set()

    def __str__(self):
        return str(self.typename)

    # Create specific instances of types. You will need to add
    # appropriate arguments depending on your definition of uCType

IntType = uCType("int",
                 unary_ops   = {"-", "+", "--", "++", "p--", "p++", "*", "&"},
                 binary_ops  = {"+", "-", "*", "/", "%"},
                 rel_ops     = {"==", "!=", "<", ">", "<=", ">="},
                 assign_ops  = {"=", "+=", "-=", "*=", "/=", "%="}
                 )

# FloatType = uCType("float",
#                    ...
#     )
# CharType = uCType("char",
#                    ...
#     )
ArrayType = uCType("array",
                   unary_ops   = {"*", "&"},
                   rel_ops     = {"==", "!="}
                   )

VoidType = uCType("void")