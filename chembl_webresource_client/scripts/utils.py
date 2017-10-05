import re
from abc import ABC, abstractmethod
from chembl_webresource_client.utils import utils
from chembl_webresource_client.new_client import new_client
from io import StringIO

__author__ = 'mnowotka'

# ----------------------------------------------------------------------------------------------------------------------

inchi_key_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')
smiles_regex = re.compile(r'^([^J][.0-9BCGOHMNSEPRIFTLUA@+\-\[\]\(\)\\\/%=#$]+)$', re.IGNORECASE)
chembl_id_regex = re.compile(r'^CHEMBL(\d)+$')

# ----------------------------------------------------------------------------------------------------------------------


def inspect_synonyms(entry, term):
    return term.lower() in {x['molecule_synonym'].lower() for x in entry['molecule_synonyms']}

# ----------------------------------------------------------------------------------------------------------------------


def get_parents(mols):
    molecule = new_client.molecule
    molecule.set_format('json')
    ret = [next(iter(new_client.molecule_form.filter(molecule_chembl_id=m['molecule_chembl_id']) or []), m) for m in mols]
    return molecule.filter(molecule_chembl_id__in=[x.get('parent_chembl_id', x['molecule_chembl_id']) for x in ret])

# ----------------------------------------------------------------------------------------------------------------------


def convert_to_smiles(inp):
    return StringIO(utils.ctab2smiles(inp.read()))

# ----------------------------------------------------------------------------------------------------------------------


def resolve(mystery, single_result=False):
    molecule = new_client.molecule
    molecule.set_format('json')

    if mystery.lower().startswith('chembl'):
        return [molecule.get(mystery.upper())]

    res = molecule.filter(pref_name__iexact=mystery)
    if res:
        return res if not single_result else [res[0]]

    res = [x for x in molecule.search(mystery.lower()) if inspect_synonyms(x, mystery)]
    if res:
        return res if not single_result else [res[0]]

    if inchi_key_regex.match(mystery.upper()):
        return [molecule.get(mystery.upper())]

    inchi_key = None
    if smiles_regex.match(mystery.upper()):
        inchi_key = utils.inchi2inchiKey(utils.ctab2inchi(utils.smiles2ctab(mystery)))
    elif mystery.upper().startswith('INCHI='):
        inchi_key = utils.inchi2inchiKey(mystery)
    if inchi_key:
        return [molecule.get(inchi_key.upper())]

# ----------------------------------------------------------------------------------------------------------------------


class MolSerializer(ABC):

    def __init__(self, mols):
        self.mols = mols

    @abstractmethod
    def serialize(self):
        pass

    @staticmethod
    @abstractmethod
    def serialize_line(mols, human=True, name=None):
        pass

    @staticmethod
    @abstractmethod
    def write_header(file):
        pass

# ----------------------------------------------------------------------------------------------------------------------


class MolChEMBLIDSerializer(MolSerializer):

    def serialize(self):
        return [x['molecule_chembl_id'] for x in self.mols]

    @staticmethod
    def serialize_line(mols, human=True, name=None):
        aux = ','.join(mol['molecule_chembl_id'] for mol in mols) if mols else 'NOT FOUND'
        if human:
            return '\t'.join((name, aux)) + '\n'
        else:
            return aux + '\n'

    @staticmethod
    def write_header(file):
        file.write('\t'.join(('Name:', 'ChEMBL ID:')))
        file.write('\n')

# ----------------------------------------------------------------------------------------------------------------------


class MolSmilesSerializer(MolSerializer):

    def serialize(self):
        return [x['molecule_structures']['canonical_smiles'] for x in self.mols]

    @staticmethod
    def serialize_line(mols, human=True, name=None):
        if human:
            return '\n'.join(' '.join((mol['molecule_structures']['canonical_smiles'], name)) for mol in mols) + '\n'
        else:
            return '\n'.join(mol['molecule_structures']['canonical_smiles'] for mol in mols) + '\n'

    @staticmethod
    def write_header(file):
        file.write(' '.join(('SMILES', 'Name')))
        file.write('\n')

# ----------------------------------------------------------------------------------------------------------------------


class MolSDFSerializer(MolSerializer):

    def serialize(self):
        molecule = new_client.molecule
        molecule.set_format('sdf')
        return molecule.filter(molecule_chembl_id__in=[x['molecule_chembl_id'] for x in self.mols])

    @staticmethod
    def serialize_line(mols, human=True, name=None):
        molecule = new_client.molecule
        molecule.set_format('sdf')
        return '\n$$$$\n'.join([m.decode("utf-8") for m
                                in molecule.filter(molecule_chembl_id__in=[x['molecule_chembl_id'] for
                                                                           x in mols]) if m]) + '\n$$$$\n'

    @staticmethod
    def write_header(file):
        pass

# ----------------------------------------------------------------------------------------------------------------------


class MolInChISerializer(MolSerializer):

    def serialize(self):
        return [x['molecule_structures']['standard_inchi'] for x in self.mols]

    @staticmethod
    def serialize_line(mols, human=True, name=None):
        aux = ','.join(mol['molecule_structures']['standard_inchi'] for mol in mols) if mols else 'NOT FOUND'
        if human:
            return '\t'.join((name, aux)) + '\n'
        else:
            return aux + '\n'

    @staticmethod
    def write_header(file):
        file.write('\t'.join(('Name:', 'InChI:')))
        file.write('\n')

# ----------------------------------------------------------------------------------------------------------------------


class MolInChIKeySerializer(MolSerializer):

    def serialize(self):
        return [x['molecule_structures']['standard_inchi_key'] for x in self.mols]

    @staticmethod
    def serialize_line(mols, human=True, name=None):
        aux = ','.join(mol['molecule_structures']['standard_inchi_key'] for mol in mols) if mols else 'NOT FOUND'
        if human:
            return '\t'.join((name, aux)) + '\n'
        else:
            return aux + '\n'

    @staticmethod
    def write_header(file):
        file.write('\t'.join(('Name:', 'InChI Key:')))
        file.write('\n')

# ----------------------------------------------------------------------------------------------------------------------


def get_serializer(frmt):
    return {
        'sdf': MolSDFSerializer,
        'mol': MolSDFSerializer,
        'smi': MolSmilesSerializer,
        'smiles': MolSmilesSerializer,
        'inchi': MolInChISerializer,
        'inchi_key': MolInChIKeySerializer,
        'chembl_id': MolChEMBLIDSerializer,
    }.get(frmt.lower())

# ----------------------------------------------------------------------------------------------------------------------
