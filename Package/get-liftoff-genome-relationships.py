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
This program gets relationships between some genomes of related species using
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
import sys

import pandas as pd

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

    # get relationships between some genomes of related species using results of Liftoff processes
    get_liftoff_genome_relationships(conn, args.reference_species_id_list, args.target_species_id_list, args.common_mapped_gene_file, args.common_mapped_protein_coding_gene_file, args.common_mapped_protein_file)

    # close connection to SQLite database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'This program gets relationships between some genomes of related species using\n' \
        'results of Liftoff processes.' 
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--ref_sp_list', dest='reference_species_id_list', help='List of reference species identifications to be studied  with species_id_1,species_id_2,...,species_id_n (mandatory).')
    parser.add_argument('--tar_sp_list', dest='target_species_id_list', help='List of target identifications identifications to be studied  with species_id_1,species_id_2,...,species_id_n (mandatory).')
    parser.add_argument('--map_gene_file', dest='common_mapped_gene_file', help='Path of CSV file with common mapped genes (mandatory).')
    parser.add_argument('--map_codgene_file', dest='common_mapped_protein_coding_gene_file', help='Path of CSV file with common mapped protein-coding genes (mandatory).')
    parser.add_argument('--map_prot_file', dest='common_mapped_protein_file', help='Path of CSV file with common mapped proteins (mandatory).')
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

    # check "reference_species_id_list"
    if args.reference_species_id_list is None:
        xlib.Message.print('error', '*** The list of reference species identifications is not indicated in the input arguments.')
        OK = False
    else:
        args.reference_species_id_list = xlib.split_literal_to_text_list(args.reference_species_id_list)

    # check "target_species_id_list"
    if args.target_species_id_list is None:
        xlib.Message.print('error', '*** The list of target species identifications is not indicated in the input arguments.')
        OK = False
    else:
        args.target_species_id_list = xlib.split_literal_to_text_list(args.target_species_id_list)

    # check "common_mapped_gene_file"
    if args.common_mapped_gene_file is None:
        xlib.Message.print('error', '*** The output CSV file with common mapped genes is not indicated in the input arguments.')
        OK = False

    # check "common_mapped_protein_coding_gene_file"
    if args.common_mapped_protein_coding_gene_file is None:
        xlib.Message.print('error', '*** The output CSV file with common mapped protein-coding genes is not indicated in the input arguments.')
        OK = False

    # check "common_mapped_protein_file"
    if args.common_mapped_protein_file is None:
        xlib.Message.print('error', '*** The output CSV file with common mapped proteins is not indicated in the input arguments.')
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

