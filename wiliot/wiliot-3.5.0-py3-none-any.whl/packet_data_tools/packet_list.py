import numpy as np
import pandas
import pandas as pd
import copy

from wiliot.packet_data_tools.packet import Packet


class PacketList(list):
    def __init__(self):
        self.packet_list = np.array([], dtype=Packet)  # ndarray - conatins packets
        self.raw_packet_map_list = {}  # dict - keys: raw_packet, values: index in self.packet_list

    def __add__(self, other_packet_list):
        """
        merge 2 PacketList object using '+' sign: packet_list1+packet_list2

        :type other_packet_list: PacketList
        :param other_packet_list:

        :return: merged packet_list, not mandatory
        """
        for packet in other_packet_list.packet_list:
            raw_packet = packet.get_packet()
            if raw_packet in self.raw_packet_map_list.keys():
                raw_packet_list_index = self.raw_packet_map_list[raw_packet]
                self.packet_list[raw_packet_list_index].append_to_sprinkler(packet)
            else:
                self.packet_list = np.append(self.packet_list, packet)
                raw_packet_list_index = self.packet_list.size - 1
                self.raw_packet_map_list[raw_packet] = raw_packet_list_index
            self.print_live_stream(packet)
        return self

    def __len__(self):
        """
        Total amount of packets
        """
        return self.get_num_packets()

    def __iter__(self):
        self.n = 0
        return iter(self.packet_list)

    def __next__(self):
        if self.n <= len(self):
            return self.packet_list[self.n]
        else:
            raise StopIteration

    def __getitem__(self, key):
        return self.packet_list[key]

    def __setitem__(self, key, packet: Packet):
        # raise ValueError("Set item is not supported yet by PacketList type")
        if isinstance(packet, Packet):
            old_packet = self.packet_list[key]
            del self.raw_packet_map_list[old_packet.get_packet_string(gw_data=False, process_packet=False)]
            self.raw_packet_map_list[packet.get_packet_string(gw_data=False, process_packet=False)] = key
            self.packet_list[key] = packet
        else:
            raise TypeError("Can only set Packet type to PacketList")

    def pop(self, index: int = 0):
        packet_list = self.copy()
        raw_packet = np.take(packet_list.packet_list, index).packet_data['raw_packet']
        packet_list.packet_list = np.delete(packet_list.packet_list, index)
        packet_list.raw_packet_map_list.pop(raw_packet, None)
        return packet_list

    def copy(self):
        return copy.deepcopy(self)

    def size(self):
        """
        Total amount of packets, sprinklers count individually
        """
        packet_list_size = 0
        for packet in self.packet_list:
            packet_list_size += len(packet)
        return packet_list_size

    def append(self, packet: Packet, ignore_sprinkler=False) -> None:
        """
        Adds single Packet to PacketList

        :type packet: Packet
        :param packet: packet to be added to packet_list
        :type ignore_sprinkler: Bool
        :param ignore_sprinkler: allow duplicates packets from different sprinkler

        :return: packet_list
        """
        if packet.is_valid_packet:
            raw_packet = packet.get_packet()
            if raw_packet not in self.raw_packet_map_list.keys():
                self.packet_list = np.append(self.packet_list, packet)
                raw_packet_list_index = self.packet_list.size - 1
                self.raw_packet_map_list[raw_packet] = raw_packet_list_index
            else:
                raw_packet_list_index = self.raw_packet_map_list[raw_packet]
                self.packet_list[raw_packet_list_index].append_to_sprinkler(packet)
            # self.packet_list = np.append(self.packet_list, packet)

            return self  # True
        else:
            return False

    def get_sprinkler(self, packet):
        """
        @param packet: a packet data type. Needs to be appended before using this function.
        @return: A packet sprinkler of this packet.
        """
        raw_packet = packet.get_packet()
        if raw_packet in self.raw_packet_map_list.keys():
            raw_packet_list_index = self.raw_packet_map_list[raw_packet]
            return self.packet_list[raw_packet_list_index]
        else:
            return None

    def dump(self, packet_dict_list: list):
        """
        gets list of raw_packet or packet_dict and fill packet_list with data

        :type packet_dict_list: list
        :param packet_dict_list: gw list (get_data), fill packet_list with data

        :return: bool status
        """
        if len(self) > 0:
            # packet_list not empty
            return False
        for packet_dict in packet_dict_list:
            packet = Packet(packet_dict)
            if packet.is_valid_packet:
                self.print_live_stream(packet)
                self.append(packet)
        return True

    def print_live_stream(self, packet):
        """
        for future use - implement output
        """
        # set parameters to filter view by
        pass

    def get_df(self, sprinkler_filter=False, return_sprinkler_df=False):
        """
        returns packet_list data as dataframe, BE CAREFULL WHEN CHANGING FUNCTIONALITY, this is a fundamental function
        :type sprinkler_filter: Bool
        :param sprinkler_filter: determine if to keep all occurrences of sprinkler per packet
        :type return_sprinkler_df: Bool
        :param return_sprinkler_df: adds 'sprinkler_counter','per','tbp' attributes to df
        :return: Dataframe
        """
        packet_df = pd.DataFrame()
        packet_id = 0
        for packet in self.packet_list:
            if sprinkler_filter is True or return_sprinkler_df is True:
                if sprinkler_filter is True:
                    packet_range = [len(packet) - 1]
                else:
                    if return_sprinkler_df is True:
                        packet_range = range(len(packet))
                tbp = packet.get_tbp()
                if tbp is None:
                    tbp = -1
                per = packet.get_per()
            else:
                packet_range = range(len(packet))

            for sprinkler_id in packet_range:
                sprinkler_df = packet.as_dataframe(sprinkler_id)
                try:
                    sprinkler_df.insert(loc=0, column='packet_id',
                                        value=packet_id)  # occourences of the same pakcet will get the same packet_id.
                    if sprinkler_filter is True or return_sprinkler_df is True:
                        sprinkler_df.insert(loc=0, column='sprinkler_counter', value=sprinkler_id + 1)
                        sprinkler_df.insert(loc=len(sprinkler_df.columns), column='tbp', value=tbp)
                        sprinkler_df.insert(loc=len(sprinkler_df.columns), column='per', value=per)
                    # print(sprinkler_df.values)
                except Exception as e:
                    print(e)
                # packet_df = packet_df.append(sprinkler_df, ignore_index=True)
                packet_df = pd.concat([packet_df, sprinkler_df])
            packet_id += 1
        return packet_df

    def packet_df_to_sprinkler_df(self, packet_df, sprinkler_filter=False):
        """
        gets packet_df and returns sprinkler df
        :type packet_df: DataFrame
        :param packet_df: df to convert

        :return: Dataframe - sprinkler_df
        """
        packet_list = self.import_packet_df(packet_df=packet_df)
        sprinkler_df = packet_list.get_df(return_sprinkler_df=True, sprinkler_filter=sprinkler_filter)

        return sprinkler_df

    def sort_df_by(self, column='stat_param'):
        """
        returns dataframe sorted by column
        :type column: str
        :param column: the column to filter by

        :return: Dataframe
        """
        packet_df = self.get_df()
        packet_df_sorted = packet_df.sort_values(column)
        return packet_df_sorted

    def filter_packet_by(self, packet_data_key='adv_address', values=''):
        """
        filter packet_list by adv_address
        :type values: str or list of strings
        :param values: adv_address to search

        :return: filtered PacketList
        """
        packet_list = PacketList()
        for index, packet in enumerate(self.packet_list):
            if isinstance(values, list):
                if packet.packet_data[packet_data_key] in values:
                    packet_list.append(self.packet_list[index])
            else:
                if packet.packet_data[packet_data_key] == values:
                    packet_list.append(self.packet_list[index])
        return packet_list

    def filter_df_by(self, column='adv_address', values='', values_range=[]):
        """
        filter dataframe by value or (exclusive) by value range
        :type column: str
        :param column: column to filter by
        :type values: str or list of strings
        :param values: value to search
        :type values_range: 2 elements list of int
        :param values_range: range to find

        :return: filtered Dataframe
        """
        packet_df = self.get_df()
        if values_range:
            start = values_range[0]
            end = values_range[1]
            packet_df_filtered = packet_df.loc[(packet_df[column] > start) & (packet_df[column] <= end)]
        else:
            if isinstance(values, list):
                packet_df_filtered = packet_df.loc[packet_df[column].isin(values)]
            else:
                packet_df_filtered = packet_df.loc[packet_df[column] == values]
        return packet_df_filtered

    def get_avg_rssi_by_tag(self, adv_address=''):
        """
        return tag average rssi (4 decimal points accuracy)
        :type adv_address: str
        :param adv_address: adv_address of wanted tag

        :return: average rssi for tag
        """
        filtered_df = self.filter_df_by(values=adv_address)
        if filtered_df.empty:
            return None
        avg_rssi = round(filtered_df['rssi'].mean(), 4)
        return avg_rssi

    def get_avg_tbp_by_tag(self, adv_address='', reject_outliers=False):
        """
        return tag average tbp (4 decimal points accuracy)
        :type adv_address: str
        :param adv_address: adv_address of wanted tag

        :return: average tbp for tag
        """

        def reject_outliers(data, m=2):
            return data[abs(data - np.mean(data)) < m * np.std(data)]

        tbp_list = np.array([])
        filtered_packets = self.filter_packet_by(values=adv_address)
        for packet in filtered_packets.packet_list:
            packet_tbp = packet.get_tbp()
            if packet_tbp is not None:
                tbp_list = np.append(tbp_list, packet_tbp)
        if len(tbp_list) == 0:
            return None
        avg_tbp = round(tbp_list.mean(), 4)
        if reject_outliers:
            avg_tbp = round(reject_outliers(tbp_list).mean(), 4)
        return avg_tbp

    def to_csv(self, path):
        """
        export entire PacketList to csv

        :type path: str
        :param path: path to save csv

        :return: bool - export status
        """

        return self.export_packet_df(packet_df=self.get_df(), path=path)

    def export_packet_df(self, packet_df, path):
        """
        export given dataframe to csv

        :type packet_df: Dataframe
        :param packet_df: filtered dataframe to save as csv
        :type path: str
        :param path: path to save csv

        :return: bool - export status
        """
        try:
            # this call of 'to_csv' is a generic pandas function
            packet_df.to_csv(path, index=False)
            return True
        except Exception as e:
            return False

    def import_packet_df(self, path=None, packet_df=None):
        """
        import from a csv of dataframe
        :type path: str
        :param path: the message or part of the message that needed to be read
        :type packet_df: DataFrame
        :param packet_df: gets get_df dataframe (packet_df only)

        :return: PacketList
        """
        import_packet_list = PacketList()
        if path is not None:
            import_packets_df = pd.read_csv(path)
        else:
            import_packets_df = packet_df
        for packet_id in import_packets_df['packet_id'].unique():
            packet_df = import_packets_df.loc[import_packets_df['packet_id'] == packet_id]
            for index, row in packet_df.iterrows():
                raw_packet = row['raw_packet']
                gw_data = row['gw_packet']
                time_from_start = row['time_from_start']
                reconstructed_packet = raw_packet + gw_data
                p = Packet(reconstructed_packet, time_from_start)
                #TODO: we should add custom data here as well - or remove the support of it..
                import_packet_list.append(p)

        return import_packet_list

    def get_statistics(self):
        """
        Calculates statistics of self.
        @return dictionary with predefined statistics of the packetList.
        """
        return self.get_df_statistics(packet_df=self.get_df())

    def get_group_statistics(self, group_by_col='adv_address'):
        """
        Calculates statistics of self, grouped by some value.
        @return dictionary of items at the group, Dictionary values are dictionaries of statistics.
        """
        packet_df = self.get_df()
        # if not defines - get all values:

        groups_id_list = packet_df[group_by_col].unique()

        group_statistics = {}
        for group_id in groups_id_list:
            packet_df_filtered = packet_df.loc[packet_df[group_by_col] == group_id]
            group_statistics[group_id] = self.get_df_statistics(packet_df=packet_df_filtered)
            group_statistics[group_id][group_by_col] = group_id
        return group_statistics

    def group_by(self, group_by_col='adv_address'):
        """
        Calculates statistics of self, grouped by some value.
        @return dictionary of items at the group, Dictionary values are dictionaries of statistics.
        """
        packet_df = self.get_df(sprinkler_filter=True)
        # if not defines - get all values:

        groups_id_list = packet_df[group_by_col].unique()

        group = {}
        for group_id in groups_id_list:
            group[group_id] = self.filter_packet_by(group_by_col, group_id)
            # group[group_id][group_by_col] = group_id
        return group

    def get_num_packets(self):
        if len(self.packet_list) == 0:
            return 0
        else:
            packet_df = self.get_df(sprinkler_filter=False)
            return packet_df.shape[0]

    def get_df_statistics(self, packet_df=None):
        """
        Calculates statistics from packetList DF.
        @param packet_df - dataframe generated by packetList
        @return dictionary with predefined statistics of the packetList.
        """
        statistics = {}
        if packet_df.shape[0] == 0:
            statistics['num_packets'] = 0
            statistics['num_cycles'] = 0
            return statistics

        # sprinkler_df = self.get_df(sprinkler_filter=True)
        if packet_df is None:
            packet_df = self.get_df(sprinkler_filter=False)

        sprinkler_df = self.packet_df_to_sprinkler_df(packet_df, sprinkler_filter=True)

        statistics['num_packets'] = packet_df.shape[0]
        statistics['num_cycles'] = sprinkler_df.shape[0]

        sprinkler_counter_arr = pandas.to_numeric(sprinkler_df['sprinkler_counter'], errors='coerce')
        statistics['sprinkler_counter_mean'] = np.mean(sprinkler_counter_arr)
        statistics['sprinkler_counter_std'] = np.std(sprinkler_counter_arr)
        statistics['sprinkler_counter_min'] = np.min(sprinkler_counter_arr)
        statistics['sprinkler_counter_max'] = np.max(sprinkler_counter_arr)

        tbp_arr = pandas.to_numeric(sprinkler_df.loc[sprinkler_df['tbp'] > 0]['tbp'], errors='coerce')
        if len(tbp_arr) == 0:
            tbp_arr = [-1]
        statistics['tbp_mean'] = np.mean(tbp_arr)
        statistics['tbp_std'] = np.std(tbp_arr)
        statistics['tbp_min'] = np.min(tbp_arr)
        statistics['tbp_max'] = np.max(tbp_arr)
        statistics['tbp_num_vals'] = np.size(tbp_arr)

        per_arr = pandas.to_numeric(sprinkler_df['per'], errors='coerce')
        statistics['per_mean'] = np.mean(per_arr)
        statistics['per_std'] = np.std(per_arr)

        rssi_arr = pandas.to_numeric(packet_df['rssi'], errors='coerce')
        statistics['rssi_mean'] = np.mean(rssi_arr)
        statistics['rssi_std'] = np.std(rssi_arr)
        statistics['rssi_min'] = np.min(rssi_arr)
        statistics['rssi_max'] = np.max(rssi_arr)

        time_arr = pandas.to_numeric(packet_df['time_from_start'], errors='coerce')
        # statistics['start_time'] = np.min(time_arr)
        statistics['ttfp'] = np.min(time_arr)
        statistics['end_time'] = np.max(time_arr)
        statistics['duration'] = statistics['end_time'] - statistics['ttfp']
        if statistics['duration'] > 0:
            statistics['rx_rate_normalized'] = statistics['num_packets'] / statistics['duration']
            statistics['rx_rate'] = statistics['num_packets'] / statistics['end_time']
        else:
            statistics['rx_rate'] = 0
            statistics['rx_rate_normalized'] = 0
        return statistics


if __name__ == '__main__':
    from test_packet_list import p_list

    packet_list1 = PacketList()
    packet_list2 = PacketList()
    packet_list1.dump(p_list[:17])
    packet_list2.dump(p_list[7:])
    packet_list2[0] = packet_list1[0]

    packet_list3 = packet_list1 + packet_list2

    packet_df = packet_list1.sort_df_by()
    tag1 = packet_list1.filter_packet_by(values='0472AFC00316')
    tag1 = tag1.pop()
    packet_df = packet_list1.get_df(sprinkler_filter=False)

    # packet_df = packet_list1.filter_df_by(column='rssi', values_range=[76, 77])
    #
    # packet_list1.export_packet_df(packet_df,'C:\\Users\\ohad\\eclipse-workspace\\pywiliot_internal\\wiliot\\packet_data_tools\\packet_df2.csv')
    # #
    # a = packet_list1.import_packet_df(
    #     packet_df=packet_df)  # path='C:\\Users\\ohad\\eclipse-workspace\\pywiliot_internal\\wiliot\\packet_data_tools\\packet_df2.csv')

    q = packet_list1.packet_df_to_sprinkler_df(packet_df)
    pass
