"""
This module contains utiliy functions for testIDEA diagrams.
Always import this module for argument parsing, as command line
arguments passed by testIDEA to scripts may change in future versions.

(c) iSYSTEM Labs, 2015
"""


from __future__ import print_function

import os
import sys
import argparse
import subprocess as sp


# This class is needed, because base class calls sys.exit() in case of
# argument error. This presents no problem when scripts are called from
# testIDEA, as stderr is logged and then execution of next test continues.
# However, when scripts are called by Python test execution script, which
# imports this script as a module, then sys.exit() would terminate test
# execution completly. This class enables the main script to catch
# exception with informative error message.
class ArgumentParserWException(argparse.ArgumentParser):
    """
    This class throws exception in case of error, while base class
    calls sys.exit().
    """
    def error(self, message):
        message = 'Error in command line args: ' + self.format_usage() + '\n' + \
                  message + '\n' + \
                  'Command line: ' + ' '.join(self.args)
        raise Exception(message)


    def parse_args(self, cmdLineArgs):
        # save args to improve error reporting when the script is called
        # from Python
        self.args = cmdLineArgs
        return super(ArgumentParserWException, self).parse_args(cmdLineArgs)


# This method is currently not used, as Python 27 should also run this code.
def checkVersion():
    """ Throws exception if Python version is less than 3. """
    if sys.version_info.major < 3:
        raise Exception("Unsupported Python version! Major version should " +
                        "be at least 3 but it is: " + sys.version)


def createGraphFileName(imageFileName, graphType):
    """ Creates file name by adding 'graphType' as an extension. """
    return imageFileName + '.' + graphType


def getImageTypeFromExtension(fileName):
    """
    Use this function to get image type used by graphwiz.
    This way changing file extension in testIDEA automatically
    produces image of the correct type.

    Run 'dot -T?' for available image types. Note that only
    bitmap images and SVG images can be displayed by testIDEA.
    """
    unquotedFileName = fileName.strip('"')
    ext = os.path.splitext(unquotedFileName)[1].lower()
    if len(ext) >= 0:
        ext = ext[1:] # remove the dot before extension
    else:
        ext = 'png'

    return ext


def createGraphImage(dotDir, graphFileName, outFileName):
    """
    This function runs grphwiz dot utiliy, which creates image
    file out of text description in dot format. Format of outpu
    file depends on outFileName extension. Extensions 'png' and
    'svg' are recommened as they are supported by dot, testIDEA
    and web browsers.

    Parameters:

    dorDir - directory, where dot.exe is located

    graphFileName - name of file with graph description in dot syntax

    outFileName - name of output file
    """

    print('    Output file: ', outFileName)

    imgType = getImageTypeFromExtension(outFileName)

    dotExe = os.path.join(dotDir, 'dot')
    cmd = '"' + dotExe + '" -T' + imgType + ' -o"' + outFileName + '" "' + graphFileName + '"'
    try:
        sp.check_call(cmd, shell=True)
    except Exception as ex:
        print("\nERROR: Can not run graphwiz 'dot' utility.", file=sys.stderr)
        print("  ", ex)
        print("    Please make sure that it is installed, and that input file has correct syntax.",
              file=sys.stderr)
        print("    See help (option -h) for instructions.", file=sys.stderr)
        print("    Command: ", cmd, '\n\n', file=sys.stderr)
        raise


def parseArgs(cmdLineArgs, userArgDefs):
    """
    This function parses standard command line parameters provided by
    testIDEA.

    Parameters:
    cmdLineArgs - args passed in command line

    userArgDefs - list of tuples for arg parser. If tuple contains three
                  items, it defines mandatory positional argument, its
                  default value, and help.
                  If it contains 4 items, the first one defines long option,
                  the second one option name, the third one defines
                  default value and the last one defines help string.
                  Please note, that outFileName is always the last non-optional
                  argument.
                  If it contains 5 items, the first one defines short option,
                  remaining items are the same as in 4 items tuple. If in
                  5 item tuple default value is False, this option does
                  not have value - its presense sets it to True, absence to False

                  'userArgDefs' argument may be set to None if there are no
                  user defined args.

    After return the following items are available:

        args.dotDir - directory where dot.exe and other graphwiz tools are
                      located

        args.outFileName - name of script output file. This name is used by
                           testIDEA to show the image.

        args.testID - ID of test case for which this diagram should be created.

        args.function - name of function tested

        args.profExport - name of profiler export file

        args.cvrgExport - name of coverage export file

        args.traceExport - name of trace export file

        args.analyzerDoc - name of analyzer document file

        ags.outFileName - name of the output image file

    If argument is not provided in command line, its value is empty string.
    """
    parser = ArgumentParserWException(description="Creates a graph.")

    parser.add_argument('--dot', dest="dotDir", default='',
                        help="If specified, dot utility is run from this path.")

    parser.add_argument('--testID', dest="testID", default='',
                        help="Test case ID.")

    parser.add_argument('--function', dest="functionName", default='',
                        help="Function under test.")

    parser.add_argument('--cvrgExport', dest="cvrgExport", default='',
                        help="Name of coverage export file.")

    parser.add_argument('--profExport', dest="profExport", default='',
                        help="Name of profiler export file.")

    parser.add_argument('--binTimeline', dest='isBinaryTimeline',
                        action='store_true',
                        help="if specified, timeline is read " +
                        "from binary file (input file + extension .BIN).")

    parser.add_argument('--traceExport', dest="traceExport", default='',
                        help="Name of trace export file.")

    parser.add_argument('--analyzerDoc', dest="analyzerDoc", default='',
                        help="Name of analyzer document file.")

    userArg = '\nUSER ARG: ' # users may specify this arg in testIDEA params column

    if userArgDefs != None:
        for argTuple in userArgDefs:
            if len(argTuple) == 3:
                parser.add_argument(dest=argTuple[0],
                                    default=argTuple[1],
                                    help=argTuple[2])
            elif len(argTuple) == 4:
                parser.add_argument(argTuple[0], dest=argTuple[1],
                                    default=argTuple[2],
                                    help=argTuple[3])
            elif len(argTuple) == 5:
                defaultValue = argTuple[3]
                if defaultValue == False:   # default value is not string!
                    parser.add_argument(argTuple[0], argTuple[1], dest=argTuple[2],
                                        action='store_true',
                                        help=userArg + argTuple[4])
                else:
                    parser.add_argument(argTuple[0], argTuple[1], dest=argTuple[2],
                                        default=defaultValue,
                                        help=userArg + argTuple[4])
            else:
                raise Exception("Number of items in userArgs tuple is expected " +
                                "to be 3 or 4, but it is: " + str(len(argTuple)) +
                                "   Tuple: " + argTuple +
                                "   userArgs: " + userArgDefs)


    parser.add_argument(dest="outFileName",
                        default=None,
                        help="Name of the output image file. " +
                        "It should have extension 'png' or 'svg'.")

    args = parser.parse_args(cmdLineArgs)

    return args
