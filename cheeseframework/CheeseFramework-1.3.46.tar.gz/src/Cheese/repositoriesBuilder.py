#cheese

import os
import re

from Cheese.resourceManager import ResMan
from Cheese.finder import Finder

class RepositoriesBuilder:

    @staticmethod
    def build(parent):
        repositories = []

        for root, dirs, files in os.walk(ResMan.root()):
            for file in files:
                if (not file.endswith(".py")): continue

                path = os.path.join(root, file)

                if (Finder.isSomething(path, "repository")): 
                    repositories.append(path)

        parent.doJson(repositories, "REPOSITORIES", 
            ["REPOSITORY", "DBSCHEME", "DBMODEL"],
            [("QUERY", [("RETURN", "raw")]), ("COMMIT", [])])

        for repo in parent.dictJson["REPOSITORIES"].keys():
            scheme = parent.dictJson["REPOSITORIES"][repo]["DBSCHEME"]
            pk = re.search("\((?P<pk>\w+),.*", scheme)
            parent.dictJson["REPOSITORIES"][repo]["PRIMARY_KEY"] = pk["pk"]

        RepositoriesBuilder.preQueries(parent)
        RepositoriesBuilder.preCommits(parent)
    

    # prefabricated query methods
    @staticmethod
    def preQueries(parent):
        for repoKey in parent.dictJson["REPOSITORIES"].keys():
            repo = parent.dictJson["REPOSITORIES"][repoKey]

            repo["METHODS"]["findAll"] = {
                "QUERY": f"select * from {repo['REPOSITORY']};",
                "RETURN": "array"
            }
            repo["METHODS"]["find"] = {
                "QUERY": f"select * from {repo['REPOSITORY']} where {repo['PRIMARY_KEY']}=:primaryKey;",
                "RETURN": "one"
            }
            repo["METHODS"]["findBy"] = {
                "QUERY": f"select * from {repo['REPOSITORY']} where :columnName=:value;",
                "RETURN": "array"
            }
            repo["METHODS"]["findOneBy"] = {
                "QUERY": f"select * from {repo['REPOSITORY']} where :columnName=:value;",
                "RETURN": "one"
            }
            repo["METHODS"]["findNewId"] = {
                    "QUERY": f"select max(id) from {repo['REPOSITORY']};",
                    "RETURN": "num"
                }

    # prefabricated commit methods 
    @staticmethod
    def preCommits(parent):
        for repoKey in parent.dictJson["REPOSITORIES"].keys():
            repo = parent.dictJson["REPOSITORIES"][repoKey]
            scheme = repo["DBSCHEME"]
            name = repo["REPOSITORY"]

            repo["METHODS"]["save"] = {
                    "COMMIT": f"insert into {name} {scheme} values :obj;",
                    "RETURN": ""
                }
            
            repo["METHODS"]["update"] = {
                    "COMMIT": f"update {name} set {scheme} = :obj where {repo['PRIMARY_KEY']}=:obj.{repo['PRIMARY_KEY']};",
                    "RETURN": ""
                }

            repo["METHODS"]["delete"] = {
                    "COMMIT": f"delete from {name} where {repo['PRIMARY_KEY']}=:model.{repo['PRIMARY_KEY']};",
                    "RETURN": ""
                }