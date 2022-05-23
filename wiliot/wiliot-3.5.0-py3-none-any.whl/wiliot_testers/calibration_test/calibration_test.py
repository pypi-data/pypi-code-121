"""
  Copyright (c) 2016- 2021, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""

from time import sleep
from collections import Counter
import json
import numpy as np
import pandas as pd
from pathlib import Path
import serial

from wiliot.gateway_api.gateway import *

from wiliot.packet_data_tools.packet_list import PacketList
from wiliot.packet_data_tools.packet import Packet

from wiliot.wiliot_testers.test_equipment import Attenuator, EquipmentError
from wiliot.wiliot_testers.tester_utils import TagsHandling, update_json_field

simulation = False
fine_only = False


def set_attn_power(attn_obj, attn_power, simulation=simulation):
    """
    configure Attenuator to a specific value
    gets:
        attn_obj:       Attenuator obj
        attn_power:     value to set attn

    return:
        status if Attenuator is set correctly

    """
    if simulation:
        status = True
    else:
        status = True
        print('Setting Attenuator to {attn_power}dB'.format(attn_power=attn_power))
        attn_obj.Setattn(attn_power)
        sleep(2)

        attn_current_config = attn_obj.Getattn()
        if (float(attn_current_config) - attn_power) != 0:
            print('Error setting ATTENUATOR')
            status = False
        print(
            "Attenuator is set to: {attn_current_config} dB".format(
                attn_current_config=attn_current_config.split('.')[0]))
    return status


def start_harvesting(gw_obj, num_of_packets=100, loops_limit=int(100 * 1.5),
                     energy_pattern_val=20):
    """
    configure GW and start rx proccess, gets a specific number of packets
    gets:
        gw_obj:             Gateway obj
        num_of_packets:     number of packets to be collected using GW

    return:
        Dataframe containing packets and data
    """
    if num_of_packets != 100:
        loops_limit = int(num_of_packets * 1.5)
    print('extract {num_of_packets} packets'.format(num_of_packets=num_of_packets))
    missing_packets = num_of_packets
    num_of_loops = loops_limit

    gw_obj.config_gw(filter_val=False, pacer_val=0, energy_pattern_val=energy_pattern_val, time_profile_val=[5, 15],
                     received_channel=37, beacons_backoff_val=0)

    output_type = DataType.PACKET_CLASS

    packet_data = PacketList()
    gw_obj.reset_listener()


    while missing_packets > 0 and num_of_loops > 0:
        num_of_loops -= 1
        sleep(1)
        if gw_obj.is_data_available():

            if num_of_loops == 0:
                gw_answer = gw_obj.get_packets(action_type=ActionType.ALL_SAMPLE,
                                               data_type=output_type)
            else:
                gw_answer = gw_obj.try_get_packets(action_type=ActionType.FIRST_SAMPLES,
                                                     num_of_packets=num_of_packets,
                                                     data_type=output_type)
                # gw_answer = gw_obj.get_packets(action_type=ActionType.FIRST_SAMPLES, num_of_packets=missing_packets,
                #                                data_type=output_type)

            missing_packets = num_of_packets - gw_answer.size()

            packet_data = packet_data + gw_answer

    # gw_obj.stop_continuous_listener()

    gw_obj.config_gw(time_profile_val=[0, 6])

    # df = pd.DataFrame(packet_data)
    total_loops = loops_limit - num_of_loops
    return packet_data, total_loops


def packet_data_analysis(packet_data):
    """
    Analyze packet data and get primary data
    gets:
        packet_data:    Dataframe containing packet data

    return:  tuple with 2 cells:
        primary tag adv
        percentage of primary tag packets
        secondary tag adv
        percentage of secondary tag packets
        rssi of primary tag packets
        rssi of secondary tag packets

    """
    packets_df = packet_data.get_df()
    tag_ids = packets_df['adv_address']
    tag_ids_repetitions = dict(Counter(tag_ids))

    total_packets = sum(tag_ids_repetitions.values())

    primary_tag = max(tag_ids_repetitions, key=tag_ids_repetitions.get)
    primary_tag_ratio = round(tag_ids_repetitions[primary_tag] / total_packets, 2)
    secondary_tag_ids_repetitions = tag_ids_repetitions.copy()

    secondary_tag = None
    secondary_tag_ratio = 0
    rssi = None

    if len(secondary_tag_ids_repetitions) > 1:
        secondary_tag_ids_repetitions.pop(primary_tag)
        secondary_tag = max(secondary_tag_ids_repetitions, key=secondary_tag_ids_repetitions.get)
        secondary_tag_ratio = round(tag_ids_repetitions[secondary_tag] / total_packets, 2)

    print("primary_tag", primary_tag)
    print("secondary_tag", secondary_tag)

    primary_tag_rows = packets_df[packets_df['adv_address'] == primary_tag]
    rssi = 0
    if len(primary_tag_rows) > 0 and primary_tag != '':
        rssi = None if np.isnan(np.mean(primary_tag_rows['rssi'])) else round(np.mean(primary_tag_rows['rssi']), 2)
    secondary_rssi = 0
    if secondary_tag != '':
        secondary_tag_rows = packets_df[packets_df['adv_address'] == secondary_tag]
        if len(secondary_tag_rows) > 0:
            secondary_rssi = None if np.isnan(np.mean(secondary_tag_rows['rssi'])) else round(
                np.mean(secondary_tag_rows['rssi']), 2)

    return primary_tag, primary_tag_ratio, secondary_tag, secondary_tag_ratio, rssi, secondary_rssi


def sprinkler_harvesting(gw_obj, loops_limit=10, energy_pattern_val=20):
    """
    Setting GW to get duplicate packets, looking for 3 duplicates from the same tag,
        calculate minimum delta between packets
    gets:
        gw_obj:         Gateway object
        tag_adv:        tag advertising address to filter packets by
        loops_limit:    limit time to get packets data

    return:
        duplicates_delta_min:    time in msec
    """
    gw_obj.config_gw(filter_val=True, pacer_val=0, energy_pattern_val=energy_pattern_val, time_profile_val=[5, 15],
                     received_channel=37, beacons_backoff_val=0)  # filter_val=True allow to get duplicate packets

    gw_obj.reset_listener()
    # gw_obj.reset_buffer()
    # gw_obj.run_packets_listener_ng(tag_packets_only=False, do_process=True)

    packet_data = PacketList()

    search_duplicates = True

    while search_duplicates and loops_limit > 0:
        sleep(5)

        # gw_answer = gw_obj.get_data_ng(action_type=ActionType.ALL_SAMPLE, data_type=DataType.PROCESSED)
        gw_answer = gw_obj.get_packets(action_type=ActionType.ALL_SAMPLE, data_type=DataType.PACKET_CLASS)

        packet_data = packet_data + gw_answer

        if any([len(p) >= 3 for p in packet_data.packet_list]):
            search_duplicates = False
        else:
            loops_limit = loops_limit - 1

    # gw_obj.stop_processes()
    # print('stopped processes')
    # gw_obj.reset_buffer()
    # gw_obj.stop_continuous_listener()
    gw_obj.config_gw(time_profile_val=[0, 6])

    return packet_data


def sweep_range(attn_values, attn_obj, gw_obj, tag_handle, energy_pattern_val=20, num_of_packets=100):
    """
    Loop over attenuator values and gather packet_data_analysis and sprinkler_analysis functions data
    :type attn_values: range
    :param attn_values: List of attenuation to sweep by
    :type attn_obj: Attenuator object
    :param attn_obj: Attenuator object
    :type gw_obj: Gateway object
    :param gw_obj: Gateway object
    :type tag_handle: TagsHandling object (wiliot_testers.testers_utils)
    :param tag_handle: TagsHandling object
    :type energy_pattern_val: int
    :param energy_pattern_val: energy pattern to check
    :type num_of_packets: int
    :param num_of_packets: how many packets to count


    return:
        attn_dict:
            Dictionary,
                keys: attn_value
                values: List including the following:
                    number of packets
                    percentage of primary tag packets
                    percentage of secondary tag packets
                    rssi of primary tag packets
                    rssi of secondary tag packets
                    seconds to get @num_of_packets packets
                    primary sprinkler min time
                    secondary sprinkler min time

    """
    attn_dict = {}
    primary_duplicates_delta_min = None
    secondary_duplicates_delta_min = None
    for attn_power in attn_values:
        tag_handle.set_new_location()
        set_attn_status = set_attn_power(attn_obj, attn_power)
        if not simulation:
            print('ATTN is set to ', attn_obj.Getattn())
            if set_attn_status is not True:
                continue

        packet_data, total_loops = start_harvesting(gw_obj=gw_obj, num_of_packets=num_of_packets,
                                                    energy_pattern_val=energy_pattern_val)
        if packet_data.size() == 0:
            attn_dict[attn_power] = (0, 0, 0, 0, 0, 0, 0)
        else:
            (primary_tag_adv, primary_tag_dist, secondary_tag_adv, secondary_tag_dist, primary_avg_rssi,
             secondary_avg_rssi) = packet_data_analysis(packet_data)

        # rates = tag_handle.get_sprinkler_tbp(gw_obj, energy_pattern_val)

        sprinkler_packet_data = sprinkler_harvesting(gw_obj, loops_limit=20, energy_pattern_val=energy_pattern_val)
        if len(sprinkler_packet_data) > 0:
            primary_avg_rssi = sprinkler_packet_data.get_avg_rssi_by_tag(primary_tag_adv)
            primary_sprinkler_avg_tbp = sprinkler_packet_data.get_avg_tbp_by_tag(primary_tag_adv, reject_outliers=True)

            secondary_avg_rssi = sprinkler_packet_data.get_avg_rssi_by_tag(secondary_tag_adv)
            secondary_sprinkler_avg_tbp = sprinkler_packet_data.get_avg_tbp_by_tag(secondary_tag_adv,
                                                                                   reject_outliers=True)

            attn_dict[attn_power] = [len(packet_data),
                                     primary_tag_dist, secondary_tag_dist, primary_avg_rssi, secondary_avg_rssi,
                                     total_loops, primary_sprinkler_avg_tbp, secondary_sprinkler_avg_tbp]

            print(attn_dict)
            print('Waiting for brownout')
            sleep(5)
        else:
            attn_dict[attn_power] = (0, 0, 0, 0, 0, 0, 0)
    return attn_dict


def start_calibration(inlay_type='Single Band', num_of_packets=100, td_lower_limit=0, set_optimal_attn=True):
    """
    calibration process
    :type inlay_type: string
    :param inlay_type: will determine the energizing patterns we will use
    :type num_of_packets: int
    :param num_of_packets: default number of packets to analyze by
    :type td_lower_limit: double
    :param td_lower_limit: set sprinkler time delta to filter results by
    :type set_optimal_attn: Bool
    :param set_optimal_attn: A flag to decide if set attn to optimal value

    return:
        None
    """
    if inlay_type == 'Single Band':
        energy_pattern_values = [18]
    else:
        energy_pattern_values = [18, 51]

    attn_obj = None
    # create equipment objects
    if not simulation:
        try:
            attn_obj = Attenuator('API').GetActiveTE()
            current_attn = attn_obj.Getattn()
        except Exception as e:
            raise EquipmentError('Attenuator Error - Verify Attenuator connection')

    try:
        gw_obj = WiliotGateway(auto_connect=True, logger_name='root', verbose=False)
        # gw_obj.openPort(port='COM4', baud=921600)
        gw_obj.write('!set_tester_mode 1')
        gw_obj.start_continuous_listener()
        if not gw_obj.get_connection_status()[0]:
            raise EquipmentError('Gateway Error - Verify WiliotGateway connection')
    except Exception as e:
        raise EquipmentError('Gateway Error - Verify WiliotGateway connection')
        gw_obj.close_port()

    tag_handle = TagsHandling(tags_list_len=np.inf, rssi_threshold=100, add_to_black_list_after_locations=np.inf)

    for energy_pattern in energy_pattern_values:
        if fine_only:
            attn_values = range(15)
        else:
            print('Start sweep on coarse range:')
            attn_values = range(0, 11, 3)
            coarse_attn_dict = sweep_range(attn_values, attn_obj, gw_obj, tag_handle, energy_pattern_val=energy_pattern,
                                           num_of_packets=num_of_packets)

            print('Coarse data: {attn_dict}'.format(attn_dict=coarse_attn_dict))

            attn_dist = [value[0] for key, value in coarse_attn_dict.items()]

            top_values_keys = [list(coarse_attn_dict.keys())[i] for i in np.argsort(attn_dist)[-4:]]
            top_values_keys.remove(max(top_values_keys))

            attn_values = range(min(top_values_keys), max(top_values_keys) + 1, 1)

        print('Start sweep on fine range:')
        fine_attn_dict = sweep_range(attn_values, attn_obj, gw_obj, tag_handle, energy_pattern_val=energy_pattern,
                                     num_of_packets=num_of_packets)

        fine_attn_df = pd.DataFrame.from_dict(fine_attn_dict, orient='index')
        fine_attn_df.columns = ['num_of_packets', 'primary_tag_percentage', 'secondary_tag_percentage', 'primary_rssi',
                                'secondary_rssi', 'seconds_to_packets', 'primary_sprinkler_time',
                                'secondary_sprinkler_time']

        print('Final results for pattern: ', energy_pattern)
        if not fine_only:
            print('Coarse data: {attn_dict}'.format(attn_dict=coarse_attn_dict))
        print('Fine data: {attn_dict}'.format(attn_dict=fine_attn_dict))
    gw_obj.stop_continuous_listener()
    fine_attn_df = pd.DataFrame.from_dict(fine_attn_dict, orient='index')
    fine_attn_df.columns = ['num_of_packets', 'primary_tag_percentage', 'secondary_tag_percentage', 'primary_rssi',
                            'secondary_rssi', 'seconds_to_packets', 'primary_sprinkler_time',
                            'secondary_sprinkler_time']

    fine_attn_filtered_df = fine_attn_df[fine_attn_df['primary_sprinkler_time'] >= td_lower_limit]
    fine_attn_filtered_df = fine_attn_df.drop(fine_attn_df[fine_attn_df.primary_tag_percentage < 0.4].index)

    path = Path(os.path.dirname(__file__))
    fine_attn_filtered_df.to_csv('{parent_path}\\output.csv'.format(parent_path=path))

    try:
        fine_attn_filtered_df['primary_sprinkler_time_decending'] = fine_attn_filtered_df.apply(
            lambda row: -1 * row.primary_sprinkler_time, axis=1)
    except Exception as e:
        pass

    top_attn_by_chars = fine_attn_filtered_df.sort_values(
        ['primary_tag_percentage', 'primary_sprinkler_time_decending'], ascending=False)

    first_preference = top_attn_by_chars.iloc[0].name
    primary_rssi = top_attn_by_chars.loc[first_preference].primary_rssi

    print('Set ATTN to ', first_preference, 'dB for best performance')

    path = '{parent_path}\\config\\equipment_config.json'.format(parent_path=path.parent)

    key = "equipment"
    value = {'optimal_attenuation': int(first_preference), 'primary_rssi_mean': primary_rssi}
    update_json_field(path, key, value)

    if set_optimal_attn:
        set_attn_status = set_attn_power(attn_obj, first_preference)
    else:
        print('Setting ATTN to 0 dB')
        set_attn_status = set_attn_power(attn_obj, 0)


def set_calibration_attn(set_optimal_attn=True, config_path=None):
    """
    setting attn value
    :type set_optimal_attn: Bool
    :param set_optimal_attn: A flag to decide if set attn to optimal value
    :type config_path: string
    :param config_path: path to config file

    return:
        attenuation set to attenuator or None if set is failed
    """
    # create equipment objects
    try:
        attn_obj = Attenuator('API').GetActiveTE()
        current_attn = attn_obj.Getattn()
    except Exception as e:
        raise EquipmentError('Attenuator Error - Verify Attenuator connection')

    if config_path is None:
        parent_path = os.path.dirname(__file__)
        path = '{parent_path}\\config\\equipment_config.json'.format(parent_path=parent_path)
    else:
        path = config_path

    key = "equipment"
    optimal_attenuation_value = None
    if set_optimal_attn:
        try:
            with open(path, "r+") as jsonFile:
                config_data = json.load(jsonFile)
                optimal_attenuation_value = config_data.get(key).get('optimal_attenuation')
        except Exception as e:
            raise

    if set_optimal_attn and optimal_attenuation_value is not None:
        print('Setting ATTN to {value} dB'.format(value=optimal_attenuation_value))
        set_attn_status = set_attn_power(attn_obj, optimal_attenuation_value)
        if set_attn_status:
            return optimal_attenuation_value
    else:
        print('Setting ATTN to 0 dB')
        set_attn_status = set_attn_power(attn_obj, 0)
        if set_attn_status:
            return 0
    return None


# main
if __name__ == '__main__':
    start_calibration()
