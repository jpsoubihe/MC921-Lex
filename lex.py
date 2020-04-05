import sys

from ply.lex import lex

# tokens
from ply.yacc import yacc

# Reserved keywords
keywords = (
    'ASSERT', 'BREAK', 'CHAR', 'ELSE', 'FLOAT', 'FOR', 'IF',
    'INT', 'PRINT', 'READ', 'RETURN', 'VOID', 'WHILE',
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
    'EQUALS', 'EQ', 'TIMES', 'MINUS', 'ADDRESS', 'PLUS', 'PLUSPLUS', 'UNARYDIFF', 'MINUSMINUS',
    # operators
    'LT', 'HT', 'LE', 'HE', 'DIVIDE', 'MOD', 'DIFF', 'AND', 'OR',

    # assignment
    'DIVIDEASSIGN', 'MODASSIGN', 'PLUSASSIGN', 'MINUSASSIGN', 'TIMESASSIGN',

    # braces
    'RPAREN', 'LPAREN', 'RBRACE', 'LBRACE', 'RBRACKET', 'LBRACKET',

    # punctuation
    'SEMI', 'COMMA',
)

#
# Rules
#
t_ignore = ' \t'


# Newlines
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_ID(t):
    r'[a-zA-Z_][0-9a-zA-Z_]*'
    t.type = keyword_map.get(t.value, "ID")
    return t


