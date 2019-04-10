from setuptools import setup

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
    ]
)
