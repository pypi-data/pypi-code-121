# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 11:51:33 2020

@author: msmsa
"""
import pandas as pd
from .Flow import Flow
from .SubProcesses import mix, soil_sorption
from PFAS_SAT_InputData import LandAppInput
from .ProcessModel import ProcessModel


class LandApp(ProcessModel):
    """
**************************
Land Application
**************************

Finished compost and dewatered, stabilized WWT solids are both suitable for land application. Once these materials are land applied,
PFAS may volatize, be released to surface or ground- water, or sorbed to the soil/waste stream mixture. The flow of PFAS from land
application is modeled using a liquid-solid partition coefficient normalized to the amount of organic carbon, combined with a water
balance to track the flow of PFAS from the soil. Model predictions are based on achievement of equilibrium. By default, it is assumed
that no volatilization occurs, but a user can enter a fraction of PFAS that volatilizes. It is further assumed that the land applied
material is well mixed with the top layer of soil (thickness is a user input). The partition coefficient is used to estimate the
concentration of PFAS in the liquid and solids. The concentration in the liquid changes throughout the year as PFAS runs off or is
leached to the groundwater (i.e., it is assumed that annual precipitation is uniform throughout the year and continuously removes
PFAS from the mixture). The user enters a run-off coefficient based on the soil type, land use, grade, and vegetation. The run-off is
assumed to be released to surface water. Another fraction of the precipitation is removed via evapotranspiration (ET) based on the
local climate and vegetation. The remaining precipitation is assumed to leach into groundwater. The PFAS remaining in the soil may
be taken up by and bioaccumulate in plants. While PFAS uptake by plants was not modeled in this initial version of the SAT, it may
be an important PFAS fate pathway as plants may enter the food chain depending on what is grown.

=============================
Assumptions and Limitations:
=============================

#. The organic carbon-normalized partition coefficient assumes that the organic carbon in the soil has the same PFAS sorption capacity
   as the organic carbon in either the compost or the dewatered, stabilized WWT solids in the land applied material.
#. The water balance model is averaged over a year and ignores potential effects from intense rains that may lead to substantial
   additional erosion and loss of solids and associated PFAS.
#. Apart from precipitation, the water balance does not consider other external water inputs such as irrigation. This could be
   included by adjusting the precipitation input value.
#. Volatilization is assumed to be zero by default due to a lack of data. However, the user may assign a fraction of the PFAS to
   be volatilized.
#. Future work is also required to implement a dynamic model to account for changes in the organic C content of over time as
   land-applied materials decompose, and to account for episodic precipitation events.
#. The loading rate for the land application of dewatered WWT solids will vary based on solids properties among other factors.
   The loading rate default values given here reflect a typical annual loading rate for application to agricultural land growing corn.
    """
    ProductsType = []

    def __init__(self, input_data_path=None, CommonDataObject=None, InventoryObject=None, Name=None):
        super().__init__(CommonDataObject, InventoryObject)
        self.InputData = LandAppInput(input_data_path)
        self.Name = Name if Name else 'Land Application'

    def calc(self, Inc_flow):
        # Initialize the Incoming flow
        self.Inc_flow = Inc_flow

        # Calculating the mass of soil mixed with the Incoming flow
        soil_mass_mix = self.InputData.LandApp['depth_mix']['amount'] * self.Inc_flow.ts \
            / self.InputData.LandApp['appl_dens']['amount'] * self.InputData.SoilProp['bulk_dens']['amount']

        # Initializing the Soil flow
        self.Soil_flow = Flow(self.CommonData)
        kwargs = {}
        for key, data in self.InputData.SoilProp.items():
            kwargs[key] = data['amount']
        kwargs['mass_flow'] = soil_mass_mix
        self.Soil_flow.set_flow(**kwargs)

        # Mixing the Incoming flow with soil
        self.Mixed_flow = mix(self.Inc_flow, self.Soil_flow)

        # PFAS loss to volatilization
        self.Volatilized = Flow(self.CommonData)
        self.Volatilized.PFAS = self.Mixed_flow.PFAS * self.InputData.Volatilization['frac_vol_loss']['amount']
        self.Mixed_flow.PFAS = self.Mixed_flow.PFAS - self.Volatilized.PFAS

        # Calculating the volume of precipitation (includes RunOff and Leachate)
        Precip_Vol = self.Inc_flow.ts / self.InputData.LandApp['appl_dens']['amount'] * self.InputData.Precip['ann_precip']['amount'] * 1000  # L/yr
        total = self.InputData.Precip['frac_ET']['amount'] + self.InputData.Precip['frac_runoff']['amount']
        if total > 1:
            self.InputData.Precip['frac_ET']['amount'] /= total
            self.InputData.Precip['frac_runoff']['amount'] /= total

        ET_Vol = Precip_Vol * self.InputData.Precip['frac_ET']['amount']  # L/yr
        RunOff_Vol = Precip_Vol * self.InputData.Precip['frac_runoff']['amount']  # L/yr
        Leachate_Vol = Precip_Vol - ET_Vol - RunOff_Vol
        if Leachate_Vol < 0 and Leachate_Vol > -0.0001:
            Leachate_Vol = 0.0

        # Calculating the PFAS in water and soil partitions
        self.Remaining, self.Leachate, self.RunOff = soil_sorption(self.Mixed_flow, self.InputData.LogPartCoef, Leachate_Vol, RunOff_Vol)

        # add to Inventory
        self.Inventory.add('Volatilized', self.Name, 'Air', self.Volatilized)
        self.Inventory.add('Leachate', self.Name, 'Water', self.Leachate)
        self.Inventory.add('RunOff', self.Name, 'Water', self.RunOff)
        self.Inventory.add('Remaining', self.Name, 'Soil', self.Remaining)

    def products(self):
        Products = {}
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
            report['Remaining in Soil'] = self.Remaining.PFAS
            report['Leachate'] = self.Leachate.PFAS
            report['Runoff'] = self.RunOff.PFAS
        else:
            report['Volatilized'] = round(self.Volatilized.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Remaining in Soil'] = round(self.Remaining.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Leachate'] = round(self.Leachate.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Runoff'] = round(self.RunOff.PFAS / self.Inc_flow.PFAS * 100, 2)
            report.fillna(0.0, inplace=True)
        return report
