#!/usr/bin/env python3

import typing as ty

import dialog_script_vm.instructions as inst
from dialog_script_vm.vm import DialogScriptProgram, DialogScriptBlock
from generated.dialog_script.DialogScriptParser import DialogScriptParser
from generated.dialog_script.DialogScriptVisitor import DialogScriptVisitor
from .utils import parse_string_node


class DialogScriptMainVisitor(DialogScriptVisitor):
    def __init__(self):
        self._program_blocks: list[ty.Tuple[str, DialogScriptBlock]] = []
        self._gvar_template: dict[str, any] = {}
        self.processed = False

    @property
    def program(self):
        if not self.processed:
            raise RuntimeWarning('Program is not yet processed')
        return DialogScriptProgram(self._program_blocks, self._gvar_template)

    @property
    def gvar_template(self):
        if not self.processed:
            raise RuntimeWarning('Program is not yet processed')
        return self._gvar_template

    def visitRoot(self, ctx: DialogScriptParser.RootContext):
        gstm: DialogScriptParser.Global_stmContext
        for gstm in ctx.global_stm():
            gstm.accept(self)
        self.processed = True

    def visitProcessBlock(self, ctx: DialogScriptParser.ProcessBlockContext):
        block: DialogScriptParser.BlockContext = ctx.block()
        block_name = str(block.IDENTIFIER())
        block_inst = block.accept(DialogScriptBlockVisitor())
        self._program_blocks.append((block_name, block_inst))

    def visitProcessGlobalVarDecs(
            self,
            ctx: DialogScriptParser.ProcessGlobalVarDecsContext):
        lit_vardec: DialogScriptParser.LitvardecsContext = ctx.litvardecs()
        name = str(lit_vardec.IDENTIFIER())

        if name in self._gvar_template:
            raise RuntimeError('Name cannot be duplicate!')

        init_val = None
        if lit_vardec.EQ_ASSIGN() is not None:
            # there's an assignment
            init_val = lit_vardec.literal().accept(
                DialogScriptLiteralVisitor())
        self._gvar_template[name] = init_val


class DialogScriptLiteralVisitor(DialogScriptVisitor):
    def visitLiteral(self, ctx: DialogScriptParser.LiteralContext):
        if ctx.NUMBERS() is not None:
            return int(str(ctx.NUMBERS()))
        elif ctx.BOOLEAN_CONST() is not None:
            match ctx.getText():
                case 'true':
                    return True
                case 'false':
                    return False
                case _:
                    raise ValueError('Boolean value must be TRUE|FALSE')
        elif ctx.STRING_LIT() is not None:
            return parse_string_node(ctx.STRING_LIT())
        else:
            raise RuntimeError('Literal should have a value!')


class DialogScriptBlockVisitor(DialogScriptVisitor):
    def visitBlock(
            self,
            ctx: DialogScriptParser.BlockContext) -> \
            DialogScriptBlock:
        diag_script_block = DialogScriptBlock([])
        for stm in \
                ctx.statement():  # type: DialogScriptParser.StatementContext
            # A major invariant is that by the time we reach each statement,
            # the diag_script_block contains all needed instructions of the
            # preceding statements
            stm.accept(StatementVisitor(diag_script_block))
        return diag_script_block


class StatementVisitor(DialogScriptVisitor):
    def __init__(self, dialog_script_block: DialogScriptBlock):
        self.dialog_script_block = dialog_script_block

    def visitStatement(self, ctx: DialogScriptParser.StatementContext):
        insts: \
            list[inst.DialogScriptInstruction] \
            | inst.DialogScriptInstruction \
            | DialogScriptBlock \
            | None \
            = None

        if ctx.goto() is not None:
            goto = ctx.goto()  # type: DialogScriptParser.GotoContext
            module_txt = str(goto.IDENTIFIER())
            insts = inst.DialogScriptGotoModuleInst(module_txt)
        elif ctx.say() is not None:
            insts = ctx.say().accept(SayVisitor())
        elif ctx.opts() is not None:
            insts = ctx.opts().accept(OptionsVisitor())
        elif ctx.NOP() is not None:
            insts = inst.DialogScriptNop()
        elif ctx.assignment() is not None:
            insts = ctx.assignment().accept(AssignmentVisitor())
        elif ctx.EXIT() is not None:
            insts = inst.DialogScriptExitInst()

        if isinstance(insts, list):
            self.dialog_script_block.add_instructions(insts)
        elif isinstance(insts, inst.DialogScriptInstruction):
            self.dialog_script_block.add_instruction(insts)
        elif isinstance(insts, DialogScriptBlock):
            self.dialog_script_block.extend_dsb(insts)


class AssignmentVisitor(DialogScriptVisitor):
    def visitAssignment(self, ctx:DialogScriptParser.AssignmentContext):
        var = str(ctx.IDENTIFIER())
        insts = ctx.value().accept(ValuePushVisitor())

        insts.append(inst.DialogScriptWriteVar(var))
        return insts


