"""
 This script generates a call graph for a function from its
 symbol information.

 (c) iSYSTEM Labs, 2016
"""

from __future__ import print_function

import sys
import subprocess as sp

import isystem.connect as ic
import isystem.diagutils as diagutils


g_isDebug = False


def _createLinkLabel(label, address=''):
    if address:
        return '<font color="red">' + hex(address) + '</font><br/>' + label

    return label


def _createRank(firstNodeId, secondNodeId):
    return '{rank=same; ' + firstNodeId + '; ' + secondNodeId + '; }\n'


def _prefixNumbers(name):
    # numbers are treated differently by dot, so prefix addresses for
    # which functions are not known.
    if name.startswith('0x'):
        name = '_' + name
        return name, True

    return name, False


def _getPartition(functionName, dataCtrl2):
    qualNameParts = functionName.split(',,')
    if len(qualNameParts) == 1:
        return functionName, 0

    paths = ic.StrVector()
    fileNames = ic.StrVector()
    dataCtrl2.getPartitions(paths, fileNames)

    pyListFNames = list(fileNames)

    try:
        return qualNameParts[0], pyListFNames.index(qualNameParts[1])
    except:
        raise ValueError("Partition for '" + functionName + "' not found: " + qualNameParts[1])


def _writeCallGraph(outf,
                    callGraphNodesSet,
                    callGraphMap,
                    callGraphCountersMap,
                    functionUnderTest,
                    isShowCallsTo,
                    callTypesMap):

    outf.write('digraph G {\n')
    # font 10 in graphs should be big enough to be readable
    outf.write("  node[fontsize=10];\n")
    outf.write("  edge[fontsize=10];\n")

    if isShowCallsTo:
        outf.write("  graph [rankdir=BT];\n")

    funcUnderTestColor = 'cadetblue1'

    # write list of nodes (function names) with their graphical attributes
    for funcNode in callGraphNodesSet:
        funcNode, isNumber = _prefixNumbers(funcNode)
        outf.write('"' + funcNode + '"') # quotes are needed because scope and params: ::, ...

        # see http://www.graphviz.org/doc/info/colors.html
        if funcNode == functionUnderTest:
            color = funcUnderTestColor
        else:
            if isNumber:
                color = "azure"
            elif callTypesMap[funcNode] == ic.IConnectDebug.sFunctions:
                color = "darkseagreen1"
            elif callTypesMap[funcNode] == ic.IConnectDebug.sLabels:
                color = "linen"
            else:
                color = "firebrick1" # invalid type, color should never be used!

        outf.write('[style=filled, fillcolor="' + color + '"]')
        outf.write(';\n')

    # if the function is not called, add it as a special case
    if not functionUnderTest in callGraphNodesSet:
        outf.write('"' + functionUnderTest + '"[style=filled, fillcolor="' +
                   funcUnderTestColor + '"];\n')

    # iterate map<string, set<string>>
    for caller, setOfCalled in callGraphMap.items():
        for called in setOfCalled:
            if called:
                caller, isNumber = _prefixNumbers(caller)
                called, isNumber = _prefixNumbers(called)

                if isShowCallsTo:
                    outf.write('"' + called + '"')
                    outf.write(' -> ')
                    outf.write('"' + caller + '"')
                else:
                    outf.write('"' + caller + '"')
                    outf.write(' -> ')
                    outf.write('"' + called + '"')

                outf.write(';\n')

    #outf.write('{ rank = sink;\n')
    #outf.write('Legend [shape=none, margin=0, label="12.12.2015"]\n}')
    #outf.write('  subgraph cluster_01 {label = "12.12.2015";}')
    # 'pos' attribute does not work for dot - would have to use neato!
    #outf.write('  dateNode [shape=none,margin=0,label="12.12.2015",fontsize=10,pos="10!,10!"];\n');
    outf.write('}\n')
    outf.close()


