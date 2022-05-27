"""
This script generates a flow chart for a function from its disassembly
information.

(c) iSYSTEM Labs, 2013, 2015


Seq  Dir  Indir  Cond  Call/Jump  |  Shape          Color
-------------------------------------------------------------
 1                0       0       |   box           cornsilk
 1                1       0       | parallelogram   cornsilk
      1           0       0       |  hexagon        moccasin
      1           0       1       |  octagon        moccasin
      1           1       0       |  diamond        moccasin
      1           1       1       | Mdiamond        moccasin
            1     0       0       |  hexagon        thistle
            1     0       1       |  octagon        thistle
            1     1       0       |  diamond        thistle
            1     1       1       | Mdiamond        thistle
"""

import sys
import collections
import subprocess as sp

import isystem.connect as ic
import isystem.diagutils as diagutils


LINK_TRUE_LBL = 'True'
LINK_FALSE_LBL = 'False'
IS_DEBUG = False

# Key is node ID, value is the number of jumps to this node,
# including sequential execution (most nodes will have this
# value set to 1 or greater value.
g_nodeJumpNumber = collections.defaultdict(int)
g_ranksForCalledFunctionNodes = set()

g_externalNodes = set() # nodes for called functions and jumps outside function range


class DotLink:
    """
    Contains information for graphwiz's dot link.
    """
    def __init__(self, sourceNodeId, destNodeId, linkLabel=''):
        self.sourceNodeId = sourceNodeId
        self.destNodeId = destNodeId
        self.linkLabel = linkLabel
        self.style = None
        self.weight = -1
        self.isConstraint = True


    def setStyle(self, style):
        """
        Parameters:
        style - one of dot link styles, for example 'invis' for invisible link
        """
        self.style = style


    def setWeight(self, weight):
        """
        Parameters:
        weight - how to optimize link length, 0 for no effort to make it shorter
        """
        self.weight = weight


    def setConstraint(self, isConstraint):
        """
        Parameters:
        isConstraint - if false, this link is not used when ranking
                       nodes (placing them up to bottom)
        """
        self.isConstraint = isConstraint


    def write(self, outFile):
        """
        Writes node link to the given file.
        """

        outFile.write(self.sourceNodeId)
        outFile.write('->')
        outFile.write(self.destNodeId)

        if self.linkLabel or self.style or self.weight >= 0:
            outFile.write(' [')

            linkText = ''

            if self.linkLabel:
                linkText += 'label=<' + self.linkLabel + '>'

            if self.style:
                if linkText:
                    linkText += ', '
                linkText += 'style=' + self.style

            if self.weight >= 0:
                if linkText:
                    linkText += ', '
                linkText += 'weight=' + str(self.weight)

            if not self.isConstraint:
                # write only if set to False, as True is the default value
                if linkText:
                    linkText += ', '
                linkText += 'constraint=false'

            outFile.write(linkText)
            outFile.write(']')

        outFile.write(';\n')


