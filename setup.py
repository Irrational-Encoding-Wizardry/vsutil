import os
from setuptools import setup
from setuptools.command.test import test


class DiscoverTest(test):

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import unittest
        path = os.path.join(os.path.dirname(__file__), "tests")
        runner = unittest.TextTestRunner(verbosity=2)
        suite = unittest.TestLoader().discover(path, pattern="test_*.py")
        runner.run(suite)


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
    cmdclass={
        'test': DiscoverTest
    }
)
