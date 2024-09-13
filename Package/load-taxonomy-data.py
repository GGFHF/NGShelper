#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program loads taxanomy infomation downloaded from https://ftp.ncbi.nih.gov/pub/taxonomy/
into a SQLite database.

This software has been developed by:

    GI en especies leñosas (WooSp)
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

    # load taxonomy data from files into de gymnoTOA database
    load_taxonomy_data(conn, args.taxonomy_node_file, args.species_name_file)

    # close connection to gymnoTOA database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads taxanomy infomation downloaded from https://ftp.ncbi.nih.gov/pub/taxonomy/\n' \
       'into a SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--nodes', dest='taxonomy_node_file', help='Path of the taxonomy nodes file (mandatory).')
    parser.add_argument('--names', dest='species_name_file', help='Path of the species name file (mandatory).')
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

    # check "taxonomy_node_file"
    if args.taxonomy_node_file is None:
        xlib.Message.print('error', '*** The input taxonomy node file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.taxonomy_node_file):
        xlib.Message.print('error', f'*** The file {args.taxonomy_node_file} does not exist.')
        OK = False

    # check "species_name_file"
    if args.species_name_file is None:
        xlib.Message.print('error', '*** The input spececies name file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.species_name_file):
        xlib.Message.print('error', f'*** The file {args.species_name_file} does not exist.')
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

def load_taxonomy_data(conn, taxonomy_node_file, species_name_file):
    '''
    Load taxanomy infomation downloaded from https://ftp.ncbi.nih.gov/pub/taxonomy/
    into the database of gymnoTOA (Gymnosperms Taxonomy-oriented Annotation).
    '''

    # drop the table "taxonomy_nodes" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "taxonomy_nodes" ...\n')
    xsqlite.drop_taxonomy_nodes(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create the table "taxonomy_nodes"
    xlib.Message.print('verbose', 'Creating the table "taxonomy_nodes" ...\n')
    xsqlite.create_taxonomy_nodes(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the record counter
    record_counter = 0

    # initialize the inserted row counter
    inserted_row_counter = 0

    # open the taxonomy node file
    if taxonomy_node_file.endswith('.gz'):
        try:
            taxonomy_node_file_id = gzip.open(taxonomy_node_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', taxonomy_node_file)
    else:
        try:
            taxonomy_node_file_id = open(taxonomy_node_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', taxonomy_node_file)

    # read the first record
    record = taxonomy_node_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # initialize the row data dictionary
        row_dict = {}

        # extract data
        # record format: tax_id <field_sep> parent_tax_id <field_sep> rank <field_sep> embl_code <field_sep> division_id <field_sep> inherited_div_flag <field_sep> genetic_code_id <field_sep> inherited_gc_flag <field_sep> mitochondrial_genetic_code_id <field_sep> inherited_mgc_flag <field_sep> genbank_hidden_flag <field_sep> hidden_subtree_root_flag <field_sep> comments <record_sep>
        field_sep = '\t|\t'
        new_field_sep = '\t\t\t'
        record_sep = '\t|\n'
        record = record.replace(field_sep, new_field_sep)
        data_list = re.split(new_field_sep, record.replace(record_sep,''))
        try:
            row_dict['tax_id'] = data_list[0].strip()
            row_dict['parent_tax_id'] = data_list[1].strip()
            row_dict['rank'] = data_list[2].strip()
        except Exception as e:
            raise xlib.ProgramException(e, 'F009', os.path.basename(taxonomy_node_file), record_counter)

        # check "tax_id"
        try:
            row_dict['tax_id'] = int(row_dict['tax_id'])
        except Exception as e:
            raise xlib.ProgramException(e, 'D001', 'tax_id', os.path.basename(taxonomy_node_file), record_counter)

        # check "parent_tax_id"
        try:
            row_dict['parent_tax_id'] = int(row_dict['parent_tax_id'])
        except Exception as e:
            raise xlib.ProgramException(e, 'D001', 'parent_tax_id', os.path.basename(taxonomy_node_file), record_counter)

        # insert data into the table "taxonomy_nodes"
        xsqlite.insert_taxonomy_nodes_row(conn, row_dict)
        inserted_row_counter += 1

        # print counters
        xlib.Message.print('verbose', f'\rtaxonomy nodes file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

        # read the next record
        record = taxonomy_node_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # create the index "taxonomy_nodes_index_1" on the table "taxonomy_nodes"
    xlib.Message.print('verbose', 'Creating the index 1 on the table "taxonomy_nodes" ...\n')
    xsqlite.create_taxonomy_nodes_index_1(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # create the index "taxonomy_nodes_index_2" on the table "taxonomy_nodes"
    xlib.Message.print('verbose', 'Creating the index 2 on the table "taxonomy_nodes" ...\n')
    xsqlite.create_taxonomy_nodes_index_2(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into the SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

    # close taxonomy nodes file
    taxonomy_node_file_id.close()

    # drop the table "species_names" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "species_names" ...\n')
    xsqlite.drop_species_names(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create the table "species_names"
    xlib.Message.print('verbose', 'Creating the table "species_names" ...\n')
    xsqlite.create_species_names(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the record counter
    record_counter = 0

    # initialize the inserted row counter
    inserted_row_counter = 0

    # open the species name file
    if species_name_file.endswith('.gz'):
        try:
            species_names_file_id = gzip.open(species_name_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', species_name_file)
    else:
        try:
            species_names_file_id = open(species_name_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', species_name_file)

    # read the first record
    record = species_names_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # initialize the row data dictionary
        row_dict = {}

        # extract data
        # record format: tax_id <field_sep> name_txt <field_sep> unique_name <field_sep> name_class <record_sep>
        field_sep = '\t|\t'
        new_field_sep = '\t\t\t'
        record_sep = '\t|\n'
        record = record.replace(field_sep, new_field_sep)
        data_list = re.split(new_field_sep, record.replace(record_sep,''))
        try:
            row_dict['tax_id'] = data_list[0].strip()
            row_dict['name_txt'] = data_list[1].strip()
            row_dict['unique_name'] = data_list[2].strip()
            row_dict['name_class'] = data_list[3].strip()
        except Exception as e:
            raise xlib.ProgramException(e, 'F009', os.path.basename(species_name_file), record_counter)

        # check "tax_id"
        try:
            int(row_dict['tax_id'])
        except Exception as e:
            raise xlib.ProgramException(e, 'D001', 'tax_id', os.path.basename(species_name_file), record_counter)

        # check "name_txt"
        row_dict['name_txt'] = row_dict['name_txt'].replace("'", "´")

        # check "unique_name"
        if row_dict['unique_name'] == '':
            row_dict['unique_name'] = '-'
        else:
            row_dict['unique_name'] = row_dict['unique_name'].replace("'", "´")

        # insert data into the table "species_names"
        xsqlite.insert_species_names_row(conn, row_dict)
        inserted_row_counter += 1

        # print counters
        xlib.Message.print('verbose', f'\rspecies names file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

        # read the next record
        record = species_names_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # create the index "taxonomy_names_index_1" on the table "species_names"
    xlib.Message.print('verbose', 'Creating the index 1 on the table "species_names" ...\n')
    xsqlite.create_species_names_index_1(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # create the index "taxonomy_names_index_2" on the table "species_names"
    xlib.Message.print('verbose', 'Creating the index 2 on the table "species_names" ...\n')
    xsqlite.create_species_names_index_2(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into the SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

    # close species names file
    species_names_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
