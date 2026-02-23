#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=unnecessary-pass

#-------------------------------------------------------------------------------

'''
This program loads data from a GFF file yielded by Liftoff into a SQLite database.

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

    # load data from a GFF file yielded by Liftoff into a SQLite database
    load_liftoff_gff_data(conn, args.reference_species_id, args.target_species_id, args.gff_gene_data_file, args.gff_cds_data_file, args.unmapped_gene_file)

    # close connection to SQLite database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads data from a GFF file yielded by Liftoff into a SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--rspecies', dest='reference_species_id', help='Reference species identification (mandatory).')
    parser.add_argument('--tspecies', dest='target_species_id', help='Target species identification (mandatory).')
    parser.add_argument('--gene-file', dest='gff_gene_data_file', help='Path of the CSV file with Liftoff GFF gene data (mandatory).')
    parser.add_argument('--cds-file', dest='gff_cds_data_file', help='Path of the CSV file with Liftoff GFF CDS data (mandatory).')
    parser.add_argument('--unmapped_file', dest='unmapped_gene_file', help='Path of the unmapped gene file yielded by Liftoff (mandatory).')
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
    elif not os.path.isfile(args.sqlite_database):
        xlib.Message.print('error', f'*** The file {args.sqlite_database} does not exist.')
        OK = False

    # check "reference_species_id"
    if args.reference_species_id is None:
        xlib.Message.print('error', '*** The reference species identification is not indicated in the input arguments.')
        OK = False

    # check "target_species_id"
    if args.reference_species_id is None:
        xlib.Message.print('error', '*** The target species identification is not indicated in the input arguments.')
        OK = False

    # check "gff_gene_data_file"
    if args.gff_gene_data_file is None:
        xlib.Message.print('error', '*** The CSV file with Liftoff GFF gene data is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.gff_gene_data_file):
        xlib.Message.print('error', f'*** The file {args.gff_gene_data_file} does not exist.')
        OK = False

    # check "gff_cds_data_file"
    if args.gff_cds_data_file is None:
        xlib.Message.print('error', '*** The CSV file with Liftoff GFF CDS data is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.gff_cds_data_file):
        xlib.Message.print('error', f'*** The file {args.gff_cds_data_file} does not exist.')
        OK = False

    # check "unmapped_gene_file"
    if args.unmapped_gene_file is None:
        xlib.Message.print('error', '*** The unmapped gene file yielded by Liftoff is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.unmapped_gene_file):
        xlib.Message.print('error', f'*** The file {args.unmapped_gene_file} does not exist.')
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

def load_liftoff_gff_data(conn, reference_species_id, target_species_id, gff_gene_data_file, gff_cds_data_file, unmapped_gene_file):
    '''
    Load data from a GFF file yielded by Liftoff into a SQLite database
    '''

    # check the table "liftoff_gff_gene_data"
    xlib.Message.print('verbose', 'Checking the table "liftoff_gff_gene_data" ...\n')
    liftoff_gff_gene_data_control = xsqlite.check_liftoff_gff_gene_data(conn)
    xlib.Message.print('verbose', f'Control: {liftoff_gff_gene_data_control}.\n')

    # when the table "liftoff_gff_gene_data" has rows
    if liftoff_gff_gene_data_control == 1:
        xlib.Message.print('verbose', f'Deleting rows from the table "liftoff_gff_gene_data" coresponding to {reference_species_id}-{target_species_id} ...\n')
        xsqlite.delete_liftoff_gff_gene_data_rows(conn, reference_species_id, target_species_id)
        xlib.Message.print('verbose', 'Rows are deleted.\n')

    # where there are not rows
    else:
        xlib.Message.print('verbose', 'Dropping the table "liftoff_gff_gene_data" ...\n')
        xsqlite.drop_liftoff_gff_gene_data(conn)
        xlib.Message.print('verbose', 'The table is dropped.\n')
        xlib.Message.print('verbose', 'Creating the table "liftoff_gff_gene_data" ...\n')
        xsqlite.create_liftoff_gff_gene_data(conn)
        xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the record counter of the file with Liftoff GFF gene data
    gff_gene_data_file_record_counter = 0

    # initialize the inserted row counter of the file with Liftoff GFF gene data
    gff_gene_data_file_inserted_row_counter = 0

    # initialize the header record control of the file with Liftoff GFF gene data
    gff_gene_data_file_header_record = True

    # open the file with Liftoff GFF gene data
    if gff_gene_data_file.endswith('.gz'):
        try:
            gff_gene_data_file_id = gzip.open(gff_gene_data_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', gff_gene_data_file)
    else:
        try:
            gff_gene_data_file_id = open(gff_gene_data_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', gff_gene_data_file)

    # read the first record of the file with Liftoff GFF gene data
    gff_gene_data_file_record = gff_gene_data_file_id.readline()

    # while there are records in the file with Liftoff GFF gene data
    while gff_gene_data_file_record != '':

        # add 1 to record counter of the file with Liftoff GFF gene data
        gff_gene_data_file_record_counter += 1

        # initialize the row data dictionary of the file with Liftoff GFF gene data
        gff_gene_data_file_row_dict = {}

        # process the header record of the file with Liftoff GFF gene data
        if gff_gene_data_file_header_record:
            gff_gene_data_file_header_record = False

        # process data records of the file with Liftoff GFF gene data
        else:

            # extract data
            # record format: reference_species_id <field_sep> target_species_id <field_sep> reference_gene_id <field_sep> target_seq_id <field_sep> target_start <field_sep> target_end <field_sep> target_strand <field_sep> reference_protein_id_list <record_sep>
            field_sep = ';'
            record_sep = '\n'
            data_list = re.split(field_sep, gff_gene_data_file_record.replace(record_sep,''))
            try:
                gff_gene_data_file_row_dict['reference_species_id'] = data_list[0].strip()
                gff_gene_data_file_row_dict['target_species_id'] = data_list[1].strip()
                gff_gene_data_file_row_dict['reference_gene_id'] = data_list[2].strip()
                gff_gene_data_file_row_dict['target_seq_id'] = data_list[3].strip()
                gff_gene_data_file_row_dict['target_start'] = int(data_list[4].strip())
                gff_gene_data_file_row_dict['target_end'] = int(data_list[5].strip())
                gff_gene_data_file_row_dict['target_strand'] = data_list[6].strip()
                gff_gene_data_file_row_dict['reference_protein_id_list'] = data_list[7].strip()
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(gff_gene_data_file), gff_gene_data_file_record_counter)

            # insert data into the table "liftoff_gff_gene_data"
            xsqlite.insert_liftoff_gff_gene_data_row(conn, gff_gene_data_file_row_dict)
            gff_gene_data_file_inserted_row_counter += 1

            # print counters
            xlib.Message.print('verbose', f'\rgff_gene_data_file: {gff_gene_data_file_record_counter} processed records - Inserted rows: {gff_gene_data_file_inserted_row_counter}')

        # read the next record of the file with Liftoff GFF gene data
        gff_gene_data_file_record = gff_gene_data_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # create the index "liftoff_gff_gene_data_index_1" on the table "liftoff_gff_gene_data" if it is new
    if liftoff_gff_gene_data_control == 0:
        xlib.Message.print('verbose', 'Creating the index_1 on the table "liftoff_gff_gene_data" ...\n')
        xsqlite.create_liftoff_gff_gene_data_index_1(conn)
        xlib.Message.print('verbose', 'The index is created.\n')

    # create the index "liftoff_gff_gene_data_index_2" on the table "liftoff_gff_gene_data" if it is new
    if liftoff_gff_gene_data_control == 0:
        xlib.Message.print('verbose', 'Creating the index_2 on the table "liftoff_gff_gene_data" ...\n')
        xsqlite.create_liftoff_gff_gene_data_index_2(conn)
        xlib.Message.print('verbose', 'The index is created.\n')

    # close file with Liftoff GFF gene data
    gff_gene_data_file_id.close()

    # check the table "liftoff_gff_cds_data"
    xlib.Message.print('verbose', 'Checking the table "liftoff_gff_cds_data" ...\n')
    liftoff_gff_cds_data_control = xsqlite.check_liftoff_gff_cds_data(conn)
    xlib.Message.print('verbose', f'Control: {liftoff_gff_cds_data_control}.\n')

    # when the table "liftoff_gff_cds_data" has rows
    if liftoff_gff_cds_data_control == 1:
        xlib.Message.print('verbose', f'Deleting rows from the table "liftoff_gff_cds_data" coresponding to {reference_species_id}-{target_species_id} ...\n')
        xsqlite.delete_liftoff_gff_cds_data_rows(conn, reference_species_id, target_species_id)
        xlib.Message.print('verbose', 'Rows are deleted.\n')

    # where there are not rows
    else:
        xlib.Message.print('verbose', 'Dropping the table "liftoff_gff_cds_data" ...\n')
        xsqlite.drop_liftoff_gff_cds_data(conn)
        xlib.Message.print('verbose', 'The table is dropped.\n')
        xlib.Message.print('verbose', 'Creating the table "liftoff_gff_cds_data" ...\n')
        xsqlite.create_liftoff_gff_cds_data(conn)
        xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the record counter of the file with Liftoff GFF CDS data
    gff_cds_data_file_record_counter = 0

    # initialize the inserted row counter of the file with Liftoff GFF CDS data
    gff_cds_data_file_inserted_row_counter = 0

    # initialize the header record control of the file with Liftoff GFF CDS data
    gff_cds_data_file_header_record = True

    # open the file with Liftoff GFF CDS data
    if gff_cds_data_file.endswith('.gz'):
        try:
            gff_cds_data_file_id = gzip.open(gff_cds_data_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', gff_cds_data_file)
    else:
        try:
            gff_cds_data_file_id = open(gff_cds_data_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', gff_cds_data_file)

    # read the first record of the file with Liftoff GFF CDS data
    gff_cds_data_file_record = gff_cds_data_file_id.readline()

    # while there are records in the file with Liftoff GFF CDS data
    while gff_cds_data_file_record != '':

        # add 1 to record counter of the file with Liftoff GFF CDS data
        gff_cds_data_file_record_counter += 1

        # initialize the row data dictionary of the file with Liftoff GFF CDS data
        gff_cds_data_file_row_dict = {}

        # process the header record of the file with Liftoff GFF CDS data
        if gff_cds_data_file_header_record:
            gff_cds_data_file_header_record = False

        # process data records of the file with Liftoff GFF CDS data
        else:

            # extract data
            # record format: reference_species_id <field_sep> target_species_id <field_sep> reference_protein_id <field_sep> target_seq_id <field_sep> target_start <field_sep> target_end <field_sep> target_strand <record_sep>
            field_sep = ';'
            record_sep = '\n'
            data_list = re.split(field_sep, gff_cds_data_file_record.replace(record_sep,''))
            try:
                gff_cds_data_file_row_dict['reference_species_id'] = data_list[0].strip()
                gff_cds_data_file_row_dict['target_species_id'] = data_list[1].strip()
                gff_cds_data_file_row_dict['reference_protein_id'] = data_list[2].strip()
                gff_cds_data_file_row_dict['target_seq_id'] = data_list[3].strip()
                gff_cds_data_file_row_dict['target_start'] = int(data_list[4].strip())
                gff_cds_data_file_row_dict['target_end'] = int(data_list[5].strip())
                gff_cds_data_file_row_dict['target_strand'] = data_list[6].strip()
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(gff_cds_data_file), gff_cds_data_file_record_counter)

            # insert data into the table "liftoff_gff_cds_data"
            xsqlite.insert_liftoff_gff_cds_data_row(conn, gff_cds_data_file_row_dict)
            gff_cds_data_file_inserted_row_counter += 1

            # print counters
            xlib.Message.print('verbose', f'\rgff_cds_data_file: {gff_cds_data_file_record_counter} processed records - Inserted rows: {gff_cds_data_file_inserted_row_counter}')

        # read the next record of the file with Liftoff GFF CDS data
        gff_cds_data_file_record = gff_cds_data_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # create the index "liftoff_gff_cds_data_index_1" on the table "liftoff_gff_cds_data" if it is new
    if liftoff_gff_cds_data_control == 0:
        xlib.Message.print('verbose', 'Creating the index_1 on the table "liftoff_gff_cds_data" ...\n')
        xsqlite.create_liftoff_gff_cds_data_index_1(conn)
        xlib.Message.print('verbose', 'The index is created.\n')

    # create the index "liftoff_gff_cds_data_index_2" on the table "liftoff_gff_cds_data" if it is new
    if liftoff_gff_cds_data_control == 0:
        xlib.Message.print('verbose', 'Creating the index_2 on the table "liftoff_gff_cds_data" ...\n')
        xsqlite.create_liftoff_gff_cds_data_index_2(conn)
        xlib.Message.print('verbose', 'The index is created.\n')

    # close file with Liftoff GFF CDS data
    gff_cds_data_file_id.close()

    # check the table "liftoff_unmapped_genes"
    xlib.Message.print('verbose', 'Checking the table "liftoff_unmapped_genes" ...\n')
    liftoff_unmapped_genes_control = xsqlite.check_liftoff_unmapped_genes(conn)
    xlib.Message.print('verbose', f'Control: {liftoff_unmapped_genes_control}.\n')

    # when the table "liftoff_unmapped_genes" has rows
    if liftoff_unmapped_genes_control == 1:
        xlib.Message.print('verbose', f'Deleting rows from the table "liftoff_unmapped_genes" coresponding to {reference_species_id}-{target_species_id} ...\n')
        xsqlite.delete_liftoff_unmapped_genes_rows(conn, reference_species_id, target_species_id)
        xlib.Message.print('verbose', 'Rows are deleted.\n')

    # where there are not rows
    else:
        xlib.Message.print('verbose', 'Dropping the table "liftoff_unmapped_genes" ...\n')
        xsqlite.drop_liftoff_unmapped_genes(conn)
        xlib.Message.print('verbose', 'The table is dropped.\n')
        xlib.Message.print('verbose', 'Creating the table "liftoff_unmapped_genes" ...\n')
        xsqlite.create_liftoff_unmapped_genes(conn)
        xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the record counter of the unmapped gene file
    unmapped_gene_file_record_counter = 0

    # initialize the inserted row counter of the unmapped gene file
    unmapped_gene_file_inserted_row_counter = 0

    # open the unmapped gene file
    if unmapped_gene_file.endswith('.gz'):
        try:
            unmapped_gene_file_id = gzip.open(unmapped_gene_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', unmapped_gene_file)
    else:
        try:
            unmapped_gene_file_id = open(unmapped_gene_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', unmapped_gene_file)

    # read the first record of the unmapped gene file
    unmapped_gene_file_record = unmapped_gene_file_id.readline()

    # while there are records in the unmapped gene file
    while unmapped_gene_file_record != '':

        # add 1 to record counter of the unmapped gene file
        unmapped_gene_file_record_counter += 1

        # initialize the row data dictionary of the unmapped gene file
        unmapped_gene_file_row_dict = {}

        # extract data
        # record format: reference_species_id <field_sep> target_species_id <field_sep> reference_gene_id <record_sep>
        field_sep = ';'
        record_sep = '\n'
        data_list = re.split(field_sep, unmapped_gene_file_record.replace(record_sep,''))
        try:
            unmapped_gene_file_row_dict['reference_species_id'] = reference_species_id
            unmapped_gene_file_row_dict['target_species_id'] = target_species_id
            unmapped_gene_file_row_dict['reference_gene_id'] = data_list[0].strip()
        except Exception as e:
            raise xlib.ProgramException(e, 'F009', os.path.basename(unmapped_gene_file), unmapped_gene_file_record_counter)

        # insert data into the table "liftoff_unmapped_genes"
        xsqlite.insert_liftoff_unmapped_genes_row(conn, unmapped_gene_file_row_dict)
        unmapped_gene_file_inserted_row_counter += 1

        # print counters
        xlib.Message.print('verbose', f'\runmapped_gene_file: {unmapped_gene_file_record_counter} processed records - Inserted rows: {unmapped_gene_file_inserted_row_counter}')

        # read the next record of the unmapped gene file
        unmapped_gene_file_record = unmapped_gene_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # create the index "liftoff_unmapped_genes_index_1" on the table "liftoff_unmapped_genes" if it is new
    if liftoff_unmapped_genes_control == 0:
        xlib.Message.print('verbose', 'Creating the index_1 on the table "liftoff_unmapped_genes" ...\n')
        xsqlite.create_liftoff_unmapped_genes_index_1(conn)
        xlib.Message.print('verbose', 'The index is created.\n')

    # create the index "liftoff_unmapped_genes_index_2" on the table "liftoff_unmapped_genes" if it is new
    if liftoff_unmapped_genes_control == 0:
        xlib.Message.print('verbose', 'Creating the index_2 on the table "liftoff_unmapped_genes" ...\n')
        xsqlite.create_liftoff_unmapped_genes_index_2(conn)
        xlib.Message.print('verbose', 'The index is created.\n')

    # close unmapped gene file
    unmapped_gene_file_id.close()

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into the SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