class DotNode:
    """
    Contains information for graphwiz's dot node.
    """

    def __init__(self, nodeId, shape, bkgColor, label,
                 style='', height='', address=-1, srcLine=''):
        """
        Parameters:
        label - usually object op-code of function name
        address - address of instruction presented by this node
        srcLine - source code line, which generated this instruction
        """
        self.nodeId = nodeId
        self.shape = shape
        self.bkgColor = bkgColor
        self.label = label
        self.style = style
        self.height = height
        self.address = address
        self.srcLine = srcLine
        self.debugInfo = None
        self.isHTMLLabel = False
        self.isMergeableFlag = False
        self.dotLink = None
        self.mergedNodes = []

    def setHTMLLabel(self, isHTML):
        self.isHTMLLabel = isHTML

    def setDebugInfo(self, debugInfo):
        self.debugInfo = debugInfo

    def setMergeableFlag(self, isSequential, isConditional, isCall):
        self.isMergeableFlag = isSequential and not isConditional and not isCall

    def setLink(self, dotLink):
        self.dotLink = dotLink

    def merge(self, node):
        """
        Merges two nodes into one by concatenating labels and preserving
        link of the second node. This method may be called only on nodes,
        which have links to parameter 'node'.
        """
        self.mergedNodes.append(node)
        self.dotLink.destNodeId = node.getLinkDestination()

    def isMergeable(self):
        return self.isMergeableFlag

    def getNodeId(self):
        return self.nodeId

    def getShape(self):
        return self.getShape

    def getBkgColor(self):
        return self.bkgColor

    def getLabel(self):
        return self.label

    def createNodeLabel(self):
        label = ''
        if self.address >= 0:
            label += '<font color="red">' + hex(self.address) + '</font><br/>'

        if self.srcLine:
            label += '<font color="green">' + self.srcLine + '</font><br align="left"/>'

        label += self.label + '<br align="left"/>'

        return label


    def getFormattedLabel(self):
        #return '<<table><tr><td>' + self.label + '</td></tr></table>>'
        label = self.createNodeLabel()
        for node in self.mergedNodes:
            label += node.createNodeLabel()

        return '<' + label + '>'


    def getStyle(self):
        return self.style

    def getHeight(self):
        return self.height

    def getLinkDestination(self):
        return self.dotLink.destNodeId

    def write(self, outFile):

        style = self.style
        if style:
            style = "filled," + style
        else:
            style = "filled"

        heightStr = ''
        if self.height:
            heightStr = ', height="'+ self.height +'"'

        if self.debugInfo:
            outFile.write('/*\n' + self.debugInfo + '\n*/\n')

        outFile.write(self.nodeId)
        outFile.write(' [shape=' + self.shape +
                      ', style="' + style + '", fillcolor="' + self.bkgColor +
                      '"' + heightStr + ', label=' + self.getFormattedLabel() + '];\n')

        if self.dotLink:
            self.dotLink.write(outFile)


def _getJumpShape(instruction):

    height = ''

    if instruction.isConditional():
        if instruction.isCall():
            shape = 'Mdiamond'
        else:
            shape = 'diamond'
        height = '1'
    else:
        if instruction.isCall():
            shape = 'octagon'
        else:
            shape = 'hexagon'

    return shape, height


def _getLook(instruction, addrCtrl):
    """
    Defines node graphical properties according to instruction type.
    """
    shape = 'box'
    bkgColor = 'white'
    peripheries = 1 # used to be used for RW access, but since it is not
                    # implemeneted on all disassemblers and the meaning of
                    # double or tripple borders is not intuitive, 'peripheries'
                    # is currently not used.
    height = ''

    if instruction.isFlowSequential():
        if instruction.isConditional():
            shape = 'parallelogram'
        else:
            shape = 'box'

        bkgColor = 'cornsilk'

    elif instruction.isFlowDirectJump():
        shape, height = _getJumpShape(instruction)
        bkgColor = 'moccasin'

    else: # instruction.isFlowIndirectJump():
        shape, height = _getJumpShape(instruction)
        bkgColor = 'thistle'

    opCode = instruction.getOpCode()
    # opcode may contain double quotes when file name is included in
    # branch address, so replace them with single quotes to not break
    # dot syntax
    opCode = opCode.replace('"', "'")
    opCode = opCode.replace(':', " ")
    # replace tabs with spaces, since DOT ignores tabs in HTML labels
    opCode = opCode.replace('\t', " ")

    addr = instruction.getAddress()
    if 'g_testIter' in globals():
        srcLine = ''  # no source lines during test
    else:
        srcLine = addrCtrl.getSymbolAtAddress(ic.IConnectDebug.sSourceCode, 0, addr,
                                              ic.IConnectDebug.sScopeExact)
    # replace special HTML chars
    srcLine = srcLine.replace('&', '&amp;')
    srcLine = srcLine.replace('<', '&lt;')
    srcLine = srcLine.replace('>', '&gt;')

    return shape, bkgColor, peripheries, opCode, height, srcLine


def _createLinkLabel(label, address=''):
    if address:
        return '<font color="red">' + hex(address) + '</font><br/>' + label

    return label


def createNodeId(address):
    return "n_" + str(address)


def createRank(firstNodeId, secondNodeId):
    return '{rank=same; ' + firstNodeId + '; ' + secondNodeId + '; }\n'


def _write_Direct_Conditional_CallLink(outFile, debug, instruction,
                                       isSingleCallNode, isAutoRank):
    # the difference between conditional and unconditional calls
    # is in node look only
    label = _createLinkLabel(LINK_TRUE_LBL)
    _write_Direct_Unconditional_CallLink(outFile, debug, instruction,
                                         isSingleCallNode, isAutoRank, label)


