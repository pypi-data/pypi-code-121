# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['picopt',
 'picopt.handlers',
 'picopt.pillow',
 'tests',
 'tests.integration',
 'tests.unit']

package_data = \
{'': ['*'],
 'tests': ['test_files/containers/*',
           'test_files/images/*',
           'test_files/invalid/*']}

install_requires = \
['Pillow>=9.0,<10.0',
 'confuse>=1.7.0,<2.0.0',
 'humanize>=4.0.0,<5.0.0',
 'python-dateutil>=2.8,<3.0',
 'rarfile>=4.0,<5.0',
 'ruamel.yaml>=0.17.16,<0.18.0',
 'termcolor>=1.1.0,<2.0.0',
 'treestamps>=0.3.1,<0.4.0']

entry_points = \
{'console_scripts': ['picopt = picopt.cli:main']}

setup_kwargs = {
    'name': 'picopt',
    'version': '3.2.0',
    'description': 'A multi format lossless image optimizer that uses external tools',
    'long_description': '# picopt\n\nA multi-format, recursive, multiprocessor aware, command line lossless image optimizer utility that uses external tools to do the optimizing.\n\nPicopt depends on Python [PIL](http://www.pythonware.com/products/pil/) to identify files and Python [rarfile](https://pypi.python.org/pypi/rarfile) to open CBRs.\n\nPicopt will optionally drop hidden timestamps at the root of your image directories to avoid reoptimizing images picopt has already optimized.\n\nThe actual image optimization is best accomplished by external programs.\n\n## <a name="philosophy">Conversion Philosophy</a>\n\n### Lossy Images\n\nJPEG & Lossy WebP images are likely the best and most practical lossy image formats. Converting lossy images rarely makes sense and so picopt only optimizes them in their current format.\n\n### Lossless Images\n\nLossless WebP images are smaller than PNG, much smaller than GIF and, of course, a great deal smaller thein uncompressed bitmaps like BMP. As such the best practice is probably to convert all lossless images to WebP Lossless as now all major browsers support it. The only downside is that decoding WebP Lossless takes on average 50% more CPU than PNG.\n\n### Sequenced Images\n\nSequenced Images, like animated GIFs and WebP, most of the time, should be converted to a compressed video format like HEVC or VP9. There are several situations where this is impractical and so Animated WebP is now a good substitute.\n\n### Conversion\n\nBy default picopt does not convert images between formats. You must turn on conversion to PNG or WebP explicitly.\n\n## <a name="formats">Formats</a>\n\n- By default picopt will optimize GIF, JPEG, PNG and WEBP images.\n- Picopt can optionally optimize ZIP, ePub, and CBZ containers.\n- Picopt can be told to convert lossless images such as BPM, PPM, GIF, TIFF into PNG, and all of the mentioned lossless formats into WebP.\n- Picopt can convert Animated GIFs into Animated WebP files.\n- Picopt can convert Animated PNGs (APNG) into Animated WebP files, but does not optimize APNG as APNG.\n- Picopt can convert RAR files into Zipfiles and CBR files into CBZ files.\n\n## <a name="programs">External Programs</a>\n\nPicopt will perform some minor optimization on most formats natively without using external programs, but this is not very good compared to the optimizations external programs can provide.\n\n### JPEG\n\nTo optimize JPEG images. Picopt needs one of [mozjpeg](https://github.com/mozilla/mozjpeg) or [jpegtran](http://jpegclub.org/jpegtran/) on the path. in order of preference.\n\n### PNG\n\nTo optimize PNG images or convert other lossless formats to PNG picopt requires either [optipng](http://optipng.sourceforge.net/) or [pngout](http://advsys.net/ken/utils.htm) be on the path. Optipng provides the most advantage, but best results will be had by using pngout as well.\n\n### Animated GIF\n\nAnimated GIFs are optimized with [gifsicle](http://www.lcdf.org/gifsicle/) if it is available.\n\n### WebP\n\nWebP lossless & lossy formats are optimized with [cwebp](https://developers.google.com/speed/webp/docs/cwebp).\n\n### EPub\n\nEPub Books are zip files that often contain images and picopt unpacks and repacks this format natively. Images within the epub are handled by other programs. EPub optimization is not turned on by default.\nEPub contents are never converted to other formats because it would break internal references to them.\n\n### CBZ & CBR\n\nPicopt uncompresses, optimizes and rezips [comic book archive files](https://en.wikipedia.org/wiki/Comic_book_archive). Be aware that CBR rar archives may only be rezipped into CBZs instead of CBR. Comic book archive optimization is not turned on by default to prevent surprises.\n\n## <a name="install">Install</a>\n\n### System Dependencies\n\npicopt requires several external system dependencies to run. We must install these first\n\n#### macOS\n\n    brew install webp mozjpeg optipng jonof/kenutils/pngout gifsicle\n\nln -s $(brew --prefix)/opt/mozjpeg/bin/jpegtran /usr/local/bin/mozjpeg\n\nUnfortunately hombrew\'s `webp` formula does not yet install the gif2webp tool that picopt uses for converting animated gifs to animated webps.\nYou may manually download it and put it in your path at [Google\'s WebP developer website](https://developers.google.com/speed/webp/download)\n\n#### Debian / Ubuntu\n\n    apt-get install optipng gifsicle python-imaging webp\n\nif you don\'t want to install mozjpeg using the instructions below then use jpegtran:\n\n    apt-get install libjpeg-progs\n\n#### Redhat / Fedora\n\n    yum install optipng gifsicle python-imaging libwebp-tools\n\nif you don\'t want to install mozjpeg using the instructions below then use jpegtran:\n\n    yum install libjpeg-progs\n\n#### MozJPEG\n\nmozjpeg offers better compression than libjpeg-progs jpegtran. It may or\nmay not be packaged for your \\*nix, but even when it is, picopt requires that its separately compiled version of jpegtran be symlinked to \'mozjpeg\' somewhere in the path.\n\nInstructions for installing on macOS are given above.\nSome near recent binaries for Windows and Debian x86 [can be found here](https://mozjpeg.codelove.de/binaries.html).\nMost Linux distributions still require a more manual install as elucidated here on [Casey Hoffer\'s blog](https://www.caseyhofford.com/2019/05/01/improved-image-compression-install-mozjpeg-on-ubuntu-server/)\n\n#### pngout\n\npngout is a useful compression to use after optipng. It is not packaged for linux, but you may find the latest binary version [on JonoF\'s site](http://www.jonof.id.au/kenutils). Picopt looks for the binary to be called `pngout`\n\n### Picopt python package\n\n    pip install picopt\n\n## <a name="usage">Usage Examples</a>\n\nOptimize all JPEG files in a directory:\n\n    picopt *.jpg\n\nOptimize all files and recurse directories:\n\n    picopt -r *\n\nOptimize files, recurse directories, also optimize ePub & CBZ containers, convert lossless images into WEBP, convert CBR into CBZ.\n\n    picopt -rx EPUB,CBR,CBZ -c WEBP,CBZ *\n\nOptimize files and recurse directories AND optimize comic book archives:\n\n    picopt -rx CBZ *\n\nOptimize comic directory recursively. Convert CBRs to CBZ. Convert lossless images, including TIFF, to lossless WEBP. Do not follow symlinks. Set timestamps.\n\n    picopt -rStc CBZ,WEBP -x TIFF,CBR,CBZ /Volumes/Media/Comics\n\nOptimize all files, but only JPEG format files:\n\n    picopt -f JPEG *\n\nOptimize files and containers, but not JPEGS:\n\n    picopt -f GIF,PNG,WEBP,ZIP,CBZ,EPUB *\n\nOptimize files, but not animated gifs:\n\n    picopt -f PNG,WEBP,ZIP,CBZ,EPUB *\n\nJust list files picopt.py would try to optimize:\n\n    picopt -L *\n\nOptimize pictures in my iPhoto library, but only after the last time I did this, skipping symlinks to avoid duplicate work. Also drop a timestamp file so I don\'t have to remember the last time I did this:\n\n    picopt -rSt -D \'2013 June 1 14:00\' \'Pictures/iPhoto Library\'\n\n## <a name="package">Packages</a>\n\n- [PyPI](https://pypi.python.org/pypi/picopt/)\n- [Arch Linux](https://aur.archlinux.org/packages/picopt/)\n\n## <a name="alternatives">Alternatives</a>\n\n[imagemin](https://github.com/imagemin/imagemin-cli) looks to be an all in one cli and gui solution with bundled libraries, so no awkward dependencies.\n[Imageoptim](http://imageoptim.com/) is an all-in-one OS X GUI image optimizer. Imageoptim command line usage is possible with [an external program](https://code.google.com/p/imageoptim/issues/detail?can=2&start=0&num=100&q=&colspec=ID%20Type%20Status%20Priority%20Milestone%20Owner%20Summary%20Stars&groupby=&sort=&id=39).\n',
    'author': 'AJ Slater',
    'author_email': 'aj@slater.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ajslater/picopt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
