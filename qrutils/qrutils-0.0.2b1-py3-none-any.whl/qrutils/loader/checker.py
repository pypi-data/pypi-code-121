from tqdm import tqdm

def check_conll(file_name, cut_symbol) -> bool:
        with open(file_name, 'r', encoding='utf8') as f:
            for num, line in enumerate(f.readlines()):
                if len(line.strip().split(cut_symbol)) != 2 and line.strip() != "":
                    print("错误行数：", num, "错误行内容：", line)
