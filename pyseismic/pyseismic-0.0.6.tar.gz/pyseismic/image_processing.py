from PIL import Image
import io
import numpy as np
import os
try:
    import fitz
except ModuleNotFoundError:
    print('WARNING: Module "fitz" not found, cannot use "pic2pdf".\n'
          'For further information, visit https://pypi.org/project/PyMuPDF/.')


def cut_img(img, loc=[0, 0], show_info=False):
    w, h = img.size
    img = np.array(img)
    cut_color = img[loc[0], loc[1]]
    top, bottom, left, right = 0, h, 0, w
    for ih in range(h):
        if not (cut_color == img[ih]).all():
            top = ih
            break
    for ih in range(h):
        if not (cut_color == img[h - ih - 1]).all():
            bottom = h - ih
            break
    for iw in range(w):
        if not (cut_color == img[top:bottom, iw]).all():
            left = iw
            break
    for iw in range(w):
        if not (cut_color == img[top:bottom, w - iw - 1]).all():
            right = w - iw
            break
    if show_info:
        print(f'WxH: {w}x{h} -> {right-left}x{bottom-top}')
    return Image.fromarray(img[top:bottom, left:right])


def savefig(fig, fname, **kwargs):
    dpi = kwargs['dpi'] if 'dpi' in kwargs.keys() else 96
    buffer = io.BytesIO()
    fig.savefig(buffer, format=fname.split('.')[-1], **kwargs)
    buffer.seek(0)
    image = Image.open(buffer)
    if 'tif' in fname.split('.')[-1]:
        cut_img(image).save(fname, dpi=(dpi, dpi), compression='tiff_lzw')
    else:
        cut_img(image).save(fname, dpi=(dpi, dpi))


def figure_cutter(figure_ID_old, figure_ID_new=None, **kwargs):
    if not figure_ID_new:
        figure_ID_new = figure_ID_old
    img = Image.open(figure_ID_old)
    try:
        dpi = img.info['dpi'][0]
    except:
        print('Can’t get dpi, set dpi=96')
        dpi = 96
    if 'tif' in figure_ID_new.split('.')[-1]:
        cut_img(img, **kwargs).save(figure_ID_new, dpi=(dpi, dpi), compression='tiff_lzw')
    else:
        cut_img(img, **kwargs).save(figure_ID_new, dpi=(dpi, dpi))


def pic2pdf(img_path, pdf_path=None, pdf_name=None):
    img_name = os.path.basename(img_path).split('.')[0]
    if not pdf_name:
        pdf_name = img_name
    if not pdf_path:
        pdf_path = os.path.join(os.path.dirname(img_path), pdf_name)
    doc = fitz.open()
    imgdoc = fitz.open(img_path)
    # 使用图片创建单页的PDF
    pdfbytes = imgdoc.convertToPDF()
    imgpdf = fitz.open('pdf', pdfbytes)
    # 将当前页写入文档
    doc.insertPDF(imgpdf)
    doc.save(pdf_path)
    doc.close()


def changedpi(infile, outfile=None, dpi=300):
    if not outfile:
        outfile = infile
    im = Image.open(infile)
    if 'tif' in outfile.split('.')[-1]:
        im.save(outfile, dpi=(dpi, dpi), compression='tiff_lzw')
    else:
        im.save(outfile, dpi=(dpi, dpi))


def list_processing(func, fn_old_dir, fn_new_dir=None, format='tif', **kwargs):
    if not fn_new_dir:
        fn_new_dir = fn_old_dir
    else:
        os.makedirs(fn_new_dir, exist_ok=True)
    for fn in os.listdir(fn_old_dir):
        func(os.path.join(fn_old_dir, fn), os.path.join(fn_new_dir, f'{fn.split(".")[0]}.{format}'), **kwargs)


if __name__ == '__main__':
    figure_cutter('t1.tif', 't2.tif')
    list_processing(pic2pdf, 'img', format='pdf')
