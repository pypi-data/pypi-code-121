# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opensoundscape',
 'opensoundscape.preprocess',
 'opensoundscape.resources',
 'opensoundscape.torch',
 'opensoundscape.torch.architectures',
 'opensoundscape.torch.models']

package_data = \
{'': ['*']}

install_requires = \
['Deprecated>=1.2.13,<2.0.0',
 'Jinja2<3.0',
 'docopt>=0.6.2',
 'ipykernel>=5.2.0',
 'ipython>=7.10',
 'jupyterlab>=2.1.4',
 'librosa>=0.7.0',
 'matplotlib>=3.2.1',
 'numba>=0.48.0',
 'pandas>=1.3',
 'pywavelets>=1.2.0',
 'ray>=0.8.5',
 'schema>=0.7.2',
 'scikit-image>=0.17.2',
 'scikit-learn>=0.24.2',
 'tinytag>=1.6.0',
 'torch>=1.8.1',
 'torchvision>=0.9.1']

entry_points = \
{'console_scripts': ['build_docs = opensoundscape.console:build_docs',
                     'opensoundscape = opensoundscape.console:entrypoint']}

setup_kwargs = {
    'name': 'opensoundscape',
    'version': '0.7.0',
    'description': 'Open source, scalable acoustic classification for ecology and conservation',
    'long_description': '[![CI Status](https://github.com/kitzeslab/opensoundscape/workflows/CI/badge.svg)](https://github.com/kitzeslab/opensoundscape/actions?query=workflow%3ACI)\n[![Documentation Status](https://readthedocs.org/projects/opensoundscape/badge/?version=latest)](http://opensoundscape.org/en/latest/?badge=latest)\n\n# OpenSoundscape\n\nOpenSoundscape is a utility library for analyzing bioacoustic data. It consists of Python modules for tasks such as preprocessing audio data, training machine learning models to classify vocalizations, estimating the spatial location of sounds, identifying which species\' sounds are present in acoustic data, and more.\n\nThese utilities can be strung together to create data analysis pipelines. OpenSoundscape is designed to be run on any scale of computer: laptop, desktop, or computing cluster.\n\nOpenSoundscape is currently in active development. If you find a bug, please submit an issue. If you have another question about OpenSoundscape, please email Sam Lapp (`sam.lapp` at `pitt.edu`).\n\n\n#### Suggested Citation\n```\nLapp, Rhinehart, Freeland-Haynes, Khilnani, and Kitzes, 2022. "OpenSoundscape v0.7.0".\n```\n\n# Installation\n\nOpenSoundscape can be installed on Windows, Mac, and Linux machines. It has been tested on Python 3.7 and 3.8.\n\nMost users should install OpenSoundscape via pip: `pip install opensoundscape==0.7.0`. Contributors and advanced users can also use Poetry to install OpenSoundscape.\n\nFor more detailed instructions on how to install OpenSoundscape and use it in Jupyter, see the [documentation](http://opensoundscape.org).\n\n# Features & Tutorials\nOpenSoundscape includes functions to:\n* load and manipulate audio files\n* create and manipulate spectrograms\n* train CNNs on spectrograms with PyTorch\n* run pre-trained CNNs to detect vocalizations\n* detect periodic vocalizations with RIBBIT\n* load and manipulate Raven annotations\n\nOpenSoundscape can also be used with our library of publicly available trained machine learning models for the detection of 500 common North American bird species.\n\nFor full API documentation and tutorials on how to use OpenSoundscape to work with audio and spectrograms, train machine learning models, apply trained machine learning models to acoustic data, and detect periodic vocalizations using RIBBIT, see the [documentation](http://opensoundscape.org).\n\n# Quick Start\n\nUsing Audio and Spectrogram classes\n```python\nfrom opensoundscape.audio import Audio\nfrom opensoundscape.spectrogram import Spectrogram\n\n#load an audio file and trim out a 5 second clip\nmy_audio = Audio.from_file("/path/to/audio.wav")\nclip_5s = my_audio.trim(0,5)\n\n#create a spectrogram and plot it\nmy_spec = Spectrogram.from_audio(clip_5s)\nmy_spec.plot()\n```\n\nLoad audio starting at a real-world timestamp\n```python\nfrom datetime import datetime; import pytz\n\nstart_time = pytz.timezone(\'UTC\').localize(datetime(2020,4,4,10,25))\naudio_length = 5 #seconds  \npath = \'/path/to/audiomoth_file.WAV\' #an AudioMoth recording\n\nAudio.from_file(path, start_timestamp=start_time,duration=audio_length)\n```\n\nUsing a pre-trained CNN to make predictions on long audio files\n```python\nfrom opensoundscape.torch.models.cnn import load_model\n\n#get list of audio files\nfiles = glob(\'./dir/*.WAV\')\n\n#generate predictions with a model\nmodel = load_model(\'/path/to/saved.model\')\nscores, _, _ = model.predict(files)\n\n#scores is a dataframe with MultiIndex: file, start_time, end_time\n#containing inference scores for each class and each audio window\n```\n\nTraining a CNN with labeled audio data\n```python\nfrom opensoundscape.torch.models.cnn import CNN\nfrom sklearn.model_selection import train_test_split\n\n#load a DataFrame of one-hot audio clip labels\ndf = pd.read_csv(\'my_labels.csv\') #index: paths; columns: classes\ntrain_df, validation_df = train_test_split(df,test_size=0.2)\n\n#create a CNN and train on 2-second spectrograms for 2 epochs\nmodel = CNN(\'resnet18\',classes=df.columns,sample_duration=2.0)\nmodel.train(\n  train_df,\n  validation_df,\n  epochs=2\n)\n#the best model is automatically saved to a file `./best.model`\n```\n',
    'author': 'Justin Kitzes',
    'author_email': 'justin.kitzes@pitt.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jkitzes/opensoundscape',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1',
}


setup(**setup_kwargs)
