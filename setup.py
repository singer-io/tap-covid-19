#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap-covid-19',
      version='0.0.10',
      description='Singer.io tap for extracting COVID-19 CSV data files with the GitHub API',
      author='jeff.huth@bytecode.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_covid_19'],
      install_requires=[
          'backoff==1.8.0',
          'requests==2.23.0',
          'singer-python==5.9.0'
      ],
      entry_points='''
          [console_scripts]
          tap-covid-19=tap_covid_19:main
      ''',
      packages=find_packages(),
      package_data={
          'tap_covid_19': [
              'schemas/*.json'
          ]
      })
