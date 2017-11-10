import re
import tempfile
from abc import abstractmethod, ABCMeta
from chembl_webresource_client.utils import utils
from chembl_webresource_client.new_client import new_client
from chembl_webresource_client.elastic_client import ElasticClient

ABC = ABCMeta('ABC', (object,), {'__slots__': ()})


__author__ = 'mnowotka'

# ----------------------------------------------------------------------------------------------------------------------

inchi_key_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')
smiles_regex = re.compile(r'^([^J][.0-9BCGOHMNSEPRIFTLUA@+\-\[\]\(\)\\\/%=#$]+)$', re.IGNORECASE)
chembl_id_regex = re.compile(r'^CHEMBL(\d)+$')
sdf_line_delimiter = '$$$$\n'

# ----------------------------------------------------------------------------------------------------------------------


def inspect_synonyms(entry, term, entity="compound"):
    if entity == "compound":
        return term.lower() in {x['molecule_synonym'].lower() for x in entry['molecule_synonyms']}
    elif entity == "target":
        synonyms = set()
        for component in entry['target_components']:
            for synonym in component['target_component_synonyms']:
                synonyms.add(synonym['component_synonym'].lower())
        return term.lower() in synonyms

# ----------------------------------------------------------------------------------------------------------------------


def sdf_split(f, delim=sdf_line_delimiter, bufsize=1024):
    prev = ''
    while True:
        s = f.read(bufsize)
        if not s:
            break
        split = s.split(delim)
        if len(split) > 1:
            yield prev + split[0]
            prev = split[-1]
            for x in split[1:-1]:
                yield x
        else:
            prev += s
    if prev:
        yield prev

# ----------------------------------------------------------------------------------------------------------------------


def convert_to_smiles(inp, chunk_size=100):
    new_file = tempfile.NamedTemporaryFile(delete=False, mode='w+')
    sdf_chunk = []
    for sdf in sdf_split(inp):
        sdf_chunk.append(sdf)
        if len(sdf_chunk) == chunk_size:
            new_file.write(utils.ctab2smiles(sdf_line_delimiter.join(sdf_chunk)).split('\n', 1)[1])
            sdf_chunk = []
    if sdf_chunk:
        new_file.write(utils.ctab2smiles(sdf_line_delimiter.join(sdf_chunk)).split('\n', 1)[1])

    new_file.seek(0)
    return new_file

# ----------------------------------------------------------------------------------------------------------------------


def resolve_target(mystery, single_result=False):
    target = new_client.target
    target.set_format('json')

    if mystery.lower().startswith('chembl'):
        return [target.get(mystery.upper())]

    res = target.filter(pref_name__iexact=mystery)
    if res:
        return res if not single_result else [res[0]]

    res = [x for x in target.search(mystery.lower()) if inspect_synonyms(x, mystery, entity='target')]
    if res:
        return res if not single_result else [res[0]]
    es = ElasticClient()
    res = es.search_target(mystery)
    if res:
        res = target.filter(target_chembl_id__in=res)
        return res if not single_result else [res[0]]

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
    if smiles_regex.match(mystery):
        inchi_key = utils.inchi2inchiKey(utils.ctab2inchi(utils.smiles2ctab(mystery)))
    elif mystery.upper().startswith('INCHI='):
        inchi_key = utils.inchi2inchiKey(mystery)
    if inchi_key:
        return [molecule.get(inchi_key.upper())]
    es = ElasticClient()
    res = es.search_molecule(mystery)
    if res:
        res = molecule.filter(molecule_chembl_id__in=res)
        return res if not single_result else [res[0]]

# ----------------------------------------------------------------------------------------------------------------------


def mols_to_targets(mol_ids, organism=None, include_parents=False, only_ids=False, chunk_size=1000):

    unique_mol_ids = list(set(mol_ids))

    if include_parents:
        unique_mol_ids = enhance_mols_with_parents(unique_mol_ids, chunk_size)

    unique_mol_ids = list(set(unique_mol_ids))
    activities = []
    for i in range(0, len(unique_mol_ids), chunk_size):
        chunk = new_client.activity.filter(
            molecule_chembl_id__in=[mol for mol in unique_mol_ids[i:i + chunk_size]])
        if organism:
            chunk = chunk.filter(target_organism__icontains=organism)
        activities.extend(list(chunk))
        activities = list({v['activity_id']: v for v in activities}.values())
    target_ids = [act['target_chembl_id'] for act in activities]
    if only_ids:
        return target_ids
    targets = []
    for i in range(0, len(target_ids), chunk_size):
        chunk = new_client.target.filter(target_chembl_id__in=target_ids[i:i + chunk_size])
        targets.extend(list(chunk))
        targets = list({v['target_chembl_id']: v for v in targets}.values())
    return targets

