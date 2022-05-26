import requests
import xml.etree.ElementTree as ET
from util.getters import get_connected_sim, get_sims_info


def connect_sim(mssb_ip, mssb_serial, 
                repos_dir, mssb_file_dir, 
                sim_plmn, slot_terminal, 
                sims_config=None, sim_imsi=None):
    """
    This method connects the desired SIM having that PLMN to the provided slot/terminal
    :param repos_dir: Your repository directory
    :param mssb_file_dir: The directory with the mssb file
    :param sim_plmn: PLMN of the desired SIM Card
    :param slot_terminal: slot_terminal: MSSB terminal ID port assigned to the slot
    :param sims_config: dict containing the sims_config
    :param sim_imsi: IMSI for the specific SIM Card to be connected
    :return: returns whether the operation succeeded or not
    :rtype: bool
    """
    if sims_config:
        sims = sims_config
    else:
        sims = get_sims_info(repos_dir, mssb_serial, mssb_file_dir)
    sim_mssb = 0
    for i in range(0, len(sims)):
        if sim_plmn == sims[i].get('DEV_CUSTOM_2'):
            if sim_imsi:
                if sim_imsi == sims[i].get('DEV_CUSTOM_1'):
                    sim_mssb = sims[i].get('ID')
            else:
                sim_mssb = sims[i].get('ID')
            break
    response = requests.get('http://' + mssb_ip + '/rest.php?'
                                                     'command=connect'
                                                     '&sim='+str(sim_mssb)+
                                                     '&terminal='+str(slot_terminal)+
                                                     '&mssbSerial=' + mssb_serial)
    response_xml = ET.fromstring(response.content)
    sim_success_value = response_xml.find('params').find("success").text
    connected = get_connected_sim(mssb_ip, mssb_serial, int(slot_terminal)).get('custom_2') == sim_plmn
    return sim_success_value == "1" and connected
