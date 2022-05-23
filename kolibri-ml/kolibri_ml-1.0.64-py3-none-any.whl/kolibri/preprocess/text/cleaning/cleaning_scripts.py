import regex as re
from kdmt.text import clean_text

def fix_formating(text):

    text = text.replace(u'\\xa333', u' ')
    text = text.replace(u'\\u2019', u'\'')
    text = text.replace(u'\\x1b', u'\'')
    text = text.replace(u'\\u001b', u'\'')

    text = text.replace(u'\\xb4', u'\'')
    text = text.replace(u'\\xa0', u' ')
    text = text.replace(u'\\xa0', u' ')
    text = text.replace(u'f\\xfcr', u'\'s')
    text = text.replace(u'\\xa', u' x')
    text = text.replace(u'x000D', u'\n')
    text = text.replace(u'.à', u' a')
    text = text.replace(u' ', u'')
    text = text.replace('...', '.')
    text = text.replace('..', '.')
    text = text.replace(' .', '. ')
    text = text.replace('\r\n', '\n')
    text = text.replace('\xa0', ' ').replace('：', ': ').replace('\u200b', '').replace('\u2026', '...').replace('’', "'")
    text = text.replace('...', '.')
    text = text.replace('..', '.')
    text = re.sub(r':\s+', ': ', text)
    #    text = text.replace('\\r', '. ')
    text = text.replace(' .', '. ')
    text = re.sub(r':\s?\.', ':', text)

    return text.strip('\n').strip().strip('\n')



if __name__ == '__main__':
    mail = "[1235456] hi how are you"
    print(clean_text(mail))
