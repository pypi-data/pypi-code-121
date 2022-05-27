# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 22:09:10 2020

@author: msmsa
"""
import pandas as pd
from PFAS_SAT_InputData import CommonData


class Inventory:
    REPORT_INDEX = ['Water (10e-6g)', 'Soil (10e-6g)', 'Air (10e-6g)',
                    'Mineralized (10e-6g)', 'Stored (10e-6g)',
                    'Injection Well (10e-6g)', 'Reactivated GAC (10e-6g)']

    def __init__(self, CommonDataObject=None):
        if CommonDataObject is not None:
            self._PFAS_Index = CommonDataObject.PFAS_Index
        else:
            self._PFAS_Index = CommonData.PFAS_Index
        self._index = ['Flow_name', 'Source', 'Target', 'Unit'] + self._PFAS_Index + ['Total']
        self.Inv = pd.DataFrame(index=self._index)
        self.Col_index = 0
        self._acceptableError = 5  # acceptable percent error in PFAS mass Balance

    def add(self, Flow_name, Source, Target, flow):
        if min(flow.PFAS.values) < 0:
            msg = f'Negative PFAS flow!! \n Flow Name: {Flow_name} \n Source: {Source}'
            msg += f'\n {flow.report()}'
            raise Exception(msg)
        data = [Flow_name, Source, Target, 'μg'] + list(flow.PFAS.values) + [flow.PFAS.values.sum()]
        self.Inv[self.Col_index] = data
        self.Col_index += 1

    def report_Water(self):
        water_inv = self.Inv[self.Inv.columns[self.Inv.loc['Target'] == 'Water']]
        return water_inv

    def report_Soil(self):
        soil_inv = self.Inv[self.Inv.columns[self.Inv.loc['Target'] == 'Soil']]
        return soil_inv

    def report_Air(self):
        air_inv = self.Inv[self.Inv.columns[self.Inv.loc['Target'] == 'Air']]
        return air_inv

    def report_Mineralized(self):
        Mineralized_inv = self.Inv[self.Inv.columns[self.Inv.loc['Target'] == 'Mineralized']]
        return Mineralized_inv

    def report_Stored(self):
        Stored_inv = self.Inv[self.Inv.columns[self.Inv.loc['Target'] == 'Stored']]
        return Stored_inv

    def report_InjectionWell(self):
        InjectedWell_inv = self.Inv[self.Inv.columns[self.Inv.loc['Target'] == 'Injection Well']]
        return(InjectedWell_inv)

    def report_ReactivatedGAC(self):
        ReactivatedGAC_inv = self.Inv[self.Inv.columns[self.Inv.loc['Target'] == 'Reactivated GAC']]
        return ReactivatedGAC_inv

    def clear(self):
        self.Inv = pd.DataFrame(index=self._index)
        self.Col_index = 0

    def report(self, TypeOfPFAS='All', df=False, normalize=False,
               Start_flow=None, unit=True):
        if TypeOfPFAS == 'All':
            Index = self._PFAS_Index
        else:
            Index = [TypeOfPFAS]
        report = dict()

        if normalize and Start_flow:
            total_pfas = sum(Start_flow.PFAS[Index].values)
        else:
            total_pfas = 1

        for key in Inventory.REPORT_INDEX:
            attr = self.__getattribute__('report_' + key.replace('(10e-6g)', '').replace(' ', ''))
            if not unit:
                key = key.replace(' (10e-6g)', '')
            if df:
                report[key] = [attr().loc[Index].sum(axis=1).sum() / total_pfas]
            else:
                report[key] = attr().loc[Index].sum(axis=1).sum() / total_pfas
        if df:
            report = pd.DataFrame(report).T.rename(columns={0: 'PFAS Fate'})
        return report

    def check_PFAS_balance(self, Start_flow, pop_up=None):
        PFAS_Input = round(sum(Start_flow.PFAS.values), 1)
        PFAS_Output = round(sum(self.report(TypeOfPFAS='All').values()), 1)
        Balance_Error = round((PFAS_Input - PFAS_Output) / PFAS_Input * 100, 1)

        if Balance_Error < self._acceptableError:
            msg = """PFAS mass balance is successfully converged!
Incoming PFAS: {}
Outgoing PFAS: {}
Balance Error: {} % """.format(PFAS_Input, PFAS_Output, Balance_Error)
            if pop_up:
                pop_up('PFAS Mass Balance!', msg, 'Information')
            print(msg)
        else:
            msg = """PFAS mass balance is not converged!
Incoming PFAS: {}
Outgoing PFAS: {}
Balance Error: {} % """.format(PFAS_Input, PFAS_Output, Balance_Error)
            if pop_up:
                pop_up('PFAS Mass Balance Warning!', msg, 'Warning')
            raise Exception(msg)
