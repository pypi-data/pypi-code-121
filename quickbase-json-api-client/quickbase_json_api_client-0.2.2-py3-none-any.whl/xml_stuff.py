import base64
import io
from xml.dom import minidom

import requests
from typing.io import BinaryIO

from quickbase_json import QBClient


def xml_upload(client, tbid, rid: int, fid: int, file: any, filename: str):

    # check file type
    if not (isinstance(file, BinaryIO) and isinstance(file, io.BytesIO) and isinstance(file, io.BufferedReader)):
        raise TypeError(f'File must be of type: BinaryIO or BytesIO')

    headers = {
        'Content-Type': 'application/xml',
        'QUICKBASE-ACTION': 'API_UploadFile'
    }

    # convert file
    file = base64.b64encode(file.read()).decode()

    # begin building of XML
    root = minidom.Document()
    xml = root.createElement('qbdapi')
    root.appendChild(xml)

    # user token
    user_token = root.createElement('usertoken')
    user_token_value = root.createTextNode(client.auth)
    user_token.appendChild(user_token_value)
    xml.appendChild(user_token)

    # rid
    rid_node = root.createElement('rid')
    rid_value = root.createTextNode(str(rid))
    rid_node.appendChild(rid_value)
    xml.appendChild(rid_node)

    # field
    fid_node = root.createElement('field')
    fid_node.setAttribute('fid', str(fid))
    fid_node.setAttribute('filename', str(fid))
    fid_value = root.createTextNode(file)
    fid_node.appendChild(fid_value)
    xml.appendChild(fid_node)

    xml_str = root.toprettyxml(indent="\t")

    r = requests.post(url=f'https://synctivate.quickbase.com/db/{tbid}', headers=headers, data=xml)

    print(r)
    print(r.text)


qbc = QBClient(realm='synctivate', auth='b57mr6_nyiv_0_bthisgscp758escy56j8pdvx6smi')
xml_upload(qbc, 'bqs5cbduv', rid=118, fid=25, file=open('287.jpeg', 'rb'), filename='upload.jpeg')
