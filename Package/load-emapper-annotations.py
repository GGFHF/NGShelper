#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program loads the eggNOG-mapper annotations into the database a SQLite
 database.

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

    # load the eggNOG-mapper annotations into the database a SQLite database
    load_emapper_annotations(conn, args.annotation_file, args.taxname_file)

    # close connection to SQLite database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads eggNOG-mapper annotations into a SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--annotations', dest='annotation_file', help='Path of the eggNOG-mapper annotation file (mandatory).')
    parser.add_argument('--taxnames', dest='taxname_file', help='Path of the NCBI taxonomy name file (mandatory).')
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
        xlib.Message.print('error', '*** The database is not indicated in the input arguments.')
        OK = False

    # check "annotation_file"
    if args.annotation_file is None:
        xlib.Message.print('error', '*** The input eggNOG-mapper annotation file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.annotation_file):
        xlib.Message.print('error', f'*** The file {args.annotation_file} does not exist.')
        OK = False

    # check "taxname_file"
    if args.taxname_file is None:
        xlib.Message.print('error', '*** The input NCBI taxonomy names file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.taxname_file):
        xlib.Message.print('error', f'*** The file {args.taxname_file} does not exist.')
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

def load_emapper_annotations(conn, annotation_file, taxname_file):
    '''
    Load the eggNOG-mapper annotations into the database a SQLite database.
    '''

    # get the taxonomy name dictionary
    taxname_dict = get_taxname_dict(taxname_file)

    # drop the table "emapper_annotations" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "emapper_annotations" ...\n')
    xsqlite.drop_emapper_annotations(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create the table "emapper_annotations"
    xlib.Message.print('verbose', 'Creating the table "emapper_annotations" ...\n')
    xsqlite.create_emapper_annotations(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the record counter
    record_counter = 0

    # initialize the inserted row counter
    inserted_row_counter = 0

    # open the eggNOG-mapper annotation file
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

    # read the first record
    record = annotation_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # when the record is not a comment
        if not record.startswith('#'):

            # initialize the row data dictionary
            row_dict = {}

            # extract data
            # record format: cluster_id <field_sep> seed_ortholog <field_sep> evalue <field_sep> score <field_sep> eggnog_ogs <field_sep> max_annot_lvl <field_sep> cog_category <field_sep> description <field_sep> preferred_name <field_sep> goterms <field_sep> ec <field_sep> kegg_kos <field_sep> kegg_pathways <field_sep> kegg_modules <field_sep> kegg_reactions <field_sep> kegg_rclasses <field_sep> brite <field_sep> kegg_tc <field_sep> cazy <field_sep> bigg_reaction <field_sep> pfams <record_sep>
            field_sep = '\t'
            record_sep = '\n'
            data_list = re.split(field_sep, record.replace(record_sep,''))
            try:
                row_dict['cluster_id'] = data_list[0].strip()
                seed_ortholog = data_list[1].strip()
                point_pos = seed_ortholog.find('.')
                species_tax_id = seed_ortholog[:point_pos]
                species_name = taxname_dict.get(species_tax_id, species_tax_id)
                ortholog_seq_id = seed_ortholog[point_pos + 1:]
                row_dict['ortholog_seq_id'] = ortholog_seq_id
                row_dict['ortholog_species'] = species_name
                row_dict['eggnog_ogs'] = data_list[4].strip()
                row_dict['cog_category'] = data_list[6].strip()
                row_dict['description'] = data_list[7].strip()
                row_dict['goterms'] = data_list[9].strip().replace(',', '|')
                row_dict['ec'] = data_list[10].strip().replace(',', '|')
                row_dict['kegg_kos'] = data_list[11].strip().replace(',', '|')
                row_dict['kegg_pathways'] = data_list[12].strip().replace(',', '|')
                row_dict['kegg_modules'] = data_list[13].strip().replace(',', '|')
                row_dict['kegg_reactions'] = data_list[14].strip().replace(',', '|')
                row_dict['kegg_rclasses'] = data_list[15].strip().replace(',', '|')
                row_dict['brite'] = data_list[16].strip().replace(',', '|')
                row_dict['kegg_tc'] = data_list[17].strip().replace(',', '|')
                row_dict['cazy'] = data_list[18].strip().replace(',', '|')
                row_dict['pfams'] = data_list[20].strip().replace(',', '|')
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(annotation_file), record_counter)

            # replace characters not allowed in species name
            row_dict['ortholog_species'] = row_dict['ortholog_species'].replace('"', '').replace("'", "").replace(';', ',')

            # replace characters not allowed in description
            row_dict['description'] = row_dict['description'].replace('"', '').replace("'", "").replace(';', ',')

            # insert data into the table "emapper_annotations"
            xsqlite.insert_emapper_annotations_row(conn, row_dict)
            inserted_row_counter += 1

        # print counters
        xlib.Message.print('verbose', f'\reggNOG-mapper annotation file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

        # read the next record
        record = annotation_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # create the index "emapper_annotations_index" on the table "emapper_annotations"
    xlib.Message.print('verbose', 'Creating the index on the table "emapper_annotations" ...\n')
    xsqlite.create_emapper_annotations_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

    # close eggNOG-mapper annotation file
    annotation_file_id.close()

#-------------------------------------------------------------------------------

def get_taxname_dict(taxname_file):
    '''
    Get the taxonomy name dictionary from del taxonomy name file.
    '''

    # initialize the taxonomy name dictionary
    taxname_dict = {}

    # initialize the record counter
    record_counter = 0

    # open the taxonomy name file
    if taxname_file.endswith('.gz'):
        try:
            taxname_file_id = gzip.open(taxname_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', taxname_file)
    else:
        try:
            taxname_file_id = open(taxname_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', taxname_file)

    # read the first record
    record = taxname_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to the record counter
        record_counter += 1

        # extract the data
        # format: tax_id <field_sep> name_txt <field_sep> unique_name <field_sep> name_class <record_sep>
        field_sep = r'\|'
        record_sep = '\n'
        data_list = re.split(field_sep, record.replace(record_sep,''))
        try:
            tax_id = data_list[0].strip().strip('\t')
            name_txt = data_list[1].strip().strip('\t')
            name_class = data_list[3].strip().strip('\t')
        except Exception as e:
            raise xlib.ProgramException(e, 'F009', os.path.basename(taxname_file), record_counter)

        # add species data to the dictionary
        if name_class == 'scientific name':
            taxname_dict[tax_id] = name_txt

        xlib.Message.print('verbose', f'\rTaxonomy names records processed ... {record_counter:4d}')

        # read the next record
        record = taxname_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close taxonomy name file
    taxname_file_id.close()

    # return the taxonomy name dictionary
    return taxname_dict

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
