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
lexer.input(open(sys.argv[1]).read())
# for tok in lexer:
#     print(tok)
