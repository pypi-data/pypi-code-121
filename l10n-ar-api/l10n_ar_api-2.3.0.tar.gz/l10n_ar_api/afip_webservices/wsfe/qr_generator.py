import qrcode
import json
import base64


class QrGeneratorElectronicInvoice(object):

    def __init__(self, qr_value):
        self.qr_value = qr_value
        self.qr_img = 0
        self.reverse_color = False

    def generate_qr(self):
        msg_json = str.encode(json.dumps(self.qr_value))
        url = "https://www.afip.gob.ar/fe/qr/?p=%s" % (base64.b64encode(msg_json)).decode('utf-8')
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(url)
        qr.make(fit=True)
        if self.reverse_color:
            self.qr_img = qr.make_image(fill_color="white", back_color="black")
        else:
            self.qr_img = qr.make_image(fill_color="black", back_color="white")

    def get_qr_image(self):
        return self.qr_img
