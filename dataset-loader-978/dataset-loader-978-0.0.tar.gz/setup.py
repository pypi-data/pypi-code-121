from setuptools import setup, find_packages

from dataset_loader import __version__

setup(
    name='dataset-loader-978',
    version=__version__,

    url='https://github.com/seppia978/dataset-loader-978',
    author='seppia978',
    author_email='samuele.poppi@unimore.it',

    # py_modules=['ZoomCAM'],
    packages=find_packages(),
    package_data={
        # 'annotations': ['*'],
        # 'Architecture': ['*'],
        # 'AttributionMethod': ['*'],
        'dataset_loader': ['*'],
        # 'FakeCAMS': ['*'],
        # 'generics': ['*'],
        # 'images_utils': ['*'],
        # 'pytorch_grad_cam': ['*'],
        # 'RelevanceCAM': ['*'],
        # 'torchcammaster': ['*'],
        # 'ZoomCAM': ['*']
    },
    include_package_data=True
)