from zwutils.textutils import is_chinese, is_chinese_punctuation
def rmexblank(txt):
    '''
    删除多余空格, 英文保留一个空格, 中文则不保留空格
    '''
    s = txt.strip()
    rtn = []
    for i,c in enumerate(s):
        if c.isspace():
            prev_char = rtn[-1] if len(rtn)>0 else ''
            next_char = s[i+1]
            if any([next_char.isspace(), is_chinese(next_char), is_chinese_punctuation(next_char)]):
                # 当前是空格，若后接空格或中文则不留
                continue
            elif not is_chinese(next_char) and any([is_chinese(prev_char), is_chinese_punctuation(prev_char)]):
                # 当前是空格，若前接非中文且后接中文则不留
                continue
            else:
                rtn.append(c)
        else:
            rtn.append(c)
    return ''.join(rtn)