class ValuePushVisitor(DialogScriptVisitor):
    """
    Generates instructions that pushes a value into the stack
    """

    def visitProcessParentheses(
            self,
            ctx:DialogScriptParser.ProcessParenthesesContext):
        return ctx.value().accept(self)

    def visitProcessLiteral(
            self,
            ctx: DialogScriptParser.ProcessLiteralContext):
        return ctx.literal().accept(self)

    def visitProcessBinaryOp(
            self,
            ctx: DialogScriptParser.ProcessBinaryOpContext) -> \
            ty.List[inst.DialogScriptInstruction]:
        insts = []
        val1, val2 = ctx.value()
        insts.extend(val1.accept(self))
        insts.extend(val2.accept(self))

        insts.append(ctx.binary_op().accept(BinaryOpVisitor()))
        return insts

    def visitLiteral(self, ctx: DialogScriptParser.LiteralContext) -> \
            ty.List[inst.DialogScriptInstruction]:
        lit = ctx.accept(DialogScriptLiteralVisitor())
        return [inst.DialogScriptPushLiteral(lit)]


class BinaryOpVisitor(DialogScriptVisitor):
    def visitBinary_op(self, ctx: DialogScriptParser.Binary_opContext) -> \
            inst.DialogScriptInstruction:
        if ctx.EQ_OPERATOR():
            return inst.DialogScriptEqualityOp()
        elif ctx.AND_OPERATOR():
            return inst.DialogScriptAndOp()
        elif ctx.OR_OPERATOR():
            return inst.DialogScriptOrOp()

        raise ValueError(f'Operator {ctx.getText()} unknown!')


class SayVisitor(DialogScriptVisitor):
    def visitSay(self, ctx: DialogScriptParser.SayContext) -> \
            inst.DialogScriptSaysInst:
        name = str(ctx.IDENTIFIER())
        parsed_msg = parse_string_node(ctx.STRING_LIT())

        return inst.DialogScriptSaysInst(name, parsed_msg)


class OptionsVisitor(DialogScriptVisitor):
    TOptResult = ty.Tuple[int, str, DialogScriptBlock]

    def visitOpts(self, ctx: DialogScriptParser.OptsContext):
        diag_opts: ty.List[inst.DialogOption] = []
        opt_dsbs: ty.List[DialogScriptBlock] = []
        for opt in ctx.option():  # type: DialogScriptParser.OptionContext
            num, txt, dsb = opt.accept(self)
            diag_opts.append(inst.DialogOption(num, txt))
            opt_dsbs.append(dsb)

        # for options, the instructions should be arranged by
        # opt
        # goto S1
        # <...>
        # goto Sn
        # S1: ...
        # goto end
        # ...
        # Sn: ...
        # goto end
        # end: ...

        # invariant: I is the number of instructions between current "goto Si"
        # and the Si block.
        # initialize I to n
        # and after each loop, subtract 1, and add len(inst) + 1 to
        # compensate for "goto end", with

        # "goto end" being the length of all remaining instructions +
        # number of remaining instructions to compensate for "end".

        dsb = DialogScriptBlock()
        dsb.add_instruction(inst.DialogScriptOptInst(diag_opts))

        # the -1 is to compensate because the instruction pointer moves
        # forward before executing - e.g.
        # (executing)    goto S1
        # (ptr location) goto S2
        i = len(opt_dsbs) - 1
        for opt_dsb in opt_dsbs:
            dsb.add_instruction(inst.DialogScriptGotoOffsetInst(i))
            # <goto Si>
            i += len(opt_dsb.instructions)

        end_offset = sum(len(opt_dsb.instructions) + 1 for opt_dsb in opt_dsbs)

        for opt_dsb in opt_dsbs:
            dsb.extend_dsb(opt_dsb)  # <Si: ...>
            # <goto end>
            end_offset -= len(opt_dsb.instructions)
            end_offset -= 1
            dsb.add_instruction(inst.DialogScriptGotoOffsetInst(end_offset))
        return dsb

    def visitOption(self, ctx: DialogScriptParser.OptionContext):
        if ctx.option_inert() is not None:
            return ctx.option_inert().accept(self)
        elif ctx.option_stm() is not None:
            return ctx.option_stm().accept(self)
        elif ctx.option_single_stm() is not None:
            return ctx.option_single_stm().accept(self)
        else:
            raise RuntimeError('Option statement cannot be None!')

    def visitOption_inert(
            self,
            ctx: DialogScriptParser.Option_inertContext) -> TOptResult:
        num = int(str(ctx.NUMBERS()))
        text = parse_string_node(ctx.STRING_LIT())
        dsb = DialogScriptBlock([inst.DialogScriptNop()])
        return num, text, dsb

    def visitOption_stm(
            self,
            ctx: DialogScriptParser.Option_stmContext) -> \
            TOptResult:
        num = int(str(ctx.NUMBERS()))
        text = parse_string_node(ctx.STRING_LIT())
        dsb = DialogScriptBlock()
        visitor = StatementVisitor(dsb)
        for stm in ctx.statement():
            stm.accept(visitor)
        return num, text, dsb

    def visitOption_single_stm(
            self,
            ctx: DialogScriptParser.Option_single_stmContext) -> \
            TOptResult:
        num = int(str(ctx.NUMBERS()))
        text = parse_string_node(ctx.STRING_LIT())
        dsb = DialogScriptBlock()
        ctx.statement().accept(StatementVisitor(dsb))
        return num, text, dsb
