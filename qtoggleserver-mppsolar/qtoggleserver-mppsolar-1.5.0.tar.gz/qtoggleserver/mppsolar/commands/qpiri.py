
from .base import Command

from qtoggleserver.mppsolar import constants


class QPIRI(Command):
    REQUEST_FMT = 'QPIRI'

    UNITS = {
        'battery_back_to_charging_voltage': 'V',
        'battery_cut_off_voltage': 'V',
        'battery_bulk_charging_voltage': 'V',
        'battery_float_charging_voltage': 'V',
        'battery_max_grid_charging_current': 'A',
        'battery_max_charging_current': 'A',
        'battery_back_to_discharging_voltage': 'V',
        'battery_max_discharging_current': 'A',
    }

    DISPLAY_NAMES = {
        'battery_back_to_charging_voltage': 'Battery Back-to-charging Voltage',
        'battery_cut_off_voltage': 'Battery Cut-off Voltage',
        'battery_bulk_charging_voltage': 'Battery Bulk Charging Voltage',
        'battery_float_charging_voltage': 'Battery Float Charging Voltage',
        'battery_type': 'Battery Type',
        'battery_max_grid_charging_current': 'Battery Max Grid Charging Current',
        'battery_max_charging_current': 'Battery Max Charging Current',
        'output_source_priority': 'Output Source Priority',
        'charging_source_priority': 'Charging Source Priority',
        'battery_back_to_discharging_voltage': 'Battery Back-to-discharging Voltage',
        'battery_max_discharging_current': 'Battery Max Discharging Current',
    }

    CHOICES = {
        'battery_type': constants.BATTERY_TYPE_CHOICES,
        'output_source_priority': constants.OUTPUT_SOURCE_PRIORITY_CHOICES,
        'charging_source_priority': constants.CHARGING_SOURCE_PRIORITY_CHOICES,
        'battery_max_discharging_current': constants.BATTERY_MAX_DISCHARGING_CURRENT_CHOICES,
    }


class QPIRI_GK(QPIRI):
    RESPONSE_FMT = (
        '{_grid_rating_voltage:f} '
        '{_grid_rating_current:f} '
        '{_ac_output_rating_voltage:f} '
        '{_ac_output_rating_frequency:f} '
        '{_ac_output_rating_current:f} '
        '{_ac_output_rating_apparent_power:f} '
        '{_ac_output_rating_active_power:f} '
        '{_battery_rating_voltage:f} '
        '{battery_back_to_charging_voltage:f} '
        '{battery_cut_off_voltage:f} '
        '{battery_bulk_charging_voltage:f} '
        '{battery_float_charging_voltage:f} '
        '{battery_type:d} '
        '{battery_max_grid_charging_current:d} '
        '{battery_max_charging_current:d} '
        '{_input_voltage_range:d} '
        '{output_source_priority:d} '
        '{charging_source_priority:d} '
        '{_parallel_max:d} '
        '{_type:d} '
        '{_topology:d} '
        '{_output_mode:d} '
        '{battery_back_to_discharging_voltage:f} '
        '{_parallel_pv_ok:d} '
        '{_parallel_pv_power_balance:d}'
    )


class QPIRI_MK(QPIRI):
    RESPONSE_FMT = (
        '{_grid_rating_voltage:f} '
        '{_grid_rating_current:f} '
        '{_ac_output_rating_voltage:f} '
        '{_ac_output_rating_frequency:f} '
        '{_ac_output_rating_current:f} '
        '{_ac_output_rating_apparent_power:f} '
        '{_ac_output_rating_active_power:f} '
        '{_battery_rating_voltage:f} '
        '{battery_back_to_charging_voltage:f} '
        '{battery_cut_off_voltage:f} '
        '{battery_bulk_charging_voltage:f} '
        '{battery_float_charging_voltage:f} '
        '{battery_type:d} '
        '{battery_max_grid_charging_current:d} '
        '{battery_max_charging_current:d} '
        '{_input_voltage_range:d} '
        '{output_source_priority:d} '
        '{charging_source_priority:d} '
        '{_parallel_max:d} '
        '{_type:d} '
        '{_topology:d} '
        '{_output_mode:d} '
        '{battery_back_to_discharging_voltage:f} '
        '{_parallel_pv_ok:d} '
        '{_parallel_pv_power_balance:d} '
        '{_battery_max_cv_charging_time:d} '
        '{_operation_logic:d}'
    )


class QPIRI_MAX(QPIRI):
    RESPONSE_FMT = (
        '{_grid_rating_voltage:f} '
        '{_grid_rating_current:f} '
        '{_ac_output_rating_voltage:f} '
        '{_ac_output_rating_frequency:f} '
        '{_ac_output_rating_current:f} '
        '{_ac_output_rating_apparent_power:f} '
        '{_ac_output_rating_active_power:f} '
        '{_battery_rating_voltage:f} '
        '{battery_back_to_charging_voltage:f} '
        '{battery_cut_off_voltage:f} '
        '{battery_bulk_charging_voltage:f} '
        '{battery_float_charging_voltage:f} '
        '{battery_type:d} '
        '{battery_max_grid_charging_current:d} '
        '{battery_max_charging_current:d} '
        '{_input_voltage_range:d} '
        '{output_source_priority:d} '
        '{charging_source_priority:d} '
        '{_parallel_max:d} '
        '{_type:d} '
        '{_topology:d} '
        '{_output_mode:d} '
        '{battery_back_to_discharging_voltage:f} '
        '{_parallel_pv_ok:d} '
        '{_parallel_pv_power_balance:d} '
        '{_battery_max_cv_charging_time:d} '
        '{_operation_logic:d} '
        '{battery_max_discharging_current:d}'
    )
