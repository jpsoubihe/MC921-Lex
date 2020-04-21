import ast
import sys

from ply.yacc import yacc
from Lexer import  UCLexer
from ast import *

def print_error(msg, x, y):
    print("Lexical error: %s at %d:%d" % (msg, x, y))

class UCParser():

    tokens = UCLexer.tokens

    def __init__(self):
        self.lexer = UCLexer(print_error)
        self.lexer.build()
        self.parser = yacc(module=self)
        self.debug = False

    def _type_modify_decl(self, decl, modifier):
        if self.debug:
            print("Inside _type_modify_decl:")
            print(decl)
            print('End')

        modifier_head = modifier
        modifier_tail = modifier

        while modifier_tail.type:
            modifier_tail = modifier_tail.type

        if isinstance(decl, VarDecl):
            modifier_tail.type = decl
            return modifier
        else:
            decl_tail = decl

            while not isinstance(decl_tail.type, VarDecl):
                decl_tail = decl_tail.type

            modifier_tail.type = decl_tail.type
            decl_tail.type = modifier_head
            return decl

    def p_error(self, p):
        if p:
            print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")

    def _build_function_definition(self, spec, decl, param_decls, body):
        if self.debug:
            print("Inside _build_function_definition:")
            print(spec)
            print(decl)
            print(param_decls)
            print(body)
            print('End')

        declaration = self._build_declarations(spec=spec, decls=dict(decl=decl, init=None))

        return FuncDef(spec=spec, decl=declaration, param_decls=param_decls, body=body, coord=decl.coord)

    def _fix_decl_name_type(self, decl, typename):
        """ Fixes a declaration. Modifies decl.
        """
        # Reach the underlying basic type
        type = decl
        while not isinstance(type, VarDecl):
            type = type.type

        decl.name = type.declname

        # The typename is a list of types. If any type in this
        # list isn't an Type, it must be the only
        # type in the list.
        # If all the types are basic, they're collected in the
        # Type holder.
        for tn in typename:
            if not isinstance(tn, Type):
                if len(typename) > 1:
                    self._parse_error(
                        "Invalid multiple types specified", tn.coord)
                else:
                    type.type = tn
                    return decl

        if not typename:
            pass
            # # Functions default to returning int
            # if not isinstance(decl.type, ast_classes.FuncDecl):
            #     self._parse_error("Missing type in declaration", decl.coord)
            # type.type = ast_classes.Type(['int'], coord=decl.coord)
        else:
            # At this point, we know that typename is a list of Type
            # nodes. Concatenate all the names into a single list.
            type.type = Type(
                [typename.names[0]],
                coord=typename.coord)
        return decl

    def _build_declarations(self, spec, decls):
        if self.debug:
            print("Inside _build_declarations:")
            for decl in decls:
                print(decl)
            print(spec)
            print('End')

        declarations = []

        for decl in decls:
            if self.debug:
                print(decl)
            assert decl[0] is not None
            declaration = Decl(name=None, type=decl['decl'], init=decl.get('init'), coord=decl.get('coord'))

            if isinstance(declaration.type, Type):
                fixed_decl = declaration
            else:
                fixed_decl = self._fix_decl_name_type(declaration, spec)

            declarations.append(fixed_decl)

        return declarations

    def parse(self, code, param1, param2):
        return self.parser.parse(code, param1, True)

    def p_program(self, p):
        ''' program : global_declaration_list_opt
        '''
        print("accept")
        p[0] = Program(p[1])

    def p_global_declaration_list_opt(self, p):
        ''' global_declaration_list_opt : global_declaration global_declaration_list_opt
                                        | global_declaration
        '''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_global_declaration1(self, p):
        ''' global_declaration : function_definition '''
        p[0] = GlobalDecl(p[1])

    def p_global_declaration2(self, p):
        ''' global_declaration : declaration '''
        print("declaration")
        p[0] = GlobalDecl(p[1])

    def p_declaration(self, p):
        ''' declaration : declaration_body SEMI'''
        p[0] = p[1]
        print("declaration")

    def p_declaration_body(self, p):
        ''' declaration_body : type_specifier init_declarator_list_opt'''
        # p[0] = self._build_declarations(p[1], p[2])
        # p[0] = Decl(p[2], VarDecl(p[1], p[2]), None)
        spec = p[1]
        decls = None
        if p[2] is not None:
            decls = self._build_declarations(spec=spec, decls=p[2])
        p[0] = decls
        print("declaration")

    def p_init_declarator_list_opt(self, p):
        ''' init_declarator_list_opt : init_declarator_list
                                        | empty
        '''
        p[0] = p[1]

    def p_init_declarator_list1(self, p):
        ''' init_declarator_list : init_declarator '''
        p[0] = p[1]

    def p_init_declarator(self, p):
        ''' init_declarator : direct_declarator
                            | direct_declarator EQUALS initializer
        '''
        if len(p) == 2:
            p[0] = dict(decl=p[1], init=None)
        else:
            p[0] = dict(decl=p[1], init=p[3])

    def p_direct_declarator1(self, p):
        ''' direct_declarator : identifier
                                | LPAREN direct_declarator RPAREN
        '''
        if len(p) <= 2:
            p[0] = VarDecl(p[1], type=None, coord=None)
        else:
            p[0] = p[2]

    def p_identifier(self, p):
        ''' identifier : ID'''
        p[0] = ID(p[1], coord=None)

    def p_type_specifier(self, p):
        ''' type_specifier : VOID
                            | CHAR
                            | INT
                            | FLOAT
        '''
        p[0] = Type([p[1]], coord=None)

    #         -----------------------------------------------------------

    def p_function_definition1(self, p):
        ''' function_definition : type_specifier direct_declarator compound_statement '''
        p[0] = FuncDef(p[0], p[1], p[2])

    def p_function_definition2(self, p):
        ''' function_definition : direct_declarator declaration_list_opt  compound_statement'''
        # p[0] = p[1] + [p[2]] + p[3]
        p[0] = FuncDef(p[0], [p[1]], p[2])

    def p_declaration_list_opt(self, p):
        ''' declaration_list_opt : declaration declaration_list_opt
                                    | empty
        '''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) > 2:
            p[0] = p[1] + p[2]
        else:
            p[0] = EmptyStatement(p[1])

    def p_direct_declarator2(self, p):
        ''' direct_declarator : direct_declarator LBRACKET constant_expression_opt RBRACKET'''
        p[0] = (p[1], p[3])

    def p_direct_declarator3(self, p):
        ''' direct_declarator : direct_declarator LPAREN parameter_list RPAREN'''
        # ToDo: to be completed
        # p[0] = Func


    def p_direct_declarator4(self, p):
        ''' direct_declarator : direct_declarator LPAREN identifier_list_opt RPAREN'''



    def p_constant_expression_opt(self, p):
        ''' constant_expression_opt : constant_expression
                                    | empty
        '''

    def p_identifier_list_opt(self, p):
        ''' identifier_list_opt : ID identifier_list_opt
                                | empty
        '''

    def p_constant_expression(self, p):
        ''' constant_expression : binary_expression'''
        p[0] = p[1]

    def p_binary_expression(self, p):
        ''' binary_expression : cast_expression
                                | binary_expression TIMES binary_expression
                                | binary_expression DIVIDE binary_expression
                                | binary_expression MOD binary_expression
                                | binary_expression PLUS binary_expression
                                | binary_expression MINUS binary_expression
                                | binary_expression LT binary_expression
                                | binary_expression EQUALS binary_expression
                                | binary_expression EQ binary_expression
                                | binary_expression LE binary_expression
                                | binary_expression HT binary_expression
                                | binary_expression HE binary_expression
                                | binary_expression DIFF binary_expression
                                | binary_expression AND binary_expression
                                | binary_expression OR binary_expression
        '''
        if len(p) == 2:
            p[0] = Cast(p[1])
        else:
            p[0] = BinaryOp(p[2], p[1], p[3])

    def p_cast_expression(self, p):
        '''cast_expression : unary_expression
                            | LPAREN type_specifier RPAREN cast_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2] + p[4]

    def p_unary_expression1(self, p):
        ''' unary_expression : postfix_expression
                                | PLUSPLUS unary_expression
                                | MINUSMINUS unary_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]

    def p_unary_expression2(self, p):
        ''' unary_expression : unary_operator cast_expression '''
        p[0] = p[1] + Cast(p[2])

    def p_postfix_expression1(self, p):
        ''' postfix_expression : primary_expression '''
        p[0] = p[1]

    def p_postfix_expression2(self, p):
        ''' postfix_expression : postfix_expression LBRACKET expression RBRACKET '''
        p[0] = p[1] + p[3]

    def p_postfix_expression3(self, p):
        ''' postfix_expression : postfix_expression LPAREN argument_expression_opt RPAREN '''
        p[0] = p[1] + p[3]

    def p_postfix_expression4(self, p):
        ''' postfix_expression : postfix_expression PLUSPLUS
                                | postfix_expression MINUSMINUS
        '''
        p[0] = p[1]

    def p_argument_expression_opt1(self, p):
        ''' argument_expression_opt : argument_expression '''
        p[0] = p[1]

    def p_argument_expression_opt2(self, p):
        ''' argument_expression_opt : empty '''
        p[0] = p[1]

    def p_primary_expression1(self, p):
        ''' primary_expression : ID '''
        p[0] = ID(p[1])

    def p_primary_expression2(self, p):
        ''' primary_expression : constant '''
        p[0] = p[1]

    def p_primary_expression3(self, p):
        ''' primary_expression : STRING '''
        #ToDo: what to do with STRING ?

    def p_primary_expression4(self, p):
        ''' primary_expression : LPAREN expression RPAREN '''
        p[0] = p[2]


    def p_constant1(self, p):
        ''' constant : INT_CONST '''
        p[0] = Constant('int', p[1])

    def p_constant2(self, p):
        ''' constant : FLOAT_CONST '''
        p[0] = Constant('float', p[1])

    def p_constant3(self, p):
        ''' constant : CHAR_CONST '''
        p[0] = Constant('char', p[1])

    def p_expression(self, p):
        ''' expression : assignment_expression
                        | expression COMMA assignment_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[3]

    def p_argument_expression(self, p):
        ''' argument_expression : assignment_expression
                                | argument_expression COMMA assignment_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[3]


    def p_assignment_expression(self, p):
        ''' assignment_expression : binary_expression
                                    | unary_expression assignment_operator assignment_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[2] + p[3]

    def p_assignment_operator(self, p):
        '''assignment_operator :  TIMESASSIGN
                                | DIVIDEASSIGN
                                | MODASSIGN
                                | PLUSASSIGN
                                | MINUSASSIGN
        '''
        p[0] = p[1]

    def p_unary_operator(self, p):
        ''' unary_operator : ADDRESS
                            | TIMES
                            | PLUS
                            | MINUS
                            | UNARYDIFF
        '''
        p[0] = p[1]

    def p_parameter_list(self, p):
        ''' parameter_list : parameter_declaration
                            | parameter_list COMMA parameter_declaration
        '''
        if len(p) == 2:
            p[0] = ParamList(p[1])
        else:
            p[0] = ParamList(p[1], p[3])

    def p_parameter_declaration(self, p):
        ''' parameter_declaration : type_specifier direct_declarator '''
        p[0] = p[1] + p[2]

    def p_init_declarator_list2(self, p):
        ''' init_declarator_list : init_declarator_list COMMA init_declarator '''
        p[0] = p[1] + p[3]



    def p_initializer1(self, p):
        ''' initializer : assignment_expression '''
        p[0] = p[1]

    def p_initializer2(self, p):
        ''' initializer : LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        '''
        p[0] = p[2]

    def p_initializer_list1(self, p):
        ''' initializer_list : initializer '''
        p[0] = InitList(p[1])

    def p_initializer_list2(self, p):
        ''' initializer_list : initializer_list COMMA initializer '''
        p[0] = InitList(p[1], p[3])

    def p_compound_statement(self, p):
        ''' compound_statement : LBRACE declaration_list_opt statement_list_opt RBRACE '''
        p[0] = Compound(p[2], p[3])

    def p_statement_list_opt(self, p):
        ''' statement_list_opt : statement statement_list_opt
                                | empty
        '''
        if len(p) > 2:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_statement(self, p):
        ''' statement : expression_statement
                        | compound_statement
                        | selection_statement
                        | iteration_statement
                        | jump_statement
                        | assert_statement
                        | print_statement
                        | read_statement
        '''
        p[0] = p[1]

    def p_expression_statement(self, p):
        ''' expression_statement : expression_opt SEMI'''
        p[0] = p[1]

    def p_expression_opt1(self, p):
        ''' expression_opt : expression '''
        p[0] = p[1]

    def p_expression_opt2(self, p):
        ''' expression_opt : empty '''
        p[0] = p[1]

    def p_selection_statement(self, p):
        ''' selection_statement : IF LPAREN expression RPAREN statement
                                | IF LPAREN expression RPAREN statement ELSE statement
        '''
        if len(p) == 6:
            p[0] = If(p[3], p[5])
        else:
            p[0] = If(p[3], p[5], p[7])

    def p_iteration_statement1(self, p):
        ''' iteration_statement : WHILE LPAREN expression RPAREN statement '''
        p[0] = While(p[3], p[5])

    def p_iteration_statement2(self, p):
        ''' iteration_statement : FOR LPAREN init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement '''
        p[0] = For(p[3], p[5], p[7], p[8])

    def p_iteration_statement3(self, p):
        ''' iteration_statement : FOR LPAREN type_specifier init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement '''
        p[0] = For(p[3], p[4], p[6], p[8], p[9])

    def p_jump_statement1(self, p):
        ''' jump_statement : BREAK SEMI '''
        p[0] = Break()

    def p_jump_statement2(self, p):
        ''' jump_statement : RETURN SEMI
                            | RETURN expression SEMI
        '''
        if len(p) <= 3:
            Return()
        else:
            Return(p[2])

    def p_assert_statement(self, p):
        ''' assert_statement : ASSERT expression SEMI '''
        p[0] = Assert(p[2])

    def p_print_statement(self, p):
        ''' print_statement : PRINT LPAREN expression_opt RPAREN SEMI'''
        p[0] = Print(p[3])

    def p_read_statement(self, p):
        ''' read_statement : READ LPAREN argument_expression RPAREN SEMI'''
        p[0] = Read(p[3])

    def p_empty(self, p):
        '''empty :'''
        p[0] = EmptyStatement()

    def p_error(self, p):
        if p:
            print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")

    precedence = (
        ('left', 'OR'),
        ('left', 'AND', 'EQUALS'),
        ('left', 'EQ', 'DIFF'),
        ('left', 'HT', 'HE', 'LT', 'LE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD')
    )




