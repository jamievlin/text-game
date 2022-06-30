#!/usr/bin/env python3
import typing as ty

TLiteral = str | None | int
TValue = TLiteral


class DialogScriptVMContext:
    def __init__(self, gvar_template: dict[str, TValue] = None):
        self.alive = True
        self.module = 'start'
        self.instruction_ptr = 0

        self.mem_stack: ty.List[TValue] = []

        self.global_vars = \
            gvar_template.copy() \
                if gvar_template is not None \
                else {}

        self.local_vars: list[dict[str, TValue]] = [{}]

    def push(self, val):
        self.mem_stack.append(val)

    def pop(self) -> TValue:
        return self.mem_stack.pop()

    def load_var(self, var: str) -> TValue:
        if var in self.global_vars:
            return self.global_vars[var]

        for scope in reversed(self.local_vars):
            if var in scope:
                return scope[var]

        raise RuntimeError(f'Variable {var} not found in VM context!')

    def load_vars(self, variables: set[str]) -> dict[str, TValue]:
        vars_to_load = set(variables)
        result_vars = \
            {key: self.global_vars[key]
             for key in vars_to_load if key in self.global_vars}
        vars_to_load = {
            v
            for v in vars_to_load
            if v not in self.global_vars}

        for scope in reversed(self.local_vars):
            if not vars_to_load:
                return result_vars
            result_vars = \
                result_vars | \
                {key: scope[key] for key in vars_to_load
                 if key in scope}
            vars_to_load = {
                v
                for v in vars_to_load
                if v not in scope}

        if vars_to_load:
            unloaded_vars = ', '.join(vars_to_load)
            raise RuntimeError(f'Variables {unloaded_vars} cannot be loaded!')
        return result_vars

    def save_var(self, var: str, value: TValue):
        # saving rule:
        # save to highest context first, then globals
        # otherwise create a new variable in highest context
        for scope in reversed(self.local_vars):
            if var in scope:
                scope[var] = value
                return

        if var in self.global_vars:
            self.global_vars[var] = value
            return

        self.local_vars[-1][var] = value
