ChEMBL webresource client
======

This is the only official Python client library developed and supported by ChEMBL (https://www.ebi.ac.uk/chembl/) group.

The library helps accessing ChEMBL data and cheminformatics tools from Python. You don't need to know how to write SQL. You don't need to know how to interact with REST APIs. You don't need to compile or install any cheminformatics framework. Results are cached.

Installation
------------

::

    pip install chembl_webresource_client
    
    
Quick start
--------------

Some most frequent use cases below.

1. Search molecule by synonym:

   ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      res = molecule.search('viagra')
        
2. Search target by gene name:

   ::

      from chembl_webresource_client.new_client import new_client
      target = new_client.target
      gene_name = 'GABRB2'
      res = target.search(gene_name)
      
   or directly in the target synonym field:
   
   ::

      from chembl_webresource_client.new_client import new_client
      target = new_client.target
      gene_name = 'GABRB2'
      res = target.filter(target_synonym__icontains=gene_name)

3. Find compounds similar to given SMILES query with similarity threshold of 85%:

   ::

      from chembl_webresource_client.new_client import new_client
      similarity = new_client.similarity
      res = similarity.filter(smiles="CO[C@@H](CCC#C\C=C/CCCC(C)CCCCC=C)C(=O)[O-]", similarity=85)
  
4. Find compounds similar to aspirin (CHEMBL25) with similarity threshold of 70%:

   ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      similarity = new_client.similarity
      aspirin_chembl_id = molecule.search('aspirin')[0]['molecule_chembl_id']
      res = similarity.filter(chembl_id="CHEMBL25", similarity=70)
      
5. Perform substructure search using SMILES:

   ::

      from chembl_webresource_client.new_client import new_client
      substructure = new_client.substructure
      res = substructure.filter(smiles="CN(CCCN)c1cccc2ccccc12")
      
6. Perform substructure search using ChEMBL ID:

   ::

      from chembl_webresource_client.new_client import new_client
      substructure = new_client.substructure
      substructure.filter(chembl_id="CHEMBL25")

6. Get a single molecule by ChEMBL ID:

   ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      m1 = molecule.get('CHEMBL25')

7. Get a single molecule by SMILES:

   ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      m1 = molecule.get('CC(=O)Oc1ccccc1C(=O)O')

8. Get a single molecule by InChi Key:

   ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      molecule.get('BSYNRYMUTXBXSQ-UHFFFAOYSA-N')

9. Get many compounds by their ChEMBL IDs:

   ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      records = molecule.get(['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505'])

10. Get many compounds by a list of SMILES:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      records = molecule.get(['CNC(=O)c1ccc(cc1)N(CC#C)Cc2ccc3nc(C)nc(O)c3c2',
            'Cc1cc2SC(C)(C)CC(C)(C)c2cc1\\N=C(/S)\\Nc3ccc(cc3)S(=O)(=O)N',
            'CC(C)C[C@H](NC(=O)[C@@H](NC(=O)[C@H](Cc1c[nH]c2ccccc12)NC(=O)[C@H]3CCCN3C(=O)C(CCCCN)CCCCN)C(C)(C)C)C(=O)O'])

11. Get many compounds by a list of InChi Keys:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      records = molecule.get(['XSQLHVPPXBBUPP-UHFFFAOYSA-N', 'JXHVRXRRSSBGPY-UHFFFAOYSA-N', 'TUHYVXGNMOGVMR-GASGPIRDSA-N'])

12. Get all approved drugs:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      approved_drugs = molecule.filter(max_phase=4)

13. Get all molecules in ChEMBL with no Rule-of-Five violations:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      no_violations = molecule.filter(molecule_properties__num_ro5_violations=0)

14. Get all biotherapeutic molecules:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      biotherapeutics = molecule.filter(biotherapeutic__isnull=False)

15. Return molecules with molecular weight <= 300:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      light_molecules = molecule.filter(molecule_properties__mw_freebase__lte=300)
      
16. Return molecules with molecular weight <= 300 AND pref_name ends with nib:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      light_nib_molecules = molecule.filter(molecule_properties__mw_freebase__lte=300).filter(pref_name__iendswith="nib")

17. Get all Ki activities related to that hERG target:

    ::

      from chembl_webresource_client.new_client import new_client
      target = new_client.target
      activity = new_client.activity
      herg = target.search('herg')[0]
      herg_activities = activity.filter(target_chembl_id=herg['target_chembl_id']).filter(standard_type="Ki")

18. Get all activitvities related to the Open TG-GATES project:

    ::

      from chembl_webresource_client.new_client import new_client
      activity = new_client.activity
      res = activity.search('"TG-GATES"')

19. Search for ADMET-reated inhibitor assays:

    ::

      from chembl_webresource_client.new_client import new_client
      assay = new_client.assay
      res = assay.search('inhibitor').filter(assay_type='A')

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