# ----------------------------------------------------------------------------------------------------------------------


def get_parents(mols):
    molecule = new_client.molecule
    molecule.set_format('json')
    ret = [
        next(iter(new_client.molecule_form.filter(molecule_chembl_id=m['molecule_chembl_id']) or []), m) for m in mols]
    return molecule.filter(molecule_chembl_id__in=[x.get('parent_chembl_id', x['molecule_chembl_id']) for x in ret])

# ----------------------------------------------------------------------------------------------------------------------


def targets_to_mols(targets_ids, include_parents=False, only_ids=False, chunk_size=1000):
    unique_target_ids = list(set(targets_ids))
    activities = []
    for i in range(0, len(unique_target_ids), chunk_size):
        chunk = new_client.activity.filter(
            target_chembl_id__in=[tar for tar in unique_target_ids[i:i + chunk_size]])
        activities.extend(list(chunk))
        activities = list({v['activity_id']: v for v in activities}.values())
    mol_ids = [act['molecule_chembl_id'] for act in activities]
    if only_ids:
        return mol_ids
    mols = []
    for i in range(0, len(mol_ids), chunk_size):
        chunk = new_client.molecule.filter(molecule_chembl_id__in=mol_ids[i:i + chunk_size])
        mols.extend(list(chunk))
    mols = list({v['molecule_chembl_id']: v for v in mols}.values())
    if include_parents:
        mols = enhance_mols_with_parents(mols, chunk_size)
    return mols

# ----------------------------------------------------------------------------------------------------------------------


def enhance_mols_with_parents(mols, chunk_size=1000):
    only_ids = mols and isinstance(mols[0], str)
    if only_ids:
        original_mol_ids = mols
    else:
        original_mol_ids = [x['molecule_chembl_id'] for x in mols]
    other_forms = set()

    for i in range(0, len(original_mol_ids), chunk_size):
        salts = new_client.molecule_form.filter(parent_chembl_id__in=original_mol_ids[i:i + chunk_size])
        other_forms |= set([x['molecule_chembl_id'] for x in salts])

    for i in range(0, len(original_mol_ids), chunk_size):
        parents = new_client.molecule_form.filter(molecule_chembl_id__in=original_mol_ids[i:i + chunk_size])
        other_forms |= set([x['parent_chembl_id'] for x in parents])

    enhanced_ids = list(set(original_mol_ids) | other_forms)
    if only_ids:
        return enhanced_ids
    else:
        return new_client.molecule.get(molecule_chembl_id__in=enhanced_ids)

# ----------------------------------------------------------------------------------------------------------------------


class ClientSerializer(ABC):

    def __init__(self, objects):
        self.objects = objects

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


class MolChEMBLIDSerializer(ClientSerializer):

    def serialize(self):
        return [x['molecule_chembl_id'] for x in self.objects]

    @staticmethod
    def serialize_line(objects, human=True, name=None):
        if objects and isinstance(objects[0], str) and objects[0].lower().startswith('chembl'):
            aux = ','.join(objects)
        elif objects and 'target_chembl_id' in objects[0]:
            aux = ','.join(obj['target_chembl_id'] for obj in objects) if objects else 'NOT FOUND'
        else:
            aux = ','.join(obj['molecule_chembl_id'] for obj in objects) if objects else 'NOT FOUND'
        if human and name:
            return '\t'.join((name, aux)) + '\n'
        else:
            return aux + '\n'

    @staticmethod
    def write_header(file):
        file.write('\t'.join(('Name:', 'ChEMBL ID:')))
        file.write('\n')

# ----------------------------------------------------------------------------------------------------------------------


