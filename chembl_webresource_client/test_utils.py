import unittest2 as unittest
from chembl_webresource_client.scripts.utils import resolve
from chembl_webresource_client.scripts.utils import sdf_split
from chembl_webresource_client.scripts.utils import get_parents
from chembl_webresource_client.scripts.utils import resolve_target
from chembl_webresource_client.scripts.utils import get_serializer
from chembl_webresource_client.scripts.utils import inspect_synonyms
from chembl_webresource_client.scripts.utils import convert_to_smiles
from chembl_webresource_client.scripts.utils import mols_to_targets
from chembl_webresource_client.scripts.utils import targets_to_mols
from chembl_webresource_client.scripts.utils import enhance_mols_with_parents
from chembl_webresource_client.scripts.utils import inchi_key_regex, chembl_id_regex, smiles_regex
from chembl_webresource_client.utils import utils
from chembl_webresource_client.elastic_client import ElasticClient
from io import StringIO


sdf = '''
  SciTegic12231509382D

 31 35  0  0  0  0            999 V2000
   11.2581  -12.0726    0.0000 F   0  0
    9.1585   -8.7448    0.0000 C   0  0
   11.1775   -9.6257    0.0000 C   0  0
   14.0880  -12.8949    0.0000 O   0  0
    9.1518  -10.1649    0.0000 N   0  0
   13.3806  -11.6670    0.0000 C   0  0
   11.2640  -10.4378    0.0000 N   0  0
   10.7879   -8.7414    0.0000 H   0  0
   14.8024  -10.8442    0.0000 C   0  0
   12.6734  -10.4371    0.0000 C   0  0
    9.9705  -10.1649    0.0000 C   0  0  1  0  0  0
   14.8024  -11.6691    0.0000 C   0  0
   12.6752  -12.0736    0.0000 C   0  0
   14.0905  -10.4284    0.0000 N   0  0
   10.3841   -9.4526    0.0000 C   0  0  1  0  0  0
    9.9789   -8.7448    0.0000 C   0  0
   16.2201  -11.6726    0.0000 O   0  0
    9.5544  -10.8666    0.0000 H   0  0
    8.7449   -9.4473    0.0000 C   0  0
   11.9594   -9.2141    0.0000 C   0  0
   12.6734   -9.6204    0.0000 O   0  0
   13.6814   -8.9080    0.0000 C   0  0
   11.9657  -11.6649    0.0000 C   0  0
   14.0880  -12.0781    0.0000 C   0  0
   11.9657  -10.8458    0.0000 C   0  0
   14.0905   -9.6117    0.0000 C   0  0
   14.4982   -8.9080    0.0000 C   0  0
   15.5127  -12.8957    0.0000 O   0  0
   13.3806  -10.8422    0.0000 C   0  0
   10.5186  -10.7695    0.0000 C   0  0
   15.5127  -12.0789    0.0000 C   0  0
 10 21  1  0
 12 31  1  0
  9 14  1  0
 29 14  1  0
 14 26  1  0
 11 30  1  0
 15 16  1  0
 21 20  1  0
 13  6  2  0
 11 18  1  6
 25 23  2  0
 27 26  1  0
 31 28  1  0
 24  4  2  0
 31 17  2  0
 26 22  1  0
 16  2  1  0
 23 13  1  0
  3 15  1  0
 25  7  1  0
  2 19  1  0
 22 27  1  0
 19  5  1  0
 29 10  2  0
 12  9  2  0
 10 25  1  0
 30  7  1  0
  6 24  1  0
 24 12  1  0
 15  8  1  6
  7  3  1  0
 11 15  1  0
 11  5  1  0
 23  1  1  0
 29  6  1  0
M  END
> <chembl_id>
CHEMBL32


$$$$

  SciTegic01161211212D

 32 35  0  0  0  0            999 V2000
    2.7125   -2.8375    0.0000 N   0  0
    3.3292   -3.9000    0.0000 C   0  0
    2.1042   -3.1917    0.0000 C   0  0
    2.1042   -3.9000    0.0000 C   0  0
    0.2542   -2.8667    0.0000 N   0  0
    3.3292   -3.1917    0.0000 C   0  0
    2.7125   -4.2417    0.0000 C   0  0
    1.4792   -2.8375    0.0000 C   0  0
    0.8667   -3.1917    0.0000 C   0  0
    0.8667   -3.9000    0.0000 C   0  0
    2.7125   -2.1292    0.0000 C   0  0
    1.4792   -4.2417    0.0000 C   0  0
    3.9500   -4.2417    0.0000 C   0  0
    0.1375   -2.1542    0.0000 C   0  0
   -0.4000   -3.1500    0.0000 C   0  0
   -0.5208   -2.0125    0.0000 C   0  0  1  0  0  0
   -0.8708   -2.6167    0.0000 C   0  0  2  0  0  0
    3.0917   -1.4542    0.0000 C   0  0
    2.3542   -1.4542    0.0000 C   0  0
   -1.5833   -2.6042    0.0000 N   0  0
    2.7125   -4.9417    0.0000 O   0  0
    3.9500   -4.9500    0.0000 O   0  0
    1.4792   -2.1292    0.0000 O   0  0
    0.2542   -4.2375    0.0000 F   0  0
    4.5542   -3.9000    0.0000 O   0  0
    4.3500   -2.6167    0.0000 Cl  0  0
   -0.8583   -1.3875    0.0000 C   0  0
   -1.9333   -2.0125    0.0000 C   0  0
    0.8875   -1.7792    0.0000 C   0  0
   -1.5708   -1.3875    0.0000 C   0  0
   -1.2333   -3.2292    0.0000 H   0  0
   -0.1708   -1.3917    0.0000 H   0  0
  2  6  2  0
  3  1  1  0
  4  3  2  0
  5  9  1  0
  6  1  1  0
  7  2  1  0
  8  3  1  0
  9  8  2  0
 10  9  1  0
 11  1  1  0
 12  4  1  0
 13  2  1  0
 14  5  1  0
 15  5  1  0
 16 14  1  0
 17 15  1  0
 18 11  1  0
 19 11  1  0
 20 17  1  0
 21  7  2  0
 22 13  2  0
 23  8  1  0
 24 10  1  0
 25 13  1  0
 27 16  1  0
 28 20  1  0
 29 23  1  0
 30 27  1  0
 17 31  1  6
 16 32  1  6
 19 18  1  0
  7  4  1  0
 10 12  2  0
 17 16  1  0
 28 30  1  0
M  END
> <chembl_id>
CHEMBL1200735


$$$$
'''

