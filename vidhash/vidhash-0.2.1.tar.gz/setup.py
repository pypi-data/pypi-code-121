# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vidhash']

package_data = \
{'': ['*'], 'vidhash': ['stubs/*']}

install_requires = \
['ImageHash>=4.2.1,<5.0.0',
 'Pillow>=9.1.1,<10.0.0',
 'ffmpy3>=0.2.4,<0.3.0',
 'numpy>=1.22.4,<2.0.0']

setup_kwargs = {
    'name': 'vidhash',
    'version': '0.2.1',
    'description': 'A package for hashing videos and checking for similarity',
    'long_description': '# Vidhash\n[Vidhash](https://pypi.org/project/vidhash/) is a perceptual video hashing and checking library, to detect similar videos, or videos containing similar scenes.\n\n## How it works\nBasically, this video hashing works by scaling the video down a bit, and taking 5 frames a second as images, and performing image hashes on those frames.\nThen it can do checks by checking how many image hashes from one video match up with image hashes from another.\n\n## How to use\nThis documentation is a little sparse at the moment, but the basic summary is that to hash a video, use `video_hash = hash_video(video_path)`.  \nThis returns a `VideoHash` object.  \nYou can also provide a `HashSettings` object. HashSettings need to match for two video hashes to be compared.\nCurrently HashSettings allow specifying the\n\nWhen checking video hashes against each-other, use `video_hash.check_match(other_hash)`.\nYou can optionally provide a `MatchOptions` object as a second argument, or use a MatchOptions object and call the `MatchOptions.check_match(hash1, hash2)` method on it.\n\nThere are 3 supported types of MatchSettings:\n- `FrameCountMatch`\n  - Checks whether a specified number of frames match between the two videos\n  - Allows specifying the hamming distance between two frames which should be considered a "match"\n  - Allows ignoring blank frames\n- `PercentageMatch`\n  - Checks whether a specified percentage of the shorter video\'s frames match the longer video\n  - Allows specifying the hamming distance between two frames which should be considered a "match"\n  - Allows ignoring blank frames\n- `DurationMatch`\n  - Checks whether a specified "duration" of frames match up in order between the two videos\n    - e.g. 3 seconds duration, at 5 fps, would check whether 15 frames match, in a row, between the two videos\n  - Allows specifying the hamming distance between two frames which should be considered a "match"\n\n\n## Todo\n- Code\n  - Wrapper for imagehash.ImageHash\n  - Datastore\n    - (For looking up matching videos from a collection)\n- More documentation\n- More tests\n',
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SpangleLabs/vidhash',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
