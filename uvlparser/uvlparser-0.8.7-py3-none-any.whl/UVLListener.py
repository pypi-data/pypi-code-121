# Generated from uvlparser/UVL.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .UVLParser import UVLParser
else:
    from UVLParser import UVLParser

# This class defines a complete listener for a parse tree produced by UVLParser.
class UVLListener(ParseTreeListener):

    # Enter a parse tree produced by UVLParser#feature_model.
    def enterFeature_model(self, ctx:UVLParser.Feature_modelContext):
        pass

    # Exit a parse tree produced by UVLParser#feature_model.
    def exitFeature_model(self, ctx:UVLParser.Feature_modelContext):
        pass


    # Enter a parse tree produced by UVLParser#namespace.
    def enterNamespace(self, ctx:UVLParser.NamespaceContext):
        pass

    # Exit a parse tree produced by UVLParser#namespace.
    def exitNamespace(self, ctx:UVLParser.NamespaceContext):
        pass


    # Enter a parse tree produced by UVLParser#features.
    def enterFeatures(self, ctx:UVLParser.FeaturesContext):
        pass

    # Exit a parse tree produced by UVLParser#features.
    def exitFeatures(self, ctx:UVLParser.FeaturesContext):
        pass


    # Enter a parse tree produced by UVLParser#child.
    def enterChild(self, ctx:UVLParser.ChildContext):
        pass

    # Exit a parse tree produced by UVLParser#child.
    def exitChild(self, ctx:UVLParser.ChildContext):
        pass


    # Enter a parse tree produced by UVLParser#relation.
    def enterRelation(self, ctx:UVLParser.RelationContext):
        pass

    # Exit a parse tree produced by UVLParser#relation.
    def exitRelation(self, ctx:UVLParser.RelationContext):
        pass


    # Enter a parse tree produced by UVLParser#feature_spec.
    def enterFeature_spec(self, ctx:UVLParser.Feature_specContext):
        pass

    # Exit a parse tree produced by UVLParser#feature_spec.
    def exitFeature_spec(self, ctx:UVLParser.Feature_specContext):
        pass


    # Enter a parse tree produced by UVLParser#ref.
    def enterRef(self, ctx:UVLParser.RefContext):
        pass

    # Exit a parse tree produced by UVLParser#ref.
    def exitRef(self, ctx:UVLParser.RefContext):
        pass


    # Enter a parse tree produced by UVLParser#attributes.
    def enterAttributes(self, ctx:UVLParser.AttributesContext):
        pass

    # Exit a parse tree produced by UVLParser#attributes.
    def exitAttributes(self, ctx:UVLParser.AttributesContext):
        pass


    # Enter a parse tree produced by UVLParser#attribute.
    def enterAttribute(self, ctx:UVLParser.AttributeContext):
        pass

    # Exit a parse tree produced by UVLParser#attribute.
    def exitAttribute(self, ctx:UVLParser.AttributeContext):
        pass


    # Enter a parse tree produced by UVLParser#key.
    def enterKey(self, ctx:UVLParser.KeyContext):
        pass

    # Exit a parse tree produced by UVLParser#key.
    def exitKey(self, ctx:UVLParser.KeyContext):
        pass


    # Enter a parse tree produced by UVLParser#value.
    def enterValue(self, ctx:UVLParser.ValueContext):
        pass

    # Exit a parse tree produced by UVLParser#value.
    def exitValue(self, ctx:UVLParser.ValueContext):
        pass


    # Enter a parse tree produced by UVLParser#relation_spec.
    def enterRelation_spec(self, ctx:UVLParser.Relation_specContext):
        pass

    # Exit a parse tree produced by UVLParser#relation_spec.
    def exitRelation_spec(self, ctx:UVLParser.Relation_specContext):
        pass


    # Enter a parse tree produced by UVLParser#constraints.
    def enterConstraints(self, ctx:UVLParser.ConstraintsContext):
        pass

    # Exit a parse tree produced by UVLParser#constraints.
    def exitConstraints(self, ctx:UVLParser.ConstraintsContext):
        pass


    # Enter a parse tree produced by UVLParser#andExp.
    def enterAndExp(self, ctx:UVLParser.AndExpContext):
        pass

    # Exit a parse tree produced by UVLParser#andExp.
    def exitAndExp(self, ctx:UVLParser.AndExpContext):
        pass


    # Enter a parse tree produced by UVLParser#parenthesisExp.
    def enterParenthesisExp(self, ctx:UVLParser.ParenthesisExpContext):
        pass

    # Exit a parse tree produced by UVLParser#parenthesisExp.
    def exitParenthesisExp(self, ctx:UVLParser.ParenthesisExpContext):
        pass


    # Enter a parse tree produced by UVLParser#term.
    def enterTerm(self, ctx:UVLParser.TermContext):
        pass

    # Exit a parse tree produced by UVLParser#term.
    def exitTerm(self, ctx:UVLParser.TermContext):
        pass


    # Enter a parse tree produced by UVLParser#orExp.
    def enterOrExp(self, ctx:UVLParser.OrExpContext):
        pass

    # Exit a parse tree produced by UVLParser#orExp.
    def exitOrExp(self, ctx:UVLParser.OrExpContext):
        pass


    # Enter a parse tree produced by UVLParser#logicalExp.
    def enterLogicalExp(self, ctx:UVLParser.LogicalExpContext):
        pass

    # Exit a parse tree produced by UVLParser#logicalExp.
    def exitLogicalExp(self, ctx:UVLParser.LogicalExpContext):
        pass


    # Enter a parse tree produced by UVLParser#notExp.
    def enterNotExp(self, ctx:UVLParser.NotExpContext):
        pass

    # Exit a parse tree produced by UVLParser#notExp.
    def exitNotExp(self, ctx:UVLParser.NotExpContext):
        pass


    # Enter a parse tree produced by UVLParser#equivExp.
    def enterEquivExp(self, ctx:UVLParser.EquivExpContext):
        pass

    # Exit a parse tree produced by UVLParser#equivExp.
    def exitEquivExp(self, ctx:UVLParser.EquivExpContext):
        pass


    # Enter a parse tree produced by UVLParser#impliesExp.
    def enterImpliesExp(self, ctx:UVLParser.ImpliesExpContext):
        pass

    # Exit a parse tree produced by UVLParser#impliesExp.
    def exitImpliesExp(self, ctx:UVLParser.ImpliesExpContext):
        pass


    # Enter a parse tree produced by UVLParser#requiresExp.
    def enterRequiresExp(self, ctx:UVLParser.RequiresExpContext):
        pass

    # Exit a parse tree produced by UVLParser#requiresExp.
    def exitRequiresExp(self, ctx:UVLParser.RequiresExpContext):
        pass


    # Enter a parse tree produced by UVLParser#excludesExp.
    def enterExcludesExp(self, ctx:UVLParser.ExcludesExpContext):
        pass

    # Exit a parse tree produced by UVLParser#excludesExp.
    def exitExcludesExp(self, ctx:UVLParser.ExcludesExpContext):
        pass


    # Enter a parse tree produced by UVLParser#imports.
    def enterImports(self, ctx:UVLParser.ImportsContext):
        pass

    # Exit a parse tree produced by UVLParser#imports.
    def exitImports(self, ctx:UVLParser.ImportsContext):
        pass


    # Enter a parse tree produced by UVLParser#imp.
    def enterImp(self, ctx:UVLParser.ImpContext):
        pass

    # Exit a parse tree produced by UVLParser#imp.
    def exitImp(self, ctx:UVLParser.ImpContext):
        pass


    # Enter a parse tree produced by UVLParser#imp_spec.
    def enterImp_spec(self, ctx:UVLParser.Imp_specContext):
        pass

    # Exit a parse tree produced by UVLParser#imp_spec.
    def exitImp_spec(self, ctx:UVLParser.Imp_specContext):
        pass


