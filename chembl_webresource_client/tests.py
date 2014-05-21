__author__ = 'mnowotka'

from chembl_webresource_client.settings import Settings
from chembl_webresource_client import *
import unittest


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
        self.assertEqual(targets.get('CHEMBL2477')['targetType'], 'SINGLE PROTEIN')
        self.assertTrue(len(targets.bioactivities('CHEMBL240')) > 10000)
        all = targets.get_all()
        self.assertTrue(len(all) > 10000)
        self.assertTrue(all[0]['bioactivityCount'] >= all[-1]['bioactivityCount'])
        self.assertEqual(targets.get(uniprot='Q13936')['proteinAccession'], 'Q13936')
        self.assertEqual(len(targets.get(['CHEMBL240', 'CHEMBL2477'])), 2)
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
        cs = compounds.get(smiles="C\C(=C/C=C/C(=C/C(=O)O)/C)\C=C\C1=C(C)CCCC1(C)C")
        self.assertTrue(len(cs) >= 9)
        self.assertEqual(cs[0]['preferredCompoundName'], 'TRETINOIN')
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
        self.assertEqual(compounds.drug_mechanisms('CHEMBL1642')[1]['name'],
                         'Platelet-derived growth factor receptor beta')

if __name__ == '__main__':
    unittest.main()
