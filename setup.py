from setuptools import setup, find_packages
from setuptools.command.test import test


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
    version='0.5.0',
    packages=find_packages(exclude=['tests']),
    package_data={
        'vsutil': ['py.typed']
    },
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
