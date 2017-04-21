ChEMBL webresource client
======

This is the only official Python client library developed and supported by ChEMBL (https://www.ebi.ac.uk/chembl/) group.

The library helps accessing ChEMBL data and cheminformatics tools from Python. You don't need to know how to write SQL. You don't need to know how to interact with REST APIs. You don't need to compile or install any cheminformatics framework. Results are cached.

Installation
------------

::

    pip install chembl_webresource_client
    
    
How to use it?
--------------

Some most frequent use cases below.

1. Search molecule by synonym:

   ::

      pip install chembl_webresource_client
        
2. Search target by gene name:
3. Find compounds similar to given SMILES query with similarity threshold of 85%:
4. Find compounds similar to aspirin (CHEMBL25) with similarity threshold of 70%:
5. Perform substructure search:
6. Get a single molecule by ChEMBL ID Key:
7. Get a single molecule by SMILES:
8. Get a single molecule by InChi Key:
9. Get many compounds by their ChEMBL IDs:
10. Get many compounds by a list of SMILES:
11. Get many compounds by a list of InChi Keys:
12. Get all approved drugs:
13. Get all molecules in ChEMBL with no Rule-of-Five violations:
14. Get all biotherapeutic molecules:
15. Return molecules with molecular weight <= 300:
16. Return molecules with molecular weight <= 300 AND pref_name ends with nib:
17. Get all Ki activities related to that hERG target:
18. Get all activitvities related to the Open TG-GATES project:
19. Search for ADMET-reated inhibitor assays:
20. Get cell line by cellosaurus id:
21. Filter drugs by approval year and name:
22. Get tissue by BTO ID:
23. Get tissue by Caloha id:
24. Get tissue by uberon id:
25. Get tissue by name:
26. Get tissue by chembl id:
27. Search documents for 'cytokine':
28. Filter targets:


.. image:: https://img.shields.io/pypi/v/chembl_webresource_client.svg
    :target: https://pypi.python.org/pypi/chembl_webresource_client/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/chembl_webresource_client.svg
    :target: https://pypi.python.org/pypi/chembl_webresource_client/
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/status/chembl_webresource_client.svg
    :target: https://pypi.python.org/pypi/chembl_webresource_client/
    :alt: Development Status

.. image:: https://img.shields.io/pypi/l/chembl_webresource_client.svg
    :target: https://pypi.python.org/pypi/chembl_webresource_client/
    :alt: License

.. image:: https://travis-ci.org/chembl/chembl_webresource_client.svg?branch=master
    :target: https://travis-ci.org/chembl/chembl_webresource_client
