#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program loads the relationships of orthologous genes into a SQLite database.

This software has been developed by:

    GI en Desarrollo de Especies y Comunidades Leñosas (WooSp)
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
import re
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

    # load the relationships of orthologous genes into the database of gymnoTOA
    load_gene_orthologs(conn, args.relationship_file)

    # close connection to gymnoTOA database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads relationships of orthologous genes\n' \
       'into a SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--relfile', dest='relationship_file', help='Path of the relationship file (mandatory).')
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

    # check "relationship_file"
    if args.relationship_file is None:
        xlib.Message.print('error', '*** The input relationship file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.relationship_file):
        xlib.Message.print('error', f'*** The file {args.relationship_file} does not exist.')
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

def load_gene_orthologs(conn, relationship_file):
    '''
    Load the relationships of orthologous genes into the database of gymnoTOA
    (Gymnosperms Taxonomy-oriented Annotation).
    '''

    # drop the table "gene_orthologs" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "gene_orthologs" ...\n')
    xsqlite.drop_gene_orthologs(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create the table "gene_orthologs"
    xlib.Message.print('verbose', 'Creating the table "gene_orthologs" ...\n')
    xsqlite.create_gene_orthologs(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the record counter
    record_counter = 0

    # initialize the inserted row counter
    inserted_row_counter = 0

    # open the relationship file
    if relationship_file.endswith('.gz'):
        try:
            relationship_file_id = gzip.open(relationship_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', relationship_file)
    else:
        try:
            relationship_file_id = open(relationship_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', relationship_file)

    # read the first record
    record = relationship_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # process data records
        if record_counter > 1:

            # initialize the row data dictionary
            row_dict = {}

            # extract data
            # record format: tax_id <field_sep> gene_id <field_sep> other_tax_id <field_sep> other_gene_id <record_sep>
            field_sep = '\t'
            record_sep = '\n'
            data_list = re.split(field_sep, record.replace(record_sep,''))
            try:
                row_dict['tax_id'] = data_list[0].strip()
                row_dict['gene_id'] = data_list[1].strip()
                row_dict['other_tax_id'] = data_list[3].strip()
                row_dict['other_gene_id'] = data_list[4].strip()
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(relationship_file), record_counter)

            # check "tax_id"
            try:
                int(row_dict['tax_id'])
            except Exception as e:
                raise xlib.ProgramException(e, 'D001', 'tax_id', os.path.basename(relationship_file), record_counter)

            # check "gene_id"
            try:
                int(row_dict['gene_id'])
            except Exception as e:
                raise xlib.ProgramException(e, 'D001', 'gene_id', os.path.basename(relationship_file), record_counter)

            # check "other_tax_id"
            try:
                int(row_dict['other_tax_id'])
            except Exception as e:
                raise xlib.ProgramException(e, 'D001', 'other_tax_id', os.path.basename(relationship_file), record_counter)

            # check "other_gene_id"
            try:
                int(row_dict['other_gene_id'])
            except Exception as e:
                raise xlib.ProgramException(e, 'D001', 'other_gene_id', os.path.basename(relationship_file), record_counter)

            # insert data into the table "gene_orthologs"
            xsqlite.insert_gene_orthologs_row(conn, row_dict)
            inserted_row_counter += 1

        # print counters
        xlib.Message.print('verbose', f'\rrelationship file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

        # read the next record
        record = relationship_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # create the index "gene_orthologs_index_1" on the table "gene_orthologs"
    xlib.Message.print('verbose', 'Creating the index 1 on the table "gene_orthologs" ...\n')
    xsqlite.create_gene_orthologs_index_1(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # create the index "gene_orthologs_index_2" on the table "gene_orthologs"
    xlib.Message.print('verbose', 'Creating the index 2 on the table "gene_orthologs" ...\n')
    xsqlite.create_gene_orthologs_index_2(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into the SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

    # close relationship file
    relationship_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
