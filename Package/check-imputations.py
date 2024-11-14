#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program checks the missing data imputations in a VCF whose missing data were simulated.

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
import collections
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

    # check the missing data imputation
    check_imputations(conn, args.ch_vcf_file, args.md_vcf_file, args.imputations_map_file, args.summary_file, args.confusion_matrix_file, args.experiment_data, args.tsi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program checks the missing data imputations in a VCF whose missing data were simulated.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--chvcffile', dest='ch_vcf_file', help='Path of the VCF file with imputations to be checked (mandatory).')
    parser.add_argument('--mdvcffile', dest='md_vcf_file', help='Path of the VCF file with missing data (mandatory).')
    parser.add_argument('--mapfile', dest='imputations_map_file', help='Path of the CSV file with the imputations map (mandatory).')
    parser.add_argument('--summfile', dest='summary_file', help='Path of the CSV file where the summaries of checkings are saved (mandatory).')
    parser.add_argument('--cmfile', dest='confusion_matrix_file', help='Path of CSV file where the confusion matrix is saved (mandatory).')
    parser.add_argument('--expdata', dest='experiment_data', help='Data semicolon-separated to identify the experimient or NONE; default NONE.')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')
    parser.add_argument('--tsi', dest='tsi_list', help='Sequence identification list to trace with format seq_id,seq_id_2,...,seq_id or NONE; default: NONE.')

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

    # check "ch_vcf_file"
    if args.ch_vcf_file is None:
        xlib.Message.print('error', '*** The VCF file with imputations to be checked is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.ch_vcf_file):
        xlib.Message.print('error', f'*** The file {args.ch_vcf_file} does not exist.')
        OK = False

    # check "md_vcf_file"
    if args.md_vcf_file is None:
        xlib.Message.print('error', '*** The VCF file with missing data is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.md_vcf_file):
        xlib.Message.print('error', f'*** The file {args.md_vcf_file} does not exist.')
        OK = False

    # check "imputations_map_file"
    if args.imputations_map_file is None:
        xlib.Message.print('error', '*** The CSV file with the imputations map is not indicated in the input arguments.')
        OK = False

    # check "summary_file"
    if args.summary_file is None:
        xlib.Message.print('error', '*** The CSV file where the summaries of checkings are saved is not indicated in the input arguments.')
        OK = False

    # check "confusion_matrix_file"
    if args.confusion_matrix_file is None:
        xlib.Message.print('error', '*** The CSV file where the confusion matrix is saved is not indicated in the input arguments.')
        OK = False

    # check "experiment_data"
    if args.experiment_data is None:
        args.experiment_data = 'NONE'

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

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def check_imputations(conn, chvcffile, mdvcffile, imputations_map_file, summary_file, confusion_matrix_file, experiment_data, tsi_list):
    '''
    Check the missing data imputations in a VCF whose missing data were simulated.
    '''

    # initialize the dictionaries
    alleles2symbol_dict = {
        'AA': 'A',
        'CC': 'C',
        'GG': 'G',
        'TT': 'T',
        'AC': 'M',
        'AG': 'R',
        'AT': 'W',
        'CG': 'S',
        'CT': 'Y',
        'GT': 'K',
        f'{xlib.get_md_symbol()}{xlib.get_md_symbol()}': f'{xlib.get_md_symbol()}'
        }
    symbol2alleles_dict = {
        'A': 'AA',
        'C': 'CC',
        'G': 'GG',
        'T': 'TT',
        'M': 'AC',
        'R': 'AG',
        'W': 'AT',
        'S': 'CG',
        'Y': 'CT',
        'K': 'GT',
        f'{xlib.get_md_symbol()}': f'{xlib.get_md_symbol()}{xlib.get_md_symbol()}'
        }

    # set the symbol list
    symbol_list = symbol2alleles_dict.keys()

    # build the confusion matrix dictionary
    confusion_matrix_dict = {}
    for symbol_list_actual in symbol_list:
        confusion_matrix_dict[symbol_list_actual] = {}
        for symbol_list_predicted in symbol_list:
            confusion_matrix_dict[symbol_list_actual][symbol_list_predicted] = 0

    # initialize the sample number
    sample_number = 0

    # initialize the lists of sample identifications in the VCF files
    chvcffile_sample_ids_list = []
    mdvcffile_sample_ids_list = []

    # open the original VCF file with missing data
    if mdvcffile.endswith('.gz'):
        try:
            mdvcffile_id = gzip.open(mdvcffile, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', mdvcffile) from None
    else:
        try:
            mdvcffile_id = open(mdvcffile, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', mdvcffile) from None

    # open the input VCF file to check
    if chvcffile.endswith('.gz'):
        try:
            chvcffile_id = gzip.open(chvcffile, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', chvcffile) from None
    else:
        try:
            chvcffile_id = open(chvcffile, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', chvcffile) from None

    # open the CSV file nwith the imputations map
    if imputations_map_file.endswith('.gz'):
        try:
            imputations_map_file_id = gzip.open(imputations_map_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', imputations_map_file)
    else:
        try:
            imputations_map_file_id = open(imputations_map_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', imputations_map_file)

    # initialize file counters
    mdvcffile_input_record_counter = 0
    mdvcffile_total_variant_counter = 0
    mdvcffile_nonconsidered_variants_counter = 0
    chvcffile_input_record_counter = 0
    chvcffile_total_variant_counter = 0
    chvcffile_nonconsidered_variants_counter = 0

    # inicialize the genotypes statistics
    total_genotypes_counter = 0
    mdvcffile_ok_genotypes_counter = 0
    mdvcffile_ko_genotypes_counter = 0
    mdvcffile_genotypes_withmd_counter = 0
    chvcffile_ok_genotypes_counter = 0
    chvcffile_ko_genotypes_counter = 0
    chvcffile_genotypes_withmd_counter = 0
    chvcffile_ok_imputed_genotypes_counter = 0
    chvcffile_ko_imputed_genotypes_counter = 0

    # read the first record of the original VCF file with missing data
    (mdvcffile_record, mdvcffile_key, mdvcffile_data_dict) = xlib.read_vcf_file(mdvcffile_id, sample_number)

    # read the first record of the VCF file to check
    (chvcffile_record, chvcffile_key, chvcffile_data_dict) = xlib.read_vcf_file(chvcffile_id, sample_number)

    # while there are records in either of the VCF files
    while mdvcffile_record != '' or chvcffile_record != '':

        # process metadata records in the original VCF file with missing data
        while mdvcffile_record != '' and mdvcffile_record.startswith('##'):

            # add 1 to the read sequence counter
            mdvcffile_input_record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rmdvcffile ---> records: {mdvcffile_input_record_counter:8d} - variants: {mdvcffile_total_variant_counter:8d} - non-considered: {mdvcffile_nonconsidered_variants_counter:8d} | chvcffile ---> records: {chvcffile_input_record_counter:8d} - variants: {chvcffile_total_variant_counter:8d} - non-considered: {chvcffile_nonconsidered_variants_counter:8d}')

            # read the next record of the original VCF file with missing data
            (mdvcffile_record, mdvcffile_key, mdvcffile_data_dict) = xlib.read_vcf_file(mdvcffile_id, sample_number)

        # process metadata records in the VCF file to check
        while chvcffile_record != '' and chvcffile_record.startswith('##'):

            # add 1 to the read sequence counter
            chvcffile_input_record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rmdvcffile ---> records: {mdvcffile_input_record_counter:8d} - variants: {mdvcffile_total_variant_counter:8d} - non-considered: {mdvcffile_nonconsidered_variants_counter:8d} | chvcffile ---> records: {chvcffile_input_record_counter:8d} - variants: {chvcffile_total_variant_counter:8d} - non-considered: {chvcffile_nonconsidered_variants_counter:8d}')

            # read the next record of the VCF file to check
            (chvcffile_record, chvcffile_key, chvcffile_data_dict) = xlib.read_vcf_file(chvcffile_id, sample_number)

        # process the column description record in the original VCF file with missing data
        if mdvcffile_record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            mdvcffile_input_record_counter += 1

            # get the record data list
            mdvcffile_record_data_list = mdvcffile_data_dict['record_data_list']

            # build the sample identification list per variant
            for i in range(9, len(mdvcffile_record_data_list)):
                sample_id = mdvcffile_record_data_list[i]
                mdvcffile_sample_ids_list.append(sample_id)

            # set the sample number
            sample_number = len(mdvcffile_sample_ids_list)

            # print the counters
            xlib.Message.print('verbose', f'\rmdvcffile ---> records: {mdvcffile_input_record_counter:8d} - variants: {mdvcffile_total_variant_counter:8d} - non-considered: {mdvcffile_nonconsidered_variants_counter:8d} | chvcffile ---> records: {chvcffile_input_record_counter:8d} - variants: {chvcffile_total_variant_counter:8d} - non-considered: {chvcffile_nonconsidered_variants_counter:8d}')

            # read the next record of the VCF file check
            (mdvcffile_record, mdvcffile_key, mdvcffile_data_dict) = xlib.read_vcf_file(mdvcffile_id, sample_number)

        # process the column description record in the VCF file to check
        if chvcffile_record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            chvcffile_input_record_counter += 1

            # get the record data list
            chvcffile_record_data_list = chvcffile_data_dict['record_data_list']

            # build the individual identification lists per variant
            for i in range(9, len(chvcffile_record_data_list)):
                sample_id = chvcffile_record_data_list[i]
                chvcffile_sample_ids_list.append(sample_id)

            # check if the samples number is OK
            if sample_number != len(chvcffile_sample_ids_list):
                raise xlib.ProgramException('', 'L017', os.path.basename(mdvcffile), sample_number, os.path.basename(chvcffile), len(chvcffile_sample_ids_list)) from None

            # check if the list of individuals is the same in both VCF files
            if collections.Counter(mdvcffile_sample_ids_list) != collections.Counter(chvcffile_sample_ids_list):
                raise xlib.ProgramException('', 'L018', os.path.basename(mdvcffile), os.path.basename(chvcffile)) from None

            # write the head record of the CSV file nwith the imputations map
            chvcffile_sample_ids_list_text = ';'.join(chvcffile_sample_ids_list)
            imputations_map_file_id.write(f'variant_id;{chvcffile_sample_ids_list_text}\n')

            # print the counters
            xlib.Message.print('verbose', f'\rmdvcffile ---> records: {mdvcffile_input_record_counter:8d} - variants: {mdvcffile_total_variant_counter:8d} - non-considered: {mdvcffile_nonconsidered_variants_counter:8d} | chvcffile ---> records: {chvcffile_input_record_counter:8d} - variants: {chvcffile_total_variant_counter:8d} - non-considered: {chvcffile_nonconsidered_variants_counter:8d}')

            # read the next record of the VCF file check
            (chvcffile_record, chvcffile_key, chvcffile_data_dict) = xlib.read_vcf_file(chvcffile_id, sample_number)

        # process variant record when the variant in the original VCF file with missing data is less than in the variant in the VCF file to check
        while mdvcffile_record != '' and not mdvcffile_record.startswith('##') and not mdvcffile.startswith('#CHROM') and mdvcffile_key < chvcffile_key:

            # add 1 to the read sequence counter
            mdvcffile_input_record_counter += 1

            # add 1 to the total variant counter
            mdvcffile_total_variant_counter += 1

            # add 1 to the non-considered variant counter
            mdvcffile_nonconsidered_variants_counter += 1

            # set the variant identification
            mdvcffile_variant_id = f'{mdvcffile_data_dict["chrom"]}-{mdvcffile_data_dict["pos"]}'
            xlib.Message.print('trace', f'only in mdvcffile ---> variant_id: {mdvcffile_variant_id}')

            # print the counters
            xlib.Message.print('verbose', f'\rmdvcffile ---> records: {mdvcffile_input_record_counter:8d} - variants: {mdvcffile_total_variant_counter:8d} - non-considered: {mdvcffile_nonconsidered_variants_counter:8d} | chvcffile ---> records: {chvcffile_input_record_counter:8d} - variants: {chvcffile_total_variant_counter:8d} - non-considered: {chvcffile_nonconsidered_variants_counter:8d}')

            # read the next record of the original VCF file with missing data
            (mdvcffile_record, mdvcffile_key, mdvcffile_data_dict) = xlib.read_vcf_file(mdvcffile_id, sample_number)

        # process variant record when the variant in the original VCF file with missing data is equal to the variant in the VCF file to check
        while mdvcffile_record != '' and not mdvcffile_record.startswith('##') and not mdvcffile_record.startswith('#CHROM') and chvcffile_record != '' and not chvcffile_record.startswith('##') and not chvcffile_record.startswith('#CHROM') and mdvcffile_key == chvcffile_key:

            # add 1 to the read sequence counters
            mdvcffile_input_record_counter += 1
            chvcffile_input_record_counter += 1

            # add 1 to the total variant counters
            mdvcffile_total_variant_counter += 1
            chvcffile_total_variant_counter += 1

            # set the sequence, position and variant identifications
            mdvcffile_chrom_scaff_id = mdvcffile_data_dict['chrom']
            mdvcffile_position = int(mdvcffile_data_dict["pos"])
            mdvcffile_variant_id = f'{mdvcffile_data_dict["chrom"]}-{mdvcffile_data_dict["pos"]}'
            chvcffile_chrom_scaff_id = chvcffile_data_dict['chrom']
            chvcffile_position = int(chvcffile_data_dict["pos"])
            chvcffile_variant_id = f'{chvcffile_data_dict["chrom"]}-{chvcffile_data_dict["pos"]}'

            # get the reference allele and alternative alleles (field ALT)
            mdvcffile_reference_allele = mdvcffile_data_dict['ref']
            mdvcffile_alternative_alleles = mdvcffile_data_dict['alt']
            chvcffile_reference_allele = chvcffile_data_dict['ref']
            chvcffile_alternative_alleles = chvcffile_data_dict['alt']

            # check if the reference allele is the same in both VCF files
            if mdvcffile_reference_allele != chvcffile_reference_allele:
                raise xlib.ProgramException('', 'L019', mdvcffile_variant_id, os.path.basename(mdvcffile), os.path.basename(chvcffile)) from None

            # check if the alternative alleles are the same in both VCF files
            if mdvcffile_alternative_alleles != chvcffile_alternative_alleles:
                raise xlib.ProgramException('', 'L020', mdvcffile_variant_id, os.path.basename(mdvcffile), os.path.basename(chvcffile)) from None

            # build the alternative alleles lists from field ALT
            mdvcffile_alternative_allele_list = mdvcffile_alternative_alleles.split(',')
            chvcffile_alternative_allele_list = chvcffile_alternative_alleles.split(',')

            # check if the variant has more than one alternative allele
            if len(mdvcffile_alternative_allele_list) > 1:
                raise xlib.ProgramException('', 'L021', mdvcffile_variant_id) from None
            if len(chvcffile_alternative_allele_list) > 1:
                raise xlib.ProgramException('', 'L021', chvcffile_variant_id) from None

            # get the position of the genotype (subfield GT) in the field FORMAT
            mdvcffile_format_subfield_list = mdvcffile_data_dict['format'].upper().split(':')
            try:
                gt_position = mdvcffile_format_subfield_list.index('GT')
            except Exception:
                raise xlib.ProgramException('', 'L007', 'GT', mdvcffile_data_dict['chrom'], mdvcffile_data_dict['pos']) from None
            chvcffile_format_subfield_list = chvcffile_data_dict['format'].upper().split(':')
            try:
                gt_position = chvcffile_format_subfield_list.index('GT')
            except Exception:
                raise xlib.ProgramException('', 'L007', 'GT', chvcffile_data_dict['chrom'], chvcffile_data_dict['pos']) from None

            # build the list of sample genotypes of a variant and update counters corresponding to the original VCF file with missing data
            mdvcffile_sample_gt_list = []
            for i in range(sample_number):
                mdvcffile_sample_data_list = mdvcffile_data_dict['sample_list'][i].split(':')
                mdvcffile_sample_gt_list.append(mdvcffile_sample_data_list[gt_position])

            # build the lists of sample genotypes of a variant and update counters corresponding to the VCF file to check
            chvcffile_sample_gt_list = []
            for i in range(sample_number):
                chvcffile_sample_data_list = chvcffile_data_dict['sample_list'][i].split(':')
                chvcffile_sample_gt_list.append(chvcffile_sample_data_list[gt_position])

            # initialize the record with imputations map
            map_record = chvcffile_variant_id

            # check the genotype of each sample
            for i in range(sample_number):

                # add 1 to total genotypes counter
                total_genotypes_counter += 1

                # get the left and right side of sample genotypes of a variant corresponding to the original VCF file with missing data
                sep = '/'
                sep_pos = mdvcffile_sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    sep = '|'
                    sep_pos = mdvcffile_sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    raise xlib.ProgramException('', 'L008', 'GT', mdvcffile_data_dict['chrom'], mdvcffile_data_dict['pos'])
                mdvcffile_sample_gt_left = mdvcffile_sample_gt_list[i][:sep_pos]
                mdvcffile_sample_gt_right = mdvcffile_sample_gt_list[i][sep_pos+1:]

                # get the left and right side of sample genotypes of a variant corresponding to the VCF file to check
                sep = '/'
                sep_pos = chvcffile_sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    sep = '|'
                    sep_pos = chvcffile_sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    raise xlib.ProgramException('', 'L008', 'GT', chvcffile_data_dict['chrom'], chvcffile_data_dict['pos'])
                chvcffile_sample_gt_left = chvcffile_sample_gt_list[i][:sep_pos]
                chvcffile_sample_gt_right = chvcffile_sample_gt_list[i][sep_pos+1:]

                # check the genotype corresponding to the original VCF file with missing data
                if mdvcffile_sample_gt_left == xlib.get_md_symbol() or mdvcffile_sample_gt_right == xlib.get_md_symbol():
                    mdvcffile_genotypes_withmd_counter += 1
                    is_there_md = True
                else:
                    is_there_md = False
                    # build individual genotype from VCF data
                    mdvcffile_vcf_genotype_list = []
                    if mdvcffile_sample_gt_left == '0':
                        mdvcffile_vcf_genotype_list.append(mdvcffile_reference_allele.upper())
                    elif mdvcffile_sample_gt_left == '1':
                        mdvcffile_vcf_genotype_list.append(mdvcffile_alternative_alleles[0].upper())
                    if mdvcffile_sample_gt_right == '0':
                        mdvcffile_vcf_genotype_list.append(mdvcffile_reference_allele.upper())
                    elif mdvcffile_sample_gt_right == '1':
                        mdvcffile_vcf_genotype_list.append(mdvcffile_alternative_alleles[0].upper())
                    mdvcffile_vcf_genotype_list.sort()
                    mdvcffile_vcf_genotype = ''.join(mdvcffile_vcf_genotype_list)
                    # build individual genotype from the database
                    mdvcffile_db_genotype_list = []
                    (db_gt_left,  db_gt_right) = xsqlite.get_vcf_individual_genotype(conn, mdvcffile_variant_id, mdvcffile_sample_ids_list[i])
                    if db_gt_left == '0':
                        mdvcffile_db_genotype_list.append(mdvcffile_reference_allele.upper())
                    elif db_gt_left == '1':
                        mdvcffile_db_genotype_list.append(mdvcffile_alternative_alleles[0].upper())
                    if db_gt_right == '0':
                        mdvcffile_db_genotype_list.append(mdvcffile_reference_allele.upper())
                    elif db_gt_right == '1':
                        mdvcffile_db_genotype_list.append(mdvcffile_alternative_alleles[0].upper())
                    mdvcffile_db_genotype_list.sort()
                    mdvcffile_db_genotype = ''.join(mdvcffile_db_genotype_list)
                    # check
                    if mdvcffile_vcf_genotype == mdvcffile_db_genotype:
                        mdvcffile_ok_genotypes_counter += 1
                    else:
                        # -- print(f'mdvcffile_key: {mdvcffile_key} - mdvcffile_db_genotype: {mdvcffile_db_genotype} - mdvcffile_vcf_genotype: {mdvcffile_vcf_genotype} - db_gt_left: {db_gt_left} - db_gt_right: {db_gt_right}')
                        mdvcffile_ko_genotypes_counter += 1

                # check the genotype correspondint to the imputed VCF file
                # build individual genotype from VCF data
                chvcffile_vcf_genotype_list = []
                if chvcffile_sample_gt_left == xlib.get_md_symbol() or chvcffile_sample_gt_right == xlib.get_md_symbol():
                    chvcffile_vcf_genotype = f'{xlib.get_md_symbol()}{xlib.get_md_symbol()}'
                else:
                    if chvcffile_sample_gt_left == '0':
                        chvcffile_vcf_genotype_list.append(chvcffile_reference_allele.upper())
                    elif chvcffile_sample_gt_left == '1':
                        chvcffile_vcf_genotype_list.append(chvcffile_alternative_alleles[0].upper())
                    if chvcffile_sample_gt_right == '0':
                        chvcffile_vcf_genotype_list.append(chvcffile_reference_allele.upper())
                    elif chvcffile_sample_gt_right == '1':
                        chvcffile_vcf_genotype_list.append(chvcffile_alternative_alleles[0].upper())
                    chvcffile_vcf_genotype_list.sort()
                    chvcffile_vcf_genotype = ''.join(chvcffile_vcf_genotype_list)
                # build individual genotype from the database
                chvcffile_db_genotype_list = []
                (db_gt_left,  db_gt_right) = xsqlite.get_vcf_individual_genotype(conn, chvcffile_variant_id, chvcffile_sample_ids_list[i])
                if db_gt_left == '0':
                    chvcffile_db_genotype_list.append(chvcffile_reference_allele.upper())
                elif db_gt_left == '1':
                    chvcffile_db_genotype_list.append(chvcffile_alternative_alleles[0].upper())
                if db_gt_right == '0':
                    chvcffile_db_genotype_list.append(chvcffile_reference_allele.upper())
                elif db_gt_right == '1':
                    chvcffile_db_genotype_list.append(chvcffile_alternative_alleles[0].upper())
                chvcffile_db_genotype_list.sort()
                chvcffile_db_genotype = ''.join(chvcffile_db_genotype_list)

                # when there is missing data in the genotype corresponding to the original VCF file with missing data,
                # add information to the confusion matrix
                if is_there_md:
                    genotype_symbol_real = alleles2symbol_dict[chvcffile_db_genotype]
                    genotype_symbol_predicted = alleles2symbol_dict[chvcffile_vcf_genotype]
                    confusion_matrix_dict[genotype_symbol_real][genotype_symbol_predicted] += 1

                # add information in the map record
                # when there is missing data in the genotype corresponding to the original VCF file with missing data
                if is_there_md:
                    # when there is missing data in the genotype corresponding to the imputed VCF
                    if chvcffile_sample_gt_left == xlib.get_md_symbol() or chvcffile_sample_gt_right == xlib.get_md_symbol():
                        map_record += ';MD'
                        chvcffile_genotypes_withmd_counter += 1
                        xlib.Message.print('trace', f'MD ---> variant_id: {chvcffile_variant_id} - sample_ids_list[i]: {chvcffile_sample_ids_list[i]} - sample_gt_left: {chvcffile_sample_gt_left} - sample_gt_right: {chvcffile_sample_gt_right}')
                    # when there is not missing data in the genotype corresponding to the imputed VCF
                    else:
                        # when there was a missing data in the VCF with missing data
                        if chvcffile_vcf_genotype == chvcffile_db_genotype:
                            map_record += ';OK'
                            chvcffile_ok_imputed_genotypes_counter += 1
                        else:
                            map_record += ';KO'
                            chvcffile_ko_imputed_genotypes_counter += 1
                # when there is not missing data in the genotype corresponding to the original VCF file with missing data
                else:
                    if chvcffile_vcf_genotype == chvcffile_db_genotype:
                        map_record += ';-'
                        chvcffile_ok_genotypes_counter += 1
                    else:
                        map_record += ';-'
                        chvcffile_ko_genotypes_counter += 1

            # write the record with imputations map
            imputations_map_file_id.write(f'{map_record}\n')

            # print the counters
            xlib.Message.print('verbose', f'\rmdvcffile ---> records: {mdvcffile_input_record_counter:8d} - variants: {mdvcffile_total_variant_counter:8d} - non-considered: {mdvcffile_nonconsidered_variants_counter:8d} | chvcffile ---> records: {chvcffile_input_record_counter:8d} - variants: {chvcffile_total_variant_counter:8d} - non-considered: {chvcffile_nonconsidered_variants_counter:8d}')

            # read the next record of the original VCF file with missing data
            (mdvcffile_record, mdvcffile_key, mdvcffile_data_dict) = xlib.read_vcf_file(mdvcffile_id, sample_number)

            # read the next record of the VCF file to check
            (chvcffile_record, chvcffile_key, chvcffile_data_dict) = xlib.read_vcf_file(chvcffile_id, sample_number)

        # process variant record when the variant key in the VCF file to check is less than in the variant key in the original VCF file with missing data
        while chvcffile_record != '' and not chvcffile_record.startswith('##') and not chvcffile_key.startswith('#CHROM') and chvcffile_key < mdvcffile_key:

            # add 1 to the read sequence counter
            chvcffile_input_record_counter += 1

            # add 1 to the total variant counter
            chvcffile_total_variant_counter += 1

            # add 1 to the non-considered variant counter
            chvcffile_nonconsidered_variants_counter += 1

            # set the variant identification
            chvcffile_variant_id = f'{chvcffile_data_dict["chrom"]}-{chvcffile_data_dict["pos"]}'
            xlib.Message.print('trace', f'only in chvcffile ---> variant_id: {chvcffile_variant_id}')

            # print the counters
            xlib.Message.print('verbose', f'\rmdvcffile ---> records: {mdvcffile_input_record_counter:8d} - variants: {mdvcffile_total_variant_counter:8d} - non-considered: {mdvcffile_nonconsidered_variants_counter:8d} | chvcffile ---> records: {chvcffile_input_record_counter:8d} - variants: {chvcffile_total_variant_counter:8d} - non-considered: {chvcffile_nonconsidered_variants_counter:8d}')

            # read the next record of the VCF file to check
            (chvcffile_record, chvcffile_key, chvcffile_data_dict) = xlib.read_vcf_file(chvcffile_id, sample_number)

    xlib.Message.print('verbose', '\n')

    # open the confusion matrix file
    if confusion_matrix_file.endswith('.gz'):
        try:
            confusion_matrix_file_id = gzip.open(confusion_matrix_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', confusion_matrix_file)
    else:
        try:
            confusion_matrix_file_id = open(confusion_matrix_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', confusion_matrix_file)

    # save the header in the confusion matrix file
    confusion_matrix_header = ' '
    for symbol_predicted in symbol_list:
        confusion_matrix_header = f'{confusion_matrix_header};{symbol_predicted}'
    confusion_matrix_file_id.write(f'{confusion_matrix_header}\n')

    # save the confusion matrix
    for symbol_actual in symbol_list:
        confusion_matrix_row = f'{symbol_actual} ({symbol2alleles_dict[symbol_actual]})'
        for symbol_predicted in symbol_list:
            confusion_matrix_row = f'{confusion_matrix_row};{confusion_matrix_dict[symbol_actual][symbol_predicted]}'
        confusion_matrix_file_id.write(f'{confusion_matrix_row}\n')

    # Calculate the metrics of the confusion matrix
    (average_accuracy, error_rate, micro_precision, micro_recall, micro_fscore, macro_precision, macro_recall, macro_fscore, macro_precision_zde, macro_recall_zde) = calculate_confusion_matrix_metrics(confusion_matrix_dict)

    # open the summary file
    if summary_file.endswith('.gz'):
        try:
            summary_file_id = gzip.open(summary_file, mode='at', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', summary_file)
    else:
        try:
            summary_file_id = open(summary_file, mode='a', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', summary_file)

    # save the statistics summary
    if experiment_data.upper() == 'NONE':
        summary_file_id.write(f'{os.path.basename(chvcffile)};{chvcffile_ok_genotypes_counter};{chvcffile_ko_genotypes_counter};{chvcffile_genotypes_withmd_counter};{chvcffile_ok_imputed_genotypes_counter};{chvcffile_ko_imputed_genotypes_counter};{average_accuracy};{error_rate};{micro_precision};{micro_recall};{micro_fscore};{macro_precision};{macro_recall};{macro_fscore};{macro_precision_zde};{macro_recall_zde}\n')
    else:
        summary_file_id.write(f'{os.path.basename(chvcffile)};{experiment_data};{chvcffile_ok_genotypes_counter};{chvcffile_ko_genotypes_counter};{chvcffile_genotypes_withmd_counter};{chvcffile_ok_imputed_genotypes_counter};{chvcffile_ko_imputed_genotypes_counter};{average_accuracy};{error_rate};{micro_precision};{micro_recall};{micro_fscore};{macro_precision};{macro_recall};{macro_fscore};{macro_precision_zde};{macro_recall_zde}\n')

    # show statitistics
    xlib.Message.print('info',  '*************************')
    xlib.Message.print('info', f'mdvcffile ---> variants: {mdvcffile_total_variant_counter} - considerer variants: {mdvcffile_total_variant_counter - mdvcffile_nonconsidered_variants_counter} ({(mdvcffile_total_variant_counter - mdvcffile_nonconsidered_variants_counter)/mdvcffile_total_variant_counter*100:3.2f}%) - non-considerer variants: {mdvcffile_nonconsidered_variants_counter} ({mdvcffile_nonconsidered_variants_counter/mdvcffile_total_variant_counter*100:3.2f}%)')
    xlib.Message.print('info', f'chvcffile ---> variants: {chvcffile_total_variant_counter} - considerer variants: {chvcffile_total_variant_counter - chvcffile_nonconsidered_variants_counter} ({(chvcffile_total_variant_counter - chvcffile_nonconsidered_variants_counter)/chvcffile_total_variant_counter*100:3.2f}%) - non-considerer variants: {chvcffile_nonconsidered_variants_counter} ({chvcffile_nonconsidered_variants_counter/chvcffile_total_variant_counter*100:3.2f}%)')
    xlib.Message.print('info',  '')
    xlib.Message.print('info', f'Genotypes analyzed: {total_genotypes_counter}')
    xlib.Message.print('info', f'mdvcffile ---> OK: {mdvcffile_ok_genotypes_counter} ({mdvcffile_ok_genotypes_counter/total_genotypes_counter*100:3.2f}%) - KO: {mdvcffile_ko_genotypes_counter} ({mdvcffile_ko_genotypes_counter/total_genotypes_counter*100:3.2f}%) - MD: {mdvcffile_genotypes_withmd_counter} ({mdvcffile_genotypes_withmd_counter/total_genotypes_counter*100:3.2f}%)')
    xlib.Message.print('info', f'chvcffile ---> OK: {chvcffile_ok_genotypes_counter} ({chvcffile_ok_genotypes_counter/total_genotypes_counter*100:3.2f}%) - KO: {chvcffile_ko_genotypes_counter} ({chvcffile_ko_genotypes_counter/total_genotypes_counter*100:3.2f}%) - MD: {chvcffile_genotypes_withmd_counter} ({chvcffile_genotypes_withmd_counter/total_genotypes_counter*100:3.2f}%) - OK IMPUTED: {chvcffile_ok_imputed_genotypes_counter} ({chvcffile_ok_imputed_genotypes_counter/total_genotypes_counter*100:3.2f}%) - KO IMPUTED: {chvcffile_ko_imputed_genotypes_counter} ({chvcffile_ko_imputed_genotypes_counter/total_genotypes_counter*100:3.2f}%)')
    xlib.Message.print('info',  '')
    xlib.Message.print('info',  'OK: VCF genotypes matched with initial data')
    xlib.Message.print('info',  'KO: VCF genotypes non-matched with initial data')
    xlib.Message.print('info',  'MD: VCF genotypes with missing data')
    xlib.Message.print('info',  'OK IMPUTED: VCF genotypes with missing data imputed and then matched with initial data')
    xlib.Message.print('info',  'KO IMPUTED: VCF genotypes with missing data imputed and then non-matched with initial data')
    xlib.Message.print('info',  '*************************')

    # close files
    mdvcffile_id.close()
    chvcffile_id.close()
    imputations_map_file_id.close()
    confusion_matrix_file_id.close()
    summary_file_id.close()

#-------------------------------------------------------------------------------

def calculate_confusion_matrix_metrics(confusion_matrix_dict):
    '''
    Calculate the metrics of a confusion matrix with multi-classes.
    (Sokolova, Lapalme - 2009 - A systematic analysis of performance measures for classification tasks - DOI: 10.1016/j.ipm.2009.03.002)

    '''

    # set the list and dictionary of classes
    class_codes_list = list(confusion_matrix_dict.keys())
    class_codes_dict = {}
    for class_code in class_codes_list:
        class_codes_dict[class_code] = False

    # checking the classes without values (values are 0) in the confusion matrix
    for class_code_1 in class_codes_list:
        for class_code_2 in class_codes_list:
            if confusion_matrix_dict[class_code_1][class_code_2] > 0:
                class_codes_dict[class_code_1] = True
                class_codes_dict[class_code_2] = True

    # remove classes without values from the classes list
    for key, value in class_codes_dict.items():
        if not value:
            class_codes_list.remove(key)

    # initialize the imputation count
    n = 0

    # initialize the classes count
    l = 0

    # initialize specific classes counts
    macro_precision_l  = 0
    macro_recall_l  = 0

    # initialize the summations
    average_accuracy_summation = 0
    error_rate_summation = 0
    micro_precision_numerator_summation = 0
    micro_precision_denominator_summation = 0
    micro_recall_numerator_summation = 0
    micro_recall_denominator_summation = 0
    macro_precision_summation = 0
    macro_recall_summation = 0

    # initialize ZeroDivisionError counts
    macro_precision_zde = 0
    macro_recall_zde = 0

    # process the confusion matrix to calculate summations involved in their metrics
    for class_code_1 in class_codes_list:

        # calculate the TP (true positive) count for the current actual class
        tp = confusion_matrix_dict[class_code_1][class_code_1]
        n += tp

        # calculate the FN (false netative) count for the current actual class
        fn = 0
        for class_code_2 in class_codes_list:
            if class_code_2 != class_code_1:
                fn += confusion_matrix_dict[class_code_1][class_code_2]
        n += fn

        # calculate the fp (false positive) count for the current actual class
        fp = 0
        for class_code_2 in class_codes_list:
            if class_code_2 != class_code_1:
                fp +=  confusion_matrix_dict[class_code_2][class_code_1]
        n += fp

        # calculate the tn (true negative) count for the current actual class
        tn = 0
        for class_code_2 in class_codes_list:
            for class_3 in class_codes_list:
                if class_code_2 != class_code_1 and class_3 != class_code_1:
                    tn +=  confusion_matrix_dict[class_code_2][class_3]
                    n += tn

        xlib.Message.print('info', f'class_1: {class_code_1} - tp: {tp} - fn: {fn} - fp: {fp} - tn: {tn}')

        # update the summations
        if (tp + fn + fp + tn) > 0:

            l += 1

            average_accuracy_summation += (tp + tn) / (tp + fn + fp + tn)
            error_rate_summation +=  (fp + fn) / (tp + fn + fp + tn)
            micro_precision_numerator_summation += tp
            micro_precision_denominator_summation += (tp + fp)
            micro_recall_numerator_summation += tp
            micro_recall_denominator_summation += (tp + fn)
            try:
                macro_precision_summation += tp / (tp + fp)
                macro_precision_l += 1
            except ZeroDivisionError:
                macro_precision_zde += 1
            try:
                macro_recall_summation += tp / (tp + fn)
                macro_recall_l += 1
            except ZeroDivisionError:
                macro_recall_zde += 1

    # calculate metrics
    if n > 0:

        average_accuracy = average_accuracy_summation / l
        error_rate = error_rate_summation / l
        try:
            micro_precision = micro_precision_numerator_summation / micro_precision_denominator_summation
        except ZeroDivisionError:
            micro_precision = 'NA'
        try:
            micro_recall = micro_recall_numerator_summation / micro_recall_denominator_summation
        except ZeroDivisionError:
            micro_recall = 'NA'
        try:
            macro_precision = macro_precision_summation / macro_precision_l
        except ZeroDivisionError:
            macro_precision = 'NA'
        try:
            macro_recall = macro_recall_summation / macro_recall_l
        except ZeroDivisionError:
            macro_recall = 'NA'
        beta = 1
        try:
            if micro_precision == 'NA' or micro_recall == 'NA':
                micro_fscore = 'NA'
            else:
                micro_fscore = (beta ** 2 + 1) * micro_precision * micro_recall / ((beta ** 2) * micro_precision + micro_recall)
        except ZeroDivisionError:
            micro_fscore = 'NA'
        try:
            if macro_precision == 'NA' or macro_recall == 'NA':
                macro_fscore = 'NA'
            else:
                macro_fscore = (beta ** 2 + 1) * macro_precision * macro_recall / ((beta ** 2) * macro_precision + macro_recall)
        except ZeroDivisionError:
            macro_fscore = 'NA'

    else:

        average_accuracy = 'NA'
        error_rate = 'NA'
        micro_precision = 'NA'
        micro_recall = 'NA'
        macro_precision = 'NA'
        macro_recall = 'NA'
        micro_fscore = 'NA'
        macro_fscore = 'NA'
        macro_precision_zde = 'NA'
        macro_recall_zde = 'NA'

    xlib.Message.print('info', f'n: {n} - l: {l} - macro_precision_l: {macro_precision_l}  - macro_recall_l: {macro_recall_l}')
    xlib.Message.print('info', f'average_accuracy: {average_accuracy} - error_rate: {error_rate}')
    xlib.Message.print('info', f'micro_precision: {micro_precision} - micro_recall: {micro_recall} - micro_fscore: {micro_fscore}')
    xlib.Message.print('info', f'macro_precision: {macro_precision} - macro_recall: {macro_recall} - macro_fscore: {macro_fscore}')
    xlib.Message.print('info', f'macro_precision_zde: {macro_precision_zde} - macro_recall_zde: {macro_recall_zde}')

    # return metrics
    return average_accuracy, error_rate, micro_precision, micro_recall, micro_fscore, macro_precision, macro_recall, macro_fscore, macro_precision_zde, macro_recall_zde

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
