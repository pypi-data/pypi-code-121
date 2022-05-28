from pyparsing import OneOrMore, Group
from .definitions import *
from .keywords import *
from .keywords import _

NOT_CREATE_STATEMENT = Word(alphas)

COL_NAME = Word(alphanums + '_')
COLUMN = Word(alphanums+'_') + COLUMN_DEFINITION.ignore(',')

# Key Variables
table_name = Word(alphanums)("table_name")

create_definition = '(' + OneOrMore(COLUMN)("columns") + ')'

CREATE = CREATE + TEMPORARY + TABLE + IF_NOT_EXISTS + table_name + \
         create_definition + \
         table_options + \
         partition_options + \
         Optional(';')

definition = OneOrMore(Group(CREATE))
