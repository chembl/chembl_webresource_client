#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'mnowotka'

import sys

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='chembl-webresource-client',
    version='0.9.12',
    author='Michal Nowotka',
    author_email='mnowotka@ebi.ac.uk',
    description='Python client fot accessing ChEMBL webservices.',
    url='https://www.ebi.ac.uk/chembldb/index.php/ws',
    license='Apache Software License',
    packages=['chembl_webresource_client'],
    long_description="""
    Documentation and repository: https://github.com/chembl/chembl_webresource_client.
    This is the only official Python client library developed and supported by ChEMBL (https://www.ebi.ac.uk/chembl/) group.

    The library helps accessing ChEMBL data and cheminformatics tools from Python. 
    You don't need to know how to write SQL. 
    You don't need to know how to interact with REST APIs. 
    You don't need to compile or install any cheminformatics framework. 
    Results are cached.
    """,
    install_requires=[
        'six',
        'urllib3',
        'requests==2.5.3',
        'requests-cache>=0.4.7',
        'grequests==0.2.0',
        'easydict',
        'gevent<1.2.0'
    ],
    tests_require = ['pytest-timeout'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Apache Software License',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.3',
                 'Topic :: Scientific/Engineering :: Chemistry'],
    zip_safe=False,
)
