__author__ = 'mnowotka'

from chembl_webresource_client.settings import Settings
from chembl_webresource_client import *
from chembl_webresource_client.utils import utils
import json
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
        self.assertEqual(targets.get('CHEMBL2476')['targetType'], 'SINGLE PROTEIN')
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
        self.assertEqual(cs[0]['preferredCompoundName'], 'ISOTRETINOIN')
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
                         'Stem cell growth factor receptor')

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
        self.assertEqual(len(js1), 33)
        self.assertTrue('path' in js1[0] and 'stroke' in js1[0] and 'type' in js1[0])
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
