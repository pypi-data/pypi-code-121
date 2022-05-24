"""
This module implements a generic energy-storage model, developed by IFES LUH.

The central class is EnergyStorage. An EnergyStorage contains the model parameter and the
state of the storage. Plus it has several functions to charge or discharge the storage.
"""
import numpy as np

class EnergyStorage:
    """
    Models a generic energy storage. Mainly the storage takes two effects into account:
    1. (charge, discharge)-efficiency
    2. selfDischarge
    """

    class Builder:
        """
        Builder for the EnergyModel.
        """

        def __init__(self):
            self.b_step = 0
            self.b_step_size = 15
            self.b_load = 1
            self.b_time_constant = 0.1
            self.b_capacity = 100
            self.b_charge_efficiency = 0.9
            self.b_discharge_efficiency = 0.9
            self.b_max_discharge = 100
            self.b_max_charge = 100
            self.b_operating_cost = 0

        def max_charge(self, max_charge):
            """
            Sets the max_charge

            :param max_charge: max charge
            :returns: Builder to chain method-calls
            """
            self.b_max_charge = max_charge
            return self

        def max_discharge(self, max_discharge):
            """
            Sets the max_discharge

            :param max_discharge: max discharge
            :returns: Builder to chain method-calls
            """
            self.b_max_discharge = max_discharge
            return self

        def step(self, step):
            """
            Sets the step.

            :param step: the new step
            :returns: Builder to chain method-calls
            """
            self.b_step = step
            return self

        def step_size(self, step_size):
            """
            Sets the stepSize.

            :param step_size: the new stepSize
            :returns: Builder to chain method-calls
            """
            self.b_step_size = step_size
            return self

        def load(self, load):
            """
            Sets the initial load.

            :param load: the initial load
            :returns: Builder to chain method-calls
            """
            self.b_load = load
            return self

        def time_constant(self, time_constant):
            """
            Sets the timeConstant.

            :param time_constant: the new timeConstant-value
            :returns: Builder to chain method-calls
            """
            self.b_time_constant = time_constant
            return self

        def capacity(self, capacity):
            """
            Sets the capacity.

            :param capacity: the new capacity
            :returns: Builder to chain method-calls
            """
            self.b_capacity = capacity
            return self

        def charge_efficiency(self, charge_efficiency):
            """
            Sets the chargeEfficiency.

            :param charge_efficiency: the new chargeEfficiency
            :returns: Builder to chain method-calls
            """
            self.b_charge_efficiency = charge_efficiency
            return self

        def discharge_efficiency(self, discharge_efficiency):
            """
            Sets the dischargeEfficiency.

            :param discharge_efficiency: the new dischargeEfficiency
            :returns: Builder to chain method-calls
            """
            self.b_discharge_efficiency = discharge_efficiency
            return self

        def self_discharge(self, self_discharge):
            """
            Sets the self discharge of the energy storage in percent / d.

            :param self_discharge: self discharge in per/d
            :returns: Builder to chain method-calls
            """
            self.b_time_constant = convert_to_time_constant(self_discharge)
            return self

        def operating_cost(self, operating_cost):
            """
            Set the operating cost

            :param operating_cost:
            :returns: Builder
            """
            self.b_operating_cost = operating_cost
            return self

        def build(self):
            """
            Builds the EnergyStorage
            :returns: new EnergyStorage with set parameters
            """
            return EnergyStorage(self)

    # ---------------------------------------------------------------------

    def __init__(self, builder):
        """
        Initializes the model with some parameters.

        :param builder: Builder object containing the model parameters
        """
        self.__step = builder.b_step
        self.__step_size = builder.b_step_size
        self.__load = builder.b_load
        self.__time_constant = builder.b_time_constant
        self.__capacity = builder.b_capacity
        self.__charge_efficiency = builder.b_charge_efficiency
        self.__discharge_efficiency = builder.b_discharge_efficiency
        self.__max_discharge = builder.b_max_discharge
        self.__max_charge = builder.b_max_charge
        self.__operating_cost = builder.b_operating_cost
        self.__cache_exp_component = None 
        self.__dirty = True

    def __str__(self):
        return "[ %s, %s, %s, %s, %s, %s, %s, %s ]" % (self.__step, self.__step_size, self.__load, self.__time_constant,
                                                   self.__capacity, self.__charge_efficiency, self.__discharge_efficiency,
                                                   self.__operating_cost)

    @property
    def operating_cost(self):
        """
        :returns: cost-horizon, operating-cost in the planning_horizon
        """
        return self.__operating_cost

    @property
    def max_discharge(self):
        """
        :returns: max discharge capability of the storage
        """
        return self.__max_discharge

    @property
    def max_charge(self):
        """
        :returns: max charge capability of the storage
        """
        return self.__max_charge

    @property
    def load(self):
        """
        :returns: current load of the storage
        """
        return self.__load

    @load.setter
    def load(self, new_load):
        """
        Set the load state

        :param new_load: new load
        """
        self.__load = new_load

    @property
    def capacity(self):
        """
        :returns: capacity of the storage
        """
        return self.__capacity

    def set_self_discharge(self, self_discharge):
        """
        Sets the self discharge of the energy storage in percent / d.
        """
        self.__time_constant = convert_to_time_constant(self_discharge)
        self.__dirty = True

    def charge(self, charge_energy):
        """
        Charges the storage with a given amount of energy <code>charge_energy</code>.

        :param charge_energy: energy to be charged
        :returns: new storage load
        """
        self.__step += 1
        self.__load = self.__calc_next(charge_energy, True)
        return self.__load

    def discharge(self, discharge_energy):
        """
        Discharges the storage with a given amount of energy <code>discharge_energy</code>.

        :param discharge_energy: energy to be discharged
        :returns: new storage load
        """
        self.__step += 1
        self.__load = self.__calc_next(-discharge_energy, False)
        return self.__load

    def apply_load(self, new_load, output_map=lambda x: abs(x)):
        """
        Applies new_load to the storage, therefor it calculates the amount of energy
        charged (or discharged) and returns it.

        :param new_load: new load to apply
        """
        self.__step += 1
        energy = output_map(self.__calc_energy(new_load))
        self.__load = new_load
        return energy

    def __calc_energy(self, new_load):
        """
        Calc energy of the state change to new_load.

        :param new_load: new load of storage
        :returns: energy amount of state change
        """
        is_charge = new_load > self.__load
        exp_component = self.__calc_exp_component()
        return (((new_load - self.__load * exp_component) / (1 - exp_component)) \
             * (self.__capacity / self.__time_constant)) \
             / (self.__charge_efficiency if is_charge else (1 / self.__discharge_efficiency))


    def __calc_next(self, energy, is_charge):
        """
        Calculates next state of the model when charging/discharging an amount of <code>energy</code>
        to the battery. Therefor there exists the <code>is_charge</code>-Flag.

        :param energy: amount of energy to be charged/discharged
        :param is_charge: indicates whether you want to charge/discharge energy to the storage
        :returns: new load after charging/discharging the amount
        """
        exp_component = self.__calc_exp_component()
        return self.__load * exp_component + energy \
                * (self.__time_constant / self.__capacity) \
                * (1 - exp_component) \
                * (self.__charge_efficiency if is_charge else (1 / self.__discharge_efficiency))

    def __calc_exp_component(self):
        """
        Calculates the exp part of the SoC-Calculation. Aditionally to the original equation this calculation avoid float division by zero.
        Also the exp-component gets cached and will only be calculated again if step_size or the time_constant changes.

        :returns: exp part or (when time_constant is 0) 0
        """
        if self.__time_constant == 0:
            return 0

        if self.__cache_exp_component is None or self.__dirty:
            self.__dirty = False
            self.__cache_exp_component = np.exp(-self.__step_size / self.__time_constant)

        return self.__cache_exp_component

    def remaining_load(self):
        """
        Calculates the remaining load for discharge

        :returns: remaining energy in W
        """
        exp_component = self.__calc_exp_component()
        return (self.__load * exp_component) / \
                    ((self.__time_constant / self.__capacity) \
                    * (1 - exp_component) \
                    * (1 / self.__discharge_efficiency))

    def load_until_cap(self):
        """
        Calculates the load in W until the cap is reached

        :returns: necessary energy in W until cap
        """
        exp_component = self.__calc_exp_component()
        return (1 - self.__load * exp_component) / \
                ((self.__time_constant / self.__capacity) \
                * (1 - exp_component) \
                * (self.__charge_efficiency))

    def possible_load_one_step(self):
        """
        Calculates max possible load after one step for charging and discharging

        :returns: tuple of load state (min_load_after_discharge, max_load_after_charge)
        """
        return [max(0, self.__calc_next(-self.__max_discharge, False)), min(1, self.__calc_next(self.__max_charge, True))]

    def min_load_one_step_discharge(self):
        """
        Calculates min load after on step of discharging. This is relevant due to self-discharge-effect.

        :returns: minimum valid load after discharge
        """
        return max(0, self.__calc_next(0, False))

    @staticmethod
    def builder():
        """
        Create a Builder and return it.
        :returns: a new Builder
        """
        return EnergyStorage.Builder()


MIN_VALUE_NOT_ZERO = 0.000000000000001

def convert_to_time_constant(self_discharge):
    """
    Converts self discharge of the energy storage in percent / d to time constant.
    """
    self_discharge_modified = self_discharge
    if self_discharge == 0:
        self_discharge_modified += MIN_VALUE_NOT_ZERO

    return 1 / np.log(1 + self_discharge_modified)
