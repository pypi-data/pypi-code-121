import re

typeRe = re.compile('^(str|int|list|dict)')
commonVariableNameRe = re.compile('(?<=\s)(.*)(?=:)')
commonVariableValueRe = re.compile('(?<=:\s)(.*)(?=\Z)')
listVariableName = re.compile('(?<=[A-z]\s)(.*)(?=:\Z)')
listValueRe = re.compile('(?<=-\s)(.*)(?=\Z)')

def load(code):
    code = code.strip().split('\n')
    dataCode = {}
    lastVariable = ''

    for line in code:
        if typeRe.search(line):
            lastVariable = commonVariableNameRe.findall(line)[0]

            if commonVariableValueRe.search(line):
                if line.startswith('str'):
                    dataCode[lastVariable] = commonVariableValueRe.findall(line)[0]

                elif line.startswith('int'):
                    dataCode[lastVariable] = int(commonVariableValueRe.findall(line)[0])

            elif listVariableName.search(line):
                if line.startswith('list'):
                    dataCode[lastVariable] = []

                elif line.startswith('dict'):
                    dataCode[lastVariable] = {}

        elif commonVariableValueRe.search(line):
            name = commonVariableNameRe.findall(line)[0]
            value = commonVariableValueRe.findall(line)[0]

            dataCode[lastVariable][name] = value

        elif listValueRe.search(line):
            value = listValueRe.findall(line)[0]

            dataCode[lastVariable].append(value)

    return dataCode

def dump(dictionary):
    datalang = ''

    for key in dictionary:
        keyValue = dictionary.get(key)

        if isinstance(keyValue, (str, int)):
            valueType = str(type(keyValue))[8:11]
            datalang += f'{valueType} {key}: {keyValue}\n'

        elif isinstance(keyValue, dict):
            datalang += f'dict {key}:\n'

            for dictKey in keyValue:
                datalang += f'- {dictKey}: {keyValue.get(dictKey)}\n'

        else:
            datalang += f'list {key}:\n'

            for value in keyValue:
                datalang += f'- {value}\n'

        datalang += '\n'

    return datalang

def loadFile(fileObject):
    with open(fileObject) as fileObject:
        loaded = load(fileObject.read())

    return loaded

def dumpFile(fileObject, dictionary):
    with open(fileObject, 'w+') as fileObject:
        dumpedData = dump(dictionary)

        fileObject.write(dumpedData)