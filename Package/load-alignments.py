#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

'''
This software has been developed by:

    GI Sistemas Naturales e Historia Forestal (formerly known as GI Genetica, Fisiologia e Historia Forestal)
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

'''
This program loads alignment data into NGShelper database.
'''

#-------------------------------------------------------------------------------

import argparse
import gzip
import os
import sys

import xlib
import xsqlite

#-------------------------------------------------------------------------------

def main(argv):
    '''
    Main line of the program.
    '''

    # check the operating system
    xlib.check_os()

    # get and check the arguments
    parser = build_parser()
    args = parser.parse_args()
    check_args(args)

    # connect to the NGShelper database
    conn = xsqlite.connect_database(args.ngshelper_database)

    # load alignment data
    load_alignments(conn, args.alignment_file)

    # close connection to NGShelper database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads alignment data into NGShelper database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--db', dest='ngshelper_database', help='Path of the NGShelper database (mandatory).')
    parser.add_argument('--alignment', dest='alignment_file', help='Path of alignmanet file in CSV format (mandatory).')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def check_args(args):
    '''
    Check the input arguments.
    '''

    # initialize the control variable
    OK = True

    # check "ngshelper_database"
    if args.ngshelper_database is None:
        xlib.Message.print('error', '*** The NGShelper database is not indicated in the input arguments.')
        OK = False

    # check "alignment_file"
    if args.alignment_file is None:
        xlib.Message.print('error', '*** The alignment file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.alignment_file):
        xlib.Message.print('error', f'*** The file {args.alignment_file} does not exist.')
        OK = False

    # check "verbose"
    if args.verbose is None:
        args.verbose = xlib.Const.DEFAULT_VERBOSE
    elif not xlib.check_code(args.verbose, xlib.get_verbose_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** verbose has to be {xlib.get_verbose_code_list_text()}.')
        OK = False
    if args.verbose.upper() == 'Y':
        xlib.Message.set_verbose_status(True)

    # check "trace"
    if args.trace is None:
        args.trace = xlib.Const.DEFAULT_TRACE
    elif not xlib.check_code(args.trace, xlib.get_trace_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** trace has to be {xlib.get_trace_code_list_text()}.')
        OK = False
    if args.trace.upper() == 'Y':
        xlib.Message.set_trace_status(True)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def load_alignments(conn, alignment_file):
    '''
    Load alignment data into NGShelper database.
    '''

    # drop the table "alignments" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "alignments" ...\n')
    xsqlite.drop_alignments(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create the table "alignments"
    xlib.Message.print('verbose', 'Creating the table "alignments" ...\n')
    xsqlite.create_alignments(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the record counter
    record_counter = 0

    # initialize the inserted row counter
    inserted_row_counter = 0

    # initialize the header record control
    header_record = True

    # open the alignments file
    if alignment_file.endswith('.gz'):
        try:
            alignment_file_id = gzip.open(alignment_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', alignment_file)
    else:
        try:
            alignment_file_id = open(alignment_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', alignment_file)

    # read the first record
    record = alignment_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # initialize the row data dictionary
        row_dict = {}

        # process the header record 
        if header_record:
            header_record = False

        # process data records
        else:

            # extract data 
            # record format: variant_id;chromosome_id;identity;coord1;coord2;e-value
            data_list = []
            begin = 0
            for end in [i for i, chr in enumerate(record) if chr == ';']:
                data_list.append(record[begin:end].strip())
                begin = end + 1
            data_list.append(record[begin:].strip('\n').strip())
            try:
                row_dict['variant_id'] = data_list[0]
                row_dict['chromosome_id'] = data_list[1]
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(alignment_file), record_counter)

            # insert data into the table "alignments"
            xsqlite.insert_alignments_row(conn, row_dict)
            inserted_row_counter += 1

            # print counters
            xlib.Message.print('verbose', f'\ralignment file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

        # read the next record
        record = alignment_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # create the index "vcf_alignments_index" on the table "alignments"
    xlib.Message.print('verbose', 'Creating the index on the table "alignments" ...\n')
    xsqlite.create_alignments_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into NGShelper database
    xlib.Message.print('verbose', 'Saving changes into NGShelper database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

    # close alignments file
    alignment_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
