from tqdm import tqdm

def bio2bmes(read_file, save_file, split_symbol):
    f = open(read_file, encoding='utf-8')
    f1 = open(save_file, 'w+', encoding='utf_8')

    sentences = []
    sentence = []
    label_set = set()
    cnt_line = 0
    for line in f:

        cnt_line += 1
        if len(line) == 0 or line[0] == "\n":
            if len(sentence) > 0:
                sentences.append(sentence)
                # print(sentence)
                sentence = []
            continue
        splits = line.split(split_symbol)
        sentence.append([splits[0], splits[-1][:-1]])
        label_set.add(splits[-1])

    if len(sentence) > 0:
        sentences.append(sentence)
        sentence = []
    f.close()

    # 文件转换 存储文件
    for sen in sentences:
        i = 0
        for index, word in enumerate(sen):
            char = word[0]
            label = word[1]
            if index < len(sen) - 1:
                if (label[0] == 'B'):
                    if sen[index + 1][1][0] == 'I':
                        label = label
                    elif sen[index + 1][1][0] == 'O':
                        label = 'S' + label[1:]
                elif (label[0] == 'I'):
                    if sen[index + 1][1][0] == 'I':
                        label = 'M' + label[1:]
                    if sen[index + 1][1][0] == 'O' or sen[index + 1][1][0] == 'B':
                        label = 'E' + label[1:]
                elif (label[0] == 'O'):
                    label = label
            else:
                if (label[0] == 'B'):
                    label = 'S' + label[1:]
                elif (label[0] == 'I'):
                    label = 'E' + label[1:]
                elif (label[0] == 'O'):
                    label = label

            f1.write(f'{char} {label}\n')
        f1.write('\n')
    f1.close()

def split_trans(read_file, save_file, split_before, split_after):
    with open(read_file, 'r', encoding='utf8') as f1, open(
            save_file, "w", encoding="utf8") as f2:
        for line in tqdm(f1.readlines()):
            fline = line.split(split_before)
            f2.write(split_after.join(fline))