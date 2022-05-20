from setuptools import setup, Extension


setup(
    name='dequeapp',
    version='0.0035',
    description='Python Package for Deque tools',
    author="The Deque Team",
    author_email='team@deque.app',
    packages=["deque"],
    url='https://github.com/rijupahwa/deque',
    keywords='deque client for experiment tracking, sweep and other deep learning tooling',
    install_requires=[
          'redis','redis-server',"coolname","requests","pillow"
      ],
)