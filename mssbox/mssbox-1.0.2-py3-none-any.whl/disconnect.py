import requests
import xml.etree.ElementTree as ET
from util.getters import get_connected_sim


def disconnect_sim(mssb_ip, mssb_serial, slot_terminal):
    """
    This method disconnects any SIM attached to the specified terminal/slot
    :param slot_terminal: MSSB terminal ID port assigned to the slot
    :return: returns whether the operation succeeded or not
    :rtype: bool
    """
    if get_connected_sim(mssb_ip, mssb_serial, int(slot_terminal)).get('id') == "":
        return True
    response = requests.get(f"http://{mssb_ip}/rest.php?command=disconnect&sim=0&terminal={str(slot_terminal)}&mssbSerial={mssb_serial}")
    response_xml = ET.fromstring(response.content)
    sim_success_value = response_xml.find('params').find("success").text
    return sim_success_value == "1" and get_connected_sim(int(slot_terminal)).get('id') == ""
