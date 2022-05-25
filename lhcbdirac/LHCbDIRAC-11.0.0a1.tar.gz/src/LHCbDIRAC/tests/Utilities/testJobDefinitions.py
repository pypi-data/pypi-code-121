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
""" Collection of user jobs for testing purposes
"""
import os
import time
import errno

from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers
from DIRAC.tests.Utilities.testJobDefinitions import baseToAllJobs, endOfAllJobs, find_all
from DIRAC.Core.Utilities.Proxy import executeWithUserProxy
from LHCbDIRAC.Interfaces.API.LHCbJob import LHCbJob
from LHCbDIRAC.Interfaces.API.DiracLHCb import DiracLHCb
from LHCbDIRAC.tests.Workflow import createJob

from LHCbDIRAC import rootPath

# parameters

jobClass = LHCbJob
diracClass = DiracLHCb

try:
    tier1s = DMSHelpers().getTiers(tier=(0, 1))
except AttributeError:
    tier1s = [
        "LCG.CERN.cern",
        "LCG.CNAF.it",
        "LCG.GRIDKA.de",
        "LCG.IN2P3.fr",
        "LCG.NIKHEF.nl",
        "LCG.PIC.es",
        "LCG.RAL.uk",
        "LCG.RRCKI.ru",
        "LCG.SARA.nl",
    ]

# List of jobs
wdir = os.getcwd()


