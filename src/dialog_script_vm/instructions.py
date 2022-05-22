#!/usr/bin/env python3

from abc import ABC, abstractmethod
import typing as ty
from .vm_context import DialogScriptVMContext, TLiteral




class DialogOption:
    def __init__(self, number: int, text: str):
        self.number = number
        self.text = text


class DialogScriptInstruction(ABC):
    @abstractmethod
    def execute(self, prog: DialogScriptVMContext):
        pass


class DialogScriptSaysInst(DialogScriptInstruction):
    def __init__(self, character: str, text: str):
        self.character = character
        self.text = text

    def execute(self, prog: DialogScriptVMContext):
        print(f'{self.character}:')
        print(f'{self.text}')


class DialogScriptExitInst(DialogScriptInstruction):
    def execute(self, prog: DialogScriptVMContext):
        prog.alive = False


class DialogScriptGotoModuleInst(DialogScriptInstruction):
    def __init__(self, module):
        self.module = module

    def execute(self, prog: DialogScriptVMContext):
        prog.module = self.module
        prog.instruction_ptr = 0


class DialogScriptGotoInst(DialogScriptInstruction):
    def __init__(self, instruction_ptr: int):
        self.instruction_ptr = instruction_ptr

    def execute(self, prog: DialogScriptVMContext):
        prog.instruction_ptr = self.instruction_ptr


class DialogScriptGotoOffsetInst(DialogScriptInstruction):
    def __init__(self, offset: int):
        self.offset = offset

    def execute(self, prog: DialogScriptVMContext):
        prog.instruction_ptr += self.offset


class DialogScriptNop(DialogScriptInstruction):
    def __init__(self):
        pass

    def execute(self, prog: DialogScriptVMContext):
        pass


class DialogScriptPushLiteral(DialogScriptInstruction):
    def __init__(self, literal: TLiteral):
        self._literal = literal

    def execute(self, prog: DialogScriptVMContext):
        prog.push(self._literal)


class DialogScriptLoadVar(DialogScriptInstruction):
    """
    Load a variable to the stack
    """
    def __init__(self, var: str):
        self._var = var

    def execute(self, prog: DialogScriptVMContext):
        val = prog.load_var(self._var)
        prog.push(val)


class DialogScriptWriteVar(DialogScriptInstruction):
    """
    Load a variable to the stack
    """
    def __init__(self, var: str):
        self._var = var

    def execute(self, prog: DialogScriptVMContext):
        val = prog.pop()
        prog.save_var(self._var, val)

class DialogScriptPop(DialogScriptInstruction):
    def execute(self, prog: DialogScriptVMContext):
        prog.mem_stack.pop()


class DialogScriptPopMulti(DialogScriptInstruction):
    def __init__(self, count: int):
        if count <= 0:
            raise RuntimeError('Must pop a positive amount')
        self.count = count

    def execute(self, prog: DialogScriptVMContext):
        del prog.mem_stack[-self.count:]


class DialogScriptOptInst(DialogScriptInstruction):
    def __init__(self, options: ty.List[DialogOption]):
        self.options = options

    def execute(self, prog: DialogScriptVMContext):
        for i, option in enumerate(self.options):
            print(f'{i + 1})')
            print('  ' + option.text)
        i = None
        while i is None:
            try:
                i = int(input('Your Choice: '))
            except (TypeError, ValueError):
                print('Invalid input')
                continue
            if i is None or not 1 <= i <= len(self.options):
                print('Invalid input')
                i = None
        prog.instruction_ptr += (i - 1)
