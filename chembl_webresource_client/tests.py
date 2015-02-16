__author__ = 'mnowotka'

from xml.dom.minidom import parseString
from chembl_webresource_client.settings import Settings
from chembl_webresource_client import *
from chembl_webresource_client.utils import utils
from chembl_webresource_client.new_client import new_client
import json
import unittest
import pytest
import logging
from random import randint
logging.basicConfig()

TIMEOUT = Settings.Instance().TEST_CASE_TIMEOUT

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        Settings.Instance().WEBSERVICE_PROTOCOL = 'https'
        Settings.Instance().WEBSERVICE_DOMAIN = 'www.ebi.ac.uk'
        Settings.Instance().WEBSERVICE_PREFIX = '/chemblws'
        Settings.Instance().TIMEOUT = 10

    def test_assays(self):
        assays = AssayResource()
        self.assertTrue(assays.status())
        self.assertEqual(assays.get('CHEMBL1217643')['assayOrganism'], 'Homo sapiens')
        self.assertEqual(len(assays.get(['CHEMBL1217643', 'CHEMBL1217644'])), 2)
        self.assertEqual(len(assays.bioactivities('CHEMBL1217643')), 1)

    def test_targets(self):
        targets = TargetResource()
        self.assertTrue(targets.status())
        self.assertEqual(targets.get('CHEMBL2476')['targetType'], 'SINGLE PROTEIN')
        self.assertTrue(len(targets.bioactivities('CHEMBL240')) > 10000)
        all = targets.get_all()
        self.assertTrue(len(all) > 10000)
        self.assertTrue(all[0]['bioactivityCount'] >= all[-1]['bioactivityCount'])
        self.assertEqual(targets.get(uniprot='Q13936')['proteinAccession'], 'Q13936')
        self.assertEqual(len(targets.get(['CHEMBL240', 'CHEMBL1927'])), 2)
        self.assertEqual(len(targets.approved_drugs('CHEMBL1824')),5)
        self.assertEqual(targets.approved_drugs('CHEMBL1824')[1]['name'], 'PERTUZUMAB')

    def test_compounds(self):
        compounds = CompoundResource()
        self.assertTrue(compounds.status())
        self.assertEqual(compounds.get('CHEMBL1')['stdInChiKey'], 'GHBOEFUAGSHXPO-XZOTUCIWSA-N')
        self.assertEqual(len(compounds.get(['CHEMBL%s' % x for x in range(1,6)])), 5)
        self.assertEqual(len(compounds.get(['CHEMBL%s' % x for x in range(1,301)])), 300)
        self.assertEqual(compounds.get(stdinchikey='QFFGVLORLPOAEC-SNVBAGLBSA-N')['molecularFormula'], 'C19H21ClFN3O3')
        self.assertEqual(compounds.get(smiles='COc1ccc2[C@@H]3[C@H](COc2c1)C(C)(C)OC4=C3C(=O)C(=O)C5=C4OC(C)(C)[C@@H]6COc7cc(OC)ccc7[C@H]56')[0]['stdInChiKey'], 'GHBOEFUAGSHXPO-UWXQAFAOSA-N')
        cs = compounds.get(smiles="C\C(=C\C(=O)O)\C=C\C=C(/C)\C=C\C1=C(C)CCCC1(C)C")
        self.assertTrue(len(cs) >= 9)
        self.assertTrue('ISOTRETINOIN' in [c['preferredCompoundName'] for c in cs])
        cs = compounds.get(smiles="COC1(CN2CCC1CC2)C#CC(C#N)(c3ccccc3)c4ccccc4")
        self.assertEqual(len(cs), 1)
        self.assertEqual(cs[0]['stdInChiKey'], 'MMAOIAFUZKMAOY-UHFFFAOYSA-N')
        self.assertEqual(len(cs), 1)
        cs = compounds.get(smiles="CN1C\C(=C/c2ccc(C)cc2)\C3=C(C1)C(C(=C(N)O3)C#N)c4ccc(C)cc4")
        self.assertEqual(cs[0]['chemblId'], 'CHEMBL319317')
        self.assertTrue(len(compounds.similar_to('COc1ccc2[C@@H]3[C@H](COc2c1)C(C)(C)OC4=C3C(=O)C(=O)C5=C4OC(C)(C)[C@@H]6COc7cc(OC)ccc7[C@H]56', 70)) > 800)
        self.assertTrue(len(compounds.similar_to('C\C(=C/C=C/C(=C/C(=O)O)/C)\C=C\C1=C(C)CCCC1(C)C', 70)) > 200)
        self.assertTrue(len(compounds.substructure('COcccc')) > 6000)
        self.assertTrue(len(compounds.substructure('C\C(=C/C=C/C(=C/C(=O)O)/C)\C=C\C1=C(C)CCCC1(C)C')) >= 100)
        self.assertTrue(len(compounds.bioactivities('CHEMBL1')) > 10)
        self.assertEqual(len(compounds.forms('CHEMBL415863')), 2)
        self.assertEqual(set(map(lambda x: x['chemblId'],compounds.forms('CHEMBL415863'))),
                         {'CHEMBL415863', 'CHEMBL1207563'})
        self.assertEqual(len(compounds.forms('CHEMBL1207563')), 2)
        self.assertEqual(set(map(lambda x: x['chemblId'],compounds.forms('CHEMBL1207563'))),
                         {'CHEMBL415863', 'CHEMBL1207563'})
        self.assertEqual(len(compounds.forms('CHEMBL1078826')), 17)
        self.assertEqual(len(compounds.drug_mechanisms('CHEMBL1642')), 3)
        self.assertTrue('Stem cell growth factor receptor' in [comp['name'] for
                                                               comp in compounds.drug_mechanisms('CHEMBL1642')])

    @pytest.mark.timeout(TIMEOUT)
    def test_activity_resource(self):
        activity = new_client.activity
        count = len(activity.all())
        self.assertTrue(count)
        self.assertTrue(activity.filter(standard_type="Log Ki").filter(standard_value__gte=5).exists())
        self.assertTrue(activity.filter(target_chembl_id="CHEMBL333").exists())
        self.assertTrue('c' in activity.get(66369)['canonical_smiles'])
        self.assertEquals([act['activity_id'] for act in activity.all().order_by('activity_id')[0:5]],
            [31863, 31864, 31865, 31866, 31867])
        random_index = 11000 #randint(0, count - 1) - too slow!
        random_elem = activity.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('activity_comment', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('activity_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_description', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('bao_endpoint', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('canonical_smiles', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('data_validity_comment', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('document_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('document_journal', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('document_year', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('pchembl_value', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('potential_duplicate', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('published_relation', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('published_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('published_units', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('published_value', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('qudt_units', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('record_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('standard_flag', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('standard_relation', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('standard_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('standard_units', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('standard_value', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('target_pref_name', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('target_organism', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('uo_units', random_elem, 'One of required fields not found in resource %s' % random_elem)
        activity.set_format('xml')
        parseString(activity.all()[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_assay_resource(self):
        assay = new_client.assay
        count = len(assay.all())
        self.assertTrue(count)
        self.assertTrue(assay.filter(assay_oragism="Sus scrofa").filter(assay_type="B").exists())
        self.assertEqual( [ass['bao_format'] for ass in assay.get(['CHEMBL615111', 'CHEMBL615112', 'CHEMBL615113'])],
        [u'BAO_0000019', u'BAO_0000019', u'BAO_0000019'])
        random_index = randint(0, count - 1)
        random_elem = assay.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('assay_category', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_cell_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_organism', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_strain', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_subcellular_fraction', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_tax_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_test_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_tissue', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('assay_type_description', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('bao_format', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('cell_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('confidence_description', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('confidence_score', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('description', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('document_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('relationship_description', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('relationship_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('src_assay_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('src_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('target_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        assay.set_format('xml')
        parseString(assay.filter(confidence_score__gte=8)[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_atc_class_resource(self):
        atc_class = new_client.atc_class
        count = len(atc_class.all())
        self.assertTrue(count)
        self.assertTrue(len(atc_class.filter(level1="H")) >= len(atc_class.filter(level2="H03")) >=
                        len(atc_class.filter(level3="H03A")) >= len(atc_class.filter(level4="H03AA")) >=
                        len(atc_class.filter(level5="H03AA03")))
        self.assertEquals(atc_class.get('H03AA03')['who_name'], 'combinations of levothyroxine and liothyronine')
        self.assertEquals([atc['level5'] for atc in atc_class.all().order_by('level5')[0:5]],
            [u'A01AA01', u'A01AA02', u'A01AA03', u'A01AA04', u'A01AA30'])
        random_index = randint(0, count - 1)
        random_elem = atc_class.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('level1', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('level2', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('level3', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('level4', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('level5', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('who_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('who_name', random_elem, 'One of required fields not found in resource %s' % random_elem)
        atc_class.set_format('xml')
        parseString(atc_class.filter(level1="G")[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_binding_site_resource(self):
        binding_site = new_client.binding_site
        count = len(binding_site.all())
        self.assertTrue(count)
        self.assertTrue('site_name' in binding_site.all()[0])
        self.assertEquals([site['site_components'][0]['domain']['domain_type'] for site in
                           binding_site.get([962, 963, 943])], [u'Pfam-A', u'Pfam-A', u'Pfam-A'])
        self.assertEquals([bind['site_id'] for bind in binding_site.all().order_by('site_id')[0:5]],
            [1, 2, 3, 4, 5])
        random_index = randint(0, count - 1)
        random_elem = binding_site.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('site_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('site_name', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('site_components', random_elem, 'One of required fields not found in resource %s' % random_elem)
        binding_site.set_format('xml')
        parseString(binding_site.get(1))

    @pytest.mark.timeout(TIMEOUT)
    def test_biocomponent_resource(self):
        biocomponent = new_client.biocomponent
        count = len(biocomponent.all())
        self.assertTrue(count)
        self.assertTrue(biocomponent.filter(component_type="PROTEIN").filter(organism="Homo sapiens").exists())
        self.assertTrue(all([l > 100 for l in [len(comp['sequence']) for comp in
                                                    biocomponent.get([6451, 6452, 6453])]]))
        self.assertEquals([biocomp['component_id'] for biocomp in biocomponent.all().order_by('component_id')[0:5]],
            [6287, 6288, 6289, 6290, 6291])
        random_index = randint(0, count - 1)
        random_elem = biocomponent.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('component_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('component_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('description', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('sequence', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('tax_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('organism', random_elem, 'One of required fields not found in resource %s' % random_elem)
        biocomponent.set_format('xml')
        parseString(biocomponent.filter(tax_id=9606)[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_cell_line_resource(self):
        cell_line = new_client.cell_line
        count = len(cell_line.all())
        self.assertTrue(count)
        self.assertTrue(cell_line.filter(cell_name__startswith="MDA").exists())
        self.assertTrue('efo_id' in cell_line.get(1))
        self.assertEqual([cell['cell_id'] for cell in cell_line.all().order_by('cell_id')[0:5]],
            [1, 2, 3, 4, 5])
        self.assertEqual([cell['cell_id'] for cell in cell_line.get(['CHEMBL3307242','CHEMBL3307243'])],
            [cell['cell_id'] for cell in cell_line.get([2,3])])
        self.assertEqual([cell['cell_id'] for cell in cell_line.get(cell_chembl_id=['CHEMBL3307242','CHEMBL3307243'])],
            [cell['cell_id'] for cell in cell_line.get(cell_id=[2,3])])
        random_index = randint(0, count - 1)
        random_elem = cell_line.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('cell_description', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('cell_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('cell_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('cell_name', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('cell_source_organism', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('cell_source_tax_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('cell_source_tissue', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('cellosaurus_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('clo_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('efo_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        cell_line.set_format('xml')
        parseString(cell_line.filter(cellosaurus_id="CVCL_0417")[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_document_resource(self):
        document = new_client.document
        count = len(document.all())
        self.assertTrue(count)
        self.assertTrue(document.filter(doc_type='PUBLICATION').filter(year__gt=1985).filter(volume=5).exists())
        self.assertTrue(all([page[0] < page[1] for page in [(doc['first_page'], doc['last_page']) for doc in
                                                document.get(['CHEMBL1121361', 'CHEMBL1121362', 'CHEMBL1121364'])]]))
        random_index = randint(0, count - 1)
        random_elem = document.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('abstract', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('authors', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('doc_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('document_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('doi', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('first_page', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('issue', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('journal', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('last_page', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('pubmed_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('title', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('volume', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('year', random_elem, 'One of required fields not found in resource %s' % random_elem)
        document.set_format('xml')
        parseString(document.filter(journal="J. Med. Chem.")[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_image_resource(self):
        image = new_client.image
        self.assertTrue(image.get('CHEMBL1').startswith('\x89PNG\r\n'))

    @pytest.mark.timeout(TIMEOUT)
    def test_mechanism_resource(self):
        mechanism = new_client.mechanism
        count = len(mechanism.all())
        self.assertTrue(count)
        self.assertTrue(mechanism.filter(action_type="ANTAGONIST")
            .filter(direct_interaction=True)
            .filter(disease_efficacy=True)
            .exists())
        self.assertTrue('mechanism_of_action' in mechanism.get(662))
        self.assertEqual([mec['mec_id'] for mec in mechanism.all().order_by('mec_id')[0:5]],
            [13, 14, 15, 16, 17])
        random_index = randint(0, count - 1)
        random_elem = mechanism.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('action_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('binding_site_comment', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('direct_interaction', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('disease_efficacy', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('mec_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('mechanism_comment', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('mechanism_of_action', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecular_mechanism', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('record_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('selectivity_comment', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('site_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('target_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        mechanism.set_format('xml')
        parseString(mechanism.filter(moleculer_mechanism=True)[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_molecule_resource(self):
        molecule = new_client.molecule
        count = len(molecule.all())
        self.assertTrue(count)
        self.assertTrue(molecule.filter(molecule_properties__acd_logp__gte=1.9)
                                .filter(molecule_properties__aromatic_rings__lte=3)
                                .filter(chirality=(-1))
                                .exists())
        range = molecule.filter(molecule_properties__full_mwt__range=[200,201])
        self.assertTrue(range.exists())
        self.assertTrue(700 < len(range) < 800)
        ids_from_ids_no_name = set(map(lambda x: x['molecule_chembl_id'],
                                                        molecule.get(['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505'])))
        ids_from_ids_by_name = set(map(lambda x: x['molecule_chembl_id'],
                                        molecule.get(molecule_chembl_id=['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505'])))
        ids_from_keys_no_name = set(map(lambda x: x['molecule_chembl_id'],
            molecule.get(['XSQLHVPPXBBUPP-UHFFFAOYSA-N', 'JXHVRXRRSSBGPY-UHFFFAOYSA-N', 'TUHYVXGNMOGVMR-GASGPIRDSA-N'])))
        ids_from_keys_by_name = set(map(lambda x: x['molecule_chembl_id'],
            molecule.get(molecule_structures__standard_inchi_key=['XSQLHVPPXBBUPP-UHFFFAOYSA-N',
                                                        'JXHVRXRRSSBGPY-UHFFFAOYSA-N', 'TUHYVXGNMOGVMR-GASGPIRDSA-N'])))
        ids_from_smiles_no_name = set(map(lambda x: x['molecule_chembl_id'],
            molecule.get(['CNC(=O)c1ccc(cc1)N(CC#C)Cc2ccc3nc(C)nc(O)c3c2',
            'Cc1cc2SC(C)(C)CC(C)(C)c2cc1\\N=C(/S)\\Nc3ccc(cc3)S(=O)(=O)N',
            'CC(C)C[C@H](NC(=O)[C@@H](NC(=O)[C@H](Cc1c[nH]c2ccccc12)NC(=O)[C@H]3CCCN3C(=O)C(CCCCN)CCCCN)C(C)(C)C)C(=O)O'])))
        ids_from_smiles_by_name = set(map(lambda x: x['molecule_chembl_id'],
            molecule.get(molecule_structures__canonical_smiles=['CNC(=O)c1ccc(cc1)N(CC#C)Cc2ccc3nc(C)nc(O)c3c2',
            'Cc1cc2SC(C)(C)CC(C)(C)c2cc1\\N=C(/S)\\Nc3ccc(cc3)S(=O)(=O)N',
            'CC(C)C[C@H](NC(=O)[C@@H](NC(=O)[C@H](Cc1c[nH]c2ccccc12)NC(=O)[C@H]3CCCN3C(=O)C(CCCCN)CCCCN)C(C)(C)C)C(=O)O'])))

        self.assertEquals(ids_from_ids_no_name, ids_from_ids_by_name)
        self.assertEquals(ids_from_ids_by_name, ids_from_keys_no_name)
        self.assertEquals(ids_from_keys_no_name, ids_from_keys_by_name)
        self.assertEquals(ids_from_keys_by_name, ids_from_smiles_no_name)
        self.assertEquals(ids_from_smiles_no_name, ids_from_smiles_by_name)
        with_components = molecule.get('CHEMBL1743070')
        self.assertIsNotNone(with_components)
        self.assertTrue(len(with_components['biocomponents']))
        component = with_components['biocomponents'][0]
        self.assertIn("component_id", component)
        self.assertIn("component_type", component)
        self.assertIn("description", component)
        self.assertIn("organism", component)
        self.assertIn("sequence", component)
        self.assertIn("tax_id", component)
        random_index = randint(0, count - 1)
        random_elem = molecule.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('atc_classifications', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('availability_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('biotherapeutic', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('black_box_warning', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('chebi_par_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('chirality', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('dosed_ingredient', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('first_approval', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('first_in_class', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('helm_notation', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('indication_class', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('inorganic_flag', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('max_phase', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_hierarchy', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_properties', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_structures', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('natural_product', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('oral', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('parenteral', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('polymer_flag', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('pref_name', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('prodrug', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('structure_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('therapeutic_flag', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('topical', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_stem', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_stem_definition', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_substem', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_year', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertEqual(len(molecule.get('CHEMBL1475')['atc_classifications']),2)
        self.assertTrue(molecule.filter(atc_classifications__level5='C07AB01').exists())
        self.assertEqual(len(molecule.filter(atc_classifications__level5='C07AB01')), 1)
        self.assertTrue(molecule.filter(atc_classifications__level5__startswith='A10').exists())
        self.assertEqual(len(molecule.filter(atc_classifications__level5__startswith='A10')),
            len(set([mol['molecule_chembl_id'] for
                     mol in molecule.filter(atc_classifications__level5__startswith='A10')])))
        atc_query = ['CHEMBL1073','CHEMBL1201496']
        molecules = new_client.molecule.get(atc_query)
        self.assertEqual(len(molecules),2)
        longest_chembl_smiles = "CC.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC1OC(CO)C(O)C(O)C1O)C(O)CO.CCCCCCCCCCCCCCCC" \
                                "[NH2+]OC(CO)C(O)C(OC2OC(CO)C(O)C(O)C2O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(O" \
                                "C3OC(CO)C(O)C(O)C3O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC4OC(CO)C(O)C(O)C4O" \
                                ")C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC5OC(CO)C(O)C(O)C5O)C(O)CO.CCCCCCCCCCC" \
                                "CCCCC[NH2+]OC(CO)C(O)C(OC6OC(CO)C(O)C(O)C6O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(" \
                                "O)C(OC7OC(CO)C(O)C(O)C7O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC8OC(CO)C(O)C(" \
                                "O)C8O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC9OC(CO)C(O)C(O)C9O)C(O)CO.CCCCCC" \
                                "CCCCCCCCCC[NH2+]OC(CO)C(O)C(OC%10OC(CO)C(O)C(O)C%10O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+" \
                                "]OC(CO)C(O)C(OC%11OC(CO)C(O)C(O)C%11O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC" \
                                "%12OC(CO)C(O)C(O)C%12O)C(O)CO.CCCCCCCCCC(C(=O)NCCc%13ccc(OP(=S)(Oc%14ccc(CCNC(=O)" \
                                "C(CCCCCCCCC)P(=O)(O)[O-])cc%14)N(C)\N=C\c%15ccc(Op%16(Oc%17ccc(\C=N\N(C)P(=S)(Oc%" \
                                "18ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%18)Oc%19ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O" \
                                ")[O-])cc%19)cc%17)np(Oc%20ccc(\C=N\N(C)P(=S)(Oc%21ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O" \
                                ")[O-])cc%21)Oc%22ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%22)cc%20)(Oc%23ccc(\C=N" \
                                "\N(C)P(=S)(Oc%24ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%24)Oc%25ccc(CCNC(=O)C(CCC" \
                                "CCCCCC)P(=O)(O)[O-])cc%25)cc%23)np(Oc%26ccc(\C=N\N(C)P(=S)(Oc%27ccc(CCNC(=O)C(CCC" \
                                "CCCCCC)P(=O)(O)[O-])cc%27)Oc%28ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%28)cc%26)(" \
                                "Oc%29ccc(\C=N\N(C)P(=S)(Oc%30ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%30)Oc%31ccc(" \
                                "CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%31)cc%29)n%16)cc%15)cc%13)P(=O)(O)[O-]"

        res_1 = molecule.get(longest_chembl_smiles)
        self.assertEqual(res_1['molecule_chembl_id'], 'CHEMBL1172371')
        res_2 = molecule.filter(molecule_structures__canonical_smiles=longest_chembl_smiles)
        self.assertEqual(len(res_2), 1)
        self.assertEqual(res_1, res_2[0])
        res_3 = molecule.get(molecule_structures__canonical_smiles=longest_chembl_smiles)
        self.assertEqual(res_1, res_3[0])

        molecule.set_format('xml')
        parseString(molecule.filter(molecule_properties__full_mwt__gt=600)
                            .filter(molecule_properties__aromatic_rings=4)
                            .filter(oral=True)[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_molecule_form_resource(self):
        molecule_form = new_client.molecule_form
        count = len(molecule_form.all())
        self.assertTrue(count)
        self.assertTrue(all([form['parent'] == 'True' for form in
                             molecule_form.get(['CHEMBL328730', 'CHEMBL80863', 'CHEMBL80176'])]))
        self.assertEquals(len(molecule_form.get(molecule_chembl_id=['CHEMBL328730', 'CHEMBL80863', 'CHEMBL80176'])), 3)
        random_index = randint(0, count - 1)
        random_elem = molecule_form.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('parent', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        known_forms = molecule_form.get('CHEMBL211471')
        self.assertEqual(len(known_forms['molecule_forms']), 3)
        self.assertEqual(set([form['molecule_chembl_id'] for form in known_forms['molecule_forms']]),
                                                                set(["CHEMBL54126", "CHEMBL278020", "CHEMBL211471"]))
        self.assertTrue(any(form['parent'] == 'True' for form in known_forms['molecule_forms']))
        molecule_form.set_format('xml')
        parseString(molecule_form.all()[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_protein_class_resource(self):
        protein_class = new_client.protein_class
        count = len(protein_class.all())
        self.assertTrue(count)
        self.assertTrue(len(protein_class.filter(l1="Enzyme")) >= len(protein_class.filter(l2="Kinase")) >=
                        len(protein_class.filter(l3="Protein Kinase")) >=
                        len(protein_class.filter(l4="CAMK protein kinase group")) >=
                        len(protein_class.filter(l5="CAMK protein kinase CAMK1 family")) >=
                        len(protein_class.filter(l6="CAMK protein kinase AMPK subfamily")))
        self.assertEqual([prot['protein_class_id'] for prot in protein_class.all().order_by('protein_class_id')[0:5]],
            [1, 2, 3, 4, 5])
        random_index = randint(0, count - 1)
        random_elem = protein_class.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('l1', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('l2', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('l3', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('l4', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('l5', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('l6', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('l7', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('l8', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('protein_class_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        protein_class.set_format('xml')
        parseString(protein_class.get(409))

    @pytest.mark.timeout(TIMEOUT)
    def test_similarity_resource(self):
        similarity = new_client.similarity
        #self.assertTrue(len(similarity.all()))
        res = similarity.filter(smiles="CC(=O)Oc1ccccc1C(=O)O", similarity=70)
        self.assertTrue(res.exists())
        count = len(res)
        self.assertTrue('molecule_hierarchy' in res.filter(molecule_properties__acd_logp__gte=3.4).filter(molecule_properties__hbd__lte=5)[0])
        random_index = randint(0, count - 1)
        random_elem = res[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('availability_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('black_box_warning', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('chebi_par_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('chirality', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('dosed_ingredient', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('first_approval', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('first_in_class', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('indication_class', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('inorganic_flag', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('max_phase', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_hierarchy', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_properties', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_structures', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('natural_product', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('oral', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('parenteral', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('polymer_flag', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('pref_name', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('prodrug', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('structure_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('therapeutic_flag', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('topical', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_stem', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_stem_definition', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_substem', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_year', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('similarity', random_elem, 'One of required fields not found in resource %s' % random_elem)
        res.set_format('xml')
        parseString(res[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_source_resource(self):
        source = new_client.source
        count = len(source.all())
        self.assertTrue(count)
        self.assertTrue(source.filter(src_short_name="ATLAS").exists())
        self.assertEquals( [src['src_id'] for src in source.all().order_by('src_id')[0:5]], [1,2,3,4,5])
        random_index = randint(0, count - 1)
        random_elem = source.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('src_description', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('src_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('src_short_name', random_elem, 'One of required fields not found in resource %s' % random_elem)
        source.set_format('xml')
        parseString(source.filter(src_short_name="DRUGS")[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_substructure_resource(self):
        substructure = new_client.substructure
        #self.assertTrue(len(substructure.all()))
        res = substructure.filter(smiles="CN(CCCN)c1cccc2ccccc12")
        self.assertTrue(res.exists())
        count = len(res)
        self.assertTrue('med_chem_friendly' in res.filter(molecule_properties__full_mwt__gte=400)
                                               .filter(molecule_properties__num_alerts__gt=1)[0]['molecule_properties'])
        random_index = randint(0, count - 1)
        random_elem = res[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('availability_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('black_box_warning', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('chebi_par_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('chirality', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('dosed_ingredient', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('first_approval', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('first_in_class', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('indication_class', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('inorganic_flag', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('max_phase', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_hierarchy', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_properties', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_structures', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('molecule_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('natural_product', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('oral', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('parenteral', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('polymer_flag', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('pref_name', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('prodrug', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('structure_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('therapeutic_flag', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('topical', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_stem', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_stem_definition', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_substem', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('usan_year', random_elem, 'One of required fields not found in resource %s' % random_elem)
        res.set_format('xml')
        parseString(res[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_target_resource(self):
        target = new_client.target
        count = len(target.all())
        self.assertTrue(count)
        self.assertTrue(target.filter(organism="Homo sapiens").filter(target_type="SINGLE PROTEIN").exists())
        self.assertEquals( [t['pref_name'] for t in target.get(['CHEMBL1927', 'CHEMBL1929', 'CHEMBL1930'])],
        ['Thioredoxin reductase 1',
         'Xanthine dehydrogenase',
         'Vitamin k epoxide reductase complex subunit 1 isoform 1'])
        random_index = randint(0, count - 1)
        random_elem = target.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('organism', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('pref_name', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('species_group_flag', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('target_chembl_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('target_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('target_components', random_elem, 'One of required fields not found in resource %s' % random_elem)
        target.set_format('xml')
        parseString(target.all()[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_target_component_resource(self):
        target_component = new_client.target_component
        count = len(target_component.all())
        self.assertTrue(count)
        self.assertTrue('sequence' in target_component.get(1295))
        self.assertEqual([targcomp['component_id'] for targcomp in target_component.all().order_by('component_id')[0:5]],
            [1, 2, 3, 4, 5])
        target_component.set_format('xml')
        random_index = randint(0, count - 1)
        random_elem = target_component.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get %s element from the list" % random_index)
        self.assertIn('accession', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('sequence', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('component_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('component_type', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('description', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('organism', random_elem, 'One of required fields not found in resource %s' % random_elem)
        self.assertIn('tax_id', random_elem, 'One of required fields not found in resource %s' % random_elem)
        parseString(target_component.all()[0])

    @pytest.mark.timeout(TIMEOUT)
    def test_traversing(self):
        new_client.molecule.set_format('json')
        molecules = new_client.molecule.filter(atc_classifications__level5__startswith='A10')
        self.assertTrue(molecules.exists())
        molecule_ids = map(lambda d: d['molecule_chembl_id'], molecules)
        activities = new_client.activity.filter(molecule_chembl_id__in=molecule_ids)
        self.assertTrue(activities.exists())
        activities_1 = new_client.activity.get(molecule_chembl_id=molecule_ids)
        self.assertEqual(len(activities), len(activities_1))

    def test_utils_format_conversion(self):
        smiles = 'O=C(Oc1ccccc1C(=O)O)C' # aspirin
        ctab = utils.smiles2ctab(smiles)
        self.assertIsNotNone(ctab)
        canonical_smiles = utils.ctab2smiles(ctab).split()[2]
        self.assertEqual(canonical_smiles, 'CC(=O)Oc1ccccc1C(=O)O')
        inchi = utils.ctab2inchi(ctab)
        self.assertEqual(inchi, 'InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)')
        inchiKey = utils.inchi2inchiKey(inchi)
        self.assertEqual(inchiKey, 'BSYNRYMUTXBXSQ-UHFFFAOYSA-N')
        ctab2 = utils.inchi2ctab(inchi)
        self.assertIsNotNone(ctab2)
        smiles2 = utils.ctab2smiles(ctab2).split()[2]
        self.assertEqual(canonical_smiles, smiles2)

    def test_utils_marvin(self):
        smiles = 'O=C(Oc1ccccc1C(=O)O)C' # aspirin
        mrv = json.loads(utils.molExport(structure=smiles, parameters="mrv"))['structure']
        self.assertIsNotNone(mrv)
        self.assertTrue('<cml><MDocument><MChemicalStruct>' in mrv)
        hdr = utils.hydrogenize(structure=str(mrv), parameters={"method":"HYDROGENIZE"}, input_format="mrv")
        self.assertEqual(hdr.count('<atom elementType="H"'), 8)
        cln = utils.clean(structure=mrv)
        self.assertTrue('<cml><MDocument><MChemicalStruct>' in cln)
        self.assertTrue('H H H H H H H H' not in cln)
        cml = "<cml><MDocument><MChemicalStruct><molecule molID=\"m1\"><atomArray><atom id=\"a1\" elementType=\"C\" x2=\"-3.1249866416667733\" y2=\"-0.5015733293207466\"/><atom id=\"a2\" elementType=\"C\" x2=\"-4.458533297665067\" y2=\"-1.2715733231607467\"/><atom id=\"a3\" elementType=\"C\" x2=\"-4.458533297665067\" y2=\"-2.81175997750592\"/><atom id=\"a4\" elementType=\"C\" x2=\"-3.1249866416667733\" y2=\"-3.58175997134592\"/><atom id=\"a5\" elementType=\"C\" x2=\"-1.7912533190033066\" y2=\"-2.81175997750592\"/><atom id=\"a6\" elementType=\"C\" x2=\"-1.7912533190033066\" y2=\"-1.2715733231607467\"/><atom id=\"a7\" elementType=\"C\" x2=\"-0.45751999633984003\" y2=\"-0.5013866626555733\"/><atom id=\"a8\" elementType=\"O\" x2=\"-0.45751999633984003\" y2=\"1.0384266583592534\"/><atom id=\"a9\" elementType=\"C\" x2=\"0.87583999299328\" y2=\"-1.2713866564955734\"/><atom id=\"a10\" elementType=\"C\" x2=\"0.87583999299328\" y2=\"-2.8113866441755735\"/></atomArray><bondArray><bond atomRefs2=\"a1 a2\" order=\"2\"/><bond atomRefs2=\"a2 a3\" order=\"1\"/><bond atomRefs2=\"a3 a4\" order=\"2\"/><bond atomRefs2=\"a4 a5\" order=\"1\"/><bond atomRefs2=\"a5 a6\" order=\"2\"/><bond atomRefs2=\"a6 a1\" order=\"1\"/><bond atomRefs2=\"a6 a7\" order=\"1\"/><bond atomRefs2=\"a7 a9\" order=\"1\"/><bond atomRefs2=\"a9 a10\" order=\"1\"/><bond atomRefs2=\"a7 a8\" order=\"1\"><bondStereo>W</bondStereo></bond></bondArray></molecule></MChemicalStruct></MDocument></cml>"
        stereo_info = json.loads(utils.cipStereoInfo(structure=cml))
        self.assertEqual(stereo_info['tetraHedral'][0], {u'atomIndex': 6, u'chirality': u'S'})

    def test_utils_standardisation(self):
        mol = utils.smiles2ctab("[Na]OC(=O)c1ccccc1")
        br = utils.breakbonds(mol)
        smiles = utils.ctab2smiles(br).split()[2]
        self.assertEqual(smiles, '[Na+].O=C([O-])c1ccccc1')
        mol = utils.smiles2ctab("C(C(=O)[O-])(Cc1n[n-]nn1)(C[NH3+])(C[N+](=O)[O-])")
        ne = utils.neutralise(mol)
        smiles = utils.ctab2smiles(ne).split()[2]
        self.assertEqual(smiles, 'NCC(Cc1nn[nH]n1)(C[N+](=O)[O-])C(=O)O')
        mol = utils.smiles2ctab("Oc1nccc2cc[nH]c(=N)c12")
        ru = utils.rules(mol)
        smiles = utils.ctab2smiles(ru).split()[2]
        self.assertEqual(smiles, 'Nc1nccc2cc[nH]c(=O)c12')
        mol = utils.smiles2ctab("[Na+].OC(=O)Cc1ccc(CN)cc1.OS(=O)(=O)C(F)(F)F")
        un = utils.unsalt(mol)
        smiles = utils.ctab2smiles(un).split()[2]
        self.assertEqual(smiles, 'NCc1ccc(CC(=O)O)cc1')
        mol = utils.smiles2ctab("[Na]OC(=O)Cc1ccc(C[NH3+])cc1.c1nnn[n-]1.O")
        st = utils.standardise(mol)
        smiles = utils.ctab2smiles(st).split()[2]
        self.assertEqual(smiles, 'NCc1ccc(CC(=O)O)cc1')

    def test_utils_calculations(self):
        aspirin = utils.smiles2ctab('O=C(Oc1ccccc1C(=O)O)C')
        num_atoms = json.loads(utils.getNumAtoms(aspirin))[0]
        self.assertEqual(num_atoms, 13)
        mol_wt = json.loads(utils.molWt(aspirin))[0]
        self.assertAlmostEqual(mol_wt, 180.159, 3)
        log_p = json.loads(utils.logP(aspirin))[0]
        self.assertAlmostEqual(log_p, 1.31, 2)
        tpsa = json.loads(utils.tpsa(aspirin))[0]
        self.assertAlmostEqual(tpsa, 63.6, 1)
        descriptors = json.loads(utils.descriptors(aspirin))[0]
        self.assertEqual(descriptors['MolecularFormula'], 'C9H8O4')
        self.assertEqual(descriptors['RingCount'], 1)
        self.assertEqual(descriptors['NumRotatableBonds'], 3)
        self.assertEqual(descriptors['HeavyAtomCount'], num_atoms)
        self.assertAlmostEqual(mol_wt, descriptors['MolWt'], 3)
        self.assertAlmostEqual(log_p, descriptors['MolLogP'], 2)
        self.assertAlmostEqual(tpsa, descriptors['TPSA'], 1)

    def test_utils_fingerprints(self):
        aspirin = utils.smiles2ctab('O=C(Oc1ccccc1C(=O)O)C')
        fingerprints = utils.sdf2fps(aspirin)
        parts = fingerprints.split()
        self.assertEqual(parts[0], '#FPS1')
        self.assertEqual(parts[1], '#num_bits=2048')
        self.assertTrue(parts[2].startswith('#software='))
        self.assertEqual(len(parts[3]), 512)
        self.assertEqual(parts[4], 'BSYNRYMUTXBXSQ-UHFFFAOYSA-N')

    def test_utils_json_images(self):
        aspirin = 'O=C(Oc1ccccc1C(=O)O)C'
        js1 = json.loads(utils.smiles2json(aspirin))
        self.assertEqual(len(js1), 34)
        self.assertTrue('path' in js1[0] and 'fill' in js1[0] and 'type' in js1[0])
        mol = utils.smiles2ctab(aspirin)
        js2 = json.loads(utils.ctab2json(mol))
        self.assertEqual(len(js1), len(js2))

    def test_utils_svg_images(self):
        benzene = 'c1ccccc1'
        svg1 = utils.smiles2svg(benzene)
        self.assertTrue(len(svg1) > 2000)
        self.assertTrue(svg1.startswith('<?xml version="1.0" encoding="UTF-8"?>'))
        mol = utils.smiles2ctab(benzene)
        svg2 = utils.ctab2svg(mol)
        self.assertEqual(svg1, svg2)

    def test_utils_raster_images(self):
        aspirin = 'O=C(Oc1ccccc1C(=O)O)C'
        img1 = utils.smiles2image(aspirin)
        self.assertEqual(img1[0:4], '\x89PNG')
        self.assertTrue(len(img1) > 5000)
        mol = utils.smiles2ctab(aspirin)
        img2 = utils.ctab2image(mol)
        self.assertEqual(img2[0:4], '\x89PNG')
        self.assertTrue(len(img2) > 5000)

    def test_utils_mcs(self):
        smiles = ["O=C(NCc1cc(OC)c(O)cc1)CCCC/C=C/C(C)C", "CC(C)CCCCCC(=O)NCC1=CC(=C(C=C1)O)OC", "c1(C=O)cc(OC)c(O)cc1"]
        mols = [utils.smiles2ctab(smile) for smile in smiles]
        sdf = ''.join(mols)
        result = utils.mcs(sdf)
        self.assertEqual(result, '[#6]-[#6]:1:[#6]:[#6](:[#6](:[#6]:[#6]:1)-[#8])-[#8]-[#6]')

    def test_utils_3D_coords(self):
        aspirin = 'O=C(Oc1ccccc1C(=O)O)C'
        mol_3D = utils.smiles23D(aspirin)
        lines = mol_3D.split('\n')
        atoms_lines = lines[4:25]
        z_coords = [float(line.split()[2]) for line in atoms_lines]
        self.assertTrue(any(z_coords))
        mol = utils.smiles2ctab(aspirin)
        mol_3D1 = utils.ctab23D(mol)
        lines = mol_3D1.split('\n')
        atoms_lines = lines[4:25]
        z_coords = [float(line.split()[2]) for line in atoms_lines]
        self.assertTrue(any(z_coords))

    def test_utils_osra(self):
        aspirin = 'CC(=O)Oc1ccccc1C(=O)O'
        im = utils.smiles2image(aspirin)
        mol = utils.image2ctab(im)
        smiles = utils.ctab2smiles(mol).split()[2]
        self.assertEqual(smiles, aspirin)

    def test_utis_kekulize(self):
        aromatic='''
  Mrv0541 08191414212D

  6  6  0  0  0  0            999 V2000
   -1.7679    1.5616    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -2.4823    1.1491    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -2.4823    0.3241    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.7679   -0.0884    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.0534    0.3241    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.0534    1.1491    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  4  0  0  0  0
  1  6  4  0  0  0  0
  2  3  4  0  0  0  0
  3  4  4  0  0  0  0
  4  5  4  0  0  0  0
  5  6  4  0  0  0  0
M  END

'''
        kek = utils.kekulize(aromatic)
        lines = kek.split('\n')
        bond_lines = lines[10:16]
        bond_types = [int(line.split()[2]) for line in bond_lines]
        self.assertFalse(any([x == 4 for x in bond_types]))

if __name__ == '__main__':
    unittest.main()
