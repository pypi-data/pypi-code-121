import requests

class download:
    def dl(self,url):
        data = {'url':url, 'extension':'mp3'}
        BG = requests.post(f"https://onlinevideoconverter.pro/api/convert?url={url}", data=data).json()
        return BG

    class instagram:
       def story(self,username):
        headers = {
               'accept': '*/*',
    'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
    'cookie': 'PHPSESSID=3a695tfplvr6b2dd9k08js1gv8; lang=en; _ga=GA1.2.1463466898.1650441389; _gid=GA1.2.1956429257.1650441389; __gads=ID=54266b5d6ddd11f8-22381e227bcd0007:T=1650441390:RT=1650441390:S=ALNI_Mb9iEXPRGiKpWxsdOrnjofRvrKZCg; _gat_gtag_UA_65465319_3=1',
    'referer': 'https://instabig.net/stories/' + username,
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        }
        BG = requests.get(f"https://instabig.net/s/story?u={username}", headers=headers).json()
        return BG

