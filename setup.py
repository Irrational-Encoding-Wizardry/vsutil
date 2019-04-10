import os
from setuptools import setup


def discover_tests():
    import unittest
    path = os.path.join(os.path.dirname(__file__), "tests")
    return unittest.TestLoader().discover(path, pattern="test_*.py")


setup(
    name='vsutil',
    version='0.1.0',
    py_modules=['vsutil'],
    url='https://encode.moe/vsutil',
    license='MIT',
    author='kageru',
    author_email='wizards@encode.moe',
    description='A collection of general-purpose Vapoursynth functions to be reused in modules and scripts.',
    install_requires=[
        "vapoursynth"
    ],
    test_suite="setup.discover_tests"
)
