# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 11:39:58 2020

@author: msmsa
"""
# Import UI
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from .Table_from_pandas import *
from . import PFAS_SAT_ui
from . import MC_ui
from . import SA_ui
from . import HelpGuide_ui
from . import Reference_ui
from . import Setting_ui
from .Workers import Worker_MC, Worker_Plot

# Import Top level
import os
import io
import csv
import sys
import importlib  #to import module with string name

# Import General
import pandas as pd
import numpy as np
from copy import deepcopy
from pathlib import Path


# Import PFAS_SAT
from PFAS_SAT_ProcessModels import IncomFlow
from PFAS_SAT_InputData import CommonData
from PFAS_SAT_ProcessModels import Inventory
from .. Project import Project
from .. MCResults import MCResults
from PFAS_SAT_ProcessModels import ProcessModelsMetaData
import PFAS_SAT
import PFAS_SAT_InputData
import PFAS_SAT_ProcessModels

# Import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class MyQtApp(PFAS_SAT_ui.Ui_PFAS_SAT, QtWidgets.QMainWindow):
    def __init__(self):
        super(MyQtApp,self).__init__()
        self.setupUi(self)
        self.init_app()

        self.setWindowTitle(f'PFAS SAT {PFAS_SAT.__version__} (InputData {PFAS_SAT_InputData.__version__}, ProcessModels {PFAS_SAT_ProcessModels.__version__})')


        self.WM_tab.setDisabled(True)
        self.PM_tab.setDisabled(True)
        self.SYS_tab.setDisabled(True)
        self.FA_tab.setDisabled(True)
        self.MC_tab.setDisabled(True)
        self.SA_tab.setDisabled(True)

        self.WM_tab_init_status = False
        self.PM_tab_init_status = False
        self.PM_Input_tab_init_status = False
        self.SYS_tab_init_status = False
        self.FA_tab_init_status = False
        self.MC_tab_init_status = False
        self.SA_tab_init_status = False


        ### Menu
        self.actionHelp_Gui.triggered.connect(self.Help_Gui_func)
        self.actionExit.triggered.connect(sys.exit)
        self.actionSaveInventory.triggered.connect(self.SaveInventoryFunc())
        self.actionOptions.triggered.connect(self.SAT_Options_func)
        self.actionReferences.triggered.connect(self.show_References_func)


        # Icon
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(":/icons/ICONS/PFAS_SAT_1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        ### set setting
        self.CutOff = 0.001  # Fraction of total incoming PFAS
        self.AcceptableError = 5  # %
        self.Included_PFAS = deepcopy(CommonData.PFAS_Index)
        self._All_PFAS = deepcopy(CommonData.PFAS_Index)


    def init_app(self):
        self.PFAS_SAT_1.setCurrentWidget(self.Start_tab)

        #bottoms connection
        self.Start_new_project.clicked.connect(self.Start_new_project_func)


    @QtCore.Slot()
    def Start_new_project_func(self):
        self.init_WM_tab()
        self.PFAS_SAT_1.setCurrentWidget(self.WM_tab)


#%% WM tab
# =============================================================================
# =============================================================================
    ### Waste Materials tab
# =============================================================================
# =============================================================================
    def init_WM_tab(self):
        if not self.WM_tab_init_status:
            self.WM_tab.setEnabled(True)
            self.WM_DefData.setChecked(True)
            self.CommonData = CommonData()
            self.IncomFlow = IncomFlow(CommonDataObject=self.CommonData)
            self.WM_Combo.clear()
            self.WM_Combo.currentTextChanged.connect(self.Load_Waste_Prop_func)
            self.WM_Combo.addItems(sorted(self.IncomFlow.WasteMaterialsFullName))

            self.WM_help.clicked.connect(self.help_WM_Function)
            self.WM_UncertaintyHelp.clicked.connect(self.help_MC_Function)

            self.Clear_WM_uncert.clicked.connect(self.Clear_WM_Uncert_func)
            self.Update_WM_prop.clicked.connect(self.Update_WM_prop_func)
            self.Def_Proc_models.clicked.connect(self.init_PM_tab_func)
            self.WM_ExportData.clicked.connect(self.Export_WM_func())

            self.WM_Show_Uncertainty.stateChanged.connect(self.filter_uncertinty_WM_Data)

            # Import Data for WM properties
            self.WM_browse.clicked.connect(self.select_file(self.WM_DataPath,"CSV (*.csv)"))
            self.WM_browse.clicked.connect(self.ChangeDataType)
            self.WM_ImportData.clicked.connect(self.Init_WM_Object)
            self.WM_tab_init_status = True


    # Help function
    @QtCore.Slot()
    def help_WM_Function(self):
        QtGui.QDesktopServices.openUrl('file:///'+str(Path(__file__).parent.parent/'html/WasteMaterialsProperties.html'))
        #QtGui.QDesktopServices.openUrl('https://pfas-sat.readthedocs.io/en/latest/WasteMaterialsProperties.html')
# =============================================================================
#         self.help_window = QWebEngineView()
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
#         self.help_window.setSizePolicy(sizePolicy)
#         self.help_window.setMinimumSize(QtCore.QSize(800, 500))
#         self.help_window.setWindowIcon(self.icon)
#         self.help_window.setWindowTitle('PFAS_SAT: Help')
#         self.help_window.setUrl(QtCore.QUrl('https://pfas-sat.readthedocs.io/en/latest/ProcessModels.html'))
#         self.help_window.show()
# =============================================================================


    @QtCore.Slot()
    def ChangeDataType(self):
        self.WM_UserData.setChecked(True)

    @QtCore.Slot()
    def Init_WM_Object(self):
        if self.WM_UserData.isChecked():
            input_data_path = self.WM_DataPath.text()
        else:
            input_data_path = None
        self.IncomFlow = IncomFlow(input_data_path=input_data_path, CommonDataObject=self.CommonData)
        self.WM_Combo.clear()
        self.WM_Combo.addItems(sorted(self.IncomFlow.WasteMaterialsFullName))

    @QtCore.Slot(str)
    def Load_Waste_Prop_func(self,waste):
        data = self.IncomFlow.InputData.Data[:][(self.IncomFlow.InputData.Data['Category']== waste) | (self.IncomFlow.InputData.Data['Category']==waste+' PFAS Concentration')]
        Waste_Prop_model = Table_from_pandas_editable(data, pop_up=self.msg_popup)
        self.WM_table_prop.setModel(Waste_Prop_model)
        self.WM_table_prop.installEventFilter(self)
        self.WM_table_prop.setSortingEnabled(True)
        self.WM_table_prop.setColumnHidden(0,True)
        self.WM_table_prop.setColumnHidden(1,True)
        self.WM_table_prop.setColumnHidden(2,True)
        self.filter_uncertinty_WM_Data(self.WM_Show_Uncertainty.isChecked())


    @QtCore.Slot()
    def Clear_WM_Uncert_func(self):
        self.WM_table_prop.model()._data['uncertainty_type'] = 0
        self.WM_table_prop.model()._data[['loc','scale','shape','minimum','maximum']] = np.nan
        self.WM_table_prop.model().layoutChanged.emit()

        self.WM_table_prop.setWordWrap(True)
        self.WM_table_prop.resizeColumnsToContents()
        self.WM_table_prop.setColumnWidth(13, 400)
        self.WM_table_prop.resizeRowsToContents()

    @QtCore.Slot()
    def Update_WM_prop_func(self):
        self.IncomFlow.InputData.Update_input(self.WM_table_prop.model()._data)
        self.msg_popup('Update Input Data','The data is updated successfully.','Information')


    @QtCore.Slot(int)
    def filter_uncertinty_WM_Data(self,status):
        if status:
            for i in [6, 7, 8, 9, 10, 11]:
                self.WM_table_prop.setColumnHidden(i,False)
        else:
            for i in [6, 7, 8, 9, 10, 11]:
                self.WM_table_prop.setColumnHidden(i,True)

        self.WM_table_prop.setWordWrap(True)
        self.WM_table_prop.resizeColumnsToContents()
        self.WM_table_prop.setColumnWidth(13, 400)
        self.WM_table_prop.resizeRowsToContents()


    @QtCore.Slot()
    def Export_WM_func(self):
        fileDialog = QtWidgets.QFileDialog()
        def helper():
            DF=self.IncomFlow.InputData.Data
            file_name = str(fileDialog.getSaveFileName(filter="CSV (*.csv)")[0])
            if file_name:
                DF.to_csv(file_name, index=False)
        return(helper)


#%% PM tab
# =============================================================================
# =============================================================================
    ### Process Models tab
# =============================================================================
# =============================================================================
    @QtCore.Slot()
    def init_PM_tab_func(self):
        if not self.PM_tab_init_status:
            self.PM_tab.setEnabled(True)

            self.PM_Help.clicked.connect(self.help_PM_Function)

            # Disable flows that are not modeled.
            self.Med_Waste.setDisabled(True)
            self.MOSP.setDisabled(True)
            self.AutoShredRes.setDisabled(True)

            self._InputKey = {'MSW': self.MSW,
                            'C_DWaste': self.C_D_Waste,
                            'Med_Waste': self.Med_Waste,
                            'MOSP': self.MOSP,
                            'FoodWaste': self.FW,
                            'Compost': self.Compost,
                            'ADLiquids': self.ADLiquids,
                            'ADSolids': self.ADSolids,
                            'CompostResiduals': self.CompRes,
                            'MRFRes': self.MRFRes,
                            'CombustionResiduals': self.CombRes,
                            'AutoShredRes': self.AutoShredRes,
                            'ContaminatedWater': self.ContWater,
                            'ContaminatedSoil': self.ContSoil,
                            'WWTEffluent': self.WWTEffluent,
                            'DewateredWWTSolids': self.DewWWTSol,
                            'DriedWWTSolids': self.DryWWTSol,
                            'RawWWTSolids': self.RawWWTSol,
                            'WWTScreenRejects': self.WWTSol,
                            'ROConcentrate': self.ROC,
                            'LFLeachate': self.LFLeach,
                            'ContactWater': self.ContactWater,
                            'Solidi_Waste': self.Solidi_Waste,
                            'SpentGAC': self.SGAC,
                            'SpentIER': self.SIER,
                            'AFFF_Sulfonate': self.AFFF_1,
                            'AFFF_Fluorotelomer': self.AFFF_2,
                            'StabilizedSoil': self.StabSoil}
            for CheckBox in self._InputKey.values():
                CheckBox.setChecked(False)

            self.ListOfProcessModels = list(ProcessModelsMetaData.keys())
            self.AllProcessModels = {}
            for P in self.ListOfProcessModels:
                self.AllProcessModels[P]={}
                self.AllProcessModels[P]['Default']=True
                self.AllProcessModels[P]['InputDataPath']=None
                self.AllProcessModels[P]['Name']= ProcessModelsMetaData[P]['Name']
                self.AllProcessModels[P]['InputType']=[]
                for flow in ProcessModelsMetaData[P]['InputType']:
                    self.AllProcessModels[P]['InputType'].append(flow)

            self.ProcessNamehelper={}
            for key,val in ProcessModelsMetaData.items():
                self.ProcessNamehelper[val['Name']] = key

            self.ProcModel_Combo.clear()
            self.ProcModel_Combo.currentTextChanged.connect(self.load_PM_metadata)
            self.ProcModel_Combo.addItems(sorted(list(self.ProcessNamehelper.keys())))

            self.ProcModel_Brow_Input.clicked.connect(self.select_file(self.ProcModel_Input_path,"CSV (*.csv)"))
            self.ProcModel_Brow_Input.clicked.connect(self.PM_ChangeDataType)
            self.ProcModel_update.clicked.connect(self.update_PM_metadata)
            self.ProcModel_clear.clicked.connect(self.clear_PM_metadata)
            self.Check_Data.clicked.connect(self.import_PM_init_PMInput)

            self.PM_tab_init_status = True

        self.PFAS_SAT_1.setCurrentWidget(self.PM_tab)


    # Help function
    @QtCore.Slot(str)
    def help_PM_Function(self):
# =============================================================================
#         self.help_window = QWebEngineView()
#         self.help_window.setWindowIcon(self.icon)
#         self.help_window.setWindowTitle('PFAS_SAT: Help')
#         self.help_window.setUrl(QtCore.QUrl('https://pfas-sat.readthedocs.io/en/latest/ProcessModels.html'))
#         self.help_window.show()
# =============================================================================
        QtGui.QDesktopServices.openUrl('file:///'+str(Path(__file__).parent.parent/'html/ProcessModels.html'))
        #QtGui.QDesktopServices.openUrl('https://pfas-sat.readthedocs.io/en/latest/ProcessModels.html')


    # Help function for uncertainty distributions
    @QtCore.Slot(str)
    def help_MC_Function(self):
        QtGui.QDesktopServices.openUrl('file:///'+str(Path(__file__).parent.parent/'html/Getting_started.html')+'#uncertainty-distribution')
        #QtGui.QDesktopServices.openUrl('https://pfas-sat.readthedocs.io/en/latest/Getting_started.html#uncertainty-distribution')


    @QtCore.Slot()
    def PM_ChangeDataType(self):
        self.ProcModel_user_input.setChecked(True)


    @QtCore.Slot(str)
    def load_PM_metadata(self,process):
        process = self.ProcessNamehelper[process]
        self.ProcModel_def_input.setChecked(self.AllProcessModels[process]['Default'])

        if self.AllProcessModels[process]['InputDataPath']:
            self.ProcModel_Input_path.setText(self.AllProcessModels[process]['InputDataPath'])
        else:
            self.ProcModel_Input_path.setText(None)

        for CheckBox in self._InputKey.values():
            CheckBox.setChecked(False)
            CheckBox.setEnabled(True)

        for flow, CheckBox in self._InputKey.items():
            if flow not in ProcessModelsMetaData[process]['InputType']:
                CheckBox.setDisabled(True)

        for flow in self.AllProcessModels[process]['InputType']:
            self._InputKey[flow].setEnabled(True)
            self._InputKey[flow].setChecked(True)

    @QtCore.Slot()
    def update_PM_metadata(self):
        Process = self.ProcessNamehelper[self.ProcModel_Combo.currentText()]
        self.AllProcessModels[Process]['Default']=self.ProcModel_def_input.isChecked()
        if self.ProcModel_user_input.isChecked():
            self.AllProcessModels[Process]['InputDataPath']= self.ProcModel_Input_path.text()
        else:
            self.AllProcessModels[Process]['InputDataPath']= None

        self.AllProcessModels[Process]['InputType']=[]
        for flow,CheckBox in self._InputKey.items():
            if CheckBox.isChecked():
                self.AllProcessModels[Process]['InputType'].append(flow)
        self.msg_popup('Update Process Model','The input data for the process model ({}) is updated successfully.'.format(self.ProcModel_Combo.currentText()),'Information')

    @QtCore.Slot()
    def clear_PM_metadata(self):
        self.ProcModel_def_input.setChecked(True)
        self.ProcModel_Input_path.setText(None)
        for flow,CheckBox in self._InputKey.items():
            CheckBox.setChecked(False)

    @QtCore.Slot()
    def import_PM_init_PMInput(self):
        self.Inventory = Inventory(CommonDataObject=self.CommonData)
        for proc in self.AllProcessModels:
            clas_name= proc
            clas_file=  ProcessModelsMetaData[proc]['File'].split('.')[0]
            module = importlib.import_module('PFAS_SAT_ProcessModels.'+clas_file)
            model = module.__getattribute__(clas_name)
            self.AllProcessModels[proc]['Model'] = model(input_data_path=self.AllProcessModels[proc]['InputDataPath'],
                                                         CommonDataObject=self.CommonData,
                                                         InventoryObject=self.Inventory,
                                                         Name=self.AllProcessModels[proc]['Name'])

        print('\n \n All the process models: \n {} \n\n'.format(self.AllProcessModels))
        self.init_PM_Input_Tab_func()

#%% PM Input Data tab
# =============================================================================
# =============================================================================
    ### Process Models Input Data tab
# =============================================================================
# =============================================================================
    @QtCore.Slot()
    def init_PM_Input_Tab_func(self):
        if not self.PM_Input_tab_init_status:
            self.PM_Input_Tab.setEnabled(True)

            self.PM_Input_Help.clicked.connect(self.help_PM_Function)
            self.PM_UncertaintyHelp.clicked.connect(self.help_MC_Function)

            self.ProcessNamehelper={}
            for key,val in ProcessModelsMetaData.items():
                self.ProcessNamehelper[val['Name']] = key

            self.PM_Input_model.clear()
            self.PM_Input_model.currentTextChanged.connect(self.load_PM_InputData)
            self.PM_Input_model.addItems(sorted(list(self.ProcessNamehelper.keys())))

            self.PM_Show_Uncertainty.stateChanged.connect(self.filter_uncertinty_PM_Data)
            self.Update_PM_Data.clicked.connect(self.update_PM_InputData)
            self.Clear_PM_uncert.clicked.connect(self.clear_PM_InputDataUncertainty)
            self.Def_System.clicked.connect(self.init_SYS_tab_func)
            self.PM_ExportData.clicked.connect(self.Export_PM_func())
            self.PM_Input_tab_init_status = True

        self.PFAS_SAT_1.setCurrentWidget(self.PM_Input_Tab)


    @QtCore.Slot()
    def load_PM_InputData(self):
        Process = self.ProcessNamehelper[self.PM_Input_model.currentText()]
        Data = self.AllProcessModels[Process]['Model'].InputData.Data

        model = Table_from_pandas_editable(Data, pop_up=self.msg_popup)
        self.PM_InputData_Table.setModel(model)
        self.PM_InputData_Table.setColumnHidden(1,True)
        self.filter_uncertinty_PM_Data(self.PM_Show_Uncertainty.isChecked())


    @QtCore.Slot(int)
    def filter_uncertinty_PM_Data(self,status):
        if status:
            for i in [6, 7, 8, 9, 10, 11]:
                self.PM_InputData_Table.setColumnHidden(i,False)
        else:
            for i in [6, 7, 8, 9, 10, 11]:
                self.PM_InputData_Table.setColumnHidden(i,True)

        self.PM_InputData_Table.setWordWrap(True)
        self.PM_InputData_Table.resizeColumnsToContents()
        self.PM_InputData_Table.setColumnWidth(13, 400)
        self.PM_InputData_Table.resizeRowsToContents()


    @QtCore.Slot()
    def update_PM_InputData(self):
        Process = self.ProcessNamehelper[self.PM_Input_model.currentText()]
        self.AllProcessModels[Process]['Model'].InputData.Update_input(self.PM_InputData_Table.model()._data)
        self.msg_popup('Update Input Data','The data is updated successfully.','Information')


    @QtCore.Slot()
    def clear_PM_InputDataUncertainty(self):
        for i in self.PM_InputData_Table.model()._data.index:
            self.PM_InputData_Table.model()._data.loc[i,'uncertainty_type'] = 0
            self.PM_InputData_Table.model()._data.loc[i,['loc','scale','shape','minimum','maximum']] = np.nan
        self.PM_InputData_Table.model().layoutChanged.emit()
        self.PM_InputData_Table.setWordWrap(True)
        self.PM_InputData_Table.resizeColumnsToContents()
        self.PM_InputData_Table.setColumnWidth(13, 400)
        self.PM_InputData_Table.resizeRowsToContents()



    @QtCore.Slot()
    def Export_PM_func(self):
        fileDialog = QtWidgets.QFileDialog()
        def helper():
            Process = self.ProcessNamehelper[self.PM_Input_model.currentText()]
            DF=self.AllProcessModels[Process]['Model'].InputData.Data
            file_name = str(fileDialog.getSaveFileName(filter="CSV (*.csv)")[0])
            if file_name:
                DF.to_csv(file_name, index=False)
        return(helper)

#%% SYS tab
# =============================================================================
# =============================================================================
    ### Define System tab
# =============================================================================
# =============================================================================
    @QtCore.Slot()
    def init_SYS_tab_func(self):
        if not self.SYS_tab_init_status:
            self.SYS_tab.setEnabled(True)
            self.FU.clear()
            self.FU.addItems(sorted(self.IncomFlow.WasteMaterialsFullName))
            self.FU_unit.setText('kg')
            self.FU_amount.setText('1000')
            self.reset.clicked.connect(self.clear_project_setup)
            self.InitProject_Buttom.clicked.connect(self.init_project)
            self.Set_ProcessSet.clicked.connect(self.set_process_set_func)
            self.Update_Flowparams.clicked.connect(self.set_flow_params_func)
            self.FA_Btm.clicked.connect(self.init_FA_tab_func)
            self.MC_Btm.clicked.connect(self.init_MC_tab_func)
            self.SA_Btm.clicked.connect(self.init_SA_tab_func)

            self.init_project_status = True

            self.SYS_tab_init_status = True
            self.project_init_status = True

        self.PFAS_SAT_1.setCurrentWidget(self.SYS_tab)

    def init_project(self):
        if self.project_init_status:
            self.CommonData.PFAS_Index = deepcopy(self.Included_PFAS)
            self.Inventory.__init__(CommonDataObject=self.CommonData)
            self.IncomFlow.set_flow(self.FU.currentText(),float(self.FU_amount.text()))
            self.Inventory._acceptableError = self.AcceptableError
            self.Project = Project(Inventory=self.Inventory, CommonData=self.CommonData,
                                   ProcessModels=self.AllProcessModels, pop_up=self.msg_popup)
            Process_set=self.Project.get_process_set(self.IncomFlow.Inc_flow)

            # Potential down stream processes for each process
            self._Process_edges = {}
            for P in Process_set[0]:
                self._Process_edges[P]=set()
                for prdct in self.Project.ProcessModels[P]['Model'].ProductsType:
                    for process in self.Project.WasteTreatment[prdct]:
                        self._Process_edges[P].add(process)

            self.Process_set_dict={}
            self._Process_inputs = {}
            self.Layout = QtWidgets.QGridLayout(self.ProcessSetFrame)
            row=0
            col=0
            for level,ProcessSet in enumerate([Process_set[1], Process_set[2], Process_set[3], Process_set[4]]):
                for P in ProcessSet:
                    if P not in self.Process_set_dict:
                        self._Process_inputs[P] = 0
                        self.Process_set_dict[P] = QtWidgets.QCheckBox(self.ProcessSetFrame)
                        self.Process_set_dict[P].setObjectName(P)
                        self.Process_set_dict[P].setText(self.AllProcessModels[P]['Name'])
                        if level == 0:
                            self.Process_set_dict[P].setEnabled(True)
                            self._Process_inputs[P]+=1
                        else:
                            self.Process_set_dict[P].setEnabled(False)
                        self.Process_set_dict[P].setChecked(False)
                        self.Layout.addWidget(self.Process_set_dict[P],row,col)
                        col+=1
                        if col==2:
                            col=0
                            row+=1

                if len(ProcessSet)>0:
                    row = row + 1 if col !=0 else row
                    col = 0
                    line = QtWidgets.QFrame(self.ProcessSetFrame)
                    line.setFrameShape(QtWidgets.QFrame.HLine)
                    line.setFrameShadow(QtWidgets.QFrame.Sunken)
                    self.Layout.addWidget(line,row,col,1,2)
                    row += 1

            for P in Process_set[0]:
                self.Process_set_dict[P].clicked.connect(self.activate_potential_processes(P, Process_set))

            self.project_init_status=False

        else:
            self.msg_popup('Error: Create new scenario', 'Reset the scenario to start a new one','Warning')

    @QtCore.Slot(str)
    def activate_potential_processes(self,P, Process_set):
        def helper():
            if self.Process_set_dict[P].isChecked():
                for process in self._Process_edges[P]:
                    self._Process_inputs[process]+=1
            else:
                for process in self._Process_edges[P]:
                    self._Process_inputs[process]-=1

            for Process,N in self._Process_inputs.items():
                if N == 0:
                    self.Process_set_dict[Process].setChecked(False)
                    self.Process_set_dict[Process].setDisabled(True)
                elif N>0:
                    self.Process_set_dict[Process].setEnabled(True)
# =============================================================================
#             if all([not self.Process_set_dict[P].isChecked() for P in Process_set[1]]):
#                 print('Nothing is checked in level1')
#                 for process in Process_set[2].difference(Process_set[1]):
#                     self._Process_inputs[process]=0
#                     self.Process_set_dict[process].setChecked(False)
#                     self.Process_set_dict[process].setDisabled(True)
#                 for process in Process_set[3].difference(Process_set[2],Process_set[1]):
#                     self._Process_inputs[process]=0
#                     self.Process_set_dict[process].setChecked(False)
#                     self.Process_set_dict[process].setDisabled(True)
#                 for process in Process_set[4].difference(Process_set[3],Process_set[2],Process_set[1]):
#                     self._Process_inputs[process]=0
#                     self.Process_set_dict[process].setChecked(False)
#                     self.Process_set_dict[process].setDisabled(True)
#
#             if all([not self.Process_set_dict[P].isChecked() for P in Process_set[2].difference(Process_set[1])]):
#                 print('Nothing is checked in level2')
#                 for process in Process_set[3].difference(Process_set[2],Process_set[1]):
#                     self._Process_inputs[process]=0
#                     self.Process_set_dict[process].setChecked(False)
#                     self.Process_set_dict[process].setDisabled(True)
#                 for process in Process_set[4].difference(Process_set[3],Process_set[2],Process_set[1]):
#                     self._Process_inputs[process]=0
#                     self.Process_set_dict[process].setChecked(False)
#                     self.Process_set_dict[process].setDisabled(True)
#
#             if all([not self.Process_set_dict[P].isChecked() for P in Process_set[3].difference(Process_set[1],Process_set[2])]):
#                 print('Nothing is checked in level3')
#                 for process in Process_set[4].difference(Process_set[3],Process_set[2],Process_set[1]):
#                     self._Process_inputs[process]=0
#                     self.Process_set_dict[process].setChecked(False)
#                     self.Process_set_dict[process].setDisabled(True)
# =============================================================================
            set_edge_level1 = set()
            for pr in Process_set[1]:
                if self.Process_set_dict[pr].isChecked():
                    for process in self._Process_edges[pr]:
                        set_edge_level1.add(process)

            for pr in Process_set[2].difference(set_edge_level1,Process_set[1]):
                self._Process_inputs[pr]=0
                self.Process_set_dict[pr].setChecked(False)
                self.Process_set_dict[pr].setDisabled(True)

            set_edge_level2 = set()
            for pr in Process_set[2]:
                if self.Process_set_dict[pr].isChecked():
                    for process in self._Process_edges[pr]:
                        set_edge_level2.add(process)

            for pr in Process_set[3].difference(set_edge_level1,set_edge_level2,Process_set[1],Process_set[2]):
                self._Process_inputs[pr]=0
                self.Process_set_dict[pr].setChecked(False)
                self.Process_set_dict[pr].setDisabled(True)

            set_edge_level3 = set()
            for pr in Process_set[3]:
                if self.Process_set_dict[pr].isChecked():
                    for process in self._Process_edges[pr]:
                        set_edge_level3.add(process)

            for pr in Process_set[4].difference(set_edge_level1,set_edge_level2,set_edge_level3,Process_set[1],Process_set[2], Process_set[3]):
                self._Process_inputs[pr]=0
                self.Process_set_dict[pr].setChecked(False)
                self.Process_set_dict[pr].setDisabled(True)
        return(helper)

    @QtCore.Slot()
    def clear_project_setup(self):
        self.Process_set_dict = {}
        self.Layout = None
        for Layout in self.ProcessSetFrame.findChildren(QtWidgets.QGridLayout):
# =============================================================================
#             for Checkbox in Layout.findChildren(QtWidgets.QCheckBox):
#                 Checkbox.deleteLater()
# =============================================================================
            Layout.deleteLater()
        for Checkbox in self.ProcessSetFrame.findChildren(QtWidgets.QCheckBox):
            Checkbox.deleteLater()
        for line in self.ProcessSetFrame.findChildren(QtWidgets.QFrame):
            line.deleteLater()
        self.Network_ImageLable.clear()
        self.FlowParams_TreeView.setModel(None)
        self.project_init_status=True
        QtWidgets.QApplication.processEvents()

        # Clear MC
        self.MC_tab.setEnabled(False)
        self.MC_PBr.setValue(0)

        # Clear FA
        self.html_figur.setUrl(None)
        self.Inventory_table.clearSpans()
        self.FA_tab.setEnabled(False)

        # Clear SA
        self.SA_tab.setEnabled(False)
        self.SA_Clear_func()

    @QtCore.Slot()
    def set_process_set_func(self):
        process_set = []
        for key,val in self.Process_set_dict.items():
            if val.isChecked():
                process_set.append(key)

        self.Project.set_process_set(process_set)
        print('\n Process set: {} \n'.format(process_set))

        self.FlowParams = self.Project.get_flow_params()
        print(self.FlowParams)

        model = TreeView(self.FlowParams, self.msg_popup)
        self.FlowParams_TreeView.setModel(model)
        self.FlowParams_TreeView.expandAll()
        self.FlowParams_TreeView.resizeColumnToContents(0)

        self.Network_ImageLable.clear()


    @QtCore.Slot()
    def set_flow_params_func(self):
        flowparams = self.FlowParams_TreeView.model().model_to_dict()
        print('\n flow paramters: {}\n \n '.format(flowparams))
        try:
            self.Project.set_flow_params(flowparams)
        except ValueError as msg:
            self.msg_popup('Error', str(msg),'Warning')

        self.Project.setup_network(Cut_Off=self.CutOff)

        ### Plot Network
        self.Project.plot_network(view=False)
        image = QtGui.QImage('Network.png')
        pixmap = QtGui.QPixmap(image)
        self.Network_ImageLable.setPixmap(pixmap)

#%% FA tab
# =============================================================================
# =============================================================================
    ### Define Flow analysis tab
# =============================================================================
# =============================================================================
    @QtCore.Slot()
    def init_FA_tab_func(self):
        if not self.FA_tab_init_status:
            self.FA_tab.setEnabled(True)

            # connect the signal for download file
            QWebEngineProfile.defaultProfile().downloadRequested.connect(self.on_downloadRequested)

            # set the htm webEngine
            self.html_figur = QWebEngineView(parent=self.Sankey_groupBox)
            self.Sankey_layout.addWidget(self.html_figur)
            self.FA_tab_init_status = True

        self.FA_tab.setEnabled(True)
        self.PFAS_SAT_1.setCurrentWidget(self.FA_tab)

        self.Project.setup_network(Cut_Off=self.CutOff)

        ### Inventory Table
        model = Table_from_pandas(self.Project.Inventory.Inv)
        self.Inventory_table.setModel(model)
        self.Inventory_table.resizeColumnsToContents()
        self.Inventory_table.installEventFilter(self)

        ### Plot Sankey
        plot_worker = Worker_Plot(parent=self.FA_Btm, project = self.Project)
        plot_worker.Plot.connect(self.setup_sankey)
        plot_worker.start()

        ### Check PFAS Balance
        self.Project.Inventory.check_PFAS_balance(Start_flow = self.Project.InputFlow, pop_up = self.msg_popup)
    @QtCore.Slot()
    def setup_sankey(self):
        self.html_figur.setUrl(QtCore.QUrl.fromLocalFile(os.getcwd()+'\\sankey.html'))

#%% MC tab
# =============================================================================
# =============================================================================
    ### Define MC tab
# =============================================================================
# =============================================================================
    @QtCore.Slot()
    def init_MC_tab_func(self):
        if not self.MC_tab_init_status:
            self.MC_tab.setEnabled(True)

            self.MC_N_runs.setMinimum(1)
            self.MC_N_runs.setMaximum(1000000)
            self.MC_N_runs.setValue(1000)

            self.MC_Seed.setMinimum(0)
            self.MC_Seed.setMaximum(1000000)
            self.MC_Seed.setValue(0)

            self.MC_PBr.setMaximum(100)
            self.MC_PBr.setMinimum(0)
            self.MC_PBr.setValue(0)

            self.MC_Model.currentTextChanged.connect(self.show_inputdata)
            self.MC_unceratin_clear.clicked.connect(self.Clear_MC_Uncert_func)
            self.MC_uncertain_update.clicked.connect(self.Update_MC_Uncert_func)
            self.MC_ExportData.clicked.connect(self.Export_MCtab_func())
            self.MC_run.clicked.connect(self.MC_Run_func)
            self.MC_show.clicked.connect(self.show_res_func)
            self.MC_save.clicked.connect(self.MC_save_file())
            self.MC_uncertain_filter.clicked.connect(self.MC_uncertain_filter_func)

            self.MC_tab_init_status = True

            self.MC_UncertaintyHelp.clicked.connect(self.help_MC_Function)

            self.MC_Uncertain_table.installEventFilter(self)
            self.MC_Uncertain_table.setSortingEnabled(True)

        self.MC_PFAS.clear()
        self.MC_PFAS.addItems(['All']+[i for i in self.CommonData.PFAS_Index])

        self.MC_tab.setEnabled(True)
        self.PFAS_SAT_1.setCurrentWidget(self.MC_tab)
        self.MC_Model.clear()
        self.MC_Model.addItems(sorted(['IncomFlow']+[self.Project.ProcessModels[p]['Name'] for p in self.Project.ProcessSet]))

    @QtCore.Slot(str)
    def show_inputdata(self,process):
        if process == '':
            pass
        elif process == 'IncomFlow':
            self._uncertain_data = deepcopy(self.IncomFlow.InputData.Data[(self.IncomFlow.InputData.Data['Dictionary_Name']==self.IncomFlow._flow_name) |
                                                                 (self.IncomFlow.InputData.Data['Dictionary_Name']==self.IncomFlow._flow_name+'_PFAS')])
        else:
            self._uncertain_data = self.Project.ProcessModels[self.Project._ProcessNameRef[process]]['Model'].InputData.Data

        model = Table_from_pandas_editable(self._uncertain_data, pop_up=self.msg_popup)
        self.MC_Uncertain_table.setModel(model)
        self.MC_Uncertain_table.setColumnHidden(1,True)
        self.MC_Uncertain_table.setWordWrap(True)
        self.MC_Uncertain_table.resizeColumnsToContents()
        self.MC_Uncertain_table.setColumnWidth(13, 400)
        self.MC_Uncertain_table.resizeRowsToContents()


    @QtCore.Slot()
    def Clear_MC_Uncert_func(self):
        for i in self.MC_Uncertain_table.model()._data.index:
            self.MC_Uncertain_table.model()._data.loc[i,'uncertainty_type'] = 0
            self.MC_Uncertain_table.model()._data.loc[i,['loc','scale','shape','minimum','maximum']] = np.nan
        self.MC_Uncertain_table.model().layoutChanged.emit()

        self.MC_Uncertain_table.setWordWrap(True)
        self.MC_Uncertain_table.resizeColumnsToContents()
        self.MC_Uncertain_table.setColumnWidth(13, 400)
        self.MC_Uncertain_table.resizeRowsToContents()


    @QtCore.Slot()
    def Update_MC_Uncert_func(self):
        process = self.MC_Model.currentText()
        if process == 'IncomFlow':
            self.IncomFlow.InputData.Update_input(self.MC_Uncertain_table.model()._data)
        else:
            self.Project.ProcessModels[self.Project._ProcessNameRef[process]]['Model'].InputData.Update_input(self.MC_Uncertain_table.model()._data)

        self.msg_popup('Updata Input Data','The data is updated successfully.','Information')

    @QtCore.Slot()
    def Export_MCtab_func(self):
        fileDialog = QtWidgets.QFileDialog()
        def helper():
            process = self.MC_Model.currentText()
            if process == 'IncomFlow':
                DF = self.IncomFlow.InputData.Data
            else:
                DF = self.Project.ProcessModels[self.Project._ProcessNameRef[process]]['Model'].InputData.Data

            file_name = str(fileDialog.getSaveFileName(filter="CSV (*.csv)")[0])
            if file_name:
                DF.to_csv(file_name, index=False)
        return(helper)



    @QtCore.Slot()
    def MC_uncertain_filter_func(self):
        process = self.MC_Model.currentText()
        if process == '':
            pass
        elif process == 'IncomFlow':
            self._uncertain_data = deepcopy(self.IncomFlow.InputData.Data[(self.IncomFlow.InputData.Data['Dictionary_Name']==self.IncomFlow._flow_name) |
                                                                 (self.IncomFlow.InputData.Data['Dictionary_Name']==self.IncomFlow._flow_name+'_PFAS')])
        else:
            self._uncertain_data = self.Project.ProcessModels[self.Project._ProcessNameRef[process]]['Model'].InputData.Data

        if self.MC_uncertain_filter.isChecked():
            model = Table_from_pandas_editable(self._uncertain_data[:][self._uncertain_data['uncertainty_type']>1], pop_up=self.msg_popup)
        else:
            model = Table_from_pandas_editable(self._uncertain_data, pop_up=self.msg_popup)
        self.MC_Uncertain_table.setModel(model)

        self.MC_Uncertain_table.setWordWrap(True)
        self.MC_Uncertain_table.resizeColumnsToContents()
        self.MC_Uncertain_table.setColumnWidth(13, 400)
        self.MC_Uncertain_table.resizeRowsToContents()



    @QtCore.Slot()
    def MC_Run_func(self):
        self.MC_is_runnning = True
        print(" \n Monte Carlo simulation is started. \n Number of iterations: {} \n".format(int(self.MC_N_runs.text())))
        MC_worker = Worker_MC(parent=self.MC_run,
                              project=self.Project,
                              InputFlow_object=self.IncomFlow,
                              n=int(self.MC_N_runs.text()),
                              seed=int(self.MC_Seed.text()),
                              TypeOfPFAS=self.MC_PFAS.currentText())
        MC_worker.UpdatePBr_Opt.connect(self.setPBr_MC)
        MC_worker.Report.connect(self.report_time_WP)
        MC_worker.start()

    @QtCore.Slot()
    def report_time_WP(self, report):
        #Notify the user that the project has created successfully
        self.MC_results = report['results']
        self.msg_popup('Monte Carlo Simulation','The monte carlo simulation is done successfully in {} seconds.'.format(report['time']),'Information')
        print('The monte carlo simulation is done successfully in {} seconds. \n'.format(report['time']))
        self.show_res_func()

    @QtCore.Slot(int)
    def setPBr_MC(self, val):
        self.MC_PBr.setValue(val)

    @QtCore.Slot()  # select file and read the name of it. Import the name to the LineEdit.
    def MC_save_file(self):
        fileDialog = QtWidgets.QFileDialog()
        def helper():
            file_name = str(fileDialog.getSaveFileName(filter="CSV (*.csv)")[0])
            if file_name:
                self.MC_results.results_df.to_csv(file_name, index=False)
        return(helper)


#%% MC results window
# =============================================================================
# =============================================================================
    ### Define MC results window
# =============================================================================
# =============================================================================
    @QtCore.Slot()
    def show_res_func(self):
        Dialog = QtWidgets.QDialog()
        self.MC_Widget = MC_ui.Ui_MC_Results()
        self.MC_Widget.setupUi(Dialog)
        self.MC_Widget.tabWidget.setCurrentWidget(self.MC_Widget.MC_Data)

        ### Data Tab
        MC_res_table_model = Table_from_pandas(self.MC_results.results_df)
        self.MC_Widget.MC_Res_Table.setModel(MC_res_table_model)
        self.MC_Widget.MC_Res_Table.resizeColumnsToContents()
        self.MC_Widget.MC_Res_Table.installEventFilter(self)
        self.MC_Widget.MC_Res_Table.setSortingEnabled(True)

        ### Plot tab
        #Figure initialization _ plot
        self.fig_plot_mc = Figure(figsize=(4, 5), dpi=65, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.canvas_plot_mc = FigureCanvas(self.fig_plot_mc)
        toolbar = NavigationToolbar(self.canvas_plot_mc, self)
        lay = QtWidgets.QVBoxLayout(self.MC_Widget.plot)
        lay.addWidget(toolbar)
        lay.addWidget(self.canvas_plot_mc)
        #self.ax_plot_mc = self.fig_plot_mc.add_subplot(111)

        #Figure initialization _ plot dist
        self.fig_plot_dist_mc = Figure(figsize=(4, 5), dpi=65, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.canvas_plot_dist_mc = FigureCanvas(self.fig_plot_dist_mc)
        toolbar2 = NavigationToolbar(self.canvas_plot_dist_mc, self)
        lay2 = QtWidgets.QVBoxLayout(self.MC_Widget.plot_dist)
        lay2.addWidget(toolbar2)
        lay2.addWidget(self.canvas_plot_dist_mc)
        #self.ax_plot_dist_mc = self.fig_plot_dist_mc.add_subplot(111)

        self.MC_Widget.y_axis.addItems([str(x) for x in Inventory.REPORT_INDEX])
        self.MC_Widget.x_axis.addItems([str(x) for x in self.MC_results.results_df.columns])
        self.MC_Widget.scatter.setChecked(True)
        self.MC_Widget.param.addItems([str(x) for x in self.MC_results.results_df.columns])
        self.MC_Widget.box.setChecked(True)


        ### Connect the push bottoms
        self.MC_Widget.Update_plot.clicked.connect(self.mc_plot_func)
        self.MC_Widget.Update_dist_fig.clicked.connect(self.mc_plot_dist_func)

        # Correlation plot
        self.MC_Widget.Corr_param.addItems(Inventory.REPORT_INDEX)
        self.MC_Widget.Corr_btm.clicked.connect(self.corr_plot_func)

        #Figure initialization _ correlation plot
        self.fig_corr = Figure(figsize=(4, 5), dpi=65, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.canvas_corr = FigureCanvas(self.fig_corr)
        toolbar = NavigationToolbar(self.canvas_corr, self)
        lay = QtWidgets.QVBoxLayout(self.MC_Widget.Corr_plot)
        lay.addWidget(toolbar)
        lay.addWidget(self.canvas_corr)

        Dialog.show()
        Dialog.exec_()

    @QtCore.Slot()
    def corr_plot_func(self):
        self.fig_corr.clear()
        self.ax_plot_corr = self.fig_corr.add_subplot(111)

        self.MC_results.plot_corr(param=self.MC_Widget.Corr_param.currentText(),
                                  ax=self.ax_plot_corr, **{'fontsize':18})

        #set margins
        self.canvas_corr.draw()
        self.fig_corr.set_tight_layout(True)

    @QtCore.Slot()
    def mc_plot_func(self):
        self.fig_plot_mc.clear()
        self.ax_plot_mc = self.fig_plot_mc.add_subplot(111)

        try:
            x=eval(self.MC_Widget.x_axis.currentText())
        except Exception:
            x=self.MC_Widget.x_axis.currentText()

        try:
            y=eval(self.MC_Widget.y_axis.currentText())
        except Exception:
            y=self.MC_Widget.y_axis.currentText()

        self.MC_results.plot_data(x=x,
                                  y=y,
                                  fig_type='scatter' if self.MC_Widget.scatter.isChecked() else 'hexbin',
                                  ax=self.ax_plot_mc,
                                  **{'title': str(self.IncomFlow.Inc_flow.FlowType),
                                     'fontsize': 18})
        #set margins
        self.canvas_plot_mc.draw()
        self.fig_plot_mc.set_tight_layout(True)

    @QtCore.Slot()
    def mc_plot_dist_func(self):
        self.fig_plot_dist_mc.clear()
        self.ax_plot_dist_mc = self.fig_plot_dist_mc.add_subplot(111)

        if self.MC_Widget.hist.isChecked():
            kind = 'hist'
        elif self.MC_Widget.box.isChecked():
            kind = 'box'
        else:
            kind = 'density'

        try:
            param = eval(self.MC_Widget.param.currentText())
        except Exception:
            param = self.MC_Widget.param.currentText()

        self.MC_results.plot_dist(param=param,
                                  fig_type=kind,
                                  ax=self.ax_plot_dist_mc,
                                  **{'title': str(self.IncomFlow.Inc_flow.FlowType),
                                     'fontsize': 18})
        #set margins
        self.canvas_plot_dist_mc.draw()
        self.fig_plot_dist_mc.set_tight_layout(True)

#%%  SA tab
# =============================================================================
# =============================================================================
    ### Sensitivity analysis
# =============================================================================
# =============================================================================
    @QtCore.Slot()
    def init_SA_tab_func(self):
        if not self.SA_tab_init_status:
            self.SA_Model.currentTextChanged.connect(self.load_categories_func)
            self.SA_Category.currentTextChanged.connect(self.load_parameters_func)
            self.SA_Parameter.currentTextChanged.connect(self.load_paramInfo_func)
            self.SA_Run.clicked.connect(self.SA_Run_func)
            self.SA_Save.clicked.connect(self.SA_save_file())
            self.SA_Clear.clicked.connect(self.SA_Clear_func)
            self.SA_Plot.clicked.connect(self.show_sa_res_func)
            self.SA_NStep.setMinimum(2)
            self.SA_NStep.setMaximum(1000)
            self.SA_NStep.setValue(25)
            self.SA_tab_init_status = True

        self.SA_tab.setEnabled(True)
        self.SA_PFAS.clear()
        self.SA_PFAS.addItems(['All']+[i for i in self.CommonData.PFAS_Index])

        self.PFAS_SAT_1.setCurrentWidget(self.SA_tab)
        self.SA_Model.clear()
        self.SA_Model.addItems(['...', 'IncomFlow']+sorted([self.Project.ProcessModels[p]['Name'] for p in self.Project.ProcessSet]))
        self.SA_PFAS.setCurrentIndex(0)

    @QtCore.Slot(str)
    def load_categories_func(self,process):
        if process == '...' or process == '':
            categories = ['...']
        elif process == 'IncomFlow':
            categories = ['...']+list(self.IncomFlow.InputData.Input_dict.keys())
        else:
            categories = ['...']+list(self.Project.ProcessModels[self.Project._ProcessNameRef[process]]['Model'].InputData.Input_dict.keys())

        self.SA_Category.clear()
        self.SA_Category.addItems(categories)

    @QtCore.Slot(str)
    def load_parameters_func(self,category):
        if category == '...' or category == '':
            parameters = ['...']
        elif self.SA_Model.currentText() == 'IncomFlow':
            parameters = ['...']+['{}: {}'.format(key, val['Parameter Description']) for key,val  in self.IncomFlow.InputData.Input_dict[category].items()]
        else:
            parameters = ['...']+['{}: {}'.format(key, val['Parameter Description']) for key,val in self.Project.ProcessModels[self.Project._ProcessNameRef[self.SA_Model.currentText()]]['Model'].InputData.Input_dict[category].items()]

        self.SA_Parameter.clear()
        self.SA_Parameter.addItems(parameters)

    @QtCore.Slot(str)
    def load_paramInfo_func(self,parameter):
        if parameter == '...' or parameter == '':
            info= ''
            self.SA_Unit_1.setText('')
            self.SA_Unit_2.setText('')
        elif self.SA_Model.currentText() == 'IncomFlow':
            param = parameter.split(': ')[0]
            param_dict = self.IncomFlow.InputData.Input_dict[self.SA_Category.currentText()][param]
            info = str()
            for key in ['unit', 'amount', 'uncertainty_type', 'loc', 'scale', 'minimum', 'maximum', 'Comment', 'Reference']:
                val = param_dict[key]
                if isinstance(val, str):
                    info += key + ': ' + str(val) + '\n'
                elif not np.isnan(val):
                    info += key + ': ' + str(val) + '\n'

                if key == 'unit':
                    self.SA_Unit_1.setText(val)
                    self.SA_Unit_2.setText(val)
                elif key == 'minimum' and not pd.isna(val):
                    self.SA_Start.setText(str(val))
                elif key == 'minimum' and pd.isna(val):
                    self.SA_Start.setText("")
                elif key == 'maximum' and not pd.isna(val):
                    self.SA_Stop.setText(str(val))
                elif key == 'maximum' and pd.isna(val):
                    self.SA_Stop.setText("")

        else:
            param = parameter.split(': ')[0]
            param_dict = self.Project.ProcessModels[self.Project._ProcessNameRef[self.SA_Model.currentText()]]['Model'].InputData.Input_dict[self.SA_Category.currentText()][param]
            info = str()
            for key in ['unit', 'amount', 'uncertainty_type', 'loc', 'scale', 'minimum', 'maximum', 'Comment', 'Reference']:
                val = param_dict[key]
                if isinstance(val, str):
                    info += key + ': ' + str(val) + '\n'
                elif not np.isnan(val):
                    info += key + ': ' + str(val) + '\n'

                if key == 'unit':
                    self.SA_Unit_1.setText(val)
                    self.SA_Unit_2.setText(val)
                elif key == 'minimum' and not pd.isna(val):
                    self.SA_Start.setText(str(val))
                elif key == 'minimum' and pd.isna(val):
                    self.SA_Start.setText("")
                elif key == 'maximum' and not pd.isna(val):
                    self.SA_Stop.setText(str(val))
                elif key == 'maximum' and pd.isna(val):
                    self.SA_Stop.setText("")


        self.SA_ParamInfo.setText(info)

    @QtCore.Slot(str)
    def SA_Run_func(self):
        self.Project.setup_MC(self.IncomFlow)
        if self.SA_Model.currentText() == 'IncomFlow':
            model = 'IncomFlow'
        else:
            model = self.Project._ProcessNameRef[self.SA_Model.currentText()]

        SA_Res_raw = self.Project.SensitivityAnalysis(Model=model,
                                                      Category=self.SA_Category.currentText(),
                                                      Parameter=str.split(self.SA_Parameter.currentText(),': ')[0],
                                                      Start=float(self.SA_Start.text()),
                                                      Stop=float(self.SA_Stop.text()),
                                                      Nstep=self.SA_NStep.value(),
                                                      TypeOfPFAS=self.SA_PFAS.currentText())
        self.SA_Res = MCResults(SA_Res_raw)
        self.SA_Res.to_df()

        ### Data Tab
        SA_Res_table_model = Table_from_pandas(self.SA_Res.results_df)
        self.SA_Results.setModel(SA_Res_table_model)
        self.SA_Results.resizeColumnsToContents()
        self.SA_Results.installEventFilter(self)
        self.SA_Results.setSortingEnabled(True)
        self.msg_popup('Sensitivity Analysis','The sensitivity analysis is done successfully.','Information')

    @QtCore.Slot()  # select file and read the name of it. Import the name to the LineEdit.
    def SA_save_file(self):
        fileDialog = QtWidgets.QFileDialog()
        def helper():
            file_name = str(fileDialog.getSaveFileName(filter="CSV (*.csv)")[0])
            if file_name:
                self.SA_Res.results_df.to_csv(file_name, index=False)
        return(helper)

    @QtCore.Slot(str)
    def SA_Clear_func(self):
        self.SA_Model.setCurrentIndex(0)
        self.SA_Start.clear()
        self.SA_Stop.clear()
        self.SA_NStep.clear()
        self.SA_ParamInfo.clear()
        self.SA_Results.setModel(Table_from_pandas(pd.DataFrame()))
        self.SA_PFAS.setCurrentIndex(0)
        self.SA_Unit_1.setText('')
        self.SA_Unit_2.setText('')

#%% SA results window
# =============================================================================
# =============================================================================
    ### Define SA results window
# =============================================================================
# =============================================================================
    @QtCore.Slot()
    def show_sa_res_func(self):
        Dialog = QtWidgets.QDialog()
        self.SA_Widget = SA_ui.Ui_SA_Plot()
        self.SA_Widget.setupUi(Dialog)

        ### Plot tab
        #Figure initialization _ plot
        self.fig_plot_sa = Figure(figsize=(4, 5), dpi=65, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.canvas_plot_sa = FigureCanvas(self.fig_plot_sa)
        toolbar = NavigationToolbar(self.canvas_plot_sa, self)
        lay = QtWidgets.QVBoxLayout(self.SA_Widget.plot)
        lay.addWidget(toolbar)
        lay.addWidget(self.canvas_plot_sa)

        self.SA_Widget.y_axis.addItems([str(x) for x in self.SA_Res.results_df.columns])
        self.SA_Widget.x_axis.addItems([str(x) for x in self.SA_Res.results_df.columns])

        ### Connect the push bottoms
        self.SA_Widget.Update_plot.clicked.connect(self.sa_plot_func)

        Dialog.show()
        Dialog.exec_()

    @QtCore.Slot()
    def sa_plot_func(self):
        self.fig_plot_sa.clear()
        self.ax_plot_sa = self.fig_plot_sa.add_subplot(111)

        try:
            x = eval(self.SA_Widget.x_axis.currentText())
        except Exception:
            x = self.SA_Widget.x_axis.currentText()

        try:
            y = eval(self.SA_Widget.y_axis.currentText())
        except Exception:
            y = self.SA_Widget.y_axis.currentText()

        self.SA_Res.plot_data(x=x,
                              y=y,
                              fig_type='scatter',
                              ax=self.ax_plot_sa,
                              **{'title': str(self.IncomFlow.Inc_flow.FlowType),
                                 'fontsize': 18})
        #set margins
        self.canvas_plot_sa.draw()
        self.fig_plot_sa.set_tight_layout(True)

#%% General Functions
# =============================================================================
# =============================================================================
    ### General Functions
# =============================================================================
# =============================================================================
    def msg_popup(self, Subject, Information, Type):
        msg = QtWidgets.QMessageBox()
        if Type =='Warning':
            msg.setIcon(msg.Icon.Warning)
        elif Type == 'Information':
            msg.setIcon(msg.Icon.Information)
        msg.setWindowTitle('PFAS SAT')
        msg.setWindowIcon(self.icon)
        msg.setText(Subject)
        msg.setInformativeText(Information)
        Ok=msg.addButton(msg.Ok)
        msg.exec()

    @QtCore.Slot()  # select file and read the name of it. Import the name to the LineEdit.
    def select_file(self, LineEdit,Filter):
        fileDialog = QtWidgets.QFileDialog()
        def edit_line():
            file_name = str(fileDialog.getOpenFileName(filter=Filter)[0])
            LineEdit.setText(file_name)
        return(edit_line)


    @QtCore.Slot()
    def on_downloadRequested(self, download):
        """
        https://stackoverflow.com/questions/55963931/how-to-download-csv-file-with-qwebengineview-and-qurl
        """
        old_path = download.url().path()
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", old_path, "*.png")
        if path:
            download.setPath(path)
            download.accept()

    @QtCore.Slot()
    def Help_Gui_func(self):
        Dialog = QtWidgets.QDialog()
        Help_Gui_Widget = HelpGuide_ui.Ui_HelpGuide()
        Help_Gui_Widget.setupUi(Dialog)

        urlLink = """<a href=\"{}\">(Learn How)</a>""".format('file:///'+str(Path(__file__).parent.parent/'html/Getting_started.html#create-new-project'))
        #urlLink="<a href=\"https://pfas-sat.readthedocs.io/en/latest/Getting_started.html#create-new-project\">(Learn How)</a>"
        Help_Gui_Widget.link_Create_project.setText(urlLink)
        Help_Gui_Widget.link_Create_project.setOpenExternalLinks(True)

        urlLink = """<a href=\"{}\">(Learn How)</a>""".format('file:///'+str(Path(__file__).parent.parent/'html/Getting_started.html#flow-analysis'))
        #urlLink="<a href=\"https://pfas-sat.readthedocs.io/en/latest/Getting_started.html#flow-analysis\">(Learn How)</a>"
        Help_Gui_Widget.link_FA.setText(urlLink)
        Help_Gui_Widget.link_FA.setOpenExternalLinks(True)

        urlLink = """<a href=\"{}\">(Learn How)</a>""".format('file:///'+str(Path(__file__).parent.parent/'html/Getting_started.html#monte-carlo-simulation'))
        #urlLink="<a href=\"https://pfas-sat.readthedocs.io/en/latest/Getting_started.html#monte-carlo-simulation\">(Learn How)</a>"
        Help_Gui_Widget.link_MC.setText(urlLink)
        Help_Gui_Widget.link_MC.setOpenExternalLinks(True)

        urlLink = """<a href=\"{}\">(Learn How)</a>""".format('file:///'+str(Path(__file__).parent.parent/'html/Getting_started.html#sensitivity-analysis'))
        #urlLink="<a href=\"https://pfas-sat.readthedocs.io/en/latest/Getting_started.html#sensitivity-analysis\">(Learn How)</a>"
        Help_Gui_Widget.link_SA.setText(urlLink)
        Help_Gui_Widget.link_SA.setOpenExternalLinks(True)

        urlLink = """<a href=\"{}\">(Learn How)</a>""".format('file:///'+str(Path(__file__).parent.parent/'html/doc_PFAS_SAT.html'))
        #urlLink="<a href=\"https://pfas-sat.readthedocs.io/en/latest/doc_PFAS_SAT.html\">(Learn How)</a>"
        Help_Gui_Widget.link_CodeDoc.setText(urlLink)
        Help_Gui_Widget.link_CodeDoc.setOpenExternalLinks(True)

        urlLink = """<a href=\"{}\">(Learn How)</a>""".format('file:///'+str(Path(__file__).parent.parent/'html/contributing.html'))
        #urlLink="<a href=\"https://pfas-sat.readthedocs.io/en/latest/contributing.html\">(Learn How)</a>"
        Help_Gui_Widget.link_Contr.setText(urlLink)
        Help_Gui_Widget.link_Contr.setOpenExternalLinks(True)

        Dialog.show()
        Dialog.exec_()

    def eventFilter(self, obj, event):
        if isinstance(obj,QtWidgets.QTableView):
            if event.type() == QtCore.QEvent.KeyPress and event.matches(QtGui.QKeySequence.Copy):
                self.copySelection(obj)
                return True
            elif event.type() == QtCore.QEvent.KeyPress and event.matches(QtGui.QKeySequence.Paste):
                self.pasteSelection(obj)
                return True
            else:
                return False
        else:
            # pass the event on to the parent class
            return super(MyQtApp,self).eventFilter(obj, event)

    # Copy function for QTableView
    def copySelection(self,obj):
        selection = obj.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data()
            stream = io.StringIO()
            csv.writer(stream, delimiter='\t').writerows(table)
            QtWidgets.QApplication.clipboard().setText(stream.getvalue())

    # Paste function for QTableView
    def pasteSelection(self,obj):
        model = obj.model()
        if hasattr(model,'setData'):
            selection = obj.selectedIndexes()
            if selection:
                buffer = QtWidgets.QApplication.clipboard().text()
                rows = sorted(index.row() for index in selection)
                columns = sorted(index.column() for index in selection)
                reader = csv.reader(io.StringIO(buffer), delimiter='\t')
                #if the user select only one cell for the location
                if len(rows) == 1 and len(columns) == 1:
                    for i, line in enumerate(reader):
                        for j, cell in enumerate(line):
                            #check that the index is available in the table
                            if (rows[0]+i) < model.rowCount() and (columns[0]+j) < model.columnCount():
                                model.setData(model.index(rows[0]+i,columns[0]+j), cell)
                else:
                    arr = [ [ cell for cell in row ] for row in reader]
                    for index in selection:
                        row = index.row() - rows[0]
                        column = index.column() - columns[0]
                        model.setData(model.index(index.row(), index.column()), arr[row][column])
        else:
            print('Warning: The table is not editable!')



