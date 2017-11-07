#!/usr/bin/env python
from __future__ import print_function


__author__ = 'mnowotka'

# ----------------------------------------------------------------------------------------------------------------------

import sys
import argparse
from chembl_webresource_client.scripts.utils import get_serializer, chembl_id_regex, smiles_regex, convert_to_smiles
from chembl_webresource_client.scripts.utils import resolve, mols_to_targets

AVAILABLE_SOURCE_FORMATS = ('chembl_id', 'sdf', 'smi')

# ----------------------------------------------------------------------------------------------------------------------


def get_options():

    description = 'Find related targets for a set of compounds'
    parser = argparse.ArgumentParser(description=description, prog='chembl_m2t')
    parser.add_argument('-i', '--input', action='store', dest='input',
                        help='input file, standard input by default')
    parser.add_argument('-o', '--output', action='store', dest='output',
                        help='output file, standard output by default')
    parser.add_argument('-s', '--source-format', action='store', dest='source_format', default='csv',
                        help='input file format. Can be one of 3: chembl_id (a comma separated list of chembl IDs), '
                             'sdf: (MDL molfile), smi (file containing smiles)')
    parser.add_argument('-d', '--destination-format', action='store', dest='dest_format', default='uniprot',
                        help='output file format. can be chosen from 3 options: '
                             '[uniprot, gene_name, chembl_id]')
    parser.add_argument('-H', '--Human', action='store_true', dest='human',
                        help='human readable output: prints header and first column with original names')
    parser.add_argument('-O', '--organism', action='store', dest='organism',
                        help='Filter results by organism')
    parser.add_argument('-p', '--parent', action='store_true', dest='parent',
                        help='when fetching targets include also targets from parents of given molecules')
    parser.add_argument('-c', '--chunk-size', action='store', dest='chunk', default='1000',
                        help='Size of chunk of data retrieved from API')
    return parser.parse_args()

# ----------------------------------------------------------------------------------------------------------------------


def main():
    options = get_options()

    source_format = options.source_format.lower()
    if source_format not in AVAILABLE_SOURCE_FORMATS:
        sys.stderr.write('Unsupported source format', options.source_format)
        return

    inp = sys.stdin
    if source_format == 'sdf':
        with open(options.input) if options.input else sys.stdin as in_f:
            options.input = None
            inp = convert_to_smiles(in_f)

    with open(options.input) if options.input else inp as in_f, \
            open(options.output, 'w') if options.output else sys.stdout as out_f:

        serializer_cls = get_serializer(options.dest_format)
        if not serializer_cls:
            sys.stderr.write('Unsupported format', options.dest_format)
            return

        if options.human:
            serializer_cls.write_header(out_f)

        for line in in_f:
            if not line or line.lower().startswith('smiles'):
                continue
            chunk = line.strip().split()[0]
            identifiers = chunk.strip().split(',')
            valid_identifiers = list()
            for identifier in identifiers:
                if chembl_id_regex.match(identifier):
                    valid_identifiers.append(identifier)
                elif smiles_regex.match(identifier):
                    valid_identifiers.extend([x['molecule_chembl_id'] for x in resolve(identifier)])
            targets = mols_to_targets(valid_identifiers,
                                      organism=options.organism,
                                      only_ids=(options.dest_format == 'chembl_id'),
                                      include_parents=options.parent,
                                      chunk_size=int(options.chunk))
            out_f.write(serializer_cls.serialize_line(targets, human=options.human, name=','.join(valid_identifiers)))

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------------------------------------------------------
