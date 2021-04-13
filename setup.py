#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'mnowotka'

from setuptools import setup

setup(
    name='chembl-webresource-client',
    version='0.10.3',
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
    url='https://www.ebi.ac.uk/chembl/api/data/docs',
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
    install_requires=[
        'urllib3',
        'requests>=2.18.4',
        'requests-cache>=0.4.7',
        'easydict',
    ],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Apache Software License',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Topic :: Scientific/Engineering :: Chemistry'],
    zip_safe=False,
)
