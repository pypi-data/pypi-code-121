import requests
import xml.etree.ElementTree as ET 


def reset_all_connections(mssb_ip, mssb_serial):  # PAY ATTENTION! THIS METHOD IMPACTS ALL DEVICES CONNECTED TO THE MSSB
    """
    This method disconnects all SIMs connected to any terminals
    :return: returns the result of the request, 'true' or 'false
    :rtype: bool
    """
    response = requests.get(f"http://{mssb_ip}/rest.php?command=resetall&mssbSerial={mssb_serial}")
    response_xml = ET.fromstring(response.content)
    success_value = response_xml.find('params').find("success").text
    return bool(success_value)
