#!/usr/bin/env python
from __future__ import print_function

__author__ = 'mnowotka'

# ----------------------------------------------------------------------------------------------------------------------

import sys
import argparse
from chembl_webresource_client.scripts.utils import resolve
from chembl_webresource_client.scripts.utils import get_parents
from chembl_webresource_client.scripts.utils import get_serializer

# ----------------------------------------------------------------------------------------------------------------------


def get_options():

    description = 'Try to convert various chemical names and identifiers into a single type of identifiers taken from' \
                  'the ChEMBL DB (by default ChEMBL IDs). By default input is read from the standard input and ' \
                  'output written to the standard output'
    parser = argparse.ArgumentParser(description=description, prog='chembl_ids')
    parser.add_argument('-i', '--input', action='store', dest='input',
                        help='input file with chemical identifiers, one line each')
    parser.add_argument('-o', '--output', action='store', dest='output',
                        help='output file with identifiers from ChEMBL (ChEMBL IDs by default)')
    parser.add_argument('-f', '--format', action='store', dest='format', default='chembl_id',
                        help='output file format, can be chosen from 5 options: [chembl_id, smi, sdf, inchi, inchi_key]')
    parser.add_argument('-s', '--single', action='store_true', dest='single',
                        help='if the name is resolved into more than one result, show only the most relevant one')
    parser.add_argument('-p', '--parent', action='store_true', dest='parent',
                        help='instead of actual results, fetch their parents')
    parser.add_argument('-H', '--Human', action='store_true', dest='human',
                        help='human readable output: prints header and first column with original names')
    return parser.parse_args()

# ----------------------------------------------------------------------------------------------------------------------


def main():

    options = get_options()
    with open(options.input) if options.input else sys.stdin as in_f, \
            open(options.output, 'w') if options.output else sys.stdout as out_f:

        serializer_cls = get_serializer(options.format)
        if not serializer_cls:
            sys.stderr.write('Unsupported format', options.format)
            return

        if options.human:
            serializer_cls.write_header(out_f)

        for line in in_f:
            name = line.strip()
            if not name:
                continue
            resolved = None
            try:
                resolved = resolve(name, options.single)
            except Exception as e:
                pass
            if options.parent:
                resolved = get_parents(resolved)
            out_f.write(serializer_cls.serialize_line(resolved, human=options.human, name=name))

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------------------------------------------------------
