import gzip
import json

from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.basefile import BaseFile

ref_outPathFile = r"F:\fun3\ref\cnkiref.big_json.gz"
f_ref = gzip.open(ref_outPathFile, "wb")
if BaseFile.get_file_size(ref_outPathFile) >= 100 * 1024 * 1024:
    f_ref.close()
    ref_outPathFile = BaseFile.change_file(ref_outPathFile, size=100 * 1024 * 1024)
    ref_outPathFile = ref_outPathFile.replace(".big_json", '.big_json.gz')
    f_ref = gzip.open(ref_outPathFile, "wb")
    print("new dst_path: %s" % ref_outPathFile)
for file in BaseDir.get_dir_all_files(r"F:\fun2\ref"):
    print(file)
    with gzip.open(file, 'r') as f:
        for lineb in f:
            line = lineb.decode()
            linedicts = json.loads(line)
            print(linedicts)
            if "stat" in linedicts:
                for key in linedicts:
                    if key == "stat":
                        continue
                    else:
                        print(key)
                        tempdicts = linedicts[key]
                        print(tempdicts)
                        line_ref = json.dumps(tempdicts, ensure_ascii=False) + "\n"
                        line_refs = line_ref.encode()
                        f_ref.write(line_refs)
            else:
                f_ref.write(lineb)
            if BaseFile.get_file_size(ref_outPathFile) >= 100 * 1024 * 1024:
                f_ref.close()
                ref_outPathFile = BaseFile.change_file(ref_outPathFile, size=100 * 1024 * 1024)
                ref_outPathFile = ref_outPathFile.replace(".big_json", '.big_json.gz')
                f_ref = gzip.open(ref_outPathFile, "wb")
                print("new dst_path: %s" % ref_outPathFile)