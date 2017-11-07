#!/usr/bin/env python

__author__ = 'mnowotka'

# ----------------------------------------------------------------------------------------------------------------------

import re
import sys
import argparse
from chembl_webresource_client.utils import utils
from chembl_webresource_client.new_client import new_client

inchi_key_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')
smilesRegex = re.compile(r'^([^J][.0-9BCGOHMNSEPRIFTLUA@+\-\[\]\(\)\\\/%=#$]+)$')


# ----------------------------------------------------------------------------------------------------------------------


def inspect_synonyms(entry, term):
    return term.lower() in {x['molecule_synonym'].lower() for x in entry['molecule_synonyms']}


# ----------------------------------------------------------------------------------------------------------------------

def get_options():
    description = 'Try to convert names and identifiers into ChEMBL IDs. By default input is read from the standard ' \
                  'input and output written to the standard output'
    parser = argparse.ArgumentParser(description=description, prog='chembl_ids')
    parser.add_argument('-i', '--input', action='store', dest='input', help='input file with names, one line each')
    parser.add_argument('-o', '--output', action='store', dest='output', help='output file with ChEMBL IDs')
    return parser.parse_args()


# ----------------------------------------------------------------------------------------------------------------------


def resolve(mystery):
    ret = 'NOT FOUND'
    if mystery.istartswith('chembl'):
        return mystery.upper()

    molecule = new_client.molecule

    res = molecule.filter(pref_name__iexact=mystery)
    if len(res):
        return ', '.join(x['molecule_chembl_id'] for x in res)

    res = [x for x in molecule.search(mystery) if inspect_synonyms(x, mystery)]
    if len(res):
        return ', '.join(x['molecule_chembl_id'] for x in res)

    if inchi_key_regex.match(mystery.upper()):
        res = molecule.get(mystery.upper())
        if res:
            ret = res['molecule_chembl_id']
        return ret

    if smilesRegex.match(mystery):
        inchi_key = utils.inchi2inchiKey(utils.ctab2inchi(utils.smiles2ctab(mystery)))
    elif mystery.upper().startswith('INCHI='):
        inchi_key = utils.inchi2inchiKey(mystery)
    if inchi_key:
        res = molecule.get(mystery.upper())
    if res:
        ret = res['molecule_chembl_id']
    return ret


# ----------------------------------------------------------------------------------------------------------------------


def main():
    options = get_options()
    with open(options.input) if options.input else sys.stdin as in_f, \
            open(options.output, 'w') if options.output else sys.stdout as out_f:

        out_f.write('\t'.join(('Name:', 'ChEMBL ID:')))

        for line in in_f:
            name = line.strip()
            if not name:
                continue
            resolved = 'NOT FOUND'
            try:
                resolved = resolve(name)
            except:
                pass
            out_f.write('\t'.join((name, resolved)))


# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------------------------------------------------------