### References
    @QtCore.Slot()
    def show_References_func(self):
        Dialog = QtWidgets.QDialog()
        self.References = Reference_ui.Ui_References()
        self.References.setupUi(Dialog)

        self.RefDF = pd.read_csv(PFAS_SAT_InputData.__path__[0]+'/Data/References.csv')
        references = Table_from_pandas(self.RefDF)
        self.References.TableRef.setModel(references)
        self.References.TableRef.installEventFilter(self)
        self.References.TableRef.setWordWrap(True)
        self.References.TableRef.resizeColumnsToContents()
        self.References.TableRef.setColumnWidth(1, 600)
        self.References.TableRef.resizeRowsToContents()


        ### Connect the push bottoms
        self.References.Filter.clicked.connect(self.Ref_filter_func)
        self.References.Export.clicked.connect(self.Ref_Export_func())

        Dialog.show()
        Dialog.exec_()

    @QtCore.Slot()
    def Ref_filter_func(self):
        kwrd = self.References.kwrd.text()
        references = Table_from_pandas(self.RefDF[[kwrd.lower() in str(x).lower() for x in self.RefDF['Reference']]])
        self.References.TableRef.setModel(references)
        self.References.TableRef.installEventFilter(self)
        self.References.TableRef.setWordWrap(True)
        self.References.TableRef.resizeColumnsToContents()
        self.References.TableRef.setColumnWidth(1, 600)
        self.References.TableRef.resizeRowsToContents()

    @QtCore.Slot()
    def Ref_Export_func(self):
        fileDialog = QtWidgets.QFileDialog()
        def helper():
            DF=self.RefDF
            file_name = str(fileDialog.getSaveFileName(filter="CSV (*.csv)")[0])
            if file_name:
                DF.to_csv(file_name, index=False)
        return(helper)



