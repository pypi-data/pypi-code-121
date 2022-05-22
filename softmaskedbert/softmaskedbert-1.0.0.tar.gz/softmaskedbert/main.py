import pandas as pd
from inference import Corrector
from softmaskedbert3 import SmbModel


if __name__ == "__main__":
    # 整句的纠错结果
    # Presion: 0.7884302349847656
    # Recall: 0.8384748546318079
    # F1:0.8126
    corrector = Corrector()
    data = pd.read_csv('data/dev1.csv')
    # 记录纠错准确率
    TP, TN, FP, FN = 0, 0, 0, 0
    for i, row in data.iterrows():
        random_text = row[1]
        origin_text = row[0]
        correct_text, details = corrector.correct(random_text)
        # 判断句子是否有误
        # 1.无误
        if origin_text == random_text:
            if correct_text == origin_text:
                TN += 1
            else:
                FP += 1
        # 2.有误
        else:
            if correct_text == origin_text:
                TP += 1
            else:
                if len(details) == 0:
                    FN += 1
                else:
                    FP += 1
        if i % 100 == 0 and i != 0:
            print(TP, FN, TN, FN)
            print('Presion:', TP/(TP+FP))
            print('Recall:', TP/(TP+FN))