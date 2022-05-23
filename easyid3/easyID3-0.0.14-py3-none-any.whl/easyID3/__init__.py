import pandas as pd
import math
import numpy as np

class Node:
    def __init__(self):
        self.children = []
        self.value = ""
        self.isLeaf = False
        self.pred = ""
        self.answerCol = ""
        self.pred_id = 999999
        self.countAns = {}

def __orderdata__(data, answerCol):
    data = data.astype("str")
    for col in data.columns:
        if len(data[col]) == len(pd.unique(data[col])):
            data = data.drop(col, axis = 1)
    features = [feat for feat in data]
    features.remove(answerCol)
    return data, features


def __entropy__(data, answerCol):
    answers = data[answerCol].unique()
    prob = []
    for ans in answers:
        prob.append(sum(data[answerCol]==ans)/len(data[answerCol]))
    tot = 0
    for p in prob:
        tot += p * math.log(p, 2)
    return -tot

def __info_gain__(data, feature, answerCol):
    uniq = np.unique(data[feature])
    gain = __entropy__(data, answerCol)
    for u in uniq:
        subdata = data[data[feature] == u]
        subEntropy = __entropy__(subdata, answerCol)
        gain -= (float(len(subdata)) / float(len(data))) * subEntropy
    return gain

def __id3_bg__(data, features, answerCol):
    answers = data[answerCol].unique()
    root = Node()

    max_gain = 0
    max_feat = ""
    for feature in features:
        gain = __info_gain__(data, feature, answerCol)
        if gain > max_gain:
            max_gain = gain
            max_feat = feature
    root.value = max_feat
    if max_feat != "":
        uniq = np.unique(data[max_feat])
        for u in uniq:
            subdata = data[data[max_feat] == u]
            if __entropy__(subdata, answerCol) == 0.0:
                newNode = Node()
                newNode.isLeaf = True
                newNode.value = u
                newNode.pred = np.unique(subdata[answerCol])
                newNode.answerCol = answerCol
                newNode.pred_id = np.where(np.sort(answers)==newNode.pred[0])[0][0]
                root.children.append(newNode)
            else:
                dummyNode = Node()
                dummyNode.value = u
                new_features = features.copy()
                new_features.remove(max_feat)
                child = __id3_bg__(subdata, new_features, answerCol)
                dummyNode.children.append(child)
                dummyNode.answerCol = answerCol
                answers = data[answerCol].unique()
                for ans in answers:
                    count = sum(subdata[answerCol]==ans)
                    dummyNode.countAns[ans] = count
                root.children.append(dummyNode)
             
        return root

def ID3(data, answerCol):
    data, features = __orderdata__(data, answerCol)
    return __id3_bg__(data, features, answerCol)

def printTree(root: Node, depth=0):
    treeColors = [('\x1b[30m', '\x1b[46m'), ('\x1b[37m', '\x1b[45m'), 
                  ('\x1b[37m', '\x1b[44m'), ('\x1b[30m', '\x1b[43m')]
    ansColors = [('\x1b[37m', '\x1b[41m'), ('\x1b[30m', '\x1b[42m')]
    Bold, Underline = '\033[1m', '\033[4m'
    ForeWHITE, BackBLACK = '\x1b[37m', '\x1b[40m'
    StyleRESET_ALL = '\x1b[0m'
    n=0
    while root != None and n<1:
        for i in range(depth):
            print("\t", end="")
        print(f'{treeColors[depth%len(treeColors)][0]}'+
              f'{treeColors[depth%len(treeColors)][1]}'+root.value+f'{StyleRESET_ALL}', end="")
        if root.isLeaf:
            print(" -> ", f'{Bold}{Underline}{ansColors[root.pred_id%len(ansColors)][0]}{ansColors[root.pred_id%len(ansColors)][1]}'
                  +'['+f'{root.answerCol}'+': '+f'{root.pred[0]}'+']'+f'{StyleRESET_ALL}')

        else:
            if root.children == [None]:
                print(" -> ", f'{Bold}{Underline}{ForeWHITE}{BackBLACK}'+"Uncertain"+" "
                      +f'{dict(sorted(root.countAns.items()))}'+f'{StyleRESET_ALL}')
        print()
        for child in root.children:
            printTree(child, depth + 1)
        n += 1