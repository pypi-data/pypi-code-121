# Generated from Vsh.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .VshParser import VshParser
else:
    from VshParser import VshParser

# This class defines a complete listener for a parse tree produced by VshParser.
class VshListener(ParseTreeListener):

    # Enter a parse tree produced by VshParser#program.
    def enterProgram(self, ctx:VshParser.ProgramContext):
        pass

    # Exit a parse tree produced by VshParser#program.
    def exitProgram(self, ctx:VshParser.ProgramContext):
        pass


    # Enter a parse tree produced by VshParser#statement.
    def enterStatement(self, ctx:VshParser.StatementContext):
        pass

    # Exit a parse tree produced by VshParser#statement.
    def exitStatement(self, ctx:VshParser.StatementContext):
        pass


    # Enter a parse tree produced by VshParser#combined_operation.
    def enterCombined_operation(self, ctx:VshParser.Combined_operationContext):
        pass

    # Exit a parse tree produced by VshParser#combined_operation.
    def exitCombined_operation(self, ctx:VshParser.Combined_operationContext):
        pass


    # Enter a parse tree produced by VshParser#operation.
    def enterOperation(self, ctx:VshParser.OperationContext):
        pass

    # Exit a parse tree produced by VshParser#operation.
    def exitOperation(self, ctx:VshParser.OperationContext):
        pass


    # Enter a parse tree produced by VshParser#op_add.
    def enterOp_add(self, ctx:VshParser.Op_addContext):
        pass

    # Exit a parse tree produced by VshParser#op_add.
    def exitOp_add(self, ctx:VshParser.Op_addContext):
        pass


    # Enter a parse tree produced by VshParser#op_arl.
    def enterOp_arl(self, ctx:VshParser.Op_arlContext):
        pass

    # Exit a parse tree produced by VshParser#op_arl.
    def exitOp_arl(self, ctx:VshParser.Op_arlContext):
        pass


    # Enter a parse tree produced by VshParser#op_dp3.
    def enterOp_dp3(self, ctx:VshParser.Op_dp3Context):
        pass

    # Exit a parse tree produced by VshParser#op_dp3.
    def exitOp_dp3(self, ctx:VshParser.Op_dp3Context):
        pass


    # Enter a parse tree produced by VshParser#op_dp4.
    def enterOp_dp4(self, ctx:VshParser.Op_dp4Context):
        pass

    # Exit a parse tree produced by VshParser#op_dp4.
    def exitOp_dp4(self, ctx:VshParser.Op_dp4Context):
        pass


    # Enter a parse tree produced by VshParser#op_dph.
    def enterOp_dph(self, ctx:VshParser.Op_dphContext):
        pass

    # Exit a parse tree produced by VshParser#op_dph.
    def exitOp_dph(self, ctx:VshParser.Op_dphContext):
        pass


    # Enter a parse tree produced by VshParser#op_dst.
    def enterOp_dst(self, ctx:VshParser.Op_dstContext):
        pass

    # Exit a parse tree produced by VshParser#op_dst.
    def exitOp_dst(self, ctx:VshParser.Op_dstContext):
        pass


    # Enter a parse tree produced by VshParser#op_expp.
    def enterOp_expp(self, ctx:VshParser.Op_exppContext):
        pass

    # Exit a parse tree produced by VshParser#op_expp.
    def exitOp_expp(self, ctx:VshParser.Op_exppContext):
        pass


    # Enter a parse tree produced by VshParser#op_lit.
    def enterOp_lit(self, ctx:VshParser.Op_litContext):
        pass

    # Exit a parse tree produced by VshParser#op_lit.
    def exitOp_lit(self, ctx:VshParser.Op_litContext):
        pass


    # Enter a parse tree produced by VshParser#op_logp.
    def enterOp_logp(self, ctx:VshParser.Op_logpContext):
        pass

    # Exit a parse tree produced by VshParser#op_logp.
    def exitOp_logp(self, ctx:VshParser.Op_logpContext):
        pass


    # Enter a parse tree produced by VshParser#op_mad.
    def enterOp_mad(self, ctx:VshParser.Op_madContext):
        pass

    # Exit a parse tree produced by VshParser#op_mad.
    def exitOp_mad(self, ctx:VshParser.Op_madContext):
        pass


    # Enter a parse tree produced by VshParser#op_max.
    def enterOp_max(self, ctx:VshParser.Op_maxContext):
        pass

    # Exit a parse tree produced by VshParser#op_max.
    def exitOp_max(self, ctx:VshParser.Op_maxContext):
        pass


    # Enter a parse tree produced by VshParser#op_min.
    def enterOp_min(self, ctx:VshParser.Op_minContext):
        pass

    # Exit a parse tree produced by VshParser#op_min.
    def exitOp_min(self, ctx:VshParser.Op_minContext):
        pass


    # Enter a parse tree produced by VshParser#op_mov.
    def enterOp_mov(self, ctx:VshParser.Op_movContext):
        pass

    # Exit a parse tree produced by VshParser#op_mov.
    def exitOp_mov(self, ctx:VshParser.Op_movContext):
        pass


    # Enter a parse tree produced by VshParser#op_mul.
    def enterOp_mul(self, ctx:VshParser.Op_mulContext):
        pass

    # Exit a parse tree produced by VshParser#op_mul.
    def exitOp_mul(self, ctx:VshParser.Op_mulContext):
        pass


    # Enter a parse tree produced by VshParser#op_rcc.
    def enterOp_rcc(self, ctx:VshParser.Op_rccContext):
        pass

    # Exit a parse tree produced by VshParser#op_rcc.
    def exitOp_rcc(self, ctx:VshParser.Op_rccContext):
        pass


    # Enter a parse tree produced by VshParser#op_rcp.
    def enterOp_rcp(self, ctx:VshParser.Op_rcpContext):
        pass

    # Exit a parse tree produced by VshParser#op_rcp.
    def exitOp_rcp(self, ctx:VshParser.Op_rcpContext):
        pass


    # Enter a parse tree produced by VshParser#op_rsq.
    def enterOp_rsq(self, ctx:VshParser.Op_rsqContext):
        pass

    # Exit a parse tree produced by VshParser#op_rsq.
    def exitOp_rsq(self, ctx:VshParser.Op_rsqContext):
        pass


    # Enter a parse tree produced by VshParser#op_sge.
    def enterOp_sge(self, ctx:VshParser.Op_sgeContext):
        pass

    # Exit a parse tree produced by VshParser#op_sge.
    def exitOp_sge(self, ctx:VshParser.Op_sgeContext):
        pass


    # Enter a parse tree produced by VshParser#op_slt.
    def enterOp_slt(self, ctx:VshParser.Op_sltContext):
        pass

    # Exit a parse tree produced by VshParser#op_slt.
    def exitOp_slt(self, ctx:VshParser.Op_sltContext):
        pass


    # Enter a parse tree produced by VshParser#op_sub.
    def enterOp_sub(self, ctx:VshParser.Op_subContext):
        pass

    # Exit a parse tree produced by VshParser#op_sub.
    def exitOp_sub(self, ctx:VshParser.Op_subContext):
        pass


    # Enter a parse tree produced by VshParser#p_a0_in.
    def enterP_a0_in(self, ctx:VshParser.P_a0_inContext):
        pass

    # Exit a parse tree produced by VshParser#p_a0_in.
    def exitP_a0_in(self, ctx:VshParser.P_a0_inContext):
        pass


    # Enter a parse tree produced by VshParser#p_out_in.
    def enterP_out_in(self, ctx:VshParser.P_out_inContext):
        pass

    # Exit a parse tree produced by VshParser#p_out_in.
    def exitP_out_in(self, ctx:VshParser.P_out_inContext):
        pass


    # Enter a parse tree produced by VshParser#p_out_in_in.
    def enterP_out_in_in(self, ctx:VshParser.P_out_in_inContext):
        pass

    # Exit a parse tree produced by VshParser#p_out_in_in.
    def exitP_out_in_in(self, ctx:VshParser.P_out_in_inContext):
        pass


    # Enter a parse tree produced by VshParser#p_out_in_in_in.
    def enterP_out_in_in_in(self, ctx:VshParser.P_out_in_in_inContext):
        pass

    # Exit a parse tree produced by VshParser#p_out_in_in_in.
    def exitP_out_in_in_in(self, ctx:VshParser.P_out_in_in_inContext):
        pass


    # Enter a parse tree produced by VshParser#reg_const.
    def enterReg_const(self, ctx:VshParser.Reg_constContext):
        pass

    # Exit a parse tree produced by VshParser#reg_const.
    def exitReg_const(self, ctx:VshParser.Reg_constContext):
        pass


    # Enter a parse tree produced by VshParser#uniform_const.
    def enterUniform_const(self, ctx:VshParser.Uniform_constContext):
        pass

    # Exit a parse tree produced by VshParser#uniform_const.
    def exitUniform_const(self, ctx:VshParser.Uniform_constContext):
        pass


    # Enter a parse tree produced by VshParser#p_a0_output.
    def enterP_a0_output(self, ctx:VshParser.P_a0_outputContext):
        pass

    # Exit a parse tree produced by VshParser#p_a0_output.
    def exitP_a0_output(self, ctx:VshParser.P_a0_outputContext):
        pass


    # Enter a parse tree produced by VshParser#p_output.
    def enterP_output(self, ctx:VshParser.P_outputContext):
        pass

    # Exit a parse tree produced by VshParser#p_output.
    def exitP_output(self, ctx:VshParser.P_outputContext):
        pass


    # Enter a parse tree produced by VshParser#p_input_raw.
    def enterP_input_raw(self, ctx:VshParser.P_input_rawContext):
        pass

    # Exit a parse tree produced by VshParser#p_input_raw.
    def exitP_input_raw(self, ctx:VshParser.P_input_rawContext):
        pass


    # Enter a parse tree produced by VshParser#p_input_negated.
    def enterP_input_negated(self, ctx:VshParser.P_input_negatedContext):
        pass

    # Exit a parse tree produced by VshParser#p_input_negated.
    def exitP_input_negated(self, ctx:VshParser.P_input_negatedContext):
        pass


    # Enter a parse tree produced by VshParser#p_input.
    def enterP_input(self, ctx:VshParser.P_inputContext):
        pass

    # Exit a parse tree produced by VshParser#p_input.
    def exitP_input(self, ctx:VshParser.P_inputContext):
        pass


    # Enter a parse tree produced by VshParser#uniform_type.
    def enterUniform_type(self, ctx:VshParser.Uniform_typeContext):
        pass

    # Exit a parse tree produced by VshParser#uniform_type.
    def exitUniform_type(self, ctx:VshParser.Uniform_typeContext):
        pass


    # Enter a parse tree produced by VshParser#uniform_declaration.
    def enterUniform_declaration(self, ctx:VshParser.Uniform_declarationContext):
        pass

    # Exit a parse tree produced by VshParser#uniform_declaration.
    def exitUniform_declaration(self, ctx:VshParser.Uniform_declarationContext):
        pass


