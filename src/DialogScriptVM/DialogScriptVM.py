#!/usr/bin/env python3
from .DialogScriptInstructions import *
from .DialogScriptVMContext import DialogScriptVMContext


class DialogScriptBlock:
    def __init__(self, instructions: list[DialogScriptInstruction]):
        self._instructions = instructions

    @property
    def instructions(self):
        return self._instructions


class DialogScriptProgram:
    def __init__(self, modules: list[tuple[str, DialogScriptBlock]]):
        self.modules: dict[str, DialogScriptBlock] = \
            {key: val for key, val in modules}


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
            inst = blk.instructions[self.context.instruction_ptr]
            self.context.instruction_ptr += 1

            inst.execute(self.context)


def main():
    dsb = DialogScriptBlock([
        DialogScriptSaysInst('sarah', 'hello traveler'),
        DialogScriptOptInst([
            DialogOption(1, "hello sarah"),
            DialogOption(2, "i'll be going")
        ]),
        DialogScriptGotoInst(4),
        DialogScriptGotoInst(6),
        DialogScriptSaysInst('sarah', 'hello traveler again'),
        DialogScriptGotoInst(8),
        DialogScriptExitInst(),
        DialogScriptGotoInst(8),
        DialogScriptSaysInst('sarah', 'goodbye'),
    ])
    dp = DialogScriptProgram([('start', dsb)])
    ds = DialogScriptVM(dp)
    ds.execute()
    pass


if __name__ == '__main__':
    # main()
    pass
