import time

from re_common.baselibrary.utils.basefile import BaseFile

with open(r"\\192.168.31.171\caiji\test.txt", 'w', encoding="utf-8") as f:
    while True:
        f.write("test\n")
        time.sleep(10)
        print("1")