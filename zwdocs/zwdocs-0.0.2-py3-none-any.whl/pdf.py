import re
import uuid
import shutil
import subprocess
import traceback
import fitz
from loguru import logger
from pathlib import Path
from bs4 import BeautifulSoup
from zwutils.dlso import upsert_config
from zwutils.fileutils import writefile, readfile, rmfile
from zwutils.sysutils import iswin
from .utils import rmexblank

class Pdf(object):
    def __init__(self, pth, cfg=None, **kwargs):
        cfgdef = {
            'zoom': (4.16666, 4.16666),
            'tmpdir': 'tmp',
            'pdf2htmlex_path': 'bin/pdf2htmlex/pdf2htmlex.bat' if iswin() else 'bin/pdf2htmlex/pdf2htmlex.sh',
            'pdf2htmlex_timeout': 300,
            'pdf2htmlex_mergeline': True,
            'debug': False,
        }
        self.cfg = upsert_config({}, cfgdef, cfg, kwargs)
        self.pth = Path(pth)
        self.pdf2htmlex_path = self.cfg.pdf2htmlex_path
        self.tmpdir = Path(self.cfg.tmpdir)

    def pdf2txt(self, outpth=None, exclude_re=None):
        pth = self.pth
        outs = []
        with fitz.open(pth) as doc:
            toc = doc.get_toc()
            for page in doc.pages():
                if exclude_re and re.search(exclude_re, page.getText()):
                    continue
                s = self.page2txt(page=page)
                outs.append(s)
        if outpth:
            writefile(outpth, '\n'.join(outs))
        return outs

    def page2txt(self, pno=None, page=None):
        rtn = None
        if pno is not None:
            with fitz.open(self.pth) as doc:
                page = doc[pno]
                rtn = page.getText('text')
        elif page:
            rtn = page.getText('text')
        else:
            raise Exception('Neither page num nor page object has been given!')
        return rtn

    def pdf2png(self, outdir=None, zoom=None, alpha=False):
        pth = self.pth
        outs = []
        with fitz.open(pth) as doc:
            for page in doc.pages():
                s = self.page2png(outpath=outdir/(f'{pth.stem}_{page.number}.png'), page=page, zoom=zoom, alpha=alpha)
                outs.append(s)
        return outs

    def page2png(self, pno=None, page=None, outpath=None, zoom=None, alpha=False):
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=96
        cfg = self.cfg
        zoom = zoom or cfg.zoom
        rotate = int(0)
        zoom_x = zoom[0]
        zoom_y = zoom[1]
        mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
        if pno is not None:
            with fitz.open(self.pth) as doc:
                page = doc[pno]
                pix = page.getPixmap(matrix=mat, alpha=alpha)
        elif page:
            pix = page.getPixmap(matrix=mat, alpha=alpha)
        else:
            raise Exception('Neither page num nor page object has been given!')

        if outpath:
            Path(outpath).parent.mkdir(parents=True, exist_ok=True)
            pix.writeImage(outpath)
        rtn = {
            'pgnum' : page.number,
            'width' : pix.width,
            'height': pix.height,
            'image' : pix.getPNGData(),
        }
        return rtn

    def pdf2html(self, outpath=None, exclude_re=None):
        pth = self.pth
        pages = []
        htmlstr = ''
        with fitz.open(pth) as doc:
            for page in doc:
                if exclude_re:
                    m = re.search(exclude_re, page.getText())
                    if m:
                        continue
                html = self.page2html(page=page, pageid='page_%i' % len(pages))
                pages.append(html)
        htmlstr = ''.join(pages)
        if outpath:
            writefile(outpath, htmlstr)
        return htmlstr

    def page2html(self, pno=None, page=None, outpath=None, pageid=None):
        html = None
        if pno is not None:
            with fitz.open(self.pth) as doc:
                page = doc[pno]
                html = fix_html_font(page.getText('xhtml'))
        else:
            html = fix_html_font(page.getText('xhtml'))

        soup = BeautifulSoup(html, 'html.parser')
        ps = soup.find_all('p')
        for p in ps:
            spans = p.find_all('span')
            if len(spans)<2:
                continue
            spantxt = ''
            spancls = spans[0]['style']
            for span in spans:
                spantxt += span.text
                span.decompose()
            markup = '<span style="%s">%s</span>' % (spancls, spantxt)
            new_span = BeautifulSoup(markup, features='html.parser')
            p.append(new_span)
        if pageid:
            soup.div['id'] = pageid
        html = str(soup)
        if outpath:
            # outpath = outpath or str(self.pth.parent/self.pth.stem)
            # outpath = '%s-%i.html' % (outpath, page.number)
            writefile(outpath, html)
        return html

    def pdf2htmlex(self, outpath=None, exclude_re=None):
        pth = self.pth
        htmlstr = None
        uid = uuid.uuid4()
        # pdf2htmlex have file name bug in win when file name is long, so make a short name copy(tmppdf)
        tmppdf = self.tmpdir if self.tmpdir else pth.parent
        tmpout = self.tmpdir if self.tmpdir else pth.parent
        tmppdf = tmppdf / ( '%s.pdf' % uid )
        tmpout = tmpout / ( '%s.html' % uid )
        tmppdf.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(pth), str(tmppdf))

        if iswin():
            # use exe rather than docker if in win
            # https://soft.rubypdf.com/software/pdf2htmlex-windows-version
            cmd = self.pdf2htmlex_path
            cmdstr = '"{}" "{}" "{}"'.format(cmd, tmppdf.resolve(), tmpout.parent.resolve())
        else:
            # use docker in linux and mac:
            # docker_volume = docker_volume.replace(':', '')
            # docker_volume = docker_volume.replace('\\', '/')
            # docker_volume = '/c' + docker_volume[1:]
            cmd = self.pdf2htmlex_path
            docker_volume = str(tmppdf.parent.resolve())
            cmdstr = '{} {} "{}"'.format(cmd, docker_volume, tmppdf.name)

        logger.info(f'pdf2htmlex cmdstr: {cmdstr}')
        try:
            p = subprocess.run(cmdstr, shell=True, timeout=self.cfg.pdf2htmlex_timeout)
            if p.returncode == 0:
                htmlstr = readfile(tmpout)
                soup = BeautifulSoup(htmlstr, 'html.parser')
                pgctn = soup.find(id='page-container')
                pages = [o for o in pgctn.children if o.name and o.name == 'div']

                if exclude_re:
                    for pg in pages:
                        if re.search(exclude_re, pg.text):
                            pg.decompose()

                # merge mutli tags into one span
                if self.cfg.pdf2htmlex_mergeline:
                    for pg in pages:
                        lines = pg.select('div.t')
                        for line in lines:
                            new_tag = soup.new_tag('span')
                            new_tag.string = rmexblank(line.text)
                            line.clear()
                            line.insert(0, new_tag)

                htmlstr = soup.decode_contents()
                if outpath:
                    htmlpath = Path(outpath)
                    htmlpath.parent.mkdir(parents=True, exist_ok=True)
                    writefile(htmlpath, htmlstr)
                    logger.info('Write html to %s' % outpath)

        except subprocess.TimeoutExpired:
            logger.error('pdf2htmlex process pdf: %s timeout!' % pth)
        except Exception:
            logger.error('pdf2htmlex ex: %s'%traceback.format_exc())
        finally:
            rmfile(tmppdf)
            rmfile(tmpout)
        return htmlstr

def fix_html_font(htmlstr):
    otext = htmlstr                               # original html text string
    pos1 = 0                                      # search start poition
    font_serif = "font-family:Times"              # enter ...
    font_sans  = "font-family:Helvetica"          # ... your choices ...
    font_mono  = "font-family:Courier"            # ... here

    while True:
        pos0 = otext.find("font-family:", pos1)   # start of a font spec
        if pos0 < 0:                              # none found - we are done
            break
        pos1 = otext.find(";", pos0)              # end of font spec
        test = otext[pos0 : pos1]                 # complete font spec string
        testn = ""                                # the new font spec string
        if test.endswith(",serif"):               # font with serifs?
            testn = font_serif                    # use Times instead
        elif test.endswith(",sans-serif"):        # sans serifs font?
            testn = font_sans                     # use Helvetica
        elif test.endswith(",monospace"):         # monospaced font?
            testn = font_mono                     # becomes Courier

        if testn != "":                           # any of the above found?
            otext = otext.replace(test, testn)    # change the source
            pos1 = 0                              # start over
    return otext