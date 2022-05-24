import zipfile


class BaseZIP(object):

    @classmethod
    def get_zip_file(cls, filepath):
        azip = zipfile.ZipFile(filepath)
        return azip

    @classmethod
    def get_zip_namelist(cls, zip_obj):
        """
        返回zip的文件列表，包括深层次目录
        :return: list
        """
        zip_list = zip_obj.namelist()
        result_list = []
        for zip_file in zip_list:
            try:
                zip_file = zip_file.encode('cp437').decode('gbk')
            except:
                zip_file = zip_file.encode('utf-8').decode('utf-8')
            result_list.append(zip_file)
        return result_list

    @classmethod
    def get_zipname(cls,zipobj):
        """

        :param zipobj:
        :return: zip文件位置
        """
        return zipobj.filename

    @classmethod
    def get_info(cls,zipobj,filepath):
        """
        获取文件的基本信息，注意，不是所有格式的文件都能获取信息
        zipobj.getinfo(filepath)后可以获取以下信息
                # 原来文件大小
        print(azip_info.file_size)
        # 压缩后大小
        print(azip_info.compress_size)

        # 这样可以求得压缩率，保留小数点后两位
        print('压缩率为{:.2f}'.format(azip_info.file_size/azip_info.compress_size))
        :param zipobj:
        :param filepath: 为压缩文件下的相对目录 比如 test/test1/第二次目录/2021因工作被隔离明细表_采集组.xlsx
        :return:
        """
        return zipobj.getinfo(filepath)


# zipobj = BaseZIP.get_zip_file(r'C:\Users\xuzhu\Desktop\VIPPatents_20210514To20210518.rar')
# print(BaseZIP.get_zip_namelist(zipobj))
#
