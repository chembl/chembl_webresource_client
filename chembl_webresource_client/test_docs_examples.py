from chembl_webresource_client.settings import Settings

Settings.Instance().MAX_LIMIT = 500

import unittest2 as unittest
import json
from chembl_webresource_client.new_client import new_client
from chembl_webresource_client.utils import utils
from chembl_webresource_client.unichem import unichem_client as unichem
from statistics import median


class TestDocsExamples(unittest.TestCase):

    def test_search_molecule_by_synonym(self):
        molecule = new_client.molecule
        molecule.set_format('json')
        res = molecule.search('viagra')
        self.assertEqual(len(res), 2)
        self.assertTrue(
            all([any(['Sildenafil' in y['molecule_synonym'] for y in x['molecule_synonyms']]) for x in res]))

    def test_search_target_by_gene_name(self):
        target = new_client.target
        gene_name = 'BRD4'
        res = target.search(gene_name)
        self.assertEqual(len(res), 2)
        self.assertTrue(all([all(
            [any(['brd4' in z['component_synonym'].lower() for z in y['target_component_synonyms']]) for y in
             x['target_components']]) for x in res]))

    def test_search_gene_name_in_target_synonym(self):
        target = new_client.target
        gene_name = 'GABRB2'
        res = target.filter(target_synonym__icontains=gene_name)
        self.assertEqual(len(res), 14)
        self.assertTrue(all([any(
            [any(['GABRB2' in z['component_synonym'].upper() for z in y['target_component_synonyms']]) for y in
             x['target_components']]) for x in res]))

    def test_chembl_id_to_uniprot(self):
        chembl_ids = ['CHEMBL819', 'CHEMBL820', 'CHEMBL821']
        compounds2targets = dict()

        # First, let's just parse the csv file to extract compounds ChEMBL IDs:
        for chembl_id in chembl_ids:
            compounds2targets[chembl_id] = set()

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
            uniprots = set()
            for i in range(0, len(val), chunk_size):
                targets = new_client.target.filter(target_chembl_id__in=lval[i:i + chunk_size]).only(
                    ['target_components'])
                uniprots |= set(
                    sum([[comp['accession'] for comp in t['target_components']] for t in targets], []))
            compounds2targets[key] = uniprots

        self.assertTrue({'A1E3K9', 'P35695', 'P62593'}.issubset(compounds2targets['CHEMBL819']))
        self.assertTrue('P00811' not in compounds2targets['CHEMBL819'])
        self.assertTrue(len(compounds2targets['CHEMBL819']) == 14)
        self.assertTrue(len(compounds2targets['CHEMBL820']) == 123)
        self.assertTrue(len(compounds2targets['CHEMBL821']) == 13)

    def test_chembl_id_to_uniprot_with_parents(self):
        chembl_ids = ['CHEMBL819', 'CHEMBL820', 'CHEMBL821']
        organism = 'Escherichia coli'
        compounds2targets = dict()
        header = True

        for chembl_id in chembl_ids:
            compounds2targets[chembl_id] = set()

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
                    set(sum([[comp['accession'] for comp in t['target_components']] for t in targets], [])))
            compounds2targets[key] = uniprots

        self.assertTrue('P00811' in compounds2targets['CHEMBL819'])
        self.assertTrue(len(compounds2targets['CHEMBL819']) == 4)
        self.assertTrue(len(compounds2targets['CHEMBL820']) == 0)
        self.assertTrue(len(compounds2targets['CHEMBL821']) == 0)

    def test_chembl_id_to_human_gene_names(self):
        chembl_ids = ['CHEMBL819', 'CHEMBL820', 'CHEMBL821']
        compounds2targets = dict()

        # First, let's just parse the csv file to extract compounds ChEMBL IDs:
        for chembl_id in chembl_ids:
            compounds2targets[chembl_id] = set()

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

        self.assertTrue({'ORF35', 'Pept2', 'Oat1'}.issubset(compounds2targets['CHEMBL819']),
                        compounds2targets['CHEMBL819'])
        self.assertTrue({'B2AR', 'AVPR1', 'UBP41'}.issubset(compounds2targets['CHEMBL820']),
                        compounds2targets['CHEMBL820'])
        self.assertTrue({'OATP1B3', 'OAT3', 'OCT2'}.issubset(compounds2targets['CHEMBL821']),
                        compounds2targets['CHEMBL821'])

    def test_similarity_85(self):

        similarity = new_client.similarity
        res = similarity.filter(smiles="CO[C@@H](CCC#C\C=C/CCCC(C)CCCCC=C)C(=O)[O-]", similarity=85)
        self.assertTrue(len(res) >= 2)
        self.assertTrue(all([float(r['similarity']) >= 80.0 for r in res]))
        self.assertTrue({'CHEMBL478779', 'CHEMBL477888'}.issubset(set([r['molecule_chembl_id'] for r in res])))

    def test_similarity_70(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        similarity = new_client.similarity
        aspirin_chembl_id = molecule.search('aspirin')[0]['molecule_chembl_id']
        res = similarity.filter(chembl_id=aspirin_chembl_id, similarity=70)
        self.assertTrue(len(res) >= 6)
        self.assertTrue(res[0]['similarity'] == '100')
        self.assertTrue(res[0]['molecule_chembl_id'] == 'CHEMBL25')
        self.assertTrue({'CHEMBL163148', 'CHEMBL351485', 'CHEMBL2260706', 'CHEMBL1234172', 'CHEMBL1359634'}.issubset(
            set([r['molecule_chembl_id'] for r in res])))

    def test_smiles_substructure(self):

        substructure = new_client.substructure
        res = substructure.filter(smiles="CN(CCCN)c1cccc2ccccc12")
        self.assertTrue(len(res) > 80)
        self.assertTrue({'CHEMBL442138', 'CHEMBL287955', 'CHEMBL38899', 'CHEMBL53821', 'CHEMBL55826'}.issubset(
            set([r['molecule_chembl_id'] for r in res])))

    def test_chembl_id_substructure(self):

        substructure = new_client.substructure
        res = substructure.filter(chembl_id="CHEMBL25")
        self.assertTrue(len(res) > 380)
        self.assertTrue({'CHEMBL25', 'CHEMBL7666', 'CHEMBL10222', 'CHEMBL10008'}.issubset(
            set([r['molecule_chembl_id'] for r in res])))

    def test_get_by_chembl_id(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        m1 = molecule.get('CHEMBL25')
        self.assertEqual(m1['pref_name'], 'ASPIRIN')
        self.assertEqual(m1['molecule_chembl_id'], 'CHEMBL25')

    def test_get_by_smiles(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        m1 = molecule.get('CC(=O)Oc1ccccc1C(=O)O')
        self.assertEqual(m1['pref_name'], 'ASPIRIN')
        self.assertEqual(m1['molecule_chembl_id'], 'CHEMBL25')

    def test_get_by_smiles_flexmatch(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        res = molecule.filter(molecule_structures__canonical_smiles__flexmatch='CN(C)C(=N)N=C(N)N')
        self.assertEqual(len(res), 6)  # this returns 6 compounds
        self.assertTrue('CHEMBL1431' in [x['molecule_chembl_id'] for x in res])
        self.assertTrue('METFORMIN' in [x['pref_name'] for x in res])

    def test_get_by_inchi_key(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        m1 = molecule.get('BSYNRYMUTXBXSQ-UHFFFAOYSA-N')
        self.assertEqual(m1['pref_name'], 'ASPIRIN')
        self.assertEqual(m1['molecule_chembl_id'], 'CHEMBL25')

    def test_get_multiple_by_chmbl_ids(self):

        mols = ['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505']
        molecule = new_client.molecule
        molecule.set_format('json')
        records = molecule.get(['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505'])
        self.assertEqual(len(records), 3)
        self.assertTrue(len(set([x['molecule_chembl_id'] for x in records]) ^ set(mols)) == 0)

    def test_get_multiple_by_smiles(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        records = molecule.get(['CNC(=O)c1ccc(cc1)N(CC#C)Cc2ccc3nc(C)nc(O)c3c2',
                                'Cc1cc2SC(C)(C)CC(C)(C)c2cc1\\N=C(/S)\\Nc3ccc(cc3)S(=O)(=O)N',
                                'CC(C)C[C@H](NC(=O)[C@@H](NC(=O)[C@H](Cc1c[nH]c2ccccc12)NC'
                                '(=O)[C@H]3CCCN3C(=O)C(CCCCN)CCCCN)C(C)(C)C)C(=O)O'])
        self.assertEqual(len(records), 3)
        self.assertTrue(
            len(set([x['molecule_chembl_id'] for x in records]) ^ set(['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505'])) == 0)

    def test_get_multiple_by_inchi_keys(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        records = molecule.get(['XSQLHVPPXBBUPP-UHFFFAOYSA-N',
                                'JXHVRXRRSSBGPY-UHFFFAOYSA-N', 'TUHYVXGNMOGVMR-GASGPIRDSA-N'])
        self.assertEqual(len(records), 3)
        self.assertTrue(
            len(set([x['molecule_chembl_id'] for x in records]) ^ set(['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505'])) == 0)

    def test_pChembl(self):

        activities = new_client.activity
        res = activities.filter(molecule_chembl_id="CHEMBL25", pchembl_value__isnull=False)
        pchembls = [float(r['pchembl_value']) for r in res]
        self.assertTrue(5.2 < sum(pchembls) / len(pchembls) < 5.3)

    def test_get_pChembl_for_compound_and_target(self):

        activities = new_client.activity
        res = activities.filter(molecule_chembl_id="CHEMBL25", target_chembl_id="CHEMBL612545",
                                pchembl_value__isnull=False)
        pchembls = [float(r['pchembl_value']) for r in res]
        self.assertTrue(4.8 < sum(pchembls) / len(pchembls) < 4.9)

    def test_get_all_approved_drugs(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        approved_drugs = molecule.filter(max_phase=4)
        self.assertTrue(3900 < len(approved_drugs) < 4000)
        self.assertTrue(1.74 < sum(
            [float(d['molecule_properties']['alogp'] or 0) for d in approved_drugs if d['molecule_properties']]) / len(
            approved_drugs) < 1.76)

    def test_get_approved_drugs_for_lung_cancer(self):

        drug_indication = new_client.drug_indication
        molecule = new_client.molecule
        molecule.set_format('json')
        lung_cancer_ind = drug_indication.filter(efo_term__icontains="LUNG CARCINOMA")
        lung_cancer_mols = molecule.filter(
            molecule_chembl_id__in=[x['molecule_chembl_id'] for x in lung_cancer_ind])
        self.assertTrue(210 < len(lung_cancer_mols) < 220)
        self.assertTrue(
            set(['NICOTINE', 'SARACATINIB', 'BEMIPARIN']).issubset(set([l['pref_name'] for l in lung_cancer_mols])))

    def test_get_mols_with_no_ro5_violations(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        no_violations = molecule.filter(molecule_properties__num_ro5_violations=0)
        self.assertTrue(1200000 < len(no_violations) < 1300000)
        self.assertTrue(set(['GEMFIBROZIL', 'ANIROLAC', 'AZEPINDOLE']).issubset(
            set([n['pref_name'] for n in no_violations[:10000]])))

    def test_get_biotherapeutic_molecules(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        biotherapeutics = molecule.filter(biotherapeutic__isnull=False)
        self.assertTrue(21000 < len(biotherapeutics) < 22000)
        self.assertTrue(
            set(['LYPRESSIN', 'USTEKINUMAB', 'APICIDIN']).issubset(set([n['pref_name'] for n in biotherapeutics])))

    def test_get_natural_product_drugs(self):

        molecule = new_client.molecule
        molecule.set_format('sdf')
        natural_drugs = molecule.filter(natural_product=1)
        self.assertTrue(1900 < len(natural_drugs) < 2000)
        b'$$$$'.join([n for n in natural_drugs if n])
        molecule.set_format('json')

    def test_get_all_natural_products(self):

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
        self.assertTrue(34000 < len(natural_products) < 35000)
        self.assertTrue(
            'CC(=O)Oc1ccccc1C(=O)O' in [d['molecule_structures']['canonical_smiles'] for d in natural_products if
                                        d['molecule_structures']])

    def test_get_light_molecules(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        light_molecules = molecule.filter(molecule_properties__mw_freebase__lte=300)
        self.assertTrue(310000 < len(light_molecules) < 320000)
        mean = sum([float(d['molecule_properties']['mw_freebase'] or 0) for d in light_molecules if
                    d['molecule_properties']]) / len(light_molecules)
        self.assertTrue(251 < mean < 252, mean)

    def test_get_light_molecules_ending_with_nib(self):

        molecule = new_client.molecule
        molecule.set_format('json')
        light_nib_molecules = molecule.filter(
            molecule_properties__mw_freebase__lte=300).filter(pref_name__iendswith="nib")
        self.assertEqual(len(light_nib_molecules), 1)
        self.assertEqual('SEMAXANIB', light_nib_molecules[0]['pref_name'])

    def test_get_ki_activities_for_herg(self):

        target = new_client.target
        activity = new_client.activity
        herg = target.search('herg')[0]
        herg_activities = activity.filter(target_chembl_id=herg['target_chembl_id']).filter(standard_type="Ki")
        self.assertTrue(2500 < len(herg_activities) < 3000)
        self.assertTrue(
            5300 < sum([float(x['standard_value'] or 0) for x in herg_activities]) / len(herg_activities) < 5400)

    def test_get_tg_gates_activities(self):

        activity = new_client.activity
        res = activity.search('"TG-GATES"')
        self.assertTrue(150000 < len(res) < 160000)
        mean = sum([float(r['pchembl_value'] or 0) for r in res]) / len(res)
        self.assertEqual(0.0, mean, mean)

    def test_get_b_or_f_type_activities(self):

        activity = new_client.activity
        res = activity.filter(target_chembl_id='CHEMBL3938', assay_type__iregex='(B|F)')
        self.assertTrue(400 < len(res) < 500)
        mean = sum([float(r['pchembl_value'] or 0) for r in res]) / len(res)
        self.assertTrue(0 < mean < 1, mean)

    def test_get_admet_related_inhibitor_assays(self):

        assay = new_client.assay
        res = assay.search('inhibitor').filter(assay_type='A')
        self.assertTrue(1000 < len(res) < 1100)
        self.assertEqual(median([r['confidence_score'] for r in res]), 1)

    def test_get_cell_by_cellosaurus_id(self):

        cell_line = new_client.cell_line
        res = cell_line.filter(cellosaurus_id="CVCL_0417")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['cell_chembl_id'], 'CHEMBL3307686')

    def test_get_drugs_by_approval_year_and_name(self):

        drug = new_client.drug
        res = drug.filter(first_approval=1976).filter(usan_stem="-azosin")
        self.assertEqual(len(res), 1)
        self.assertTrue('Prazosin' in res[0]['synonyms'])

    def test_get_tissue_by_bto_id(self):

        tissue = new_client.tissue
        res = tissue.filter(bto_id="BTO:0001073")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['tissue_chembl_id'], 'CHEMBL3638173')

    def test_get_tissue_by_caloha_id(self):

        tissue = new_client.tissue
        res = tissue.filter(caloha_id="TS-0490")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['tissue_chembl_id'], 'CHEMBL3638176')

    def test_get_tissue_by_uberon_id(self):

        tissue = new_client.tissue
        res = tissue.filter(uberon_id="UBERON:0000173")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['tissue_chembl_id'], 'CHEMBL3638177')

    def test_get_tissue_by_name(self):

        tissue = new_client.tissue
        res = tissue.filter(pref_name__istartswith='blood')
        self.assertTrue(len(res) >= 3)
        self.assertTrue(set(['Blood', 'Blood/Brain', 'Blood/Uterus']).issubset(set([r['pref_name'] for r in res])))

    def test_get_documents_for_cytokine(self):

        document = new_client.document
        res = document.search('cytokine')
        self.assertTrue(300 < len(res) < 400)
        self.assertEqual(median([x['year'] for x in res]), 2010)

    def test_search_compound_in_unichem(self):

        ret = unichem.get('AIN')
        self.assertEqual(len(ret), 1)
        self.assertTrue(set(['aspirin', 'CHEMBL25', 'SCHEMBL1353']).issubset(
            set([x['src_compound_id'] for x in ret[list(ret.keys())[0]]])))

    def test_resolve_inchi_key_to_inchi(self):

        ret = unichem.inchiFromKey('AAOVKJBEBIDNHE-UHFFFAOYSA-N')
        self.assertEqual(ret[0]['standardinchi'],
                         'InChI=1S/C16H13ClN2O/c1-19-14-8-7-12(17)9-13(14)16(18-10-15(19)20)11-5-3-2-4-6-11/h2-9H,10H2,1H3')

    def test_covert_smiles_to_ctab(self):

        aspirin = utils.smiles2ctab('O=C(Oc1ccccc1C(=O)O)C')
        self.assertTrue('V2000' in aspirin)

    def test_convert_smiles_to_image_and_back_to_smiles(self):

        aspirin = 'CC(=O)Oc1ccccc1C(=O)O'
        im = utils.smiles2image(aspirin)
        mol = utils.image2ctab(im)
        smiles = utils.ctab2smiles(mol).split()[2]
        self.assertEqual(smiles[-10:], aspirin[-10:])  # TODO: fix OSRA!

    def test_compute_fingerprints(self):

        aspirin = utils.smiles2ctab('O=C(Oc1ccccc1C(=O)O)C')
        fingerprints = utils.sdf2fps(aspirin)
        self.assertTrue(fingerprints.startswith('#FPS'))

    def test_compute_maximal_common_substructure(self):

        smiles = ["O=C(NCc1cc(OC)c(O)cc1)CCCC/C=C/C(C)C", "CC(C)CCCCCC(=O)NCC1=CC(=C(C=C1)O)OC", "c1(C=O)cc(OC)c(O)cc1"]
        mols = [utils.smiles2ctab(smile) for smile in smiles]
        sdf = ''.join(mols)
        result = utils.mcs(sdf)
        self.assertEqual(result, '[#6]1(-[#6]):[#6]:[#6](-[#8]-[#6]):[#6](:[#6]:[#6]:1)-[#8]')

    def test_compute_molecular_descriptors(self):

        aspirin = utils.smiles2ctab('O=C(Oc1ccccc1C(=O)O)C')

        num_atoms = json.loads(utils.getNumAtoms(aspirin))[0]
        self.assertEqual(num_atoms, 13)

        mol_wt = json.loads(utils.molWt(aspirin))[0]
        self.assertTrue(180 < mol_wt < 181)

        log_p = json.loads(utils.logP(aspirin))[0]
        self.assertTrue(1.31 < log_p < 1.32)

        tpsa = json.loads(utils.tpsa(aspirin))[0]
        self.assertTrue(63 < tpsa < 64)

        descriptors = json.loads(utils.descriptors(aspirin))[0]
        self.assertEqual(descriptors['MolecularFormula'], 'C9H8O4')

    def test_standardise_molecule(self):

        mol = utils.smiles2ctab("[Na]OC(=O)Cc1ccc(C[NH3+])cc1.c1nnn[n-]1.O")
        st = utils.standardise(mol)
        self.assertTrue('V2000' in st)


if __name__ == '__main__':
    unittest.main()