def _write_Direct_Conditional_JumpLink(outFile, iiter, instruction, isAutoRank):
    # the difference between conditional and unconditional jumps
    # is in node look only
    label = _createLinkLabel(LINK_TRUE_LBL, instruction.getJumpTarget())
    _write_Direct_Unconditional_JumpLink(outFile, iiter, instruction, isAutoRank, label)


def _write_Direct_Unconditional_CallLink(outFile, debug, instruction,
                                         isSingleCallNode, isAutoRank, label):

    targetAddr = instruction.getJumpTarget()

    if isSingleCallNode:
        # all calls to other functions link to the same node - better when
        # we are interested in called funtions, but layout is less readable
        calledNodeId = createNodeId(targetAddr)
    else:
        # make unique node ID for each call
        calledNodeId = createNodeId(targetAddr) + createNodeId(instruction.getAddress())

    currentNodeId = createNodeId(instruction.getAddress())
    rankStr = createRank(currentNodeId, calledNodeId)

    if not calledNodeId in g_externalNodes:
        g_externalNodes.add(calledNodeId)
        calledFunction = debug.getSymbolAtAddress(ic.IConnectDebug.sFunctions,
                                                  0,
                                                  targetAddr,
                                                  ic.IConnectDebug.sScopeNarrow)
        node = DotNode(calledNodeId, 'ellipse', 'paleturquoise', calledFunction, 'dashed',
                       address=targetAddr)
        node.write(outFile)
        g_ranksForCalledFunctionNodes.add(rankStr)
    else:
        if rankStr in g_ranksForCalledFunctionNodes:
            g_ranksForCalledFunctionNodes.remove(rankStr)

    writeJumpLink(outFile, currentNodeId, calledNodeId, label, isAutoRank)


def _write_Direct_Unconditional_JumpLink(outFile, iiter, instruction, isAutoRank, label):
    # create link to node when condition is True
    jmpAddress = instruction.getJumpTarget()
    jmpNodeId = createNodeId(jmpAddress)

    if not jmpNodeId in g_externalNodes:
        g_externalNodes.add(jmpNodeId)
        if not iiter.isAddressInRange(jmpAddress):
            # jump to address outside function!
            node = DotNode(jmpNodeId, 'ellipse', 'lightpink', str(jmpAddress), 'dotted')
            node.write(outFile)
        else:
            pass # node for jump inside function will be created later
            # iter.branch(jmpAddress)
            # jmpInstruction = iter.next()
            # shape, bkgColor, peripheries, label = _getLook(jmpInstruction)
            # writeNode(outFile, jmpNodeId, shape, bkgColor, peripheries, label)
            # iter.branch(instruction.getAddress())

    currentNodeId = createNodeId(instruction.getAddress())

    if not label: # not defined by caller, add address
        label = _createLinkLabel('', jmpAddress)

    writeJumpLink(outFile, currentNodeId, jmpNodeId, label, isAutoRank)
    g_nodeJumpNumber[jmpNodeId] += 1


def _write_Indirect_CallLink(outFile, instruction, isAutoRank, label):
    # this node can not exist, as its ID contains current address
    currentNodeId = createNodeId(instruction.getAddress())
    calledNodeId = currentNodeId + '_indirectCall'
    rankStr = createRank(currentNodeId, calledNodeId)
    node = DotNode(calledNodeId, 'ellipse', 'paleturquoise', 'indirectCall', 'dotted')
    node.write(outFile)
    writeJumpLink(outFile, currentNodeId, calledNodeId, label, isAutoRank)
    g_ranksForCalledFunctionNodes.add(rankStr)


def _write_Indirect_JumpLink(instruction):
    # this node can not exist, as its ID contains current address
    currentNodeId = createNodeId(instruction.getAddress())
    jmpNodeId = currentNodeId + '_indirectBranch'

    # indirect jump nodes are currently not shown, as they are annoying in case of
    # 'blr', and indirect jumps are shown with special node color
    #writeNode(outFile, jmpNodeId, 'house', 'gold', 1, 'indirectBranch', 'dotted')
    #writeJumpLink(outFile, currentNodeId, jmpNodeId, label, isAutoRank)


