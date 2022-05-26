# Generated from Vsh.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .VshParser import VshParser
else:
    from VshParser import VshParser

# This class defines a complete generic visitor for a parse tree produced by VshParser.

class VshVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by VshParser#program.
    def visitProgram(self, ctx:VshParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#statement.
    def visitStatement(self, ctx:VshParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#combined_operation.
    def visitCombined_operation(self, ctx:VshParser.Combined_operationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#operation.
    def visitOperation(self, ctx:VshParser.OperationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_add.
    def visitOp_add(self, ctx:VshParser.Op_addContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_arl.
    def visitOp_arl(self, ctx:VshParser.Op_arlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_dp3.
    def visitOp_dp3(self, ctx:VshParser.Op_dp3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_dp4.
    def visitOp_dp4(self, ctx:VshParser.Op_dp4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_dph.
    def visitOp_dph(self, ctx:VshParser.Op_dphContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_dst.
    def visitOp_dst(self, ctx:VshParser.Op_dstContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_expp.
    def visitOp_expp(self, ctx:VshParser.Op_exppContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_lit.
    def visitOp_lit(self, ctx:VshParser.Op_litContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_logp.
    def visitOp_logp(self, ctx:VshParser.Op_logpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_mad.
    def visitOp_mad(self, ctx:VshParser.Op_madContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_max.
    def visitOp_max(self, ctx:VshParser.Op_maxContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_min.
    def visitOp_min(self, ctx:VshParser.Op_minContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_mov.
    def visitOp_mov(self, ctx:VshParser.Op_movContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_mul.
    def visitOp_mul(self, ctx:VshParser.Op_mulContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_rcc.
    def visitOp_rcc(self, ctx:VshParser.Op_rccContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_rcp.
    def visitOp_rcp(self, ctx:VshParser.Op_rcpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_rsq.
    def visitOp_rsq(self, ctx:VshParser.Op_rsqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_sge.
    def visitOp_sge(self, ctx:VshParser.Op_sgeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_slt.
    def visitOp_slt(self, ctx:VshParser.Op_sltContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#op_sub.
    def visitOp_sub(self, ctx:VshParser.Op_subContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#p_a0_in.
    def visitP_a0_in(self, ctx:VshParser.P_a0_inContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#p_out_in.
    def visitP_out_in(self, ctx:VshParser.P_out_inContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#p_out_in_in.
    def visitP_out_in_in(self, ctx:VshParser.P_out_in_inContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#p_out_in_in_in.
    def visitP_out_in_in_in(self, ctx:VshParser.P_out_in_in_inContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#reg_const.
    def visitReg_const(self, ctx:VshParser.Reg_constContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#uniform_const.
    def visitUniform_const(self, ctx:VshParser.Uniform_constContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#p_a0_output.
    def visitP_a0_output(self, ctx:VshParser.P_a0_outputContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#p_output.
    def visitP_output(self, ctx:VshParser.P_outputContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#p_input_raw.
    def visitP_input_raw(self, ctx:VshParser.P_input_rawContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#p_input_negated.
    def visitP_input_negated(self, ctx:VshParser.P_input_negatedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#p_input.
    def visitP_input(self, ctx:VshParser.P_inputContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#uniform_type.
    def visitUniform_type(self, ctx:VshParser.Uniform_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VshParser#uniform_declaration.
    def visitUniform_declaration(self, ctx:VshParser.Uniform_declarationContext):
        return self.visitChildren(ctx)



del VshParser