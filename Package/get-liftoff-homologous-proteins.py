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
This program gets homologous proteins between a reference and target species using
results of Liftoff processes.

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

    # get homologous proteins between a reference and target species using results of Liftoff processes
    get_liftoff_homologous_proteins(conn, args.reference_species_id, args.target_species_id, args.common_mapped_proteins_file, args.threshold, args.tpi_list)

    # close connection to SQLite database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'This program gets homologous proteins between a reference and target species using\n' \
        'results of Liftoff processes.' 
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--ref_sp', dest='reference_species_id', help='Reference species identification (mandatory).')
    parser.add_argument('--tar_sp', dest='target_species_id', help='Target species identification (mandatory).')
    parser.add_argument('--map_prot_file', dest='common_mapped_proteins_file', help='Path of CSV file with common mapped proteins (mandatory).')
    parser.add_argument('--threshold', dest='threshold', help='Start position decrease and end position increase in the items search of GFF file items (mandatory).')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')
    parser.add_argument('--tpi', dest='tpi_list', help='Reference protein identification list to trace with format protein_id,protein_id_2,...,protein_id_n or NONE; default: NONE.')

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
    if args.target_species_id is None:
        xlib.Message.print('error', '*** The target species identification is not indicated in the input arguments.')
        OK = False

    # check "common_mapped_proteins_file"
    if args.common_mapped_proteins_file is None:
        xlib.Message.print('error', '*** The input CSV file with common mapped proteins is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.common_mapped_proteins_file):
        xlib.Message.print('error', f'*** The file {args.common_mapped_proteins_file} does not exist.')
        OK = False

    # check "threshold"
    if args.threshold is None:
        xlib.Message.print('error', '*** The threshold is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.threshold, minimum=0):
        xlib.Message.print('error', 'The threshold has to be a integer number greater than or equal to 0.')
        OK = False
    else:
        args.threshold = int(args.threshold)

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

    # check "tpi_list"
    if args.tpi_list is None or args.tpi_list == 'NONE':
        args.tpi_list = []
    else:
        args.tpi_list = xlib.split_literal_to_text_list(args.tpi_list)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def get_liftoff_homologous_proteins(conn, reference_species_id, target_species_id, common_mapped_proteins_file, threshold, tpi_list):
    '''
    Get get homologous proteins between a reference and target species using results of Liftoff processes.
    '''

    # check the table "liftoff_homologous_proteins"
    xlib.Message.print('verbose', 'Checking the table "liftoff_homologous_proteins" ...\n')
    liftoff_homologous_proteins_control = xsqlite.check_liftoff_homologous_proteins(conn)
    xlib.Message.print('verbose', f'Control: {liftoff_homologous_proteins_control}.\n')

    # when the table "liftoff_homologous_proteins" has rows
    if liftoff_homologous_proteins_control == 1:
        xlib.Message.print('verbose', f'Deleting rows from the table "liftoff_homologous_proteins" coresponding to {reference_species_id}-{target_species_id} ...\n')
        xsqlite.delete_liftoff_homologous_proteins_rows(conn, reference_species_id, target_species_id)
        xlib.Message.print('verbose', 'Rows are deleted.\n')

    # where there are not rows
    else:
        xlib.Message.print('verbose', 'Dropping the table "liftoff_homologous_proteins" ...\n')
        xsqlite.drop_liftoff_homologous_proteins(conn)
        xlib.Message.print('verbose', 'The table is dropped.\n')
        xlib.Message.print('verbose', 'Creating the table "liftoff_homologous_proteins" ...\n')
        xsqlite.create_liftoff_homologous_proteins(conn)
        xlib.Message.print('verbose', 'The table is created.\n')

    # open the file with common mapped proteins
    if common_mapped_proteins_file.endswith('.gz'):
        try:
            common_mapped_proteins_file_id = gzip.open(common_mapped_proteins_file, mode='rt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', common_mapped_proteins_file)
    else:
        try:
            common_mapped_proteins_file_id = open(common_mapped_proteins_file, mode='r', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', common_mapped_proteins_file)

    # read the first record of the file with common mapped proteins
    record = common_mapped_proteins_file_id.readline()

    # set the first record control variable
    first_record = True

    # while there are records in file with common mapped proteins
    while record != '':

        # the header record
        if first_record:

            # set the first record control variable
            first_record = False

        # data records
        else:

            # extract data
            # record format: reference_species_id <field_sep> reference_protein_id <record_sep>
            field_sep = ';'
            record_sep = '\n'
            data_list = re.split(field_sep, record.replace(record_sep,''))
            record_reference_species_id = data_list[0].strip()
            reference_protein_id = data_list[1].strip()

            # when the record reference species identification is the parameter reference species identification
            if record_reference_species_id == reference_species_id:

                if reference_protein_id in tpi_list: xlib.Message.print('trace', '-' * 40)
                if reference_protein_id in tpi_list: xlib.Message.print('trace', f'reference_protein_id: {reference_protein_id}')


                # get the CDS data of the target species corresponding to the reference protein identification from the Liftoff database
                liftoff_protein_cds_data_list = xsqlite.get_liftoff_protein_cds_data_list_1(conn, reference_species_id, target_species_id, reference_protein_id)
                if reference_protein_id in tpi_list: print(f'liftoff_protein_cds_data_list:\n{liftoff_protein_cds_data_list}')

                # set parameters to find CDS CDS data the target species corresponding from the SQLite database of GFF data
                target_seq_id = liftoff_protein_cds_data_list[0]['target_seq_id']
                target_strand = liftoff_protein_cds_data_list[0]['target_strand']
                target_start = sys.maxsize
                target_end = 0
                for protein_cds_data in liftoff_protein_cds_data_list:
                    if protein_cds_data['target_start'] < target_start:
                        target_start = protein_cds_data['target_start']
                    if protein_cds_data['target_end'] > target_end:
                        target_end = protein_cds_data['target_end']

                # get the CDS data the target species corresponding from the SQLite database of GFF data
                gff_protein_cds_data_list = xsqlite.get_liftoff_protein_cds_data_list_2(conn, target_species_id, 'NA', target_seq_id, (target_start - threshold), (target_end + threshold), target_strand)
                if reference_protein_id in tpi_list: xlib.Message.print('trace', f'gff_protein_cds_data_list:\n{gff_protein_cds_data_list}')

                # get the homologous protein list
                homologous_protein_id_set = set()
                for gff_protein_cds_data_list in gff_protein_cds_data_list:
                    homologous_protein_id_set.add(gff_protein_cds_data_list['reference_protein_id'])

                # insert data
                for hologogous_protein_id in homologous_protein_id_set:
                    row_dict = {'reference_species_id': reference_species_id, 'target_species_id': target_species_id, 'reference_protein_id': reference_protein_id, 'target_protein_id': hologogous_protein_id}
                    xsqlite.insert_liftoff_homologous_proteins_row(conn, row_dict)

        # read the next record of the file with common mapped proteins
        record = common_mapped_proteins_file_id.readline()

    if reference_protein_id in tpi_list: xlib.Message.print('trace', '-' * 40)

    # create the index "liftoff_homologous_proteins_index_1" on the table "liftoff_homologous_proteins" if it is new
    if liftoff_homologous_proteins_control == 0:
        xlib.Message.print('verbose', 'Creating the index_1 on the table "liftoff_homologous_proteins" ...\n')
        xsqlite.create_liftoff_homologous_proteins_index_1(conn)
        xlib.Message.print('verbose', 'The index is created.\n')

    # create the "liftoff_homologous_proteins_index_2" on the table "liftoff_homologous_proteins" if it is new
    if liftoff_homologous_proteins_control == 0:
        xlib.Message.print('verbose', 'Creating the index_2 on the table "liftoff_homologous_proteins" ...\n')
        xsqlite.create_liftoff_homologous_proteins_index_2(conn)
        xlib.Message.print('verbose', 'The index is created.\n')

    # close the file with common mapped proteins
    common_mapped_proteins_file_id.close()

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into the SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
