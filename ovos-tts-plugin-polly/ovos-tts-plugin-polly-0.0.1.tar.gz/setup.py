#!/usr/bin/env python3
from setuptools import setup

PLUGIN_ENTRY_POINT = 'ovos-tts-plugin-polly = ' \
                     'ovos_tts_plugin_polly:PollyTTS'
setup(
    name='ovos-tts-plugin-polly',
    version='0.0.1',
    description='polly tts plugin for OpenVoiceOS mycroft neon chatterbox',
    url='https://github.com/OpenVoiceOS/ovos-tts-plugin-polly',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    packages=['ovos_tts_plugin_polly'],
    install_requires=["boto3", 'ovos-plugin-manager>=0.0.1a13'],
    zip_safe=True,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3'
    ],
    keywords='OpenVoiceOS mycroft neon chatterbox plugin tts',
    entry_points={'mycroft.plugin.tts': PLUGIN_ENTRY_POINT}
)
