import numpy as np
import pandas
import pandas as pd
import copy

from wiliot.packet_data_tools.packet import Packet
from wiliot.packet_data_tools.packet_list import PacketList


class MultiTag(dict):
    def __init__(self):
        self.tags = {}  # key is adv_address, value is Packet_list

    def __len__(self):
        """
        Amount of tags
        """
        return len(self.tags)

    def __add__(self, other_multi_tag):
        """
        merge 2 MultiTag object using '+' sign: multi_tag1+multi_tag2

        :type other_multi_tag: MultiTag
        :param other_multi_tag:

        :return: merged other_multi_tag, not mandatory
        """
        for adv_address in other_multi_tag.keys():
            if adv_address not in self.tags.keys():
                self.tags[adv_address] = other_multi_tag[adv_address].copy()
            else:
                self.tags[adv_address] = self.tags[adv_address] + other_multi_tag[adv_address]
        return self

    def copy(self):
        return copy.deepcopy(self)

    def append(self, packet: Packet, ignore_sprinkler=False) -> None:
        """
        Adds single Packet to MultiTag

        :type packet: Packet
        :param packet: packet to be added to packet_list
        :type ignore_sprinkler: Bool
        :param ignore_sprinkler: allow duplicates packets from different sprinkler

        :return: None
        """
        adv_address = packet.packet_data['adv_address']
        if adv_address not in self.tags.keys():
            self.tags[adv_address] = PacketList().copy()

        self.tags[adv_address].append(packet, ignore_sprinkler)

    def dump(self, packet_dict_list: list):
        """
        gets list of raw_packet or packet_dict and fill packet_list with data

        :type packet_dict_list: list
        :param packet_dict_list: gw list (get_data), fill packet_list with data

        :return: bool status
        """
        try:
            for packet_dict in packet_dict_list:
                packet = Packet(packet_dict)
                if packet.is_valid_packet:
                    self.print_live_stream(packet)
                    self.append(packet)
            return True
        except:
            return False

    def print_live_stream(self, packet):
        """
        for future use - implement output
        """
        # set parameters to filter view by
        pass

    def get_statistics_by_adv(self, adv_address):
        """
        Calculates statistics of self.
        @return dictionary with predefined statistics of the packetList.
        """
        return self.tags[adv_address].get_statistics()

    def to_csv(self,path):
        statistics_df = self.get_statistics()
        statistics_df.to_csv(path)

    def get_statistics(self):
        statistics_df = pd.DataFrame()
        for adv_address in self.tags.keys():
            adv_statistics = self.get_statistics_by_adv(adv_address)
            adv_statistics['adv_address'] = adv_address
            adv_statistics_df = pd.DataFrame(adv_statistics, index=[0])
            statistics_df = pd.concat([statistics_df, adv_statistics_df], axis=0)
        return statistics_df

    def get_statistics_list(self, attributes=['adv_address', 'num_cycles', 'num_packets', 'tbp_mean', 'rssi_mean']):
        statistics_df = self.get_statistics()
        statistics_list = []
        specific_statistics_df = statistics_df[attributes]

        for index, row in specific_statistics_df.iterrows():
            dict = {}
            for att in attributes:
                dict[att] = row[att]
            statistics_list.append(dict.copy())

        return statistics_list


if __name__ == '__main__':
    from test_packet_list import p_list

    packet_list1 = PacketList()
    # packet_list2 = PacketList()
    packet_list1.dump(p_list)
    #
    # packet_list3 = packet_list1 + packet_list2

    mt = MultiTag()
    for packet in packet_list1.packet_list[:7]:
        mt.append(packet)

    mt2 = MultiTag()
    mt2.dump(p_list)

    m3 = mt + mt2
    a = m3.get_statistics_list()
    pass
