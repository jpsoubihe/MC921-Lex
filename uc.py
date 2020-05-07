#!/usr/bin/env python3
# ============================================================
# uc.py -- uC (a.k.a. micro C) language compiler
#
# This is the main program for the uc compiler, which just
# parses command-line options, figures out which source files
# to read and write to, and invokes the different stages of
# the compiler proper.
# ============================================================
import ast
import sys
from contextlib import contextmanager
from Parser import UCParser

"""
One of the most important (and difficult) parts of writing a compiler
is reliable reporting of error messages back to the user.  This file
defines some generic functionality for dealing with errors throughout
the compiler project. Error handling is based on a subscription/logging
based approach.

To report errors in uc compiler, we use the error() function. For example:

       error(lineno,"Some kind of compiler error message")

where lineno is the line number on which the error occurred.

Error handling is based on a subscription based model using context-managers
and the subscribe_errors() function. For example, to route error messages to
standard output, use this:

       with subscribe_errors(print):
            run_compiler()

To send messages to standard error, you can do this:

       import sys
       from functools import partial
       with subscribe_errors(partial(print,file=sys.stderr)):
            run_compiler()

To route messages to a logger, you can do this:

       import logging
       log = logging.getLogger("somelogger")
       with subscribe_errors(log.error):
            run_compiler()

To collect error messages for the purpose of unit testing, do this:

       errs = []
       with subscribe_errors(errs.append):
            run_compiler()
       # Check errs for specific errors

The utility function errors_reported() returns the total number of
errors reported so far.  Different stages of the compiler might use
this to decide whether or not to keep processing or not.

Use clear_errors() to clear the total number of errors.
"""

_subscribers = []
_num_errors = 0


def error(lineno, message, filename=None):
    """ Report a compiler error to all subscribers """
    global _num_errors
    if not filename:
        errmsg = "{}: {}".format(lineno, message)
    else:
        errmsg = "{}:{}: {}".format(filename,lineno,message)
    for subscriber in _subscribers:
        subscriber(errmsg)
    _num_errors += 1


def errors_reported():
    """ Return number of errors reported. """
    return _num_errors


def clear_errors():
    """ Clear the total number of errors reported. """
    global _num_errors
    _num_errors = 0


@contextmanager
def subscribe_errors(handler):
    """ Context manager that allows monitoring of compiler error messages.
        Use as follows where handler is a callable taking a single argument
        which is the error message string:

        with subscribe_errors(handler):
            ... do compiler ops ...
    """
    _subscribers.append(handler)
    try:
        yield
    finally:
        _subscribers.remove(handler)


class Compiler:
    """ This object encapsulates the compiler and serves as a
        facade interface for the compiler itself.
    """

    def __init__(self):
        self.total_errors = 0
        self.total_warnings = 0

    def _parse(self, susy, ast_file, debug):
        """ Parses the source code. If ast_file != None,
            or running at susy machine,
            prints out the abstract syntax tree.
        """
        self.parser = UCParser()
        self.ast = self.parser.parse(self.code, '', debug)
        if susy:
            self.ast.show(showcoord=True)
        elif ast_file is not None:
            self.ast.show(buf=ast_file, showcoord=True)

    def _do_compile(self, susy, ast_file, debug):
        """ Compiles the code to the given file object. """
        self._parse(susy, ast_file, debug)

    def compile(self, code, susy, ast_file, debug):
        """ Compiles the given code string """
        self.code = code
        with subscribe_errors(lambda msg: sys.stderr.write(msg+"\n")):
            self._do_compile(susy, ast_file, debug)
            if errors_reported():
                sys.stderr.write("{} error(s) encountered.".format(errors_reported()))
        return 0


def run_compiler():
    """ Runs the command-line compiler. """

    if len(sys.argv) < 2:
        print("Usage: ./uc.py <source-file> [-at-susy] [-no-ast] [-debug]")
        sys.exit(1)

    emit_ast = True
    susy = False
    debug = False

    params = sys.argv[1:]
    files = sys.argv[1:]

    for param in params:
        if param[0] == '-':
            if param == '-no-ast':
                emit_ast = False
            elif param == '-at-susy':
                susy = True
            elif param == '-debug':
                debug = True
            else:
                print("Unknown option: %s" % param)
                sys.exit(1)
            files.remove(param)

    for file in files:
        if file[-3:] == '.uc':
            source_filename = file
        else:
            source_filename = file + '.uc'

        open_files = []
        ast_file = None
        if emit_ast and not susy:
            ast_filename = source_filename[:-3] + '.ast'
            print("Outputting the AST to %s." % ast_filename)
            ast_file = open(ast_filename, 'w')
            open_files.append(ast_file)

        source = open(source_filename, 'r')
        code = source.read()
        source.close()

        retval = Compiler().compile(code, susy, ast_file, debug)
        for f in open_files:
            f.close()
        if retval != 0:
            sys.exit(retval)

    sys.exit(retval)

class NodeVisitor(object):
    """ A base NodeVisitor class for visiting uc_ast nodes.
        Subclass it and define your own visit_XXX methods, where
        XXX is the class name you want to visit with these
        methods.

        For example:

        class ConstantVisitor(NodeVisitor):
            def __init__(self):
                self.values = []

            def visit_Constant(self, node):
                self.values.append(node.value)

        Creates a list of values of all the constant nodes
        encountered below the given node. To use it:

        cv = ConstantVisitor()
        cv.visit(node)

        Notes:

        *   generic_visit() will be called for AST nodes for which
            no visit_XXX method was defined.
        *   The children of nodes for which a visit_XXX was
            defined will not be visited - if you need this, call
            generic_visit() on the node.
            You can use:
                NodeVisitor.generic_visit(self, node)
        *   Modeled after Python's own AST visiting facilities
            (the ast module of Python 3.0)
    """

    _method_cache = None

    def visit(self, node):
        """ Visit a node.
        """

        if self._method_cache is None:
            self._method_cache = {}

        visitor = self._method_cache.get(node.__class__.__name__, None)
        if visitor is None:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            self._method_cache[node.__class__.__name__] = visitor

        return visitor(node)

    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        for c in node:
            self.visit(c)


def _repr(obj):
    """
    Get the representation of an object, with dedicated pprint-like format for lists.
    """
    if isinstance(obj, list):
        return '[' + (',\n '.join((_repr(e).replace('\n', '\n ') for e in obj))) + '\n]'
    else:
        return repr(obj)


if __name__ == '__main__':
    run_compiler()