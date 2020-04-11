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


    def _fix_decl_name_type(self, decl, typename):
        """ Fixes a declaration. Modifies decl.
        """
        # Reach the underlying basic type
        type = decl
        while not isinstance(type, ast.VarDecl):
            type = type.type

        decl.name = type.declname

        # The typename is a list of types. If any type in this
        # list isn't an Type, it must be the only
        # type in the list.
        # If all the types are basic, they're collected in the
        # Type holder.
        for tn in typename:
            if not isinstance(tn, ast.Type):
                if len(typename) > 1:
                    self._parse_error(
                        "Invalid multiple types specified", tn.coord)
                else:
                    type.type = tn
                    return decl

        if not typename:
            # Functions default to returning int
            if not isinstance(decl.type, ast.FuncDecl):
                self._parse_error("Missing type in declaration", decl.coord)
            type.type = ast.Type(['int'], coord=decl.coord)
        else:
            # At this point, we know that typename is a list of Type
            # nodes. Concatenate all the names into a single list.
            type.type = ast.Type(
                [typename.names[0]],
                coord=typename.coord)
        return decl

    def _type_modify_decl(self, decl, modifier):
        """ Tacks a type modifier on a declarator, and returns
            the modified declarator.
            Note: the declarator and modifier may be modified
        """
        modifier_head = modifier
        modifier_tail = modifier

        # The modifier may be a nested list. Reach its tail.
        while modifier_tail.type:
            modifier_tail = modifier_tail.type

        # If the decl is a basic type, just tack the modifier onto it
        if isinstance(decl, ast.VarDecl):
            modifier_tail.type = decl
            return modifier
        else:
            # Otherwise, the decl is a list of modifiers. Reach
            # its tail and splice the modifier onto the tail,
            # pointing to the underlying basic type.
            decl_tail = decl

            while not isinstance(decl_tail.type, ast.VarDecl):
                decl_tail = decl_tail.type

            modifier_tail.type = decl_tail.type
            decl_tail.type = modifier_head
            return decl

    def _build_declarations(self, spec, decls):
        """ Builds a list of declarations all sharing the given specifiers.
        """
        declarations = []

        for decl in decls:
            assert decl['decl'] is not None
            declaration = ast.Decl(
                name=None,
                type=decl['decl'],
                init=decl.get('init'),
                coord=decl['decl'].coord)

            fixed_decl = self._fix_decl_name_type(declaration, spec)
            declarations.append(fixed_decl)

        return declarations

    def parse(self, code, bosta, debug):

        return self.parser.parse(code)

    def p_program(self, p):
        ''' program : global_declaration_list_opt
        '''
        p[0] = Program(p[1])

    def p_global_declaration_list_opt(self, p):
        ''' global_declaration_list_opt : global_declaration global_declaration_list_opt
                                        | global_declaration
        '''
        if len(p) >= 3:
            p[0] = [p[1] + p[2]]
        else:
            p[0] = [p[1]]
        print('p_global_declaration_list_opt')

    def p_global_declaration(self, p):
        ''' global_declaration : function_definition
                              | declaration
        '''
        p[0] = GlobalDecl(p[1])
        print('global_declaration')

    def p_function_definition(self, p):
        ''' function_definition : type_specifier declarator compound_statement
                                | declarator declaration_list_opt  compound_statement
        '''
        print('function_definition')

    def p_declaration_list_opt(self, p):
        ''' declaration_list_opt : declaration declaration_list_opt
                                 | empty
        '''
        print("declaration_list_opt")

    def p_declarator(self, p):
        ''' declarator : direct_declarator
        '''
        p[0] = p[1]
        print('declarator')

    def p_direct_declarator1(self, p):
        ''' direct_declarator : ID
                              | LPAREN declarator RPAREN
        '''
        if len(p) == 2:
            p[0] = ID(p[1])
        else:
            pass
        # elif len(p) == 4:
        #     p[0] = Decl(p[2])
        print('direct_declarator')

    def p_direct_declarator2(self, p):
        ''' direct_declarator : direct_declarator LBRACKET constant_expression_opt RBRACKET '''


    def p_direct_declarator3(self, p):
        ''' direct_declarator : direct_declarator LPAREN parameter_list RPAREN '''

    def p_direct_declarator4(self, p):
        ''' direct_declarator : direct_declarator LPAREN identifier_list_opt RPAREN '''

    def p_constant_expression_opt(self, p):
        ''' constant_expression_opt : constant_expression
                                    | empty
        '''
        print('constant_expression_opt')

    def p_identifier_list_opt(self, p):
        ''' identifier_list_opt : ID identifier_list_opt
                                | empty
        '''
        print('identifier_list_opt')

    def p_constant_expression(self, p):
        ''' constant_expression : binary_expression'''
        print('constant_expression')

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
        print('binary_expression')

    def p_cast_expression(self, p):
        '''cast_expression : unary_expression
                            | LPAREN type_specifier RPAREN cast_expression
        '''
        print('cast_expression')

    def p_unary_expression(self, p):
        ''' unary_expression : postfix_expression
                             | PLUSPLUS unary_expression
                             | MINUSMINUS unary_expression
                             | unary_operator cast_expression
        '''
        print('')

    def p_postfix_expression(self, p):
        ''' postfix_expression : primary_expression
                               | postfix_expression LBRACKET expression RBRACKET
                               | postfix_expression LPAREN argument_expression_opt RPAREN
                               | postfix_expression PLUSPLUS
                               | postfix_expression MINUSMINUS
        '''
        print('')

    def p_argument_expression_opt(self, p):
        ''' argument_expression_opt : argument_expression
                                    | empty
        '''
        print('')

    def p_primary_expression(self, p):
        ''' primary_expression : ID
                               | constant
                               | STRING
                               | LPAREN expression RPAREN
        '''
        print('')

    def p_constant(self, p):
        ''' constant : INT_CONST
                     | FLOAT_CONST
                     | CHAR_CONST
        '''
        print('')

    def p_expression(self, p):
        ''' expression : assignment_expression
                       | expression COMMA assignment_expression
        '''
        print('')

    def p_argument_expression(self, p):
        ''' argument_expression : assignment_expression
                                | argument_expression COMMA assignment_expression
        '''
        print('')

    def p_assignment_expression(self, p):
        ''' assignment_expression : binary_expression
                                  | unary_expression assignment_operator assignment_expression
        '''
        print('')

    def p_assignment_operator(self, p):
        '''assignment_operator :  TIMESASSIGN
                               | DIVIDEASSIGN
                               | MODASSIGN
                               | PLUSASSIGN
                               | MINUSASSIGN
        '''
        print('')

    def p_unary_operator(self, p):
        ''' unary_operator : ADDRESS
                           | TIMES
                           | PLUS
                           | MINUS
                           | UNARYDIFF
        '''
        print('unary_operator')

    def p_type_specifier(self, p):
        ''' type_specifier : VOID
                           | CHAR
                           | INT
                           | FLOAT
        '''
        p[0] = Type(p[1], coord=None)
        print('type_specifier')

    def p_parameter_list(self, p):
        ''' parameter_list : parameter_declaration
                           | parameter_list COMMA parameter_declaration
        '''
        print('parameter_list')

    def p_parameter_declaration(self, p):
        ''' parameter_declaration : type_specifier declarator '''
        print('parameter_declaration')

    def p_declaration(self, p):
        ''' declaration : declaration_body SEMI'''
        p[0] = p[1]
        print("declaration")

    def p_declaration_body(self, p):
        ''' declaration_body : type_specifier init_declarator_list_opt'''
        # p[0] = self._build_declarations(p[1], p[2])
        p[0] = Decl(p[2], VarDecl(p[1], p[2]), None)
        print("declaration")

    def p_init_declarator_list_opt(self, p):
        ''' init_declarator_list_opt : init_declarator_list
                                     | empty
        '''
        p[0] = p[1]
        print('init_declarator_list_opt')

    def p_init_declarator_list(self, p):
        ''' init_declarator_list : init_declarator
                                 | init_declarator_list COMMA init_declarator
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            # p[0] = DeclList()
            # p[0] = p[1]
            pass
        print('init_declarator_list')

    def p_init_declarator(self, p):
        ''' init_declarator : declarator
                            | declarator EQUALS initializer
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            # p[0] = Assignment(p[2])
            pass
        print('init_declarator')

    def p_initializer(self, p):
        ''' initializer : assignment_expression
                        | LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        '''
        print('initializer')

    def p_initializer_list(self, p):
        ''' initializer_list : initializer
                             | initializer_list COMMA initializer
        '''
        print('initializer_list')

    def p_compound_statement(self, p):
        ''' compound_statement : LBRACE declaration_list_opt statement_list_opt RBRACE '''
        print('compound_statement')

    def p_statement_list_opt(self, p):
        ''' statement_list_opt : statement statement_list_opt
                               | empty
        '''
        print("statement_list_opt")

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
        print("statement")

    def p_expression_statement(self, p):
        ''' expression_statement : expression_opt SEMI'''
        print('expression_statement')

    def p_expression_opt(self, p):
        ''' expression_opt : expression
                           | empty
        '''
        print('expression_opt')

    def p_selection_statement(self, p):
        ''' selection_statement : IF LPAREN expression RPAREN statement
                                | IF LPAREN expression RPAREN statement ELSE statement
        '''
        print('selection_statement')

    def p_iteration_statement(self, p):
        ''' iteration_statement : WHILE LPAREN expression RPAREN statement
                                | FOR LPAREN init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement
                                | FOR LPAREN type_specifier init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement
        '''
        print("iteration_statement")

    def p_jump_statement(self, p):
        ''' jump_statement : BREAK SEMI
                           | RETURN SEMI
                           | RETURN expression SEMI
        '''
        print('jump_statement')

    def p_assert_statement(self, p):
        ''' assert_statement : ASSERT expression SEMI '''
        print('assert_statement')

    def p_print_statement(self, p):
        ''' print_statement : PRINT LPAREN expression_opt RPAREN SEMI'''
        print('print_statement')

    def p_read_statement(self, p):
        ''' read_statement : READ LPAREN argument_expression RPAREN SEMI'''
        print('read_statement')

    def p_empty(self, p):
        '''empty :'''
        pass

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




