# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 17:03:27 2020

@author: msmsa
"""
import numpy as np
import pandas as pd
from PFAS_SAT_ProcessModels.SubProcesses import split
import graphviz
import plotly.graph_objects as go
from plotly.offline import plot
import json
import warnings
import time
from .utils import NpEncoder
import importlib  # to import module with string name
from PFAS_SAT_ProcessModels import ProcessModelsMetaData


class Project():
    def __init__(self, Inventory, CommonData, ProcessModels=None, pop_up=None):

        self.pop_up = pop_up

        self.Inventory = Inventory

        self.CommonData = CommonData
        self.WasteMaterials = self.CommonData.WasteMaterials

        if ProcessModels:
            self.ProcessModels = ProcessModels
        else:
            self.ProcessModels = {}
            for P in ProcessModelsMetaData:
                self.ProcessModels[P] = {}
                self.ProcessModels[P]['Name'] = ProcessModelsMetaData[P]['Name']
                self.ProcessModels[P]['InputType'] = []
                for flow in ProcessModelsMetaData[P]['InputType']:
                    self.ProcessModels[P]['InputType'].append(flow)
                clas_file = ProcessModelsMetaData[P]['File'].split('.')[0]
                module = importlib.import_module('PFAS_SAT_ProcessModels.' + clas_file)
                model = module.__getattribute__(P)
                self.ProcessModels[P]['Model'] = model(input_data_path=None,
                                                       CommonDataObject=self.CommonData,
                                                       InventoryObject=self.Inventory,
                                                       Name=self.ProcessModels[P]['Name'])

        self.Processes = list(self.ProcessModels.keys())
        self._ProcessNameRef = {}
        for key, val in self.ProcessModels.items():
            self._ProcessNameRef[val['Name']] = key

        self.WasteTreatment = {}
        for i in self.WasteMaterials:
            self.WasteTreatment[i] = self._find_destination(i)
        msg = "=========================================================\n"
        msg += "        Treatment options for each waste material        \n"
        msg += "=========================================================\n"

        for k, v in self.WasteTreatment.items():
            msg += f'\n{k}\n'
            msg += f'{v}\n'
        msg += "=========================================================\n"
        print(msg)

        # Print warnings
        warnings.simplefilter('always', UserWarning)

    def _find_destination(self, product):
        destination = []
        for P in self.Processes:
            if product in self.ProcessModels[P]['InputType']:
                destination.append(P)
        return(destination)

    def get_process_set(self, InputFlow):
        self.Inventory.clear()
        self.InputFlow = InputFlow

        ProcessSet = set()
        ProcessSetPrim = set()
        ProcessSetSec = set()
        ProcessSetTer = set()
        ProcessSetQua = set()
        # Input flow
        for P in self.WasteTreatment[self.InputFlow.FlowType]:
            ProcessSet.add(P)
            ProcessSetPrim.add(P)
            # Intermediate products (Level 1)
            for Product1 in self.ProcessModels[P]['Model'].ProductsType:
                # Add the processes for treatment of level 1 products
                for PP in self.WasteTreatment[Product1]:
                    ProcessSet.add(PP)
                    ProcessSetSec.add(PP)
                    # Intermediate products (Level 2)
                    for Product2 in self.ProcessModels[PP]['Model'].ProductsType:
                        # Add the processes for treatment of level 2 products
                        for PPP in self.WasteTreatment[Product2]:
                            ProcessSet.add(PPP)
                            ProcessSetTer.add(PPP)
                            # Intermediate products (Level 3)
                            for Product3 in self.ProcessModels[PPP]['Model'].ProductsType:
                                # Add the processes for treatment of level 3 products
                                for PPPP in self.WasteTreatment[Product3]:
                                    ProcessSet.add(PPPP)
                                    ProcessSetQua.add(PPPP)
        for i, j in enumerate((ProcessSetPrim, ProcessSetSec, ProcessSetTer, ProcessSetQua)):
            print(f"Level {i} options: {j}\n")
        return ProcessSet, ProcessSetPrim, ProcessSetSec, ProcessSetTer, ProcessSetQua

    def set_process_set(self, ProcessSet):
        self.ProcessSet = ProcessSet
        self.FlowSet = []
        self.FlowSet.append(self.InputFlow.FlowType)

        self._NtwkrNode = set()
        self._NtwkrNodeShape = {}
        self._NtwkrNodeColor = {}
        self._Ntwkedge = set()

        self._NtwkrNode.add(self.InputFlow.FlowType)
        self._NtwkrNodeShape[self.InputFlow.FlowType] = 'oval'
        self._NtwkrNodeColor[self.InputFlow.FlowType] = 'azure'

        for P in self.ProcessSet:
            self._NtwkrNode.add(self.ProcessModels[P]['Name'])
            self._NtwkrNodeShape[self.ProcessModels[P]['Name']] = 'rectangle'
            self._NtwkrNodeColor[self.ProcessModels[P]['Name']] = 'cyan3'
            for product in self.ProcessModels[P]['Model'].ProductsType:
                self._NtwkrNode.add(product)
                self._NtwkrNodeShape[product] = 'oval'
                self._NtwkrNodeColor[product] = 'azure'
                self._Ntwkedge.add((self.ProcessModels[P]['Name'], product))
                if product not in self.FlowSet:
                    self.FlowSet.append(product)

    def get_flow_params(self, normalize=True):
        self.FlowParams = dict()
        for F in self.FlowSet:
            self.FlowParams[F] = {}
            for P in self.ProcessSet:
                if F in self.ProcessModels[P]['InputType']:
                    self.FlowParams[F][self.ProcessModels[P]['Name']] = 0
                    self._Ntwkedge.add((F, self.ProcessModels[P]['Name']))
        if normalize:
            for key, val in self.FlowParams.items():
                if len(val) > 0:
                    sum_norm = 0
                    for key2 in val:
                        sum_norm += np.round(1 / len(val), 4)
                        val[key2] = np.round(1 / len(val), 4)
                    val[key2] += np.round((1 - sum_norm), 4)
        return(self.FlowParams)

    def set_flow_params(self, FlowParams):
        for key, value in FlowParams.items():
            if len(value) > 0:
                if abs(1 - sum(value.values())) > 0.0001:
                    raise ValueError('Sum of the fractions for {} is not 1'.format(key))
        self.FlowParams = FlowParams

    def setup_network(self, Cut_Off=0.001):
        self._CuttOff_factor = Cut_Off
        self.Inventory.clear()
        if self.InputFlow.PFAS.values.sum() > 0:
            self.CuttOff = self.InputFlow.PFAS.values.sum() * self._CuttOff_factor
        else:
            self.CuttOff = 0.001
        product = {self.InputFlow.FlowType: self.InputFlow}
        Project.calc(product, self.InputFlow.FlowType, self.ProcessModels, self.FlowParams, self.Inventory, self.CuttOff,
                     self._ProcessNameRef, self.WasteTreatment, pop_up=self.pop_up)

    @staticmethod
    def calc(product, source, processmodel, FlowParams, Inventory, CuttOff, ProcessNameRef, Treatment_options, pop_up=None):
        for prdct in product:
            if FlowParams[prdct]:
                flows = split(InputFlow=product[prdct], **FlowParams[prdct])
                for prcs, flw in flows.items():
                    if np.isnan(sum(flw.PFAS.values)):
                        msg = """ The PFAS flow for {} stream is nan! check the related input data and process model ({}).""".format(prdct, source)
                        if pop_up:
                            pop_up('PFAS Flow Warning!', msg, 'Warning')
                        raise ValueError(msg)
                    elif sum(flw.PFAS.values) > CuttOff or sum(flw.PFAS.values) > 1:
                        Inventory.add(prdct, source, prcs, flw)
                        processmodel[ProcessNameRef[prcs]]['Model'].calc(flw)
                        product_2 = processmodel[ProcessNameRef[prcs]]['Model'].products()
                        Project.calc(product_2, prcs, processmodel, FlowParams, Inventory, CuttOff, ProcessNameRef, Treatment_options, pop_up=pop_up)
            else:
                if sum(product[prdct].PFAS.values) > CuttOff or sum(product[prdct].PFAS.values) > 1:
                    # Change the warning to exception when all the process models are done
                    msg = "No process is defined for {} treatment! \nSelect one of the following processes: \n".format(prdct)
                    for j in Treatment_options[prdct]:
                        msg += processmodel[j]['Name'] + '\n'
                    if pop_up:
                        pop_up('Treatment Network Warning!', msg, 'Warning')
                    warnings.warn(msg)

    def setup_MC(self, InputFlow_object, seed=None, flow_concentration=True):
        self.InputFlow_object = InputFlow_object
        self.InputFlow_object.setup_MC(seed=seed,
                                       concentration=flow_concentration)
        for p in self.ProcessSet:
            self.ProcessModels[p]['Model'].setup_MC(seed=seed)

    def MC_Next(self):
        NewInputData = []
        NewInputData += self.InputFlow_object.MC_Next()
        for p in self.ProcessSet:
            Raw_newdata = []
            for x in self.ProcessModels[p]['Model'].MC_Next():
                Raw_newdata.append(((p, x[0]), x[1]))
            NewInputData += Raw_newdata
        self.Inventory.clear()
        self.InputFlow_object.calc()
        self.CuttOff = self.InputFlow_object.Inc_flow.PFAS.values.sum() * self._CuttOff_factor
        self.CuttOff = 0.001 if self.CuttOff == 0 else self.CuttOff
        product = {self.InputFlow_object.Inc_flow.FlowType: self.InputFlow_object.Inc_flow}
        Project.calc(product, 'Start', self.ProcessModels, self.FlowParams, self.Inventory, self.CuttOff, self._ProcessNameRef, self.WasteTreatment)
        return(NewInputData)

    def MC_Run(self, n, TypeOfPFAS='All', normalize=False,
               Start_flow=None, signal=None):
        # Print warning only first time
        warnings.simplefilter('once', UserWarning)

        start_time = time.time()
        progress = 0
        progress_steps = [int(x) for x in np.linspace(1, n, 19)]
        MC_results = []
        for i in range(n):
            NewInputData = self.MC_Next()
            MC_results.append((i,
                               NewInputData,
                               self.Inventory.report(TypeOfPFAS=TypeOfPFAS,
                                                     normalize=normalize,
                                                     Start_flow=Start_flow)))
            if i in progress_steps:
                if signal:
                    progress += 5
                    signal.emit(progress)
                    time.sleep(0.1)
                print('Iteration {} \n ... '.format(i))
        self.Reset_static_Data()
        if not signal:
            print(f"Simulation time: {time.time() - start_time:.0f} sec")
            print(f"Number of iterations: {n}")
        return MC_results

    def Reset_static_Data(self):
        self.InputFlow_object.InputData.reset_static_vals()
        for p in self.Processes:
            self.ProcessModels[p]['Model'].InputData.reset_static_vals()

    def setup_SA(self, InputFlow_object):
        self.InputFlow_object = InputFlow_object

    def SensitivityAnalysis(self, Model, Category, Parameter, Start=None,
                            Stop=None, Nstep=20, TypeOfPFAS='All', Default_Res=False):
        try:
            SA_results = []
            if Model == 'IncomFlow':
                param_dict = self.InputFlow_object.InputData.Input_dict[Category][Parameter]
            else:
                param_dict = self.ProcessModels[Model]['Model'].InputData.Input_dict[Category][Parameter]

            Start = param_dict['minimum'] if Start is None else Start
            Stop = param_dict['maximum'] if Stop is None else Stop
            if np.isnan(Start) or np.isnan(Stop):
                raise ValueError('Set the Start & Stop.')

            param_vals = np.linspace(Start, Stop, Nstep)
            if Default_Res:
                param_vals = [param_dict['amount']]
            for i, val in enumerate(param_vals):
                # Update the Input data
                param_dict['amount'] = val
                # Calculating results
                self.Inventory.clear()
                self.InputFlow_object.calc()
                self.CuttOff = self.InputFlow_object.Inc_flow.PFAS.values.sum() * self._CuttOff_factor
                self.CuttOff = 0.001 if self.CuttOff == 0 else self.CuttOff
                product = {self.InputFlow_object.Inc_flow.FlowType: self.InputFlow_object.Inc_flow}
                Project.calc(product, 'Start', self.ProcessModels, self.FlowParams, self.Inventory, self.CuttOff,
                             self._ProcessNameRef, self.WasteTreatment)

                # Store Results
                SA_results.append((i, [((Category, Parameter), val)], self.Inventory.report(TypeOfPFAS)))

        except Exception as e:
            print('Error while running the SA: \n')
            print(e)

        finally:
            # Reset Values
            self.Reset_static_Data()
            self.Inventory.clear()
            return SA_results

    def SA_SR(self, mc_res_cols, TypeOfPFAS, target_result):
        uncertain_params = mc_res_cols[len(self.Inventory.REPORT_INDEX) + 1:]
        target = target_result.replace(' (10e-6g)', '')
        results = pd.DataFrame(columns=[f'SR {target}'], dtype=object)
        for param in uncertain_params:
            kwargs = {}
            kwargs['Nstep'] = 2
            kwargs['TypeOfPFAS'] = TypeOfPFAS
            if isinstance(param[1], tuple):
                kwargs['Model'] = param[0]
                kwargs['Category'] = param[1][0]
                kwargs['Parameter'] = param[1][1]
                param_dict = self.ProcessModels[kwargs['Model']]['Model'].InputData.Input_dict[kwargs['Category']][kwargs['Parameter']]
            else:
                kwargs['Model'] = 'IncomFlow'
                kwargs['Category'] = param[0]
                kwargs['Parameter'] = param[1]
                param_dict = self.InputFlow_object.InputData.Input_dict[kwargs['Category']][kwargs['Parameter']]

            if not np.isnan(param_dict['maximum']):
                kwargs['Stop'] = param_dict['maximum']
            elif param_dict['uncertainty_type'] == 3:
                kwargs['Stop'] = param_dict['loc'] + 3 * param_dict['scale']
            else:
                next

            if not np.isnan(param_dict['minimum']):
                kwargs['Start'] = param_dict['minimum']
            elif param_dict['uncertainty_type'] == 3:
                kwargs['Start'] = param_dict['loc'] - 3 * param_dict['scale']
            else:
                next

            sa_res = self.SensitivityAnalysis(Default_Res=True, **kwargs)
            res = sa_res[0][2][target_result]

            sa_res_1 = self.SensitivityAnalysis(**kwargs)
            res_min = sa_res_1[0][2][target_result]
            res_max = sa_res_1[1][2][target_result]
            try:
                SR = ((res_max - res_min) / res) / ((kwargs['Stop'] - kwargs['Start']) / param_dict['amount'])
                results.loc[str(param), f'SR {target}'] = SR
            except Exception:
                next
        results.sort_values(by=f'SR {target}', key=abs, inplace=True, ascending=False)
        return results

    def plot_network(self, view=True, show_vals=True, file_name='Network'):
        """
        To render the generated DOT source code, you also need to install `Graphviz <https://www.graphviz.org/download>`_.

        ..note:: Make sure that the directory containing the dot executable is on your systems path.

        """
        # Set the color for starting waste material
        self._NtwkrNodeColor[self.InputFlow.FlowType] = 'chartreuse2'
        # Initialize PFAS treatment network
        self.network = graphviz.Digraph(name=file_name, filename=file_name + '.gv', format='png', engine='dot')
        self.network.graph_attr['rankdir'] = 'LR'
        self.network.attr(dpi='300')
        self.network.attr(size='5,5')
        for x in self._NtwkrNode:
            self.network.node(x, shape=self._NtwkrNodeShape[x], fillcolor=self._NtwkrNodeColor[x], style='filled', width='1.2')

        for e in self._Ntwkedge:
            if show_vals:
                if e[0] in self.FlowParams:
                    label = str(self.FlowParams[e[0]][e[1]])
                else:
                    label = None
                self.network.edge(e[0], e[1], label=label, color='black')
            else:
                self.network.edge(e[0], e[1], label=None, color='black')
        try:
            self.network.render(file_name, view=view)
        except Exception:
            print("""
                  To render the generated DOT source code, you also need to install Graphviz (`Graphviz <https://www.graphviz.org/download>`_).\n
                  Make sure that the directory containing the dot executable is on your systems’ path.
                  """)

    def plot_sankey(self, view=True, filename=None, TypeOfPFAS='All', normalize=False, Start_flow=None):
        Data = self.Inventory.Inv

        if TypeOfPFAS == 'All':
            pfas_index = self.CommonData.PFAS_Index
        else:
            pfas_index = [TypeOfPFAS]

        if normalize and Start_flow:
            total_pfas = sum(Start_flow.PFAS[pfas_index].values)
        else:
            total_pfas = 1

        label = []
        label_dict = {}
        source = []
        target = []
        value = []
        label_link = []
        color_link = []

        # List of colors: https://flaviocopes.com/rgb-color-codes/
        edge_color_dict = {'ADLiquids': (220, 20, 60),  # crimson    #DC143C
                           'ADSolids': (124, 252, 0),  # lawn green    #7CFC00
                           'AFFF': (138, 43, 226),  # blue violet	#8A2BE2
                           'C_DWaste': (238, 232, 205),  # cornsilk2    #EEE8CD
                           'CombustionResiduals': (169, 169, 169),  # darkgray    #A9A9A9
                           'Compost': (110, 139, 61),  # darkolivegreen4    #6E8B3D
                           'CompostResiduals': (118, 238, 0),  # chartreuse2    #76EE00
                           'Contact Water': (142, 229, 238),  # cadetblue2    #8EE5EE
                           'ContactWater': (142, 229, 238),  # cadetblue2    #8EE5EE
                           'ContaminatedSoil': (128, 138, 135),  # coldgrey    #808A87
                           'ContaminatedWater': (0, 0, 139),  # dark blue    #00008B
                           'Deep Well Injection': (65, 105, 225),  # royal blue	#4169E1
                           'Mineralized': (255, 165, 0),  # orange	#FFA500
                           'Destructed': (255, 165, 0),  # orange	#FFA500
                           'DewateredWWTSolids': (128, 128, 128),  # gray / grey    #808080
                           'DriedWWTSolids': (192, 192, 192),  # silver    #C0C0C0
                           'DryerExhaust': (128, 128, 128),  # gray / grey	#808080
                           'Effluent': (0, 191, 255),  # deep sky blue	#00BFFF
                           'Exhaust': (128, 128, 128),  # gray / grey	#808080
                           'FoodWaste': (202, 255, 112),  # darkolivegreen1  #CAFF70
                           'GAC Effluent': (72, 209, 204),  # medium turquoise	#48D1CC
                           'IER Effluent': (72, 209, 204),  # medium turquoise	#48D1CC
                           'LFLeachate': (0, 0, 255),  # blue    #0000FF
                           'Leachate': (106, 90, 205),  # slate blue	#6A5ACD
                           'MSW': (139, 101, 8),  # darkgoldenrod4    #8B6508
                           'RO Effluent': (72, 209, 204),  # medium turquoise	#48D1CC
                           'ROConcentrate': (123, 104, 238),  # medium slate blue    #7B68EE
                           'RawWWTSolids': (112, 128, 144),  # slate gray    #708090
                           'Reactivated GAC': (220, 20, 60),  # crimson	#DC143C
                           'Release': (32, 178, 170),  # light sea green	#20B2AA
                           'Remaining': (244, 164, 96),  # sandy brown	#F4A460
                           'RunOff': (0, 255, 255),  # aqua    #00FFFF
                           'SpentGAC': (189, 183, 107),  # darkkhaki    #BDB76B
                           'SpentIER': (189, 183, 107),  # darkkhaki    #BDB76B
                           'Stabilized': (218, 165, 32),  # golden rod	#DAA520
                           'StabilizedSoil': (72, 61, 139),  # dark slate blue    #483D8B
                           'Storage': (233, 150, 122),  # dark salmon	#E9967A
                           'Volatilization': (255, 127, 80),  # coral	#FF7F50
                           'Volatilized': (255, 127, 80),  # coral	#FF7F50
                           'WWTEffluent': (102, 205, 170),  # medium aqua marine	#66CDAA
                           'WWTScreenRejects': (255, 99, 71)}  # tomato	#FF6347

        for i in Data.loc['Flow_name']:
            if i not in edge_color_dict:
                edge_color_dict[i] = (np.random.randint(0, 200), np.random.randint(0, 200), np.random.randint(0, 150))

        index = 0
        for i in Data.loc['Source']:
            if i not in label_dict:
                label_dict[i] = index
                label.append(i)
                index += 1
            source.append(label_dict[i])

        for i in Data.loc['Target']:
            if i not in label_dict:
                label_dict[i] = index
                label.append(i)
                index += 1
            target.append(label_dict[i])

        for i in Data.loc[pfas_index].sum():
            value.append(i / total_pfas * 100)

        for i in Data.loc['Flow_name']:
            label_link.append(i)
            if i in edge_color_dict:
                color_link.append('rgba({},{},{}, 0.8)'.format(*edge_color_dict[i]))
            else:
                color_link.append('rgba(255,127, 0, 0.8)')

        msg = "=============================\n"
        msg += "       Sankey Mass flows     \n"
        msg += "=============================\n"
        msg += f"label = {label}\n"
        msg += f"source = {source}\n"
        msg += f"target = {target}\n"
        msg += f"label_link = {label_link}\n"
        msg += f"value = {value}\n"
        msg += "=============================\n"
        print(msg)

        node = dict(pad=20,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=label,
                    color='rgba({}, {}, {}, 0.8)'.format(*(176, 196, 222)))  # light steel blue    #B0C4DE

        link = dict(source=source,
                    target=target,
                    value=value,
                    label=label_link,
                    color=color_link)

        # The other good option for the valueformat is ".3f".
        layout = go.Layout(title_text=None,
                           font_size=16,
                           hoverlabel=dict(font_size=14))
        if normalize and Start_flow:
            data = go.Sankey(valueformat=".4s",
                             valuesuffix="%",
                             node=node,
                             link=link)
        else:
            data = go.Sankey(valueformat=".3s",
                             valuesuffix="μg",
                             node=node,
                             link=link)
        fig = go.Figure(data=[data], layout=layout)
        plot(fig, filename=filename + '.html' if filename else 'sankey.html', auto_open=view)

        # Store data for ploting the sankey
        store_data = {}
        store_data['title_text'] = None
        store_data['font_size'] = 16
        store_data['hoverlabel'] = dict(font_size=14)
        store_data['valueformat'] = ".3s"
        store_data['valuesuffix'] = "μg"
        store_data['node'] = node
        store_data['link'] = link

        with open(filename + '.JSON' if filename else 'Sankey_Data.JSON', 'w') as outfile:
            json.dump(store_data, outfile, indent=4, cls=NpEncoder)
