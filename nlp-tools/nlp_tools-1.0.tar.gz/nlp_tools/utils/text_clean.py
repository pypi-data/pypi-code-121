import re
def _regular_(sen):
    """
    句子规范化，主要是对原始语料的句子进行一些标点符号的统一
    :param sen:
    :return:
    """
    sen = sen.replace('/', '')
    sen = re.sub(r'…{1,100}', '…', sen)
    sen = re.sub(r'\.{3,100}', '…', sen)
    sen = re.sub(r'···{2,100}', '…', sen)
    sen = re.sub(r',{1,100}', '，', sen)
    sen = re.sub(r'\.{1,100}', '。', sen)
    sen = re.sub(r'。{1,100}', '。', sen)
    sen = re.sub(r'\?{1,100}', '？', sen)
    sen = re.sub(r'？{1,100}', '？', sen)
    sen = re.sub(r'!{1,100}', '！', sen)
    sen = re.sub(r'！{1,100}', '！', sen)
    sen = re.sub(r'~{1,100}', '～', sen)
    sen = re.sub(r'～{1,100}', '～', sen)
    sen = re.sub(r'[“”]{1,100}', '"', sen)
    sen = re.sub('[^\w\u4e00-\u9fff"。，？！～·]+', '', sen)
    sen = re.sub(r'[ˇˊˋˍεπのゞェーω]', '', sen)

    return sen


def full_to_half(s):
    """
    Convert full-width character to half-width one
    """
    n = []
    for char in s:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        char = chr(num)
        n.append(char)
    return ''.join(n)


def cut_to_sentence(text):
    """
    Cut text to sentences
    """
    sentence = []
    sentences = []
    len_p = len(text)
    pre_cut = False
    for idx, word in enumerate(text):
        sentence.append(word)
        cut = False
        if pre_cut:
            cut=True
            pre_cut=False
        if word in u"。;!?\n":
            cut = True
            if len_p > idx+1:
                if text[idx+1] in ".。”\"\'“”‘’?!":
                    cut = False
                    pre_cut=True

        if cut:
            sentences.append(sentence)
            sentence = []
    if sentence:
        sentences.append("".join(list(sentence)))
    return sentences


def replace_html(s):
    s = s.replace('&quot;','"')
    s = s.replace('&amp;','&')
    s = s.replace('&lt;','<')
    s = s.replace('&gt;','>')
    s = s.replace('&nbsp;',' ')
    s = s.replace("&ldquo;", "“")
    s = s.replace("&rdquo;", "”")
    s = s.replace("&mdash;","")
    s = s.replace("\xa0", " ")
    return(s)