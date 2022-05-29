import psycopg2
from constants.strings import k500Error


def excecute(entity, attributes, options, type, subType):
    try:
        connection = getConnection(entity.database)
        cursor = connection.cursor()
        queryData = getFinalQuery(entity, attributes, options, type)
        cursor.execute(queryData)
        data = None
        if(subType == "ONE"):
            data = cursor.fetchone()
            if(data is None):
                return
        elif(subType == 'ALL'):
            data = cursor.fetchall()

        if(data is not None):
            data = convertToReadableData(data, cursor.description)

        cursor.close()
        connection.close()
        return data
    except Exception as e:
        return k500Error


def getConnection(database):
    try:
        connection = psycopg2.connect(
            host='localhost',
            database=database,
            user='postgres',
            password='postgres')
        return connection
    except Exception as e:
        return k500Error


def createTable(tablename, connection, schema):
    try:
        cursor = connection.cursor()
        sqlCreateTable = f'''
        create table "{tablename}" 
        (id bigint primary key, 
        consigmentNo varchar(15),
        loanId bigint not null,
        CONSTRAINT loanId
        FOREIGN KEY(loanId) 
	    REFERENCES loanTansaction(id))'''
        cursor.execute(sqlCreateTable)
        cursor.commit()
    except Exception as e:
        return k500Error


def getFinalQuery(entity, attributes, options, type):
    try:
        repository = entity.repository
        finalQuery = ""
        trail = ""
        publicString = f' FROM public."{repository}" '

        attributeString = convertAttributesToString(
            repository, attributes, options)

        joinString = ''
        if('include' in options):
            joinString = convertJoinToString(entity, options)

        if(type == "SELECT"):
            trail = "SELECT "

        whereString = ""
        if("where" in options):
            whereString = convertWhereToString(options["where"])

        finalQuery = trail + attributeString + publicString + joinString + whereString

        if("limit" in options):
            finalQuery += f'LIMIT {options["limit"]}'

        finalQuery += ' ;'
        return finalQuery
    except Exception as e:
        return k500Error


def convertAttributesToString(repository, attributes, options):
    try:
        finalQuery = ""
        isIncluded = False
        if("include" in options.keys()):
            isIncluded = True
        if(isIncluded == True):
            if(len(options['include']) == 0):
                isIncluded = False

        if len(attributes) == 0:
            return '*'

        for index, attribute in enumerate(attributes):
            if(isIncluded == True):
                finalQuery += f'"{repository}"."{attribute}"'
            else:
                finalQuery += f'"{attribute}"'
            isLastIndex = index == len(attributes) - 1
            if(isLastIndex == False):
                finalQuery = finalQuery + ', '

        if(isIncluded):
            includedAttributes = convertIncludedAttributes(options['include'])
            finalQuery += includedAttributes

        return finalQuery
    except Exception as e:
        return k500Error


def convertIncludedAttributes(includeList):
    try:
        finalQuery = ""
        for includeData in includeList:
            if("model" not in includeData):
                pass
            elif("attributes" not in includeData):
                pass
            repository = includeData["model"]
            attributes = includeData["attributes"]
            for index, attribute in enumerate(attributes):
                finalQuery += f'"{repository}"."{attribute}"'
                isLastIndex = index == len(attributes) - 1
                if(isLastIndex == False):
                    finalQuery += ', '

        if(len(finalQuery) > 0):
            finalQuery = ', ' + finalQuery
        return finalQuery
    except Exception as e:
        return k500Error


def convertWhereToString(where):
    try:
        finalWhere = ""
        trail = "WHERE "
        index = 0
        for key, value in where.items():
            if type(value) is dict:
                for _, dictValue in value.items():
                    finalWhere += f""""{key}" like '%{dictValue}%'"""
                continue

            finalWhere += f""""{key}" = '{value}'"""
            if(index != len(where.items()) - 1):
                finalWhere = finalWhere + " and "
            index = index + 1

        finalWhere = trail + finalWhere
        return finalWhere
    except Exception as e:
        return k500Error


def convertJoinToString(entity, options):
    try:
        repository = entity.repository
        finalQuery = 'FULL OUTER JOIN '

        for includeData in options['include']:
            if("model" not in includeData.keys()):
                pass
            targetRepo = includeData["model"]
            relationData = None
            for relation in entity.relations:
                if(targetRepo in relation.keys()):
                    relationData = relation[targetRepo]
                    break
            if(relationData == None):
                return

            foreignKey = relationData.foreignKey
            targetKey = relationData.targetKey
            finalQuery += f'public."{targetRepo}" ON public."{repository}"."{targetKey}" = public."{targetRepo}"."{foreignKey}" '
        return finalQuery
    except Exception as e:
        return k500Error


def convertToReadableData(rawData, columns):
    data = {}
    listData = []
    isValueList = type(rawData) is list
    if(isValueList == False):
        for column, value in zip(columns, rawData):
            columnName = column[0]
            data[columnName] = value
        return data

    else:
        for value in rawData:
            newData = {}
            for column, subValue in zip(columns, value):
                columnName = column[0]
                newData[columnName] = subValue
            listData.append(newData)
        return listData
