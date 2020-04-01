import sys

from ply.lex import lex

# tokens
from ply.yacc import yacc

# Reserved keywords
keywords = (
    # type specifiers
    'CHAR', 'FLOAT', 'VOID', 'INT',
    'ASSERT', 'BREAK', 'ELSE', 'FOR', 'IF',
    'PRINT', 'READ', 'RETURN', 'WHILE',
)

keyword_map = {}
for keyword in keywords:
    keyword_map[keyword.lower()] = keyword

#
# All the tokens recognized by the lexer
#
tokens = keywords + (
    # Identifiers
    'ID',

    # constants
    'INT_CONST', 'FLOAT_CONST', 'STRING',


    # operations
    'TIMES', 'MINUS', 'UNARYDIFF', 'MINUSMINUS', 'ADDRESS', 'PLUS', 'PLUSPLUS',

    #operators
    'LT', 'HT', 'LE', 'HE', 'DIVIDE', 'MOD', 'DIFF', 'AND', 'OR',

    # assignment
    'EQUALS', 'EQ', 'DIVIDEASSIGN', 'MODASSIGN', 'PLUSASSIGN', 'MINUSASSIGN', 'TIMESASSIGN',

    # braces
    'RPAREN', 'LPAREN', 'RBRACE', 'LBRACE', 'RBRACKET', 'LBRACKET',

    # punctuation
    'SEMI', 'COMMA',
)

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value == 'print':
        t.type = "PRINT"
    return t

t_TIMES = r'\*'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_STRING = r'\".*?\"'
t_DIVIDE = r'\/'
t_EQ = r'\=\='
t_EQUALS = r'='
t_PLUS = r'\+'
t_PLUSPLUS = r'\+\+'
t_MINUS = r'\-'
t_MINUSMINUS = r'\-\-'
t_DIFF = r'\!='
t_LE = r'\<\='
t_LT = r'\<'
t_HE = r'\>\='
t_HT = r'\>'
t_SEMI = r';'
t_FLOAT_CONST = r'[0-9]\.[0-9]*'
t_INT_CONST = r'[0-9][0-9]*'
t_MOD = r'\%'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r'\,'
t_ADDRESS = r'\&'
t_AND = r'\&\&'
t_OR = r'\|\|'
t_UNARYDIFF = r'\!'
t_DIVIDEASSIGN = r'\/\='
t_MODASSIGN = r'\%\='
t_MINUSASSIGN = r'\-\='
t_PLUSASSIGN = r'\+\='
t_TIMESASSIGN = r'\*\='


def t_error(t):
    print(f'Illegal character {t.value[0]}')
    t.lexer.skip(1)

t_ignore = ' \t'

lexer = lex()

lexer.input("a = 3 * 4 + 5")
for tok in lexer:
    print(tok)

#def p_program(p):
 #   '''program : LBRACE global_declaration RBRACE'''

def p_global_declaration(p):
    ''' global_declaration : function_definition
                            | declaration
        '''

def p_function_declaration(p):
    ''' function_definition : LBRACE type_specifier RBRACE declarator LBRACE declaration RBRACE compound_statement
        '''

def p_type_specifier(p):
    ''' type_specifier : VOID
                        | CHAR
                        | INT
                        | FLOAT
            '''

def p_declarator(p):
    '''declarator : direct_declarator
    '''

def p_direct_declarator(p):
    '''direct_declarator : ID
                        | LPAREN declarator RPAREN
                        | direct_declarator LBRACKET constant_expression RBRACKET
                        | direct_declarator LPAREN parameter_list RPAREN
                        | direct_declarator LPAREN LBRACE ID RBRACE RPAREN
    '''

def p_constant_expression(p):
    '''constant_expression : binary_expression'''

def p_binary_expression(p):
    '''binary_expression :  cast_expression
                        | binary_expression TIMES binary_expression
                        | binary_expression DIVIDE binary_expression
                        | binary_expression MOD binary_expression
                        | binary_expression PLUS binary_expression
                        | binary_expression MINUS binary_expression
                        | binary_expression LT binary_expression
                        | binary_expression LE binary_expression
                        | binary_expression HT binary_expression
                        | binary_expression HE binary_expression
                        | binary_expression EQ binary_expression
                        | binary_expression DIFF binary_expression
                        | binary_expression AND binary_expression
                        | binary_expression OR binary_expression
    '''

