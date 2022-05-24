# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['playwrightcapture']

package_data = \
{'': ['*']}

install_requires = \
['dateparser>=1.1.1,<2.0.0', 'playwright>=1.22.0,<2.0.0']

extras_require = \
{'recaptcha': ['requests>=2.27.1,<3.0.0',
               'pydub>=0.25.1,<0.26.0',
               'SpeechRecognition>=3.8.1,<4.0.0']}

setup_kwargs = {
    'name': 'playwrightcapture',
    'version': '1.12.1',
    'description': 'A simple library to capture websites using playwright',
    'long_description': '# Playwright Capture\n\nSimple replacement for [splash](https://github.com/scrapinghub/splash) using [playwright](https://github.com/microsoft/playwright-python).\n\n# Install\n\n```bash\npip install playwrightcapture\n```\n\n# Usage\n\nA very basic example:\n\n```python\nfrom playwrightcapture import Capture\n\nasync with Capture() as capture:\n    await capture.prepare_context()\n    entries = await capture.capture_page(url)\n```\n\nEntries is a dictionaries that contains (if all goes well) the HAR, the screenshot, all the cookies of the session, the URL as it is in the browser at the end of the capture, and the full HTML page as rendered.\n\n\n# reCAPTCHA bypass\n\nNo blackmagic, it is just a reimplementation of a [well known technique](https://github.com/NikolaiT/uncaptcha3)\nas implemented [there](https://github.com/Binit-Dhakal/Google-reCAPTCHA-v3-solver-using-playwright-python),\nand [there](https://github.com/embium/solverecaptchas).\n\nThis modules will try to bypass reCAPTCHA protected websites if you install it this way:\n\n```bash\npip install playwrightcapture[recaptcha]\n```\n\nThis will install `requests`, `pydub` and `SpeechRecognition`. In order to work, `pydub`\nrequires `ffmpeg` or `libav`, look at the [install guide ](https://github.com/jiaaro/pydub#installation)\nfor more details.\n`SpeechRecognition` uses the Google Speech Recognition API to turn the audio file into text (I hope you appreciate the irony).\n',
    'author': 'Raphaël Vinot',
    'author_email': 'raphael.vinot@circl.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Lookyloo/PlaywrightCapture',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
