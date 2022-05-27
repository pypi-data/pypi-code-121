import os
try:
    from aip import AipOcr
except:
    import time
    os.system("pip install baidu-aip==2.2.18.0")
    time.sleep(2)
    from aip import AipOcr


OCR_APP_ID = os.environ.get("OCR_APP_ID")
OCR_APP_KEY = os.environ.get("OCR_APP_KEY")
OCR_APP_SECRET = os.environ.get("OCR_APP_SECRET")


client = AipOcr(OCR_APP_ID, OCR_APP_KEY, OCR_APP_SECRET)


def ocr(file_bin, accurate: bool = False):
    """OCR识别图片
    :param file_bin: bytes, 文件二进制内容
    :param accurate: bool, 高精度版
    """
    if OCR_APP_ID and OCR_APP_KEY and OCR_APP_SECRET:
        # 通用文字识别（高精度版）
        if accurate:
            data = client.basicAccurate(file_bin)
        # 通用文字识别
        else:
            data = client.basicGeneral(file_bin)
        return data
    else:
        raise ValueError(f"参数没有赋值：OCR_APP_ID，OCR_APP_KEY，OCR_APP_SECRET")
