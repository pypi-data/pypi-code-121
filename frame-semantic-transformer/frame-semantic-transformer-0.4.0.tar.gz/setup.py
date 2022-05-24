# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['frame_semantic_transformer',
 'frame_semantic_transformer.data',
 'frame_semantic_transformer.data.augmentations',
 'frame_semantic_transformer.data.tasks']

package_data = \
{'': ['*']}

install_requires = \
['nltk>=3.7,<4.0',
 'pytorch-lightning>=1.6.2,<2.0.0',
 'sentencepiece>=0.1.96,<0.2.0',
 'torch>=1.11.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0',
 'transformers>=4.18.0,<5.0.0']

setup_kwargs = {
    'name': 'frame-semantic-transformer',
    'version': '0.4.0',
    'description': 'Frame Semantic Parser based on T5 and FrameNet',
    'long_description': '# Frame Semantic Transformer\n\n[![ci](https://img.shields.io/github/workflow/status/chanind/frame-semantic-transformer/CI/main)](https://github.com/chanind/frame-semantic-transformer)\n[![PyPI](https://img.shields.io/pypi/v/frame-semantic-transformer?color=blue)](https://pypi.org/project/frame-semantic-transformer/)\n\nFrame-based semantic parsing library trained on [FrameNet](https://framenet2.icsi.berkeley.edu/) and built on HuggingFace\'s [T5 Transformer](https://huggingface.co/docs/transformers/model_doc/t5). This library is designed to be easy to use, yet powerful.\n\n**Live Demo: [chanind.github.io/frame-semantic-transformer](https://chanind.github.io/frame-semantic-transformer)**\n\nThis library draws heavily on [Open-Sesame](https://github.com/swabhs/open-sesame) ([paper](https://arxiv.org/abs/1706.09528)) for inspiration on training and evaluation on FrameNet 1.7, and uses ideas from the paper [Open-Domain Frame Semantic Parsing Using Transformers](https://arxiv.org/abs/2010.10998) for using T5 as a frame-semantic parser. [SimpleT5](https://github.com/Shivanandroy/simpleT5) was also used as a base for the initial training setup.\n\n## Performance\n\nThis library uses the same train/dev/test documents and evaluation methodology as Open-Sesame, so that the results should be comparable between the 2 libraries. There are 2 pretrained models available, `base` and `small`, corresponding to `t5-base` and `t5-small` in Huggingface, respectively.\n\n| Task                   | Sesame F1 (dev/test) | Small Model F1 (dev/test) | Base Model F1 (dev/test) |\n| ---------------------- | -------------------- | ------------------------- | ------------------------ |\n| Trigger identification | 0.80 / 0.73          | 0.69 / 0.66               | 0.76 / 0.72              |\n| Frame classification   | 0.90 / 0.87          | 0.82 / 0.81               | 0.88 / 0.87              |\n| Argument extraction    | 0.61 / 0.61          | 0.68 / 0.61               | 0.74 / 0.72              |\n\nThe base model performs similarly to Open-Sesame on trigger identification and frame classification tasks, but outperforms it by a significant margin on argument extraction. The small pretrained model has lower F1 than base across the board, but is 1/4 the size and is still comparable to Open-Sesame at argument extraction.\n\n## Installation\n\n```\npip install frame-semantic-transformer\n```\n\n## Usage\n\n### Inference\n\nThe main entry to interacting with the library is the `FrameSemanticTransformer` class, as shown below. For inference the `detect_frames()` method is likely all that is needed to perform frame parsing.\n\n```python\nfrom frame_semantic_transformer import FrameSemanticTransformer\n\nframe_transformer = FrameSemanticTransformer()\n\nresult = frame_transformer.detect_frames("The hallway smelt of boiled cabbage and old rag mats.")\n\nprint(f"Results found in: {result.sentence}")\nfor frames in result.frames:\n    print(f"FRAME: {frame.name}")\n    for element in frame.frame_elements:\n        print(f"{element.name}: {element.text}")\n```\n\nThe result returned from `detect_frames()` is an object containing `sentence`, a parsed version of the original sentence text, `trigger_locations`, the indices within the sentence where frame triggers were detected, and `frames`, a list of all detected frames in the sentence. Within `frames`, each object containes `name` which corresponds to the FrameNet name of the frame, `trigger_location` corresponding to which trigger in the text this frame this frame uses, and `frame_elements` containing a list of all relevant frame elements found in the text.\n\n### Loading Models\n\nThere are currently 2 available pre-trained models for inference, called `base` and `small`, fine-tuned from HuggingFace\'s [t5-base](https://huggingface.co/t5-base) and [t5-small](https://huggingface.co/t5-base) model respectively. If a local fine-tuned t5 model exists that can be loaded as well. If no model is specified, the `base` model will be used.\n\n```\nbase_transformer = FrameSemanticTransformer("base") # this is also the default\nsmall_transformer = FrameSemanticTransformer("small") # a smaller pretrained model which is faster to run\ncustom_transformer = FrameSemanticTransformer("/path/to/model") # load a custom t5 model\n```\n\nBy default, models are lazily loaded when `detect_frames()` is first called. If you want to load the model sooner, you can call `setup()` on a `FrameSemanticTransformer` instance to load models immediately.\n\n```\nframe_transformer = FrameSemanticTransformer()\nframe_transformer.setup() # load models immediately\n```\n\n### Training\n\nIf you want to train a new model yourself, you can run the training script like below:\n\n```\npython -m frame_semantic_transformer.train \\\n    --base-model t5-base \\\n    --use-gpu \\\n    --batch-size 8 \\\n    --epochs 10 \\\n    --learning-rate 1e-5 \\\n    --output-dir ./outputs\n```\n\nTraining uses [Pytorch Lightning](https://www.pytorchlightning.ai/) behind the scenes, and will place tensorboard logs into `./lightning_logs` as it trains.\n\nIf you need more control, you can also directly import the `train()` method from `frame_semantic_transformer.train` and run training directly in code.\n\n## Contributing\n\nAny contributions to improve this project are welcome! Please open an issue or pull request in this repo with any bugfixes / changes / improvements you have!\n\nThis project uses [Black](https://github.com/psf/black) for code formatting, [Flake8](https://flake8.pycqa.org/en/latest/) for linting, and [Pytest](https://docs.pytest.org/) for tests. Make sure any changes you submit pass these code checks in your PR. If you have trouble getting these to run feel free to open a pull-request regardless and we can discuss further in the PR.\n\n## License\n\nThe code contained in this repo is released under a MIT license, however the pretrained models are released under an Apache 2.0 license in accordance with FrameNet training data and HuggingFace\'s T5 base models.\n',
    'author': 'David Chanin',
    'author_email': 'chanindav@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chanind/frame-semantic-transformer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
