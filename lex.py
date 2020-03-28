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
    'TIMES', 'MINUS', 'UNARYAND', 'UNARYDIFF', 'MINUSMINUS', 'ADDRESS', 'PLUS', 'PLUSPLUS',

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

# def t_NUM(t):
#     r'[0-9]+'
#     t.value = int(t.value)
#     return t

t_TIMES = r'\*'
# t_EQ = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
# t_NEWLINE = r'\n+'
# t_multilinecomment = r'/\*(.|\n)*?\*/'
# t_comment = r'\/\/.*'
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
t_UNARYDIFF = '\!'
t_UNARYAND = '\&'








def t_error(t):
    print(f'Illegal character {t.value[0]}')
    t.lexer.skip(1)

t_ignore = ' \t'

lexer = lex()

lexer.input("a = 3 * 4 + 5")
for tok in lexer:
    print(tok)


def p_statement_list(p):
    ''' statements : statements statement
                   | statement
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + (p[2])



def p_assign_statement(p):
    ''' statement : ID EQUALS expr
    '''
    p[0] = ('assign', p[1], p[3])

def p_print_statement(p):
    ''' statement : PRINT LPAREN expr RPAREN
    '''
    p[0] = ('print', p[3])


def p_binop_expr(p):
    ''' expr : expr PLUS expr
             | expr TIMES expr
    '''
    p[0] = (p[2], p[1], p[3])


def p_num_expr(p):
    ''' expr : INT_CONST
    '''
    p[0] = ('int', p[1])


def p_name_expr(p):
    ''' expr : ID
    '''
    p[0] = ('id', p[1])

def p_ADDRESS(p):
    ''' expr : ADDRESS
    '''

def p_ASSERT(p):
    ''' expr : ASSERT
    '''

def p_BREAK(p):
    ''' expr : BREAK
    '''

def p_CHAR(p):
    ''' expr : CHAR
    '''

def p_COMMA(p):
    ''' expr : COMMA
    '''

def p_DIFF(p):
    ''' expr : DIFF
    '''

def p_DIVIDE(p):
    ''' expr : DIVIDE
    '''

def p_ELSE(p):
    ''' expr : ELSE
    '''

def p_EQUALS(p):
    ''' expr : EQUALS
    '''

def p_EQ(p):
    ''' expr : EQ
    '''

def p_FLOAT(p):
    ''' expr : FLOAT
    '''

def p_FLOAT_CONST(p):
    ''' expr : FLOAT_CONST
    '''

def p_FOR(p):
    ''' expr : FOR
    '''

def p_HE(p):
    ''' expr : HE
    '''

def p_HT(p):
    ''' expr : HT
    '''

def p_IF(p):
    ''' expr : IF
    '''

def p_INT(p):
    ''' expr : INT
    '''

def p_LBRACE(p):
    ''' expr : LBRACE
    '''

def p_LBRACKET(p):
    ''' expr : LBRACKET
    '''

def p_LE(p):
    ''' expr : LE
    '''

def p_LT(p):
    ''' expr : LT
    '''

def p_MINUS(p):
    ''' expr : MINUS
    '''

def p_MOD(p):
    ''' expr : MOD
    '''

def p_PLUSPLUS(p):
    ''' expr : PLUSPLUS
    '''

def p_RBRACE(p):
    ''' expr : RBRACE
    '''

def p_RBRACKET(p):
    ''' expr : RBRACKET
    '''

def p_READ(p):
    ''' expr : READ
    '''

def p_RETURN(p):
    ''' expr : RETURN
    '''

def p_SEMI(p):
    ''' expr : SEMI
    '''

def p_STRING(p):
    ''' expr : STRING
    '''

def p_VOID(p):
    ''' expr : VOID
    '''

def p_WHILE(p):
    ''' expr : WHILE
    '''

def p_MINUSMINUS(p):
    ''' expr : MINUSMINUS
    '''

def p_AND(p):
    ''' expr : AND
    '''

def p_OR(p):
    ''' expr : OR
    '''

def p_DIVIDEASSIGN(p):
    ''' expr : DIVIDEASSIGN
    '''

def p_TIMESASSIGN(p):
    ''' expr : TIMESASSIGN
    '''


def p_MODASSIGN(p):
    ''' expr : MODASSIGN
    '''


def p_PLUSASSIGN(p):
    ''' expr : PLUSASSIGN
    '''


def p_MINUSASSIGN(p):
    ''' expr : MINUSASSIGN
    '''

def p_UNARYDIFF(p):
    ''' expr : UNARYDIFF
    '''

def p_UNARYAND(p):
    ''' expr : UNARYAND
    '''





def p_compound_expr(p):
    ''' expr : LPAREN expr RPAREN
    '''
    p[0] = p[2]


def p_error (p):
    if p:
        print("Error near the symbol %s" % p.value)
    else:
        print("Error at the end of input")


precedence = (
    ('left', 'PLUS'),
    ('left', 'TIMES')
    )

parser = yacc(write_tables=False)
parser.parse('a = 3 * 4 + 5')

# parser.parse('a == 3')