class TestSequenceFunctions(unittest.TestCase):

    def test_resolve(self):

        ret = resolve('viagra')
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]['molecule_chembl_id'], 'CHEMBL1737')

        ret = resolve('gleevec')
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret[0]['molecule_chembl_id'], 'CHEMBL941')
        self.assertEqual(ret[1]['molecule_chembl_id'], 'CHEMBL1642')

        ret = resolve('gleevec', single_result=True)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]['molecule_chembl_id'], 'CHEMBL941')

        ret = resolve('aspirin')
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]['molecule_chembl_id'], 'CHEMBL25')

        ret = resolve('chembl59')
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]['molecule_chembl_id'], 'CHEMBL59')

        ret = resolve('OLEOYL')
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]['molecule_chembl_id'], 'CHEMBL191896')

        ret = resolve('Fc1ccc2[nH]c3CCN(CCc4ccncc4)Cc3c2c1')
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]['molecule_chembl_id'], 'CHEMBL300443')

        ret = resolve('VYFYYTLLBUKUHU-WTJCDBBSSA-N')
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]['molecule_chembl_id'], 'CHEMBL3247442')

        ret = resolve('Vigamox')
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret[0]['molecule_chembl_id'], 'CHEMBL32')
        self.assertEqual(ret[1]['molecule_chembl_id'], 'CHEMBL1200735')

        ret = resolve('Vigamox', single_result=True)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]['molecule_chembl_id'], 'CHEMBL32')

        ret = resolve('InChI=1S/C8H12N4O5/c9-6(16)7-10-2-12(11-7)8-5(15)4(14)3(1-13)17-8/h2-5,8,13-15H,1H2,(H2,9,16)')
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]['molecule_chembl_id'], 'CHEMBL34')

    def test_resolve_target(self):
        self.assertEqual(len(resolve_target('5-HT')), 5)
        res = resolve_target('Serotonin transporter')
        self.assertEqual(len(res), 4)
        self.assertTrue(all([r['pref_name'] == 'Serotonin transporter' for r in res]))
        res = resolve_target('Dopamine D1 receptor')
        self.assertEqual(len(res), 6)
        self.assertTrue(all([r['pref_name'] == 'Dopamine D1 receptor' for r in res]))
        res = resolve_target('Influenza A virus')
        self.assertEqual(len(res), 1)
        self.assertTrue(all([r['pref_name'] == 'Influenza A virus' for r in res]))
        res = resolve_target('HERG')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['target_chembl_id'], 'CHEMBL240')
        res = resolve_target('pde5')
        self.assertEqual(len(res), 10)
        self.assertTrue(all(
            ['pdbe5' in r['pref_name'].lower() or 'phosphodiesterase' in r['pref_name'].lower() for r in res]))
        res = resolve_target('BRD4')
        self.assertEqual(len(res), 2)
        self.assertTrue(all([r['pref_name'] == 'Bromodomain-containing protein 4' for r in res]))

    def test_chembl_id_serialiser(self):
        serialiser = get_serializer('chembl_id')
        mols = resolve('Vigamox')
        buf = StringIO()
        serialiser.write_header(buf)
        buf.seek(0)
        self.assertEqual(buf.read(), 'Name:\tChEMBL ID:\n')
        self.assertEqual(serialiser.serialize_line(mols), 'CHEMBL32,CHEMBL1200735\n')
        self.assertEqual(serialiser.serialize_line(mols, human=True), 'CHEMBL32,CHEMBL1200735\n')
        self.assertEqual(serialiser.serialize_line(mols, human=True, name='Vigamox'),
                         'Vigamox\tCHEMBL32,CHEMBL1200735\n')

    def test_smiles_serialiser(self):
        serialiser = get_serializer('smi')
        mols = resolve('Vigamox')
        buf = StringIO()
        serialiser.write_header(buf)
        buf.seek(0)
        self.assertEqual(buf.read(), 'SMILES Name\n')
        self.assertEqual(serialiser.serialize_line(mols),
                         'COc1c(N2C[C@@H]3CCCN[C@@H]3C2)c(F)cc4C(=O)C(=CN(C5CC5)c14)C(=O)O\n'
                         'Cl.COc1c(N2C[C@@H]3CCCN[C@@H]3C2)c(F)cc4C(=O)C(=CN(C5CC5)c14)C(=O)O\n')
        self.assertEqual(serialiser.serialize_line(mols, human=True),
                         'COc1c(N2C[C@@H]3CCCN[C@@H]3C2)c(F)cc4C(=O)C(=CN(C5CC5)c14)C(=O)O\n'
                         'Cl.COc1c(N2C[C@@H]3CCCN[C@@H]3C2)c(F)cc4C(=O)C(=CN(C5CC5)c14)C(=O)O\n')
        self.assertEqual(serialiser.serialize_line(mols, human=True, name='Vigamox'),
                         'COc1c(N2C[C@@H]3CCCN[C@@H]3C2)c(F)cc4C(=O)C(=CN(C5CC5)c14)C(=O)O Vigamox\n'
                         'Cl.COc1c(N2C[C@@H]3CCCN[C@@H]3C2)c(F)cc4C(=O)C(=CN(C5CC5)c14)C(=O)O Vigamox\n')

    def test_sdf_serialiser(self):

        serialiser = get_serializer('sdf')
        mols = resolve('Vigamox')
        buf = StringIO()
        serialiser.write_header(buf)
        buf.seek(0)
        self.assertEqual(buf.read(), '')
        self.assertEqual(serialiser.serialize_line(mols), sdf, serialiser.serialize_line(mols))
        self.assertEqual(serialiser.serialize_line(mols, human=True), sdf)
        self.assertEqual(serialiser.serialize_line(mols, human=True, name='Vigamox'), sdf)
        serialiser = get_serializer('mol')
        mols = resolve('Vigamox')
        buf = StringIO()
        serialiser.write_header(buf)
        buf.seek(0)
        self.assertEqual(buf.read(), '')
        self.assertEqual(serialiser.serialize_line(mols), sdf, serialiser.serialize_line(mols))
        self.assertEqual(serialiser.serialize_line(mols, human=True), sdf)
        self.assertEqual(serialiser.serialize_line(mols, human=True, name='Vigamox'), sdf)

    def test_inchi_serialiser(self):
        serialiser = get_serializer('inchi')
        mols = resolve('Vigamox')
        buf = StringIO()
        serialiser.write_header(buf)
        buf.seek(0)
        self.assertEqual(buf.read(), 'Name:\tInChI:\n')
        self.assertEqual(serialiser.serialize_line(mols),
                         'InChI=1S/C21H24FN3O4/c1-29-20-17-13(19(26)14(21(27)28)9-25(17)12-4-5-12)7-15(22)18(20)24-8-11'
                         '-3-2-6-23-16(11)10-24/h7,9,11-12,16,23H,2-6,8,10H2,1H3,(H,27,28)/t11-,16+/m0/s1\tInChI=1S/C21'
                         'H24FN3O4.ClH/c1-29-20-17-13(19(26)14(21(27)28)9-25(17)12-4-5-12)7-15(22)18(20)24-8-11-3-2-6-2'
                         '3-16(11)10-24;/h7,9,11-12,16,23H,2-6,8,10H2,1H3,(H,27,28);1H/t11-,16+;/m0./s1\n')
        self.assertEqual(serialiser.serialize_line(mols, human=True),
                         'InChI=1S/C21H24FN3O4/c1-29-20-17-13(19(26)14(21(27)28)9-25(17)12-4-5-12)7-15(22)18(20)24-8-11'
                         '-3-2-6-23-16(11)10-24/h7,9,11-12,16,23H,2-6,8,10H2,1H3,(H,27,28)/t11-,16+/m0/s1\tInChI=1S/C21'
                         'H24FN3O4.ClH/c1-29-20-17-13(19(26)14(21(27)28)9-25(17)12-4-5-12)7-15(22)18(20)24-8-11-3-2-6-2'
                         '3-16(11)10-24;/h7,9,11-12,16,23H,2-6,8,10H2,1H3,(H,27,28);1H/t11-,16+;/m0./s1\n')
        self.assertEqual(serialiser.serialize_line(mols, human=True, name='Vigamox'),
                         'Vigamox\tInChI=1S/C21H24FN3O4/c1-29-20-17-13(19(26)14(21(27)28)9-25(17)12-4-5-12)7-15(22)18(2'
                         '0)24-8-11-3-2-6-23-16(11)10-24/h7,9,11-12,16,23H,2-6,8,10H2,1H3,(H,27,28)/t11-,16+/m0/s1\tInC'
                         'hI=1S/C21H24FN3O4.ClH/c1-29-20-17-13(19(26)14(21(27)28)9-25(17)12-4-5-12)7-15(22)18(20)24-8-1'
                         '1-3-2-6-23-16(11)10-24;/h7,9,11-12,16,23H,2-6,8,10H2,1H3,(H,27,28);1H/t11-,16+;/m0./s1\n')

    def test_chembl_key_serialiser(self):
        serialiser = get_serializer('inchi_key')
        mols = resolve('Vigamox')
        buf = StringIO()
        serialiser.write_header(buf)
        buf.seek(0)
        self.assertEqual(buf.read(), 'Name:\tInChI Key:\n')
        self.assertEqual(serialiser.serialize_line(mols), 'FABPRXSRWADJSP-MEDUHNTESA-N,IDIIJJHBXUESQI-DFIJPDEKSA-N\n')
        self.assertEqual(serialiser.serialize_line(mols, human=True),
                         'FABPRXSRWADJSP-MEDUHNTESA-N,IDIIJJHBXUESQI-DFIJPDEKSA-N\n')
        self.assertEqual(serialiser.serialize_line(mols, human=True, name='Vigamox'),
                         'Vigamox\tFABPRXSRWADJSP-MEDUHNTESA-N,IDIIJJHBXUESQI-DFIJPDEKSA-N\n')

    def test_get_parents(self):
        parents = get_parents(resolve('CHEMBL1642'))
        self.assertEqual(len(parents), 1)
        self.assertEqual(parents[0]['molecule_chembl_id'], 'CHEMBL941')

        parents = get_parents(resolve('CHEMBL941'))
        self.assertEqual(len(parents), 1)
        self.assertEqual(parents[0]['molecule_chembl_id'], 'CHEMBL941')

        parents = get_parents(resolve('CHEMBL1200735'))
        self.assertEqual(len(parents), 1)
        self.assertEqual(parents[0]['molecule_chembl_id'], 'CHEMBL32')

        parents = get_parents(resolve('CHEMBL32'))
        self.assertEqual(len(parents), 1)
        self.assertEqual(parents[0]['molecule_chembl_id'], 'CHEMBL32')

        parents = get_parents(resolve('CHEMBL1642') + resolve('CHEMBL1200735'))
        self.assertEqual(len(parents), 2)
        self.assertEqual(parents[1]['molecule_chembl_id'], 'CHEMBL941')
        self.assertEqual(parents[0]['molecule_chembl_id'], 'CHEMBL32')

    def test_enhance_mols_with_parents(self):
        enhanced = [x['molecule_chembl_id'] for x in enhance_mols_with_parents(resolve('CHEMBL1642'))]
        self.assertEqual(enhanced, ['CHEMBL941', 'CHEMBL1642'])

    def test_regexes(self):
        self.assertTrue(inchi_key_regex.match('FABPRXSRWADJSP-MEDUHNTESA-N'))
        self.assertFalse(inchi_key_regex.match('FAPRXSRWADJSP-MEDUHNTESA-N'))
        self.assertFalse(inchi_key_regex.match('FABPRXSRWADJSP-MEDUNTESA-N'))
        self.assertFalse(inchi_key_regex.match('FABPRXSRWADJSP-MEDUHNTESA-'))
        self.assertFalse(inchi_key_regex.match('FABPRXSRWADJSP\MEDUHNTESA-N'))
        self.assertFalse(inchi_key_regex.match('FABPRXSRWADJSP-MEDUHNTESA\\N'))

        self.assertTrue(chembl_id_regex.match('CHEMBL25'))
        self.assertFalse(chembl_id_regex.match('CHEML25'))
        self.assertFalse(chembl_id_regex.match('25'))
        self.assertFalse(chembl_id_regex.match('CHEMBL_25'))
        self.assertFalse(chembl_id_regex.match('CHEMBL'))

        self.assertTrue(smiles_regex.match('Fc1ccc2[nH]c3CCN(CCc4ccncc4)Cc3c2c1'))
        self.assertTrue(smiles_regex.match('COc1c(N2C[C@@H]3CCCN[C@@H]3C2)c(F)cc4C(=O)C(=CN(C5CC5)c14)C(=O)O'))
        self.assertTrue(
            smiles_regex.match('Cl.COc1c(N2C[C@@H]3CCCN[C@@H]3C2)c(F)cc4C(=O)C(=CN(C5CC5)c14)C(=O)O'))
        self.assertTrue(smiles_regex.match('cc'))

    def test_inspect_synonyms(self):
        dopamine = resolve('dopamine')[0]
        self.assertTrue(inspect_synonyms(dopamine, 'Intropin'))
        self.assertTrue(inspect_synonyms(dopamine, 'parcopa'))
        self.assertTrue(inspect_synonyms(dopamine, 'SINEMET'))
        self.assertFalse(inspect_synonyms(dopamine, 'viagra'))
        self.assertFalse(inspect_synonyms(dopamine, ''))

    def test_sdf_split(self):
        count = 0
        inchis = ['InChI=1S/C21H24FN3O4/c1-29-20-17-13(19(26)14(21(27)28)9-25(17)12-4-5-12)7-15(22)18(20)24-8-11-3-2-6-'
                  '23-16(11)10-24/h7,9,11-12,16,23H,2-6,8,10H2,1H3,(H,27,28)/t11-,16+/m0/s1',
                  'InChI=1S/C21H24FN3O4.ClH/c1-29-20-17-13(19(26)14(21(27)28)9-25(17)12-4-5-12)7-15(22)18(20)24-8-11-3-'
                  '2-6-23-16(11)10-24;/h7,9,11-12,16,23H,2-6,8,10H2,1H3,(H,27,28);1H/t11-,16+;/m0./s1']
        f = StringIO(sdf)
        for idx, mol in enumerate(sdf_split(f)):
            count += 1
            self.assertEqual(utils.ctab2inchi(mol), inchis[idx])
        self.assertEqual(count, 2)

    def test_convert_to_smiles(self):
        f = StringIO(sdf)
        inp = convert_to_smiles(f)
        self.assertEqual(inp.read(), 'COc1c(N2CC3CCCNC3C2)c(F)cc2c(=O)c(C(=O)O)cn(C3CC3)c12 0\n'
                                     'COc1c(N2CC3CCCNC3C2)c(F)cc2c(=O)c(C(=O)O)cn(C3CC3)c12.Cl 1\n')

    def test_combine_sdf_split_with_smiles_conversion(self):
        smiles = ['COc1c(N2CC3CCCNC3C2)c(F)cc2c(=O)c(C(=O)O)cn(C3CC3)c12',
                  'COc1c(N2CC3CCCNC3C2)c(F)cc2c(=O)c(C(=O)O)cn(C3CC3)c12.Cl']
        f = StringIO(sdf)
        for idx, mol in enumerate(sdf_split(f)):
            self.assertEqual(utils.ctab2smiles(mol).split()[2], smiles[idx])

    def test_mols_to_targets(self):
        ret = mols_to_targets(['CHEMBL819'], organism='Escherichia coli')
        serialiser = get_serializer('uniprot')
        self.assertEqual(set(serialiser.serialize_line(ret).strip().split(',')), {'A1E3K9', 'P62593', 'P35695'})

        ret = mols_to_targets(['CHEMBL819'], organism='Escherichia coli', include_parents=True)
        serialiser = get_serializer('uniprot')
        self.assertEqual(set(serialiser.serialize_line(ret).strip().split(',')),
                         {'A1E3K9', 'P62593', 'P35695', 'P00811'})

        ret = mols_to_targets(['CHEMBL25', 'CHEMBL1'])
        serialiser = get_serializer('gene_name')
        self.assertTrue({'POLK', 'ADRA2RL2', 'CCR2', 'CHRM5', 'ADRA2L1', 'CMKAR1', 'PTPRC', 'HADH2', 'ITGAB', 'VIPR1'
                         }.issubset(set(serialiser.serialize_line(ret).strip().split(','))))

        ret = mols_to_targets(['CHEMBL2', 'CHEMBL1737'])
        serialiser = get_serializer('chembl_id')
        targets_a = set(serialiser.serialize_line(ret).strip().split(','))
        self.assertTrue({'CHEMBL213', 'CHEMBL1916', 'CHEMBL205', 'CHEMBL4071', 'CHEMBL1909043', 'CHEMBL2622',
                         }.issubset(targets_a))

        ret = mols_to_targets(['CHEMBL2', 'CHEMBL1737'], only_ids=True)
        serialiser = get_serializer('chembl_id')
        targets_b = set(serialiser.serialize_line(ret).strip().split(','))
        self.assertTrue({'CHEMBL213', 'CHEMBL1916', 'CHEMBL205', 'CHEMBL4071', 'CHEMBL1909043', 'CHEMBL2622',
                         }.issubset(targets_b))

        self.assertEqual(targets_a, targets_b)

        drugs = ['Viagra', 'Gleevec']

        ret = mols_to_targets([resolve(x)[0]['molecule_chembl_id'] for x in drugs])
        serialiser = get_serializer('uniprot')
        self.assertTrue({'Q9BQI3', 'P00523', 'O15111', 'P22612', 'P25021', 'P16591', 'Q13153', 'Q8WXR4', 'P28564',
                         }.issubset(set(serialiser.serialize_line(ret).strip().split(','))))

    def test_targets_to_mols(self):

        ret = targets_to_mols([resolve_target(x)[0]['target_chembl_id'] for x in ['POLK']])
        serialiser = get_serializer('chembl_id')
        self.assertTrue({'CHEMBL6', 'CHEMBL25', 'CHEMBL10', 'CHEMBL30', 'CHEMBL50', 'CHEMBL71', 'CHEMBL28', 'CHEMBL66'
                          }.issubset(set(serialiser.serialize_line(ret).strip().split(','))))

        ret = targets_to_mols([resolve_target(x)[0]['target_chembl_id'] for x in ['HERG']])
        serialiser = get_serializer('smiles')
        self.assertTrue({'CN1C(=O)N(CC(=O)c2ccccc2)C(=O)c3c1nc(N4CCC[C@H](N)C4)n3CC=C(C)C',
                         'C[C@]12CCC(=O)C=C1CC[C@@H]3[C@@H]2CC[C@@]4(C)[C@H]3CC[C@@]4(O)C#C',
                         'CS(=O)(=O)N1CCC(CN([C@@H]2CC[C@@]3(CC3C2)c4cccc(c4)C#N)C(=O)Nc5ccc(F)c(F)c5)CC1',
                         'O=S(=O)(NCCCN1CCN(CC1)c2nsc3ccccc23)c4cccc5scnc45',
                         'Cl.CC(C)n1nc(C(=O)NCC2CCN(CCNS(=O)(=O)C)CC2)c3ccccc13',
                         'CC1CN(CC(=O)N[C@@H]2C3CC4CC2C[C@@](C4)(C3)C(=O)N)S(=O)(=O)N(C1)c5c(Cl)cc(Cl)cc5Cl',
                         'Oc1cccc2CC(CN3CCC4(CC3)CCc5ccccc45)NCc12',
                         '[O-][N+](=O)c1ccc(cc1)c2nc(c3ccc(F)cc3)c([nH]2)c4ccncc4'
                         }.issubset(set(serialiser.serialize_line(ret).strip().split())))

        ret = targets_to_mols([resolve_target(x)[0]['target_chembl_id'] for x in ['CMKAR1']])
        serialiser = get_serializer('inchi')
        self.assertTrue({
                            'InChI=1S/C7H6O2/c8-7(9)6-4-2-1-3-5-6/h1-5H,(H,8,9)',
                            'InChI=1S/C11H7NS/c13-8-12-11-7-3-5-9-4-1-2-6-10(9)11/h1-7H',
                            'InChI=1S/CHCl3/c2-1(3)4/h1H',
                            'InChI=1S/H4N2/c1-2/h1-2H2',
                            'InChI=1S/C8H8N4/c9-11-8-7-4-2-1-3-6(7)5-10-12-8/h1-5H,9H2,(H,11,12)',
                            'InChI=1S/CH4N2O2/c2-1(4)3-5/h5H,(H3,2,3,4)',
                            'InChI=1S/CH3O5P/c2-1(3)7(4,5)6/h(H,2,3)(H2,4,5,6)',
                            'InChI=1S/C4H11NO3/c5-4(1-6,2-7)3-8/h6-8H,1-3,5H2',
                            'InChI=1S/C9H9Cl2N3O/c10-6-2-1-3-7(11)5(6)4-8(15)14-9(12)13/h1-3H,4H2,(H4,12,13,14,15)',
                        }.issubset(set(serialiser.serialize_line(ret).strip().split('\t'))))

        ret = targets_to_mols([resolve_target(x)[0]['target_chembl_id'] for x in ['ADRA2L1', 'VIPR1']])
        serialiser = get_serializer('inchi_key')
        self.assertTrue({
                            'OELFLUMRDSZNSF-BRWVUGGUSA-N',
                            'KJPRLNWUNMBNBZ-QPJJXVBHSA-N',
                            'VEPKQEUBKLEPRA-UHFFFAOYSA-N',
                            'ACGUYXCXAPNIKK-UHFFFAOYSA-N',
                            'MVGSNCBCUWPVDA-MFOYZWKCSA-N',
                            'JZHXLYHEWUWHQL-LVYIWIAJSA-N',
                            'CUVBGWMAORETGV-UHFFFAOYSA-N',
                            'DVSMVUMYJDOPJQ-UHFFFAOYSA-N',
                         }.issubset(set(serialiser.serialize_line(ret).strip().split(','))))

    def test_elastic(self):
        es = ElasticClient()
        ret = es.search_target('CMKAR1')
        self.assertEqual(ret, ['CHEMBL4029', 'CHEMBL2096909'])

        ret = es.search_molecule('viagra')
        self.assertEqual(ret, ['CHEMBL1737'])

        ret = es.search_assay('modulation activity')
        self.assertEqual(ret, ['CHEMBL3371687'])

        ret = es.search_cell_line('caco-2')
        self.assertEqual(ret, ['CHEMBL3307519'])

        ret = es.search_document('nowotarski')
        self.assertEqual(ret, ['CHEMBL3400002'])

        ret = es.search_tissue('liver')
        self.assertEqual(ret, ['CHEMBL3559723'])

if __name__ == '__main__':
    unittest.main()