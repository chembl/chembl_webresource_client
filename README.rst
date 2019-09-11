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

.. image:: http://mybinder.org/badge.svg
    :target: http://beta.mybinder.org/v2/gh/chembl/chembl_webresource_client/master?filepath=demo_wrc.ipynb

======

ChEMBL webresource client
======

This is the only official Python client library developed and supported by `ChEMBL <https://www.ebi.ac.uk/chembl/>`_ group.

The library helps accessing ChEMBL data and cheminformatics tools from Python.
You don't need to know how to write SQL.
You don't need to know how to interact with REST APIs.
You don't need to compile or install any cheminformatics frameworks.
Results are cached.

The client handles interaction with the HTTPS protocol and caches all results in the local file system for faster retrieval.
Abstracting away all network-related tasks, the client provides the end user with a convenient interface, giving the impression of working with a local resource.
Design is based on the Django `QuerySet <https://docs.djangoproject.com/en/1.11/ref/models/querysets/>`_ interface.
The client also implements lazy evaluation of results, which means it will only evaluate a request for data when a value is required.
This approach reduces number of network requests and increases performance.

Installation
------------

.. code-block:: bash

    pip install chembl_webresource_client


Quick start
--------------

Some most frequent use cases below.

#. Search molecule by synonym:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      res = molecule.search('viagra')

#. Search target by gene name:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      target = new_client.target
      gene_name = 'BRD4'
      res = target.search(gene_name)

   or directly in the target synonym field:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      target = new_client.target
      gene_name = 'GABRB2'
      res = target.filter(target_synonym__icontains=gene_name)