def getInstructionIterator(socCodeInfo, addrCtrl, dataCtrl2, functionName):
    funcNameParts = functionName.split(',,')

    if len(funcNameParts) == 2:
        partitionCodeInfo = socCodeInfo.loadCodeInfo(dataCtrl2, funcNameParts[1])
    else:
        partitionCodeInfo = socCodeInfo.loadCodeInfo(dataCtrl2, '')

    iiter = ic.CInstructionIter(partitionCodeInfo,
                                addrCtrl,
                                functionName)
    return iiter


def createStartNode(nodesList, iiter, functionName):
    nextInstr = iiter.peek()
    node = DotNode(functionName, 'ellipse', 'aquamarine', functionName,
                   address=nextInstr.getAddress())

    nextNodeId = createNodeId(nextInstr.getAddress())
    node.setLink(DotLink(functionName, nextNodeId))
    nodesList.append(node)


def createNode(instruction, addrCtrl):
    currentNodeId = createNodeId(instruction.getAddress())
    shape, bkgColor, _, opCode, height, srcLine = _getLook(instruction, addrCtrl)
    node = DotNode(currentNodeId, shape, bkgColor, opCode, height=height, srcLine=srcLine)
    node.setMergeableFlag(instruction.isFlowSequential(),
                          instruction.isConditional(),
                          instruction.isCall())

    if IS_DEBUG:
        node.setDebugInfo(instruction.toString())

    return node


def writeJumpLink(outFile, startNode, endNode, decoration, isAutoRank):
    link = DotLink(startNode, endNode, decoration)
    # if jump links do not influence ranking, nodes are placed top to
    # bottom following the address order
    if not isAutoRank:
        link.setConstraint(False)

    link.write(outFile)


def linkToNextNode(instruction, currentNodeId, nextNodeId):

    link = None

    if (instruction.isFlowSequential() or instruction.isCall() or
            instruction.isConditional()):

        if instruction.isConditional():
            label = _createLinkLabel(LINK_FALSE_LBL)
            link = DotLink(currentNodeId, nextNodeId, label)
        else:
            link = DotLink(currentNodeId, nextNodeId)

        g_nodeJumpNumber[nextNodeId] += 1
    else:
        # jumps should have invisible links to next nodes, which contain
        # instructions on next addresses to maintain address order of nodes
        isIndirectUnconditionalJump = (instruction.isFlowIndirectJump() and
                                       not instruction.isConditional() and
                                       not instruction.isCall())
        # skip invisible links for nodes, which are not present, see comment in
        # write_Indirect_Unconditional_JumpLink() above
        if not isIndirectUnconditionalJump:
            link = DotLink(currentNodeId, nextNodeId)
            link.setStyle('invis')

    return link


def handleCallsAndJumps(outFile, instruction, debug, iiter,
                        isSingleCallNode, isAutoRank):

    if instruction.isFlowSequential():
        pass
    elif instruction.isFlowDirectJump():
        if instruction.isConditional():
            if instruction.isCall():
                _write_Direct_Conditional_CallLink(outFile, debug, instruction,
                                                   isSingleCallNode, isAutoRank)
            else:
                _write_Direct_Conditional_JumpLink(outFile, iiter,
                                                   instruction, isAutoRank)
        else:
            if instruction.isCall():
                _write_Direct_Unconditional_CallLink(outFile, debug, instruction,
                                                     isSingleCallNode, isAutoRank, '')
            else:
                _write_Direct_Unconditional_JumpLink(outFile, iiter, instruction,
                                                     isAutoRank, '')

    elif instruction.isFlowIndirectJump():
        if instruction.isConditional():
            if instruction.isCall():
                _write_Indirect_CallLink(outFile, instruction, isAutoRank, LINK_TRUE_LBL)
            else:
                _write_Indirect_JumpLink(instruction)
        else:
            if instruction.isCall():
                _write_Indirect_CallLink(outFile, instruction, isAutoRank, '')
            else:
                _write_Indirect_JumpLink(instruction)
    else:
        raise Exception("Invalid instruction - should be sequential, or direct, or indirect jump")


