ChEMBL webresource client
======

This is the only official Python client library developed and supported by ChEMBL (https://www.ebi.ac.uk/chembl/) group. Python 2 and 3 compatible.

The library helps accessing ChEMBL data and cheminformatics tools from Python. You don't need to know how to write SQL. You don't need to know how to interact with REST APIs. You don't need to compile or install any cheminformatics framework. Results are cached.

The client handles interaction with the HTTPS protocol and caches all results in the local file system for faster retrieval. Abstracting away all network-related tasks, the client provides the end user with a convenient interface, giving the impression of working with a local resource. Design is based on the Django QuerySet interface (https://docs.djangoproject.com/en/1.11/ref/models/querysets/). The client also implements lazy evaluation of results, which means it will only evaluate a request for data when a value is required. This approach reduces number of network requests and increases performance. 

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

3. Having a list of molecules ChEMBL IDs in a CSV file, produce another CSV file that maps every compound ID into a list
   of uniprot accession numbers and save the mapping into output csv file.

   ::
   
        import csv
        from chembl_webresource_client.new_client import new_client

        # This will be our resulting structure mapping compound ChEMBL IDs into target uniprot IDs
        compounds2targets = dict()

        # First, let's just parse the csv file to extract compounds ChEMBL IDs:
        with open('compounds_list.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                compounds2targets[row[0]] = set()

        # OK, we have our source IDs, let's process them in chunks:
        chunk_size = 50
        keys = compounds2targets.keys()

        for i in range(0, len(keys), chunk_size):
            # we jump from compounds to targets through activities:
            activities = new_client.activity.filter(molecule_chembl_id__in=keys[i:i + chunk_size])
            # extracting target ChEMBL IDs from activities:
            for act in activities:
                compounds2targets[act['molecule_chembl_id']].add(act['target_chembl_id'])

        # OK, now our dictionary maps from compound ChEMBL IDs into target ChEMBL IDs
        # We would like to replace target ChEMBL IDs with uniprot IDs

        for key, val in compounds2targets.items():
            # We don't know how many targets are assigned to a given compound so again it's
            # better to process targets in chunks:
            lval = list(val)
            uniprots = set()
            for i in range(0, len(val), chunk_size):
                targets = new_client.target.filter(target_chembl_id__in=lval[i:i + chunk_size])
                uniprots |= set(sum([[comp['accession'] for comp in t['target_components']] for t in targets],[]))
            compounds2targets[key] = uniprots

        # Finally write it to the output csv file
        with open('compounds_2_targets.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            for key, val in compounds2targets.items():
                writer.writerow([key] + list(val))      

4. If you run the example above to get all distinct uniprot accession for targets related with oxacillin (CHEMBL819) you will find only 3 targets for E.coli (A1E3K9, P35695, P62593). ChEMBL website (https://www.ebi.ac.uk/chembl/compound/inspect/CHEMBL819), on the other hand will show 4 targets (A1E3K9, P35695, P62593 and P00811). You may wonder why this discrepancy occurs. The ChEMBL interface aggregates data from salts and parent compounds and API just returns the data as they are stored in the database. In order to get the same results you will need to add in a call to the molecule_forms endpoint like in the example below, which is taken directly from Marco Galadrini repository (https://github.com/mgalardini/chembl_tools) exposing more useful functions that will soon become a part of the client (https://github.com/chembl/chembl_webresource_client/issues/25).

   ::
   
        from chembl_webresource_client.new_client import new_client

        organism = 'Escherichia coli'
        compounds2targets = {}
        header = True
        for name, chembl in [(x.split('\t')[0], x.rstrip().split('\t')[1])
                             for x in open('compounds_list.csv')]:
            if header:
                header = False
                continue
            compounds2targets[chembl] = set()

        chunk_size = 50
        keys = compounds2targets.keys()

        ID_forms = dict()
        for x in keys:
            ID_forms[x] = set()

        for i in range(0, len(keys), chunk_size):
            for form in new_client.molecule_form.filter(parent_chembl_id__in=keys[i:i + chunk_size]):
                ID_forms[form['parent_chembl_id']].add(form['molecule_chembl_id'])

        for i in range(0, len(keys), chunk_size):
            for form in new_client.molecule_form.filter(molecule_chembl_id__in=keys[i:i + chunk_size]):
                ID_forms[form['molecule_chembl_id']].add(form['parent_chembl_id'])

        values = []
        for x in ID_forms.values():
            values.extend(x)
        forms_to_ID = dict()
        for x in values:
            forms_to_ID[x] = set()

        for k in forms_to_ID:
            for parent, molecule in ID_forms.items():
                if k in molecule:
                    forms_to_ID[k] = parent

        for i in range(0, len(values), chunk_size):
            activities = new_client.activity.filter(molecule_chembl_id__in=values[i:i + chunk_size]).filter(target_organism__istartswith=organism)
            for act in activities:
                compounds2targets[forms_to_ID[act['molecule_chembl_id']]].add(act['target_chembl_id'])

        for key, val in compounds2targets.items():
            lval = list(val)
            uniprots = set()
            for i in range(0, len(val), chunk_size):
                targets = new_client.target.filter(target_chembl_id__in=lval[i:i + chunk_size])
                uniprots = uniprots.union(set(sum([[comp['accession'] for comp in t['target_components']] for t in targets],[])))
            compounds2targets[key] = uniprots

        print('\t'.join(('chembl', 'target')))
        for chembl in sorted(compounds2targets):
            for uniprot in compounds2targets[chembl]:
    print('\t'.join((chembl, uniprot)))

5. Having a list of molecules ChEMBL IDs in a CSV file, produce another CSV file that maps every compound ID into a list
   of human gene names.

   ::
   
        import csv
        from chembl_webresource_client.new_client import new_client

        # This will be our resulting structure mapping compound ChEMBL IDs into target uniprot IDs
        compounds2targets = dict()

        # First, let's just parse the csv file to extract compounds ChEMBL IDs:
        with open('compounds_list.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                compounds2targets[row[0]] = set()

        # OK, we have our source IDs, let's process them in chunks:
        chunk_size = 50
        keys = compounds2targets.keys()

        for i in range(0, len(keys), chunk_size):
            # we jump from compounds to targets through activities:
            activities = new_client.activity.filter(molecule_chembl_id__in=keys[i:i + chunk_size])
            # extracting target ChEMBL IDs from activities:
            for act in activities:
                compounds2targets[act['molecule_chembl_id']].add(act['target_chembl_id'])

        # OK, now our dictionary maps from compound ChEMBL IDs into target ChEMBL IDs
        # We would like to replace target ChEMBL IDs with uniprot IDs

        for key, val in compounds2targets.items():
            # We don't know how many targets are assigned to a given compound so again it's
            # better to process targets in chunks:
            lval = list(val)
            genes = set()
            for i in range(0, len(val), chunk_size):
                targets = new_client.target.filter(target_chembl_id__in=lval[i:i + chunk_size])
                for target in targets:
                    for component in target['target_components']:
                        for synonym in component['target_component_synonyms']:
                            if synonym['syn_type'] == "GENE_SYMBOL":
                                genes.add(synonym['component_synonym'])
            compounds2targets[key] = genes

        # Finally write it to the output csv file
        with open('compounds_2_genes.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            for key, val in compounds2targets.items():
                writer.writerow([key] + list(val))      

6. Display a compound image in Jupyter (IPython) notebook:

   ::

      from chembl_webresource_client.new_client import new_client
      Image(new_client.image.get('CHEMBL25'))

   or if the compound doesn't exist in ChEMBL but you have SMILES or molfile:
   
   ::

      from chembl_webresource_client.utils import utils
      Image(utils.smiles2image(smiles))
      
      # or:
      
      Image(utils.ctab2image(molfile))
      
7. Find compounds similar to given SMILES query with similarity threshold of 85%:

   ::

      from chembl_webresource_client.new_client import new_client
      similarity = new_client.similarity
      res = similarity.filter(smiles="CO[C@@H](CCC#C\C=C/CCCC(C)CCCCC=C)C(=O)[O-]", similarity=85)
  
8. Find compounds similar to aspirin (CHEMBL25) with similarity threshold of 70%:

   ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      similarity = new_client.similarity
      aspirin_chembl_id = molecule.search('aspirin')[0]['molecule_chembl_id']
      res = similarity.filter(chembl_id="CHEMBL25", similarity=70)
      
9. Perform substructure search using SMILES:

   ::

      from chembl_webresource_client.new_client import new_client
      substructure = new_client.substructure
      res = substructure.filter(smiles="CN(CCCN)c1cccc2ccccc12")
      
10. Perform substructure search using ChEMBL ID:

   ::

      from chembl_webresource_client.new_client import new_client
      substructure = new_client.substructure
      substructure.filter(chembl_id="CHEMBL25")

11. Get a single molecule by ChEMBL ID:

   ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      m1 = molecule.get('CHEMBL25')

12. Get a single molecule by SMILES:

   ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      m1 = molecule.get('CC(=O)Oc1ccccc1C(=O)O')

13. Get a single molecule by InChi Key:

   ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      molecule.get('BSYNRYMUTXBXSQ-UHFFFAOYSA-N')

14. Get many compounds by their ChEMBL IDs:

    ::

       from chembl_webresource_client.new_client import new_client
       molecule = new_client.molecule
       records = molecule.get(['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505'])

15. Get many compounds by a list of SMILES:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      records = molecule.get(['CNC(=O)c1ccc(cc1)N(CC#C)Cc2ccc3nc(C)nc(O)c3c2',
            'Cc1cc2SC(C)(C)CC(C)(C)c2cc1\\N=C(/S)\\Nc3ccc(cc3)S(=O)(=O)N',
            'CC(C)C[C@H](NC(=O)[C@@H](NC(=O)[C@H](Cc1c[nH]c2ccccc12)NC(=O)[C@H]3CCCN3C(=O)C(CCCCN)CCCCN)C(C)(C)C)C(=O)O'])

16. Get many compounds by a list of InChi Keys:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      records = molecule.get(['XSQLHVPPXBBUPP-UHFFFAOYSA-N', 'JXHVRXRRSSBGPY-UHFFFAOYSA-N', 'TUHYVXGNMOGVMR-GASGPIRDSA-N'])

17. Obtain the pChEMBL value for compound:

    ::

      from chembl_webresource_client.new_client import new_client
      activities = new_client.activity
      res = activities.filter(molecule_chembl_id="CHEMBL25", pchembl_value__isnull=False)
      
18. Obtain the pChEMBL value for a specific compound AND a specific target:

    ::

      from chembl_webresource_client.new_client import new_client
      activities = new_client.activity
      activities.filter(molecule_chembl_id="CHEMBL25", target_chembl_id="CHEMBL612545", pchembl_value__isnull=False)

19. Get all approved drugs:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      approved_drugs = molecule.filter(max_phase=4)
      
20. Get approved drugs for lung cancer:

    ::

      from chembl_webresource_client.new_client import new_client
      drug_indication = new_client.drug_indication
      molecules = new_client.molecule
      lung_cancer_ind = drug_indication.filter(efo_term__icontains="LUNG CARCINOMA")
      lung_cancer_mols = molecules.filter(molecule_chembl_id__in=[x['molecule_chembl_id'] for x in lung_cancer_ind])     

21. Get all molecules in ChEMBL with no Rule-of-Five violations:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      no_violations = molecule.filter(molecule_properties__num_ro5_violations=0)

22. Get all biotherapeutic molecules:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      biotherapeutics = molecule.filter(biotherapeutic__isnull=False)

23. Return molecules with molecular weight <= 300:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      light_molecules = molecule.filter(molecule_properties__mw_freebase__lte=300)
      
24. Return molecules with molecular weight <= 300 AND pref_name ends with nib:

    ::

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      light_nib_molecules = molecule.filter(molecule_properties__mw_freebase__lte=300).filter(pref_name__iendswith="nib")

25. Get all Ki activities related to the hERG target:

    ::

      from chembl_webresource_client.new_client import new_client
      target = new_client.target
      activity = new_client.activity
      herg = target.search('herg')[0]
      herg_activities = activity.filter(target_chembl_id=herg['target_chembl_id']).filter(standard_type="Ki")

26. Get all activitvities related to the Open TG-GATES project:

    ::

      from chembl_webresource_client.new_client import new_client
      activity = new_client.activity
      res = activity.search('"TG-GATES"')
      
27. Get all activitvities for a specific target with assay type 'B' OR 'F':

    ::

      from chembl_webresource_client.new_client import new_client
      activity = new_client.activity
      res = activity.filter(target_chembl_id='CHEMBL3938', assay_type__iregex='(B|F)')  

28. Search for ADMET-reated inhibitor assays:

    ::

      from chembl_webresource_client.new_client import new_client
      assay = new_client.assay
      res = assay.search('inhibitor').filter(assay_type='A')

29. Get cell line by cellosaurus id:

    ::

      from chembl_webresource_client.new_client import new_client
      cell_line = new_client.cell_line
      res = cell_line.filter(cellosaurus_id="CVCL_0417")

30. Filter drugs by approval year and name:

    ::

      from chembl_webresource_client.new_client import new_client
      drug = new_client.drug
      res = drug.filter(first_approval=1976).filter(usan_stem="-azosin")

31. Get tissue by BTO ID:

    ::

      from chembl_webresource_client.new_client import new_client
      tissue = new_client.tissue
      res = tissue.filter(bto_id="BTO:0001073")
      
32. Get tissue by Caloha id:

    ::

      from chembl_webresource_client.new_client import new_client
      tissue = new_client.tissue
      res = tissue.filter(caloha_id="TS-0490")

33. Get tissue by Uberon id:

    ::

      from chembl_webresource_client.new_client import new_client
      tissue = new_client.tissue
      res = tissue.filter(uberon_id="UBERON:0000173")

34. Get tissue by name:

    ::

      from chembl_webresource_client.new_client import new_client
      tissue = new_client.tissue
      res = tissue.filter(pref_name__istartswith='blood')

35. Search documents for 'cytokine':

    ::

      from chembl_webresource_client.new_client import new_client
      document = new_client.document
      res = document.search('cytokine')

36. Search for compound in Unichem:

    ::

      from chembl_webresource_client.new_client import new_client
      ret = unichem.get('AIN')
      
37. Resolve InChi Key to Inchi using Unichem:

    ::

      from chembl_webresource_client.unichem import unichem_client as unichem
      ret = unichem.inchiFromKey('AAOVKJBEBIDNHE-UHFFFAOYSA-N')
      
38. Convert SMILES to CTAB:

    ::

      ffrom chembl_webresource_client.unichem import unichem_client as unichem
      aspirin = utils.smiles2ctab('O=C(Oc1ccccc1C(=O)O)C')

39. Convert SMILES to image and image back to SMILES:

    ::
    
      from chembl_webresource_client.utils import utils
      aspirin = 'CC(=O)Oc1ccccc1C(=O)O'
      im = utils.smiles2image(aspirin)
      mol = utils.image2ctab(im)
      smiles = utils.ctab2smiles(mol).split()[2]
      self.assertEqual(smiles, aspirin)
      
40. Compute fingerprints:

    ::
    
      from chembl_webresource_client.utils import utils
      aspirin = utils.smiles2ctab('O=C(Oc1ccccc1C(=O)O)C')
      fingerprints = utils.sdf2fps(aspirin)
      
41. Compute Maximal Common Substructure:

    ::
    
      from chembl_webresource_client.utils import utils
      smiles = ["O=C(NCc1cc(OC)c(O)cc1)CCCC/C=C/C(C)C", "CC(C)CCCCCC(=O)NCC1=CC(=C(C=C1)O)OC", "c1(C=O)cc(OC)c(O)cc1"]
      mols = [utils.smiles2ctab(smile) for smile in smiles]
      sdf = ''.join(mols)
      result = utils.mcs(sdf)
      
42. Compute various molecular descriptors:

    ::
    
      from chembl_webresource_client.utils import utils
      aspirin = utils.smiles2ctab('O=C(Oc1ccccc1C(=O)O)C')
      num_atoms = json.loads(utils.getNumAtoms(aspirin))[0]
      mol_wt = json.loads(utils.molWt(aspirin))[0]
      log_p = json.loads(utils.logP(aspirin))[0]
      tpsa = json.loads(utils.tpsa(aspirin))[0]
      descriptors = json.loads(utils.descriptors(aspirin))[0]
      
43. Standardize molecule:

    ::
    
      from chembl_webresource_client.utils import utils
      mol = utils.smiles2ctab("[Na]OC(=O)Cc1ccc(C[NH3+])cc1.c1nnn[n-]1.O")
      st = utils.standardise(mol)

Supported formats
-----------------

The following formats are supported:

- JSON (default format):

     ::
    
       from chembl_webresource_client.new_client import new_client
       activity = new_client.activity
       activity.set_format('json')
       activity.all().order_by('assay_type')[0]['activity_id']
      
- XML (you need to parse XML yourself):

    ::
    
      from chembl_webresource_client.new_client import new_client
      activity = new_client.activity
      activity.set_format('xml')
      activity.all().order_by('assay_type')    

- SDF (only for compounds):
  For example you can use the client to save sdf file of a set of compounds and compute 3D coordinates:

    ::
    
      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      molecule.set_format('sdf')

      mols = molecule.filter(molecule_properties__acd_logp__gte=self.logP) \
                       .filter(molecule_properties__aromatic_rings__lte=self.rings_number) \
                       .filter(chirality=self.chirality) \
                       .filter(molecule_properties__full_mwt__lte=self.mwt)

      with open('mols_2D.sdf', 'w') as output:
            for mol in mols:
                output.write(mol)
                output.write('$$$$\n')
                
      with open('mols_3D.sdf', 'w') as output:
            with open('mols_2D.sdf', 'r') as input:
                mols = input.open('r').read().split('$$$$\n')
                for mol in mols:
                    mol_3D = utils.ctab23D(mol)
                    output.write(mol_3D)
                    output.write('$$$$\n')

- FPS (as a result of sdf2fps method)

- PNG, SVG for image randering

    ::
    
      from chembl_webresource_client.new_client import new_client
      image = new_client.image
      image.get('CHEMBL1')


Available data entities
-----------------------

You can list available data entities using the following code:

    ::

      from chembl_webresource_client.new_client import new_client
      available_resources = [resource for resource in dir(new_client) if not resource.startswith('_')]
      print available_resources

At the time of writing this documentation there are 29 entities:

 - activity
 - assay
 - atc_class
 - binding_site
 - biotherapeutic
 - cell_line
 - chembl_id_lookup
 - compound_record
 - compound_structural_alert
 - document
 - document_similarity
 - document_term
 - drug
 - drug_indication
 - go_slim
 - image
 - mechanism
 - metabolism
 - molecule
 - molecule_form
 - protein_class
 - similarity
 - source
 - substructure
 - target
 - target_component
 - target_prediction
 - target_relation
 - tissue

Available filters
-----------------

As was mentioned above the desing of the client is based on Django QuerySet (https://docs.djangoproject.com/en/1.11/ref/models/querysets) and most important lookup types are supported. These are:

 - exact
 - iexact
 - contains
 - icontains
 - in
 - gt
 - gte
 - lt
 - lte
 - startswith
 - istartswith
 - endswith
 - iendswith
 - range
 - isnull
 - regex
 - iregex
 - search (implemented as a method of several selected endpoints instead of a lookup)

Settings
--------------

In order to use settings you need to import them before using the client:

    ::
    
      from chembl_webresource_client.settings import Settings
      
Settings object is a singleton that exposes `Instance` method, for example:

    ::
    
      Settings.Instance().TIMEOUT = 10
      
Most important options:

 - CACHING: should results be cached locally (default is True)
 - CACHE_EXPIRE: cache expiry time in seconds (default 24 hours)
 - CACHE_NAME: name of the .sqlite file with cache
 - TOTAL_RETRIES: number of total retires per HTTP request (default is 3)
 - CONCURRENT_SIZE: total number of concurent requests (default is 50)
 - FAST_SAVE: Speedup cache saving up to 50 times but with possibility of data loss (default is True)

Is that a full functionality?
-----------------------------

No. For more examples, please see the comprehansive test suite (https://github.com/chembl/chembl_webresource_client/blob/master/chembl_webresource_client/tests.py) and dedicated IPython notebook (https://github.com/chembl/mychembl/blob/master/ipython_notebooks/09_myChEMBL_web_services.ipynb)


Citing / Other resources
---------------

There are two papers describing some implementation details of the client library:

- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4489243/
- https://arxiv.org/pdf/1607.00378v1.pdf

There are also two related blog posts:

- http://chembl.blogspot.co.uk/2016/03/chembl-21-web-services-update.html
- http://chembl.blogspot.co.uk/2016/03/this-python-inchi-key-resolver-will.html

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
