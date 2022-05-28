from re import sub, findall, search
from hashlib import shake_256
from .toolkit.data_structures import ParamError


# 段落清洗
def wash_paragraph(text):
    text = sub('\s+', ' ', text)
    text = sub('^[ 0-9.,:#)(。，：、]+', '', text)
    text = sub(' +$', '', text)
    return text

# 密实哈希
def compact_hash(text, size=32):
    text = sub('[^\u4e00-\u9fa5\da-zA-Z]', '', text)
    hash = shake_256(text.encode('utf8')).hexdigest(int(size/2))
    return hash

# 密实标志
def compact_mark(text, size=32):
    text = sub('[^\u4e00-\u9fa5\da-zA-Z]', '', text)
    if len(text) > size:
        text = shake_256(text.encode('utf8')).hexdigest(int(size/2))
    return text

def sound_len(text): return len(findall('[\u4e00-\u9fa5\da-zA-Z]', text))

def effbool(text): return bool(search('[^\s]', text))


class chre():
    
    def __init__(self, s):
        self.s = s
        
    def sub(self, *vs, **kvs):
        s = sub(*vs, string=self.s, **kvs)
        return chre(s)

    def search(self, *vs, **kvs):
        s = search(*vs, string=self.s, **kvs).group(0)
        return chre(s)
    
    def replace(self, *vs, **kvs):
        s = self.s.replace(*vs, **kvs)
        return chre(s)

    def wash_paragraph(self):
        s = wash_paragraph(self.s)
        return chre(s)


def check_chinese(text, pattern):
    if pattern == 'any': return bool(search('[\u4e00-\u9fa5]', text))
    if pattern == 'all': return not bool(search('[^\u4e00-\u9fa5]', text))
    raise ParamError(f'未知的模式: {pattern}')

a_z = 'abcdefghijklmnopqrstuvwxyz'
A_Z = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
n0_9 = '0123456789'
