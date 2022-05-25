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
# import mock
# if mock.__version__ < '1.0.1':
#   print 'Invalid Mock version %s !' % mock.__version__
#   import sys
#   sys.exit( 0 )
#
# import unittest
#
# from DIRAC import gLogger
#
# import LHCbDIRAC.ProductionManagementSystem.Agent.ProductionStatusAgent as sut
#
# class AgentTestCase( unittest.TestCase ):
#   """ Base class for the Agent test cases
#   """
#   def setUp( self ):
#
#     # reload SoftwareUnderTest to drop old patchers
#     reload( sut )
#
#     patcher = mock.patch( 'DIRAC.Core.Base.AgentModule.AgentModule', autospec = True )
#     pStarted = patcher.start()
#     class AgentMocked():
#       def __init__( self, *args, **kwargs ):
#         for k, v in pStarted.__dict__.items():
#           setattr( self, k, v )
#
#     sut.AgentModule = AgentMocked
#     sut.ProductionStatusAgent.__bases__ = ( AgentMocked, )
#
#     self.psa = sut.ProductionStatusAgent( '', '', '' )
#     self.psa.log = gLogger
#
#   def tearDown( self ):
#
#     # Stop patchers
#     mock.patch.stopall()
#
# #############################################################################
# # ProductionStatusAgent.py
# #############################################################################
#
# class ProductionStatusSuccess( AgentTestCase ):
#
#   def test__checkActiveToIdle( self ):
#     self.psa.transClient = mock.Mock()
#     self.psa._getTransformations = mock.Mock()
#     self.psa._getTransformationTaskStats = mock.Mock()
#     self.psa._getTransformationFilesStats = mock.Mock()
#     self.psa._updateProductionStatus = mock.Mock()

#     ###########################################################################
#     # no productions
#
#     updatedProductions = []
#     prods = []
#
#     self.psa._getTransformations.return_value = prods
#
#     self.psa._checkActiveToIdle( updatedProductions )
#     self.assertFalse( self.psa._updateProductionStatus.called )
#     self.psa._updateProductionStatus.reset_mock()

#     simulations and other type, idle and non idle

#     updatedProductions = []
#     prods = [1L, 2L, 3L]
#     prodsInfo = {1L : {'Value': {'Type' : 'MCSimulation'}},
#                  2L : {'Value': {'Type' : 'MCSimulation'}},
#                  3L : {'Value': {'Type' : 'MCSimulation'}},
#                  4L : {'Value': {'Type' : 'Merge'}},
#                  5L : {'Value': {'Type' : 'Merge'}},
#                  6L : {'Value': {'Type' : 'Merge'}}}
#     tasksStats = {1L : {'Created' : 100, 'Submitted' : 100, 'Done' : 90, 'Failed' : 10},  # idle
#                   2L : {'Created' : 100, 'Submitted' : 50, 'Done' : 50},  # not idle
#                   3L : {'Created' : 100, 'Submitted' : 100, 'Done' : 50, 'Failed' : 10, 'Running' : 40}}  # not idle
#     filesStats = {1L : {'Processed' : 100},  # idle
#                   2L : {'Processes' : 0, 'Unused' : 100},  # not idle
#                   3L : {'Processed' : 50, 'Unused' : 25, 'Assigned' : 25},  # not idle
#                   4L : {'Processed' : 100},  # idle
#                   5L : {'Processes' : 0, 'Unused' : 100},  # not idle
#                   6L : {'Processed' : 50, 'Unused' : 25, 'Assigned' : 25}}  # not idle
#
#     self.psa._getTransformations.return_value = prods
#     self.psa.transClient.getTransformation.side_effect = lambda prod : prodsInfo[prod]
#     self.psa._getTransformationTaskStats.side_effect = lambda prod : tasksStats[prod]
#     self.psa._getTransformationFilesStats.side_effect = lambda prod : filesStats[prod]

#     self.psa._checkActiveToIdle( updatedProductions )


#   def test__evaluateProgress( self ):
#     prodReqSummary = {
#                       8733: {'bkTotal': 1090805L, 'master': 0, 'reqTotal': 2000000L},
#                       8744: {'bkTotal': 2090805L, 'master': 0, 'reqTotal': 2000000L},
#                       9050: {'bkTotal': 1600993L, 'master': 9048, 'reqTotal': 500000L},
#                       9237: {'bkTotal': 0L, 'master': 9235, 'reqTotal': 500000L}
#                       }
#
#     progressSummary = {
#                         8733L: {20940L: {'Events': 33916336L, 'Used': 0},
#                                 20941L: {'Events': 1245467L, 'Used': 0},
#                                 20942L: {'Events': 1090805L, 'Used': 1}},
#                         8744L: {20140L: {'Events': 33916336L, 'Used': 0},
#                                 20141L: {'Events': 1245467L, 'Used': 0},
#                                 20142L: {'Events': 2090805L, 'Used': 1}},
#                         9050L: {21034L: {'Events': 1616993L, 'Used': 0},
#                                 21035L: {'Events': 1600993L, 'Used': 1}},
#                         9237L: {21080L: {'Events': 0L, 'Used': 0},
#                                 21081L: {'Events': 0L, 'Used': 1}}
#                       }
#
#     doneAndUsed, doneAndNotUsed, notDoneAndUsed, notDoneAndNotUsed = self.psa._evaluateProgress( prodReqSummary,
#                                                                                                  progressSummary )
#     self.assertEqual( doneAndUsed, {21035L:9050, 20142L:8744} )
#     self.assertEqual( doneAndNotUsed, { 21034L:9050, 20140L:8744, 20141L:8744} )
#     self.assertEqual( notDoneAndUsed, {20942L:8733} )
#     self.assertEqual( notDoneAndNotUsed, {20940L:8733, 20941L:8733} )