def _walkFuncTree(addrCtrl, funcMap, functionName, depth, isShowCallsTo,
                  allCalledFuncsSet, func2CalledSetMap, callTypesMap):

    #print("-- '" + functionName + "'")
    if functionName in funcMap:
        addrs = ic.AddressVector()
        func = funcMap[functionName]

        if isShowCallsTo:
            func.getCallsToFunction(addrs)
        else:
            func.getCallsFromFunction(addrs)

        funcNames = ic.StrVector()
        addrTypes = ic.IntVector()
        addrCtrl.getFunctionNames(addrs, funcNames, addrTypes)

        for idx in range(funcNames.size()):
            callTypesMap[funcNames[idx]] = addrTypes[idx]

        uniqFuncNames = set(funcNames) # eliminate duplicates, when the
                                       # same function is called at two addresses
        uniqFuncNames = list(uniqFuncNames) # order in set is not the same in two runs
        uniqFuncNames.sort()           # make it deterministic

        func2CalledSetMap[functionName] = uniqFuncNames

        for uniqFuncName in uniqFuncNames:

            # negative depth means infinite
            if (not uniqFuncName in allCalledFuncsSet)  and  depth != 0:

                allCalledFuncsSet.add(uniqFuncName)

                _walkFuncTree(addrCtrl, funcMap, uniqFuncName, depth - 1, isShowCallsTo,
                              allCalledFuncsSet, func2CalledSetMap, callTypesMap)
    else:
        print("Function not found: ", functionName)


def analyzeFunction(connectionMgr,
                    startFunctionName,
                    isAutoRank,
                    depth,
                    isShowScope, # namespace / class, not used as not required at the moment
                    isShowParameters, # not used as not required at the moment
                    isShowCallsTo,
                    outFile):
    """
    This is top-level function for creation of dot file. It iterates calls
    from the firt to the last depth and creates dot nodes and links
    of appropriate look.
    """

    dataCtrl2 = ic.CDataController2(connectionMgr)
    addrCtrl = ic.CAddressController(connectionMgr)

    startFunctionName, partition = _getPartition(startFunctionName, dataCtrl2)

    functions = ic.FunctionVector()
    dataCtrl2.getFunctions(partition, functions)
    funcMap = {}

    # put functions to map for faster search
    for func in functions:
        funcMap[func.getQualifiedName()] = func

    if not startFunctionName in funcMap:
        raise ValueError("Function not found in symbol info: '" + startFunctionName +
                         "'\nIf the name is not properly qualified, use the name as " +
                         "proposed in content asyst.")

    allCalledFuncsSet = set()
    func2CalledSetMap = {}
    callTypesMap = {}

    _walkFuncTree(addrCtrl, funcMap, startFunctionName, depth, isShowCallsTo,
                  allCalledFuncsSet, func2CalledSetMap, callTypesMap)

    _writeCallGraph(outFile, allCalledFuncsSet, func2CalledSetMap, None,
                    startFunctionName, isShowCallsTo, callTypesMap)


def _main(cmdLineArgs):

    opts = diagutils.parseArgs(cmdLineArgs,
                               [('-d',
                                 '--depth',
                                 'depth',
                                 -1,
                                 'defines how deep call tree should be traversed. -1 means ' +
                                 'infinite.'),
                                ('-t',
                                 '--callsTo',
                                 'isCallsTo',
                                 False,
                                 'if present, functions called from the given function are ' +
                                 'shown. If absent, functions whic call to the given function ' +
                                 'are shown.'),
                                ('-a',
                                 '--autoRank',
                                 'isAutoRank',
                                 False,
                                 'if present, then nodes are not ordered according to ' +
                                 'addresses, but to minimize length of links.'),
                                ('-o',
                                 '--open',
                                 'isOpenInSystemViewer',
                                 False,
                                 'if present, then generated diagram is opened in OS default ' +
                                 'viwer'),
                               ])

    cmgr = ic.ConnectionMgr()
    cmgr.connectMRU('')

    graphFileName = diagutils.createGraphFileName(opts.outFileName,
                                                  'statcallg')
    print('    Dot file: ', graphFileName)

    with open(graphFileName, 'w') as outf:

        if g_isDebug:
            print(' '.join(cmdLineArgs))

        analyzeFunction(cmgr,
                        opts.functionName,
                        opts.isAutoRank,
                        int(opts.depth),
                        False,
                        False,
                        opts.isCallsTo,
                        outf)

    # this statement must NOT be in with statement above. as outf must be
    # closed for dot to see complete file
    diagutils.createGraphImage(opts.dotDir,
                               graphFileName,
                               opts.outFileName)

    if opts.isOpenInSystemViewer:
        sp.check_call('start ' + opts.outFileName, shell=True)

    print('    Done!')


if __name__ == "__main__":
    _main(sys.argv[1:])
