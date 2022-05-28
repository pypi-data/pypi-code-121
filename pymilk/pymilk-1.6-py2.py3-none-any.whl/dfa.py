'''
项目介绍
    DFA 是一种常见的关键词快速检测算法, 其检测速度比普通的 "x in text" 更快.

已实现的功能
    ● 忽略原文中的无意义字符
    ● 只识别最短的关键词 (存在多种关键词组合时)
    ● 只识别最长的关键词 (存在多种关键词组合时)
    ● 识别所有长度的关键词 (存在多种关键词组合时)
'''

# 预置一批常见的无意义字符(要忽略的字符), 可直接调用
Neglect = '''!@#$%^&*()_+`~-=,./<>?;:'"[]{}|'''

class dfa():

    def __init__(self, words=set(), neglect=''):
        '''
        words: 要检测的词
        neglect: 要忽略的字符
        '''
        self.tree = {}
        self.neglect = set(neglect)
        if words:
            self.add_words(words)
    
    def add_words(self, words):
        for word in words:
            tree = self.tree
            for x in word:
                tree = tree.setdefault(x, {'__end__': False})
            tree['__end__'] = True

    def add_neglect(self, s):
        self.neglect |= set(s)

    def _find_from_index(self, text, start_index, mode='long'):
        indexs = []
        rlong = 0
        kw_size = 0  # 总长度(包括无意义字符的长度)
        tree = self.tree
        for i in range(start_index, len(text)):
            s = text[i]
            if s in tree:
                kw_size += 1
                tree = tree[s]
                if tree["__end__"]:
                    if mode == 'long':
                        rlong = kw_size
                    elif mode == 'short':
                        return [kw_size]
                    else:
                        indexs.append(kw_size)  # 相当于 mode == 'all'
            elif s in self.neglect:
                kw_size += 1
            else:
                break
        return [rlong] if rlong else indexs

    def _FindBase(self, text, mode):
        words = []
        curi = -1
        for i, t in enumerate(text):
            if i >= curi or mode == 'all':
                if t not in self.neglect:
                    indexs = self._find_from_index(text, i, mode=mode)
                    if indexs:
                        for x in indexs:
                            words.append(text[i: i + x])
                        curi = i + x
        return words

    def find(self, text): return self._FindBase(text, 'all')
    def find_long(self, text): return self._FindBase(text, 'long')
    def find_short(self, text): return self._FindBase(text, 'short')


if __name__ == '__main__':
    example = dfa(
        words = {'5', '6', '7', '56', '67', '567'},
        neglect = '''!@#$%^&*()_+`~-=,./<>?;:'"[]{}|'''
    )

    text = '1-2-3-4-5-6-7-8-9'

    print( example.find_short(text) )
    # >>> ['5', '6', '7']

    print( example.find_long(text) )
    # >>> ['5-6-7']

    print( example.find(text) )
    # >>> ['5', '5-6', '5-6-7', '6', '6-7', '7']
