from ply.yacc import yacc
from pack.lex import UCLexer
from pack import ast
import sys


class UCParser:
    def __init__(self, lexer=UCLexer, yacc_optimize=True):
        self.uclex = lexer(error_func=print_error)
        self.uclex.build()
        self.tokens = self.uclex.tokens

        self.ucparser = yacc(module=self, optimize=yacc_optimize)
        self._scope_stack = [dict()]
        self._last_yielded_token = None

    def parse(self, text, filename='', debuglevel=0):
        """ Parses C code and returns an AST.
            text:
                A string containing the C source code
            filename:
                Name of the file being parsed (for meaningful
                error messages)
            debuglevel:
                Debug level to yacc
        """
        self.uclex.filename = filename
        self.uclex.reset_lineno()
        self._scope_stack = [dict()]
        self._last_yielded_token = None
        return self.ucparser.parse(
            input=text,
            lexer=self.uclex,
            debug=debuglevel)

    def _coord(self, lineno, column=None):
        return ast.Coord(
            line=lineno,
            column=column)

    def _token_coord(self, p, token_idx):
        """ Returns the coordinates for the YaccProduction objet 'p' indexed
            with 'token_idx'. The coordinate includes the 'lineno' and
            'column'. Both follow the lex semantic, starting from 1.
        """
        last_cr = p.lexer.lexer.lexdata.rfind('\n', 0, p.lexpos(token_idx))
        if last_cr < 0:
            last_cr = -1
        column = (p.lexpos(token_idx) - last_cr)
        return self._coord(p.lineno(token_idx), column)

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NOT_EQUAL'),
        ('left', 'GT', 'GTE', 'LT', 'LTE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIV', 'MOD')
    )

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

        if not typename:
            # Functions default to returning int
            if not isinstance(decl.type, ast.FuncDecl):
                self._parse_error("Missing type in declaration", decl.coord)
            type.type = ast.Type(['int'], coord=decl.coord)
        else:
            # At this point, we know that typename is a list of Type
            # nodes. Concatenate all the names into a single list.
            for tn in typename:
                if not isinstance(tn, ast.Type):
                    if len(typename) > 1:
                        self._parse_error(
                            "Invalid multiple types specified", tn.coord)
                    else:
                        type.type = tn
                        return decl
            type.type = ast.Type(
                [typename.names[0]],
                coord=typename.coord)
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
                init=decl.get('init'))

            fixed_decl = self._fix_decl_name_type(declaration, spec)
            declarations.append(fixed_decl)

        return declarations

    def _build_function_definition(self, spec, decl, body):
        """ Builds a function definition.
        """
        declaration = self._build_declarations(
            spec=spec,
            decls=[dict(decl=decl, init=None)])[0]

        return ast.FuncDef(
            type=declaration.type.type.type,
            decl=declaration,
            body=body)

    def _type_modify_decl(self, decl, modifier):
        """ Tacks a type modifier on a declarator, and returns
            the modified declarator.
            Note: the declarator and modifier may be modified
            :param decl:
            :param modifier:
            :return:
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

    def p_program(self, p):
        # <program> ::= {<global_declaration>}+
        """
        program : global_declaration_list
        """
        p[0] = ast.Program(p[1])

    def p_global_declaration_list(self, p):
        """
        global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_global_declaration_1(self, p):
        """
        global_declaration : function_definition
        """
        p[0] = p[1]

    def p_function_definition(self, p):
        # <function_definition> ::= {<type_specifier>}? <declarator> {<declaration>}* <compound_statement>
        """
        function_definition : type_specifier_opt declarator compound_statement
        """
        p[0] = self._build_function_definition(
            spec=p[1],
            decl=p[2],
            body=p[3])

    def p_global_declaration_2(self, p):
        """
        global_declaration : declaration
        """
        p[0] = ast.GlobalDecl(decl=p[1][0])

    def p_type_specifier_opt(self, p):
        """
        type_specifier_opt : type_specifier
                           | empty
        """
        p[0] = p[1]

    def p_declaration_list(self, p):
        """
        declaration_list : declaration
                        | declaration_list declaration
        """
        if len(p) == 2:
            decls = [p[1]]
        else:
            decls = p[1] + [p[2]]

        p[0] = ast.DeclList(decls, coord=self._token_coord(p, 1))

    def p_type_specifier(self, p):
        # <type_specifier> ::= void
        #                    | char
        #                    | int
        #                    | float
        """
        type_specifier : VOID
                        | CHAR
                        | INT
                        | FLOAT
        """
        p[0] = ast.Type([p[1]], coord=self._token_coord(p, 1))

    def p_declarator(self, p):
        # <declarator> ::= {<pointer>}? <direct_declarator>
        """
        declarator : pointer direct_declarator
                   | direct_declarator
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = self._type_modify_decl(decl=p[2], modifier=p[1])

    def p_pointer(self, p):
        # <pointer> ::= * {<pointer>}?
        """ pointer : TIMES
                    | TIMES pointer
        """
        coord = self._token_coord(p, 1)

        p[0] = ast.PtrDecl(type=None, coord=coord)

    def p_constant_expression_opt(self, p):
        """
        constant_expression_opt : constant_expression
                                | empty
        """
        p[0] = p[1]

    def p_direct_declarator_1(self, p):
        """
        direct_declarator : LPAREN declarator RPAREN
        """
        p[0] = p[2]

    def p_direct_declarator_2(self, p):
        """
        direct_declarator : direct_declarator LBRACKET constant_expression_opt RBRACKET
        """
        arr = ast.ArrayDecl(
            type=None,
            dim=p[3])

        p[0] = self._type_modify_decl(decl=p[1], modifier=arr)

    def p_direct_declarator_3(self, p):
        """
        direct_declarator : direct_declarator LPAREN parameter_list RPAREN
        """
        func = ast.FuncDecl(
            type=None,
            args=p[3]
        )

        p[0] = self._type_modify_decl(decl=p[1], modifier=func)

    def p_direct_declarator_4(self, p):
        """
        direct_declarator : direct_declarator LPAREN identifier_list_opt RPAREN
        """
        func = ast.FuncDecl(args=p[3], type=None)

        p[0] = self._type_modify_decl(decl=p[1], modifier=func)

    def p_direct_declarator_0(self, p):
        # <direct_declarator> ::= <identifier>
        #                       | ( <declarator> )
        #                       | <direct_declarator> [ {<constant_expression>}? ]
        #                       | <direct_declarator> ( <parameter_list> )
        #                       | <direct_declarator> ( {<ID>}* )
        """
        direct_declarator : identifier
        """
        p[0] = ast.VarDecl(p[1], None)

    def p_identifier_list_opt(self, p):
        """
        identifier_list_opt : identifier_list
                            | empty
        """
        p[0] = p[1]

    def p_identifier_list(self, p):
        """
        identifier_list : identifier
                        | identifier_list identifier
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_identifier(self, p):
        """
        identifier : ID
        """
        p[0] = ast.ID(p[1], self._token_coord(p, 1))

    def p_constant_expression(self, p):
        # <constant_expression> ::= <binary_expression>
        """
        constant_expression : binary_expression
        """
        p[0] = p[1]

    def p_binary_expression_1(self, p):
        """
        binary_expression : cast_expression
        """
        p[0] = p[1]

    def p_binary_expression_2(self, p):
        """
        binary_expression : binary_expression TIMES binary_expression
                        | binary_expression DIV binary_expression
                        | binary_expression MOD binary_expression
                        | binary_expression PLUS binary_expression
                        | binary_expression MINUS binary_expression
                        | binary_expression LT binary_expression
                        | binary_expression LTE binary_expression
                        | binary_expression GT binary_expression
                        | binary_expression GTE binary_expression
                        | binary_expression EQ binary_expression
                        | binary_expression NOT_EQUAL binary_expression
                        | binary_expression AND binary_expression
                        | binary_expression OR binary_expression
        """
        p[0] = ast.BinaryOp(op=p[2], left=p[1], right=p[3], coord=p[1].coord)

    def p_cast_expression_1(self, p):
        """
        cast_expression : unary_expression
        """
        p[0] = p[1]

    def p_cast_expression_2(self, p):
        """
        cast_expression : LPAREN type_specifier RPAREN cast_expression
        """
        p[0] = ast.Cast(to_type=p[2], expr=p[4], coord=self._token_coord(p, 1))

    def p_unary_expression(self, p):
        # <unary_expression> ::= <postfix_expression>
        #                      | ++ <unary_expression>
        #                      | -- <unary_expression>
        #                      | <unary_operator> <cast_expression>
        """
        unary_expression : postfix_expression
                        | PLUSPLUS unary_expression
                        | MINUSMINUS unary_expression
                        | unary_operator cast_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.UnaryOp(op=p[1], expr=p[2], coord=p[2].coord)

    def p_postfix_expression_1(self, p):
        # <postfix_expression> ::= <primary_expression>
        #                        | <postfix_expression> [ <expression> ]
        #                        | <postfix_expression> ( {<argument_expression>}? )
        #                        | <postfix_expression> ++
        #                        | <postfix_expression> --
        """
        postfix_expression : primary_expression
        """
        p[0] = p[1]

    def p_postfix_expression_2(self, p):
        """
        postfix_expression : postfix_expression LBRACKET expression RBRACKET
        """
        p[0] = ast.ArrayRef(p[1], p[3], coord=p[1].coord)

    def p_postfix_expression_3(self, p):
        """
        postfix_expression : postfix_expression LPAREN argument_expression RPAREN
                        | postfix_expression LPAREN RPAREN
        """
        p[0] = ast.FuncCall(p[1], p[3] if len(p) == 5 else None, coord=p[1].coord)

    def p_postfix_expression_4(self, p):
        """
        postfix_expression : postfix_expression PLUSPLUS
                        | postfix_expression MINUSMINUS
        """
        p[0] = ast.UnaryOp('p' + p[2], p[1], p[1].coord)

    def p_string_constant(self, p):
        """
        string_constant : STRING
        """
        p[0] = ast.Constant('string', p[1], self._token_coord(p, 1))

    def p_primary_expression_1(self, p):
        """
        primary_expression : identifier
                           | constant
                           | string_constant
        """
        p[0] = p[1]

    def p_primary_expression_2(self, p):
        """
        primary_expression : LPAREN expression RPAREN
        """
        p[0] = p[2]

    def p_constant_1(self, p):
        # <constant> ::= <integer_constant>
        #              | <character_constant>
        #              | <floating_constant>
        """
        constant : INT_CONST
        """
        p[0] = ast.Constant('int', p[1], self._token_coord(p, 1))

    def p_constant_2(self, p):
        """
        constant : CHAR_CONST
        """
        p[0] = ast.Constant('char', p[1], self._token_coord(p, 1))

    def p_constant_3(self, p):
        """
        constant : FLOAT_CONST
        """
        p[0] = ast.Constant('float', p[1], self._token_coord(p, 1))

    def p_expression(self, p):
        # <expression> ::= <assignment_expression>
        #                | <expression> , <assignment_expression>
        """
        expression : assignment_expression
                   | expression COMMA assignment_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1], ast.ExprList):
                p[1] = ast.ExprList([p[1]], p[1].coord)

            p[1].exprs.append(p[3])
            p[0] = p[1]

    def p_argument_expression(self, p):
        # <argument_expression> ::= <assignment_expression>
        #                         | <argument_expression> , <assignment_expression>
        """
        argument_expression : assignment_expression
                            | argument_expression COMMA assignment_expression
        """
        if len(p) == 2:
            p[0] = ast.ExprList([p[1]], p[1].coord)
        else:
            p[1].exprs.append(p[3])
            p[0] = p[1]

    def p_assignment_expression(self, p):
        # <assignment_expression> ::= <binary_expression>
        #                           | <unary_expression> <assignment_operator> <assignment_expression>
        """
        assignment_expression : binary_expression
                            | unary_expression assignment_operator assignment_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Assignment(p[2], p[1], p[3], p[1].coord)

    def p_assignment_operator(self, p):
        # <assignment_operator> ::= =
        #                         | *=
        #                         | /=
        #                         | %=
        #                         | +=
        #                         | -=
        """
        assignment_operator : EQUALS
                            | TIMES_EQUALS
                            | DIV_EQUALS
                            | MOD_EQUALS
                            | PLUS_EQUALS
                            | MINUS_EQUALS
        """
        p[0] = p[1]

    def p_unary_operator(self, p):
        # <unary_operator> ::= &
        #                    | *
        #                    | +
        #                    | -
        #                    | !
        """
        unary_operator : ADDRESS
                       | TIMES
                       | PLUS
                       | MINUS
                       | NOT
        """
        p[0] = p[1]

    def p_parameter_list(self, p):
        # <parameter_list> ::= <parameter_declaration>
        #                    | <parameter_list> , <parameter_declaration>
        """
        parameter_list : parameter_declaration
                        | parameter_list COMMA parameter_declaration
        """
        if len(p) == 2:  # single parameter
            p[0] = ast.ParamList([p[1]], p[1].coord)
        else:
            p[1].params.append(p[3])
            p[0] = p[1]

    def p_parameter_declaration(self, p):
        # <parameter_declaration> ::= <type_specifier> <declarator>
        """
        parameter_declaration : type_specifier declarator
        """
        spec = p[1]
        # if not spec['type']:
        #     spec['type'] = [ast.Type(['int'], coord=self._token_coord(p, 1))]

        p[0] = self._build_declarations(
            spec=spec,
            decls=[dict(decl=p[2])])[0]

    def p_decl_body(self, p):
        """ decl_body : type_specifier_opt init_declarator_list_opt
        """
        spec = p[1]
        if p[2] is None:
            decls = self._build_declarations(
                spec=spec,
                decls=[dict(decl=None, init=None)])

        else:
            decls = self._build_declarations(
                spec=spec,
                decls=p[2])

        p[0] = decls

    def p_declaration(self, p):
        """ declaration : decl_body SEMI
        """
        p[0] = p[1]

    def p_init_declarator_list_opt(self, p):
        """
        init_declarator_list_opt : init_declarator_list
                                 | empty
        """
        p[0] = p[1]

    def p_init_declarator_list_1(self, p):
        # <init_declarator_list> ::= <init_declarator>
        #                          | <init_declarator_list> , <init_declarator>
        """
        init_declarator_list : init_declarator
        """
        p[0] = [p[1]]

    def p_init_declarator_list_2(self, p):
        """
        init_declarator_list : init_declarator_list COMMA init_declarator
        """
        p[0] = p[1] + [p[3]]

    def p_init_declarator(self, p):
        # <init_declarator> ::= <declarator>
        #                     | <declarator> = <initializer>
        """
        init_declarator : declarator
                        | declarator EQUALS initializer
        """
        p[0] = dict(decl=p[1], init=(p[3] if len(p) > 2 else None))

    def p_initializer_1(self, p):
        # <initializer> ::= <assignment_expression>
        #                 | { <initializer_list> }
        #                 | { <initializer_list> , }
        """
        initializer : assignment_expression
        """
        p[0] = p[1]

    def p_initializer_2(self, p):
        """
        initializer : LBRACE initializer_list RBRACE
                    | LBRACE initializer_list COMMA RBRACE
        """
        if p[2] is None:
            p[0] = ast.InitList([], self._token_coord(p, 1))
        else:
            p[0] = p[2]

    def p_initializer_list(self, p):
        # <initializer_list> ::= <initializer>
        #                      | <initializer_list> , <initializer>
        """
        initializer_list : initializer
                        | initializer_list COMMA initializer
        """
        if len(p) == 2:
            p[0] = ast.InitList(exprs=[p[1]], coord=p[1].coord)
        else:
            p[1].exprs.append(p[3])
            p[0] = p[1]

    def p_compound_statement(self, p):
        # <compound_statement> ::= { {<declaration>}* {<statement>}* }
        """
        compound_statement : LBRACE block_item_list_opt RBRACE
        """
        token_coord = self._token_coord(p, 1)
        token_coord.column = 1;
        p[0] = ast.Compound(block_items=p[2], coord=token_coord)

    def p_block_item_list_opt(self, p):
        """
        block_item_list_opt : block_item_list
                            | empty
        """
        p[0] = p[1]

    def p_block_item_list(self, p):
        """
        block_item_list : block_item
                        | block_item_list block_item
        """
        p[0] = p[1] if (len(p) == 2 or p[2] == [None]) else p[1] + p[2]

    def p_block_item(self, p):
        """
        block_item : statement
                   | declaration
        """
        p[0] = p[1] if isinstance(p[1], list) else [p[1]]

    def p_statement(self, p):
        # <statement> ::= <expression_statement>
        #               | <compound_statement>
        #               | <selection_statement>
        #               | <iteration_statement>
        #               | <jump_statement>
        #               | <assert_statement>
        #               | <print_statement>
        #               | <read_statement>
        """
        statement : expression_statement
                | compound_statement
                | selection_statement
                | iteration_statement
                | jump_statement
                | assert_statement
                | print_statement
                | read_statement
        """
        p[0] = p[1]

    def p_expression_statement(self, p):
        # <expression_statement> ::= {<expression>}? ;
        """
        expression_statement : expression_opt SEMI
        """
        p[0] = p[1]

    def p_expression_opt(self, p):
        """
        expression_opt : expression
                       | empty
        """
        p[0] = p[1]

    def p_selection_statement_1(self, p):
        # <selection_statement> ::= if ( <expression> ) <statement>
        #                         | if ( <expression> ) <statement> else <statement>
        """
        selection_statement : IF LPAREN expression RPAREN statement
        """
        p[0] = ast.If(p[3], p[5], None, self._token_coord(p, 1))

    def p_selection_statement_2(self, p):
        """
        selection_statement : IF LPAREN expression RPAREN statement ELSE statement
        """
        p[0] = ast.If(p[3], p[5], p[7], self._token_coord(p, 1))

    def p_iteration_statement_1(self, p):
        """
        iteration_statement : WHILE LPAREN expression RPAREN statement
        """
        p[0] = ast.While(p[3], p[5], self._token_coord(p, 1))

    def p_iteration_statement_0(self, p):
        """
        iteration_statement : FOR LPAREN declaration expression_opt SEMI expression_opt RPAREN statement
        """
        p[0] = ast.For(init=ast.DeclList(decls=p[3], coord=self._token_coord(p, 1)),
                       cond=p[4], next=p[6], stmt=p[8], coord=self._token_coord(p, 1))

    def p_iteration_statement_2(self, p):
        """
        iteration_statement : FOR LPAREN expression_opt SEMI expression_opt SEMI expression_opt RPAREN statement
        """
        p[0] = ast.For(init=p[3], cond=p[5], next=p[7], stmt=p[9], coord=self._token_coord(p, 1))

    def p_jump_statement_1(self, p):
        # <jump_statement> ::= break ;
        #                    | return {<expression>}? ;
        """
        jump_statement : BREAK SEMI
        """
        p[0] = ast.Break(self._token_coord(p, 1))

    def p_jump_statement_2(self, p):
        """
        jump_statement : RETURN expression SEMI
                    | RETURN SEMI
        """
        p[0] = ast.Return(p[2] if len(p) == 4 else None, self._token_coord(p, 1))

    def p_assert_statement(self, p):
        # <assert_statement> ::= assert <expression> ;
        """
        assert_statement : ASSERT expression SEMI
        """
        p[0] = ast.Assert(p[2], self._token_coord(p, 1))

    def p_print_statement(self, p):
        # <print_statement> ::= print ( {<expression>}? ) ;
        """
        print_statement : PRINT LPAREN expression_opt RPAREN SEMI
        """
        p[0] = ast.Print(p[3], self._token_coord(p, 1))

    def p_read_statement(self, p):
        # <read_statement> ::= read ( <argument_expression> ) ;
        """
        read_statement : READ LPAREN argument_expression RPAREN SEMI
        """
        p[0] = ast.Read(p[3], self._token_coord(p, 1))

    def p_empty(self, p):
        """
        empty :
        """
        pass

    def p_error(self, p):
        if p:
            print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")


def print_error(msg, x, y):
    print("Lexical error: %s at %d:%d" % (msg, x, y))


if __name__ == '__main__':
    parser = UCParser()
    parser.parse(open(sys.argv[1]).read(), sys.argv[1]).show()