from distutils.core import setup

setup(
    name='realt',
    version='0.1.dev0',
    author='Anthony Theocharis',
    url='https://github.com/anthonyt/real_transparency',
    packages=['realt',],
    license='Apache License 2.0',
    long_description=open('README.md').read(),
    install_requires=[
        'nose',
        'mock',
        'requests',
    ],
)
