
from ipra.Model.policyCollection import PolicyCollection
from ipra.Utility.tkinterUtility import *
import pandas as pd

class PolicyCollectionController:
    def __init__(self):
        self.policyCollection = PolicyCollection()
        return
    
    def policySwitch(self,record):
        if record[0] == 'AIA':
            if record[1] not in self.policyCollection.AIA:
                self.policyCollection.AIA.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))
                
        elif record[0] == 'AXA':
            if record[1] not in self.policyCollection.AXA:
                self.policyCollection.AXA.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))
                
        elif record[0] == 'BOCG':
            if record[1] not in self.policyCollection.BOCG:            
                self.policyCollection.BOCG.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))
                
        elif record[0] == 'CHINALIFE':
            if record[1] not in self.policyCollection.CHINALIFE:            
                self.policyCollection.CHINALIFE.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))

        elif record[0] == 'PRU':
            if record[1] not in self.policyCollection.PRU:
                self.policyCollection.PRU.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))

        elif record[0] == 'FWD':
            if record[1] not in self.policyCollection.FWD:
                self.policyCollection.FWD.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))

        elif record[0] == "MANULIFE":
            if record[1] not in self.policyCollection.MANULIFE:
                self.policyCollection.MANULIFE.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))

        elif record[0] == 'YFL':
            if record[1] not in self.policyCollection.YFLIFE:
                self.policyCollection.YFLIFE.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))

        elif record[0] == 'SUNLIFE':
            if record[1] not in self.policyCollection.SUNLIFE:
                self.policyCollection.SUNLIFE.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))

        elif record[0] == 'CIGNA':
            if record[1] not in self.policyCollection.CIGNA:
                self.policyCollection.CIGNA.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))

        elif record[0] == 'GENERALI':
            if record[1] not in self.policyCollection.GENERALI:
                self.policyCollection.GENERALI.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))

        elif record[0] == 'CHUBB':
            if record[1] not in self.policyCollection.CHUBB:
                self.policyCollection.CHUBB.append(record[1])
            else:
                ShowAlert("Import Policy","{0}: {1} is duplicated".format(record[0],record[1]))
    

    def policySwitchByList(self,recordLists):
        for record in recordLists:
            self.policySwitch(record)
    
    def getPolicyListFromFile(self,filePath):
        try:
            policy_no_col = pd.read_excel(filePath,sheet_name='IPRA',usecols='A:B',header=0,dtype=str)
            policy_no_list = policy_no_col.values.tolist()
            for policy in policy_no_list:
                self.policySwitch(policy)
            return True
        except:
            return False
    
    def getDownloadReportIndicator(self):
        pass
    
    def getPolicyCollection(self):
        return self.policyCollection.getTotalList()
    
    def cleanAllPolicy(self):
        self.policyCollection.cleanAllPolicy()
    
    def getSupportedList(self):
        return self.policyCollection.getSupportedList()