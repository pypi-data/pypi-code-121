import io
import magic
import oss2
import requests
from PIL import Image
def img_cut(content,exceed_size,down_height=None,height=None):
    """
    content:需要处理的img的二进制
    exceed_size:当图片尺寸大于该尺寸进行裁剪
    down_height:从底部开始裁剪
    height:从上边开始裁剪
    """
    kind = magic.from_buffer(content, mime=True).split('/')[-1]
    img = Image.open(io.BytesIO(content))
    x_max = img.size[0]
    y_max = img.size[1]
    img_bytes = io.BytesIO()
    if int(y_max) > exceed_size:
        if down_height:
            img_bytes = io.BytesIO()
            cropped = img.crop((0, 0, x_max, y_max-down_height))  # (left, upper, right, lower)
            cropped.save(img_bytes, format=kind)
            # 从字节流管道中获取二进制
            image_bytes = img_bytes.getvalue()
            return image_bytes
        if height:
            cropped = img.crop((0, 0, x_max,height))  # (left, upper, right, lower)
            cropped.save(img_bytes, format=kind)
            # 从字节流管道中获取二进制
            image_bytes = img_bytes.getvalue()
            return image_bytes

def img_to_pdf(content_s):
    """
    content_s:需要处理的img图片的二进制,list类型
    """
    imgs = []
    for content in content_s:
        img = Image.open(io.BytesIO(content))
        # PNG格式转换成的四通道转成RGB的三通道
        img = img.convert("RGB")
        imgs.append(img)
    pdf_bytes = io.BytesIO()
    img0 = imgs[0]
    imgs = imgs[1:]
    img0.save(pdf_bytes,"PDF", resolution=100.0, save_all=True, append_images=imgs)
    return pdf_bytes.getvalue()



