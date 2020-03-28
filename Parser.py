
from ply.yacc import yacc
from Lexer import UCLexer

class Parser:

    lexer = UCLexer()



    def p_statement_list(p):
        ''' statements : statements statement
                       | statement
        '''

    def p_assign_statement (p):
        ''' statement : ID EQ expr
        '''

    def p_print_statement (p):
        ''' statement : PRINT LPAREN expr RPAREN
        '''

    def p_binop_expr (p):
        ''' expr : expr PLUS expr
                 | expr TIMES expr
        '''

    def p_num_expr (p):
        ''' expr : NUM
        '''

    def p_name_expr (p):
        ''' expr : ID
        '''

    def p_compound_expr (p):
        ''' expr : LPAREN expr RPAREN
        '''

    parser = yacc(write_tables=False)

