#!/usr/bin/env python
# coding: utf-8

# In[1]:

import ply.lex as lex


class UCLexer:
    """ A lexer for the uC language. After building it, set the
        input text with input(), and call token() to get new
        tokens.
    """

    def __init__(self, error_func):
        """ Create a new Lexer.
            An error function. Will be called with an error
            message, line and column as arguments, in case of
            an error during lexing.
        """
        self.error_func = error_func
        self.filename = ''

        # Keeps track of the last token returned from self.token()
        self.last_token = None

    def build(self, **kwargs):
        """ Builds the lexer from the specification. Must be
            called after the lexer object is created.

            This method exists separately, because the PLY
            manual warns against calling lex.lex inside __init__
        """
        self.lexer = lex.lex(object=self, **kwargs)

    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    def find_tok_column(self, token):
        """ Find the column of the token in its line.
        """
        last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
        return token.lexpos - last_cr

    # Internal auxiliary methods
    def _error(self, msg, token):
        location = self._make_tok_location(token)
        self.error_func(msg, location[0], location[1])
        self.lexer.skip(1)

    def _make_tok_location(self, token):
        return token.lineno, self.find_tok_column(token)

    # Reserved keywords
    keywords = (
        'CHAR', 'FLOAT', 'INT', 'VOID',
        'IF', 'ELSE', 'WHILE', 'FOR',
        'PRINT', 'READ',
        'BREAK', 'RETURN', 'ASSERT'
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
        'INT_CONST', 'FLOAT_CONST', 'CHAR_CONST', 'STRING',
        # symbols
        'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', 'COMMA', 'SEMI',
        # operators
        'EQUALS', 'EQ', 'NOT', 'NOT_EQUAL', 'PLUS', 'PLUSPLUS', 'PLUS_EQUALS', 'MINUS', 'MINUSMINUS', 'MINUS_EQUALS',
        'TIMES', 'TIMES_EQUALS', 'DIV', 'DIV_EQUALS', 'MOD', 'MOD_EQUALS', 'GT', 'GTE', 'LT', 'LTE', 'AND', 'OR',
        'ADDRESS'
    )

    #
    # Rules
    #
    t_ignore = ' \t'
    t_LPAREN = '\('
    t_RPAREN = '\)'
    t_LBRACKET = '\['
    t_RBRACKET = '\]'
    t_LBRACE = '\{'
    t_RBRACE = '\}'
    t_COMMA = ','
    t_SEMI = ';'
    t_EQ = '=='
    t_EQUALS = '='
    t_NOT_EQUAL = '\!='
    t_NOT = '\!'
    t_PLUSPLUS = '\+\+'
    t_PLUS_EQUALS = '\+='
    t_MINUSMINUS = '--'
    t_PLUS = '\+'
    t_MINUS_EQUALS = '-='
    t_MINUS = '-'
    t_TIMES_EQUALS = '\*='
    t_TIMES = '\*'
    t_DIV_EQUALS = '/='
    t_DIV = '/'
    t_MOD_EQUALS = '%='
    t_MOD = '%'
    t_GTE = '>='
    t_GT = '>'
    t_LTE = '<='
    t_LT = '<'
    t_AND = '&&'
    t_OR = '\|\|'
    t_ADDRESS = '&'

    def t_comment(self, t):
        r'(/\*(.|\n)*\*/)|(//.*)'
        t.lexer.lineno += t.value.count('\n')

    # Newlines
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_ID(self, t):
        r'[a-zA-Z_][0-9a-zA-Z_]*'
        t.type = self.keyword_map.get(t.value, "ID")
        return t

    def t_STRING(self, t):
        r'\".*\"'
        t.type = self.keyword_map.get(t.value, "STRING")
        return t

    def t_CHAR_CONST(self, t):
        r'\'.{1}\''
        t.type = self.keyword_map.get(t.value, "CHAR_CONST")
        return t

    def t_FLOAT_CONST(self, t):
        r'([0-9]*[.][0-9]+)|([0-9]+[.][0-9]*)'
        t.type = self.keyword_map.get(t.value, "FLOAT_CONST")
        return t

    def t_INT_CONST(self, t):
        r'[0-9]+'
        t.type = self.keyword_map.get(t.value, "INT_CONST")
        return t

    def t_error(self, t):
        msg = "Illegal character %s" % repr(t.value[0])
        self._error(msg, t)

    # Scanner (used only for test)
    def scan(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)


if __name__ == '__main__':
    import sys


    def print_error(msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y))


    m = UCLexer(print_error)
    m.build()  # Build the lexer
    m.scan(open(sys.argv[1]).read())  # print tokens
