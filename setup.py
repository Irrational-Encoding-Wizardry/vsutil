from setuptools import setup, find_packages
from setuptools.command.test import test
from distutils.util import convert_path

# We can't import the submodule normally as that would "run" the main module
# code while the setup script is meant to *build* the module.

# Besides preventing a whole possible mess of issues with an un-built package,
# this also prevents the vapoursynth import which breaks the docs on RTD.

# convert_path is used here because according to the distutils docs:
# '...filenames in the setup script are always supplied in Unix
# style, and have to be converted to the local convention before we can
# actually use them in the filesystem.'
meta = {}
exec(open(convert_path('vsutil/_metadata.py')).read(), meta)


class DiscoverTest(test):

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import os
        import unittest
        path = os.path.join(os.path.dirname(__file__), "tests")
        runner = unittest.TextTestRunner(verbosity=2)
        suite = unittest.TestLoader().discover(path, pattern="test_*.py")
        runner.run(suite)


setup(
    name='vsutil',
    version=meta['__version__'],
    packages=find_packages(exclude=['tests']),
    package_data={
        'vsutil': ['py.typed']
    },
    url='https://encode.moe/vsutil',
    license='MIT',
    author=meta['__author__'].split()[0],
    author_email=meta['__author__'].split()[1][1:-1],
    description='A collection of general-purpose Vapoursynth functions to be reused in modules and scripts.',
    install_requires=[
        "vapoursynth"
    ],
    cmdclass={
        'test': DiscoverTest
    },
    python_requires='>=3.8',
    project_urls={
        'Documentation': 'http://vsutil.encode.moe/en/latest/',
        'Source': 'https://github.com/Irrational-Encoding-Wizardry/vsutil',
        'Tracker': 'https://github.com/Irrational-Encoding-Wizardry/vsutil/issues',
    },
    keywords='encoding vapoursynth video',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Video",
        "Typing :: Typed",
    ],
)