### Setting (SAT Options)
    @QtCore.Slot()
    def SAT_Options_func(self):
        self.Setting_Dialog = QtWidgets.QDialog()
        self.Setting = Setting_ui.Ui_Setting()
        self.Setting.setupUi(self.Setting_Dialog)

        self.Setting.CutOff.setText(str(self.CutOff))
        self.Setting.ErrorLimit.setText(str(self.AcceptableError))

        ### Connect the push bottoms
        self.Setting.Apply.clicked.connect(self.Setting_apply_func)
        self.Setting.Cancel.clicked.connect(self.Setting_cancel_func)

        self.pfas_choices = {}
        x=0
        y=0
        for PFAS in self._All_PFAS:
            if x==2:
                x=0
                y+=1
            self.pfas_choices[PFAS] = QtWidgets.QCheckBox(self.Setting.PFAS_box)
            self.pfas_choices[PFAS].setText(PFAS)
            if PFAS in self.Included_PFAS:
                self.pfas_choices[PFAS].setChecked(True)
            else:
                self.pfas_choices[PFAS].setChecked(False)
            self.Setting.PFAS_Layout.addWidget(self.pfas_choices[PFAS], y, x, 1, 1)
            x+=1

        self.Setting_Dialog.show()
        self.Setting_Dialog.exec_()

    @QtCore.Slot()
    def Setting_apply_func(self):
        self.CutOff = float(self.Setting.CutOff.text())
        self.AcceptableError = float(self.Setting.ErrorLimit.text())
        self.Setting_Dialog.close()
        for PFAS, checkbox in self.pfas_choices.items():
            if checkbox.isChecked() and PFAS not in self.Included_PFAS:
                self.Included_PFAS.append(PFAS)
            elif not checkbox.isChecked() and PFAS in self.Included_PFAS:
                self.Included_PFAS.remove(PFAS)
        print(self.Included_PFAS)

    @QtCore.Slot()
    def Setting_cancel_func(self):
        self.Setting_Dialog.close()


### Save Inventory
    @QtCore.Slot()
    def SaveInventoryFunc(self):
        fileDialog = QtWidgets.QFileDialog()
        def helper():
            try:
                DF=self.Inventory_table.model()._data
                file_name = str(fileDialog.getSaveFileName(filter="CSV (*.csv)")[0])
                if file_name:
                    DF.to_csv(file_name)
            except AttributeError:
                msg = 'No Inventory Found! \n First perform Flow Analysis.'
                self.msg_popup('Error', str(msg),'Warning')


        return(helper)