def mergeAndWriteNodesToFile(outFile, nodesList):

    mergedNode = None

    for node in nodesList:
        nodeId = node.getNodeId()

        if node.isMergeable():
            if mergedNode is None:
                mergedNode = node
            else:
                if g_nodeJumpNumber[nodeId] < 2:
                    mergedNode.merge(node)
                else:
                    mergedNode.write(outFile)
                    mergedNode = node
        else:
            if not mergedNode is None:
                mergedNode.write(outFile)
                mergedNode = None
            node.write(outFile)

    if mergedNode: # write the last merged node, if exists
        mergedNode.write(outFile)

    for rank in g_ranksForCalledFunctionNodes:
        outFile.write(rank)



def writeNodesToFile(outFile, nodesList):
    for node in nodesList:
        node.write(outFile)

    for rank in g_ranksForCalledFunctionNodes:
        outFile.write(rank)


def analyzeFunction(connectionMgr, functionName, isExpanded,
                    isSingleCallNode,
                    isAutoRank,
                    outFile):
    """
    This is top-level function for creation of dot file. It iterates from the
    firt to the last instruction in function and creates dot nodes and links
    of appropiate look.
    """

    outFile.write("digraph {\n")
    # font 10 in graphs should be big enough to be readable
    outFile.write("  node[fontsize=10];\n")
    outFile.write("  graph [rank=max];\n")
    outFile.write("  edge[fontsize=10];\n")

    debug = ic.CDebugFacade(connectionMgr)
    dataCtrl2 = ic.CDataController2(connectionMgr)
    addrCtrl = ic.CAddressController(connectionMgr)
    socCodeInfo = ic.CSOCCodeInfo()

    nodesList = []

    if 'g_testIter' in globals():
        iiter = g_testIter
    else:
        iiter = getInstructionIterator(socCodeInfo, addrCtrl, dataCtrl2, functionName)

    createStartNode(nodesList, iiter, functionName)

    while iiter.hasNext():

        instruction = iiter.next()

        if IS_DEBUG:
            print('instruction: addr = ', instruction.getAddress(),
                  '  opCode = ', instruction.getOpCode())

        node = createNode(instruction, addrCtrl)
        nodesList.append(node)
        currentNodeId = node.getNodeId()

        handleCallsAndJumps(outFile, instruction, debug, iiter,
                            isSingleCallNode, isAutoRank)

        if iiter.hasNext():
            nextInstr = iiter.peek()
            nextNodeId = createNodeId(nextInstr.getAddress())
        else:
            nextNodeId = 'OutOfFunction'  # should never be used

        link = linkToNextNode(instruction, currentNodeId, nextNodeId)
        node.setLink(link)


    if isExpanded:
        writeNodesToFile(outFile, nodesList)
    else:
        mergeAndWriteNodesToFile(outFile, nodesList)

    outFile.write("}\n\n")


def main(cmdLineArgs):

    print('Creating flow chart:')

    opts = diagutils.parseArgs(cmdLineArgs,
                               [('-e',
                                 '--expand',
                                 'isExpanded',
                                 False,
                                 'if present, sequence instructions are shown in separate nodes'),
                                ('-s',
                                 '--singleCallNode',
                                 'isSingleCallNode',
                                 False,
                                 'if present, all calls to the same function are linked to the ' +
                                 'same node, otherwise each call has its own node, but results ' +
                                 'in more readable layout'),
                                ('-a',
                                 '--autoRank',
                                 'isAutoRank',
                                 False,
                                 'if present, then nodes are not ordered according to addresses, ' +
                                 'but to minimize length of links.'),
                                ('-o',
                                 '--open',
                                 'isOpenInSystemViewer',
                                 False,
                                 'if present, then generated diagram is opened in OS default ' +
                                 'viewer'),
                               ])

    cmgr = ic.ConnectionMgr()
    cmgr.connectMRU('')

    graphFileName = diagutils.createGraphFileName(opts.outFileName,
                                                  'flow')
    with open(graphFileName, 'w') as outf:

        if IS_DEBUG:
            print(' '.join(cmdLineArgs))

        analyzeFunction(cmgr,
                        opts.functionName,
                        opts.isExpanded,
                        opts.isSingleCallNode,
                        opts.isAutoRank,
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
    main(sys.argv[1:])
