#!/usr/bin/env python
from __future__ import print_function


__author__ = 'mnowotka'

# ----------------------------------------------------------------------------------------------------------------------

import sys
import argparse
from chembl_webresource_client.scripts.utils import get_serializer
from chembl_webresource_client.scripts.utils import resolve_target, targets_to_mols


# ----------------------------------------------------------------------------------------------------------------------


def get_options():

    description = 'Find related compounds for a set of targets'
    parser = argparse.ArgumentParser(description=description, prog='chembl_t2m')
    parser.add_argument('-i', '--input', action='store', dest='input',
                        help='input file, standard input by default')
    parser.add_argument('-o', '--output', action='store', dest='output',
                        help='output file, standard output by default')
    parser.add_argument('-d', '--destination-format', action='store', dest='dest_format', default='uniprot',
                        help='output file format. can be chosen from 3 options: '
                             '[sdf, smi, chembl_id]')
    parser.add_argument('-H', '--Human', action='store_true', dest='human',
                        help='human readable output: prints header and first column with original names')
    parser.add_argument('-p', '--parent', action='store_true', dest='parent',
                        help='when fetching compounds include their parents as well')
    parser.add_argument('-c', '--chunk-size', action='store', dest='chunk', default='1000',
                        help='Size of chunk of data retrieved from API')
    return parser.parse_args()

# ----------------------------------------------------------------------------------------------------------------------


def main():
    options = get_options()

    with open(options.input) if options.input else sys.stdin as in_f, \
            open(options.output, 'w') if options.output else sys.stdout as out_f:

        serializer_cls = get_serializer(options.dest_format)
        if not serializer_cls:
            sys.stderr.write('Unsupported format', options.dest_format)
            return

        if options.human:
            serializer_cls.write_header(out_f)

        for line in in_f:
            chunk = line.strip().split()[0]
            identifiers = chunk.strip().split(',')
            valid_identifiers = list()
            for identifier in identifiers:
                target = resolve_target(identifier)
                if not target:
                    continue
                valid_identifiers.append(target)
            mols = targets_to_mols(valid_identifiers,
                                   only_ids=(options.dest_format == 'chembl_id'),
                                   include_parents=options.parent,
                                   chunk_size=int(options.chunk))
            out_f.write(serializer_cls.serialize_line(mols, human=options.human, name=','.join(valid_identifiers)))

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------------------------------------------------------
