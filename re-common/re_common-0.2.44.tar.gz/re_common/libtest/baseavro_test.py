from re_common.baselibrary.utils.baseavro import BaseAvro

id_set = set()
for line in BaseAvro().read_line_yeild(r"F:\fun2\avro"):
    id_set.add(line["key"])

print(len(id_set))
lines = ""

with open(r"F:\fun2\avro1.txt", 'w', encoding="utf-8") as f:
    for id in id_set:
        lines = id + "\n"
        f.write(lines)
