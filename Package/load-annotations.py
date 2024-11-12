#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program loads annotation data from a TOA annotation file into SQLite database.

This software has been developed by:

    GI en Especies Leñosas (WooSp)
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

    # connect to the SQLite database
    conn = xsqlite.connect_database(args.sqlite_database)

    # load annotation data from a TOA annotation file
    load_annotations(conn, args.annotation_file, args.toa_file_type)

    # close connection to SQLite database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads annotation data from a TOA annotation file into SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--annotation', dest='annotation_file', help='Path of the TOA annotation file in CSV format (mandatory).')
    parser.add_argument('--type', dest='toa_file_type', help=f'Type of the TOA annotation file (mandatory): {xlib.get_toa_file_type_code_list_text()}.')
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

    # check "sqlite_database"
    if args.sqlite_database is None:
        xlib.Message.print('error', '*** The SQLite database is not indicated in the input arguments.')
        OK = False

    # check "annotation_file"
    if args.annotation_file is None:
        xlib.Message.print('error', '*** The TOA annotation file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.annotation_file):
        xlib.Message.print('error', f'*** The file {args.annotation_file} does not exist.')
        OK = False

    # check "toa_file_type"
    if args.toa_file_type is None:
        xlib.Message.print('error', '*** The type of TOA annotation file is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.toa_file_type, xlib.get_toa_file_type_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The type of TOA annotation file has to be {xlib.get_toa_file_type_code_list_text()}.')
        OK = False
    else:
        args.toa_file_type = args.toa_file_type.upper()

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

def load_annotations(conn, annotation_file, toa_file_type):
    '''
    Load annotation data from a TOA annotation file into SQLite database.
    '''

    # drop the table "annotations" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "annotations" ...\n')
    xsqlite.drop_annotations(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create the table "annotations"
    xlib.Message.print('verbose', 'Creating the table "annotations" ...\n')
    xsqlite.create_annotations(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the record counter
    record_counter = 0

    # initialize the inserted row counter
    inserted_row_counter = 0

    # open the annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', annotation_file)
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', annotation_file)

    # read head record of the annotation file
    (record, _, data_dict) = xlib.read_toa_annotation_record(annotation_file, annotation_file_id, toa_file_type, record_counter)

    # add 1 to record counter
    record_counter += 1

    # read the first data record of the annotation file
    (record, _, data_dict) = xlib.read_toa_annotation_record(annotation_file, annotation_file_id, toa_file_type, record_counter)

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # save the sequence identification
        seq_id = data_dict['seq_id']
        min_evalue = float(sys.maxsize)
        description = 'N/A'

        # while there are records and same sequence identification
        while record != '' and seq_id == data_dict['seq_id']:

            # get e-Value
            try:
                hsp_evalue = float(data_dict['hsp_evalue'])
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(annotation_file), record_counter)

            # save the description of the annotation with lower e-Value provided that the description is not 'N/A'
            if min_evalue > hsp_evalue and data_dict['desc'] != 'N/A':
                min_evalue = hsp_evalue
                description = data_dict['desc'].replace("'", '´').replace(';', ',')

            # read the next record
            (record, _, data_dict) = xlib.read_toa_annotation_record(annotation_file, annotation_file_id, toa_file_type, record_counter)

        # insert data into the table "annotations"
        row_dict = {'seq_id': seq_id, 'description': description}
        xsqlite.insert_annotations_row(conn, row_dict)
        inserted_row_counter += 1

        # print counters
        xlib.Message.print('verbose', f'\rAnnotations file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

        # read the next record
        record = annotation_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # create the index "vcf_annotations_index" on the table "annotations"
    xlib.Message.print('verbose', 'Creating the index on the table "annotations" ...\n')
    xsqlite.create_annotations_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

    # close annotations file
    annotation_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
