from translate import Translator
import qrcode
import string
import random

from service.tools.weather_service import weather_spider
from utils.tools.weather import WEATHER_CITY_CODE_DIC


def transtools(to_lang, content):
    # specifying the language
    translator = Translator(to_lang)
    # typing the message
    translation = translator.translate(content)
    # print the translated message
    print(translation)


def qrcodetools(url):
    # Creating object
    # version: defines size of image from integer(1 to 40), box_size = size of each box in pixels, border = thickness of the border.
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    # add_date :  pass the input text
    qr.add_data(url)
    # converting into image
    qr.make(fit=True)
    # specify the foreground and background color for the img
    img = qr.make_image(fill='black', back_color='white')
    # store the image
    img.save('qrcode_img.png')


def passwordtools(len=8):
    """
    @Author & Date  : CoderWanFeng 2022/5/9 11:54
    @Desc  : 随机密码生成器，默认是8位
    @Return  ：
    """
    chars = string.digits + string.ascii_letters
    return ''.join(random.sample(chars * 10, len))


def weather():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7'
    }
    while (True):
        try:
            cityName = input('请输入城市名称(按q/Q键退出)：')
            if cityName == 'q' or cityName == 'Q':
                break
            cityCode = WEATHER_CITY_CODE_DIC[cityName]  # 得到城市代码
            url = 'http://www.weather.com.cn/weather1d/%d.shtml' % cityCode  # 得到城市天气网址
            weather_spider(url, headers)
        except:
            print('未查到%s城市，请重新输入：' % cityName)


