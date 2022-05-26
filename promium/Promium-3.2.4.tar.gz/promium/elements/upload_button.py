
from promium.elements.input_field import InputField


class UploadButton(InputField):

    def upload_file(self, file_path):
        """Uploads file by file path"""
        self.send_keys(file_path)
