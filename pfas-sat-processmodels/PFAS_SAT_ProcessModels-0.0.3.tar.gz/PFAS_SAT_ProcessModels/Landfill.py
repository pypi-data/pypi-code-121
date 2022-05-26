# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 21:04:20 2020

@author: msmsa
"""
import pandas as pd
from .Flow import Flow
from .SubProcesses import mix, landfil_sorption, landfil_sorption_plus
from PFAS_SAT_InputData import LandfillInput
from .ProcessModel import ProcessModel


class Landfill(ProcessModel):
    """
************
Landfill
************

While the model describes a generic landfill, there are in practice four types of landfills (MSW, hazardous waste, C&D waste, ash). Each of these
types of landfill includes the same basic processes as illustrated in Figure below and each type may be represented by adjusting default parameters.
They may be unlined (e.g., many C&D landfills), have a single liner system (e.g., most MSW landfills), or be double-lined (e.g., hazardous waste
landfills). The landfills may or may not have active gas collection and control systems. If there is an active gas control system utilizing a flare
or engine, then some fraction of the volatilized or aerosolized PFAS may be destroyed. The PFAS that is not released remains stored in the landfill.


To calculate PFAS release, the disposed PFAS-containing waste material is assumed to be well mixed with the bulk MSW. The area occupied by the
disposed waste is estimated based on a default parameter that represents the mass of total waste that can be disposed per unit area. The area
occupied by the PFAS-containing waste mixed in with MSW is coupled with the leachate generation rate (volume/area-time) to estimate the
volume of leachate produced. The partitioning of PFAS from the solid waste to the aqueous phase is modeled using a liquid-solid partition
coefficient normalized to the amount of organic carbon. Model predictions are based on achievement of equilibrium. By default, it
is assumed that no volatilization occurs, but a user can enter a fraction of PFAS that is volatilized.


The partition coefficient is used to estimate the concentration of PFAS in the liquid and solids. The concentration in the liquid changes throughout
the year as is leached to the leachate collection system (i.e., it is assumed that leaching is uniform throughout the year and continuously removes
PFAS from the mixture). The leachate collection efficiency is used to calculate the fraction of leachate that is collected and subsequently treated.
The landfill process models in the SAT is designed so that by changing default parameters, a variety of landfill processes can be represented. For
example, a C&D landfill without a liner would be modeled with no collection efficiency, all the generated leachate would be released to groundwater.
A double-lined hazardous waste landfill could be modeled by increasing the leachate collection efficiency.

=============================
Assumptions and Limitations:
=============================

#. The organic carbon-normalized partition coefficient assumes that the organic carbon in different materials generally
   have the PFAS sorption capacity. However, material-specific coefficients were developed for activated carbon,
#. Volatilization is assumed to be zero by default due to a lack of data. However, the user may assign a fraction of
   the PFAS to be volatilized.
#. Future work is also required to implement a dynamic (i.e., non-equilibrium) model to account for changes in the
   organic C content of over time as landfilled materials decompose, and the effectiveness of cover system improves.
