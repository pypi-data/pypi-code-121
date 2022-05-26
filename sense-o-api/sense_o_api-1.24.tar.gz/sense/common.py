import ast
import json


def evalInput(inText):
    if not inText:
        return {}
    if isinstance(inText, (list, dict)):
        return inText
    try:
        inText = ast.literal_eval(inText)
    except ValueError as ex:
        inText = json.loads(inText)
    except SyntaxError as ex:
        print("SyntaxError: Failed to literal eval dict. Err:%s " % ex)
    return inText


def loadJSON(path):
    file = open(path)
    ret = json.load(file)
    file.close()
    return ret
