from argparse import ArgumentParser
from paddl.langs.mysql import definition as mysql
from paddl import parse, erd

parser = ArgumentParser("paddl", description="Parse DDLs")
parser.add_argument("sql", type=str,
                    help="sql with CREATE statements")
parser.add_argument("--erd", action='store_true', default=True,
                    help="render PlantUML ER Diagram")

args = parser.parse_args()

ddl_s = open(args.sql).read()

# result = mysql.parseString(ddl_s, parseAll=False)
result = parse(ddl_s)

if args.erd:
    print(erd.render(result))
else:
    print(ddl_s)
    print(result)
