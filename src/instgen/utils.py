#!/usr/bin/env python3

import re

from antlr4 import TerminalNode

TRIPLE_STRING_MATCH_REGEX = re.compile(r'^"""((.|\r?\n)*)"""', re.MULTILINE)
STRING_MATCH_REGEX = re.compile(r'"(.*)"')


def parse_string_node(node: TerminalNode) -> str:
    msg = str(node)
    if msg.startswith('"""'):
        parsed_msg = TRIPLE_STRING_MATCH_REGEX.match(msg)[1].strip()
    else:
        parsed_msg = STRING_MATCH_REGEX.match(msg)[1]
    return parsed_msg
