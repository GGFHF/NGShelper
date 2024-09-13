#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program lists data of variants and alleles and variant identifications to the scenario X.

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

    # get the SQLite database name
    file_name, _ = os.path.splitext(os.path.basename(args.sqlite_database))

    # list data of variants and alleles and variant identifications to the scenario X
    query_data(conn, file_name, args.sp1_id, args.sp2_id, args.hybrid_id, args.imputed_md_id, args.max_separation, args.output_dir, args.tsi_list)

    # close connection to TOA database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program lists data of variants and alleles and variant identifications to the scenario X.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species (mandatory).')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--imd_id', dest='imputed_md_id', help=f'Identification of the alternative allele for imputed missing data; default {xlib.Const.DEFAULT_IMPUTED_MD_ID}')
    parser.add_argument('--maxsep', dest='max_separation', help='Maximum separation between variants of the same intergenic fragment (mandatory).')
    parser.add_argument('--outdir', dest='output_dir', help='Path of output directoty where files with allele data about scenario X are saved (mandatory).')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')
    parser.add_argument('--tsi', dest='tsi_list', help='Sequence identification list to trace with format seq_id,seq_id_2,...,seq_id_n or NONE; default: NONE.')

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

    # check "sp1_id"
    if args.sp1_id is None:
        xlib.Message.print('error', '*** The identification of the first species is not indicated in the input arguments.')
        OK = False

    # check "sp2_id"
    if args.sp2_id is None:
        xlib.Message.print('error', '*** The identification of the second species is not indicated in the input arguments.')
        OK = False

    # check "hybrid_id"
    if args.hybrid_id is None:
        args.hybrid_id = 'NONE'

    # check "max_separation"
    if args.max_separation is None:
        xlib.Message.print('error', '*** The maximum separation between variants of the same intergenic fragment is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.max_separation, minimum=1):
        xlib.Message.print('error', 'The maximum separation between variants of the same intergenic fragment has to be a integer number greater than 1.')
        OK = False
    else: 
        args.max_separation = int(args.max_separation)

    # check "output_dir"
    if args.output_dir is None:
        xlib.Message.print('error', '*** The output directy is not indicated in the input arguments.')
        OK = False
    elif not os.path.isdir(args.output_dir):
        xlib.Message.print('error', '*** The output directy does not exist.')
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

    # check "tsi_list"
    if args.tsi_list is None or args.tsi_list == 'NONE':
        args.tsi_list = []
    else:
        args.tsi_list = xlib.split_literal_to_string_list(args.tsi_list)

    # check the identification set
    if OK:
        if args.sp1_id == args.sp2_id or (args.sp1_id == args.hybrid_id or args.sp2_id == args.hybrid_id):
            xlib.Message.print('error', 'The identifications must be different.')
            OK = False

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def query_data(conn, file_name, sp1_id, sp2_id, hybrid_id, imputed_md_id, max_separation, output_dir, tsi_list):
    '''
    List data of variants and alleles and variant identifications to the scenario X.
    '''

    # check if the table "gene_info" is loaded
    xlib.Message.print('verbose', 'Checking the table "gene_info" ...\n')
    if xsqlite.check_gene_info(conn) == 0:
        raise xlib.ProgramException('', 'B003', 'gene_info')
    xlib.Message.print('verbose', 'The table is loaded.\n')

    # check if the table "genomic_features" is loaded
    xlib.Message.print('verbose', 'Checking the table "genomic_features" ...\n')
    if xsqlite.check_genomic_features(conn) == 0:
        raise xlib.ProgramException('', 'B003', 'genomic_features')
    xlib.Message.print('verbose', 'The table is loaded.\n')

    # check if the table "vcf_samples" is loaded
    xlib.Message.print('verbose', 'Checking the table "vcf_samples" ...\n')
    if xsqlite.check_vcf_samples(conn) == 0:
        raise xlib.ProgramException('', 'B003', 'vcf_samples')
    xlib.Message.print('verbose', 'The table is loaded.\n')

    # check if the table "vcf_variants" is loaded
    xlib.Message.print('verbose', 'Checking the table "vcf_variants" ...\n')
    if xsqlite.check_vcf_variants(conn) == 0:
        raise xlib.ProgramException('', 'B003', 'vcf_variants')
    xlib.Message.print('verbose', 'The table is loaded.\n')

    # check if the table "vcf_alleles" is loaded
    xlib.Message.print('verbose', 'Checking the table "vcf_alleles" ...\n')
    if xsqlite.check_vcf_alleles(conn) == 0:
        raise xlib.ProgramException('', 'B003', 'vcf_alleles')
    xlib.Message.print('verbose', 'The table is loaded.\n')

    # check if the table "vcf_samples_alleles" is loaded
    xlib.Message.print('verbose', 'Checking the table "vcf_samples_alleles" ...\n')
    if xsqlite.check_vcf_samples_alleles(conn) == 0:
        raise xlib.ProgramException('', 'B003', 'vcf_samples_alleles')
    xlib.Message.print('verbose', 'The table is loaded.\n')

    # get the variant dictionary
    xlib.Message.print('verbose', 'Getting variant data ...\n')
    variant_dict = xsqlite.query_variants(conn)
    xlib.Message.print('verbose', 'Data are got.\n')

    # get the allele dictionary
    xlib.Message.print('verbose', 'Getting allele data ...\n')
    allele_dict = xsqlite.get_vcf_allele_dict(conn)
    xlib.Message.print('verbose', 'Data are got.\n')

    # get the imputated allele dictionary
    xlib.Message.print('verbose', 'Getting imputated allele data ...\n')
    imputed_allele_dict = xsqlite.query_imputed_alleles(conn, imputed_md_id)
    xlib.Message.print('verbose', 'Data are got.\n')

    # get the dictionary of allele frecuency per species
    xlib.Message.print('verbose', 'Getting the dictionary of allele frecuency per species ...\n')
    species_allele_frequency_dict = xsqlite.query_species_allele_frequencies(conn, xlib.get_md_symbol())
    xlib.Message.print('verbose', 'Data are got.\n')

    # get the dictionary of allele frecuency per species
    xlib.Message.print('verbose', 'Getting the dictionary of allele frecuency per species and type ...\n')
    species_and_type_allele_frequency_dict = xsqlite.query_species_and_type_allele_frequencies(conn, xlib.get_md_symbol())
    xlib.Message.print('verbose', 'Data are got.\n')

    #-------------------------------------------------------------------------------
    # build the intergenic variant dictionary
    #-------------------------------------------------------------------------------

    xlib.Message.print('verbose', 'Building the intergenic variant dictionary ...\n')

    # initialize intergenic variant dictionary
    intergenic_variant_dict = xlib.NestedDefaultDict()

    # initialize the current item
    i = 0

    # while there are items in the variant dictionary
    while i < len(variant_dict):

        # initialize data
        variant_id = variant_dict[i]['variant_id']
        seq_id = ''
        position = 0
        found_gene = False
        found_exon = False

        # while there are items in the variant dictionary and the items have the same variant identification
        while i < len(variant_dict) and variant_id == variant_dict[i]['variant_id']:

            # save data
            variant_id = variant_dict[i]['variant_id']
            seq_id = variant_dict[i]['seq_id']
            position = variant_dict[i]['position']
            gene = variant_dict[i]['gene']

            # next item
            i += 1

        # add item to the intergenic variant dictionary
        if gene == 'N/A':
            intergenic_variant_dict[seq_id][position] = {'variant_id': variant_id}

    xlib.Message.print('verbose', 'Dictionary is built.\n')

    #-------------------------------------------------------------------------------
    # build the intergenic fragment dictionary
    #-------------------------------------------------------------------------------

    xlib.Message.print('verbose', 'Building the intergenic fragment dictionary ...\n')

    # initialize the fragment dictionary
    fragment_dict = xlib.NestedDefaultDict()

    # for each sequence identification in the intergenic variant dictionary
    for seq_id in sorted(intergenic_variant_dict.keys()):

        if seq_id in tsi_list: xlib.Message.print('trace', f'seq_id: {seq_id}')
        if seq_id in tsi_list: xlib.Message.print('trace', f'intergenic_variant_dict[seq_id]: {intergenic_variant_dict[seq_id]}')

        # initialize control variable for the first variant in the sequence
        first_variant = True

        # initialize the fragment number
        fragment_num = 0

        # for each position in the sequence
        for position in sorted(intergenic_variant_dict[seq_id]):

            # first variant in the sequence
            if first_variant:
                first_variant = False
                variant_id = intergenic_variant_dict[seq_id][position]['variant_id']
                fragment_id = f'{seq_id}-F{fragment_num:03d}'
                fragment_dict[variant_id] = {'fragment_id': fragment_id}
                old_position = position

            # the following variants in the sequence
            else:

                # when the position is less or equal to the maximum separation between variants of the same intergenic fragment
                if position <= old_position + max_separation:
                    variant_id = intergenic_variant_dict[seq_id][position]['variant_id']
                    fragment_id = f'{seq_id}-F{fragment_num:03d}'
                    fragment_dict[variant_id] = {'fragment_id': fragment_id}

                # when the position is greater to the maximum separation between variants of the same intergenic fragment
                else:
                    fragment_num += 1
                    variant_id = intergenic_variant_dict[seq_id][position]['variant_id']
                    fragment_id = f'{seq_id}-F{fragment_num:03d}'
                    fragment_dict[variant_id] = {'fragment_id': fragment_id}
                    old_position = position

    xlib.Message.print('verbose', 'Dictionary is built.\n')

    #-------------------------------------------------------------------------------
    # Create the variant file
    #-------------------------------------------------------------------------------

    xlib.Message.print('verbose', 'Writting the variant file ...\n')

    # initialize the imputation dictionary
    imputation_dict = xlib.NestedDefaultDict()

    # open the output variant file
    variant_file = f'{output_dir}/{file_name}-data2scenarioX-variants.csv'
    try:
        variant_file_id = open(variant_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', variant_file)

    # write head record of the output variant file
    variant_file_id.write('"variant_id";"seq_id";"position";"genomic_zone";"gene/fragment";"description";"chromosome_id";"imputations"\n')

    # initialize the current item
    i = 0

    # while there are items in the variant dictionary
    while i < len(variant_dict):

        # initialize data
        variant_id = variant_dict[i]['variant_id']
        found_gene = False
        found_exon = False

        # while there are items in the variant dictionary and the items have the same variant identification
        while i < len(variant_dict) and variant_id == variant_dict[i]['variant_id']:

            # save data
            seq_id = variant_dict[i]['seq_id']
            position = variant_dict[i]['position']
            # -- start = variant_dict[i]['start']
            end = variant_dict[i]['end']
            gene = variant_dict[i]['gene']
            description = variant_dict[i]['description']
            if description == None:
                description = 'N/A'
            chromosome_id = variant_dict[i]['chromosome_id']
            if chromosome_id == None:
                chromosome_id = 'N/A'
            if variant_dict[i]['gene'] != 'N/A':
                gene_or_fragment = variant_dict[i]['gene']
            else:
                gene_or_fragment = fragment_dict[variant_id]['fragment_id']
            if variant_dict[i]['type'] in ['gene', 'pseudogene']:
                found_gene = True
            elif variant_dict[i]['type'] == 'exon':
                found_exon = True

            # next item
            i += 1

        # set genomic_zone
        if end == 0:
            genomic_zone = 'N/A'
        elif not found_gene:
            genomic_zone = 'intergenic'
        elif found_exon:
            genomic_zone = 'exonic'
        else:
            genomic_zone = 'intronic'

        # set imputations
        if imputed_allele_dict.get(variant_id, 0) == 0:
            imputations = 'N'
        else:
            imputations = 'Y'

        # add variant dictionary to the gene dictionary
        imputation_dict[gene_or_fragment][variant_id] = {'imputations': imputations}

        # write data
        variant_file_id.write(f'"{variant_id}";"{seq_id}";{position};"{genomic_zone}";"{gene_or_fragment}";"{description}";"{chromosome_id}";"{imputations}"\n')

    # print OK message
    xlib.Message.print('info', f'The file {os.path.basename(variant_file)} containing variant data is created.')

    # close the output variant file
    variant_file_id.close()

    #-------------------------------------------------------------------------------
    # Create the allele file
    #-------------------------------------------------------------------------------

    xlib.Message.print('verbose', 'Writting the allele file ...\n')

    # open the output allele file
    allele_file = f'{output_dir}/{file_name}-data2scenarioX-alleles.csv'
    try:
        allele_file_id = open(allele_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', allele_file)

    # write head record of the output allele file
    allele_file_id.write(f'"variant_id";"seq_id";"position";"genomic_zone";"gene/fragment";"description";"chromosome_id";"imputations";"allele_id";"bases";"{sp1_id}_frequency";"{sp2_id}_frequency";"{hybrid_id}_frequency";"{sp1_id}_mothers_frequency";"{sp2_id}_mothers_frequency";"{hybrid_id}_mothers_frequency";"{sp1_id}_progenies_frequency";"{sp2_id}_progenies_frequency";"{hybrid_id}_progenies_frequency"\n')

    # initialize the current item
    i = 0

    # while there are items in the variant dictionary
    while i < len(variant_dict):

        # initialize data
        variant_id = variant_dict[i]['variant_id']
        found_gene = False
        found_exon = False

        if seq_id in tsi_list: xlib.Message.print('trace', f'variant_id: {variant_id}')

        # while there are items in the variant dictionary and the items have the same variant identification
        while i < len(variant_dict) and variant_id == variant_dict[i]['variant_id']:

            # save data
            seq_id = variant_dict[i]['seq_id']
            position = variant_dict[i]['position']
            # -- start = variant_dict[i]['start']
            end = variant_dict[i]['end']
            gene = variant_dict[i]['gene']
            description = variant_dict[i]['description']
            if description == None:
                description = 'N/A'
            chromosome_id = variant_dict[i]['chromosome_id']
            if chromosome_id == None:
                chromosome_id = 'N/A'
            if variant_dict[i]['gene'] != 'N/A':
                gene_or_fragment = variant_dict[i]['gene']
            else:
                gene_or_fragment = fragment_dict[variant_id]['fragment_id']
            if variant_dict[i]['type'] in ['gene', 'pseudogene']:
                found_gene = True
            elif variant_dict[i]['type'] == 'exon':
                found_exon = True

            # next item
            i += 1

        # set genomic_zone
        if end == 0:
            genomic_zone = 'N/A'
        elif not found_gene:
            genomic_zone = 'intergenic'
        elif found_exon:
            genomic_zone = 'exonic'
        else:
            genomic_zone = 'intronic'

        # set imputations
        if imputed_allele_dict.get(variant_id, 0) == 0:
            imputations = 'N'
        else:
            imputations = 'Y'

        # build the frecuency summation dictionary of every species per allele
        species_frecuency_summation_dict = {}
        for species_id in species_allele_frequency_dict[variant_id].keys():
            for allele_id in species_allele_frequency_dict[variant_id][species_id].keys():
                allele_data_dict = species_frecuency_summation_dict.get(allele_id, {sp1_id: 0, sp2_id: 0, hybrid_id: 0})
                allele_data_dict[species_id] += species_allele_frequency_dict[variant_id][species_id][allele_id]['frecuency_sum']
                species_frecuency_summation_dict[allele_id] = allele_data_dict

        if seq_id in tsi_list: xlib.Message.print('trace', f'species_frecuency_summation_dict: {species_frecuency_summation_dict}')

        # build the frecuency summation dictionary of every species and type per allele
        # species_and_type_allele_frequency_dict
        species_and_type_frecuency_summation_dict = {}
        for species_id in species_and_type_allele_frequency_dict[variant_id].keys():
            for type in species_and_type_allele_frequency_dict[variant_id][species_id].keys():
                for allele_id in species_and_type_allele_frequency_dict[variant_id][species_id][type].keys():
                    allele_data_dict = species_and_type_frecuency_summation_dict.get(allele_id, {f'{sp1_id}_mothers': 0, f'{sp2_id}_mothers': 0, f'{hybrid_id}_mothers': 0, f'{sp1_id}_progenies': 0, f'{sp2_id}_progenies': 0, f'{hybrid_id}_progenies': 0})
                    if type == 'MOTHER':
                        data_id = f'{species_id}_mothers'
                    elif type == 'PROGENY':
                        data_id = f'{species_id}_progenies'
                    allele_data_dict[data_id] += species_and_type_allele_frequency_dict[variant_id][species_id][type][allele_id]['frecuency_sum']
                    species_and_type_frecuency_summation_dict[allele_id] = allele_data_dict

        if seq_id in tsi_list: xlib.Message.print('trace', f'species_and_type_frecuency_summation_dict: {species_and_type_frecuency_summation_dict}')

        # calculate the allelle frecuency totals per species
        allele_frecuency_total_sp1 = 0
        allele_frecuency_total_sp2 = 0
        allele_frecuency_total_hybrid = 0
        for allele_id in species_frecuency_summation_dict.keys():
            allele_frecuency_total_sp1 += species_frecuency_summation_dict.get(allele_id, {}).get(sp1_id, 0)
            allele_frecuency_total_sp2 += species_frecuency_summation_dict.get(allele_id, {}).get(sp2_id, 0)
            allele_frecuency_total_hybrid += species_frecuency_summation_dict.get(allele_id, {}).get(hybrid_id, 0)

        if seq_id in tsi_list: xlib.Message.print('trace', f'allele_frecuency_total_sp1: {allele_frecuency_total_sp1}')
        if seq_id in tsi_list: xlib.Message.print('trace', f'allele_frecuency_total_sp2: {allele_frecuency_total_sp2}')
        if seq_id in tsi_list: xlib.Message.print('trace', f'allele_frecuency_total_hybrid: {allele_frecuency_total_hybrid}')

        # calculate the allelle frecuency totals per species and type
        allele_frecuency_total_sp1_mothers = 0
        allele_frecuency_total_sp2_mothers = 0
        allele_frecuency_total_hybrid_mothers = 0
        allele_frecuency_total_sp1_progenies = 0
        allele_frecuency_total_sp2_progenies = 0
        allele_frecuency_total_hybrid_progenies = 0
        for allele_id in species_frecuency_summation_dict.keys():
            allele_frecuency_total_sp1_mothers += species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{sp1_id}_mothers', 0)
            allele_frecuency_total_sp2_mothers += species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{sp2_id}_mothers', 0)
            allele_frecuency_total_hybrid_mothers += species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{hybrid_id}_mothers', 0)
            allele_frecuency_total_sp1_progenies += species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{sp1_id}_progenies', 0)
            allele_frecuency_total_sp2_progenies += species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{sp2_id}_progenies', 0)
            allele_frecuency_total_hybrid_progenies += species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{hybrid_id}_progenies', 0)

        if seq_id in tsi_list: xlib.Message.print('trace', f'allele_frecuency_total_sp1_mothers: {allele_frecuency_total_sp1_mothers}')
        if seq_id in tsi_list: xlib.Message.print('trace', f'allele_frecuency_total_sp2_mothers: {allele_frecuency_total_sp2_mothers}')
        if seq_id in tsi_list: xlib.Message.print('trace', f'allele_frecuency_total_hybrid_mothers: {allele_frecuency_total_hybrid_mothers}')
        if seq_id in tsi_list: xlib.Message.print('trace', f'allele_frecuency_total_sp1_progenies: {allele_frecuency_total_sp1_progenies}')
        if seq_id in tsi_list: xlib.Message.print('trace', f'allele_frecuency_total_sp2_progenies: {allele_frecuency_total_sp2_progenies}')
        if seq_id in tsi_list: xlib.Message.print('trace', f'allele_frecuency_total_hybrid_progenies: {allele_frecuency_total_hybrid_progenies}')

        # for each allele of the variant
        for allele_id in species_frecuency_summation_dict.keys():

            # calculate the relative frequency of each specie per allele
            try:
                sp1_frequency = species_frecuency_summation_dict[allele_id][sp1_id] / allele_frecuency_total_sp1
            except:
                sp1_frequency = 'N/A'
            try:
                sp2_frequency = species_frecuency_summation_dict[allele_id][sp2_id] / allele_frecuency_total_sp2
            except:
                sp2_frequency = 'N/A'
            try:
                hybrid_frequency = species_frecuency_summation_dict[allele_id][hybrid_id] / allele_frecuency_total_hybrid
            except:
                hybrid_frequency = 'N/A'

            # calculate the relative frequency of each specie and type per allele
            try:
                sp1_mothers_frequency = species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{sp1_id}_mothers', 0) / allele_frecuency_total_sp1_mothers
            except:
                sp1_mothers_frequency = 'N/A'
            try:
                sp2_mothers_frequency = species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{sp2_id}_mothers', 0) / allele_frecuency_total_sp2_mothers
            except:
                sp2_mothers_frequency =  'N/A'
            try:
                hybrid_mothers_frequency = species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{hybrid_id}_mothers', 0) / allele_frecuency_total_hybrid_mothers
            except:
                hybrid_mothers_frequency = 'N/A'
            try:
                sp1_progenies_frequency = species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{sp1_id}_progenies', 0) / allele_frecuency_total_sp1_progenies
            except:
                sp1_progenies_frequency = 'N/A'
            try:
                sp2_progenies_frequency = species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{sp2_id}_progenies', 0) / allele_frecuency_total_sp2_progenies
            except:
                sp2_progenies_frequency = 'N/A'
            try:
                hybrid_progenies_frequency = species_and_type_frecuency_summation_dict.get(allele_id, {}).get(f'{hybrid_id}_progenies', 0) / allele_frecuency_total_hybrid_progenies
            except:
                hybrid_progenies_frequency = 'N/A'

            # get bases sequence
            bases = allele_dict[variant_id][allele_id]['bases']

            # write data variant identification
            allele_file_id.write(f'"{variant_id}";"{seq_id}";{position};"{genomic_zone}";"{gene_or_fragment}";"{description}";"{chromosome_id}";"{imputations}";"{allele_id}";"{bases}";"{sp1_frequency}";"{sp2_frequency}";"{hybrid_frequency}";"{sp1_mothers_frequency}";"{sp2_mothers_frequency}";"{hybrid_mothers_frequency}";"{sp1_progenies_frequency}";"{sp2_progenies_frequency}";"{hybrid_progenies_frequency}"\n')

    # print OK message
    xlib.Message.print('info', f'The file {os.path.basename(allele_file)} containing allele data is created.')

    # close the output allele file
    allele_file_id.close()

    #-------------------------------------------------------------------------------
    # Create the selected variant id file corresponding to the scenario X
    #-------------------------------------------------------------------------------

    xlib.Message.print('verbose', 'Writting the file with selected variant id corresponding to the scenario X...\n')

    # open the output file with variant ids corresponding to the scenario X
    selected_id_file = f'{output_dir}/{file_name}-data2scenarioX-selected_ids.txt'
    try:
        selected_id_file_id = open(selected_id_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', selected_id_file)

    # for every gene/fragment write the variant identifications corresponding to scenario X
    for gene_or_fragment in sorted(imputation_dict.keys()):

        # initialize control variables
        imputations_with_y = False
        imputations_with_n = False

        # check imputations of variants of this gene/fragment
        for variant_id in imputation_dict[gene_or_fragment].keys():
            if imputation_dict[gene_or_fragment][variant_id]['imputations'] == 'Y':
                imputations_with_y = True
            else:
                imputations_with_n = True

        # write variant identitications
        for variant_id in imputation_dict[gene_or_fragment].keys():
            if imputations_with_y == True and imputations_with_n == False or imputation_dict[gene_or_fragment][variant_id]['imputations'] == 'N':
                selected_id_file_id.write(f'{variant_id}\n')

    # print OK message
    xlib.Message.print('info', f'The file {os.path.basename(selected_id_file)} containing selected ids is created.')

    # close the output allele file
    selected_id_file_id.close()


#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
