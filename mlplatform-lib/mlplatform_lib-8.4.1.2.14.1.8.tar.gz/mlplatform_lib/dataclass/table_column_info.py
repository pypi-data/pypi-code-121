from dataclasses import dataclass

# {
#     "name": "review",
#     "type": "VARCHAR",
#     "alias": "review",
#     "nullable": true,
#     "primaryKey": false,
#     "foreignKey": false,
#     "description": ""
# },


@dataclass
class TableColumnInfo:
    name: str
    type: str
    alias: str
    nullable: bool
    primary_key: bool
    foreign_key: bool
    description: str
