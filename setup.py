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
        # direct dependencies
        'nose == 1.3.7',
        'mock == 1.1.3',
        'lxml == 3.4.4',
        'requests == 2.7.0',

        # sub-dependencies
        'six == 1.9.0',
        'pbr == 1.3.0',
        'funcsigs == 0.4',
    ],
)
