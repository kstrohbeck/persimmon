from os import path
from setuptools import setup


long_description = 'Idiomatic parser combinators, Python-style.'
if path.exists('README.rst'):
    long_description = open('README.rst').read()


setup(
    name='persimmon',
    version='0.0.1',
    author='Kyle Strohbeck',
    author_email='kstrohbeck@gmail.com',
    description='Idiomatic parser combinators, Python-style.',
    long_description=long_description,
    url='https://github.com/kstrohbeck/persimmon',
    packages=['persimmon'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
