#!/usr/bin/env python3
from . import instructions as inst
from .vm_context import DialogScriptVMContext


class DialogScriptBlock:
    def __init__(self, instructions: list[inst.DialogScriptInstruction]):
        self._instructions = instructions

    @property
    def instructions(self):
        return self._instructions


class DialogScriptProgram:
    def __init__(self, modules: list[tuple[str, DialogScriptBlock]]):
        self.modules: dict[str, DialogScriptBlock] = dict(modules)


class DialogScriptVM:
    def __init__(self, program: DialogScriptProgram):
        self._last_block = 'start'
        self.program = program
        self.context = DialogScriptVMContext()

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


def main():
    dsb = DialogScriptBlock([
        inst.DialogScriptSaysInst('sarah', 'hello traveler'),
        inst.DialogScriptOptInst([
            inst.DialogOption(1, "hello sarah"),
            inst.DialogOption(2, "i'll be going")
        ]),
        inst.DialogScriptGotoInst(4),
        inst.DialogScriptGotoInst(6),
        inst.DialogScriptSaysInst('sarah', 'hello traveler again'),
        inst.DialogScriptGotoInst(8),
        inst.DialogScriptExitInst(),
        inst.DialogScriptGotoInst(8),
        inst.DialogScriptSaysInst('sarah', 'goodbye'),
    ])
    dpr = DialogScriptProgram([('start', dsb)])
    dsc = DialogScriptVM(dpr)
    dsc.execute()


if __name__ == '__main__':
    # main()
    pass
