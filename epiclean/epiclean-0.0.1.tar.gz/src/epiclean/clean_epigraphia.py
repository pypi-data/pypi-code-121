import re

# This file contains the actual functionality of the processor
def processor(input, lang, e, o, s, n):
    if lang == 'kn':
        output = input
        if e:
            output = re.sub('é', 'ē', output)
        if o:
            output = re.sub('ô', 'ō', output)
        if s:
            output = re.sub('[sS$gé]ri', 'śrī', output)
        if n:
            output = re.sub('nk', 'ṅk', output)
            output = re.sub('ng', 'ṅg', output)

            output = re.sub('nc', 'ñc', output)
            output = re.sub('nj', 'ñj', output)

            output = re.sub('nṭ', 'ṇṭ', output)
            output = re.sub('nḍ', 'ṇḍ', output)
        return output
    else:
        return None
