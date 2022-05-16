#!/usr/bin/env python3
import antlr4

from dialog_script_vm.vm import DialogScriptProgram
from generated.dialog_script.DialogScriptLexer import DialogScriptLexer
from generated.dialog_script.DialogScriptParser import DialogScriptParser
from .ds_instgen import DialogScriptMainVisitor


def program_from_file(filename: str, encoding: str = 'UTF-8') -> \
        DialogScriptProgram:
    """
    This function generates a DialogScript VM from a given file

    :param filename: name of input file
    :param encoding: Encoding of the file, defaults to UTF-8
    :return: A DialogScriptProgram that can be executed in a VM
    """
    with open(filename, 'r', encoding=encoding) as infile:
        istream = antlr4.InputStream(infile.read())
        lexer = DialogScriptLexer(istream)
    tokens = antlr4.CommonTokenStream(lexer)
    parser = DialogScriptParser(tokens)
    visitor = DialogScriptMainVisitor()

    return visitor.visit(parser.root())