#. Having a list of molecules ChEMBL IDs in a CSV file, produce another CSV file that maps every compound ID into a list
   of `Uniprot accession <https://www.uniprot.org/help/accession_numbers>`_ numbers and save the mapping into output CSV file.
   Note the use of the ``only`` operator allowing to specify which fields should be included in the results, making critical API queries faster.

   .. code-block:: python

        import csv
        from chembl_webresource_client.new_client import new_client

        # This will be our resulting structure mapping compound ChEMBL IDs into target uniprot IDs
        compounds2targets = dict()

        # First, let's just parse the csv file to extract compounds ChEMBL IDs:
        with open('compounds_list.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                compounds2targets[row[0]] = set()

        # OK, we have our source IDs, let's process them in chunks:
        chunk_size = 50
        keys = list(compounds2targets.keys()) # for Python 3 we need to convert keys() to list

        for i in range(0, len(keys), chunk_size):
            # we jump from compounds to targets through activities:
            activities = new_client.activity.filter(molecule_chembl_id__in=keys[i:i + chunk_size]).only(
                ['molecule_chembl_id', 'target_chembl_id'])
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
                targets = new_client.target.filter(target_chembl_id__in=lval[i:i + chunk_size]).only(
                    ['target_components'])
                uniprots |= set(
                    sum([[comp['accession'] for comp in t['target_components']] for t in targets],[]))
            compounds2targets[key] = uniprots

        # Finally write it to the output csv file
        with open('compounds_2_targets.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            for key, val in compounds2targets.items():
                writer.writerow([key] + list(val))

#. If you run the example above to get all distinct Uniprot accession for targets related with ``oxacillin`` (CHEMBL819) you will find only 3 targets for ``E.coli`` (``A1E3K9``, ``P35695``, ``P62593``).
   ChEMBL website (https://www.ebi.ac.uk/chembl/compound/inspect/CHEMBL819), on the other hand will show 4 targets (``A1E3K9``, ``P35695``, ``P62593`` and ``P00811``). You may wonder why this discrepancy occurs.
   The ChEMBL interface aggregates data from salts and parent compounds and API just returns the data as they are stored in the database.
   In order to get the same results you will need to add in a call to the molecule_forms endpoint like in the example below, which is taken directly from Marco Galadrini repository (https://github.com/mgalardini/chembl_tools) exposing more useful functions that will soon become a part of the client (https://github.com/chembl/chembl_webresource_client/issues/25).

   .. code-block:: python

    from chembl_webresource_client.new_client import new_client

    organism = 'Escherichia coli'
    compounds2targets = dict()
    header = True
    for name, chembl in [(x.split('\t')[0], x.rstrip().split('\t')[1])
                         for x in open('compounds_list.csv')]:
        if header:
            header = False
            continue
        compounds2targets[chembl] = set()

    chunk_size = 50
    keys = list(compounds2targets.keys())

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
        activities = new_client.activity.filter(molecule_chembl_id__in=values[i:i + chunk_size]).filter(
            target_organism__istartswith=organism).only(['molecule_chembl_id', 'target_chembl_id'])
        for act in activities:
            compounds2targets[forms_to_ID[act['molecule_chembl_id']]].add(act['target_chembl_id'])

    for key, val in compounds2targets.items():
        lval = list(val)
        uniprots = set()
        for i in range(0, len(val), chunk_size):
            targets = new_client.target.filter(target_chembl_id__in=lval[i:i + chunk_size]).only(
                ['target_components'])
            uniprots = uniprots.union(
                set(sum([[comp['accession'] for comp in t['target_components']] for t in targets],[])))
        compounds2targets[key] = uniprots

    print('\t'.join(('chembl', 'target')))
    for chembl in sorted(compounds2targets):
        for uniprot in compounds2targets[chembl]:
            print('\t'.join((chembl, uniprot)))

#. Having a list of molecules ChEMBL IDs in a CSV file, produce another CSV file that maps every compound ID into a list
   of human gene names.
   Again, please note the use of the ``only`` operator which makes API calls faster.

   .. code-block:: python

        import csv
        from chembl_webresource_client.new_client import new_client

        # This will be our resulting structure mapping compound ChEMBL IDs into target uniprot IDs
        compounds2targets = dict()

        # First, let's just parse the csv file to extract compounds ChEMBL IDs:
        with open('compounds_list.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                compounds2targets[row[0]] = set()

        # OK, we have our source IDs, let's process them in chunks:
        chunk_size = 50
        keys = list(compounds2targets.keys())

        for i in range(0, len(keys), chunk_size):
            # we jump from compounds to targets through activities:
            activities = new_client.activity.filter(molecule_chembl_id__in=keys[i:i + chunk_size]).only(
                ['molecule_chembl_id', 'target_chembl_id'])
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
                targets = new_client.target.filter(target_chembl_id__in=lval[i:i + chunk_size]).only(
                    ['target_components'])
                for target in targets:
                    for component in target['target_components']:
                        for synonym in component['target_component_synonyms']:
                            if synonym['syn_type'] == "GENE_SYMBOL":
                                genes.add(synonym['component_synonym'])
            compounds2targets[key] = genes

        # Finally write it to the output csv file
        with open('compounds_2_genes.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            for key, val in compounds2targets.items():
                writer.writerow([key] + list(val))

#. Display a compound image in `Jupyter <http://jupyter.org/>`_ (IPython) notebook:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      Image(new_client.image.get('CHEMBL25'))

   or if the compound doesn't exist in ChEMBL but you have SMILES or molfile:

   .. code-block:: python

      from chembl_webresource_client.utils import utils
      Image(utils.smiles2image(smiles))

      # or:

      Image(utils.ctab2image(molfile))

#. Find compounds similar to given SMILES query with similarity threshold of 85%:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      similarity = new_client.similarity
      res = similarity.filter(smiles="CO[C@@H](CCC#C\C=C/CCCC(C)CCCCC=C)C(=O)[O-]", similarity=85)

#. Find compounds similar to aspirin (CHEMBL25) with similarity threshold of 70%:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      similarity = new_client.similarity
      aspirin_chembl_id = molecule.search('aspirin')[0]['molecule_chembl_id']
      res = similarity.filter(chembl_id=aspirin_chembl_id, similarity=70)

#. **Two similarity search examples above can be slow**.
   This is because by default the ``similarity`` endpoint returns the same information as the ``molecule`` endpoint, which causes many joins on data.
   Often all you need is simply a list of CHEMBL_IDs and maybe a similarity score.
   This is why the API and client support the ``only`` method where you can specify fields you want to be included in response.
   Below is an example of iterating over a large file containing thousands of SMILES strings.
   Each SMILES string from the file is checked against ChEMBL database to see if there are any similar compounds.
   We just need a simple yes/no answer to the question: if there is any compound in ChEMBL that may be considered similar to the given SMILES query.

   .. code-block:: python

        from chembl_webresource_client.new_client import new_client
        similarity_query = new_client.similarity
        dark_smiles = []
        with open('12K_smile_strings.smi') as f:
            content = f.readlines()

        for idx, line in enumerate(content):
            smile = line.strip()
            res = similarity_query.filter(smiles=smile, similarity=70).only(['molecule_chembl_id'])
            print("{0} {1} {2}".format(idx, smile, len(res)))
            if len(res) == 0:
                dark_smiles.append(smile)


   If you also want to know the similarity score, replace ``only(['molecule_chembl_id'])`` with ``only(['molecule_chembl_id', 'similarity'])``.

#. Perform substructure search using SMILES:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      substructure = new_client.substructure
      res = substructure.filter(smiles="CN(CCCN)c1cccc2ccccc12")

#. Perform substructure search using ChEMBL ID:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      substructure = new_client.substructure
      substructure.filter(chembl_id="CHEMBL25")

#. **Two substructure search examples above can be slow**.
   Please use the `only` operator to specify required fields.
   For example this code will be faster then one above:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      substructure = new_client.substructure
      substructure.filter(chembl_id="CHEMBL25").only(['molecule_chembl_id'])

#. Get a single molecule by ChEMBL ID:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      m1 = molecule.get('CHEMBL25')

#. Get a single molecule by SMILES:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      m1 = molecule.get('CC(=O)Oc1ccccc1C(=O)O')

   Please note that using the ``get`` method will perform string-based comparison between the query SMILES and ChEMBL contents.
   Because there are many different canonicalisation algorithms this may not be the optimal way to search for SMILES in ChEMBL.
   This is why we provide a ``flexmatch`` filter that finds compounds described by the query SMILES string regardless of the canonicalisation used.
   Example will look like this:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      res = molecule.filter(molecule_structures__canonical_smiles__flexmatch='CN(C)C(=N)N=C(N)N')
      len(res) # this returns 6 compounds

   Another way would be using similarity or substructure search using SMILES, described in example 7 and 10 respectively.

#. Get a single molecule by InChi Key:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      molecule.get('BSYNRYMUTXBXSQ-UHFFFAOYSA-N')

#. Get many compounds by their ChEMBL IDs:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      records = molecule.get(['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505'])

#. Get many compounds by a list of SMILES:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      records = molecule.get(['CNC(=O)c1ccc(cc1)N(CC#C)Cc2ccc3nc(C)nc(O)c3c2',
            'Cc1cc2SC(C)(C)CC(C)(C)c2cc1\\N=C(/S)\\Nc3ccc(cc3)S(=O)(=O)N',
            'CC(C)C[C@H](NC(=O)[C@@H](NC(=O)[C@H](Cc1c[nH]c2ccccc12)NC' # <- notice lack of coma, we just...
            '(=O)[C@H]3CCCN3C(=O)C(CCCCN)CCCCN)C(C)(C)C)C(=O)O']) # ... broke long SMILE into 2 pieces

#. Get many compounds by a list of InChi Keys:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      records = molecule.get(['XSQLHVPPXBBUPP-UHFFFAOYSA-N',
                              'JXHVRXRRSSBGPY-UHFFFAOYSA-N', 'TUHYVXGNMOGVMR-GASGPIRDSA-N'])

#. Obtain the pChEMBL value for compound:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      activities = new_client.activity
      res = activities.filter(molecule_chembl_id="CHEMBL25", pchembl_value__isnull=False)

#. Obtain the pChEMBL value for a specific compound AND a specific target:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      activities = new_client.activity
      activities.filter(molecule_chembl_id="CHEMBL25", target_chembl_id="CHEMBL612545",
                        pchembl_value__isnull=False)

#. Get all approved drugs:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      approved_drugs = molecule.filter(max_phase=4)

#. Get approved drugs for lung cancer:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      drug_indication = new_client.drug_indication
      molecules = new_client.molecule
      lung_cancer_ind = drug_indication.filter(efo_term__icontains="LUNG CARCINOMA")
      lung_cancer_mols = molecules.filter(
          molecule_chembl_id__in=[x['molecule_chembl_id'] for x in lung_cancer_ind])

#. Get all molecules in ChEMBL with no `Rule-of-Five <https://en.wikipedia.org/wiki/Lipinski%27s_rule_of_five>`_ violations:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      no_violations = molecule.filter(molecule_properties__num_ro5_violations=0)

#. Get all biotherapeutic molecules:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      biotherapeutics = molecule.filter(biotherapeutic__isnull=False)

#. Get all natural products:

   The `molecule` resource has a ``natural_product`` flag but it's only set for approved drugs.
   So if you want an sdf file with approved drugs being natural products you can simply use this URL:

   https://www.ebi.ac.uk/chembl/api/data/molecule.sdf?natural_product=1

   Which can be translated into the following client code:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      molecule.set_format('sdf')
      molecule.filter(natural_product=1)

   If you want to retrieve all the natural products compounds regardless it they are approved drugs or not, you can fetch all compounds extracted from the `Journal of Natural Products <http://pubs.acs.org/journal/jnprdf>`_.
   Using the client you will write a following code:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      document = new_client.document
      docs = document.filter(journal="J. Nat. Prod.").only('document_chembl_id')
      compound_record = new_client.compound_record
      records = compound_record.filter(
          document_chembl_id__in=[doc['document_chembl_id'] for doc in docs]).only(
          ['document_chembl_id', 'molecule_chembl_id'])
      molecule = new_client.molecule
      natural_products = molecule.filter(
          molecule_chembl_id__in=[rec['molecule_chembl_id'] for rec in records]).only(
          'molecule_structures')

#. Return molecules with molecular weight <= 300:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      light_molecules = molecule.filter(molecule_properties__mw_freebase__lte=300)

#. Return molecules with molecular weight <= 300 AND ``pref_name`` ending with ``nib``:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      molecule = new_client.molecule
      light_nib_molecules = molecule.filter(
          molecule_properties__mw_freebase__lte=300).filter(pref_name__iendswith="nib")

#. Get all ``Ki`` activities related to the ``hERG`` target:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      target = new_client.target
      activity = new_client.activity
      herg = target.search('herg')[0]
      herg_activities = activity.filter(target_chembl_id=herg['target_chembl_id']).filter(standard_type="Ki")

#. Get all activities related to the ``Open TG-GATES`` project:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      activity = new_client.activity
      res = activity.search('"TG-GATES"')

#. Get all activities for a specific target with assay type ``B`` (Binding) OR ``F`` (Functional):

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      activity = new_client.activity
      res = activity.filter(target_chembl_id='CHEMBL3938', assay_type__iregex='(B|F)')

#. Search for ADMET-related inhibitor assays (type ``A``):

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      assay = new_client.assay
      res = assay.search('inhibitor').filter(assay_type='A')

#. Get cell line by cellosaurus id:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      cell_line = new_client.cell_line
      res = cell_line.filter(cellosaurus_id="CVCL_0417")

#. Filter drugs by approval year and name:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      drug = new_client.drug
      res = drug.filter(first_approval=1976).filter(usan_stem="-azosin")

#. Get tissue by BTO ID:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      tissue = new_client.tissue
      res = tissue.filter(bto_id="BTO:0001073")

#. Get tissue by Caloha id:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      tissue = new_client.tissue
      res = tissue.filter(caloha_id="TS-0490")

#. Get tissue by Uberon id:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      tissue = new_client.tissue
      res = tissue.filter(uberon_id="UBERON:0000173")

#. Get tissue by name:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      tissue = new_client.tissue
      res = tissue.filter(pref_name__istartswith='blood')

#. Search documents for ``cytokine``:

   .. code-block:: python

      from chembl_webresource_client.new_client import new_client
      document = new_client.document
      res = document.search('cytokine')

#. Search for compound in `Unichem <https://www.ebi.ac.uk/unichem/>`_:

   .. code-block:: python

      from chembl_webresource_client.unichem import unichem_client as unichem
      ret = unichem.get('AIN')

#. Resolve InChi Key to Inchi using Unichem:

   .. code-block:: python

      from chembl_webresource_client.unichem import unichem_client as unichem
      ret = unichem.inchiFromKey('AAOVKJBEBIDNHE-UHFFFAOYSA-N')

#. Convert SMILES to CTAB:

   .. code-block:: python

      from chembl_webresource_client.utils import utils
      aspirin = utils.smiles2ctab('O=C(Oc1ccccc1C(=O)O)C')

#. Convert SMILES to image and image back to SMILES:

   .. code-block:: python

      from chembl_webresource_client.utils import utils
      aspirin = 'CC(=O)Oc1ccccc1C(=O)O'
      im = utils.smiles2image(aspirin)
      mol = utils.image2ctab(im)
      smiles = utils.ctab2smiles(mol).split()[2]
      self.assertEqual(smiles, aspirin)

#. Compute fingerprints:

   .. code-block:: python

      from chembl_webresource_client.utils import utils
      aspirin = utils.smiles2ctab('O=C(Oc1ccccc1C(=O)O)C')
      fingerprints = utils.sdf2fps(aspirin)

#. Compute Maximal Common Substructure:

   .. code-block:: python

      from chembl_webresource_client.utils import utils
      smiles = ["O=C(NCc1cc(OC)c(O)cc1)CCCC/C=C/C(C)C",
                "CC(C)CCCCCC(=O)NCC1=CC(=C(C=C1)O)OC", "c1(C=O)cc(OC)c(O)cc1"]
      mols = [utils.smiles2ctab(smile) for smile in smiles]
      sdf = ''.join(mols)
      result = utils.mcs(sdf)

#. Compute various molecular descriptors:

   .. code-block:: python

      from chembl_webresource_client.utils import utils
      aspirin = utils.smiles2ctab('O=C(Oc1ccccc1C(=O)O)C')
      num_atoms = json.loads(utils.getNumAtoms(aspirin))[0]
      mol_wt = json.loads(utils.molWt(aspirin))[0]
      log_p = json.loads(utils.logP(aspirin))[0]
      tpsa = json.loads(utils.tpsa(aspirin))[0]
      descriptors = json.loads(utils.descriptors(aspirin))[0]

#. Standardize molecule:

   .. code-block:: python

      from chembl_webresource_client.utils import utils
      mol = utils.smiles2ctab("[Na]OC(=O)Cc1ccc(C[NH3+])cc1.c1nnn[n-]1.O")
      st = utils.standardise(mol)

Supported formats
-----------------

The following formats are supported:

- JSON (default format):

  .. code-block:: python

     from chembl_webresource_client.new_client import new_client
     activity = new_client.activity
     activity.set_format('json')
     activity.all().order_by('assay_type')[0]['activity_id']

- XML (you need to parse XML yourself):

  .. code-block:: python

     from chembl_webresource_client.new_client import new_client
     activity = new_client.activity
     activity.set_format('xml')
     activity.all().order_by('assay_type')

- SDF (only for compounds):
  For example you can use the client to save sdf file of a set of compounds and compute 3D coordinates:

  .. code-block:: python

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

- PNG, SVG for image rendering

  .. code-block:: python

     from chembl_webresource_client.new_client import new_client
     image = new_client.image
     image.get('CHEMBL1')


Available data entities
-----------------------

You can list available data entities using the following code:

.. code-block:: python

   from chembl_webresource_client.new_client import new_client
   available_resources = [resource for resource in dir(new_client) if not resource.startswith('_')]
   print available_resources

At the time of writing this documentation there are 30 entities:

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
- drug
- drug_indication
- go_slim
- image
- mechanism
- metabolism
- molecule
- molecule_form
- organism
- protein_class
- similarity
- source
- substructure
- target
- target_component
- target_prediction
- target_relation
- tissue
- xref_source

Available filters
-----------------

As was mentioned above the design of the client is based on Django QuerySet (https://docs.djangoproject.com/en/1.11/ref/models/querysets) and most important lookup types are supported.
These are:

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

``Only`` operator
-----------------

``only`` is a special method allowing to limit the results to a selected set of fields.
``only`` should take a single argument: a list of fields that should be included in result.
Specified fields have to exists in the endpoint against which ``only`` is executed.
Using ``only`` will usually make an API call faster because less information returned will save bandwidth.
The API logic will also check if any SQL joins are necessary to return the specified field and exclude unnecessary joins with critically improves performance.

Please note that ``only`` has one limitation: a list of fields will ignore nested fields i.e. calling ``only(['molecule_properties__alogp'])`` is equivalent to ``only(['molecule_properties'])``.

For many 2 many relationships ``only`` will not make any SQL join optimisation.

Settings
--------------

In order to use settings you need to import them before using the client:

.. code-block:: python

   from chembl_webresource_client.settings import Settings

Settings object is a singleton that exposes `Instance` method, for example:

.. code-block:: python

   Settings.Instance().TIMEOUT = 10

Most important options:

- CACHING: should results be cached locally (default is True)
- CACHE_EXPIRE: cache expiry time in seconds (default 24 hours)
- CACHE_NAME: name of the .sqlite file with cache
- TOTAL_RETRIES: number of total retires per HTTP request (default is 3)
- CONCURRENT_SIZE: total number of concurrent requests (default is 50)
- FAST_SAVE: Speedup cache saving up to 50 times but with possibility of data loss (default is True)

Is that a full functionality?
-----------------------------

No.
For more examples, please see the Binder notebook link on top of this file.


Citing / Other resources
---------------

There are two papers describing some implementation details of the client library:

- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4489243/
- https://arxiv.org/pdf/1607.00378v1.pdf

There are also two related blog posts:

- http://chembl.blogspot.co.uk/2016/03/chembl-21-web-services-update.html
- http://chembl.blogspot.co.uk/2016/03/this-python-inchi-key-resolver-will.html
