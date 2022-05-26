# -*- coding: utf-8 -*-
import pandas as pd
from .Flow import Flow
from .SubProcesses import mix, aerobic_composting, curing, split
from PFAS_SAT_InputData import CompInput
from .ProcessModel import ProcessModel


class Comp(ProcessModel):
    """
*************
Composting
*************

Composting can accept specific fractions of MSW including food, yard, and some paper wastes. It is also capable of treating dried and
stabilized WWT solids. The primary purpose of composting is to produce a stabilized organic product that can be used as a soil amendment
to enhance water retention, carbon and nutrient content, and erosion control among other potential benefits. In addition to finished compost,
composting systems also produce residual solid materials from pre- and post-screening. Those materials can be combusted or landfilled.
Compost also may produce leachate that needs to be managed through wastewater treatment. It is also possible that PFAS are volatilized
during aerobic composting due to the elevated temperatures and stripping from active aeration, but there is currently no data on this
potential pathway.

In the composting process model, feedstocks (e.g., WWT solids or food waste) are mixed with amendments (wood chips by default) to
increase porosity to allow air flow through the system. Active composting may be under cover or open to the atmosphere. In the latter
case, there will be contact water that may contain PFAS that will need to be managed.

Model predictions are based on achievement of equilibrium. The partition coefficient is used to estimate the concentration of PFAS in
the liquid and solids. The concentration in the liquid changes throughout the year as PFAS leaches through the compost piles (i.e., it
is assumed that annual precipitation is uniform throughout the year and continuously removes PFAS from the mixture). The model then
calculates a fraction of precipitation that becomes contact water. The contact water can either be collected and managed or be released to
surface or ground- water depending on the composting process and applicable regulations. If active composting is under a cover, then no
contact water is included. The PFAS that is not removed in the contact water remains in the compost. By default, the compost is cured after
active composting. The curing model is the same as the active composting model, except it is not covered and contact water is not managed.
Any PFAS that does not leave the curing piles through leaching or run-off remains in the finished compost that will be either land applied or
landfilled.

The behavior of the finished compost in a landfill and land application process are described in their respective sections. There
are several different compost processes (e.g., windrows, static piles, in-vessel). The compost process model in the SAT framework is designed
so that by changing default parameters, any compost process can be represented.

============================
Assumptions and Limitations
============================

1.	Organic carbon partitioning coefficients determined from soils/sediments are used for compost partitioning.
2.	Wood chips are currently the only amendment that is built into the material flow properties.
3.	We assume that the mass of solid loss per carbon loss is similar both for active and curing composting stages.
4.	Volatilization is assumed to be zero by default. However, the user may assign a fraction of the PFAS to be volatilized.
5.	Future work is required to implement a dynamic (i.e., non-equilibrium) model to account for changes in the organic C
    content over time as composted materials decompose, and to account for episodic precipitation events.
6.	We do not consider the possible conversion of "precursor" compounds to commonly measured PFAAs.

    """
    ProductsType = ['Compost', 'ContactWater', 'CompostResiduals']

    def __init__(self, input_data_path=None, CommonDataObject=None, InventoryObject=None, Name=None):
        super().__init__(CommonDataObject, InventoryObject)
        self.InputData = CompInput(input_data_path)
        self.Name = Name if Name else 'Composting'

    def calc(self, Inc_flow):
        # Initialize the Incoming flow
        self.Inc_flow = Inc_flow

        # Screen
        rmvd_frac = self.InputData.Screen['frac_rmvd']['amount']
        self.Screen = split(self.Inc_flow, **{'CompostFeedstock': 1 - rmvd_frac, 'CompostResiduals': rmvd_frac})

        # Calculating the mass of Amendments
        Amnd_mass = self.InputData.AmndProp['mass_ratio']['amount'] * self.Screen['CompostFeedstock'].ts /\
            self.InputData.AmndProp['ts_cont']['amount']

        # Initializing the Soil flow
        self.Amnd_flow = Flow(self.CommonData)
        kwargs = {}
        kwargs['mass_flow'] = Amnd_mass
        kwargs['ts_cont'] = self.InputData.AmndProp['ts_cont']['amount']
        kwargs['C_cont'] = self.InputData.AmndProp['C_cont']['amount']
        self.Amnd_flow.set_flow(**kwargs)

        # Mixing the Incoming flow with soil
        self.Mix_to_ac = mix(self.Screen['CompostFeedstock'], self.Amnd_flow)

        # PFAS loss to volatilization
        self.Volatilized = Flow(self.CommonData)
        self.Volatilized.PFAS = self.Mix_to_ac.PFAS * self.InputData.Volatilization['frac_vol_loss']['amount']
        self.Mix_to_ac.PFAS = self.Mix_to_ac.PFAS - self.Volatilized.PFAS

        # Active Composting
        self.Mix_to_cu, self.Contact_Water_ac, self.Collected_Contact_water_ac = aerobic_composting(self.Mix_to_ac,
                                                                                                    self.InputData.AComp,
                                                                                                    self.InputData.LogPartCoef,
                                                                                                    self.InputData.Precip)

        # Curing
        self.Finished_Comp, self.Contact_Water_cu = curing(self.Mix_to_cu,
                                                           self.InputData.Curing,
                                                           self.InputData.LogPartCoef,
                                                           self.InputData.Precip)

        self.Contact_water = mix(self.Contact_Water_ac, self.Contact_Water_cu)

        # add to Inventory
        self.Inventory.add('Volatilized', self.Name, 'Air', self.Volatilized)
        self.Inventory.add('Contact Water', self.Name, 'Water', self.Contact_water)

    def products(self):
        Products = {}
        Products['Compost'] = self.Finished_Comp
        Products['ContactWater'] = self.Collected_Contact_water_ac
        Products['CompostResiduals'] = self.Screen['CompostResiduals']
        return(Products)

    def setup_MC(self, seed=None):
        self.InputData.setup_MC(seed)

    def MC_Next(self):
        input_list = self.InputData.gen_MC()
        return(input_list)

    def report(self, normalized=False):
        report = pd.DataFrame(index=self.Inc_flow._PFAS_Index)
        if not normalized:
            report['Volatilized'] = self.Volatilized.PFAS
            report['Compost'] = self.Finished_Comp.PFAS
            report['Contact water'] = self.Contact_water.PFAS
            report['Collected Contact water'] = self.Collected_Contact_water_ac.PFAS
            report['Compost Residuals'] = self.Screen['CompostResiduals'].PFAS
        else:
            report['Volatilized'] = round(self.Volatilized.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Compost'] = round(self.Finished_Comp.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Contact water'] = round(self.Contact_water.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Collected Contact water'] = round(self.Collected_Contact_water_ac.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Compost Residuals'] = round(self.Screen['CompostResiduals'].PFAS / self.Inc_flow.PFAS * 100, 2)
            report.fillna(0.0, inplace=True)

        return(report)
