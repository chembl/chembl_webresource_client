# -*- coding: utf-8 -*-

__author__ = 'mnowotka'

from xml.dom.minidom import parseString
from requests.exceptions import RetryError
from chembl_webresource_client.settings import Settings
from chembl_webresource_client import *
from chembl_webresource_client.utils import utils
from chembl_webresource_client.new_client import new_client
from chembl_webresource_client.unichem import unichem_client as unichem
from chembl_webresource_client.http_errors import HttpBadRequest, HttpNotFound
from chembl_webresource_client.scripts.utils import resolve
from chembl_webresource_client.scripts.utils import get_parents
from decimal import Decimal
import time
import json
import unittest
import logging
import itertools
from random import randint
logging.basicConfig()
logging.basicConfig(level=logging.INFO)

TIMEOUT = Settings.Instance().TEST_CASE_TIMEOUT


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        super(TestSequenceFunctions, self).setUp()
        Settings.Instance().WEBSERVICE_PROTOCOL = 'https'
        Settings.Instance().WEBSERVICE_DOMAIN = 'www.ebi.ac.uk'
        Settings.Instance().TIMEOUT = 10
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("{0}: {1:3f}".format(self.id(), t))

    # def test_activity_resource_lists(self):
    #     activity = new_client.activity
    #     activity.set_format('json')
    #     count = len(activity.all())
    #     self.assertTrue(count)
    #     self.assertNotEqual(activity.all().order_by('assay_type')[0]['activity_id'],activity.all().order_by('-assay_type')[0]['activity_id'])
    #     self.assertNotEqual(activity.all().order_by('published_relation')[0]['activity_id'],activity.all().order_by('-published_relation')[0]['activity_id'])
    #     self.assertTrue(activity.filter(standard_type="Log Ki").filter(standard_value__gte=5).exists())
    #     self.assertTrue(activity.filter(target_chembl_id="CHEMBL333").exists())
    #     self.assertTrue('c' in activity.get(66369)['canonical_smiles'])
    #     self.assertEqual([act['activity_id'] for act in activity.all().order_by('activity_id')[0:5]],
    #         [31863, 31864, 31865, 31866, 31867])
    #     reg = activity.filter(target_chembl_id="CHEMBL3938", assay_type__iregex="(B|F)")
    #     self.assertTrue(400 <= len(reg) < 500)
    #     self.assertTrue(all('CHEMBL3938' == x['target_chembl_id'] and (x['assay_type'] in 'B', 'F') for x in reg[:20]))
    #     type_a = activity.filter(assay_type='A')
    #     self.assertTrue(650000 <= len(type_a) < 800000, len(type_a))
    #     self.assertTrue(all('A' == x['assay_type'] for x in type_a[:20]))
    #     self.assertTrue(activity.filter(assay_type='A').exists())
    #     self.assertTrue(activity.filter(assay_type='B').exists())
    #     self.assertTrue(activity.filter(assay_type='F').exists())
    #     self.assertTrue(activity.filter(assay_type='U').exists())
    #     self.assertTrue(activity.filter(assay_type='P').exists())
    #     self.assertTrue(500 < len(activity.filter(target_chembl_id='CHEMBL4506')
    #                               .filter(standard_type__in=['IC50', 'Ki', 'EC50', 'Kd'])
    #                               .filter(standard_value__isnull=False)
    #                               .filter(ligand_efficiency__isnull=False)) < 750)

    # def test_activity_resource_details(self):
    #     activity = new_client.activity
    #     activity.set_format('json')
    #     random_index = 11000 #randint(0, count - 1) - too slow!
    #     random_elem = activity.all()[random_index]
    #     self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
    #     self.assertIn('activity_comment', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('activity_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_description', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('bao_format', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('bao_label', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('bao_endpoint', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('canonical_smiles', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('data_validity_comment', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('data_validity_description', random_elem,'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('document_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('document_journal', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('document_year', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('pchembl_value', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('potential_duplicate', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('published_relation', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('published_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('published_units', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('published_value', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('qudt_units', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('record_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('standard_flag', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('standard_relation', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('standard_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('standard_units', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('standard_value', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('src_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('target_pref_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('target_tax_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('target_organism', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('parent_molecule_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('uo_units', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('ligand_efficiency', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     activity.set_format('xml')
    #     parseString(activity.all()[0])

    # def test_activity_unique(self):
    #     activity = new_client.activity
    #     activity.set_format('json')
    #     acts = activity.filter(target_chembl_id='CHEMBL5619')[:5000]
    #     self.assertTrue(len(acts) == len(set([act['activity_id'] for act in acts])))

    # def test_activity_assay_description_search_is_fast(self):
    #     activity = new_client.activity
    #     activity.set_format('json')
    #     acts = activity.filter(assay_description__icontains='TG-GATES')
    #     l = len(acts)
    #     self.assertTrue(200000 <= l < 230000, l)
    #     self.assertTrue(all('TG-GATES' in x['assay_description'] for x in acts[0:20]))
    #     acts = activity.filter(assay_description__icontains='tg-gates')
    #     self.assertEqual(len(acts), l)
    #     res = activity.search('"TG-GATES"')
    #     k = len(res)
    #     self.assertTrue(200000 <= k < 230000, k)
    #     assay = new_client.assay
    #     assay.set_format('json')
    #     res1 = assay.search('"TG-GATES"')
    #     m = len(res1)
    #     self.assertTrue(200000 <= m < 230000, m)
    #     self.assertTrue(l == k == m)

    # def test_assay_resource(self):
    #     assay = new_client.assay
    #     count = len(assay.all())
    #     self.assertTrue(count)
    #     self.assertTrue(assay.filter(assay_oragism="Sus scrofa").filter(assay_type="B").exists())
    #     self.assertNotEqual(assay.all().order_by('assay_category')[0]['assay_chembl_id'], assay.all().order_by('-assay_category')[0]['assay_chembl_id'])
    #     self.assertNotEqual(assay.all().order_by('assay_strain')[0]['assay_chembl_id'], assay.all().order_by('-assay_strain')[0]['assay_chembl_id'])
    #     self.assertEqual([ass['bao_format'] for ass in assay.get(['CHEMBL615111', 'CHEMBL615112', 'CHEMBL615113'])],
    #     [u'BAO_0000019', u'BAO_0000019', u'BAO_0000019'])
    #     random_index = 4567 #randint(0, count - 1)
    #     random_elem = assay.all()[random_index]
    #     self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
    #     self.assertIn('assay_category', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_cell_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_organism', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_strain', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_subcellular_fraction', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_tax_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_test_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_tissue', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('assay_type_description', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('bao_format', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('bao_label', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('cell_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('confidence_description', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('confidence_score', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('description', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('document_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('relationship_description', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('relationship_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('src_assay_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('src_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('target_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     l1 = len(assay.filter(assay_type='B').filter(description__icontains='insulin'))
    #     l2 = len(assay.filter(assay_type='B').filter(description__icontains='insulin').filter(description__icontains='inhibition'))
    #     self.assertTrue(l1 > 100)
    #     self.assertTrue(l1 > l2, str((l1, l2)))
    #     self.assertTrue(l2 > 0)
    #     assay.set_format('xml')
    #     parseString(assay.filter(confidence_score__gte=8)[0])

    def test_assay_search(self):
        assay = new_client.assay
        assay.set_format('json')
        count = len(assay.all())
        res = assay.search('inhibitor')
        self.assertTrue(len(res) > 6000)
        self.assertTrue(len(res) < count)
        self.assertTrue('inhibitor' in res[0]['description'])
        res = assay.search('inhibitor').filter(assay_type='A')
        self.assertTrue('inhibitor' in res[0]['description'])
        self.assertEqual(res[0]['assay_type'], 'A')
        self.assertTrue(1000 < len(res) < 1300, len(res))

    def test_atc_class_resource(self):
        atc_class = new_client.atc_class
        count = len(atc_class.all())
        self.assertTrue(count)
        self.assertTrue(len(atc_class.filter(level1="H")) >= len(atc_class.filter(level2="H03")) >=
                        len(atc_class.filter(level3="H03A")) >= len(atc_class.filter(level4="H03AA")) >=
                        len(atc_class.filter(level5="H03AA03")))
        self.assertEqual(atc_class.get('H03AA03')['who_name'], 'combinations of levothyroxine and liothyronine')
        self.assertEqual([atc['level5'] for atc in atc_class.all().order_by('level5')[0:5]],
            [u'A01AA01', u'A01AA02', u'A01AA03', u'A01AA04', u'A01AA30'])
        self.assertEqual(atc_class.all().order_by('level1')[0]['level1'], "A")
        self.assertEqual(atc_class.all().order_by('-level1')[0]['level1'], "V")
        random_index = 4321 #randint(0, count - 1)
        random_elem = atc_class.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('level1', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('level2', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('level3', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('level4', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('level5', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('who_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        atc_class.set_format('xml')
        parseString(atc_class.filter(level1="G")[0])

    def test_binding_site_resource(self):
        binding_site = new_client.binding_site
        count = len(binding_site.all())
        self.assertTrue(count)
        self.assertTrue('site_name' in binding_site.all()[0])
        self.assertEqual([site['site_components'][0]['domain']['domain_type'] for site in
                           binding_site.get([962, 963, 943])], [u'Pfam-A', u'Pfam-A', u'Pfam-A'])
        self.assertEqual([bind['site_id'] for bind in binding_site.all().order_by('site_id')[0:5]],
            [2, 3, 4, 5, 6])
        random_index = 1234 #randint(0, count - 1)
        random_elem = binding_site.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('site_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('site_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('site_components', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        site_component = binding_site.get(2)['site_components'][0]
        self.assertIn('component_id', site_component, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('sitecomp_id', site_component, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('domain', site_component, 'One of required fields not found in resource {0}'.format(random_elem))
        domain = site_component['domain']
        self.assertIn('domain_description', domain, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('domain_id', domain, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('domain_name', domain, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('domain_type', domain, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('source_domain_id', domain, 'One of required fields not found in resource {0}'.format(random_elem))
        binding_site.set_format('xml')
        parseString(binding_site.get(3))

    def test_biotherapeutic_resource(self):
        biotherapeutic = new_client.biotherapeutic
        count = len(biotherapeutic.all())
        self.assertTrue(count)
        self.assertTrue(biotherapeutic.filter(description__isnull=False).filter(helm_notation__startswith="PEPTIDE1").exists())
        self.assertTrue(all([l > 5 for l in [len(biot['description']) for biot in
                                                    biotherapeutic.get(['CHEMBL525076','CHEMBL1200516','CHEMBL160'])]]))
        random_index = 321 #randint(0, count - 1)
        random_elem = biotherapeutic.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('helm_notation', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('biocomponents', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        biotherapeutic.set_format('xml')
        parseString(biotherapeutic.filter(helm_notation__contains='meV')[0])

    def test_cell_line_resource(self):
        cell_line = new_client.cell_line
        count = len(cell_line.all())
        self.assertTrue(count)
        self.assertTrue(cell_line.filter(cell_name__startswith="MDA").exists())
        self.assertTrue('efo_id' in cell_line.get(1))
        self.assertNotEqual(cell_line.all().order_by('cell_chembl_id')[0]['cell_id'], cell_line.all().order_by('-cell_chembl_id')[0]['cell_id'])
        self.assertNotEqual(cell_line.all().order_by('cell_source_organism')[0]['cell_id'], cell_line.all().order_by('-cell_source_organism')[0]['cell_id'])
        self.assertNotEqual(cell_line.all().order_by('cell_source_tax_id')[0]['cell_id'], cell_line.all().order_by('-cell_source_tax_id')[0]['cell_id'])
        self.assertNotEqual(cell_line.all().order_by('cell_source_tissue')[0]['cell_id'], cell_line.all().order_by('-cell_source_tissue')[0]['cell_id'])
        self.assertNotEqual(cell_line.all().order_by('cellosaurus_id')[0]['cell_id'], cell_line.all().order_by('-cellosaurus_id')[0]['cell_id'])
        self.assertEqual([cell['cell_id'] for cell in cell_line.all().order_by('cell_id')[0:5]],
            [1, 2, 3, 4, 5])
        self.assertEqual([cell['cell_id'] for cell in cell_line.get(['CHEMBL3307242','CHEMBL3307243'])],
            [cell['cell_id'] for cell in cell_line.get([2,3])])
        self.assertEqual([cell['cell_id'] for cell in cell_line.get(cell_chembl_id=['CHEMBL3307242','CHEMBL3307243'])],
            [cell['cell_id'] for cell in cell_line.get(cell_id=[2,3])])
        random_index = 1234 #randint(0, count - 1)
        random_elem = cell_line.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('cell_description', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('cell_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('cell_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('cell_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('cell_source_organism', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('cell_source_tax_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('cell_source_tissue', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('cellosaurus_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('clo_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('efo_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('cl_lincs_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        cell_line.set_format('xml')
        parseString(cell_line.filter(cellosaurus_id="CVCL_0417")[0])

    def test_go_slim_resource(self):
        go_slim = new_client.go_slim
        count = len(go_slim.all())
        self.assertTrue(count)
        self.assertTrue(go_slim.filter(aspect="F").filter(class_level__gte=3).exists())
        self.assertEqual(go_slim.order_by('aspect')[0]['aspect'], "C")
        self.assertTrue(all(['cellular_component  organelle' in x['path'] for x in go_slim.get(['GO:0000229','GO:0005730'])]))
        random_index = 205
        random_elem = go_slim.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('aspect', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('class_level', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('go_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('parent_go_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('path', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('pref_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        go_slim.set_format('xml')
        parseString(go_slim.filter(pref_name="nucleolus")[0])

    # def test_drug_indication_resource(self):
    #     drug_indication = new_client.drug_indication
    #     count = len(drug_indication.all())
    #     self.assertTrue(count)
    #     self.assertTrue(all([x['efo_term'].startswith('OSTEOARTHRITIS') for x in drug_indication.filter(max_phase_for_ind__lte=3, efo_term__startswith='OSTEOARTHRITIS')]))
    #     self.assertTrue(drug_indication.order_by('mesh_id')[0]['mesh_id'].startswith('D0000'))
    #     self.assertTrue(all([x['efo_id'].startswith('EFO:000') for x in drug_indication.get([22614, 22615])]))
    #     ncts = drug_indication.filter(indication_refs__ref_id__contains='NCT')
    #     all(any('NCT' in y['ref_id'] for y in x['indication_refs']) for x in ncts)
    #     self.assertTrue(11000 < len(ncts) < count)
    #     random_index = 2345
    #     random_elem = drug_indication.all()[random_index]
    #     self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
    #     self.assertIn('drugind_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('efo_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('efo_term', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('indication_refs', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('max_phase_for_ind', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('mesh_heading', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('mesh_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     indication_refs = drug_indication.get(molecule_chembl_id=['CHEMBL606'])[0]['indication_refs'][0]
    #     self.assertIn('ref_id', indication_refs, 'One of required fields not found in resource {0}'.format(indication_refs))
    #     self.assertIn('ref_type', indication_refs, 'One of required fields not found in resource {0}'.format(indication_refs))
    #     self.assertIn('ref_url', indication_refs, 'One of required fields not found in resource {0}'.format(indication_refs))
    #     drug_indication.set_format('xml')
    #     parseString(drug_indication.filter(molecule_chembl_id="CHEMBL1201460")[0])

    def test_drug_resource(self):
        drug = new_client.drug
        count = len(drug.all())
        self.assertTrue(count)
        self.assertTrue(drug.filter(first_approval=1976).filter(usan_stem="-azosin").exists())
        # self.assertEqual(drug.order_by('sc_patent').filter(sc_patent__isnull=False)[0]['ob_patent'], "5223510")
        # self.assertTrue(all([x['development_phase'] == 4 for x in drug.get(['CHEMBL2', 'CHEMBL3'])]))
        # random_index = 1725
        # random_elem = drug.all()[random_index]
        # self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        # self.assertIn('applicants', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('atc_classification', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('availability_type', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('black_box', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('chirality', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('development_phase', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('drug_type', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('first_approval', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('first_in_class', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('indication_class', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('molecule_chembl_id', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('ob_patent', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('oral', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('parenteral', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('prodrug', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('research_codes', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('rule_of_five', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('sc_patent', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('synonyms', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('topical', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('usan_stem', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('usan_stem_definition', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('usan_stem_substem', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('usan_year', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('withdrawn_country', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('withdrawn_reason', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # self.assertIn('withdrawn_year', random_elem,
        #               'One of required fields not found in resource {0}'.format(random_elem))
        # dr = drug.get('CHEMBL1201572')
        # self.assertEqual(dr['atc_classification'][0]['code'], 'L04AB01', dr)
        # drug.set_format('xml')
        # parseString(drug.filter(synonyms__icontains="prazosin")[0])

    def test_metabolism_resource(self):
        metabolism = new_client.metabolism
        count = len(metabolism.all())
        self.assertTrue(count)
        self.assertTrue(metabolism.filter(met_conversion__startswith='hydroxylation', met_comment__icontains='liver', enzyme_name__isnull=False).exists())
        self.assertEqual(metabolism.order_by('-pathway_id')[0]['pathway_id'], 3)
        self.assertTrue(all([x['met_conversion'] == 'O-demethylation' for x in metabolism.get([149,151])]))
        random_index = 123
        random_elem = metabolism.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('drug_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('enzyme_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('substrate_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('metabolite_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('met_comment', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('met_conversion', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('met_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('metabolism_refs', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('metabolite_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('organism', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('pathway_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('pathway_key', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('substrate_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('target_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('tax_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        metabolism_refs = metabolism.get(target_chembl_id=['CHEMBL612545'])[0]['metabolism_refs'][0]
        self.assertIn('ref_id', metabolism_refs, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('ref_type', metabolism_refs, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('ref_url', metabolism_refs, 'One of required fields not found in resource {0}'.format(random_elem))
        metabolism.set_format('xml')
        parseString(metabolism.filter(substrate_chembl_id="CHEMBL1071")[0])

    def test_tissue_resource(self):
        tissue = new_client.tissue
        count = len(tissue.all())
        self.assertTrue(count)
        self.assertTrue(tissue.filter(pref_name__istartswith='blood').exists())
        self.assertTrue(tissue.order_by('efo_id').exists())
        self.assertTrue(tissue.filter(bto_id="BTO:0001073")[0]['pref_name'] == "Pituitary gland")
        self.assertTrue(tissue.filter(caloha_id="TS-0490")[0]['pref_name'] == "Intestine")
        self.assertTrue(tissue.filter(uberon_id="UBERON:0000173")[0]['tissue_chembl_id'] == "CHEMBL3638177")
        self.assertTrue(tissue.filter(efo_id="UBERON:0000178")[0]['tissue_chembl_id'] == "CHEMBL3638178")
        random_index = 2 #randint(0, count - 1)
        random_elem = tissue.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('efo_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('pref_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('tissue_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('uberon_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('bto_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('caloha_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        tissue.set_format('xml')
        parseString(tissue.filter(efo_id__startswith="EFO")[0])

    def test_target_relations(self):
        target_relation = new_client.target_relation
        count = len(target_relation.all())
        self.assertTrue(count)
        self.assertTrue(target_relation.filter(target_chembl_id='CHEMBL2096621',relationship='OVERLAPS WITH').exists())
        self.assertEqual(target_relation.order_by('relationship')[0]['relationship'],'EQUIVALENT TO')
        self.assertTrue(len(target_relation.get('CHEMBL2096621')['target_relations']) == 4, str(target_relation.get('CHEMBL2096621')))
        random_index = 4321 #randint(0, count - 1)
        random_elem = target_relation.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list of {1} elements".format(random_index, count))
        self.assertIn('related_target_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('relationship', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('target_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        target_relation.set_format('xml')
        parseString(target_relation.filter(relationship='EQUIVALENT TO')[0])

    def test_document_search(self):
        document = new_client.document
        document.set_format('json')
        count = len(document.all())
        res = document.search('cytokine')
        self.assertTrue(len(res) > 300)
        self.assertTrue(len(res) < count)
        self.assertTrue('cytokine' in res[0]['abstract'], res[0]['abstract'])
        res = document.search('activators')
        self.assertTrue('activators' in (res[0]['abstract'].lower() + res[0]['title'].lower()))
        act_count = len(res)
        self.assertTrue(act_count >= 10000)
        self.assertTrue(act_count < count)
        res = document.filter(abstract__icontains="activators")
        self.assertTrue('activators' in res[0]['abstract'])
        act_count_1 = len(res)
        self.assertTrue(act_count_1 < act_count)
        self.assertTrue(act_count_1 > 300)

    def test_document_similarity_resource(self):
        document_similarity = new_client.document_similarity
        count = len(document_similarity.all())
        self.assertTrue(count)
        self.assertTrue(document_similarity.filter(document_1_chembl_id='CHEMBL1122254').exists())
        self.assertTrue(document_similarity.filter(document_1_chembl_id='CHEMBL1122702').order_by('tid_tani').exists())

        self.assertEqual(len(document_similarity.filter(document_1_chembl_id='CHEMBL1124609')), 50)
        self.assertEqual(document_similarity.filter(document_1_chembl_id='CHEMBL1147570').order_by('tid_tani')[0]['tid_tani'], 0)
        self.assertEqual(document_similarity.filter(document_1_chembl_id='CHEMBL1147570').order_by('-tid_tani')[0]['tid_tani'], 1)
        self.assertEqual(document_similarity.filter(document_1_chembl_id='CHEMBL1122254').order_by('mol_tani')[0]['mol_tani'], 0)
        self.assertEqual(document_similarity.filter(document_1_chembl_id='CHEMBL1122254').order_by('-mol_tani')[0]['mol_tani'], 0.01)

        random_index = 444444
        random_elem = document_similarity.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('document_1_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('document_2_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('mol_tani', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('tid_tani', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))

        document_similarity.set_format('xml')
        parseString(document_similarity.filter(document_2_chembl_id='CHEMBL1123409')[0])

    # def test_document_resource(self):
    #     document = new_client.document
    #     count = len(document.all())
    #     self.assertTrue(count)
    #     self.assertTrue(document.filter(doc_type='PUBLICATION').filter(year__gt=1985).filter(volume=5).exists())
    #     self.assertTrue(document.order_by('authors').exists())
    #     self.assertTrue(document.filter(patent_id="US-8470825-B2")[0]['doc_type'] == 'PATENT')
    #     self.assertTrue(document.filter(patent_id="US-8470825-B2")[0]['document_chembl_id'] == 'CHEMBL3639262')
    #     self.assertTrue(document.filter(patent_id="US-8470825-B2")[0]['document_chembl_id'] == 'CHEMBL3639262')
    #     self.assertTrue(len(document.filter(patent_id__startswith='US-')) >= 1000)
    #     self.assertTrue(all([page[0] < page[1] for page in [(doc['first_page'], doc['last_page']) for doc in
    #                                             document.get(['CHEMBL1121361', 'CHEMBL1121362', 'CHEMBL1121364'])]]))
    #     random_index = 7777 #randint(0, count - 1)
    #     random_elem = document.all()[random_index]
    #     self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
    #     self.assertIn('authors', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('doc_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('document_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('doi', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('first_page', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('issue', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('journal', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('journal_full_title', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('last_page', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('pubmed_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('title', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('volume', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('year', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('patent_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     document.set_format('xml')
    #     parseString(document.filter(journal="J. Med. Chem.")[0])

    # def test_compound_structural_alert_resource(self):
    #     compound_structural_alert = new_client.compound_structural_alert
    #     compound_structural_alert.set_format('json')
    #     count = len(compound_structural_alert.all())
    #     self.assertTrue(count)
    #     self.assertTrue(compound_structural_alert.filter(alert__alert_set__priority=8).exists())
    #     ans = len(compound_structural_alert.
    #         filter(alert__alert_set__priority__lte=5).
    #         filter(alert__alert_set__set_name='Dundee').
    #         filter(alert__smarts__startswith='C').
    #         filter(alert_name='imine'))
    #     self.assertTrue(320000 < ans < 360000, ans)

    #     self.assertTrue(all([x['alert']['alert_set']['set_name']==u'MLSMR' for x in compound_structural_alert.get([1, 3])]))

    #     self.assertEqual(compound_structural_alert.order_by('-alert__alertset__priority')[0]['alert']['alert_set']['priority'], 8)
    #     self.assertEqual(compound_structural_alert.order_by('alert__alertset__priority')[0]['alert']['alert_set']['priority'], 1)

    #     random_index = 891 #randint(0, count - 1)
    #     random_elem = compound_structural_alert.all()[random_index]
    #     self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
    #     self.assertIn('alert', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('cpd_str_alert_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))

    #     compound_structural_alert.set_format('xml')
    #     parseString(compound_structural_alert.filter(molecule_chembl_id='CHEMBL266429')[0])

    #     compound_structural_alert.set_format('png')
    #     self.assertTrue(compound_structural_alert.get(1).startswith(b'\x89PNG\r\n'))
    #     self.assertTrue(compound_structural_alert.get(2).startswith(b'\x89PNG\r\n'))

    def test_image_resource(self):
        image = new_client.image
        image.set_format('svg')
        self.assertTrue(len(image.get('CHEMBL25')) > 1000)

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
        random_index = 1234 #randint(0, count - 1)
        random_elem = mechanism.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('action_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('binding_site_comment', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('direct_interaction', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('disease_efficacy', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('max_phase', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('mec_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('mechanism_comment', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('mechanism_of_action', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('molecular_mechanism', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('record_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('selectivity_comment', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('site_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('target_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        mechanism.set_format('xml')
        parseString(mechanism.filter(moleculer_mechanism=True)[0])

    def test_compound_records(self):
        compound_record = new_client.compound_record
        count = len(compound_record.all())
        self.assertTrue(count)
        self.assertTrue(compound_record.filter(molecule_chembl_id="CHEMBL25")
                        .filter(compound_name__istartswith='2-Acetoxy')
                        .filter(compound_key__icontains='ASA')
                        .filter(document_chembl_id="CHEMBL1123757")
                        .exists())
        self.assertTrue('compound_key' in compound_record.get(8888))
        self.assertTrue(all(rec['document_chembl_id'] == 'CHEMBL1126670' for rec in compound_record.get(list(range(1, 11)))))
        self.assertTrue(len(compound_record.filter(document_chembl_id='CHEMBL1126670')) >= 20)
        self.assertTrue(len(compound_record.filter(compound_name__iendswith='propionamide')) >= 6000)
        self.assertTrue(len(compound_record.filter(molecule_chembl_id='CHEMBL409')) >= 70)

        compound_record.set_format('xml')
        parseString(compound_record.filter(compound_name="Ranibizumab")[0])

    def test_xref_source(self):
        xref_source = new_client.xref_source
        count = len(xref_source.all())
        self.assertTrue(count)
        random_index = 1  # randint(0, count - 1)
        random_elem = xref_source.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('xref_id_url', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('xref_src_db', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('xref_src_description', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('xref_src_url', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        xref_source.set_format('xml')
        parseString(xref_source.filter(compound_name="Ranibizumab")[0])

    def test_organism(self):
        organism = new_client.organism
        count = len(organism.all())
        self.assertTrue(count)
        self.assertTrue(organism.filter(l1="Eukaryotes").filter(l2="Mammalia").filter(l3="Rodentia").exists())
        self.assertTrue(all(org['l1'] == 'Bacteria' for org in organism.filter(l3='Acinetobacter')))
        self.assertTrue(len(organism.filter(l1='Eukaryotes')) >= 1215)
        self.assertTrue(len(organism.filter(l1='Bacteria')) >= 1245)
        self.assertTrue(len(organism.filter(l1='Fungi')) >= 665)
        self.assertTrue(len(organism.filter(l1='Viruses')) >= 580)
        self.assertTrue(len(organism.filter(l1='Archaea')) >= 15)
        self.assertTrue(len(organism.filter(l1='Unclassified')) >= 1)

        organism.set_format('xml')
        parseString(organism.filter(l1="Bacteria")[0])

    # def test_molecule_resource_lists(self):
    #     molecule = new_client.molecule
    #     molecule.set_format('json')
    #     count = len(molecule.all())
    #     self.assertTrue(count)
    #     self.assertTrue(molecule.filter(molecule_properties__acd_logp__gte=1.9)
    #                             .filter(molecule_properties__aromatic_rings__lte=3)
    #                             .filter(chirality=(-1))
    #                             .exists())
    #     rng = molecule.filter(molecule_properties__full_mwt__range=[200, 201])
    #     self.assertTrue(rng.exists())
    #     self.assertTrue(700 < len(rng) < 900, 'len(rng) is {0} but should be between 700 and 800'.format(len(rng)))
    #     wrong_range = molecule.filter(molecule_properties__full_mwt__range=[200])
    #     with self.assertRaisesRegex(HttpBadRequest, 'Invalid range'):
    #         len(wrong_range)
    #     exact = molecule.filter(molecule_structures__canonical_smiles="COc1ccc2[C@@H]3[C@H](COc2c1)C(C)(C)OC4=C3C(=O)C(=O)C5=C4OC(C)(C)[C@H]6COc7cc(OC)ccc7[C@@H]56")
    #     self.assertEqual(len(exact), 1)
    #     self.assertEqual(list(map(lambda x: x['molecule_chembl_id'], exact)), ['CHEMBL446858'])
    #     flex = molecule.filter(molecule_structures__canonical_smiles__flexmatch="COc1ccc2[C@@H]3[C@H](COc2c1)C(C)(C)OC4=C3C(=O)C(=O)C5=C4OC(C)(C)[C@H]6COc7cc(OC)ccc7[C@@H]56")
    #     self.assertEqual(len(flex), 2)
    #     self.assertEqual(set(map(lambda x: x['molecule_chembl_id'], flex)), set(['CHEMBL446858', 'CHEMBL1']))
    #     self.assertTrue(len(molecule.filter(biotherapeutic__isnull=True)) > len(molecule.filter(biotherapeutic__isnull=False)))
    #     some_compound_id = 'CHEMBL1'
    #     smiles = molecule.get(some_compound_id)['molecule_structures']['canonical_smiles']
    #     res1 = molecule.filter(molecule_structures__canonical_smiles__flexmatch=smiles)
    #     res2 = molecule.filter(molecule_structures__canonical_smiles__flexmatch=some_compound_id)
    #     self.assertEqual(set(map(lambda x: x['molecule_chembl_id'], res1)), set(map(lambda x: x['molecule_chembl_id'], res2)))

    #     molecule.set_format('sdf')
    #     molstring = molecule.all()[0]
    #     inchi_from_molstring = utils.ctab2inchi(molstring)
    #     molecule.set_format('json')
    #     inchi_from_chembl = molecule.all()[0]['molecule_structures']['standard_inchi']
    #     self.assertEqual(inchi_from_molstring, inchi_from_chembl)

    #     molecule.set_format('sdf')
    #     sdf = molecule.filter(molecule_chembl_id__in=['CHEMBL25', 'CHEMBL2260549', 'CHEMBL458500', 'CHEMBL457234',
    #                                                   'CHEMBL1161014', 'CHEMBL458299', 'CHEMBL163612', 'CHEMBL499817',
    #                                                   'CHEMBL455843', 'CHEMBL506341', 'CHEMBL1494499', 'CHEMBL454433',
    #                                                   'CHEMBL2103782', 'CHEMBL441043', 'CHEMBL2107978'])
    #     self.assertTrue(len(sdf), 14)


    #     molecule.set_format('json')
    #     self.assertFalse(molecule.get('CHEMBL6961')['molecule_structures'])
    #     molecule.set_format('sdf')
    #     self.assertRaisesRegex(RetryError, 'too many 404 error responses', molecule.get, 'CHEMBL6961')

    #     molecule.set_format('json')
    #     cont = molecule.filter(molecule_chembl_id__contains="25")
    #     self.assertTrue(83895 <= len(cont) < 90000, len(cont))
    #     self.assertTrue(all('25' in x['molecule_chembl_id'] for x in cont[0:25]))

    #     molecule.set_format('json')
    #     self.assertFalse(molecule.get('CHEMBL6963')['molecule_structures'])
    #     molecule.set_format('sdf')
    #     self.assertRaisesRegex(RetryError, 'too many 404 error responses', molecule.get, 'CHEMBL6963')

    def test_molecule_search(self):
        molecule = new_client.molecule
        molecule.set_format('json')
        res = molecule.search('aspirin')
        self.assertEqual(len(res), 46)
        self.assertEqual(res[0]['molecule_chembl_id'], 'CHEMBL25')
        self.assertEqual(res[0]['pref_name'], 'ASPIRIN')
        self.assertEqual(res[1]['molecule_chembl_id'], 'CHEMBL2260549')
        self.assertEqual(res[1]['pref_name'], 'ASPIRIN EUGENOL ESTER')
        typo = molecule.search('Caffeicæacidæphenethylester')
        self.assertEqual(len(typo), 0)

    # def test_molecule_resource_multiple(self):
    #     molecule = new_client.molecule
    #     molecule.set_format('json')
    #     ids_from_ids_no_name = set(map(lambda x: x['molecule_chembl_id'],
    #                                                     molecule.get(['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505'])))
    #     ids_from_ids_by_name = set(map(lambda x: x['molecule_chembl_id'],
    #                                     molecule.get(molecule_chembl_id=['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505'])))
    #     ids_from_keys_no_name = set(map(lambda x: x['molecule_chembl_id'],
    #         molecule.get(['XSQLHVPPXBBUPP-UHFFFAOYSA-N', 'JXHVRXRRSSBGPY-UHFFFAOYSA-N', 'TUHYVXGNMOGVMR-GASGPIRDSA-N'])))
    #     ids_from_keys_by_name = set(map(lambda x: x['molecule_chembl_id'],
    #         molecule.get(molecule_structures__standard_inchi_key=['XSQLHVPPXBBUPP-UHFFFAOYSA-N',
    #                                                     'JXHVRXRRSSBGPY-UHFFFAOYSA-N', 'TUHYVXGNMOGVMR-GASGPIRDSA-N'])))
    #     ids_from_smiles_no_name = set(map(lambda x: x['molecule_chembl_id'],
    #         molecule.get(['CNC(=O)c1ccc(cc1)N(CC#C)Cc2ccc3nc(C)nc(O)c3c2',
    #         'Cc1cc2SC(C)(C)CC(C)(C)c2cc1\\N=C(/S)\\Nc3ccc(cc3)S(=O)(=O)N',
    #         'CC(C)C[C@H](NC(=O)[C@@H](NC(=O)[C@H](Cc1c[nH]c2ccccc12)NC(=O)[C@H]3CCCN3C(=O)C(CCCCN)CCCCN)C(C)(C)C)C(=O)O'])))
    #     ids_from_smiles_by_name = set(map(lambda x: x['molecule_chembl_id'],
    #         molecule.get(molecule_structures__canonical_smiles=['CNC(=O)c1ccc(cc1)N(CC#C)Cc2ccc3nc(C)nc(O)c3c2',
    #         'Cc1cc2SC(C)(C)CC(C)(C)c2cc1\\N=C(/S)\\Nc3ccc(cc3)S(=O)(=O)N',
    #         'CC(C)C[C@H](NC(=O)[C@@H](NC(=O)[C@H](Cc1c[nH]c2ccccc12)NC(=O)[C@H]3CCCN3C(=O)C(CCCCN)CCCCN)C(C)(C)C)C(=O)O'])))

    #     self.assertEqual(ids_from_ids_no_name, ids_from_ids_by_name)
    #     self.assertEqual(ids_from_ids_by_name, ids_from_keys_no_name)
    #     self.assertEqual(ids_from_keys_no_name, ids_from_keys_by_name)
    #     self.assertEqual(ids_from_keys_by_name, ids_from_smiles_no_name)
    #     self.assertEqual(ids_from_smiles_no_name, ids_from_smiles_by_name)


    # def test_molecule_resource_details(self):
    #     molecule = new_client.molecule
    #     molecule.set_format('json')
    #     chembl125_smiles = 'CCCCCCCCCCCCCCCCOP(=O)([O-])OCC[N+](C)(C)C'
    #     self.assertEqual(molecule.get(chembl125_smiles)['molecule_chembl_id'], 'CHEMBL125')
    #     self.assertEqual(molecule.filter(smiles=chembl125_smiles)[0]['molecule_chembl_id'], 'CHEMBL125')
    #     self.assertEqual(molecule.filter(molecule_structures__canonical_smiles=chembl125_smiles)[0]['molecule_chembl_id'], 'CHEMBL125')
    #     self.assertEqual(molecule.filter(molecule_structures__canonical_smiles__exact=chembl125_smiles)[0]['molecule_chembl_id'], 'CHEMBL125')
    #     self.assertTrue('CHEMBL125' in x['molecule_chembl_id'] for x in molecule.filter(molecule_structures__canonical_smiles__flexmatch=chembl125_smiles))
    #     approved_drugs = molecule.filter(max_phase=4)
    #     approved_drugs_count = len(approved_drugs)
    #     self.assertTrue(approved_drugs_count > 2000)
    #     len(approved_drugs[123])
    #     self.assertEqual(len([m for m in approved_drugs[2:5]]), 3)
    #     self.assertEqual(len([m for m in approved_drugs]), approved_drugs_count)
    #     with_components = molecule.get('CHEMBL1743070')
    #     self.assertIsNotNone(with_components)
    #     therapeutic = with_components['biotherapeutic']
    #     self.assertIn("molecule_chembl_id", therapeutic)
    #     self.assertIn("helm_notation", therapeutic)
    #     self.assertIn("description", therapeutic)
    #     self.assertIn("biocomponents", therapeutic)
    #     self.assertTrue(len(therapeutic['biocomponents']))
    #     component = therapeutic['biocomponents'][0]
    #     self.assertIn("sequence", component)
    #     self.assertIn("tax_id", component)
    #     self.assertIn("organism", component)
    #     self.assertIn("description", component)
    #     self.assertIn("component_type", component)
    #     self.assertIn("component_id", component)
    #     random_index = 11234 #randint(0, count - 1)
    #     random_elem = molecule.all()[random_index]
    #     self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
    #     self.assertIn('atc_classifications', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('availability_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('biotherapeutic', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('black_box_warning', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('chebi_par_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('chirality', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('dosed_ingredient', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('first_approval', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('first_in_class', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('helm_notation', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('indication_class', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('inorganic_flag', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('max_phase', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('molecule_hierarchy', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('molecule_properties', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('molecule_structures', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('molecule_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('natural_product', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('oral', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('parenteral', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('polymer_flag', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('pref_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('prodrug', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('structure_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('therapeutic_flag', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('topical', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('usan_stem', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('usan_stem_definition', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('usan_substem', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('usan_year', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('withdrawn_flag', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('withdrawn_year', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('withdrawn_country', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('withdrawn_reason', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('hba_lipinski', random_elem['molecule_properties'], 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('hbd_lipinski', random_elem['molecule_properties'], 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('num_lipinski_ro5_violations', random_elem['molecule_properties'], 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertEqual(len(molecule.get('CHEMBL1475')['atc_classifications']),2)
    #     self.assertTrue(molecule.filter(atc_classifications__level5='C07AB01').exists())
    #     self.assertEqual(len(molecule.filter(atc_classifications__level5='C07AB01')), 1)
    #     self.assertTrue(molecule.filter(atc_classifications__level5__startswith='A10').exists())
    #     self.assertEqual(len(molecule.filter(atc_classifications__level5__startswith='A10')),
    #         len(set([mol['molecule_chembl_id'] for
    #                  mol in molecule.filter(atc_classifications__level5__startswith='A10')])))
    #     atc_query = ['CHEMBL1073','CHEMBL1201496']
    #     molecules = new_client.molecule.get(atc_query)
    #     self.assertEqual(len(molecules),2)
    #     longest_chembl_smiles = r"CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC1OC(CO)C(O)C(O)C1O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+" \
    #                             r"]OC(CO)C(O)C(OC2OC(CO)C(O)C(O)C2O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC3OC(CO" \
    #                             r")C(O)C(O)C3O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC4OC(CO)C(O)C(O)C4O)C(O)CO.C" \
    #                             r"CCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC5OC(CO)C(O)C(O)C5O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]" \
    #                             r"OC(CO)C(O)C(OC6OC(CO)C(O)C(O)C6O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC7OC(CO)" \
    #                             r"C(O)C(O)C7O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC8OC(CO)C(O)C(O)C8O)C(O)CO.CC" \
    #                             r"CCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC9OC(CO)C(O)C(O)C9O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]O" \
    #                             r"C(CO)C(O)C(OC%10OC(CO)C(O)C(O)C%10O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC%11O" \
    #                             r"C(CO)C(O)C(O)C%11O)C(O)CO.CCCCCCCCCCCCCCCC[NH2+]OC(CO)C(O)C(OC%12OC(CO)C(O)C(O)C%12" \
    #                             r"O)C(O)CO.CCCCCCCCCC(C(=O)NCCc%13ccc(OP(=S)(Oc%14ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-" \
    #                             r"])cc%14)N(C)\N=C\c%15ccc(Op%16(Oc%17ccc(\C=N\N(C)P(=S)(Oc%18ccc(CCNC(=O)C(CCCCCCCCC" \
    #                             r")P(=O)(O)[O-])cc%18)Oc%19ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%19)cc%17)np(Oc%20c" \
    #                             r"cc(\C=N\N(C)P(=S)(Oc%21ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%21)Oc%22ccc(CCNC(=O)" \
    #                             r"C(CCCCCCCCC)P(=O)(O)[O-])cc%22)cc%20)(Oc%23ccc(\C=N\N(C)P(=S)(Oc%24ccc(CCNC(=O)C(CC" \
    #                             r"CCCCCCC)P(=O)(O)[O-])cc%24)Oc%25ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%25)cc%23)np" \
    #                             r"(Oc%26ccc(\C=N\N(C)P(=S)(Oc%27ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%27)Oc%28ccc(C" \
    #                             r"CNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%28)cc%26)(Oc%29ccc(\C=N\N(C)P(=S)(Oc%30ccc(CCNC(" \
    #                             r"=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%30)Oc%31ccc(CCNC(=O)C(CCCCCCCCC)P(=O)(O)[O-])cc%31)c" \
    #                             r"c%29)n%16)cc%15)cc%13)P(=O)(O)[O-]"

    #     res_1 = molecule.get(longest_chembl_smiles)
    #     self.assertEqual(res_1['molecule_chembl_id'], 'CHEMBL1628285')
    #     res_2 = molecule.filter(molecule_structures__canonical_smiles=longest_chembl_smiles)
    #     self.assertEqual(len(res_2), 1)
    #     self.assertEqual(res_1, res_2[0])
    #     res_3 = molecule.get(molecule_structures__canonical_smiles=longest_chembl_smiles)
    #     self.assertEqual(res_1, res_3[0])
    #     with_x_refs = molecule.get('CHEMBL25')
    #     self.assertIn('cross_references', with_x_refs, 'No cross references')
    #     x_refs = with_x_refs['cross_references']
    #     self.assertTrue(len(x_refs))
    #     single_ref = x_refs[0]
    #     self.assertIn('xref_id', single_ref, 'No xref_id in cross reference')
    #     self.assertIn('xref_name', single_ref, 'No xref_name in cross reference')
    #     self.assertIn('xref_src', single_ref, 'No xref_src in cross reference')

    #     molecule.set_format('xml')
    #     parseString(molecule.filter(molecule_properties__full_mwt__gt=600)
    #                         .filter(molecule_properties__aromatic_rings=4)
    #                         .filter(oral=True)[0])

    #     molecule.set_format('sdf')
    #     molstring = str(molecule.get('CHEMBL25'))
    #     inchi_from_molstring = utils.ctab2inchi(molstring)
    #     molecule.set_format('json')
    #     inchi_from_chembl = molecule.get('CHEMBL25')['molecule_structures']['standard_inchi']
    #     self.assertEqual(inchi_from_molstring, inchi_from_chembl)

    # @pytest.mark.timeout(TIMEOUT)
    # def test_molecule_unique(self):
    #     molecule = new_client.molecule
    #     molecule.set_format('json')
    #     mols = molecule.filter(molecule_properties__full_mwt__gte=100)[:5000]
    #     self.assertTrue(len(mols) == len(set([mol['molecule_chembl_id'] for mol in mols])))

    # @pytest.mark.timeout(TIMEOUT)
    # def test_molecule_form_resource(self):
    #     molecule_form = new_client.molecule_form
    #     count = len(molecule_form.all())
    #     self.assertTrue(count)
    #     self.assertTrue(all([form['is_parent'] == 'True' for form in
    #                          molecule_form.get(['CHEMBL328730', 'CHEMBL80863', 'CHEMBL80176'])]))
    #     self.assertEqual(len(molecule_form.get(molecule_chembl_id=['CHEMBL328730', 'CHEMBL80863', 'CHEMBL80176'])), 3)
    #     self.assertTrue(len(molecule_form.filter(parent_chembl_id='CHEMBL660')) > 3)
    #     asp = molecule_form.filter(molecule_chembl_id='CHEMBL25')
    #     self.assertTrue(len(asp) == 1)
    #     self.assertTrue(asp[0]['molecule_chembl_id'] == 'CHEMBL25')
    #     self.assertTrue(asp[0]['parent_chembl_id'] == 'CHEMBL25')
    #     via = molecule_form.filter(parent_chembl_id='CHEMBL192')
    #     self.assertTrue(len(via) == 2)
    #     self.assertTrue(via[0]['molecule_chembl_id'] == 'CHEMBL192')
    #     self.assertTrue(via[0]['parent_chembl_id'] == 'CHEMBL192')
    #     self.assertTrue(via[0]['is_parent'] == 'True')
    #     self.assertTrue(via[1]['molecule_chembl_id'] == 'CHEMBL1737')
    #     self.assertTrue(via[1]['parent_chembl_id'] == 'CHEMBL192')
    #     self.assertTrue(via[1]['is_parent'] == 'False')

    #     random_index = 6543 #randint(0, count - 1)
    #     random_elem = molecule_form.all()[random_index]
    #     self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
    #     self.assertIn('is_parent', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('parent_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     known_forms = molecule_form.get('CHEMBL211471')
    #     self.assertEqual(len(known_forms['molecule_forms']), 3)
    #     self.assertEqual(set([form['molecule_chembl_id'] for form in known_forms['molecule_forms']]),
    #                                                             set(["CHEMBL54126", "CHEMBL278020", "CHEMBL211471"]))
    #     self.assertTrue(any(form['is_parent'] == 'True' for form in known_forms['molecule_forms']))
    #     molecule_form.set_format('xml')
    #     parseString(molecule_form.all()[0])

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
        random_index = 800 #randint(0, count - 1)
        random_elem = protein_class.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('l1', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('l2', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('l3', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('l4', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('l5', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('l6', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('l7', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('l8', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('protein_class_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        protein_class.set_format('xml')
        parseString(protein_class.get(409))

    def test_protein_class_traversing(self):
        protein_class = new_client.protein_class
        protein_class.set_format('json')
        target_component = new_client.target_component
        target = new_client.target
        bromodomain_id = protein_class.filter(l3__icontains="Bromodomain")[0]['protein_class_id']
        bromodomain_family_target_ids = [t for t
                                         in [component['targets'] for component in
                                             target_component.filter(
                                                 protein_classifications__protein_classification_id=bromodomain_id)]]
        bromodomain_family_target_ids = [item['target_chembl_id'] for sublist in bromodomain_family_target_ids for item in sublist]
        bromodomain_family_targets = target.filter(target_chembl_id__in=bromodomain_family_target_ids)
        bromodomain_family_gene_names = []
        for target in bromodomain_family_targets:
            for component in target['target_components']:
                for synonym in component['target_component_synonyms']:
                    if synonym['syn_type'] == "GENE_SYMBOL":
                        bromodomain_family_gene_names.append(synonym['component_synonym'])

        self.assertIn('BRD1', bromodomain_family_gene_names)
        self.assertIn('BRD2', bromodomain_family_gene_names)
        self.assertIn('BRD3', bromodomain_family_gene_names)
        self.assertIn('BRD4', bromodomain_family_gene_names)
        self.assertIn('BRDT', bromodomain_family_gene_names)

    def test_protein_class_search(self):
        protein_class = new_client.protein_class
        protein_class.set_format('json')
        reader = protein_class.search('reader')
        self.assertEqual(len(reader), 10, len(reader))
        self.assertEqual(reader[0]['l2'], 'Reader', reader)
        self.assertEqual(reader[0]['l1'], 'Epigenetic regulator', reader[0]['l1'])
        bromodomain = protein_class.search('bromodomain')
        self.assertEqual(len(bromodomain), 1, len(bromodomain))
        self.assertEqual(bromodomain[0]['l3'], 'Bromodomain', bromodomain[0]['l3'])
        self.assertEqual(bromodomain[0]['l2'], 'Reader', bromodomain[0]['l2'])
        self.assertEqual(bromodomain[0]['l1'], 'Epigenetic regulator', bromodomain[0]['l1'])

    def test_similarity_resource(self):
        similarity = new_client.similarity
        res = similarity.filter(smiles="CO[C@@H](CCC#C\C=C/CCCC(C)CCCCC=C)C(=O)[O-]", similarity=70)
        self.assertTrue(all(Decimal(res[i]['similarity']) >= Decimal(res[i+1]['similarity']) for i in range(len(res)-1)), [Decimal(r['similarity']) for r in res])
        self.assertTrue(res.exists())

    def test_similarity_resource_a(self):
        similarity = new_client.similarity
        res = similarity.filter(smiles='[O--].[Fe++].OCC1OC(OC2C(CO)OC(OC3C(O)C(CO)OC(OCC4OC(OCC5OC(O)C(O)C(OC6OC(CO)C(O)C(OC7OC(COC8OC(COC9OC(CO)C(O)C(O)C9O)C(O)C(O)C8O)C(O)C(OC8OC(CO)C(O)C(OC9OC(CO)C(O)C(OC%10OC(COC%11OC(COC%12OC(COC%13OC(COC%14OC(COC%15OC(CO)C(O)C(O)C%15O)C(O)C(OC%15OC(CO)C(O)C%15O)C%14O)C(O)C(O)C%13O)C(O)C(O)C%12O)C(O)C(O)C%11O)C(O)C(OC%11OC(CO)C(O)C(O)C%11O)C%10O)C9O)C8O)C7O)C6O)C5O)C(O)C(O)C4O)C3O)C2O)C(O)C1O', similarity=70)
        self.assertTrue(res.exists())
        self.assertTrue(all(Decimal(res[i]['similarity']) >= Decimal(res[i+1]['similarity']) for i in range(len(res)-1)), [Decimal(r['similarity']) for r in res])
        self.assertTrue(len(res) > 5, len(res))

    # def test_similarity_resource_b(self):
    #     similarity = new_client.similarity
    #     res = similarity.filter(smiles="CC(C)OC(=O)[C@H](C)N[P@](=O)(OC[C@H]1O[C@@H](N2C=CC(=O)NC2=O)[C@](C)(F)[C@@H]1O)Oc3ccccc3", similarity=70)
    #     self.assertTrue(all(Decimal(res[i]['similarity']) >= Decimal(res[i+1]['similarity']) for i in range(len(res)-1)), [Decimal(r['similarity']) for r in res])
    #     self.assertTrue(res.exists())

    def test_similarity_resource_c(self):
        similarity = new_client.similarity
        res = similarity.filter(smiles="CC(=O)Oc1ccccc1C(=O)O", similarity=70)
        self.assertTrue(all(Decimal(res[i]['similarity']) >= Decimal(res[i+1]['similarity']) for i in range(len(res)-1)), [Decimal(r['similarity']) for r in res])
        self.assertTrue(res.exists())
        _ = len(res)
        most_similar = res[0]
        self.assertEqual(Decimal(most_similar['similarity']), Decimal(100.0))
        self.assertTrue('molecule_hierarchy' in res.filter(molecule_properties__cx_logp__gte=2.8).filter(molecule_properties__hbd__lte=5)[0])

    def test_similarity_resource_d(self):
        similarity = new_client.similarity
        res = similarity.filter(smiles="CC(=O)Oc1ccccc1C(=O)O", similarity=70).order_by('similarity')
        less_similar = res[0]
        self.assertTrue(Decimal(less_similar['similarity']) >= Decimal(69.999))
        self.assertTrue(all(Decimal(res[i]['similarity']) <= Decimal(res[i+1]['similarity']) for i in range(len(res)-1)), [Decimal(r['similarity']) for r in res])

    # def test_similarity_resource_e(self):
    #     similarity = new_client.similarity
    #     res = similarity.filter(smiles="COc1ccc2[C@@H]3[C@H](COc2c1)C(C)(C)OC4=C3C(=O)C(=O)C5=C4OC(C)(C)[C@@H]6COc7cc(OC)ccc7[C@H]56", similarity=70)
    #     most_similar = res[0]
    #     self.assertEqual(Decimal(most_similar['similarity']), Decimal(100.0))
    #     self.assertEqual(most_similar['molecule_chembl_id'], 'CHEMBL1')
    #     self.assertTrue(len(res) > 1000)
    #     self.assertTrue(all(Decimal(res[i]['similarity']) >= Decimal(res[i+1]['similarity']) for i in range(len(res)-1)), [Decimal(r['similarity']) for r in res])

    #     res1 = similarity.filter(smiles="COc1ccc2[C@@H]3[C@H](COc2c1)C(C)(C)OC4=C3C(=O)C(=O)C5=C4OC(C)(C)[C@@H]6COc7cc(OC)ccc7[C@H]56", similarity=70).only(['molecule_chembl_id', 'similarity'])
    #     most_similar = res1[0]
    #     self.assertEqual(list(most_similar.keys()), ['molecule_chembl_id', 'similarity'])
    #     self.assertEqual(Decimal(most_similar['similarity']), Decimal(100.0))
    #     self.assertEqual(most_similar['molecule_chembl_id'], 'CHEMBL1')
    #     self.assertTrue(len(res1) > 1000)
    #     self.assertTrue(all(Decimal(res1[i]['similarity']) >= Decimal(res1[i+1]['similarity']) for i in range(len(res1)-1)), [Decimal(r['similarity']) for r in res1])

    #     self.assertEquals(len(res), len(res1))

    # def test_similarity_resource_f(self):
    #     similarity = new_client.similarity
    #     res = similarity.filter(smiles="COc1ccc2[C@@H]3[C@H](COc2c1)C(C)(C)OC4=C3C(=O)C(=O)C5=C4OC(C)(C)[C@@H]6COc7cc(OC)ccc7[C@H]56", similarity=70).order_by('similarity')
    #     self.assertTrue(all(Decimal(res[i]['similarity']) <= Decimal(res[i+1]['similarity']) for i in range(len(res)-1)), [Decimal(r['similarity']) for r in res])
    #     less_similar = res[0]
    #     self.assertTrue(Decimal(less_similar['similarity']) >= Decimal(70))

    def test_similarity_resource_g(self):
        similarity = new_client.similarity
        res = similarity.filter(smiles="COc1ccc2[C@@H]3[C@H](COc2c1)C(C)(C)OC4=C3C(=O)C(=O)C5=C4OC(C)(C)[C@@H]6COc7cc(OC)ccc7[C@H]56", similarity=70).filter(molecule_properties__aromatic_rings=2)
        self.assertTrue(len(res) > 5)

    def test_similarity_resource_h(self):
        similarity = new_client.similarity
        res = similarity.filter(chembl_id="CHEMBL25", similarity=100)
        res.set_format('json')
        self.assertTrue(len(res) > 0)
        res = similarity.filter(smiles="CC(=O)Oc1ccccc1C(=O)O", similarity=100)
        res.set_format('json')
        self.assertTrue(len(res) > 1)
        res = similarity.filter(chembl_id="CHEMBL25", similarity=70)
        res.set_format('json')
        self.assertTrue(len(res) >= 5)
        self.assertTrue(
            all(Decimal(res[i]['similarity']) >= Decimal(res[i + 1]['similarity']) for i in range(len(res) - 1)),
            [Decimal(r['similarity']) for r in res])
        self.assertTrue("CHEMBL2296002" in [r['molecule_chembl_id'] for r in res])

    def test_similarity_resource_j(self):
        similarity = new_client.similarity
        similarity.set_format('sdf')
        res = similarity.filter(smiles="CO[C@@H](CCC#C\C=C/CCCC(C)CCCCC=C)C(=O)[O-]", similarity=70)
        self.assertTrue(len(res))

    # def test_get_all_natural_products(self):
    #     document = new_client.document
    #     docs = document.filter(journal="J. Nat. Prod.").only('document_chembl_id')
    #     docs.set_format('json')
    #     self.assertTrue(len(docs) >= 6000)
    #     compound_record = new_client.compound_record
    #     records = compound_record.filter(document_chembl_id__in=[doc['document_chembl_id'] for doc in docs]).only(['document_chembl_id', 'molecule_chembl_id'])
    #     records.set_format('json')
    #     self.assertTrue(len(records) >= 45000)
    #     molecule = new_client.molecule
    #     natural_products = molecule.filter(molecule_chembl_id__in=[rec['molecule_chembl_id'] for rec in records]).only('compoundstructures')
    #     natural_products.set_format('json')
    #     self.assertTrue(len(natural_products) >= 34000)

    def test_source_resource(self):
        source = new_client.source
        count = len(source.all())
        self.assertTrue(count)
        self.assertTrue(source.filter(src_short_name="ATLAS").exists())
        self.assertEqual([src['src_id'] for src in source.all().order_by('src_id')[0:5]], [0, 1, 2, 3, 4])
        random_index = 5
        # randint(0, count - 1)
        random_elem = source.all()[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('src_description', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('src_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('src_short_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        source.set_format('xml')
        parseString(source.filter(src_short_name="DRUGS")[0])

    def test_substructure_resource_a(self):
        substructure = new_client.substructure
        with self.assertRaisesRegex(HttpBadRequest, 'Structure or identifier required'):
            substructure[0]

    def test_substructure_resource_b(self):
        substructure = new_client.substructure
        res = substructure.filter(smiles="CCC#C\C=C/CCC")
        self.assertTrue(res.exists())
        slice = res[:6]
        self.assertEqual(len([m for m in slice]), 6)
        self.assertTrue(len(res) > 10)

    def test_substructure_resource_c(self):
        substructure = new_client.substructure
        res = substructure.filter(smiles="CN(CCCN)c1cccc2ccccc12")
        self.assertTrue(res.exists())
        count = len(res)

        res1 = substructure.filter(smiles="CN(CCCN)c1cccc2ccccc12").only('molecule_chembl_id')
        self.assertTrue(res1.exists())
        count1 = len(res1)
        self.assertEqual(count, count1)

        random_index = 80 #randint(0, count - 1)
        random_elem = res[random_index]
        self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
        self.assertIn('availability_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('black_box_warning', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('chebi_par_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('chirality', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('dosed_ingredient', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('first_approval', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('first_in_class', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('indication_class', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('inorganic_flag', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('max_phase', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('molecule_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('molecule_hierarchy', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('molecule_properties', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('molecule_structures', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('molecule_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('natural_product', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('oral', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('parenteral', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('polymer_flag', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('pref_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('prodrug', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('structure_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('therapeutic_flag', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('topical', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('usan_stem', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('usan_stem_definition', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('usan_substem', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        self.assertIn('usan_year', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
        res.set_format('xml')
        parseString(res[0])

    def test_substructure_resource_d(self):
        substructure = new_client.substructure
        res = substructure.filter(chembl_id="CHEMBL25")
        res.set_format('json')
        self.assertTrue(len(res) > 300)
        self.assertEqual(res[0]['molecule_chembl_id'], 'CHEMBL25')

    def test_substructure_resource_e(self):
        substructure = new_client.substructure
        self.assertRaisesRegex(HttpNotFound, 'No chemical structure defined', len, substructure.filter(chembl_id="CHEMBL1201822"))

    def test_substructure_resource_f(self):
        substructure = new_client.substructure
        substructure.set_format('sdf')
        res = substructure.filter(smiles="CN(CCCN)c1cccc2ccccc12")
        self.assertTrue(len(res))

    # def test_target_resource(self):
    #     target = new_client.target
    #     count = len(target.all())
    #     self.assertTrue(count)
    #     self.assertTrue(target.filter(organism="Homo sapiens").filter(target_type="SINGLE PROTEIN").exists())
    #     self.assertTrue(target.filter(target_components__accession="Q13936").exists())
    #     self.assertEqual(len(target.filter(target_components__accession="Q13936")), 3)
    #     self.assertNotEqual(target.all().order_by('species_group_flag')[0]['target_chembl_id'],target.all().order_by('-species_group_flag')[0]['target_chembl_id'])
    #     self.assertNotEqual(target.all().order_by('target_chembl_id')[0]['target_chembl_id'],target.all().order_by('-target_chembl_id')[0]['target_chembl_id'])
    #     self.assertEqual( [t['pref_name'] for t in target.get(['CHEMBL1927', 'CHEMBL1929', 'CHEMBL1930'])],
    #     ['Thioredoxin reductase 1',
    #      'Xanthine dehydrogenase',
    #      'Vitamin k epoxide reductase complex subunit 1 isoform 1'])
    #     random_index = 8888  # randint(0, count - 1)
    #     random_elem = target.all()[random_index]
    #     self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
    #     self.assertIn('organism', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('tax_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('pref_name', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('species_group_flag', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('target_chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('target_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('target_components', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     has_components = target.get('CHEMBL247')
    #     target_component = has_components['target_components'][0]
    #     self.assertIn('accession', target_component, 'One of required fields not found in resource {0}'.format(target_component))
    #     self.assertIn('component_id', target_component, 'One of required fields not found in resource {0}'.format(target_component))
    #     self.assertIn('component_type', target_component, 'One of required fields not found in resource {0}'.format(target_component))
    #     self.assertIn('relationship', target_component, 'One of required fields not found in resource {0}'.format(target_component))
    #     self.assertIn('component_description', target_component, 'One of required fields not found in resource {0}'.format(target_component))
    #     self.assertIn('target_component_synonyms', target_component, 'One of required fields not found in resource {0}'.format(target_component))
    #     synonym = target_component['target_component_synonyms'][0]
    #     self.assertIn('component_synonym', synonym, 'One of required fields not found in  resource {0}'.format(synonym))
    #     self.assertIn('syn_type', synonym, 'One of required fields not found in  resource {0}'.format(synonym))
    #     self.assertIn('target_component_xrefs', target_component,
    #                   'One of required fields not found in resource {0}'.format(target_component))
    #     component_xfref = target_component['target_component_xrefs'][0]
    #     self.assertIn('xref_src_db', component_xfref,
    #                   'One of required fields not found in resource {0}'.format(component_xfref))
    #     self.assertIn('xref_id', component_xfref,
    #                   'One of required fields not found in resource {0}'.format(component_xfref))
    #     self.assertIn('xref_name', component_xfref,
    #                   'One of required fields not found in resource {0}'.format(component_xfref))

    #     gene_name = 'GABRB2'
    #     targets_for_gene = target.filter(target_components__target_component_synonyms__component_synonym__icontains=gene_name)
    #     self.assertEqual(len(targets_for_gene), 18)
    #     shortcut = target.filter(target_synonym__icontains=gene_name)
    #     self.assertListEqual([x for x in targets_for_gene], [x for x in shortcut])
    #     only_components = target.filter(target_synonym__icontains=gene_name).only(['target_components'])
    #     first = only_components[0]
    #     self.assertEqual(list(first.keys()), ['target_components'])

    #     gene_name = 'flap'
    #     targets_for_gene = target.filter(target_components__target_component_synonyms__component_synonym__icontains=gene_name)
    #     self.assertEqual(len(targets_for_gene), 5)
    #     shortcut = target.filter(target_synonym__icontains=gene_name)
    #     self.assertListEqual([x for x in targets_for_gene], [x for x in shortcut])
    #     with_x_refs = target.get('CHEMBL2074')
    #     self.assertIn('cross_references', with_x_refs, 'No cross references')
    #     x_refs = with_x_refs['cross_references']
    #     self.assertTrue(len(x_refs))
    #     single_ref = x_refs[0]
    #     self.assertIn('xref_id', single_ref, 'No xref_id in cross reference')
    #     self.assertIn('xref_name', single_ref, 'No xref_name in cross reference')
    #     self.assertIn('xref_src', single_ref, 'No xref_src in cross reference')
    #     target.set_format('xml')
    #     parseString(target.all()[0])
    #     with self.assertRaisesRegex(HttpBadRequest, 'Related Field got invalid lookup: contains'):
    #         len(target.search('trypsin').filter(target_type__contains='Single').filter(organism_contains='Sus scrofa'))

    def test_target_search(self):
        target = new_client.target
        target.set_format('json')
        res = target.search('lipoxygenase')
        self.assertEqual(len(res), 23)

    # def test_target_component_resource(self):
    #     target_component = new_client.target_component
    #     count = len(target_component.all())
    #     self.assertTrue(count)
    #     self.assertTrue('sequence' in target_component.get(1295))
    #     self.assertEqual([targcomp['component_id'] for targcomp in target_component.all().order_by('component_id')[0:5]],
    #         [1, 2, 3, 4, 5])
    #     has_synonyms = target_component.get(375)
    #     self.assertIn('target_component_synonyms', has_synonyms, 'One of required fields not found in resource {0}'.format(has_synonyms))
    #     synonym = has_synonyms['target_component_synonyms'][0]
    #     self.assertIn('component_synonym', synonym, 'One of required fields not found in resource {0}'.format(synonym))
    #     self.assertIn('syn_type', synonym, 'One of required fields not found in resource {0}'.format(synonym))
    #     self.assertIn('target_component_xrefs', has_synonyms, 'One of required fields not found in resource {0}'.format(has_synonyms))
    #     component_xref = has_synonyms['target_component_xrefs'][0]
    #     self.assertIn('xref_src_db', component_xref, 'One of required fields not found in resource {0}'.format(component_xref))
    #     self.assertIn('xref_id', component_xref, 'One of required fields not found in resource {0}'.format(component_xref))
    #     self.assertIn('xref_name', component_xref, 'One of required fields not found in resource {0}'.format(component_xref))
    #     target_component.set_format('xml')
    #     random_index = 5432  # randint(0, count - 1)
    #     random_elem = target_component.all()[random_index]
    #     self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
    #     self.assertIn('accession', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('sequence', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('component_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('component_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('description', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('go_slims', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('organism', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('tax_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     parseString(target_component.all()[0])

    def test_traversing(self):
        new_client.molecule.set_format('json')
        molecules = new_client.molecule.filter(atc_classifications__level5__startswith='A10')
        self.assertTrue(molecules.exists())
        molecule_ids = list(map(lambda d: d['molecule_chembl_id'], molecules))
        activities = new_client.activity.filter(molecule_chembl_id__in=molecule_ids)
        self.assertTrue(activities.exists())
        activities_1 = new_client.activity.get(molecule_chembl_id=molecule_ids)
        self.assertEqual(len(activities), len(activities_1))

    # def test_chembl_id_lookup_resource(self):
    #     chembl_id_lookup = new_client.chembl_id_lookup
    #     count = len(chembl_id_lookup.all())
    #     self.assertTrue(count)
    #     self.assertTrue(chembl_id_lookup.filter(entity_type="TARGET").exists())
    #     random_index = 5678  # randint(0, count - 1)
    #     random_elem = chembl_id_lookup.all()[random_index]
    #     self.assertNotEqual(chembl_id_lookup.all().order_by('chembl_id')[0]['chembl_id'], chembl_id_lookup.all().order_by('-chembl_id')[0]['chembl_id'])
    #     self.assertNotEqual(chembl_id_lookup.all().order_by('entity_type')[0]['chembl_id'], chembl_id_lookup.all().order_by('-entity_type')[0]['chembl_id'])
    #     self.assertNotEqual(chembl_id_lookup.all().order_by('status')[0]['chembl_id'], chembl_id_lookup.all().order_by('-status')[0]['chembl_id'])
    #     self.assertIsNotNone(random_elem, "Can't get {0} element from the list".format(random_index))
    #     self.assertIn('chembl_id', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('entity_type', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('status', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     self.assertIn('resource_url', random_elem, 'One of required fields not found in resource {0}'.format(random_elem))
    #     chembl_id_lookup.set_format('xml')
    #     parseString(chembl_id_lookup.filter(entity_type="COMPOUND").filter(status="ACTIVE")[0])

    def test_chembl_id_lookup_search(self):
        chembl_id_lookup = new_client.chembl_id_lookup
        chembl_id_lookup.set_format('json')
        res = chembl_id_lookup.search('morphine')
        self.assertTrue(800 < len(res) < 1500, 'len(res) is actually {0}'.format(len(res)))
        by_score = sorted([x for x in res], key=lambda x: x['score'], reverse=True)
        self.assertEqual(by_score[0]['chembl_id'], 'CHEMBL2103744')
        self.assertEqual(by_score[0]['entity_type'], 'COMPOUND')

    # def test_unichem_get_src_compound_ids_from_compound_id(self):
    #     ret = unichem.get('CHEMBL12', 1)
    #     self.assertTrue(len(ret) > 10)
    #     ret = unichem.get('CHEMBL12')
    #     self.assertTrue(len(ret) > 10)
    #     self.assertTrue('CHEMBL12' in [x['src_compound_id'] for x in ret])
    #     self.assertEqual({r['src_id'] for r in ret}, {'10', '9', '8', '24', '25', '26', '27', '21', '22',
    #                                                   '23', '29', '1', '3', '2', '4', '7', '6', '11', '12',
    #                                                   '15', '14', '17', '18', '31', '34', '32', '37'})
    #     ret = unichem.get('CHEMBL12', 1, 2)
    #     self.assertEqual(len(ret), 1)
    #     self.assertEqual(ret[0]['src_compound_id'], 'DB00829')
    #     ret = unichem.get('AIN')
    #     self.assertEqual(len(ret), 1)
    #     # self.assertEqual(ret['3'][0]['src_compound_id'], 'CHEMBL25', str(ret))

    def test_unichem_get_src_compound_ids_all_from_compound_id(self):
        ret = unichem.get('CHEMBL12', 1, all=True)
        self.assertTrue(len(ret) > 10)
        self.assertTrue('diazepam' in [x['src_compound_id'] for x in ret])
        ret = unichem.get('CHEMBL12', 1, 2, all=True)
        self.assertEqual(len(ret), 2)
        self.assertTrue('DB00829' in [x['src_compound_id'] for x in ret])
        self.assertTrue('DB07699' in [x['src_compound_id'] for x in ret])

    def test_unichem_get_mapping(self):
        ret = unichem.map(4, 1)
        self.assertTrue(len(ret) > 4000)
        self.assertTrue('CHEMBL2333444' in [x['1'] for x in ret])

    def test_unichem_get_src_compound_ids_from_inchi_key(self):
        ret = unichem.get('AAOVKJBEBIDNHE-UHFFFAOYSA-N')
        self.assertTrue(len(ret) > 10)
        self.assertTrue('CHEMBL12' in [x['src_compound_id'] for x in ret])

    def test_unichem_get_src_compound_ids_all_from_inchi_key(self):
        ret = unichem.get('AAOVKJBEBIDNHE-UHFFFAOYSA-N', all=True)
        self.assertTrue(len(ret) > 10)
        self.assertTrue('diazepam' in [x['src_compound_id'] for x in ret])

    def test_unichem_get_all_src_ids(self):
        ret = unichem.src()
        self.assertTrue(len(ret) > 25)
        self.assertTrue('1' in [x['src_id'] for x in ret])

    def test_unichem_get_source_information(self):
        ret = unichem.src(1)
        self.assertEqual(len(ret),1)
        self.assertEqual(ret[0]['name_label'],'ChEMBL')
        self.assertEqual(ret[0]['name'],'chembl')
        self.assertEqual(ret[0]['src_id'],'1')

    def test_unichem_get_structure(self):
        ret = unichem.structure('CHEMBL12',1)
        self.assertEqual(len(ret),1)
        self.assertEqual(ret[0]['standardinchi'], 'InChI=1S/C16H13ClN2O/c1-19-14-8-7-12(17)9-13(14)16(18-10-15(19)20)11-5-3-2-4-6-11/h2-9H,10H2,1H3')
        self.assertEqual(ret[0]['standardinchikey'], 'AAOVKJBEBIDNHE-UHFFFAOYSA-N')

    def test_unichem_get_structure_all(self):
        ret = unichem.structure('CHEMBL12',1, all=True)
        self.assertEqual(len(ret),1)
        self.assertEqual(ret[0]['assignment'], '1')
        self.assertEqual(ret[0]['standardinchi'], 'InChI=1S/C16H13ClN2O/c1-19-14-8-7-12(17)9-13(14)16(18-10-15(19)20)11-5-3-2-4-6-11/h2-9H,10H2,1H3')
        self.assertEqual(ret[0]['standardinchikey'], 'AAOVKJBEBIDNHE-UHFFFAOYSA-N')

    def test_unichem_get_url_for_src_compound_ids_from_src_compound_id(self):
        ret = unichem.get('CHEMBL12',1, 2, url=True)
        self.assertEqual(len(ret),1)
        self.assertEqual(ret[0]['url'], 'http://www.drugbank.ca/drugs/DB00829')
        ret = unichem.get('CHEMBL490',1, 15, url=True)
        self.assertEqual(len(ret),1)
        self.assertEqual(ret[0]['url'], 'https://www.surechembl.org/chemical/SCHEMBL27799')

    def test_unichem_get_src_compound_ids_all_from_obsolete_compound_id(self):
        ret = unichem.get('DB07699',2)
        self.assertTrue(len(ret) > 25)
        self.assertTrue('J2.044C' in [x['src_compound_id'] for x in ret])
        ret = unichem.get('DB07699',2,1)
        self.assertEqual(len(ret),1)
        self.assertEqual(ret[0]['assignment'], '1')
        self.assertEqual(ret[0]['UCI'], '304698')
        self.assertEqual(ret[0]['src_compound_id'], 'CHEMBL12')

    def test_unichem_get_src_compound_ids_from_inchi_key(self):
        ret = unichem.get('AAOVKJBEBIDNHE-UHFFFAOYSA-N', verbose=True)
        self.assertTrue(len(ret) > 20)
        self.assertTrue('https://www.ebi.ac.uk/chembl/' in [x['src_url'] for x in ret])
        self.assertTrue('aux_for_url' in ret[0])
        self.assertTrue('base_id_url' in ret[0])
        self.assertTrue('base_id_url_available' in ret[0])
        self.assertTrue('description' in ret[0])
        self.assertTrue('name' in ret[0])
        self.assertTrue('name_label' in ret[0])
        self.assertTrue('name_long' in ret[0])
        self.assertTrue('src_compound_id' in ret[0])
        self.assertTrue('src_id' in ret[0])

    def test_unichem_get_auxiliary_mappings(self):
        ret = unichem.map(20)
        self.assertTrue(len(ret) > 1500)
        self.assertTrue('Vinblastine.html' in [x['auxiliary data'] for x in ret])
        self.assertTrue('gsk1070916' in [x['src_compound_id'] for x in ret])

    def test_unichem_get_connectivity_data_from_inchi_key(self):
        ret = unichem.connectivity('QJVHTELASVOWBE-YBABNSIOSA-N',c=4,h=1)
        self.assertEqual(len(ret),1)
        self.assertTrue(len(ret['1']) > 500)
        self.assertTrue('CHEMBL295075' in [x[0] for x in ret['1']])
        ret = unichem.connectivity('QJVHTELASVOWBE-YBABNSIOSA-N',a=1,c=3)
        self.assertEqual(len(ret),1)
        self.assertEqual(len(ret['1']),1)
        self.assertTrue(len(ret['1'][0]['src_matches']) > 20)
        self.assertEqual(ret['1'][0]['Full Query InChIKey'], 'QJVHTELASVOWBE-YBABNSIOSA-N')
        self.assertEqual(ret['1'][0]['Full Query InChI'], 'InChI=1S/C16H19N3O5S.C8H9NO5/c1-16(2)11(15(23)24)19-13(22)10(14(19)25-16)18-12(21)9(17)7-3-5-8(20)6-4-7;10-2-1-4-7(8(12)13)9-5(11)3-6(9)14-4/h3-6,9-11,14,20H,17H2,1-2H3,(H,18,21)(H,23,24);1,6-7,10H,2-3H2,(H,12,13)/b;4-1-/t9?,10-,11+,14-;6-,7-/m11/s1')
        self.assertEqual(ret['1'][0]['name_long'], 'ChEMBL')
        ret = unichem.connectivity('QJVHTELASVOWBE',a=1,c=3)
        self.assertEqual(len(ret),1)
        self.assertEqual(len(ret['1']),1)
        self.assertTrue(len(ret['1'][0]['src_matches']) > 20)
        self.assertEqual(ret['1'][0]['Full Query InChIKey'], 'QJVHTELASVOWBE')
        self.assertEqual(ret['1'][0]['Full Query InChI'], 'InChI=1S/C16H19N3O5S.C8H9NO5/c1-16(2)11(15(23)24)19-13(22)10(14(19)25-16)18-12(21)9(17)7-3-5-8(20)6-4-7;10-2-1-4-7(8(12)13)9-5(11)3-6(9)14-4/h3-6,9-11,14,20H,17H2,1-2H3,(H,18,21)(H,23,24);1,6-7,10H,2-3H2,(H,12,13)')
        self.assertEqual(ret['1'][0]['name_long'], 'ChEMBL')

    def test_unichem_get_connectivity_data_from_src_compound_id(self):
        ret = unichem.connectivity('CHEMBL121',1,c=4,h=1)
        self.assertEqual(len(ret),1)
        self.assertTrue(len(ret['1']) > 400)
        self.assertTrue('SCHEMBL2355017' in [x[0] for x in ret['1']])
        ret = unichem.connectivity('CHEMBL121',1)
        self.assertEqual(len(ret),1)
        self.assertTrue(len(ret['1'][0]['src_matches']) > 2)
        self.assertEqual(ret['1'][0]['Full Query InChIKey'], 'YASAKCUCGLMORW-UHFFFAOYSA-N')
        self.assertEqual(ret['1'][0]['Full Query InChI'], 'InChI=1S/C18H19N3O3S/c1-21(16-4-2-3-9-19-16)10-11-24-14-7-5-13(6-8-14)12-15-17(22)20-18(23)25-15/h2-9,15H,10-12H2,1H3,(H,20,22,23)')
        self.assertEqual(ret['1'][0]['name_long'], 'ChEMBL')

    def test_unichem_get_inchi_from_inchi_key(self):
        ret = unichem.inchiFromKey('AAOVKJBEBIDNHE-UHFFFAOYSA-N')
        self.assertEqual(len(ret),1)
        self.assertEqual(ret[0]['standardinchi'], 'InChI=1S/C16H13ClN2O/c1-19-14-8-7-12(17)9-13(14)16(18-10-15(19)20)11-5-3-2-4-6-11/h2-9H,10H2,1H3')

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

    # def test_utils_marvin(self):
    #     smiles = 'O=C(Oc1ccccc1C(=O)O)C' # aspirin
    #     mrv = json.loads(utils.molExport(structure=smiles, parameters="mrv"))['structure']
    #     self.assertIsNotNone(mrv)
    #     self.assertTrue('<cml><MDocument><MChemicalStruct>' in mrv)
    #     hdr = utils.hydrogenize(structure=str(mrv), parameters={"method":"HYDROGENIZE"}, input_format="mrv")
    #     self.assertEqual(hdr.count('<atom elementType="H"'), 8)
    #     cln = utils.clean(structure=mrv)
    #     self.assertTrue('<cml><MDocument><MChemicalStruct>' in cln)
    #     self.assertTrue('H H H H H H H H' not in cln)
    #     cml = "<cml><MDocument><MChemicalStruct><molecule molID=\"m1\"><atomArray><atom id=\"a1\" elementType=\"C\" x2=\"-3.1249866416667733\" y2=\"-0.5015733293207466\"/><atom id=\"a2\" elementType=\"C\" x2=\"-4.458533297665067\" y2=\"-1.2715733231607467\"/><atom id=\"a3\" elementType=\"C\" x2=\"-4.458533297665067\" y2=\"-2.81175997750592\"/><atom id=\"a4\" elementType=\"C\" x2=\"-3.1249866416667733\" y2=\"-3.58175997134592\"/><atom id=\"a5\" elementType=\"C\" x2=\"-1.7912533190033066\" y2=\"-2.81175997750592\"/><atom id=\"a6\" elementType=\"C\" x2=\"-1.7912533190033066\" y2=\"-1.2715733231607467\"/><atom id=\"a7\" elementType=\"C\" x2=\"-0.45751999633984003\" y2=\"-0.5013866626555733\"/><atom id=\"a8\" elementType=\"O\" x2=\"-0.45751999633984003\" y2=\"1.0384266583592534\"/><atom id=\"a9\" elementType=\"C\" x2=\"0.87583999299328\" y2=\"-1.2713866564955734\"/><atom id=\"a10\" elementType=\"C\" x2=\"0.87583999299328\" y2=\"-2.8113866441755735\"/></atomArray><bondArray><bond atomRefs2=\"a1 a2\" order=\"2\"/><bond atomRefs2=\"a2 a3\" order=\"1\"/><bond atomRefs2=\"a3 a4\" order=\"2\"/><bond atomRefs2=\"a4 a5\" order=\"1\"/><bond atomRefs2=\"a5 a6\" order=\"2\"/><bond atomRefs2=\"a6 a1\" order=\"1\"/><bond atomRefs2=\"a6 a7\" order=\"1\"/><bond atomRefs2=\"a7 a9\" order=\"1\"/><bond atomRefs2=\"a9 a10\" order=\"1\"/><bond atomRefs2=\"a7 a8\" order=\"1\"><bondStereo>W</bondStereo></bond></bondArray></molecule></MChemicalStruct></MDocument></cml>"
    #     stereo_info = json.loads(utils.cipStereoInfo(structure=cml))
    #     self.assertEqual(stereo_info['tetraHedral'][0], {u'atomIndex': 6, u'chirality': u'S'})

    # def test_utils_standardisation(self):
    #     mol = utils.smiles2ctab("[Na]OC(=O)c1ccccc1")
    #     br = utils.breakBonds(mol)
    #     smiles = utils.ctab2smiles(br).split()[2]
    #     self.assertTrue(smiles in ('[Na+].O=C([O-])c1ccccc1', 'O=C([O-])c1ccccc1.[Na+]'))
    #     mol = utils.smiles2ctab("C(C(=O)[O-])(Cc1n[n-]nn1)(C[NH3+])(C[N+](=O)[O-])")
    #     ne = utils.neutralise(mol)
    #     smiles = utils.ctab2smiles(ne).split()[2]
    #     self.assertEqual(smiles, 'NCC(Cc1nn[nH]n1)(C[N+](=O)[O-])C(=O)O')
    #     mol = utils.smiles2ctab("Oc1nccc2cc[nH]c(=N)c12")
    #     ru = utils.rules(mol)
    #     smiles = utils.ctab2smiles(ru).split()[2]
    #     self.assertEqual(smiles, 'Nc1nccc2cc[nH]c(=O)c12')
    #     mol = utils.smiles2ctab("[Na+].OC(=O)Cc1ccc(CN)cc1.OS(=O)(=O)C(F)(F)F")
    #     un = utils.unsalt(mol)
    #     smiles = utils.ctab2smiles(un).split()[2]
    #     self.assertEqual(smiles, 'NCc1ccc(CC(=O)O)cc1')
    #     mol = utils.smiles2ctab("[Na]OC(=O)Cc1ccc(C[NH3+])cc1.c1nnn[n-]1.O")
    #     st = utils.standardise(mol)
    #     smiles = utils.ctab2smiles(st).split()[2]
    #     self.assertEqual(smiles, 'NCc1ccc(CC(=O)O)cc1')

    def test_utils_svg_images(self):
        benzene = 'c1ccccc1'
        svg1 = utils.smiles2svg(benzene)
        self.assertTrue(len(svg1) > 2000)
        self.assertTrue(svg1.startswith('<?xml version='), svg1)
        mol = utils.smiles2ctab(benzene)
        svg2 = utils.ctab2svg(mol)
        self.assertEqual(svg1, svg2)

    def test_utils_mcs(self):
        smiles = ['c1ccccc1', 'c1ccccc1C', 'c1ccccc1O']
        mols = [utils.smiles2ctab(smile) for smile in smiles]
        sdf = ''.join(mols)
        result = utils.mcs(sdf)
        self.assertEqual(result, '[#6]1=[#6]-[#6]=[#6]-[#6]=[#6]-1')

    # def test_utils_osra(self):
    #     aspirin = 'CC(=O)Oc1ccccc1C(=O)O'
    #     im = utils.smiles2image(aspirin)
    #     mol = utils.image2ctab(im)
    #     smiles = utils.ctab2smiles(mol).split()[2]
    #     self.assertEqual(smiles, aspirin)

    # def test_command_line_tools(self):
    #     viagra = resolve('viagra')
    #     self.assertEqual(viagra[0]['molecule_chembl_id'], 'CHEMBL1737')
    #     parent = get_parents(viagra)
    #     self.assertEqual(parent[0]['molecule_chembl_id'], 'CHEMBL192')

    def test_sdf_batch_processing(self):
        new_client.molecule.set_format('sdf')
        records1 = new_client.molecule.get(
            ['CHEMBL6498', 'CHEMBL6499', 'CHEMBL6505'])
        records2 = new_client.molecule.get(
            ['XSQLHVPPXBBUPP-UHFFFAOYSA-N', 'JXHVRXRRSSBGPY-UHFFFAOYSA-N', 'TUHYVXGNMOGVMR-GASGPIRDSA-N'])
        records3 = new_client.molecule.get(['C#CCN(Cc1ccc2nc(C)nc(O)c2c1)c1ccc(C(=O)NC)cc1',
                                            'Cc1cc2c(cc1/N=C(\S)Nc1ccc(S(N)(=O)=O)cc1)C(C)(C)CC(C)(C)S2',
                                            'CC(C)C[C@H](NC(=O)[C@@H](NC(=O)[C@H](Cc1c[nH]c2ccccc12)NC(=O)[C@H]1CCCN1C(=O)C(CCCCN)CCCCN)C(C)(C)C)C(=O)O'])
        self.assertTrue(records1 == records2 == records3)

if __name__ == '__main__':
    unittest.main()
