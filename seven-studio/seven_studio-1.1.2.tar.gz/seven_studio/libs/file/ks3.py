# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-04-29 10:02:31
:LastEditTime: 2020-12-10 10:59:20
:LastEditors: ChenXiaolei
:Description: 金山云存储
"""
import base64
from enum import Enum
from seven_framework.log import  *
from seven_framework.uuid import *
from seven_framework.file import KS3Helper

from seven_studio.utils.random import *

from seven_studio.models.seven_model import InvokeResult
from seven_studio.models.seven_model import FileUploadInfo


class HostEnum(Enum):
    """
    :description: 服务地址
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    # 中国（北京）
    BeiJing = "ks3-cn-beijing.ksyun.com"
    # 中国（上海）
    ShangHai = "ks3-cn-shanghai.ksyun.com"
    # 中国（香港）
    XiangGang = "ks3-cn-hk-1.ksyun.com"


class PolicyEnum(Enum):
    """
    :description: 策略
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    PublicReadWrite = "public-read-write"
    PublicRead = "public-read"
    Private = "private"


class StorageClassEnum(Enum):
    """
    :description: 存储方式
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    # 标准存储
    STANDARD = "STANDARD"
    # 低频存储
    STANDARD_IA = "STANDARD_IA"


class KS3:
    """
    :description: 
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    logger_error = Logger.get_logger_by_name("log_error")
    logger_info = Logger.get_logger_by_name("log_info")

    @classmethod
    def upload(self, storage_config, file_name='', stream=None, file_path=''):
        """
        :description: 文件上传
        :param storage_config：配置内容
        :param file_name：文件名(按路径上传时此参数为空)
        :param stream：文件内容(按路径上传时此参数为空)
        :param file_path：文件路径(为空按stream上传，不为空则按路径上传)
        :return: InvokeResult
        :last_editors: HuangJingCan
        """
        # ks3 = KS3Helper("AKLT89aOKN-3TSKCO_3wajfFBw", "OE1s4w3nEq4tXSMd0WilcWhf4JgcxIYnA5XAvY24jQUXdj48ARYNs/oP5XNQtHc9hw==", "ks3-cn-beijing.ksyun.com")
        # ks3.put_file_from_file_path("gao7ts", "IMG_8726.HEIC", "/Users/chenxiaolei/Downloads/IMG_8726.HEIC")

        invoke_result = InvokeResult()
        file_upload_info = FileUploadInfo()
        file_upload_config = json.loads(storage_config)

        access_key = file_upload_config.get("AccessKey", "")
        secret_key = file_upload_config.get("SecretKey", "")
        bucket = file_upload_config.get("Bucket", "")
        end_point = file_upload_config.get("EndPoint", "")
        domain = file_upload_config.get("Domain", "").rstrip('/')
        is_autofile_name = file_upload_config.get("IsAutoFileName", 0)
        folder = file_upload_config.get("Folder", "").strip('/')
        folder = folder + "/" if folder != "" else folder

        # 返回文件名
        file_name = os.path.basename(file_path) if file_path != "" else file_name

        if is_autofile_name == 1:
            file_extension = os.path.splitext(file_name)[1]
            file_name = UUIDHelper.get_uuid().replace("-", "") + file_extension

        try:
            # conn = Connection(access_key, secret_key, end_point, is_secure=False, domain_mode=False)
            # b = conn.get_bucket(bucket).new_key(folder + file_name)
            conn = KS3Helper(access_key, secret_key, end_point)
            key_name = folder + file_name
            result = False
            if file_path != "":
                # ret = b.set_contents_from_filename(file_path, policy=PolicyEnum.PublicRead.value)
                result = conn.put_file_from_file_path(bucket, key_name, file_path, PolicyEnum.PublicRead.value)
            else:
                # ret = b.set_contents_from_string(stream, policy=PolicyEnum.PublicRead.value)
                result = conn.put_file_from_contents(bucket, key_name, stream, PolicyEnum.PublicRead.value)

            if result:
                virtual_name = RandomUtil.get_random_switch_string(domain).rstrip('/')
                file_upload_info.ResourcePath = virtual_name + "/" + key_name
                invoke_result.Data = file_upload_info.__dict__
        except Exception as ex:
            self.logger_error.exception(ex)
            invoke_result.ResultCode = "1"
            invoke_result.ResultMessage = "KS3上传文件出错"

        return invoke_result

    @classmethod
    def delete(self, storage_config, file_path):
        """
        :description: 删除文件
        :param storage_config：配置内容
        :param file_path：文件路径
        :return:
        :last_editors: HuangJingCan
        """

        if file_path=="":
            return 1
        file_upload_config = json.loads(storage_config)

        access_key = file_upload_config.get("AccessKey", "")
        secret_key = file_upload_config.get("SecretKey", "")
        bucket = file_upload_config.get("Bucket", "")
        end_point = file_upload_config.get("EndPoint", "")
        folder = file_upload_config.get("Folder", "").strip('/')
        folder = folder + "/" if folder != "" else folder

        # 返回文件名
        file_name = os.path.basename(file_path) if file_path != "" else ""

        result = 0

        try:
            # conn = Connection(access_key, secret_key, end_point, is_secure=False, domain_mode=False)
            # b = conn.get_bucket(bucket)
            # b.delete_key(folder + file_name)
            conn = KS3Helper(access_key, secret_key, end_point)
            conn.del_file(bucket, folder + file_name)
            result = 1
        except Exception as ex:
            self.logger_error.exception(ex)

        return result

    @classmethod
    def get(self, storage_config, file_path):
        """
        :description: 获取文件
        :param storage_config：配置内容
        :param file_path：文件路径或者文件名
        :return: 文件流
        :last_editors: HuangJingCan
        """
        invoke_result = InvokeResult()
        file_upload_config = json.loads(storage_config)

        access_key = file_upload_config.get("AccessKey", "")
        secret_key = file_upload_config.get("SecretKey", "")
        bucket = file_upload_config.get("Bucket", "")
        end_point = file_upload_config.get("EndPoint", "")
        folder = file_upload_config.get("Folder", "").strip('/')
        folder = folder + "/" if folder != "" else folder

        # 返回文件名
        file_name = os.path.basename(file_path) if file_path != "" else ""

        result = ""

        try:
            # conn = Connection(access_key, secret_key, end_point, is_secure=False, domain_mode=False)
            # b = conn.get_bucket(bucket)
            # k = b.get_key(folder + file_name)
            # if k:
            #     result = k.get_contents_as_string()
            conn = KS3Helper(access_key, secret_key, end_point)
            result = conn.get_file_contents(bucket, folder + file_name)
        except Exception as ex:
            self.logger_error.exception(ex)

        return result

    @classmethod
    def get_list(self, storage_config, prefix=""):
        """
        :description: 列举Bucket内的文件或者目录
        :param storage_config：配置内容
        :param file_path：文件路径
        :param prefix：指定前缀
        :return: 文件列表，目录列表
        :last_editors: HuangJingCan
        """
        invoke_result = InvokeResult()
        file_upload_config = json.loads(storage_config)

        access_key = file_upload_config.get("AccessKey", "")
        secret_key = file_upload_config.get("SecretKey", "")
        bucket = file_upload_config.get("Bucket", "")
        end_point = file_upload_config.get("EndPoint", "")
        folder = file_upload_config.get("Folder", "").strip('/')
        folder = folder + "/" if folder != "" else folder

        result_list = []
        result_dir = []

        try:
            conn = KS3Helper(access_key, secret_key, end_point)
            result_list, result_dir = conn.get_bucket_objects(bucket, prefix)
        except Exception as ex:
            self.logger_error.exception(ex)

        return result_list, result_dir

    @classmethod
    def upload_part(self, storage_config, source_path):
        """
        :description: 分块上传-单线程
        :param storage_config：配置内容
        :param source_path：文件路径
        :param prefix：指定前缀
        :return: 文件列表，目录列表
        :last_editors: HuangJingCan
        """
        invoke_result = InvokeResult()
        file_upload_info = FileUploadInfo()
        file_upload_config = json.loads(storage_config)

        access_key = file_upload_config.get("AccessKey", "")
        secret_key = file_upload_config.get("SecretKey", "")
        bucket = file_upload_config.get("Bucket", "")
        end_point = file_upload_config.get("EndPoint", "")
        domain = file_upload_config.get("Domain", "").rstrip('/')
        is_autofile_name = file_upload_config.get("IsAutoFileName", 0)
        folder = file_upload_config.get("Folder", "").strip('/')
        folder = folder + "/" if folder != "" else folder

        file_name = ""
        # 返回文件名
        file_name = os.path.basename(source_path) if source_path != "" else file_name

        if is_autofile_name == 1:
            file_extension = os.path.splitext(file_name)[1]
            file_name = UUIDHelper.get_uuid().replace("-", "") + file_extension

        try:
            conn = KS3Helper(access_key, secret_key, end_point)
            conn.multi_put_file(bucket, folder + file_name, source_path)

            virtual_name = RandomUtil.get_random_switch_string(domain).rstrip('/')
            file_upload_info.ResourcePath = virtual_name + "/" + folder + file_name
            invoke_result.Data = file_upload_info.__dict__

        except Exception as ex:
            self.logger_error.exception(ex)
            invoke_result.ResultCode = "1"
            invoke_result.ResultMessage = "KS3上传文件出错"

        return invoke_result

    @classmethod
    def water_marker_text(self, img_url, text, font="", fontsize="", fill="", dissolve="", gravity="", dx="", dy="", q=""):
        """
        :description: 文字水印
        :param img_url：文件路径
        :param text：必填；水印文字(base64EncodeText,经过URL安全的Base64编码)
        :param font：文字水印字体(base64EncodeFont，经过URL安全的Base64编码)。默认为黑体
        :param fontsize：字体大小(整形)，单位为缇(1缇=1/20磅),默认值500
        :param fill：文字水印颜色(base64EncodeFill,经过URL安全的Base64编码)，可以是RGB格式，也可以是颜色名称(例如 black),还可以是十六进制(例如 ## FF0000),可以参考RGB对照表
        :param dissolve：不透明度。取值范围为1~100，默认值为100。100为完全不透明。
        :param gravity：水印位置。可参考下面的水印锚点参数表，默认为SouthEast(右下方)。
                        NorthWest	North	NorthEast
                        West	    Center	East
                        SouthWest	South	SouthEast
        :param dx：横轴(x轴)边距，单位为像素(px),默认值为10
        :param dy：纵轴(y轴)边距，单位为像素(px),默认值为10
        :param q：决定 jpg 图片的相对quality,对原图压缩。范围为0-100 , 0表示高压缩低质量，100表示低压缩，高质量。默认90
        :return: 图片地址
        :last_editors: HuangJingCan
        """
        text = base64.b64encode(text.encode("utf-8")).decode('utf-8')
        if font != "":
            font = base64.b64encode(font.encode("utf-8")).decode('utf-8')
            font = f"&font={font}"
        if fontsize != "": fontsize = f"&fontsize={fontsize}"
        if fill != "": fill = f"&fill={fill}"
        if dissolve != "": dissolve = f"&dissolve={dissolve}"
        if gravity != "": gravity = f"&gravity={gravity}"
        if dx != "": dx = f"&dx={dx}"
        if dy != "": dy = f"&dy={dy}"
        if q != "": q = f"&q={q}"

        return f"{img_url}@base@tag=imgWaterMarker&type=2&text={text}{font}{fontsize}{fill}{dissolve}{gravity}{dx}{dy}{q}"

    @classmethod
    def water_marker_img(self, img_url, image, wtw="", wth="", dissolve="", gravity="", dx="", dy="", q=""):
        """
        :description: 图片水印
        :param img_url：文件路径
        :param image：必填；水印源图片网址(base64EncodeImageURI,经过URL安全的Base64编码),必须保证此网址返回一张图片
        :param wtw：水印添加宽度阈值，小于该值将不进行图片水印操作，单位为像素(px)。范围为0以上的整数
        :param wth：水印添加高度阈值，小于该值将不进行图片水印操作，单位为像素(px)。范围为0以上的整数
        :param dissolve：不透明度。取值范围为1~100，默认值为100。100为完全不透明。
        :param gravity：水印位置。可参考下面的水印锚点参数表，默认为SouthEast(右下方)。
                        NorthWest	North	NorthEast
                        West	    Center	East
                        SouthWest	South	SouthEast
        :param dx：横轴(x轴)边距，单位为像素(px),默认值为10
        :param dy：纵轴(y轴)边距，单位为像素(px),默认值为10
        :param q：决定 jpg 图片的相对quality,对原图压缩。范围为0-100 , 0表示高压缩低质量，100表示低压缩，高质量。默认90
        :return: 图片地址
        :last_editors: HuangJingCan
        """
        image = base64.b64encode(image.encode("utf-8")).decode('utf-8')
        if wtw != "": wtw = f"&wtw={wtw}"
        if wth != "": wth = f"&wth={wth}"
        if dissolve != "": dissolve = f"&dissolve={dissolve}"
        if gravity != "": gravity = f"&gravity={gravity}"
        if dx != "": dx = f"&dx={dx}"
        if dy != "": dy = f"&dy={dy}"
        if q != "": q = f"&q={q}"

        return f"{img_url}@base@tag=imgWaterMarker&type=1&image={image}{wtw}{wth}{dissolve}{gravity}{dx}{dy}{q}"

    @classmethod
    def img_scale(self, img_url, w="", h="", m="", p="", so="", q="", F="", r="", c="", f="", s="", cox="", coy="", rotate="", et="", etw="", eth="", etc=""):
        """
        :description: 图片处理（缩放/裁剪/旋转/格式转换）
        :param img_url：图片地址
        :param m：<mode>缩略模式，0-长边优先缩放，缩放按照较长边的缩放比例进行缩放，不剪裁，1-短边优先缩放，缩放按照较短边的缩放比例进行缩放，不剪裁，2-限定缩略图的宽最少为<width>，高最少为<height>，进行等比缩放
        :param w：<width>缩略宽度/裁剪宽度，w/h必须有一个；取值范围：1-4096；指定目标缩略图的宽度,单位:像素(px)。 当单独使用时,代表按照宽度等比缩放。
        :param h：<height>缩略高度/裁剪高度，w/h必须有一个；取值范围：1-4096；指定目标缩略图的高度,单位:像素(px)。 当单独使用时,代表按照高度等比缩放。
        :param p：<p>图片按比例缩放;倍数百分比。取值范围：1-1000;小于 100，即是缩小，大于 100 即是放大，放大时p值取值范围如下：图片小于等于1MB时，最大支持放大到10倍；图片大于1MB且小于2MB，最大支持放大5倍，图片大于2MB，最大支持放大3倍图片长边像素值*倍数最大支持5000
        :param so: <so>图片放大；指定为放大模式；值为1时开启图片放大
        :param q: <quality>决定 jpg 图片的相对quality,对原图压缩，范围为0-100 , 0表示高压缩低质量,100表示低压缩，高质量。默认q=75。
        :param F: <format>指定目标缩略图的输出格式，默认按照原图格式输出。输出格式支持JPG、JPEG、PNG、GIF、WBMP、BMP、WEBP。
        :param r: <auto-orient>有些相机拍的照片会出现旋转,本参数就是否根据原图 EXIF 信息自动适应方向，默认值r=0 r=0:按原图默认处理 r = 1:按原图 EXIF 信息自动旋转图片 r = 2:自定义旋转角度，旋转角度由<rotate> 参数指定
        :param c: <cut>是否裁剪,默认值是:0(否)对缩放后超出范围的图片内容进行剪裁,这种情况一般发生在按照短边优先的等比缩放中。缩放会以图片中线为中心,进行上下/左右的 裁剪,得到相应的尺寸
        :param f: <fixed>是否固定宽高,默认值f=0(否)f=1:以图片中线为中心,裁剪指定w和h的区域,此参数与参数 cut 配合使用,当使用 f 时会固定图片的宽高,进行非缩放裁剪
        :param s: <strip>是否支持去除元数据。默认值1，0表示否，1表示是
        :param cox: <x-coordinate>裁剪起始横坐标，此参数与参数cut及参数fixed配合使用，当不设置裁剪起始横坐标时则默认居中裁剪
        :param coy: <y-coordinate>裁剪起始纵坐标，此参数与参数cut及参数fixed配合使用，当不设置裁剪起始纵坐标时则默认居中裁剪
        :param rotate: <degree>旋转角度,取值范围1-360,缺省为不旋转。自定义旋转角度需指定参数<r>等于2
        :param et: <extent>是否增加背景，默认值是0（否）。对缩放后空白范围的图片内容进行背景填充。
        :param etw: <extent width>指定背景宽度，单位：像素（px），默认值是原图最大宽度（若eth与etw均没有设置，则默认取原图高度和宽度的最大值，构成正方形；若只设置etw，则高度默认为原图高度）。取值范围：1-4096
        :param eth: <extent height>指定背景高度，单位：像素（px），默认值是原图最大高度（若eth与etw均没有设置，则默认取原图高度和宽度的最大值，构成正方形；若只设置eth，则宽度默认为原图宽度）。取值范围：1-4096
        :param etc: <extent colour>指定背景颜色，支持RRGGBB格式，默认值是FFFFFF（透明色为“transparent”，透明背景色支持图片格式为PNG、GIF）。
        :return: 图片地址
        :last_editors: HuangJingCan
        """
        if w != "": w = f"&w={w}"
        if h != "": h = f"&h={h}"
        if m != "": m = f"&m={m}"
        if p != "": p = f"&p={p}"
        if so != "": so = f"&so={so}"
        if q != "": q = f"&q={q}"
        if F != "": F = f"&F={F}"
        if r != "": r = f"&r={r}"
        if c != "": c = f"&c={c}"
        if f != "": f = f"&f={f}"
        if s != "": s = f"&s={s}"
        if cox != "": cox = f"&cox={cox}"
        if coy != "": coy = f"&coy={coy}"
        if rotate != "": rotate = f"&rotate={rotate}"
        if et != "": et = f"&et={et}"
        if etw != "": etw = f"&etw={etw}"
        if eth != "": eth = f"&eth={eth}"
        if etc != "": etc = f"&etc={etc}"

        return f"{img_url}@base@tag=imgScale{w}{h}{m}{p}{so}{q}{F}{r}{c}{f}{s}{cox}{coy}{rotate}{et}{etw}{eth}{etc}"