def t_multilinecomment(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')

def t_comment(t):
    r'\/\/.*'


def t_string(t):
    r'\".*?\"'
    t.type = keyword_map.get(t.value, "STRING")
    return t


def t_UNARYDIFF(t):
    r'\!'
    t.type = keyword_map.get(t.value, "UNARYDIFF")
    return t


def t_DIVIDEASSIGN(t):
    r'\/\='
    t.type = keyword_map.get(t.value, "DIVIDEASSIGN")
    return t


def t_MODASSIGN(t):
    r'\%\='
    t.type = keyword_map.get(t.value, "MODASSIGN")
    return t


def t_PLUSASSIGN(t):
    r'\+\='
    t.type = keyword_map.get(t.value, "PLUSASSIGN")
    return t

def t_MINUSASSIGN(t):
    r'\-\='
    t.type = keyword_map.get(t.value, "MINUSASSIGN")
    return t


def t_MINUSMINUS(t):
    r'\-\-'
    t.type = keyword_map.get(t.value, "MINUSMINUS")
    return t


def t_AND(t):
    r'\|\|'
    t.type = keyword_map.get(t.value, "AND")
    return t

def t_OR(t):
    r'\|\|'
    t.type = keyword_map.get(t.value, "OR")
    return t


def t_divide(t):
    r'\/'
    t.type = keyword_map.get(t.value, "DIVIDE")
    return t


def t_EQ(t):
    r'\=\='
    t.type = keyword_map.get(t.value, "EQ")
    return t


def t_EQUALS(t):
    r'='
    t.type = keyword_map.get(t.value, "EQUALS")
    return t


def t_PLUSPLUS(t):
    r'\+\+'
    t.type = keyword_map.get(t.value, "PLUSPLUS")
    return t


def t_PLUS(t):
    r'\+'
    t.type = keyword_map.get(t.value, "PLUS")
    return t


def t_MINUS(t):
    r'\-'
    t.type = keyword_map.get(t.value, "MINUS")
    return t

def t_DIFF(t):
    r'\!='
    t.type = keyword_map.get(t.value, "DIFF")
    return t


def t_LE(t):
    r'\<\='
    t.type = keyword_map.get(t.value, "LE")
    return t


def t_LT(t):
    r'\<'
    t.type = keyword_map.get(t.value, "LT")
    return t


def t_HE(t):
    r'\>\='
    t.type = keyword_map.get(t.value, "HE")
    return t


def t_HT(t):
    r'\>'
    t.type = keyword_map.get(t.value, "HT")
    return t


def t_SEMI(t):
    r';'
    t.type = keyword_map.get(t.value, "SEMI")
    return t


def t_FLOAT_CONST(t):
    r'[0-9]\.[0-9]*'
    t.type = keyword_map.get(t.value, "FLOAT_CONST")
    return t

def t_INT_CONST(t):
    r'[0-9][0-9]*'
    t.type = keyword_map.get(t.value, "INT_CONST")
    return t

def t_TIMES(t):
    r'\*'
    t.type = keyword_map.get(t.value, "TIMES")
    return t


def t_MOD(t):
    r'\%'
    t.type = keyword_map.get(t.value, "MOD")
    return t


def t_LPAREN(t):
    r'\('
    t.type = keyword_map.get(t.value, "LPAREN")
    return t


def t_RPAREN(t):
    r'\)'
    t.type = keyword_map.get(t.value, "RPAREN")
    return t


def t_LBRACE(t):
    r'\{'
    t.type = keyword_map.get(t.value, "LBRACE")
    return t


def t_RBRACE(t):
    r'\}'
    t.type = keyword_map.get(t.value, "RBRACE")
    return t


def t_LBRACKET(t):
    r'\['
    t.type = keyword_map.get(t.value, "LBRACKET")
    return t


def t_RBRACKET(t):
    r'\]'
    t.type = keyword_map.get(t.value, "RBRACKET")
    return t

def t_COMMA(t):
    r'\,'
    t.type = keyword_map.get(t.value, "COMMA")
    return t

def t_ADDRESS(t):
    r'\&'
    t.type = keyword_map.get(t.value, "ADDRESS")
    return t

def t_error(t):
    print(f'Illegal character {t.value[0]}')
    t.lexer.skip(1)


lexer = lex()
# lexer.input(open(sys.argv[1]).read())
# for tok in lexer:
#     print(tok)

def p_program(p):
    '''program :  global_declaration '''
    print("program")


def p_global_declaration(p):
    ''' global_declaration : function_definition
                            | declaration
        '''
    print("global_declaration")


def p_function_definition(p):
    ''' function_definition : type_specifier direct_declarator compound_statement
                            | direct_declarator declaration compound_statement
        '''
    print("function_definition")


def p_type_specifier(p):
    ''' type_specifier : VOID
                        | CHAR
                        | INT
                        | FLOAT
            '''
    print("type_specifier")


def p_direct_declarator(p):
    '''direct_declarator : ID
                        | LPAREN direct_declarator RPAREN
                        | direct_declarator LBRACKET RBRACKET
                        | direct_declarator LBRACKET binary_expression RBRACKET
                        | direct_declarator LPAREN parameter_list RPAREN
                        | direct_declarator LPAREN RPAREN
                        | direct_declarator LPAREN ID RPAREN
    '''
    print("direct_declarator")


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
    print("binary_expression")


def p_cast_expression(p):
    '''cast_expression : unary_expression
                        | LPAREN type_specifier RPAREN cast_expression
    '''
    print("cast_expression")


def p_unary_expression(p):
    ''' unary_expression : postfix_expression
                        | PLUSPLUS unary_expression
                        | MINUSMINUS unary_expression
                        | unary_operator cast_expression
    '''
    print("unary_expression")


def p_postfix_expression(p):
    '''postfix_expression : primary_expression
                        | postfix_expression LBRACKET expression RBRACKET
                        | postfix_expression LPAREN expression RPAREN
                        | postfix_expression LPAREN RPAREN
                        | postfix_expression PLUSPLUS
                        | postfix_expression MINUSMINUS
    '''
    print("postfix_expression")


def p_primary_expression(p):
    '''primary_expression : ID
                        | constant
                        | LPAREN expression RPAREN
    '''
    print("primary_expression")


def p_constant(p):
    '''constant : INT_CONST
                | STRING
                | FLOAT_CONST
    '''
    print("constant")


def p_expression(p):
    '''expression : assignment_expression
                | expression COMMA assignment_expression
    '''
    print("expression")


def p_assignment_expression(p):
    '''assignment_expression : binary_expression
                            | unary_expression assignment_operator assignment_expression
    '''
    print("assignment_expression")

def p_assignment_operator(p):
    '''assignment_operator : EQUALS
                        | TIMESASSIGN
                        | DIVIDEASSIGN
                        | MODASSIGN
                        | PLUSASSIGN
                        | MINUSASSIGN
    '''
    print("assignment_expression")

def p_unary_operator(p):
    '''unary_operator : ADDRESS
                   | TIMES
                   | PLUS
                   | MINUS
                   | UNARYDIFF
    '''
    print("unary_operator")

def p_parameter_list(p):
    ''' parameter_list : parameter_declaration
                        | parameter_list parameter_declaration
    '''
    print("parameter_list")

def p_parameter_declaration(p):
    '''parameter_declaration : type_specifier direct_declarator
    '''
    print("parameter_declaration")

def p_declaration(p):
    '''declaration : type_specifier init_declarator_list SEMI
                   | type_specifier SEMI
    '''
    print("declaration")


def p_init_declarator_list(p):
    '''init_declarator_list : init_declarator
                            | init_declarator_list COMMA init_declarator
    '''
    print("init_declarator_list")

def p_init_declarator(p):
    '''init_declarator : direct_declarator
                        | direct_declarator EQ initializer
                        | direct_declarator EQUALS initializer
    '''
    print("init_declarator")

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
    '''compound_statement : LBRACE declaration statement RBRACE
                          | LBRACE statement RBRACE'''

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
                   | RETURN expression SEMI
                   | RETURN SEMI
    '''
    print("jump_statement")

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

print("----------------------------------------PARSE----------------------------------------")
parser = yacc(write_tables=False)
parser.parse(open(sys.argv[1]).read())
