import sys

from ply.lex import lex

# tokens
from ply.yacc import yacc
from pack.ast import Program, FuncDef, Decl
from pack.ast import GlobalDecl
from pack.ast import EmptyStatement


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
    'INT_CONST', 'FLOAT_CONST', 'STRING', 'CHAR_CONST',

    # operations
    'EQUALS', 'EQ', 'TIMES', 'MINUS', 'ADDRESS', 'PLUS', 'UNARYDIFF', 'PLUSPLUS', 'MINUSMINUS',
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
    r'\&\&'
    t.type = keyword_map.get(t.value, "AND")
    return t

def t_OR(t):
    r'\|\|'
    t.type = keyword_map.get(t.value, "OR")
    return t


def t_DIVIDE(t):
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


def t_UNARYDIFF(t):
    r'\!'
    t.type = keyword_map.get(t.value, "UNARYDIFF")
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


# ToDo: check if rule applies
def t_CHAR_CONST(t):
    r'\'[a-z | A-Z]\''
    t.type = keyword_map.get(t.value, "CHAR_CONST")
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
    ''' program : global_declaration_list_opt
    '''
    p[0] = Program(p[1])


def p_global_declaration_list_opt(p):
    ''' global_declaration_list_opt : global_declaration global_declaration_list_opt
                                    | empty
    '''
    if len(p) < 1:
        p[0] = EmptyStatement()

def p_global_declaration(p):
    ''' global_declaration : function_definition
                           | declaration
    '''
    p[0] = GlobalDecl(p[1])


def p_function_definition1(p):
    ''' function_definition : type_specifier declarator compound_statement
    '''
    p[0] = FuncDef(p[0], p[1], p[2])


def p_function_definition2(p):
    ''' function_definition : declarator declaration_list_opt  compound_statement'''
    p[0] = FuncDef(p[0], [p[1]], p[2])


def p_declaration_list_opt(p):
    ''' declaration_list_opt : declaration declaration_list_opt
                             | empty
    '''


def p_declarator(p):
    ''' declarator : direct_declarator
    '''


def p_direct_declarator(p):
    ''' direct_declarator : ID
                          | LPAREN declarator RPAREN
                          | direct_declarator LBRACKET constant_expression_opt RBRACKET
                          | direct_declarator LPAREN parameter_list RPAREN
                          | direct_declarator LPAREN identifier_list_opt RPAREN
    '''


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
    ''' postfix_expression : primary_expression
                           | postfix_expression LBRACKET expression RBRACKET
                           | postfix_expression LPAREN argument_expression_opt RPAREN
                           | postfix_expression PLUSPLUS
                           | postfix_expression MINUSMINUS
    '''


def p_argument_expression_opt(p):
    ''' argument_expression_opt : argument_expression
                                | empty
    '''


def p_primary_expression(p):
    ''' primary_expression : ID
                           | constant
                           | STRING
                           | LPAREN expression RPAREN
    '''

def p_constant(p):
    ''' constant : INT_CONST
                 | FLOAT_CONST
                 | CHAR_CONST
    '''


def p_expression(p):
    ''' expression : assignment_expression
                   | expression COMMA assignment_expression
    '''


def p_argument_expression(p):
    ''' argument_expression : assignment_expression
                            | argument_expression COMMA assignment_expression
    '''

def p_assignment_expression(p):
    ''' assignment_expression : binary_expression
                              | unary_expression assignment_operator assignment_expression
    '''


def p_assignment_operator(p):
    '''assignment_operator :  TIMESASSIGN
                           | DIVIDEASSIGN
                           | MODASSIGN
                           | PLUSASSIGN
                           | MINUSASSIGN
    '''


def p_unary_operator(p):
    ''' unary_operator : ADDRESS
                       | TIMES
                       | PLUS
                       | MINUS
                       | UNARYDIFF
    '''


def p_type_specifier(p):
    ''' type_specifier : VOID
                       | CHAR
                       | INT
                       | FLOAT
    '''


def p_parameter_list(p):
    ''' parameter_list : parameter_declaration
                       | parameter_list COMMA parameter_declaration
    '''


def p_parameter_declaration(p):
    ''' parameter_declaration : type_specifier declarator '''


def p_declaration(p):
    ''' declaration : type_specifier init_declarator_list_opt SEMI'''
    p[0] = Decl("jsojdos", p[1], [p[2]])


def p_init_declarator_list_opt(p):
    ''' init_declarator_list_opt : init_declarator_list
                                 | empty
    '''


def p_init_declarator_list(p):
    ''' init_declarator_list : init_declarator
                             | init_declarator_list COMMA init_declarator
    '''


def p_init_declarator(p):
    ''' init_declarator : declarator
                        | declarator EQUALS initializer
    '''


def p_initializer(p):
    ''' initializer : assignment_expression
                    | LBRACE initializer_list RBRACE
                    | LBRACE initializer_list COMMA RBRACE
    '''


def p_initializer_list(p):
    ''' initializer_list : initializer
                         | initializer_list COMMA initializer
    '''


def p_compound_statement(p):
    ''' compound_statement : LBRACE declaration_list_opt statement_list_opt RBRACE
    '''


def p_statement_list_opt(p):
    ''' statement_list_opt : statement statement_list_opt
                           | empty
    '''


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

def p_expression_statement(p):
    ''' expression_statement : expression_opt SEMI'''


def p_expression_opt(p):
    ''' expression_opt : expression
                       | empty
    '''


def p_selection_statement(p):
     ''' selection_statement : IF LPAREN expression RPAREN statement
                             | IF LPAREN expression RPAREN statement ELSE statement
     '''


def p_iteration_statement(p):
    ''' iteration_statement : WHILE LPAREN expression RPAREN statement
                            | FOR LPAREN init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement
                            | FOR LPAREN type_specifier init_declarator SEMI expression_opt SEMI expression_opt RPAREN statement
    '''


def p_jump_statement(p):
    ''' jump_statement : BREAK SEMI
                       | RETURN SEMI
                       | RETURN expression SEMI
    '''


def p_assert_statement(p):
    ''' assert_statement : ASSERT expression SEMI '''


def p_print_statement(p):
    ''' print_statement : PRINT LPAREN expression_opt RPAREN SEMI'''


def p_read_statement(p):
    ''' read_statement : READ LPAREN argument_expression RPAREN SEMI'''

def p_empty(p):
    '''empty :'''
    pass


def p_error(p):
    if p:
        print("Error near the symbol %s" % p.value)
    else:
        print("Error at the end of input")


precedence = (
    ('left', 'OR'),
    ('left', 'AND', 'EQUALS'),
    ('left', 'EQ','DIFF'),
    ('left', 'HT', 'HE', 'LT', 'LE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD')
    )



print("----------------------------------------PARSE----------------------------------------")
parser = yacc(write_tables=False)
parser.parse(open(sys.argv[1]).read())
