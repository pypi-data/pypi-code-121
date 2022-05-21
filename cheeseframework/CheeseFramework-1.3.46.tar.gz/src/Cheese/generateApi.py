#cheese

import os

from Cheese.database import Database
from Cheese.resourceManager import ResMan
from Cheese.Logger import Logger
from Cheese.appSettings import Settings

from Cheese.createByDb import CreateByDB
from Cheese.createApi import ApiControllerCreator as ac

class ApiGenerator:

    @staticmethod
    def generateApi():
        Settings.loadSettings()

        Settings.allowDebug = False
        Logger.initLogger()

        if (os.path.exists(f"{ResMan.web()}/api.html")):
            accept = input("api.html already exists. Do you want to continue? Old file will be rewritten. [y/n]: ")
            if (accept != "y"):
                return

        print("[0] - fully automatic lite")
        print("         - api will be generated for every table and there will be only /create, /get, /getAll, /update and /delete")
        print("[1] - fully automatic heavy")
        print("         - api will be generated for every table and there will be /create, /get, /getAll, /update, /delete and /getBy for every column")
        print("[2] - semi automatic lite")
        print("         - api will be generated for every table and there will be only /create, /get, /getAll, /update and /delete")
        print("             but user can choose if endpoint will be generated or not")
        print("[3] - semi automatic heavy")
        print("         - api will be generated for every table and there will be /create, /get, /getAll, /update, /delete and /getBy for every column")
        print("             but user can choose if endpoint will be generated or not")
        print("[4] - fully manual - WIP")
        print("         - api will be generated with all endpoints")
        print("             but user can choose if endpoint will be generated or not")
        print("             and user can make custom endpoints")
        ApiGenerator.mode = input("Choose an option: ")
        try:
            ApiGenerator.mode = int(ApiGenerator.mode)
        except:
            print("Invalid option - Aborting")
            print("Option must be integer")
            return
        
        if (ApiGenerator.mode < 0 or ApiGenerator.mode > 4):
            print("Invalid option - Aborting")
            print("Option must be between <0, 4>")
            return

        ApiGenerator.mode = int(ApiGenerator.mode)

        ApiGenerator.create()

    @staticmethod
    def create():
        ApiGenerator.tableOfContents = ApiGenerator.createContents()
        content = ApiGenerator.createHeader() 
        apiContent = "\t<ol class=\"num\">\n"
        index = 1
        print(Settings.allowDB)

        if (not Settings.allowDB):
            print(10*"==")
            print("DATABASE IS NOT ALLOWED IN YOUR PROJECT")
            print("This is not a problem... just reminder... go on if you know what are you doing :)")
            print(10*"==")
        else:
            database = Database()
            database.connect()

            tables = database.query("SELECT tablename FROM pg_catalog.pg_tables where schemaname='public';")

            for table in tables:
                columns = database.query(f"SELECT column_name, data_type from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = N'{table[0]}';")
                for column in columns:
                    if (column[0] == "id"):
                        columns.remove(column)
                        columns = [column] + columns
                cont, index = ApiGenerator.createEndpoint(index, table, columns)
                apiContent += cont

        if (ApiGenerator.mode == 4):
            while True:
                if (input(f"Do you want to create custom main endpoint [y/n]: ") == "y"):
                    mainEndpointName = input("Name (without /): ")
                    cont, index = ApiGenerator.createEndpoint(index, (mainEndpointName,), [])
                    apiContent += cont
                else:
                    break

        content += ApiGenerator.tableOfContents
        content += "\t\t</ol>\n"
        content += "\t</div>\n\n\n"

        content += apiContent
        content += "\t</ol>\n\n\n\n"
        content += "</body>\n"
        content += "</html>"

        with open(f"{ResMan.web()}/api.html", "w") as f:
            f.write(content)

    @staticmethod
    def createHeader():
        content = "<html lang=\"cs\">\n"
        content += "<head>\n"
        content += "\t<meta charset='utf-8'>\n"
        content += "\t<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        content += "\t<link rel=\"stylesheet\" href=\"https://kubaboi.github.io/CheeseFramework/public/styles/style.css\">\n"
        content += "\t<link rel=\"stylesheet\" href=\"https://kubaboi.github.io/CheeseFramework/public/styles/prism.css\">\n"
        content += "\t<link rel=\"icon\" href=\"favicon.ico\" type=\"image/x-icon\">\n"
        content += f"\t<title>API - {Settings.name}</title>\n"
        content += "</head>\n"
        content += "<body>\n"
        content += "\t<script src=\"https://kubaboi.github.io/CheeseFramework/public/scripts/prism.js\"></script>\n\n"
        return content

    @staticmethod
    def createContents():
        content = "\t<div id=\"toc_container\">\n"
        content += "\t\t<p class=\"toc_title\">Contents</p>\n"
        content += "\t\t<ol>\n"
        
        return content

    @staticmethod
    def createEndpoint(index, table, columns):
        mainEndpointName = CreateByDB.removeSpaces(table[0], table[0][0])

        if (ApiGenerator.mode > 1):
            if (input(10*"=" + f"Create main endpoint /{mainEndpointName} ? [y/n]: ") != "y"):
                return ("", index)

        ApiGenerator.tableOfContents += "\t\t\t<li>\n"
        ApiGenerator.tableOfContents += f"\t\t\t\t<a href=\"#{index}\">/{mainEndpointName}</a>\n"
        ApiGenerator.tableOfContents += "\t\t\t\t<ol>\n"

        content = "\t\t<li class=\"num\">\n"
        content += f"\t\t\t<span class=\"hd2\" id=\"{index}\">/{mainEndpointName}</span>\n"
        content += "\t\t\t<ol class=\"num\">\n"

        if (ApiGenerator.mode <= 1):
            cont, count = ApiGenerator.lite(index, mainEndpointName, columns)
            content += cont
            if (ApiGenerator.mode == 1):
                for i, column in enumerate(columns):
                    cont, count = ApiGenerator.createGETBY(index, count+i, mainEndpointName, columns, column)
                    content += cont
        elif (ApiGenerator.mode == 2):
            cont, count = ApiGenerator.lite(index, mainEndpointName, columns, True)
            content += cont
        elif (ApiGenerator.mode >= 3):
            cont, count = ApiGenerator.lite(index, mainEndpointName, columns, True)
            content += cont
            for i, column in enumerate(columns):
                cont, count = ApiGenerator.createGETBY(index, count+i, mainEndpointName, columns, column, True)
                content += cont
            if (ApiGenerator.mode == 4):
                while True:
                    if (input(f"Do you want to create custom endpoint in {mainEndpointName} [y/n]: ") == "y"):
                        content += ApiGenerator.createCustom(index, count, mainEndpointName)
                        count += 1
                    else:
                        break

                    

        content += "\t\t\t</ol>\n"
        content += "\t\t</li>\n\n\n"

        ApiGenerator.tableOfContents += "\t\t\t\t</ol>\n"
        ApiGenerator.tableOfContents += "\t\t\t</li>\n"

        return (content, index+1)

    @staticmethod
    def lite(index, mainEndpointName, columns, ask=False):
        count = 1
        content = ""
        do = True
        if (ask):
            if (input(f"Create /{mainEndpointName}/create ? [y/n]: ") != "y"):
                do = False
        if (do):
            content += ApiGenerator.createCREATE(index, count, mainEndpointName, columns)
            count += 1
        do = True

        if (ask):
            if (input(f"Create /{mainEndpointName}/get ? [y/n]: ") != "y"):
                do = False
        if (do):
            content += ApiGenerator.createGET(index, count, mainEndpointName, columns)
            count += 1
        do = True

        if (ask):
            if (input(f"Create /{mainEndpointName}/getAll ? [y/n]: ") != "y"):
                do = False
        if (do):
            content += ApiGenerator.createGETALL(index, count, mainEndpointName, columns)
            count += 1
        do = True

        if (ask):
            if (input(f"Create /{mainEndpointName}/update ? [y/n]: ") != "y"):
                do = False
        if (do):
            content += ApiGenerator.createUPDATE(index, count, mainEndpointName, columns)
            count += 1
        do = True

        if (ask):
            if (input(f"Create /{mainEndpointName}/delete ? [y/n]: ") != "y"):
                do = False
        if (do):
            content += ApiGenerator.createDELETE(index, count, mainEndpointName)
            count += 1

        return (content, count)

    @staticmethod
    def printOptions(name, array):
        while True:
            print(10*"=")
            print(name)
            for i, opt in enumerate(array):
                print(f"[{i}] - {opt}")

            answer = input("Choose: ")
            try:
                answer = int(answer)
            except:
                print("Choise must be integer from 0 to " + str(len(array)-1))
                continue
            
            if (answer < 0 or answer >= len(array)):
                print("Choise must be integer from 0 to " + str(len(array)-1))
                continue

            break
        return array[answer]

    @staticmethod
    def createCustom(index, secondIndex, mainEndpoint):
        name = input("Name of endpoint (without /): ")
        method = ApiGenerator.printOptions("HTTP method", ["GET", "POST"])
        role = input("Role: ")
        accepts = ApiGenerator.printOptions("Accepts", ["nothing", "path arguments", "post body", "bytes"])
        if (accepts == "path arguments" or accepts == "post body"):
            acceptJson = input("Accept JSON: ")
        elif (accepts == "bytes"):
            acceptJson = "Accepts bytes"
        else:
            acceptJson = ""
        
        comment = input("Comment: ")

        responses = []
        while True:
            if (input("Add response [y/n]: ") == "y"):
                respName = input("Response [Name - Code]: ")
                respJson = input("JSON response: ")
                responses.append({"name": respName, "json": respJson})
            else:
                break

        print(f"Creating /{mainEndpoint}/{name}")
        content = "\t\t\t\t<li class=\"num\">\n"
        content += f"\t\t\t\t\t<span class=\"hd3\" id=\"{index}.{secondIndex}\">/{name} - {method}</span>\n"
        content += f"\t\t\t\t\t<p>{comment}</p>\n"
        content += f"\t\t\t\t\t<p class=\"role\">Role = {role}</p>\n"
        
        content += ApiGenerator.startFigure(f"Accepts {accepts}")
        content += acceptJson
        content += ApiGenerator.endFigure()

        for resp in responses:
            content += ApiGenerator.startFigure(f"Return {resp['name']}:")
            content += resp["json"]
            content += ApiGenerator.endFigure()

        ApiGenerator.tableOfContents += f"\t\t\t\t\t<li><a href=\"#{index}.{secondIndex}\">/{name}</a>\n"

        content += "\t\t\t\t</li>\n\n"

        return content

    @staticmethod
    def createGETBY(index, secondIndex, mainEndpoint, columns, column, ask=False):
        columnName = column[0][0].upper() + ac.toVariable(column[0])[1:]

        if (ask):
            if (input(f"Create /{mainEndpoint}/getBy{columnName} ? [y/n] ") != "y"):
                return ("", secondIndex)

        print(f"Creating /{mainEndpoint}/getBy{columnName}")
        content = "\t\t\t\t<li class=\"num\">\n"
        content += f"\t\t\t\t\t<span class=\"hd3\" id=\"{index}.{secondIndex}\">/getBy{columnName} - GET</span>\n"
        content += f"\t\t\t\t\t<p>Gets all {mainEndpoint} by {column[0].upper()}</p>\n"
        content += f"\t\t\t\t\t<p class=\"role\">Role = 1</p>\n"
        
        content += ApiGenerator.startFigure("Accepts path arguments:")
        content += ApiGenerator.getJson([column], "", True)
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return OK - 200:")
        content += "{\n"
        content += f"\t\"{mainEndpoint.upper()}\": [\n"
        content += ApiGenerator.getJson(columns, "\t\t", True)
        content += "\t]\n"
        content += "}\n"
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Bad request - 400:")
        content += ApiGenerator.getJson([("ERROR", "Wrong json structure")])
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Unauthorized - 401:")
        content += ApiGenerator.getJson([("ERROR", "Unauthorized access")])
        content += ApiGenerator.endFigure()

        ApiGenerator.tableOfContents += f"\t\t\t\t\t<li><a href=\"#{index}.{secondIndex}\">/getBy{columnName}</a>\n"

        content += "\t\t\t\t</li>\n\n"

        return (content, secondIndex+1)

    @staticmethod
    def createCREATE(index, secondIndex, mainEndpoint, columns):
        print(f"Creating /{mainEndpoint}/create")

        modelName = ac.getSingular(mainEndpoint)
        content = "\t\t\t\t<li class=\"num\">\n"
        content += f"\t\t\t\t\t<span class=\"hd3\" id=\"{index}.{secondIndex}\">/create - POST</span>\n"
        content += f"\t\t\t\t\t<p>Creates a new {modelName}</p>\n"
        content += f"\t\t\t\t\t<p class=\"role\">Role = 1</p>\n"
        
        content += ApiGenerator.startFigure("Accepts post body:")
        content += ApiGenerator.getJson(columns)
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return OK - 200:")
        content += ApiGenerator.getJson([("STATUS", f"{modelName} has been created")])
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Bad request - 400:")
        content += ApiGenerator.getJson([("ERROR", "Wrong json structure")])
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Unauthorized - 401:")
        content += ApiGenerator.getJson([("ERROR", "Unauthorized access")])
        content += ApiGenerator.endFigure()

        ApiGenerator.tableOfContents += f"\t\t\t\t\t<li><a href=\"#{index}.{secondIndex}\">/create</a>\n"

        content += "\t\t\t\t</li>\n\n"

        return content

    @staticmethod
    def createGET(index, secondIndex, mainEndpoint, columns):
        print(f"Creating /{mainEndpoint}/get")

        modelName = ac.getSingular(mainEndpoint)
        content = "\t\t\t\t<li class=\"num\">\n"
        content += f"\t\t\t\t\t<span class=\"hd3\" id=\"{index}.{secondIndex}\">/get - GET</span>\n"
        content += f"\t\t\t\t\t<p>Get {modelName} by ID</p>\n"
        content += f"\t\t\t\t\t<p class=\"role\">Role = 1</p>\n"
        
        content += ApiGenerator.startFigure("Accepts path arguments:")
        content += ApiGenerator.getJson([("ID", "bigint")], "", True)
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return OK - 200:")
        content += "{\n"
        content += ApiGenerator.getJson(columns, "\t", True, modelName)
        content += "}\n"
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Bad request - 400:")
        content += ApiGenerator.getJson([("ERROR", "Wrong json structure")])
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Unauthorized - 401:")
        content += ApiGenerator.getJson([("ERROR", "Unauthorized access")])
        content += ApiGenerator.endFigure()

        ApiGenerator.tableOfContents += f"\t\t\t\t\t<li><a href=\"#{index}.{secondIndex}\">/get</a>\n"

        content += "\t\t\t\t</li>\n\n"

        return content

    @staticmethod
    def createGETALL(index, secondIndex, mainEndpoint, columns):
        print(f"Creating /{mainEndpoint}/getAll")

        modelName = ac.getSingular(mainEndpoint)
        content = "\t\t\t\t<li class=\"num\">\n"
        content += f"\t\t\t\t\t<span class=\"hd3\" id=\"{index}.{secondIndex}\">/getAll - GET</span>\n"
        content += f"\t\t\t\t\t<p>Gets all {mainEndpoint}</p>\n"
        content += f"\t\t\t\t\t<p class=\"role\">Role = 1</p>\n"
        
        content += ApiGenerator.startFigure("Accepts nothing:")
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return OK - 200:")
        content += "{\n"
        content += f"\t\"{mainEndpoint.upper()}\": [\n"
        content += ApiGenerator.getJson(columns, "\t\t", True)
        content += "\t]\n"
        content += "}\n"
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Bad request - 400:")
        content += ApiGenerator.getJson([("ERROR", "Wrong json structure")])
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Unauthorized - 401:")
        content += ApiGenerator.getJson([("ERROR", "Unauthorized access")])
        content += ApiGenerator.endFigure()

        ApiGenerator.tableOfContents += f"\t\t\t\t\t<li><a href=\"#{index}.{secondIndex}\">/getAll</a>\n"

        content += "\t\t\t\t</li>\n\n"

        return content

    @staticmethod
    def createUPDATE(index, secondIndex, mainEndpoint, columns):
        print(f"Creating /{mainEndpoint}/update")

        modelName = ac.getSingular(mainEndpoint)
        content = "\t\t\t\t<li class=\"num\">\n"
        content += f"\t\t\t\t\t<span class=\"hd3\" id=\"{index}.{secondIndex}\">/update - POST</span>\n"
        content += f"\t\t\t\t\t<p>Updates {modelName}</p>\n"
        content += f"\t\t\t\t\t<p class=\"role\">Role = 1</p>\n"
        
        content += ApiGenerator.startFigure("Accepts post body:")
        content += ApiGenerator.getJson(columns, "", True)
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return OK - 200:")
        content += ApiGenerator.getJson([("STATUS", f"{modelName} has been updated")])
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Bad request - 400:")
        content += ApiGenerator.getJson([("ERROR", "Wrong json structure")])
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Unauthorized - 401:")
        content += ApiGenerator.getJson([("ERROR", "Unauthorized access")])
        content += ApiGenerator.endFigure()

        ApiGenerator.tableOfContents += f"\t\t\t\t\t<li><a href=\"#{index}.{secondIndex}\">/update</a>\n"

        content += "\t\t\t\t</li>\n\n"

        return content

    @staticmethod
    def createDELETE(index, secondIndex, mainEndpoint):
        print(f"Creating /{mainEndpoint}/delete")

        modelName = ac.getSingular(mainEndpoint)
        content = "\t\t\t\t<li class=\"num\">\n"
        content += f"\t\t\t\t\t<span class=\"hd3\" id=\"{index}.{secondIndex}\">/delete - POST</span>\n"
        content += f"\t\t\t\t\t<p>Deletes {modelName}</p>\n"
        content += f"\t\t\t\t\t<p class=\"role\">Role = 1</p>\n"
        
        content += ApiGenerator.startFigure("Accepts post body:")
        content += ApiGenerator.getJson([("ID", "bigint")], "", True)
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return OK - 200:")
        content += ApiGenerator.getJson([("STATUS", f"{modelName} has been deleted")])
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Bad request - 400:")
        content += ApiGenerator.getJson([("ERROR", "Wrong json structure")])
        content += ApiGenerator.endFigure()

        content += ApiGenerator.startFigure("Return Unauthorized - 401:")
        content += ApiGenerator.getJson([("ERROR", "Unauthorized access")])
        content += ApiGenerator.endFigure()

        ApiGenerator.tableOfContents += f"\t\t\t\t\t<li><a href=\"#{index}.{secondIndex}\">/delete</a>\n"

        content += "\t\t\t\t</li>\n\n"

        return content

    @staticmethod
    def startFigure(title):
        content = "\t\t\t\t\t<figure>\n"
        content += f"\t\t\t\t\t\t<figcaption>{title}</figcaption>\n"
        content += "\t\t\t\t\t\t<pre><code class=\"language-json\">\n"
        return content

    @staticmethod
    def endFigure():
        return "\t\t\t\t\t\t</code></pre></figure>\n"

    @staticmethod
    def getJson(columns, tabs="", id=False, name=""):
        if (name != ""): name = f"\"{name}\": "
        content = tabs + name.upper() + "{\n"
        for i, column in enumerate(columns):
            cName = column[0].upper()
            if (cName == "ID" and not id): continue
            
            content += f"{tabs}\t\"{cName}\": "

            if (column[1] == "text"):
                content += "\"str\""
            elif (column[1] == "bigint"):
                content += "0"
            elif (column[1] == "boolean"):
                content += "true"
            else:
                content += f"\"{column[1]}\""

            if (i < len(columns)-1):
                content += ","
            content += "\n"
        content += tabs + "}\n"
        return content