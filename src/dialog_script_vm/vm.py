#!/usr/bin/env python3
import typing as ty

from . import instructions as inst
from .vm_context import DialogScriptVMContext, TValue


class DialogScriptBlock:
    _T = ty.TypeVar('_T', bound='DialogScriptBlock')

    def __init__(
            self,
            instructions: ty.Optional[
                list[inst.DialogScriptInstruction]] = None
    ):
        self._instructions = instructions or []

    @property
    def instructions(self):
        return self._instructions

    def add_instruction(self, instruction: inst.DialogScriptInstruction):
        self._instructions.append(instruction)

    def add_instructions(
            self,
            instructions: ty.Iterable[inst.DialogScriptInstruction]
    ):
        self._instructions.extend(instructions)

    def extend_dsb(self, dsb: _T):
        self._instructions.extend(dsb.instructions)


class DialogScriptProgram:
    def __init__(
            self,
            modules: list[tuple[str, DialogScriptBlock]] = None,
            gvar_template: dict[str, TValue] = None
    ):
        modules = modules or []
        gvar_template = gvar_template or {}
        self.modules: dict[str, DialogScriptBlock] = dict(modules)
        self.gvar_template = gvar_template


class DialogScriptVM:
    def __init__(self, program: DialogScriptProgram):
        self._last_block = 'start'
        self.program = program
        self.context = DialogScriptVMContext(program.gvar_template)

    def execute(self):
        while self.context.alive:
            blk = self.program.modules[self.context.module]
            if self.context.instruction_ptr >= len(blk.instructions):
                if self.context.module == self._last_block:
                    return
                raise NotImplementedError('Implement module fallthrough!')
            instr = blk.instructions[self.context.instruction_ptr]
            self.context.instruction_ptr += 1

            instr.execute(self.context)
