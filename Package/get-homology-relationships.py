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
This program gets relationships of proteins and protein-coding genes of a reference species
with their homologous proteins and protein-coding genes of other species related yielded by
a Liftoff process.

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

    # get relationships of proteins of a reference species and their homologous proteins of other species
    get_liftoff_homologous_proteins(conn, args.reference_species_id, args.target_species_ids_list, args.homology_relationships_file, args.tpi_list)

    # close connection to SQLite database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'This program gets relationships of proteins and protein-coding genes of a reference species with\n' \
        'their homologous proteins and protein-coding genes of other species related yielded by a Liftoff process.' 
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--ref_sp', dest='reference_species_id', help='Reference species identification (mandatory).')
    parser.add_argument('--tar_sp_list', dest='target_species_ids_list', help='List of target identifications identifications to be studied  with species_id_1,species_id_2,...,species_id_n (mandatory).')
    parser.add_argument('--homology_file', dest='homology_relationships_file', help='Path of CSV file with relationships of homologous proteins and protein-coding genes (mandatory).')
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

    # check "target_species_ids_list"
    if args.target_species_ids_list is None:
        xlib.Message.print('error', '*** The list of target species identifications is not indicated in the input arguments.')
        OK = False
    else:
        args.target_species_ids_list = xlib.split_literal_to_text_list(args.target_species_ids_list)

    # check "homology_relationships_file"
    if args.homology_relationships_file is None:
        xlib.Message.print('error', '*** The CSV file with relationships of homologous proteins and protein-coding genes is not indicated in the input arguments.')
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

    # check "tpi_list"
    if args.tpi_list is None or args.tpi_list == 'NONE':
        args.tpi_list = []
    else:
        args.tpi_list = xlib.split_literal_to_text_list(args.tpi_list)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def get_liftoff_homologous_proteins(conn, reference_species_id, target_species_ids_list, homologous_relationships_file, tpi_list):
    '''
    Get relationships of proteins of a reference species and their homologous proteins of other species.
    '''

    # build the all species list including the reference and target species
    all_species_ids_set = set(target_species_ids_list)
    all_species_ids_set.add(reference_species_id)
    all_species_ids_list = sorted(list(all_species_ids_set))

    # get the dictionary of the cluster identifications of concatenated CDS corresponding to the reference species
    mmseqs2_concatenated_cds_clusters_dict = xsqlite.get_mmseqs2_concatenated_cds_clusters_dict(conn, reference_species_id)

    # get the dictionary with genes corresponding to proteins
    protein_per_genes_dict = xsqlite.get_protein_per_genes_dict(conn)

    # build the list of paralogous proteins of reference species
    # initialize the diccionary of the paralogous proteins groups of reference species and paralogus proteins group
    reference_species_paralogous_proteins_groups_list = []
    paralogous_proteins_list = []

    # initialize the previous gene and cluster identifications list
    old_gene_id = ''
    cluster_ids_list = []

    # for each item of the dictionary with genes corresponding to proteins, build a list of groups of paralogous proteins of the reference species
    for key in  sorted(mmseqs2_concatenated_cds_clusters_dict.keys()):
        if old_gene_id != '' and mmseqs2_concatenated_cds_clusters_dict[key]['gene_id'] != old_gene_id:
            reference_species_paralogous_proteins_groups_list.append(sorted(paralogous_proteins_list))
            paralogous_proteins_list = []
            old_gene_id = ''
            cluster_ids_list = []
        if mmseqs2_concatenated_cds_clusters_dict[key]['cluster_id'] not in cluster_ids_list:
            paralogous_proteins_list.append(mmseqs2_concatenated_cds_clusters_dict[key]['protein_id'])
            cluster_ids_list.append(mmseqs2_concatenated_cds_clusters_dict[key]['cluster_id'])
        old_gene_id = mmseqs2_concatenated_cds_clusters_dict[key]['gene_id']
    if paralogous_proteins_list:
        reference_species_paralogous_proteins_groups_list.append(paralogous_proteins_list)

    # sort the list of paralogous proteins groups of reference species
    reference_species_paralogous_proteins_groups_list = sorted(reference_species_paralogous_proteins_groups_list, key=lambda x: x[0])

    # build the dictionary of homology relationships
    homology_relationships_dict = xlib.NestedDefaultDict()
    # each group of paralogous proteins of the reference species
    for reference_paralogous_proteins_group_list in reference_species_paralogous_proteins_groups_list:

        # set a text with the items of paralogous proteins corresponding to the reference species joined by a "|"
        reference_paralogous_proteins_group_list_text = '|'.join(reference_paralogous_proteins_group_list)

        # add reference paraogous proteins to the dictionary of homology relationships
        homology_relationships_dict[reference_paralogous_proteins_group_list_text][reference_species_id]['proteins'] = reference_paralogous_proteins_group_list

        # build a set with the items of protein coding genes corresponding to the reference species
        reference_paralogous_protein_coding_genes_set = set()
        for reference_paralogous_protein in reference_paralogous_proteins_group_list:
            reference_paralogous_protein_coding_genes_set.add(protein_per_genes_dict[f'{reference_species_id}-{reference_paralogous_protein}'])

        # add reference protein-coding genes to the dictionary of homology relationships
        homology_relationships_dict[reference_paralogous_proteins_group_list_text][reference_species_id]['coding_genes'] = list(reference_paralogous_protein_coding_genes_set)

        # get the list of target orthologous proteins corresponding to a list of reference protein
        liftoff_orthologous_proteins_list = xsqlite.get_liftoff_homologous_proteins_list(conn, reference_paralogous_proteins_group_list)

        # for each protein of the list of target orthologous proteins
        for liftoff_orthologous_protein in liftoff_orthologous_proteins_list:

            # add the protein to the orthologous protein list corresponding to target species in the diccionary of proteins relationships
            species_orthologous_proteins_set = set(homology_relationships_dict.get(reference_paralogous_proteins_group_list_text, {}).get(liftoff_orthologous_protein['target_species_id'], {}).get('proteins', []))
            species_orthologous_proteins_set.add(liftoff_orthologous_protein['target_protein_id'])
            homology_relationships_dict[reference_paralogous_proteins_group_list_text][liftoff_orthologous_protein['target_species_id']]['proteins'] = list(species_orthologous_proteins_set)

            # add genes of orthologous proteins list corresponding to target species in the diccionary of protein coding genes relationships
            species_orthologous_protein_coding_genes_set = set()
            for species_orthologous_protein in species_orthologous_proteins_set:
                species_orthologous_protein_coding_genes_set.add(protein_per_genes_dict[f'{liftoff_orthologous_protein['target_species_id']}-{species_orthologous_protein}'])
            homology_relationships_dict[reference_paralogous_proteins_group_list_text][liftoff_orthologous_protein['target_species_id']]['coding_genes'] = list(species_orthologous_protein_coding_genes_set)

    # open the file with relationships of homologous proteins and protein-coding genes
    if homologous_relationships_file.endswith('.gz'):
        try:
            homology_relationships_file_id = gzip.open(homologous_relationships_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', homologous_relationships_file)
    else:
        try:
            homology_relationships_file_id = open(homologous_relationships_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', homologous_relationships_file)

    # write the header of the file with relationships of homologous proteins and protein-coding genes
    header_text = ''
    for species_id in all_species_ids_list:
        header_text = f'{header_text}{species_id} prots;{species_id} codgenes;'
    homology_relationships_file_id.write(f'{header_text[:-1]}\n')

    # write records with proteins and protein-coding genes relationships
    for reference_paralogous_proteins_group_list_text in sorted(homology_relationships_dict.keys()):

        # build the record text corresponding to the paralogous proteins and protein-coding genes of the group of the reference species
        record_text = ''
        for species_id in all_species_ids_list:
            protein_list_text = '|'.join(sorted(homology_relationships_dict[reference_paralogous_proteins_group_list_text][species_id]['proteins']))
            protein_coding_genes_list_text = '|'.join(sorted(homology_relationships_dict[reference_paralogous_proteins_group_list_text][species_id]['coding_genes']))
            record_text = f'{record_text}{protein_list_text};{protein_coding_genes_list_text};'

        # write the record
        homology_relationships_file_id.write(f'{record_text[:-1]}\n')

    # close the file with relationships of homologous proteins and protein-coding genes
    homology_relationships_file_id.close()

    # print OK message
    xlib.Message.print('info', 'The file with relationships of homologous proteins and protein-coding genes is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