#. PFAS release is based on 1 year. A longer time horizon would result in additional PFAS release.
    """
    ProductsType = ['LFLeachate']

    def __init__(self, input_data_path=None, CommonDataObject=None, InventoryObject=None, Name=None):
        super().__init__(CommonDataObject, InventoryObject)
        self.InputData = LandfillInput(input_data_path)
        self.Name = Name if Name else 'Landfill'

    def calc(self, Inc_flow):
        # Initialize the Incoming flow
        self.Inc_flow = Inc_flow

        # Calculating the mass of MSW in Landfill
        MSW_Mass = self.Inc_flow.mass / self.InputData.LFMSW['frac_of_msw']['amount'] - self.Inc_flow.mass

        # Initializing the MSW in Landfill
        self.MSW_flow = Flow(self.CommonData)
        kwargs = {}
        kwargs['mass_flow'] = MSW_Mass
        kwargs['ts_cont'] = self.InputData.LFMSW['ts_cont']['amount']
        kwargs['C_cont'] = self.InputData.LFMSW['C_cont']['amount']
        kwargs['bulk_dens'] = self.InputData.LFMSW['bulk_dens']['amount']
        self.MSW_flow.set_flow(**kwargs)

        # Mixing the Incoming flow with MSW in landfill
        self.Mixture = mix(self.Inc_flow, self.MSW_flow)

        # PFAS loss to volatilization
        self.Volatilized = Flow(self.CommonData)
        self.Volatilized.PFAS = self.Mixture.PFAS * self.InputData.Volatilization['frac_vol_loss']['amount']
        self.Mixture.PFAS = self.Mixture.PFAS - self.Volatilized.PFAS

        # Calculating the volume of percipitation (includes RunOff and Leachate)
        area = self.Mixture.mass / 1000 / self.InputData.LF['lf_ton_area']['amount']
        LF_Leachate_Vol = area * self.InputData.Water_Blnc['leach_gpad']['amount'] * 365.25 * self.InputData.Water_Blnc['is_leach_col']['amount'] * \
            self.InputData.Water_Blnc['frac_leach_col']['amount'] / 264.172 * 1000  # L/yr
        Leachate_Vol = (area * self.InputData.Water_Blnc['leach_gpad']['amount'] * (1 - self.InputData.Water_Blnc['is_leach_col']['amount'])
                        + area * self.InputData.Water_Blnc['leach_gpad']['amount'] * self.InputData.Water_Blnc['is_leach_col']['amount']
                        * (1 - self.InputData.Water_Blnc['frac_leach_col']['amount'])) * 365.25 / 264.172 * 1000  # L/yr

        # Calculating the PFAS in water and soil partitions
        if 'FlowType' in self.Inc_flow.__dict__:
            if self.Inc_flow.FlowType == 'SpentGAC':
                self.LF_storage, self.LF_Leachate, self.Leachate = landfil_sorption_plus(
                    mixture=self.Mixture,
                    LogPartCoef_data=self.InputData.LogPartCoef,
                    Additive_LogPartCoef=self.InputData.LogPartCoef_GAC,
                    Additive_mass=self.Inc_flow.ts,
                    LF_Leachate_Vol=LF_Leachate_Vol,
                    Leachate_Vol=Leachate_Vol)

            elif self.Inc_flow.FlowType == 'StabilizedSoil':
                self.LF_storage, self.LF_Leachate, self.Leachate = landfil_sorption_plus(
                    mixture=self.Mixture,
                    LogPartCoef_data=self.InputData.LogPartCoef,
                    Additive_LogPartCoef=self.Inc_flow.AddLogPartCoef,
                    Additive_mass=self.Inc_flow.Additive_mass,
                    LF_Leachate_Vol=LF_Leachate_Vol,
                    Leachate_Vol=Leachate_Vol)

            elif self.Inc_flow.FlowType == 'SpentIER':
                self.LF_storage, self.LF_Leachate, self.Leachate = landfil_sorption_plus(
                    mixture=self.Mixture,
                    LogPartCoef_data=self.InputData.LogPartCoef,
                    Additive_LogPartCoef=self.InputData.LogPartCoef_SpentIER,
                    Additive_mass=self.Inc_flow.ts,
                    LF_Leachate_Vol=LF_Leachate_Vol,
                    Leachate_Vol=Leachate_Vol)

            else:
                self.LF_storage, self.LF_Leachate, self.Leachate = landfil_sorption(self.Mixture, self.InputData.LogPartCoef,
                                                                                    LF_Leachate_Vol, Leachate_Vol)
        else:
            self.LF_storage, self.LF_Leachate, self.Leachate = landfil_sorption(self.Mixture, self.InputData.LogPartCoef,
                                                                                LF_Leachate_Vol, Leachate_Vol)

        # add to Inventory
        self.Inventory.add('Volatilized', self.Name, 'Air', self.Volatilized)
        self.Inventory.add('Leachate', self.Name, 'Water', self.Leachate)
        self.Inventory.add('Storage', self.Name, 'Stored', self.LF_storage)

    def products(self):
        Products = {}
        Products['LFLeachate'] = self.LF_Leachate
        return Products

    def setup_MC(self, seed=None):
        self.InputData.setup_MC(seed)

    def MC_Next(self):
        input_list = self.InputData.gen_MC()
        return input_list

    def report(self, normalized=False):
        report = pd.DataFrame(index=self.Inc_flow._PFAS_Index)
        if not normalized:
            report['Volatilized'] = self.Volatilized.PFAS
            report['Collected Leachate'] = self.LF_Leachate.PFAS
            report['Fugitive Leachate'] = self.Leachate.PFAS
            report['Remaining in Landfill'] = self.LF_storage.PFAS
        else:
            report['Volatilized'] = round(self.Volatilized.PFAS / self.Inc_flow.PFAS * 100, 4)
            report['Collected Leachate'] = round(self.LF_Leachate.PFAS / self.Inc_flow.PFAS * 100, 4)
            report['Fugitive Leachate'] = round(self.Leachate.PFAS / self.Inc_flow.PFAS * 100, 4)
            report['Remaining in Landfill'] = round(self.LF_storage.PFAS / self.Inc_flow.PFAS * 100, 4)
            report.fillna(0.0, inplace=True)
        return report