class MolSmilesSerializer(ClientSerializer):

    def serialize(self):
        return [x['molecule_structures']['canonical_smiles'] for x in self.objects]

    @staticmethod
    def serialize_line(mols, human=True, name=None):
        if human and name:
            return '\n'.join(' '.join((mol['molecule_structures']['canonical_smiles'], name)) for mol in mols) + '\n'
        else:
            return '\n'.join(mol['molecule_structures']['canonical_smiles'] for mol in mols if
                             mol['molecule_structures'] and mol['molecule_structures']['canonical_smiles']) + '\n'

    @staticmethod
    def write_header(file):
        file.write(' '.join(('SMILES', 'Name')))
        file.write('\n')

# ----------------------------------------------------------------------------------------------------------------------


class MolSDFSerializer(ClientSerializer):

    def serialize(self):
        molecule = new_client.molecule
        molecule.set_format('sdf')
        return molecule.filter(molecule_chembl_id__in=[x['molecule_chembl_id'] for x in self.objects])

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


class MolInChISerializer(ClientSerializer):

    def serialize(self):
        return [x['molecule_structures']['standard_inchi'] for x in self.objects if x['molecule_structures']]

    @staticmethod
    def serialize_line(mols, human=True, name=None):
        aux = '\t'.join(mol['molecule_structures']['standard_inchi'] for mol in mols if mol['molecule_structures']) \
            if mols else 'NOT FOUND'
        if human and name:
            return '\t'.join((name, aux)) + '\n'
        else:
            return aux + '\n'

    @staticmethod
    def write_header(file):
        file.write('\t'.join(('Name:', 'InChI:')))
        file.write('\n')

# ----------------------------------------------------------------------------------------------------------------------


class MolInChIKeySerializer(ClientSerializer):

    def serialize(self):
        return [x['molecule_structures']['standard_inchi_key'] for x in self.objects if x['molecule_structures']]

    @staticmethod
    def serialize_line(mols, human=True, name=None):
        aux = ','.join(mol['molecule_structures']['standard_inchi_key'] for mol in mols if mol['molecule_structures']) \
            if mols else 'NOT FOUND'
        if human and name:
            return '\t'.join((name, aux)) + '\n'
        else:
            return aux + '\n'

    @staticmethod
    def write_header(file):
        file.write('\t'.join(('Name:', 'InChI Key:')))
        file.write('\n')

# ----------------------------------------------------------------------------------------------------------------------


class TargetUniprotSerializer(ClientSerializer):

    def serialize(self):
        return list(set(sum([[comp['accession'] for comp in t['target_components']] for t in self.objects], [])))

    @staticmethod
    def serialize_line(targets, human=True, name=None):
        uniprots = ','.join(
            list(set(sum([[comp['accession'] for comp in t['target_components']] for t in targets], []))))
        if human and name:
            return '\t'.join((name, uniprots)) + '\n'
        else:
            return uniprots + '\n'

    @staticmethod
    def write_header(file):
        file.write('\t'.join(('Compounds ChEMBL IDs:', 'Related targets Uniprot IDs:')))
        file.write('\n')


# ----------------------------------------------------------------------------------------------------------------------


class TargetGeneNameSerializer(ClientSerializer):

    def serialize(self):
        genes = set()
        for target in self.objects:
            for component in target['target_components']:
                for synonym in component['target_component_synonyms']:
                    if synonym['syn_type'] == "GENE_SYMBOL":
                        genes.add(synonym['component_synonym'])
        return list(genes)

    @staticmethod
    def serialize_line(targets, human=True, name=None):
        genes = set()
        for target in targets:
            for component in target['target_components']:
                for synonym in component['target_component_synonyms']:
                    if synonym['syn_type'] == "GENE_SYMBOL":
                        genes.add(synonym['component_synonym'])
        genes = ','.join([x.strip() for x in list(genes) if x and x.strip()])
        if human and name:
            return '\t'.join((name, genes)) + '\n'
        else:
            return genes + '\n'

    @staticmethod
    def write_header(file):
        file.write('\t'.join(('Compounds ChEMBL IDs:', 'Related targets gene names:')))
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
        'uniprot': TargetUniprotSerializer,
        'gene_name': TargetGeneNameSerializer,
    }.get(frmt.lower())

# ----------------------------------------------------------------------------------------------------------------------
