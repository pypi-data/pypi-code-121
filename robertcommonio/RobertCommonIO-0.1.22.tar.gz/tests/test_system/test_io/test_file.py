from robertcommonio.system.io.file import FileType, FileConfig, FileAccessor
from robertcommonbasic.basic.dt.utils import parse_time
import re
import pyzipper
import pandas as pd
from io import BytesIO

def test_csv():
    accessor = FileAccessor(FileConfig(PATH='E:/test.csv', MODE=FileType.CSV))
    accessor.save('ss')

def test_zip_csv():
    accessor = FileAccessor(FileConfig(PATH=r'E:\DTU\real\testdtu\20210526\databackup_202105261430.zip', PSW='RNB.beop-2019', MODE=FileType.AES_ZIP))
    results = accessor.read()
    for k, v in results.items():
        time = re.sub(r'[^0-9]+', '', k.strip())
        content = v.decode()
        body = {parse_time(time).strftime('%Y-%m-%d %H:%M:%S'): content}
        pp = [p.split(',') for p in content.split(';')]
        print()

def test_zip_csv1():
    content = b''
    with open(r'E:\DTU\real\atlanta\20210907\his_20210907095301.zip', 'rb') as f:
        content = f.read()

    accessor = FileAccessor(FileConfig(PATH=BytesIO(content), PSW=['aa', '123456', 'RNB.beop-2019', ''],
                                       MODE=FileType.AES_ZIP))
    results = accessor.read()
    for k, v in results.items():
        print(k)
    results = {}
    with pyzipper.AESZipFile(BytesIO(content)) as zip:
        zip.setpassword('RNB.beop-2019'.encode('utf-8'))
        for file in zip.namelist():
            results[file] = zip.read(file)
    print(results)


def test_excel():
    #import pandas as pd
    #df = pd.read_excel(r'E:\DTU\point\hongqiao_api\point202202221.xls', sheet_name=None)

    accessor = FileAccessor(FileConfig(PATH=r'E:\DTU\point\hongqiao_api\point20220224.xls', MODE=FileType.Excel, NAME=None))
    results = accessor.read()
    for k, v in results.items():
        print(k)
    del accessor

    accessor1 = FileAccessor(FileConfig(PATH=r'E:\DTU\point\hongqiao_api\point20220224_new.xls', MODE=FileType.Excel, NAME=None))
    accessor1.save(file_content=results)
    print()

def test_pcc():
    records = pd.read_csv('E:/PCC_AB_Davis_AirHandlers_Analog (3).csv', keep_default_na=False)
    for index, row in records.iterrows():
        row_value = row.to_dict()
        values = {}
        for k, v in row_value.items():
            if v is not None and len(str(v)) > 0:
                if isinstance(v, str) and v.find(',') > 0:
                    v = v.replace(',', '')
                print(v)

test_pcc()