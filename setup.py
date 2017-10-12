"""quicksave command line client

This file is a part of quicksave project.
Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.

see: https://quicksave.io
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='quicksave client',

    version='0.0.0',

    description='quicksave command line client',
    long_description=long_description,

    url='https://github.com/adiog/io_quicksave_client',

    author='Aleksander Gajewski',
    author_email='adiog@quicksave.io',

    license='GPLv3',

    classifiers=[
        'Development Status:: 1 - Planning',

        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',

        'Intended Audience :: End Users/Desktop',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',

        'Topic :: Utilities'
    ],

    keywords='quicksave command line client',

    packages=find_packages('src'),

    install_requires=['PyQt5', 'python-magic', 'requests'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    package_dir={
        '': 'src'
    },

    include_package_data=True,

    #package_data={
    #    'qs': ['data/*.png', 'data/quicksave.ini'],
    #},

    entry_points={
        'console_scripts': [
            'qs=qs.client.main:qs',
        ],
    },
)
