from pyparsing import (
    Word, Optional, alphas, alphanums, nums, CaselessKeyword
)

TITLE = Word(alphanums + '_')

# column_definition: {
#     data_type [NOT NULL | NULL] [DEFAULT {literal | (expr)} ]
# [VISIBLE | INVISIBLE]
# [AUTO_INCREMENT] [UNIQUE [KEY]] [[PRIMARY] KEY]
# [COMMENT 'string']
# [COLLATE collation_name]
# [COLUMN_FORMAT {FIXED | DYNAMIC | DEFAULT}]
# [ENGINE_ATTRIBUTE [=] 'string']
# [SECONDARY_ENGINE_ATTRIBUTE [=] 'string']
# [STORAGE {DISK | MEMORY}]
# [reference_definition]
# [check_constraint_definition]
# | data_type
# [COLLATE collation_name]
# [GENERATED ALWAYS] AS (expr)
# [VIRTUAL | STORED] [NOT NULL | NULL]
# [VISIBLE | INVISIBLE]
# [UNIQUE [KEY]] [[PRIMARY] KEY]
# [COMMENT 'string']
# [reference_definition]
# [check_constraint_definition]
# }
DEFAULT = Optional(CaselessKeyword("DEFAULT") + Word(alphanums + '(' + ')'))
NULLY = Optional(Optional("NOT") + Optional("NULL"))
COLUMN_DEFINITION = Word(alphanums+"_") + Optional("(" + Word(nums) + ")") +\
                    NULLY + DEFAULT

# create_definition: {
#     col_name column_definition
#   | {INDEX | KEY} [index_name] [index_type] (key_part,...)
#       [index_option] ...
#   | {FULLTEXT | SPATIAL} [INDEX | KEY] [index_name] (key_part,...)
#       [index_option] ...
#   | [CONSTRAINT [symbol]] PRIMARY KEY
#       [index_type] (key_part,...)
#       [index_option] ...
#   | [CONSTRAINT [symbol]] UNIQUE [INDEX | KEY]
#       [index_name] [index_type] (key_part,...)
#       [index_option] ...
#   | [CONSTRAINT [symbol]] FOREIGN KEY
#       [index_name] (col_name,...)
#       reference_definition
#   | check_constraint_definition
# }
INDEX = CaselessKeyword("INDEX")|CaselessKeyword("KEY") + Word(alphanums+'_')
CREATE_DEFINITION = Word(alphas+'_') + COLUMN_DEFINITION +\
    INDEX

table_options = Optional(Word(alphanums).ignore("=") + Word(alphanums))

partition_options = Optional(CaselessKeyword("PARITION"))