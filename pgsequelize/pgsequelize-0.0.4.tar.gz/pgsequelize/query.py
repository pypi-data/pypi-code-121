from execute import excecute
from constants.strings import k500Error


def getTableWhereData(entity, attributes, options):
    try:
        return excecute(entity, attributes, options, 'SELECT', 'ALL')
    except Exception as e:
        return k500Error
