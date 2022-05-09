#!/usr/bin/env python3

class DialogScriptVMContext:
    def __init__(self):
        self.alive = True
        self.module = 'start'
        self.instruction_ptr = 0

        self.mem_stack = []

    def push(self, val):
        self.mem_stack.append(val)

    def pop(self):
        self.mem_stack.pop()