def get_liftoff_genome_relationships(conn, reference_species_id_list, target_species_id_list, common_mapped_gene_file, common_mapped_protein_coding_gene_file, common_mapped_protein_file):
    '''
    Get relationships between some genomes of related species using results of Liftoff processes.
    '''

    # get the data list from the table "liftoff_gff_data" for the reference species identification list and target species identification list
    liftoff_gff_data_list = xsqlite.get_liftoff_gff_gene_data_list(conn, reference_species_id_list, target_species_id_list)

    # build the data dataframe
    liftoff_gff_data_df = pd.DataFrame(liftoff_gff_data_list)
    xlib.Message.print('info', f'liftoff_gff_data_df.info():\n{liftoff_gff_data_df.info()}')

    # open the file with common mapped genes
    if common_mapped_gene_file.endswith('.gz'):
        try:
            common_mapped_gene_file_id = gzip.open(common_mapped_gene_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', common_mapped_gene_file)
    else:
        try:
            common_mapped_gene_file_id = open(common_mapped_gene_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', common_mapped_gene_file)

    # write head record of file with common mapped genes
    common_mapped_gene_file_id.write('reference_species_id;reference_gene_id\n')

    # open the file with common mapped protein-coding genes
    if common_mapped_protein_coding_gene_file.endswith('.gz'):
        try:
            common_mapped_protein_coding_gene_file_id = gzip.open(common_mapped_protein_coding_gene_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', common_mapped_protein_coding_gene_file)
    else:
        try:
            common_mapped_protein_coding_gene_file_id = open(common_mapped_protein_coding_gene_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', common_mapped_protein_coding_gene_file)

    # write head record of file with common mapped protein-coding genes
    common_mapped_protein_coding_gene_file_id.write('reference_species_id;reference_gene_id\n')

    # open the file with common mapped proteins
    if common_mapped_protein_file.endswith('.gz'):
        try:
            common_mapped_protein_file_id = gzip.open(common_mapped_protein_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', common_mapped_protein_file)
    else:
        try:
            common_mapped_protein_file_id = open(common_mapped_protein_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', common_mapped_protein_file)

    # write head record of file with common mapped proteins
    common_mapped_protein_file_id.write('reference_species_id;reference_protein_id\n')

    # for every reference species identification
    for reference_species_id in reference_species_id_list:

        xlib.Message.print('info', f'reference_species_id: {reference_species_id}')

        # initialize the lists of protein and gene sets for target species
        gene_id_set_list = []
        protein_coding_gene_id_set_list = []
        protein_id_set_list = []

        # for every target species identification
        for target_species_id in target_species_id_list:

            # when the target species identification is not equal to reference species identification
            if target_species_id != reference_species_id:

                # build the dataframe with selected rows for the reference species identification and target species identification
                selected_gene_df = liftoff_gff_data_df[(liftoff_gff_data_df['reference_species_id'] == reference_species_id) & (liftoff_gff_data_df['target_species_id'] == target_species_id)]

                # get the set of gene identifications for the reference species identification and target species identification
                gene_id_set = set(selected_gene_df['reference_gene_id'])

                # add the set of gene identifications to the list of gene sets for target species
                gene_id_set_list.append(gene_id_set)

                # build the dataframe with selected rows for the reference species identification and target species identification and with protein identification
                selected_protein_df = liftoff_gff_data_df[(liftoff_gff_data_df['reference_species_id'] == reference_species_id) & (liftoff_gff_data_df['target_species_id'] == target_species_id) & (liftoff_gff_data_df['reference_protein_id_list'] != '')]

                # get the list of protein identifications for the reference species identification and target species identification
                protein_id_list = []
                protein_id_list_txt_list = selected_protein_df['reference_protein_id_list']
                for protein_id_list_txt in protein_id_list_txt_list:
                    protein_id_list.extend(protein_id_list_txt.split('|'))

                # get the set of protein identifications for the reference species identification and target species identification
                protein_id_set = set(protein_id_list)

                # add the set of protein idendentifications to the list of protein sets for target species
                protein_id_set_list.append(protein_id_set)

                # build the regex pattern to find the gene_id_set for selecting rows containing some of the protein identifications
                pattern = r'\b(?:' + '|'.join(map(repr, protein_id_set)).replace("'", "") + r')\b'

                # select rows containing some of gene_id_set in the selected protein dataframe
                reselected_protein_df = selected_protein_df[selected_protein_df['reference_protein_id_list'].str.contains(pattern)]

                # get the list of protein-coding gene identifications from the "reselected" protein dataframe
                protein_codig_gene_id_list = reselected_protein_df['reference_gene_id']

                # get the set of commod protein-codig gene identifications
                protein_coding_gene_id_set = set(protein_codig_gene_id_list)

                # add the set of protein-codig gene identifications to the list of protein_coding gene sets for target species
                protein_coding_gene_id_set_list.append(protein_coding_gene_id_set)

                xlib.Message.print('info', f'    target_species_id: {target_species_id} - len(gene_id_set): {len(gene_id_set)} - len(protein_coding_gene_id_set): {len(protein_coding_gene_id_set)} - len(protein_id_set): {len(protein_id_set)}')

        # get the intersection of the gene sets for target species
        gene_id_intersection_set = set.intersection(*gene_id_set_list)
        xlib.Message.print('info', f'    len(gene_id_intersection_set): {len(gene_id_intersection_set)}')

        # write detail records of file with the common mapped protein-coding genes
        for gene_id in gene_id_intersection_set:
            common_mapped_gene_file_id.write(f'{reference_species_id};{gene_id}\n')

        # get the intersection of the protein-coding gene sets for target species
        protein_coding_gene_id_intersection_set = set.intersection(*protein_coding_gene_id_set_list)
        xlib.Message.print('info', f'    len(protein_coding_gene_id_intersection_set): {len(protein_coding_gene_id_intersection_set)}')

        # write detail records of file with the common mapped protein-coding genes
        for protein_coding_gene_id in protein_coding_gene_id_intersection_set:
            common_mapped_protein_coding_gene_file_id.write(f'{reference_species_id};{protein_coding_gene_id}\n')

        # get the intersection of the protein sets for target species
        protein_id_intersection_set = set.intersection(*protein_id_set_list)
        xlib.Message.print('info', f'    len(protein_id_intersection_set): {len(protein_id_intersection_set)}')

        # write detail records of file with the common mapped proteins
        for protein_id in protein_id_intersection_set:
            common_mapped_protein_file_id.write(f'{reference_species_id};{protein_id}\n')

    # close files
    common_mapped_gene_file_id.close()
    common_mapped_protein_coding_gene_file_id.close()
    common_mapped_protein_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
