import requests
import json
import xml.etree.ElementTree as ET


def get_connected_sim(mssb_ip, mssb_serial, slot_terminal):
    """
    This method returns the SIM Card allocated to the provided slot
    :param slot_terminal: int MSSB terminal port assigned to the slot
    :return: returns a dict with SIM attribs (id, name, custom_1 (IMSI), custom_2 (PLMN)
    """
    sim = get_all_connected_sims(mssb_ip, mssb_serial).get(int(slot_terminal))
    return sim


def get_all_connected_sims(mssb_ip, mssb_serial):
    """
    This method returns all SIMs connected to terminals
    :return: A dict with all SIMs with their attribs (id, name, custom_1 (IMSI), custom_2 (PLMN)
    """
    response = requests.get(f"http://{mssb_ip}/rest.php?command=listcon&mssbSerial={mssb_serial}")                                                 
    response_xml = ET.fromstring(response.content)
    connections = response_xml.find('connections').findall("terminal")
    sims = dict()
    for i in range(0, len(connections)):
        sims[i] = connections[i].find("sim")
    return sims


def get_sims_info(repos_dir, mssb_serial, mssb_file_dir):
    """
    This function gets the info for the SIMs connected to the MSSB via file exported from MSSB
    :param repos_dir: Your repository directory
    :param mssb_serial: Serial for the MSSB
    :param mssb_file_dir: The directory with the mssb file
    :return: dict with the SIMs Config
    """
    file = f"{repos_dir}/{mssb_serial}_sims.json"
    mssb_file = f"{mssb_file_dir}/{mssb_serial}_sims.json"
    with open(file, 'wb') as f:
        f.write(mssb_file.content)
    with open(file) as json_file:
        data = json.load(json_file)
    return data

    