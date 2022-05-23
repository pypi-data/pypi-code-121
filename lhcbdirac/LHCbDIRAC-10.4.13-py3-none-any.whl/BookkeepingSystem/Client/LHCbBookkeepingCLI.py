###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Bookkeeping file system."""
import sys
import cmd
import pydoc
import shlex
import argparse

from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers
from LHCbDIRAC.Interfaces.API.DiracLHCb import DiracLHCb
from LHCbDIRAC.BookkeepingSystem.Client.LHCB_BKKDBClient import LHCB_BKKDBClient


class LHCbBookkeepingCLI(cmd.Cmd):
    """class."""

    #############################################################################

    def __init__(self):
        """constructor."""
        cmd.Cmd.__init__(self)
        self.prompt = "$[/]$"
        self.bk = LHCB_BKKDBClient()
        self.diracAPI = DiracLHCb()
        self.currentPath = "/"
        self.do_setDataQualityFlags("OK")
        self.saveParser = argparse.ArgumentParser(description="Save LFNS", prog="save")
        self.saveParser.add_argument("filename", type=str, help="file name")
        self.saveParser.add_argument("-f", "--format", help="txt or py")
        self.saveParser.add_argument("-n", "--num", help="number of files to be saved")
        self.saveParser.add_argument("-c", "--with-fileCatalog", help="save POOL XML catalog in a given site")
        self.sites = {}
        self.sites = DMSHelpers().getShortSiteNames(withStorage=False, tier=(0, 1))

    #############################################################################
    def addCurrentPath(self, path):
        """add a path."""
        if path[0] != "/" and len(self.currentPath) == 1:
            self.currentPath += path
        else:
            self.currentPath += "/" + path

    #############################################################################
    def __printPrompt(self, path=None):
        """prints the prompt."""
        if path is None:
            path = "/"
        self.prompt = "$[" + path + "]$"

    #############################################################################
    def __bklist(self, path):
        """list a path."""
        retVal = self.bk.list(path)
        return retVal

    def __bkListAll(self, path):
        """list the directory with metadata.

        This is equivalent to ls -a
        """
        if path == "":
            path = self.currentPath
        res = self.bk.list(path)
        for i in res:
            print(i["name"])
            for j in i:
                if j not in ["fullpath", "selection", "expandable", "method", "level", "name"]:
                    print("   ", j, i[j])

    #############################################################################
    def __checkDirectory(self, path):
        """is empty directory."""
        res = self.bk.list(path)
        retValue = False
        if res:
            retValue = True
        return retValue

    #############################################################################
    def __rootDirectory(self):
        """root."""
        self.currentPath = "/"
        self.__printPrompt(self.currentPath)

    #############################################################################
    def __oneLevelback(self, logical=False):
        """cd .."""
        path = self.currentPath.split("/")
        if path[0] == "" and path[1] == "":
            if not logical:
                self.currentPath = "/"
                self.__printPrompt(self.currentPath)
            else:
                return "/"
        else:
            newpath = ""
            for i in range(len(path) - 1):
                if path[i] != "":
                    newpath += "/" + path[i]
            if newpath == "":
                newpath = "/"
            if not logical:
                self.currentPath = newpath
                self.__printPrompt(self.currentPath)
            else:
                return newpath

    #############################################################################
    @staticmethod
    def help_ls():
        """provides help."""
        print("Usage: ls [OPTION]... [FILE]...")
        print("List information about the FILEs (the current directory by default).")
        print(" Available options: -a")
        print("Usage: ls or ls -a")
        print("ls -a [FILE]")
        print("Note: You can do paging using the | more")
        print("For example: ls | more")

    @staticmethod
    def help_cd():
        """help cd command."""
        print(" cd <dir>")
        print("cd ..")
        print("cd /")
        print("cd")

    #############################################################################
    def do_ls(self, path):
        """ls command."""
        paging = False
        if path.find("|") > -1:
            tmpPath = path.split("|")
            path = ""
            for i in range(len(tmpPath) - 1):
                path += tmpPath[i].strip()
            paging = True

        text = ""
        if len(path) > 0 and path[0] == "-":
            try:
                if path[1] != "a":
                    print("ls: invalid option -- {}".format(path[1]))
                    print("Try `help ls' for more information.")
                else:
                    path = path[2:]
                    self.__bkListAll(path)
            except IndexError as e:
                print("Invalid oprion:", e)
        else:
            if path == "":
                path = self.currentPath
            res = self.__bklist(path)
            for i in sorted(res, key=lambda x: x["fullpath"]):
                if paging:
                    text += i["name"] + "\n"
                else:
                    print(i["name"])
        if paging:
            pydoc.ttypager(text)

    #############################################################################
    def do_list(self, path):
        """list commamd."""
        pass

    #############################################################################
    def do_save(self, command):
        """save command."""
        try:
            args = self.saveParser.parse_args(shlex.split(command))
        except argparse.ArgumentError as exc:
            print(exc)
        except SystemExit:
            self.saveParser.print_help()
            return
        if args.format is None:
            args.format = "txt"

        retVal = self.bk.list(self.currentPath)
        files = None
        if retVal:
            if "FileName" not in retVal[0]:
                print("No file found belong to {} bookkeeping path!".format(self.currentPath))
                return
            else:
                files = retVal
        else:
            print(retVal)
            return
        if args.num is not None:
            try:
                nb = int(args.num)
            except ValueError as v:
                print(v)
                return
            nbOfFiles = nb
        else:
            nbOfFiles = len(files)

        lfns = {}
        for i in range(nbOfFiles):
            lfns[files[i]["FileName"]] = files[i]

        if args.with_fileCatalog:
            site = args.with_fileCatalog
            lfnList = list(lfns)
            totalFiles = len(lfnList)
            ff = args.filename.split(".")
            catalog = ff[0] + ".xml"
            retVal = self.diracAPI.getInputDataCatalog(lfnList, site, catalog, True)
            nbofsuccsessful = 0
            if retVal["OK"]:
                slist = {}
                faild = {}
                if "Successful" in retVal["Value"]:
                    slist = retVal["Value"]["Successful"]
                if "Failed" in retVal["Value"]:
                    faild = retVal["Value"]["Failed"]
                nbofsuccsessful = len(slist)
                nboffaild = len(faild)
                exist = {}
                for i in slist:
                    exist[i] = lfns[i]

                self.bk.writeJobOptions(exist, args.filename, savedType=None, catalog=catalog, savePfn=slist)

                message = "Total files:" + str(totalFiles) + "\n"
                if site is not None:
                    if nbofsuccsessful:
                        message += str(nbofsuccsessful) + " found " + site + "\n"
                    if nboffaild:
                        message += str(nboffaild) + " not found " + site
                print(message)
                return
        if args.format == "txt":
            text = self.bk.writeJobOptions(lfns, "", args.format)
        elif args.format == "py":
            text = self.bk.writeJobOptions(lfns, args.filename, args.format)

        with open(args.filename, "w") as f:
            f.write(text)

    #############################################################################
    def do_cd(self, path):
        """cd command."""
        newpath = self.currentPath + "/" + path
        if path == "":
            self.currentPath = "/"
            self.__printPrompt(self.currentPath)
        elif path == "..":
            self.__oneLevelback()
        elif path == "/":
            self.__rootDirectory()
        elif path[0] == "/":
            if self.__checkDirectory(path):
                self.currentPath = path
                self.__printPrompt(self.currentPath)
            else:
                print("No such file or directory.")
        elif self.__checkDirectory(newpath):
            self.addCurrentPath(path)
            self.__printPrompt(self.currentPath)
        else:
            print("No such file or directory.")

    #############################################################################
    def do_pwd(self, path):
        """pwd command."""
        print(self.currentPath)

    #############################################################################
    def do_queries(self, command=""):
        """execute query."""
        retVal = self.bk.getPossibleParameters()
        print("The following bookkeeping query types are available:")
        for i in retVal:
            print(" ".rjust(10) + i)
        print("You can change the query types using the 'use' command")

    #############################################################################
    def do_use(self, command):
        """use command."""
        self.bk.setParameter(str(command))
        self.do_cd("/")

    #############################################################################
    @staticmethod
    def help_use():
        """help of use command."""
        print("Usage:")
        print("  use type".rjust(10))
        print("Arguments:")
        print(" type: bookkeeping query type".rjust(10))
        print("The 'type' can be found using the 'queries' command!")
        print("EXAMPE:")
        print(" ".rjust(10) + "use 'Event type'")

    #############################################################################
    @staticmethod
    def help_queries():
        """help of queries command."""
        print("This method shows the available query types!")
        print("Usage:")
        print("  queries")
        print("You can choose a query type using the 'use' command  ")
        print(" NOTE: the default query type is 'Configuration'")

    #############################################################################
    def do_advanceQuery(self, command=""):
        """advancedQuery command."""
        self.bk.setAdvancedQueries(True)
        self.do_cd("/")

    #############################################################################
    @staticmethod
    def help_advanceQuery():
        """help."""
        print("It allows to see more level of the Bookkeeping Tree")
        print("Usage:")
        print("   advanceQuery")

    #############################################################################
    def do_standardQuery(self, command=""):
        """command."""
        self.bk.setAdvancedQueries(False)
        self.do_cd("/")

    #############################################################################
    @staticmethod
    def help_standardQuery():
        """help."""
        print("This is used by default")
        print("It shows a reduced bookkeeping path.")
        print("Usage:")
        print("   standardQuery")

    #############################################################################
    def do_dataQuality(self, command=""):
        """command."""
        print("The following Data Quality flags are available in the bookkeeping!")
        retVal = self.bk.getAvailableDataQuality()
        if retVal["OK"]:
            for i in retVal["Value"]:
                print(" ".ljust(10) + i)
        else:
            print(retVal["Message"])
        print("To set the data quality flags you have to use 'setDataQualityFlags' command!")
        print("More information: 'help setDataQualityFlags'")

    #############################################################################
    @staticmethod
    def help_dataQuality():
        """help."""
        print("This command shows the available data quality flags.")
        print("Usage:")
        print("  dataQuality")
        print("To change the data quality flag use the setDataQualityFlags command")

    #############################################################################
    def do_setDataQualityFlags(self, command):
        """command."""
        qualities = command.split(" ")
        if len(qualities) > 0:
            dataquality = {}
            for i in qualities:
                dataquality[i] = True
            self.bk.setDataQualities(dataquality)
        else:
            print("ERROR: Please give a data quality flag!")

    #############################################################################
    def __moreInfoProcpass(self, command):
        """more information of a directory."""
        found = False
        retVal = self.bk.getProcessingPassSteps({"StepName": command})
        if retVal["OK"]:
            proc = retVal["Value"]
            print("{0} {1} step found in the bkk".format(proc["TotalRecords"], command))
            for i in proc["Records"]:
                print(" ".ljust(5) + i)
                for j in proc["Records"][i]:
                    print(" ".ljust(10) + str(j[0]) + ":" + str(j[1]))
                found = True
        else:
            print("ERROR: ", retVal["Message"])
        return found

    #############################################################################
    def do_moreinfo(self, command=""):
        """more info command."""
        if command == "":
            previouspath = self.__oneLevelback(self.currentPath)
            values = self.__bklist(previouspath)
            name = self.currentPath.split("/")
            for i in values:
                if "level" in i and i["level"] == "FileTypes":
                    path = self.currentPath
                    retVal = self.bk.getLimitedFiles({"fullpath": str(path)}, ["nb"], -1, -1)
                    if not retVal["OK"]:
                        print(retVal["Message"])
                        return
                    print("The selected dataset is:")
                    for selected in retVal["Value"]["Extras"]["Selection"]:
                        print("".ljust(5) + selected + " " + str(retVal["Value"]["Extras"]["Selection"][selected]))
                    print("Statistics:")
                    print(" ".ljust(5) + "Number of files:" + str(retVal["Value"]["TotalRecords"]))
                    for selected in retVal["Value"]["Extras"]["GlobalStatistics"]:
                        print(
                            "".ljust(5) + selected + " " + str(retVal["Value"]["Extras"]["GlobalStatistics"][selected])
                        )
                    break
                if i["name"] == name[len(name) - 1]:
                    for j in i:
                        if j not in ["fullpath", "selection", "expandable", "method", "level", "name"]:
                            print("   ", j, i[j])
                if "level" in i and i["level"] == "Processing Pass":
                    found = self.__moreInfoProcpass(command)
                    break
        else:
            values = self.__bklist(self.currentPath)
            found = False
            for i in values:
                if i["name"] == command:
                    for j in i:
                        if j not in ["fullpath", "selection", "expandable", "method", "level", "name"]:
                            print("   ", j, i[j])
                    found = True
                if "level" in i and i["level"] == "Processing Pass":
                    found = self.__moreInfoProcpass(command)
                    break

            if not found:
                print(" The '%s' does not found" % (command))

    def do_sites(self, command):
        print("T0/1 sites: %s" % ",".join(site for site in self.sites))

    @staticmethod
    def help_sites(self):
        """help."""
        print("it returns a list of T1 sites")

    #############################################################################
    @staticmethod
    def help_setDataQualityFlags():
        """help."""
        print("This command allows to use different data quality flags.")
        print("Usage:")
        print("  setDataQualityFlags flag1 [flag2 flag3, ... flagN]")
        print("Arguments:")
        print("  flag[1...N]:  Data quality flags.")
        print("For example:")
        print(" ".ljust(10) + "setDataQualityFlags OK UNCHECKED")

    #############################################################################
    @staticmethod
    def help_EOF():
        """quit."""
        print("Quits the program")

    #############################################################################
    def do_EOF(self, line):
        """quit command."""
        sys.exit()

    #############################################################################
    def help_save(self):
        """help."""
        self.saveParser.print_help()

    #############################################################################
    @staticmethod
    def help_moreinfo():
        """help method."""
        print("Display the statistics of the selected data.")
        print("Usage:")
        print("  moreinfo")
