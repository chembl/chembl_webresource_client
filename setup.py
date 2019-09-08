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
    version='0.10.0,
    entry_points={
        'console_scripts': [
            'chembl_ids=chembl_webresource_client.scripts.chembl_ids:main',
            'chembl_sim=chembl_webresource_client.scripts.chembl_sim:main',
            'chembl_sub=chembl_webresource_client.scripts.chembl_sub:main',
            'chembl_m2t=chembl_webresource_client.scripts.chembl_m2t:main',
            'chembl_t2m=chembl_webresource_client.scripts.chembl_t2m:main',
            'chembl_act=chembl_webresource_client.scripts.chembl_act:main',
        ]
    },
    author='Michal Nowotka',
    author_email='mnowotka@ebi.ac.uk',
    description='Python client fot accessing ChEMBL webservices.',
    url='https://www.ebi.ac.uk/chembldb/index.php/ws',
    license='Apache Software License',
    packages=['chembl_webresource_client',
             'chembl_webresource_client.scripts'],
    long_description="""
    Documentation and repository: https://github.com/chembl/chembl_webresource_client.
    This is the only official Python client library developed and supported by ChEMBL (https://www.ebi.ac.uk/chembl/) group.

    The library helps accessing ChEMBL data and cheminformatics tools from Python. 
    You don't need to know how to write SQL. 
    You don't need to know how to interact with REST APIs. 
    You don't need to compile or install any cheminformatics framework. 
    Results are cached.
    """,
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Apache Software License',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Scientific/Engineering :: Chemistry'],
    zip_safe=False,
)
