# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='quicksave-consoleplugin',
      version='0.3.0',
      description='Quicksave.pl plugin for Linux',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'License :: Other/Proprietary License',
      ],
      author='Quicksave.pl',
      packages=['qsconsoleplugin'],
      install_requires=[
          # 'py-notify==0.3.1',
      ],
      entry_points={
          'console_scripts': ['qs=qsconsoleplugin.cmd:main'],
      },
      zip_safe=False)
