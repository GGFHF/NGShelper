#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program loads genomic features from a GFF file into NGShelper database.

This software has been developed by:

    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

import argparse
import gzip
import os
import sys

import xlib
import xsqlite

#-------------------------------------------------------------------------------

def main():
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

    # load genomic features from a genomic feature file
    load_genomic_features(conn, args.gff_file, args.gff_format)

    # close connection to NGShelper database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads genomic features from a GFF file into NGShelper database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--db', dest='ngshelper_database', help='Path of the NGShelper database (mandatory).')
    parser.add_argument('--gff', dest='gff_file', help='Path of the GFF file (mandatory).')
    parser.add_argument('--format', dest='gff_format', help='The format of the GFF file: GFF3; default: GFF3.')
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

    # check "gff_file"
    if args.gff_file is None:
        args.gff_file = 'GFF3'
    elif not os.path.isfile(args.gff_file):
        xlib.Message.print('error', f'*** The file {args.gff_file} does not exist.')
        OK = False

    # check "gff_format"
    if args.gff_file is None:
        xlib.Message.print('error', '*** The format of the GFF file is not indicated in the input arguments.')
        OK = False
    elif args.gff_format.upper() != 'GFF3':
        xlib.Message.print('error', '*** The format of the GFF file has to be GFF3.')
        OK = False
    else:
        args.gff_format = args.gff_format.upper()

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

def load_genomic_features(conn, gff_file, gff_format):
    '''
    x
    '''

    # drop the table "genomic_features" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "genomic_features" ...\n')
    xsqlite.drop_genomic_features(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create the table "genomic_features"
    xlib.Message.print('verbose', 'Creating the table "genomic_features" ...\n')
    xsqlite.create_genomic_features(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # open the GFF file
    if gff_file.endswith('.gz'):
        try:
            gff_file_id = gzip.open(gff_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', gff_file)
    else:
        try:
            gff_file_id = open(gff_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', gff_file)

    # initialize the record counter
    record_counter = 0

    # initialize the inserted row counter
    inserted_row_counter = 0

    # initialize the first header record control
    first_header_record = True

    # read the first record
    record = gff_file_id.readline()

    # while there are records
    while record != '':

        # while there are records and they are process header records
        while record != '' and record.startswith('#'):

            # add 1 to record counter
            record_counter += 1

            if record.startswith('#'):
                if first_header_record and gff_format == 'GFF3':
                    if not record.startswith('##gff-version 3'):
                        raise xlib.ProgramException('', 'F005', os.path.basename(gff_file), 'GFF3')
                first_header_record = False

            # print record counter
            xlib.Message.print('verbose', f'\rGFF file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

            # read the next record
            record = gff_file_id.readline()

        # while there are records and they are data records
        while record != '' and not record.startswith('#'):

            # extract data
            # record format: seqid	source	type	start	tend	score	strand	phase	attributes
            row_dict = {}
            data_list = []
            pos_1 = 0
            for pos_2 in [i for i, chr in enumerate(record) if chr == '\t']:
                data_list.append(record[pos_1:pos_2].strip())
                pos_1 = pos_2 + 1
            data_list.append(record[pos_1:].strip('\n').strip())
            try:
                row_dict['seq_id'] = data_list[0]
                row_dict['type'] = data_list[2]
                row_dict['start'] = data_list[3]
                row_dict['end'] = data_list[4]
                attributes = data_list[8]
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(gff_file), record_counter)

            # initialize the old sequence identification
            old_seq_id = row_dict['seq_id']

            # initialize the list used to control not insert rows with the same data
            control_list = []

            # while there are records and they are data record with the same sequence identification
            while record != '' and not record.startswith('#') and old_seq_id == row_dict['seq_id']:

                # add 1 to record counter
                record_counter += 1

                # initialize the row data dictionary
                row_dict = {}

                # extract data
                # record format: seqid	source	type	start	tend	score	strand	phase	attributes
                data_list = []
                pos_1 = 0
                for pos_2 in [i for i, chr in enumerate(record) if chr == '\t']:
                    data_list.append(record[pos_1:pos_2].strip())
                    pos_1 = pos_2 + 1
                data_list.append(record[pos_1:].strip('\n').strip())
                try:
                    row_dict['seq_id'] = data_list[0]
                    row_dict['type'] = data_list[2]
                    row_dict['start'] = data_list[3]
                    row_dict['end'] = data_list[4]
                    attributes = data_list[8]
                except Exception as e:
                    raise xlib.ProgramException(e, 'F009', os.path.basename(gff_file), record_counter)

                # set the control variable with the record data
                control = f'{row_dict["seq_id"]}-{row_dict["type"]}-{row_dict["start"]}-{row_dict["end"]}'

                # if the record data is not in the list used to control
                if control not in control_list:

                    # add record data to the list
                    control_list.append(control)

                    # check "start"
                    try:
                        row_dict['start'] = int(row_dict['start'])
                    except Exception as e:
                        raise xlib.ProgramException(e, 'D001', 'start', os.path.basename(gff_file), record_counter)

                    # check "end"
                    try:
                        row_dict['end'] = int(row_dict['end'])
                    except Exception as e:
                        raise xlib.ProgramException(e, 'D001', 'stop', os.path.basename(gff_file), record_counter)

                    # get "gene" data from "attributes"
                    row_dict['gene'] = xlib.get_na()
                    literal = 'gene='
                    pos_1 = attributes.find(literal)
                    if pos_1 > -1:
                        pos_2 = attributes.find(';', pos_1 + len(literal) + 1)
                        row_dict['gene'] = attributes[pos_1 + len(literal):pos_2]

                    # insert data into the table "genomic_features"
                    xsqlite.insert_genomic_features_row(conn, row_dict)
                    inserted_row_counter += 1

                # print record counter
                xlib.Message.print('verbose', f'\rGFF file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

                # read the next record
                record = gff_file_id.readline()

                # extract data
                # record format: seqid	source	type	start	tend	score	strand	phase	attributes
                if not record.startswith('#'):
                    row_dict = {}
                    data_list = []
                    pos_1 = 0
                    for pos_2 in [i for i, chr in enumerate(record) if chr == '\t']:
                        data_list.append(record[pos_1:pos_2].strip())
                        pos_1 = pos_2 + 1
                    data_list.append(record[pos_1:].strip('\n').strip())
                    try:
                        row_dict['seq_id'] = data_list[0]
                        row_dict['type'] = data_list[2]
                        row_dict['start'] = data_list[3]
                        row_dict['end'] = data_list[4]
                        attributes = data_list[8]
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F009', os.path.basename(gff_file), record_counter)

    xlib.Message.print('verbose', '\n')

    # create the index "genomic_features_index" on the table "genomic_features"
    xlib.Message.print('verbose', 'Creating the index on the table "genomic_features" ...\n')
    xsqlite.create_genomic_features_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into NGShelper database
    xlib.Message.print('verbose', 'Saving changes into NGShelper database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

    # close GFF file
    gff_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
