#!/usr/bin/env python3
import re
import typing as ty

from .vm_context import DialogScriptVMContext

RE_MATCH_VARTEMPLATE = \
    re.compile(r'(?P<pref>^|[^\\])(?P<var>\$(?P<varname>[a-zA-Z_]\w*))')


def process_template_text(text: str, prog: DialogScriptVMContext) -> str:
    var_names = RE_MATCH_VARTEMPLATE.findall(text)
    var_sets = {v[2] for v in var_names}
    variables = prog.load_vars(var_sets)

    def match_vars(match_obj: ty.Match):
        # the pref is to preserve the prefix of the original string
        # in case the match happpens (for example, hello$var), prefix is "o"
        # in "hello". Say var is 500, this function would return o500,
        # as the text "o$var" is replaced by "o500".
        return match_obj.group('pref') + variables[match_obj.group('varname')]

    return RE_MATCH_VARTEMPLATE.sub(match_vars, text)
