# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_color_transfer']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19,<2.0', 'opencv-python>=4.2,<5.0']

setup_kwargs = {
    'name': 'python-color-transfer',
    'version': '0.1.0b0',
    'description': 'Three methods of color transfer implemented in python.',
    'long_description': "# Color Transfer in Python\n\nThree methods of color transfer implemented in python.\n\n## Examples\ninput img | reference img | mean std transfer | lab mean std transfer | pdf transfer + regrain\n![img](https://raw.githubusercontent.com/pengbo-learn/python-color-transfer/master/imgs/house_display.png)\n![img](https://github.com/pengbo-learn/python-color-transfer/blob/master/imgs/tower_display.png?raw=true)\n![img](https://github.com/pengbo-learn/python-color-transfer/blob/master/imgs/scotland_display.png?raw=true)\n![img](https://github.com/pengbo-learn/python-color-transfer/blob/master/imgs/fallingwater_display.png?raw=true)\n\n## Pip Wheels\n\n### install\n```bash\npip install python-color-transfer\n```\n\n### usage\n```bash\nfrom python_color_transfer.color_transfer import ColorTransfer\n\nPT = ColorTransfer()\n\n# input image and reference image\nimg_arr_in = cv2.imread(img_path)\nimg_arr_ref = cv2.imread(ref_path)\n\n# pdf transfer\nimg_arr_reg = PT.pdf_tranfer(img_arr_in=img_arr_in,\n                             img_arr_ref=img_arr_ref,\n                             regrain=True)\n\n# mean transfer\nimg_arr_mt = PT.mean_std_transfer(img_arr_in=img_arr_in,\n                                  img_arr_ref=img_arr_ref)\n\n# lab transfer\nimg_arr_lt = PT.lab_transfer(img_arr_in=img_arr_in,\n                             img_arr_ref=img_arr_ref)\n```\n\n## From source\n\n### Clone\n```bash\ngit clone https://github.com/pengbo-learn/python-color-transfer.git\n```\n\n### Environment\n- python3\n- install dependency by ```sh env.sh```.\n```bash\n# env.sh\npip3 install opencv-python==4.2.0.34\npip3 install numpy==1.19.3\n```\n    \n\n### Run\n```bash\n# python demo.py \n/root/python_color_transfer/imgs/scotland_house.png: 361x481x3\n/root/python_color_transfer/imgs/scotland_plain.png: 361x481x3\npdf transfer time: 0.67s\nregrain time: 0.49s\nmean std transfer time: 0.04s\nlab mean std transfer time: 0.22s\nsave to /root/python_color_transfer/imgs/scotland_display.png\n\n/root/python_color_transfer/imgs/house.jpeg: 512x768x3\n/root/python_color_transfer/imgs/hats.png: 512x768x3\npdf transfer time: 1.47s\nregrain time: 1.16s\nmean std transfer time: 0.09s\nlab mean std transfer time: 0.09s\nsave to /root/python_color_transfer/imgs/house_display.png\n\n/root/python_color_transfer/imgs/fallingwater.png: 727x483x3\n/root/python_color_transfer/imgs/autumn.jpg: 727x1000x3\npdf transfer time: 1.87s\nregrain time: 0.87s\nmean std transfer time: 0.12s\nlab mean std transfer time: 0.11s\nsave to /root/python_color_transfer/imgs/fallingwater_display.png\n\n/root/python_color_transfer/imgs/tower.jpeg: 743x1280x3\n/root/python_color_transfer/imgs/sunset.jpg: 743x1114x3\npdf transfer time: 2.95s\nregrain time: 2.83s\nmean std transfer time: 0.23s\nlab mean std transfer time: 0.21s\nsave to /root/python_color_transfer/imgs/tower_display.png\n```\n\n## Methods\n\nLet input image be I, reference image be R and output image be O.\\\nLet f{I}(r, g, b), f{R}(r, g, b) be probability density functions of I and R's rgb values. \n\n- mean std transfer\n\n    O = (I - mean(I)) / std(I) \\* std(R) + mean(R).\n\n- lab mean transfer\n\n    I' = rgb2lab(I),\\\n    R' = rgb2lab(R),\\\n    O' = (I' - mean(I')) / std(I') \\* std(R') + mean(R'),\\\n    O = lab2rgb(O').\n\n- pdf transfer\n\n    O = t(I), where t: R^3-> R^3 is a continous mapping so that f{t(I)}(r, g, b) = f{R}(r, g, b). \n\n\n\n## References\n- pdf transfer\\\n    [Automated colour grading using colour distribution transfer](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.458.7694&rep=rep1&type=pdf) by F. Pitie , A. Kokaram and R. Dahyot.\\\n    [Author's matlab implementation](https://github.com/frcs/colour-transfer)\n\n- lab mean transfer\\\n    [Color Transfer between Images](https://www.cs.tau.ac.il/~turkel/imagepapers/ColorTransfer.pdf) by Erik Reinhard, Michael Ashikhmin, Bruce Gooch and Peter Shirley.\\\n    [Open source's python implementation](https://github.com/chia56028/Color-Transfer-between-Images)\n\n",
    'author': 'pengbo-learn',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
