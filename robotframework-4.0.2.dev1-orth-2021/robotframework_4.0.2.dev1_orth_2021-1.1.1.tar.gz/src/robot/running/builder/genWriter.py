from robot.parsing import get_model, Token
from robot.parsing.model.statements import KeywordCall

SPACE = "    "
LINE = "\n"


def SettingWriter(model, out_dir, file):
    # Setting
    global settingTitle
    for settingTitle in list(model.header.tokens):
        settingTitle = settingTitle.value
        if not file:
            write_dir = out_dir
        else:
            write_dir = out_dir + "/" + file
        fp = open(write_dir, "a+", encoding="utf-8")
        fp.write(settingTitle + LINE)
        fp.close()
        # print(settingTitle)
    for setting in list(model.body):
        # 对于每一个测试用例中进行遍历
        get_variable(setting, settingTitle, out_dir, file)


def VariableWriter(model, out_dir, file):
    # Variable
    global variableTitle
    for variableTitle in list(model.header.tokens):
        variableTitle = variableTitle.value
        if not file:
            write_dir = out_dir
        else:
            write_dir = out_dir + "/" + file
        fp = open(write_dir, "a+", encoding="utf-8")
        fp.write(variableTitle + LINE)
        fp.close()
        # print(variableTitle)
    for variable in list(model.body):
        # 对于每一个测试用例中进行遍历
        get_variable(variable, variableTitle, out_dir, file)


def CaseWriter(model, out_dir, orth_vars, file):
    # Test Cases
    # for key in orth_vars:

    global testcaseTitle
    for testcaseTitle in list(model.header.tokens):
        testcaseTitle = testcaseTitle.value
        if not file:
            write_dir = out_dir
        else:
            write_dir = out_dir + "/" + file
        fp = open(write_dir, "a+", encoding="utf-8")
        fp.write(testcaseTitle + LINE)
        fp.close()
        # print(testcaseTitle)
    for testcase in list(model.body):
        namelist = testcase.name.split('@%')
        casename = namelist.pop(0)
        if not file:
            write_dir = out_dir
        else:
            write_dir = out_dir + "/" + file
        fp = open(write_dir, "a+", encoding="utf-8")
        fp.write(casename + LINE)
        fp.close()
        # print(casename)
        # 对于每一个测试用例中进行遍历
        casestr = str(testcase.body)
        if not "TAGS" in casestr:
            new_tag_node(orth_vars, namelist, model, testcase.name)
        if "\\" in casestr and ": FOR" in casestr:
            # 对for关键字进行重构
            refactor_for(model.body)


        for testline in testcase.body:
            # new_tag_node(namelist, namelist, casename, model)
            get_variable(testline, testcaseTitle, out_dir, file, orth_vars, namelist, casestr)


def KeywordWriter(model, out_dir, file):
    # Keyword
    global keywordTitle, new_model
    for keywordTitle in list(model.header.tokens):
        keywordTitle = keywordTitle.value

        if not file:
            write_dir = out_dir
        else:
            write_dir = out_dir + "/" + file
        fp = open(write_dir, "a+", encoding="utf-8")
        fp.write(keywordTitle + LINE)
        fp.close()


    for keyword in list(model.body):
        # 对于每一个测试用例中进行遍历
        if "\\" in str(keyword.body) and ": FOR" in str(keyword.body):
            # 对for关键字进行重构
            refactor_for(model.body)
        get_variable(keyword, keywordTitle, out_dir, file)


def get_variable(model, name, out_dir, file, *args):
    if not file:
        write_dir = out_dir
    else:
        write_dir = out_dir + "/" + file
    fp = open(write_dir, "a+", encoding="utf-8")

    if hasattr(model, "tokens"):

        for token in model.tokens:

            if "Test Cases" in name:

                # key=list(args[0].keys())
                key = args[0]
                value = args[1]
                casestr = args[2]
                orthValue = dict(zip(key, value))

                if "TAGS" in casestr:
                    fp.write(SPACE + token.value)
                    # print(SPACE + token.value, end='')
                    if "TAGS" in token.type:
                        for key in orthValue:
                            fp.write(SPACE + key + "=" + orthValue[key])
                            # print(SPACE + key + "=" + orthValue[key], end='')
                    continue
                else:
                    fp.write(SPACE + token.value)
                    # print(SPACE + token.value, end='')
                continue

            if "Settings" in name:
                fp.write(token.value + SPACE)
                # print(token.value + SPACE, end='')
                continue
            if "Variables" in name:
                fp.write(token.value + SPACE)
                # print(token.value + SPACE, end='')
                continue
            if "Keywords" in name:
                if token.type == "KEYWORD NAME":
                    fp.write(token.value + SPACE)
                    # print(token.value + SPACE, end='')
                    continue
            fp.write(SPACE + token.value)
            # print(SPACE + token.value, end='')

        # print("")
        fp.write(LINE)
        fp.close()
    else:
        if hasattr(model, "header"):
            get_variable(model.header, name, out_dir, file, *args)
        if hasattr(model, "body"):
            for line in model.body:
                get_variable(line, name, out_dir, file, *args)
        if hasattr(model, "sections"):
            for sections in model.sections:
                get_variable(sections, name, out_dir, file, *args)
        if hasattr(model, "orelse"):
            get_variable(model.orelse, name, out_dir, file, *args)
        if hasattr(model, "end"):
            get_variable(model.end, name, out_dir, file, *args)


def new_tag_node(orthkey, orthname, model, casename):
    global tag_body
    orthValue = dict(zip(orthkey, orthname))
    str = []
    for key in orthValue:
        str.append(key + "=" + orthValue[key] + SPACE)
    str = ''.join(str)
    tag_body = get_model("[Tags]" + SPACE + str)

    for list in model.body:
        if (list.name == casename):
            list.body.insert(0, tag_body)
    tag_body = []


def refactor_for(model):

    new_keyword = KeywordCall([
        Token(Token.KEYWORD,Token.END),
    ])

    for keyword in model:
        if hasattr(keyword, "body"):

                for index, keywordCall in enumerate(keyword.body):
                    if hasattr(keywordCall,"keyword"):
                        if keywordCall.keyword == '\\' and index==len(keyword.body)-1:
                            keyword.body.insert(index + 1, new_keyword)
                            break
                        elif keywordCall.keyword == '\\' and not hasattr(keyword.body[index+1],"keyword") or keywordCall.keyword == '\\' and keyword.body[index+1].keyword != '\\' and keyword.body[index+1].keyword != 'END':
                            keyword.body.insert(index+1,new_keyword)
                    else:
                        continue

                for index, keywordCall in enumerate(keyword.body):
                    if hasattr(keywordCall, "keyword"):
                        if keywordCall.keyword == ': FOR':
                            keywordCall.tokens[0].value = 'FOR'
                        if keywordCall.keyword == '\\':
                            keywordCall.tokens[0].value = ''
                    else:
                        continue
    return keyword
