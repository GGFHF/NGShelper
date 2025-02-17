#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program loads Gene Ontology data included from the file https://purl.obolibrary.org/obo/go.obo
into a SQLite database.

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

    # load table "go_ontology"
    load_table_go_ontology(conn, args.ontology_file)

    # close connection to TOA database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads Gene Ontology data into a SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--ontology', dest='ontology_file', help='Path of the ontology file (mandatory).')
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

    # check "ontology_file"
    if args.ontology_file is None:
        xlib.Message.print('error', '*** The ontology file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.ontology_file):
        xlib.Message.print('error', f'*** The file {args.ontology_file} does not exist.')
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

def load_table_go_ontology(conn, ontology_file):
    '''
    Load Gene Ontology data included from the file https://purl.obolibrary.org/obo/go.obo
    into a SQLite database.
    '''

    # drop table "go_ontology" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "go_ontology" ...\n')
    xsqlite.drop_go_ontology(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create table "go_ontology"
    xlib.Message.print('verbose', 'Creating the table "go_ontology" ...\n')
    xsqlite.create_go_ontology(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the row data dictionary and the external database name and description
    row_dict = {}
    row_dict['external_db'] = 'ec'
    row_dict['external_desc'] = xlib.get_na()

    # open the ontology file
    if ontology_file.endswith('.gz'):
        try:
            ontology_file_id = gzip.open(ontology_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', ontology_file)
    else:
        try:
            ontology_file_id = open(ontology_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', ontology_file)

    # initialize the record counter
    record_counter = 0

    # initialize the inserted row counter
    inserted_row_counter = 0

    # read the first record
    record = ontology_file_id.readline()

    # while there are records and they are the header
    while record != '' and not record.startswith('[Term]'):

        # add 1 to record counter
        record_counter += 1

        # print record counter
        xlib.Message.print('verbose', f'\rOntology file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

        # read the next record
        record = ontology_file_id.readline()

    # if there is a first term block
    if record.startswith('[Term]'):

        # while there are records
        while record != '':

            # add 1 to record counter
            record_counter += 1

            # print record counter
            xlib.Message.print('verbose', f'\rOntology file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

            # read the next record
            record = ontology_file_id.readline()

            # initialize the row dictionary
            row_dict = {}
            row_dict['go_id'] = ''
            row_dict['go_name'] = ''
            row_dict['namespace'] = ''
            alt_id_list = []

            # while there are records and they are term details
            while record != '' and not record.startswith('[Term]'):

                # add 1 to record counter
                record_counter += 1

                # get the GO identification
                if record.startswith('id:'):
                    row_dict['go_id'] = record[len('id:'):].strip()

                # get the GO name
                if record.startswith('name:'):
                    row_dict['go_name'] = record[len('name:'):].strip()

                    # change quotation marks and semicolons in "go_name"
                    row_dict['go_name'] = row_dict['go_name'].replace("'", '|').replace(';', ',')

                # get the namespace
                if record.startswith('namespace:'):
                    row_dict['namespace'] = record[len('namespace:'):].strip()

                    # change quotation marks and semicolons in "namespace"
                    row_dict['namespace'] = row_dict['namespace'].replace("'", '|').replace(';', ',').replace('_', ' ')

                # get the alternative identificationnamespace
                if record.startswith('alt_id:'):
                    alt_id_list.append(record[len('alt_id:'):].strip())

                # print record counter
                xlib.Message.print('verbose', f'\rOntology file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

                # read the next record
                record = ontology_file_id.readline()

                # break the loop when typedef sections start
                if record.startswith('[Typedef]'):
                    break

            # insert data into table "go_ontology"
            xsqlite.insert_go_ontology_row(conn, row_dict)
            inserted_row_counter += 1
            for alt_id in alt_id_list:
                row_dict['go_id'] = alt_id
                xsqlite.insert_go_ontology_row(conn, row_dict)
                inserted_row_counter += 1

            # print record counter
            xlib.Message.print('verbose', f'\rOntology file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

            # break the loop when typedef sections start
            if record.startswith('[Typedef]'):
                break

    xlib.Message.print('verbose', '\n')

    # close ontology file
    ontology_file_id.close()

    # create the index on the table "go_ontology"
    xlib.Message.print('verbose', 'Creating the index on the table "go_ontology" ...\n')
    xsqlite.create_go_ontology_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into TOA database
    xlib.Message.print('verbose', 'Saving changes into TOA database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
