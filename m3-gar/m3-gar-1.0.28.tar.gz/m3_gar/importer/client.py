import requests


class FIASClient:
    """Клиент к серверу ФИАС"""
    fias_source = 'https://fias.nalog.ru/WebServices/Public/'

    def get_all_download_file_info(self):
        result = requests.get(
            f'{self.fias_source}GetAllDownloadFileInfo',
        ).json()

        return result


client = FIASClient()