#   def test__reqsMap( self ):
#     prodReqSummary = {
#                       8733: {'bkTotal': 1090805L, 'master': 0, 'reqTotal': 2000000L},
#                       8744: {'bkTotal': 2090805L, 'master': 0, 'reqTotal': 2000000L},
#                       11: {'bkTotal': 2090805L, 'master': 12, 'reqTotal': 2000000L},
#                       13: {'bkTotal': 2090805L, 'master': 14, 'reqTotal': 2000000L},
#                       9050: {'bkTotal': 1600993L, 'master': 9048, 'reqTotal': 500000L},
#                       9051: {'bkTotal': 1600993L, 'master': 9048, 'reqTotal': 500000L},
#                       9237: {'bkTotal': 0L, 'master': 9235, 'reqTotal': 500000L},
#                       2: {'bkTotal': 600L, 'master': 1, 'reqTotal': 500L},
#                       4: {'bkTotal': 2600L, 'master': 3, 'reqTotal': 500L},
#                       5: {'bkTotal': 1600L, 'master': 3, 'reqTotal': 500L},
#                       6: {'bkTotal': 200L, 'master': 3, 'reqTotal': 500L},
#                       8: {'bkTotal': 2090805L, 'master': 0, 'reqTotal': 2000000L},
#                       }
#
#     progressSummary = {
#                         8733L: {20940L: {'Events': 33916336L, 'Used': 0},
#                                 20941L: {'Events': 1245467L, 'Used': 0},
#                                 20942L: {'Events': 1090805L, 'Used': 1}},
#                         8744L: {20140L: {'Events': 33916336L, 'Used': 0},
#                                 20141L: {'Events': 1245467L, 'Used': 0},
#                                 20142L: {'Events': 2090805L, 'Used': 1}},
#                         9050L: {21034L: {'Events': 1616993L, 'Used': 0},
#                                 21035L: {'Events': 1600993L, 'Used': 1}},
#                         9051L: {21036L: {'Events': 1616993L, 'Used': 0},
#                                 21037L: {'Events': 1600993L, 'Used': 1}},
#                         9237L: {21080L: {'Events': 0L, 'Used': 0},
#                                 21081L: {'Events': 0L, 'Used': 1}},
#                         2L: {1000L: {'Events': 600L, 'Used': 1}},
#                         4L: {1001L: {'Events': 5600L, 'Used': 0},
#                              1002L: {'Events': 5600L, 'Used': 0},
#                              1003L: {'Events': 2600L, 'Used': 1}},
#                         5L: {1011L: {'Events': 1600L, 'Used': 1}},
#                         6L: {1021L: {'Events': 200L, 'Used': 1}},
#                         8L: {1031L: {'Events': 2090805L, 'Used': 1}},
#                         11L: {1101L: {'Events': 2090805L, 'Used': 0},
#                               1102L: {'Events': 2090805L, 'Used': 1}},
#                         13L: {1301L: {'Events': 2090805L, 'Used': 0},
#                               1302L: {'Events': 2090805L, 'Used': 1}},
#                       }
#
#     res = self.psa._getReqsMap( prodReqSummary, progressSummary )
#     self.assertEqual( res, {8733:{8733:[20940L, 20941L, 20942L]},
#                             8744:{8744:[20140L, 20141L, 20142L]},
#                             9048:{9050:[21034L, 21035L], 9051:[21036L, 21037L]},
#                             9235:{9237:[21080L, 21081L]},
#                             1:{2:[1000L]},
#                             3:{4:[1001L, 1002L, 1003L], 5:[1011L], 6:[1021L]},
#                             8:{8:[1031L]},
#                             12: {11: [1101L, 1102L]},
#                             14: {13: [1301L, 1302L]}
#
#                             } )


#############################################################################
# Test Suite run
#############################################################################

# if __name__ == '__main__':
#   suite = unittest.defaultTestLoader.loadTestsFromTestCase( AgentTestCase )
#   suite.addTest( unittest.defaultTestLoader.loadTestsFromTestCase( ProductionStatusSuccess ) )
#   testResult = unittest.TextTestRunner( verbosity = 2 ).run( suite )

# EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#