def p_cast_expression(p):
    '''cast_expression : unary_expression
                        | LPAREN type_specifier RPAREN cast_expression
    '''

def p_unary_expression(p):
    ''' unary_expression : postfix_expression
                        | PLUSPLUS unary_expression
                        | MINUSMINUS unary_expression
                        | unary_operator cast_expression
    '''

def p_postfix_expression(p):
    '''postfix_expression : primary_expression
                        | postfix_expression LBRACKET expression RBRACKET
                        | postfix_expression LPAREN LBRACE expression RBRACE RPAREN
                        | postfix_expression PLUSPLUS
                        | postfix_expression MINUSMINUS
    '''

def p_primary_expression(p):
    '''primary_expression : ID
                        | constant
                        | LPAREN expression RPAREN
    '''

def p_constant(p):
    '''constant : INT_CONST
                | STRING
                | FLOAT_CONST
    '''

def p_expression(p):
    '''expression : assignment_expression
                | expression COMMA assignment_expression
    '''

# def p_argument_expression(p):
#     '''argument_expression : assignment_expression
#                             | argument_expression COMMA assignment_expression
#     '''

def p_assignment_expression(p):
    '''assignment_expression : binary_expression
                            | unary_expression assignment_operator assignment_expression
    '''

def p_assignment_operator(p):
    '''assignment_operator : EQUALS
                        | TIMESASSIGN
                        | DIVIDEASSIGN
                        | MODASSIGN
                        | PLUSASSIGN
                        | MINUSASSIGN
    '''

def p_unary_operator(p):
    '''unary_operator : ADDRESS
                   | TIMES
                   | PLUS
                   | MINUS
                   | UNARYDIFF
    '''

def p_parameter_list(p):
    ''' parameter_list : parameter_declaration
                        | parameter_list parameter_declaration
    '''

def p_parameter_declaration(p):
    '''parameter_declaration : type_specifier declarator
    '''

def p_declaration(p):
    '''declaration : type_specifier LBRACE init_declarator_list RBRACE SEMI'''

def p_init_declarator_list(p):
    '''init_declarator_list : init_declarator
                            | init_declarator_list COMMA init_declarator
    '''

def p_init_declarator(p):
    '''init_declarator : declarator
                        | declarator EQ initializer
    '''

def p_initializer(p):
    '''initializer : assignment_expression
                    | LBRACE initializer_list RBRACE
                    | LBRACE initializer_list COMMA RBRACE
    '''

def p_initializer_list(p):
    '''initializer_list : initializer
                     | initializer_list COMMA initializer
    '''

def p_compound_statement(p):
    '''compound_statement : LBRACE LBRACE declaration RBRACE TIMES LBRACE statement RBRACE RBRACE'''

def p_statement(p):
    '''statement : expression_statement
              | compound_statement
              | selection_statement
              | iteration_statement
              | jump_statement
              | assert_statement
              | print_statement
              | read_statement
    '''

def p_expression_statement(p):
    '''expression_statement : LBRACE expression RBRACE SEMI '''

def p_selection_statement(p):
    '''selection_statement : IF LPAREN expression RPAREN statement
                        | IF LPAREN expression RPAREN statement ELSE statement
    '''

def p_iteration_statement(p):
    '''iteration_statement : WHILE LPAREN expression RPAREN statement
                        | FOR LPAREN LBRACE expression RBRACE SEMI LBRACE expression RBRACE SEMI LBRACE expression RBRACE RPAREN statement
    '''

def p_jump_statement(p):
    '''jump_statement : BREAK SEMI
                   | RETURN LBRACE expression RBRACE SEMI
    '''

def p_assert_statement(p):
    '''assert_statement : ASSERT expression SEMI
    '''

def p_print_statement(p):
    '''print_statement : PRINT LPAREN LBRACE expression RBRACE RPAREN SEMI'''

def p_read_statement(p):
    '''read_statement : READ LPAREN expression RPAREN SEMI'''


def p_error(p):
    if p:
        print("Error near the symbol %s" % p.value)
    else:
        print("Error at the end of input")


precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ','DIFF'),
    ('left', 'HT', 'HE', 'LT', 'LE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD')
    )


parser = yacc(write_tables=False)
parser.parse(open(sys.argv[1]).read())

# parser.parse('a == 3')
