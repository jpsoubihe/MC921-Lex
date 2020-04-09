import sys

from ply.yacc import yacc
from Lexer import tokens
from ast import *


class UCParser():

    def parse(self, code, bosta, debug):

        def p_program(p):
            ''' program : global_declaration_list_opt
            '''
            print("accept")
            p[0] = Program(p[1])

        def p_global_declaration_list_opt(p):
            ''' global_declaration_list_opt : global_declaration global_declaration_list_opt
                                            | global_declaration
            '''
            p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

        def p_global_declaration1(p):
            ''' global_declaration : function_definition '''
            p[0] = GlobalDecl(p[1])

        def p_global_declaration2(p):
            ''' global_declaration : declaration '''
            print("declaration")
            p[0] = GlobalDecl(p[1])

        def p_function_definition1(p):
            ''' function_definition : type_specifier direct_declarator compound_statement '''
            p[0] = FuncDef(p[0], p[1], p[2])

        def p_function_definition2(p):
            ''' function_definition : direct_declarator declaration_list_opt  compound_statement'''
            # p[0] = p[1] + [p[2]] + p[3]
            p[0] = FuncDef(p[0], [p[1]], p[2])

        def p_declaration_list_opt(p):
            ''' declaration_list_opt : declaration declaration_list_opt
                                     | empty
            '''
            if len(p) == 2:
                p[0] = p[1]
            elif len(p) > 2:
                p[0] = p[1] + p[2]
            else:
                p[0] = EmptyStatement(p[1])


        def p_direct_declarator1(p):
            ''' direct_declarator : ID
                                  | LPAREN direct_declarator RPAREN
            '''
            if len(p) <= 2:
                p[0] = ID(p[1])
            else:
                p[0] = p[2]

        def p_direct_declarator2(p):
            ''' direct_declarator : direct_declarator LBRACKET constant_expression_opt RBRACKET'''
            p[0] = (p[1], p[3])

        def p_direct_declarator3(p):
            ''' direct_declarator : direct_declarator LPAREN parameter_list RPAREN'''
            # ToDo: to be completed
            # p[0] = Func


        def p_direct_declarator4(p):
            ''' direct_declarator : direct_declarator LPAREN identifier_list_opt RPAREN'''



        def p_constant_expression_opt(p):
            ''' constant_expression_opt : constant_expression
                                        | empty
            '''

        def p_identifier_list_opt(p):
            ''' identifier_list_opt : ID identifier_list_opt
                                    | empty
            '''

        def p_constant_expression(p):
            ''' constant_expression : binary_expression'''
            p[0] = p[1]

        def p_binary_expression(p):
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

        def p_cast_expression(p):
            '''cast_expression : unary_expression
                                | LPAREN type_specifier RPAREN cast_expression
            '''
            if len(p) == 2:
                p[0] = p[1]
            else:
                p[0] = p[2] + p[4]

        def p_unary_expression1(p):
            ''' unary_expression : postfix_expression
                                 | PLUSPLUS unary_expression
                                 | MINUSMINUS unary_expression
            '''
            if len(p) == 2:
                p[0] = p[1]
            else:
                p[0] = p[2]

        def p_unary_expression2(p):
            ''' unary_expression : unary_operator cast_expression '''
            p[0] = p[1] + Cast(p[2])

        def p_postfix_expression1(p):
            ''' postfix_expression : primary_expression '''
            p[0] = p[1]

        def p_postfix_expression2(p):
            ''' postfix_expression : postfix_expression LBRACKET expression RBRACKET '''
            p[0] = p[1] + p[3]

        def p_postfix_expression3(p):
            ''' postfix_expression : postfix_expression LPAREN argument_expression_opt RPAREN '''
            p[0] = p[1] + p[3]

        def p_postfix_expression4(p):
            ''' postfix_expression : postfix_expression PLUSPLUS
                                   | postfix_expression MINUSMINUS
            '''
            p[0] = p[1]

        def p_argument_expression_opt1(p):
            ''' argument_expression_opt : argument_expression '''
            p[0] = p[1]

        def p_argument_expression_opt2(p):
            ''' argument_expression_opt : empty '''
            p[0] = p[1]

        def p_primary_expression1(p):
            ''' primary_expression : ID '''
            p[0] = ID(p[1])

        def p_primary_expression2(p):
            ''' primary_expression : constant '''
            p[0] = p[1]

        def p_primary_expression3(p):
            ''' primary_expression : STRING '''
            #ToDo: what to do with STRING ?

        def p_primary_expression4(p):
            ''' primary_expression : LPAREN expression RPAREN '''
            p[0] = p[2]


        def p_constant1(p):
            ''' constant : INT_CONST '''
            p[0] = Constant('int', p[1])

        def p_constant2(p):
            ''' constant : FLOAT_CONST '''
            p[0] = Constant('float', p[1])

        def p_constant3(p):
            ''' constant : CHAR_CONST '''
            p[0] = Constant('char', p[1])

        def p_expression(p):
            ''' expression : assignment_expression
                           | expression COMMA assignment_expression
            '''
            if len(p) == 2:
                p[0] = p[1]
            else:
                p[0] = p[1] + p[3]

        def p_argument_expression(p):
            ''' argument_expression : assignment_expression
                                    | argument_expression COMMA assignment_expression
            '''
            if len(p) == 2:
                p[0] = p[1]
            else:
                p[0] = p[1] + p[3]


        def p_assignment_expression(p):
            ''' assignment_expression : binary_expression
                                      | unary_expression assignment_operator assignment_expression
            '''
            if len(p) == 2:
                p[0] = p[1]
            else:
                p[0] = p[1] + p[2] + p[3]

        def p_assignment_operator(p):
            '''assignment_operator :  TIMESASSIGN
                                   | DIVIDEASSIGN
                                   | MODASSIGN
                                   | PLUSASSIGN
                                   | MINUSASSIGN
            '''
            p[0] = p[1]

        def p_unary_operator(p):
            ''' unary_operator : ADDRESS
                               | TIMES
                               | PLUS
                               | MINUS
                               | UNARYDIFF
            '''
            p[0] = p[1]

        def p_type_specifier(p):
            ''' type_specifier : VOID
                               | CHAR
                               | INT
                               | FLOAT
            '''
            p[0] = Type(p[1])


        def p_parameter_list(p):
            ''' parameter_list : parameter_declaration
                               | parameter_list COMMA parameter_declaration
            '''
            if len(p) == 2:
                p[0] = ParamList(p[1])
            else:
                p[0] = ParamList(p[1], p[3])

        def p_parameter_declaration(p):
            ''' parameter_declaration : type_specifier direct_declarator '''
            p[0] = p[1] + p[2]

        def p_declaration(p):
            ''' declaration : type_specifier init_declarator_list_opt SEMI'''
            # print("tipo + lista_declaracao")
            # Decl() maybe?
            p[0] = VarDecl(p[1], p[2])

        def p_init_declarator_list_opt(p):
            ''' init_declarator_list_opt : init_declarator_list
                                         | empty
            '''

            if len(p) == 2:
                p[0] = p[1]
            else:
                p[0] = p[1]

        def p_init_declarator_list1(p):
            ''' init_declarator_list : init_declarator '''
            p[0] = p[1]

        def p_init_declarator_list2(p):
            ''' init_declarator_list : init_declarator_list COMMA init_declarator '''
            p[0] = p[1] + p[3]


        def p_init_declarator(p):
            ''' init_declarator : direct_declarator
                                | direct_declarator EQUALS initializer
            '''
            if len(p) == 2:
                p[0] = p[1]
            else:
                p[0] = Decl(p[1],p[3])

        def p_initializer1(p):
            ''' initializer : assignment_expression '''
            p[0] = p[1]

        def p_initializer2(p):
            ''' initializer : LBRACE initializer_list RBRACE
                            | LBRACE initializer_list COMMA RBRACE
            '''
            p[0] = p[2]

        def p_initializer_list1(p):
            ''' initializer_list : initializer '''
            p[0] = InitList(p[1])

        def p_initializer_list2(p):
            ''' initializer_list : initializer_list COMMA initializer '''
            p[0] = InitList(p[1], p[3])

        def p_compound_statement(p):
            ''' compound_statement : LBRACE declaration_list_opt statement_list_opt RBRACE '''
            p[0] = Compound(p[2], p[3])

        def p_statement_list_opt(p):
            ''' statement_list_opt : statement statement_list_opt
                                   | empty
            '''
            if len(p) > 2:
                p[0] = p[1] + p[2]
            else:
                p[0] = p[1]

        def p_statement(p):
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

        def p_expression_statement(p):
            ''' expression_statement : expression_opt SEMI'''
            p[0] = p[1]

        def p_expression_opt1(p):
            ''' expression_opt : expression '''
            p[0] = p[1]

        def p_expression_opt2(p):
            ''' expression_opt : empty '''
            p[0] = p[1]

        def p_selection_statement(p):
            ''' selection_statement : IF LPAREN expression RPAREN statement
                                    | IF LPAREN expression RPAREN statement ELSE statement
            '''
            if len(p) == 6:
                p[0] = If(p[3], p[5])
            else:
                p[0] = If(p[3], p[5], p[7])

        def p_iteration_statement1(p):
            ''' iteration_statement : WHILE LPAREN expression RPAREN statement '''
            p[0] = While(p[3], p[5])

        def p_iteration_statement2(p):
            ''' iteration_statement : FOR LPAREN init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement '''
            p[0] = For(p[3], p[5], p[7], p[8])

        def p_iteration_statement3(p):
            ''' iteration_statement : FOR LPAREN type_specifier init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement '''
            p[0] = For(p[3], p[4], p[6], p[8], p[9])

        def p_jump_statement1(p):
            ''' jump_statement : BREAK SEMI '''
            p[0] = Break()

        def p_jump_statement2(p):
            ''' jump_statement : RETURN SEMI
                               | RETURN expression SEMI
            '''
            if len(p) <= 3:
                Return()
            else:
                Return(p[2])

        def p_assert_statement(p):
            ''' assert_statement : ASSERT expression SEMI '''
            p[0] = Assert(p[2])

        def p_print_statement(p):
            ''' print_statement : PRINT LPAREN expression_opt RPAREN SEMI'''
            p[0] = Print(p[3])

        def p_read_statement(p):
            ''' read_statement : READ LPAREN argument_expression RPAREN SEMI'''
            p[0] = Read(p[3])

        def p_empty(p):
            '''empty :'''
            p[0] = EmptyStatement()

        def p_error(p):
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



        parser = yacc(write_tables=False)
        return parser.parse(code)


