# -*- coding: utf-8 -*-
import pandas as pd
from .Flow import Flow
from PFAS_SAT_InputData import ADInput
from .ProcessModel import ProcessModel
from .SubProcesses import split, curing, AddWater, solid_water_partition, dewatering


class AD(ProcessModel):
    """
**************************
Anaerobic Digestion (AD)
**************************

AD can accept food waste or wastewater treatment solids to stabilize them prior to aerobic curing and/or land application.
The residual solids from AD can be further dewatered and the aerobically cured prior to land application. The liquid
stream (digestate) may be returned to the AD process in some cases (e.g., a low solids food waste system) or sent to WWT.
While it is possible that PFAS are volatilized/aerosolized during digestion and/or aerobic curing, as noted earlier,
the default PFAS release to the air is zero.

During digestion, the feedstocks (e.g., WWT solids, food waste) partially biodegrade with the conversion of solids to
biogas. Model predictions of PFAS fate are based on achievement of equilibrium. The partition coefficient is used to
estimate the concentration of PFAS in the liquid and solids. VS destruction during digestion changes the equilibrium
PFAS distribution between the solid and aqueous phases. There are several different potential AD processes
(e.g., thermophilic, mesophilic, single stage, multi-stages). The AD process model in the SAT framework is
designed so that by changing default parameters, different AD systems can be represented.

=============================
Assumptions and Limitations:
=============================

#. The model assumes that there is no water loss during anaerobic digestion, and that the C concentration in the solids
   remains constant.
#. Volatilization is assumed to be zero by default due to a lack of data. However, the user may assign a fraction of the PFAS
   that volatilizes/aerosolizes.
#. Future work is required to implement a dynamic model to account for changes in the organic C content over time as materials
   decompose in the reactor and during aerobic curing.
#. We do not consider the possible conversion of "precursor" compounds to commonly measured PFAAs.
#. Anaerobic digestion processes are sometimes preceded by a thermal pre-treatment process for the purpose of enhancing
   methane production. Thermal pretreatment can also enhance precursor conversion to PFAAs. This can lead to an increase
   in aqueous PFAA concentrations across the process.
    """
    ProductsType = ['ADLiquids', 'ADSolids', 'Compost']

    def __init__(self, input_data_path=None, CommonDataObject=None, InventoryObject=None, Name=None):
        super().__init__(CommonDataObject, InventoryObject)
        self.InputData = ADInput(input_data_path)
        self.Name = Name if Name else 'AD'

    def calc(self, Inc_flow):
        # Initialize the Incoming flow
        self.Inc_flow = Inc_flow

        # PFAS Balance
        self.Volatilization = Flow(self.CommonData)
        self.Digestate_product = Flow(self.CommonData)
        self.Volatilization.PFAS = self.Inc_flow.PFAS * self.InputData.AD['frac_PFAS_to_Vol']['amount']
        self.Digestate_product.PFAS = self.Inc_flow.PFAS - self.Volatilization.PFAS

        # AD Reactor: Add water
        self.ReactorInput = AddWater(InputFlow=self.Inc_flow,
                                     Final_Moist_Cont=self.InputData.AD['Reac_moist']['amount'])

        # Mass balance
        vs_loss = self.ReactorInput.VS * self.InputData.AD['frac_VS_loss']['amount']
        self.Digestate_product.ts = self.ReactorInput.ts - vs_loss
        self.Digestate_product.moist = self.ReactorInput.moist
        self.Digestate_product.mass = self.Digestate_product.moist + self.Digestate_product.ts
        self.Digestate_product.C = self.ReactorInput.get_Ccont() * self.Digestate_product.ts  # Assume C content of solids does not change.
        self.Digestate_product.VS = self.ReactorInput.VS - vs_loss

        # Partitioning
        C_Solid, C_Water = solid_water_partition(mixture=self.Digestate_product,
                                                 water_vol=self.Digestate_product.moist * 1,
                                                 LogPartCoef_data=self.InputData.LogPartCoef)

        # Dewatering
        self.ADSolids, self.ADLiquids = dewatering(mixture=self.Digestate_product,
                                                   final_sol_cont=self.InputData.Dew['Digestate_moist']['amount'],
                                                   cont_PFAS_water=C_Water,
                                                   is_active=True)

        # Allocate digestate to Curing
        frac_curing = self.InputData.AD['frac_cured']['amount']
        self.ADSolidProducts = split(self.ADSolids, **{'to_land_app': 1 - frac_curing, 'to_curing': frac_curing})

        # Curing
        if self.ADSolidProducts['to_curing'].PFAS.sum() > 0:
            self.Compost, self.Contact_Water = curing(self.ADSolidProducts['to_curing'],
                                                      self.InputData.Curing,
                                                      self.InputData.LogPartCoef,
                                                      self.InputData.Precip)
        else:
            self.Compost = Flow(self.CommonData, ZeroFlow=True)
            self.Contact_Water = Flow(self.CommonData, ZeroFlow=True)

        # add to Inventory
        self.Inventory.add('Volatilization', self.Name, 'Air', self.Volatilization)
        self.Inventory.add('Contact Water', self.Name, 'Water', self.Contact_Water)

    def products(self):
        Products = {}
        Products['ADLiquids'] = self.ADLiquids
        Products['ADSolids'] = self.ADSolidProducts['to_land_app']
        Products['Compost'] = self.Compost
        return(Products)

    def setup_MC(self, seed=None):
        self.InputData.setup_MC(seed)

    def MC_Next(self):
        input_list = self.InputData.gen_MC()
        return(input_list)

    def report(self, normalized=False):
        report = pd.DataFrame(index=self.Inc_flow._PFAS_Index)
        if not normalized:
            report['Volatilization'] = self.Volatilization.PFAS
            report['ADSolids'] = self.ADSolidProducts['to_land_app'].PFAS
            report['ADLiquids'] = self.ADLiquids.PFAS
            report['Compost'] = self.Compost.PFAS
            report['Contact Water'] = self.Contact_Water.PFAS
        else:
            report['Volatilization'] = round(self.Volatilization.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['ADSolids'] = round(self.ADSolidProducts['to_land_app'].PFAS / self.Inc_flow.PFAS * 100, 2)
            report['ADLiquids'] = round(self.ADLiquids.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Compost'] = round(self.Compost.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Contact Water'] = round(self.Contact_Water.PFAS / self.Inc_flow.PFAS * 100, 2)
            report.fillna(0.0, inplace=True)
        return(report)
