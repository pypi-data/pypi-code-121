# -*- coding: utf-8 -*-
# @Author	: starview.brotherbaby
# @Date		: 2020-09-08 22:58:27 
# @Last Modified by:   starview.brotherbaby
# @Last Modified time: 2020-09-08 22:58:27
# Thanks for your comments!

import io

import qrcode

from . import base64_encode


def qr_data_to_img_base64_data(qr_code, 
    version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4):
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction,
        box_size=box_size,
        border=border
    )
    qr.add_data(qr_code)
    qr.make(fit=True)
    img = qr.make_image()
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    qr_data = base64_encode(img_buffer.getvalue())
    qr_img_data = 'data:image/png;base64,' + qr_data
    return qr_img_data

def img_to_base64_data(img_path, format='PNG'):
    with open(img_path,"rb") as f:
        img_data = base64_encode(f.read())
        return 'data:image/png;base64,' + img_data
    return ''
