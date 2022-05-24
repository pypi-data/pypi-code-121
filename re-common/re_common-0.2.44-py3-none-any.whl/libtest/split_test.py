from re_common.baselibrary.tools.split_line_to_many import Split_2_lines

def splite_test():
    infilepath = r'E:\download\cnkistandard\download\db3\cnki_bz_append.big_json'
    outfilepath = r'E:\download\cnkistandard\download\db3\cnki_bz_append_new.big_json'
    spli = Split_2_lines()
    spli.split_line(infilepath,
                    "\"}",
                    outfilepath)

if __name__ == '__main__':
    splite_test()