@executeWithUserProxy
def helloWorldTestT2s():

    job = baseToAllJobs("helloWorldTestT2s", jobClass)
    job.setInputSandbox([find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setBannedSites(tier1s)
    return endOfAllJobs(job)


@executeWithUserProxy
def helloWorldTestCERN():

    job = baseToAllJobs("helloWorld-test-CERN", jobClass)
    job.setInputSandbox([find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setDestination("LCG.CERN.cern")
    return endOfAllJobs(job)


@executeWithUserProxy
def helloWorldTestIN2P3():
    job = baseToAllJobs("helloWorld-test-IN2P3", jobClass)
    job.setInputSandbox([find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setDestination("LCG.IN2P3.fr")
    return endOfAllJobs(job)


@executeWithUserProxy
def helloWorldTestGRIDKA():
    job = baseToAllJobs("helloWorld-test-GRIDKA", jobClass)
    job.setInputSandbox([find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setDestination("LCG.GRIDKA.de")
    return endOfAllJobs(job)


@executeWithUserProxy
def helloWorldTestARC():

    job = baseToAllJobs("helloWorld-test-ARC", jobClass)
    job.setInputSandbox([find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setDestination(["LCG.RAL.uk"])
    return endOfAllJobs(job)


@executeWithUserProxy
def helloWorldTestSSH():

    job = baseToAllJobs("helloWorld-test-SSH", jobClass)
    job.setInputSandbox([find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setDestination(["DIRAC.Zurich.ch"])
    return endOfAllJobs(job)


@executeWithUserProxy
def helloWorldTestSSHCondor():

    job = baseToAllJobs("helloWorld-test-SSHCondor", jobClass)
    job.setInputSandbox([find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setDestination(["DIRAC.Syracuse.us"])  # FIXME: not there
    return endOfAllJobs(job)


@executeWithUserProxy
def helloWorldTestVAC():

    job = baseToAllJobs("helloWorld-test-VAC", jobClass)
    job.setInputSandbox([find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setDestination(["VAC.Manchester.uk"])  # FIXME: not there
    return endOfAllJobs(job)


@executeWithUserProxy
def helloWorldTestCLOUD():

    job = baseToAllJobs("helloWorld-test-CLOUD", jobClass)
    job.setInputSandbox([find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setDestination(["CLOUD.CERN.cern"])
    return endOfAllJobs(job)


@executeWithUserProxy
def helloWorldTestCentos7():

    job = baseToAllJobs("helloWorld-test-CentOS7", jobClass)
    job.setInputSandbox([find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setPlatform("x86_64+avx2+fma-centos7-gcc8-opt")
    return endOfAllJobs(job)


@executeWithUserProxy
def jobWithOutput():

    timenow = time.strftime("%s")
    with open(os.path.join(wdir, timenow + "testFileUpload.txt"), "w") as f:
        f.write(timenow)
    inp1 = [find_all(timenow + "testFileUpload.txt", ".")[0]]
    inp2 = [find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    job = baseToAllJobs("jobWithOutput", jobClass)
    job.setInputSandbox(inp1 + inp2)
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setOutputData([timenow + "testFileUpload.txt"])
    res = endOfAllJobs(job)
    try:
        os.remove(os.path.join(wdir, timenow + "testFileUpload.txt"))
    except OSError as e:
        return e.errno == errno.ENOENT
    return res


@executeWithUserProxy
def jobWithOutputAndPrepend():

    timenow = time.strftime("%s")
    with open(os.path.join(wdir, timenow + "testFileUploadNewPath.txt"), "w") as f:
        f.write(timenow)
    job = baseToAllJobs("jobWithOutputAndPrepend", jobClass)
    inp1 = [find_all(timenow + "testFileUploadNewPath.txt", ".")[0]]
    inp2 = [find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    job.setInputSandbox(inp1 + inp2)
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setOutputData([timenow + "testFileUploadNewPath.txt"], filePrepend="testFilePrepend")
    res = endOfAllJobs(job)
    try:
        os.remove(os.path.join(wdir, timenow + "testFileUploadNewPath.txt"))
    except OSError as e:
        return e.errno == errno.ENOENT
    return res


@executeWithUserProxy
def jobWithOutputAndPrependWithUnderscore():

    timenow = time.strftime("%s")
    with open(os.path.join(wdir, timenow + "testFileUpload_NewPath.txt"), "w") as f:
        f.write(timenow)
    job = baseToAllJobs("jobWithOutputAndPrependWithUnderscore", jobClass)
    inp1 = [find_all(timenow + "testFileUpload_NewPath.txt", ".")[0]]
    inp2 = [find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    job.setInputSandbox(inp1 + inp2)
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    res = job.setOutputData([timenow + "testFileUpload_NewPath.txt"], filePrepend="testFilePrepend")
    if not res["OK"]:
        return 0
    res = endOfAllJobs(job)
    try:
        os.remove(os.path.join(wdir, timenow + "testFileUpload_NewPath.txt"))
    except OSError as e:
        return e.errno == errno.ENOENT
    return res


@executeWithUserProxy
def jobWithOutputAndReplication():

    timenow = time.strftime("%s")
    with open(os.path.join(wdir, timenow + "testFileReplication.txt"), "w") as f:
        f.write(timenow)
    job = baseToAllJobs("jobWithOutputAndReplication", jobClass)
    inp1 = [find_all(timenow + "testFileReplication.txt", ".")[0]]
    inp2 = [find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    job.setInputSandbox(inp1 + inp2)
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setOutputData([timenow + "testFileReplication.txt"], replicate="True")
    res = endOfAllJobs(job)
    try:
        os.remove(os.path.join(wdir, timenow + "testFileReplication.txt"))
    except OSError as e:
        return e.errno == errno.ENOENT
    return res


@executeWithUserProxy
def jobWith2OutputsToBannedSE():

    timenow = time.strftime("%s")
    with open(os.path.join(wdir, timenow + "testFileUploadBanned-1.txt"), "w") as f:
        f.write(timenow)
    with open(os.path.join(wdir, timenow + "testFileUploadBanned-2.txt"), "w") as f:
        f.write(timenow)
    job = baseToAllJobs("jobWith2OutputsToBannedSE", jobClass)
    inp1 = [find_all(timenow + "testFileUploadBanned-1.txt", ".")[0]]
    inp2 = [find_all(timenow + "testFileUploadBanned-2.txt", ".")[0]]
    inp3 = [find_all("exe-script.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    inp4 = [find_all("partialConfig.cfg", rootPath, "/tests/System/GridTestSubmission")[0]]
    job.setInputSandbox(inp1 + inp2 + inp3 + inp4)
    job.setExecutable("exe-script.py", "", "helloWorld.log")
    job.setConfigArgs("partialConfig.cfg")
    job.setDestination("LCG.PIC.es")
    job.setOutputData(
        [timenow + "testFileUploadBanned-1.txt", timenow + "testFileUploadBanned-2.txt"], OutputSE=["PIC-USER"]
    )
    res = endOfAllJobs(job)
    try:
        os.remove(os.path.join(wdir, timenow + "testFileUploadBanned-1.txt"))
    except OSError as e:
        return e.errno == errno.ENOENT
    try:
        os.remove(os.path.join(wdir, timenow + "testFileUploadBanned-2.txt"))
    except OSError as e:
        return e.errno == errno.ENOENT
    return res


@executeWithUserProxy
def jobWithSingleInputData():

    job = baseToAllJobs("jobWithSingleInputData-shouldGoToCERN", jobClass)
    job.setInputSandbox(
        [find_all("exe-script-with-input-single-location.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    )
    job.setExecutable("exe-script-with-input-single-location.py", "", "exeWithInput.log")
    # this file should be at CERN-USER only
    job.setInputData("/lhcb/user/f/fstagni/test/testInputFileSingleLocation.txt")
    job.setInputDataPolicy("download")
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def jobWithSingleInputDataCERN():

    job = baseToAllJobs("jobWithSingleInputDataCERN-shouldSucceed", jobClass)
    job.setInputSandbox(
        [find_all("exe-script-with-input-single-location.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    )
    job.setExecutable("exe-script-with-input-single-location.py", "", "exeWithInput.log")
    # this file should be at CERN-USER only
    job.setInputData("/lhcb/user/f/fstagni/test/testInputFileSingleLocation.txt")
    job.setInputDataPolicy("download")
    job.setDestination(["LCG.CERN.cern"])
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def jobWithSingleInputDataRAL():

    job = baseToAllJobs("jobWithSingleInputDataRAL-shouldFailOptimizers", jobClass)
    job.setInputSandbox(
        [find_all("exe-script-with-input-single-location.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    )
    job.setExecutable("exe-script-with-input-single-location.py", "", "exeWithInput.log")
    # this file should be at CERN-USER only
    job.setInputData("/lhcb/user/f/fstagni/test/testInputFileSingleLocation.txt")
    job.setInputDataPolicy("protocol")
    job.setDestination(["LCG.RAL.uk"])
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def jobWithSingleInputDataIN2P3():

    job = baseToAllJobs("jobWithSingleInputDataIN2P3-shouldFailOptimizers", jobClass)
    job.setInputSandbox(
        [find_all("exe-script-with-input-single-location.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    )
    job.setExecutable("exe-script-with-input-single-location.py", "", "exeWithInput.log")
    # this file should be at CERN-USER only
    job.setInputData("/lhcb/user/f/fstagni/test/testInputFileSingleLocation.txt")
    job.setInputDataPolicy("protocol")
    job.setDestination(["LCG.IN2P3.fr"])
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def jobWithSingleInputDataRRCKI():

    job = baseToAllJobs("jobWithSingleInputDataRRCKI-shouldFailOptimizers", jobClass)
    job.setInputSandbox(
        [find_all("exe-script-with-input-single-location.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    )
    job.setExecutable("exe-script-with-input-single-location.py", "", "exeWithInput.log")
    # this file should be at CERN-USER only
    job.setInputData("/lhcb/user/f/fstagni/test/testInputFileSingleLocation.txt")
    job.setInputDataPolicy("protocol")
    job.setDestination(["LCG.RRCKI.ru"])
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def jobWithSingleInputDataSARA():

    job = baseToAllJobs("jobWithSingleInputDataSARA-shouldFailOptimizers", jobClass)
    job.setInputSandbox(
        [find_all("exe-script-with-input-single-location.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    )
    job.setExecutable("exe-script-with-input-single-location.py", "", "exeWithInput.log")
    # this file should be at CERN-USER only
    job.setInputData("/lhcb/user/f/fstagni/test/testInputFileSingleLocation.txt")
    job.setInputDataPolicy("protocol")
    job.setDestination(["LCG.SARA.nl"])
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def jobWithSingleInputDataPIC():

    job = baseToAllJobs("jobWithSingleInputDataPIC-shouldFailOptimizers", jobClass)
    job.setInputSandbox(
        [find_all("exe-script-with-input-single-location.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    )
    job.setExecutable("exe-script-with-input-single-location.py", "", "exeWithInput.log")
    # this file should be at CERN-USER only
    job.setInputData("/lhcb/user/f/fstagni/test/testInputFileSingleLocation.txt")
    job.setInputDataPolicy("protocol")
    job.setDestination(["LCG.PIC.es"])
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def jobWithSingleInputDataSpreaded():

    job = baseToAllJobs("jobWithSingleInputDataSpreaded", jobClass)
    job.setInputSandbox([find_all("exe-script-with-input.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setExecutable("exe-script-with-input.py", "", "exeWithInput.log")
    # this file should be at CERN-USER and IN2P3-USER
    job.setInputData("/lhcb/user/f/fstagni/test/testInputFile.txt")
    job.setInputDataPolicy("download")
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def jobWithInputDataAndAncestor():

    job = baseToAllJobs("jobWithInputDataAndAncestor", jobClass)
    job.setInputSandbox(
        [find_all("exe-script-with-input-and-ancestor.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    )
    job.setExecutable("exe-script-with-input-and-ancestor.py", "", "exeWithInput.log")
    # WARNING: Collision10!!
    job.setInputData("/lhcb/data/2010/SDST/00008375/0005/00008375_00053941_1.sdst")  # this file should be at SARA-RDST
    # the ancestor should be /lhcb/data/2010/RAW/FULL/LHCb/COLLISION10/81616/081616_0000000213.raw (CERN and SARA)
    job.setAncestorDepth(1)  # pylint: disable=no-member
    job.setInputDataPolicy("download")
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def gaussJob():

    job = baseToAllJobs("gaussJob", jobClass)
    job.setInputSandbox(
        [find_all("prodConf_Gauss_00012345_00067890_1.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    )
    job.setOutputSandbox("00012345_00067890_1.sim")

    optGauss = "$APPCONFIGOPTS/Gauss/Sim08-Beam3500GeV-md100-2011-nu2.py;"
    optDec = "$DECFILESROOT/options/34112104.py;"
    optPythia = "$LBPYTHIAROOT/options/Pythia.py;"
    optOpts = "$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py;"
    optCompr = "$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py;"
    optPConf = "prodConf_Gauss_00012345_00067890_1.py"
    options = optGauss + optDec + optPythia + optOpts + optCompr + optPConf
    job.setApplication(
        "Gauss",
        "v45r5",
        options,  # pylint: disable=no-member
        extraPackages="AppConfig.v3r179;Gen/DecFiles.v27r14p1;ProdConf.v1r9",
        systemConfig="x86_64-slc5-gcc43-opt",
    )
    job.setDIRACPlatform()  # pylint: disable=no-member
    job.setCPUTime(172800)
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def booleJob():

    job = baseToAllJobs("booleJob", jobClass)
    job.setInputSandbox(
        [find_all("prodConf_Boole_00012345_00067890_1.py", rootPath, "/tests/System/GridTestSubmission")[0]]
    )
    job.setOutputSandbox("00012345_00067890_1.digi")

    opts = "$APPCONFIGOPTS/Boole/Default.py;"
    optDT = "$APPCONFIGOPTS/Boole/DataType-2011.py;"
    optTCK = "$APPCONFIGOPTS/Boole/Boole-SiG4EnergyDeposit.py;"
    optComp = "$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py;"
    optPConf = "prodConf_Boole_00012345_00067890_1.py"
    options = opts + optDT + optTCK + optComp + optPConf

    job.setApplication(
        "Boole",
        "v26r3",
        options,  # pylint: disable=no-member
        inputData="/lhcb/user/f/fstagni/test/12345/12345678/00012345_00067890_1.sim",
        extraPackages="AppConfig.v3r171;ProdConf.v1r9",
        systemConfig="x86_64-slc5-gcc43-opt",
    )

    job.setDIRACPlatform()  # pylint: disable=no-member
    job.setCPUTime(172800)
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def booleJobWithConf():

    job = baseToAllJobs("booleJobWithConf", jobClass)
    job.setInputSandbox(
        [
            find_all("prodConf_Boole_00012345_00067890_1.py", rootPath, "/tests/System/GridTestSubmission")[0],
            find_all("rootConfig.cfg", rootPath, "/tests/System/GridTestSubmission")[0],
        ]
    )
    job.setOutputSandbox("00012345_00067890_1.digi")

    opts = "$APPCONFIGOPTS/Boole/Default.py;"
    optDT = "$APPCONFIGOPTS/Boole/DataType-2011.py;"
    optTCK = "$APPCONFIGOPTS/Boole/Boole-SiG4EnergyDeposit.py;"
    optComp = "$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py;"
    optPConf = "prodConf_Boole_00012345_00067890_1.py"
    options = opts + optDT + optTCK + optComp + optPConf

    job.setApplication(
        "Boole",
        "v26r3",
        options,  # pylint: disable=no-member
        inputData="/lhcb/user/f/fstagni/test/12345/12345678/00012345_00067890_1.sim",
        extraPackages="AppConfig.v3r171;ProdConf.v1r9",
        systemConfig="x86_64-slc5-gcc43-opt",
    )

    job.setDIRACPlatform()  # pylint: disable=no-member
    job.setConfigArgs("rootConfig.cfg")
    job.setCPUTime(172800)
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def wrongJob():

    print("\n Submitting gaudiRun job (Gauss only) that will use a configuration file that contains wrong info")
    print("This will generate a job that should become Completed, use the failover, and only later it will be Done")

    job = createJob(local=False)
    job.setName("gaudirun-gauss-stays-completed")
    res = endOfAllJobs(job)
    return res


@executeWithUserProxy
def gaussMPJob():

    job = baseToAllJobs("GaussMP_v49r14", jobClass)

    job.setInputSandbox([find_all("prodConf_Gauss_MP_test.py", rootPath, "/tests/System/GridTestSubmission")[0]])
    job.setOutputSandbox("Gauss_MP_test.sim")

    options = "$APPCONFIGOPTS/Gauss/Beam6500GeV-mu100-2018-nu1.6.py;"
    options += "$APPCONFIGOPTS/Gauss/EnableSpillover-25ns.py;"
    options += "$APPCONFIGOPTS/Gauss/DataType-2017.py"
    options += "$APPCONFIGOPTS/Gauss/RICHRandomHits.py"
    options += "$DECFILESROOT/options/10132060.py"
    options += "$LBPYTHIA8ROOT/options/Pythia8.py"
    options += "$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py"
    job.setApplication(
        "Gauss",
        "v49r14",
        options,  # pylint: disable=no-member
        extraPackages="AppConfig.v3r383;Gen/DecFiles.v30r32;ProdConf.v2r8",
        systemConfig="x86_64-slc6-gcc48-opt",
    )
    job.setDIRACPlatform()  # pylint: disable=no-member
    job.setCPUTime(172800)
    job.setNumberOfProcessors(4)

    return endOfAllJobs(job)
