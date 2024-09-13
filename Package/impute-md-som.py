#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program imputes genotypes with missing data in a VCF file using Self-Organizing Maps.

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
import sys
import threading

from threading import Semaphore
semaphore = Semaphore(1)

import minisom

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
    conn = xsqlite.connect_database(args.sqlite_database, check_same_thread=False)

    # impute genotypes with missing data in a VCF file using Self-Organizing Maps
    impute_md_som(conn, args.threads_num, args.input_vcf_file, args.output_vcf_file, args.minimum_r2, args.r_estimator, args.snps_num, args.xdim, args.ydim, args.sigma, args.learning_rate, args.num_iteration, args.genotype_imputation_method, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program imputes genotypes with missing data in a VCF file using Self-Organizing Maps.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--threads', dest='threads_num', help='Number of threads (mandatory).')
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--vcf', dest='input_vcf_file', help='Path of the input VCF file (mandatory).')
    parser.add_argument('--out', dest='output_vcf_file', help='Path of the output VCF file with missing data imputed (mandatory).')
    parser.add_argument('--xdim', dest='xdim', help='X dimension of the SOM (mandatory).')
    parser.add_argument('--ydim', dest='ydim', help='Y dimension of the SOM (mandatory).')
    parser.add_argument('--sigma', dest='sigma', help='Spread of the neighborhood function (mandatory).')
    parser.add_argument('--ilrate', dest='learning_rate', help='Initial learning rate (mandatory).')
    parser.add_argument('--iter', dest='num_iteration', help='Maximum number of iterations (mandatory).')
    parser.add_argument('--mr2', dest='minimum_r2', help='Minimum r^2 to select SNPs (mandatory).')
    parser.add_argument('--estimator', dest='r_estimator', help=f'Type of estimator: {xlib.get_r_estimator_code_list_text()}; default: {xlib.Const.DEFAULT_R_ESTIMATOR}.')
    parser.add_argument('--snps', dest='snps_num', help='Number of SNPs considered among those with r^2 >= mr2 (mandatory).')
    parser.add_argument('--gim', dest='genotype_imputation_method', help=f'Genotype imputation method: {xlib.get_genotype_imputation_method_code_list_text()}; default: {xlib.Const.DEFAULT_GENOTYPE_IMPUTATION_METHOD}.')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')
    parser.add_argument('--tvi', dest='tvi_list', help='Variant identification list to trace with format seq_id_1-pos_1,seq_id_2-pos_2,...,seq_id_n-pos_n or NONE; default: NONE.')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def check_args(args):
    '''
    Check the input arguments.
    '''

    # initialize the control variable
    OK = True

    # check "threads_num"
    if args.threads_num is None:
        xlib.Message.print('error', '*** The number of threads is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.threads_num, minimum=1):
        xlib.Message.print('error', 'The number of threads has to be an integer number greater than or equal to 1.')
        OK = False
    else:
        args.threads_num = int(args.threads_num)

    # check "sqlite_database"
    if args.sqlite_database is None:
        xlib.Message.print('error', '*** The SQLite database is not indicated in the input arguments.')
        OK = False

    # check "input_vcf_file"
    if args.input_vcf_file is None:
        xlib.Message.print('error', '*** The input VCF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.input_vcf_file):
        xlib.Message.print('error', f'*** The file {args.input_vcf_file} does not exist.')
        OK = False

    # check "output_vcf_file"
    if args.output_vcf_file is None:
        xlib.Message.print('error', '*** The output VCF file with missing data imputed is not indicated in the input arguments.')
        OK = False

    # check "xdim"
    if args.xdim is None:
        xlib.Message.print('error', '*** The X dimension of the SOM is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.xdim, minimum=1):
        xlib.Message.print('error', 'The X dimension of the SOM has to be an integer number greater than or equal to 1.')
        OK = False
    else:
        args.xdim = int(args.xdim)

    # check "ydim"
    if args.ydim is None:
        xlib.Message.print('error', '*** The Y dimension of the SOM is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.ydim, minimum=1):
        xlib.Message.print('error', 'The Y dimension of the SOM has to be an integer number greater than or equal to 1.')
        OK = False
    else:
        args.ydim = int(args.ydim)

    # check "sigma"
    if args.sigma is None:
        xlib.Message.print('error', '*** The sigma value is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.sigma, minimum=0.000001):
        xlib.Message.print('error', 'The sigma value has to be a float number greater than 0.0.')
        OK = False
    else:
        args.sigma = float(args.sigma)

    # check "learning_rate"
    if args.learning_rate is None:
        xlib.Message.print('error', '*** The initial learning rate is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.learning_rate, minimum=0.000001):
        xlib.Message.print('error', 'The initial learning rate has to be a float number greater than 0.0.')
        OK = False
    else:
        args.learning_rate = float(args.learning_rate)

    # check "num_iteration"
    if args.num_iteration is None:
        xlib.Message.print('error', '*** The maximum number of iterations is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.num_iteration, minimum=1):
        xlib.Message.print('error', 'The maximum number of iterations has to be an integer number greater than or equal to 1.')
        OK = False
    else:
        args.num_iteration = int(args.num_iteration)

    # check "minimum_r2"
    if args.minimum_r2 is None:
        xlib.Message.print('error', '*** The minimum r^2 value to select SNPs is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.minimum_r2, minimum=0.000001):
        xlib.Message.print('error', 'The minimum r^2 value to select SNPs has to be an float number greater than 0.')
        OK = False
    else:
        args.minimum_r2 = float(args.minimum_r2)

    # check "r_estimator"
    if args.r_estimator is None:
        args.r_estimator = xlib.Const.DEFAULT_R_ESTIMATOR
    else:
        if not xlib.check_code(args.verbose, xlib.get_r_estimator_code_list(), case_sensitive=False):
            xlib.Message.print('error', f'*** Type of estimator has to be {xlib.get_r_estimator_code_list_text()}.')
        else:
            args.r_estimator = args.r_estimator.lower()

    # check "snps_num"
    if args.snps_num is None:
        xlib.Message.print('error', '*** The number of SNPs considered among those with r^2 is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.snps_num, minimum=2):
        xlib.Message.print('error', 'The number of SNPs considered among those with r^2 has to be an integer number greater than or equal to 2.')
        OK = False
    else:
        args.snps_num = int(args.snps_num)

    # check "genotype_imputation_method"
    if args.genotype_imputation_method is None:
        args.genotype_imputation_method = xlib.Const.DEFAULT_GENOTYPE_IMPUTATION_METHOD
    elif not xlib.check_code(args.genotype_imputation_method, xlib.get_genotype_imputation_method_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The genotype imputation method has to be {xlib.get_genotype_imputation_method_code_list_text()}.')
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

    # check "tvi_list"
    if args.tvi_list is None or args.tvi_list == 'NONE':
        args.tvi_list = []
    else:
        args.tvi_list = xlib.split_literal_to_string_list(args.tvi_list)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def impute_md_som(conn, threads_num, input_vcf_file, output_vcf_file, minimum_r2, r_estimator, snps_num, xdim, ydim, sigma, learning_rate, num_iteration, genotype_imputation_method, tvi_list):
    '''
    Impute genotypes with missing data in a VCF file using Self-Organizing Maps.
    '''

    xlib.Message.print('verbose', 'Processing the imputation in the VCF file ...\n')
    xlib.Message.print('verbose', f'input_vcf_file: {input_vcf_file}\n')
    xlib.Message.print('verbose', f'minimum_r2: {minimum_r2} - snps_num: {snps_num}\n')
    xlib.Message.print('verbose', f'xdim: {xdim} - ydim: {ydim} - sigma: {sigma} - learning_rate: {learning_rate} - num_iteration: {num_iteration}\n')

    # get the number of CPUs in the system
    cpus_num = os.cpu_count()

    # set the mximum number of threads to be used
    if cpus_num is None:
        max_threads_num = threads_num
        xlib.Message.print('info', f'CPUs number in the system is undetermed. The process will use {threads_num} threads.\n')
    else:
        if cpus_num >=  threads_num:
            max_threads_num = threads_num
        else:
            max_threads_num = cpus_num
        xlib.Message.print('verbose', f'CPUs in the system: {cpus_num}.  The process will use {max_threads_num} threads.\n')

    # initialize the sample lists, sample number and label dict
    # -- sample_name_list = []
    sample_id_list = []
    sample_label_list = []
    sample_number = 0
    label_dict = {}

    # get the kinship dictionary
    kinship_dict = xsqlite.get_vcf_kinship_dict(conn)

    # get the list of snp identification with  missing data from table "vcf_linkage_disequilibrium_snp_id_1_list"
    snp_id_1_list = sorted(xsqlite.get_vcf_linkage_disequilibrium_snp_id_1_list(conn))

    # open the input VCF file
    if input_vcf_file.endswith('.gz'):
        try:
            input_vcf_file_id = gzip.open(input_vcf_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', input_vcf_file)
    else:
        try:
            input_vcf_file_id = open(input_vcf_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', input_vcf_file)

    # open the imputed VCF file
    if output_vcf_file.endswith('.gz'):
        try:
            output_vcf_file_id = gzip.open(output_vcf_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_vcf_file)
    else:
        try:
            output_vcf_file_id = open(output_vcf_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_vcf_file)

    # initialize counters
    input_record_counter = 0
    total_variant_counter = 0
    imputed_variant_counter = 0

    # read the first record of input VCF file
    (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number=0, check_sample_number=False)

    # while there are records in the VCF file to check
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # write the metadata record
            output_vcf_file_id.write(record)

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number=0, check_sample_number=False)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Imputed variants ... {imputed_variant_counter:8d}')

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # get the record data list
            record_data_list = data_dict['record_data_list']

            # build sample lists and sample dictionary
            for i in range(9, len(record_data_list)):
                # -- sample_name_list.append(os.path.basename(record_data_list[i]))
                sample_id_list.append(i - 9)
                sample_label_list.append(f'{i - 9:04d}')
                label_dict[f'{i - 9:04d}'] = i - 9

            # set the samples number
            sample_number = len(sample_id_list)
            xlib.Message.print('trace', f'sample_number: {sample_number}')

            # write the column description record
            output_vcf_file_id.write(record)

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number=0, check_sample_number=False)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Imputed variants ... {imputed_variant_counter:8d}')

        # process variant records
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # initialize working threads number
            w_threads_num = 0

            # initialize variant data dictionaries list
            data_dict_list = []

            # create a group of max_threads_num variant records
            while record != '' and not record.startswith('##') and not record.startswith('#CHROM') and w_threads_num < max_threads_num:

                # add 1 to the read sequence counter
                input_record_counter += 1

                # add 1 to the total variant counter
                total_variant_counter += 1

                # add 1 to the working threads number
                w_threads_num += 1

                # add variant data dictionary to variant data dictionaries list
                data_dict_list.append(data_dict)

                # read the next record of the input VCF file
                (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number=0, check_sample_number=False)

            # create and start threads
            threads_list = []
            result_list = []
            for thread_id in range(w_threads_num):
                result_list.append({})
                threads_list.append(threading.Thread(target=process_variant, args=[thread_id, conn, minimum_r2, r_estimator, snps_num, xdim, ydim, sigma, learning_rate, num_iteration, genotype_imputation_method, tvi_list, kinship_dict, snp_id_1_list, sample_label_list, label_dict, sample_number, data_dict_list[thread_id], result_list]))
                threads_list[thread_id].start()

            # wait until all threads terminate
            for thread_id in range(w_threads_num):
                threads_list[thread_id].join()

            # process results of threads
            for thread_id in range(w_threads_num):

                # -- print(f'\nthread_id: {thread_id} - result_list[{thread_id}]: {result_list[thread_id]}')

                # write the variant record
                output_vcf_file_id.write(result_list[thread_id]['output_vcf_record'])

                # add 1 to imputed variant counter if the variant is imputed
                if result_list[thread_id]['is_variant_imputed']:
                    imputed_variant_counter += 1

                # print the counters
                xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Imputed variants ... {imputed_variant_counter:8d}')

    xlib.Message.print('verbose', '\n')

    # close files
    input_vcf_file_id.close()
    output_vcf_file_id.close()

#-------------------------------------------------------------------------------

def process_variant(thread_id, conn, minimum_r2, r_estimator, snps_num, xdim, ydim, sigma, learning_rate, num_iteration, genotype_imputation_method, tvi_list, kinship_dict, snp_id_1_list, sample_label_list, label_dict, sample_number, data_dict, result_list):
    '''
    Process a variant and impute its genotypes with missing data using a Self-Organizing Map if necessary.
    '''

    # initialize the impute variant indicator
    is_variant_imputed = False

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
        'NN': 'N'
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
        'N': 'NN'
        }

    # set the symbol list
    symbol_list = sorted(symbol2alleles_dict.keys())

    # add set the variant identification
    variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'

    # get the reference allele and alternative alleles (field ALT)
    reference_allele = data_dict['ref']
    alternative_alleles = data_dict['alt']

    # build the alternative alleles list from field ALT
    alternative_allele_list = alternative_alleles.split(',')

    # check if the variant has more than one alternative allele
    if len(alternative_allele_list) > 1:
        raise xlib.ProgramException('L021', variant_id) from None

    # get the position of the genotype (subfield GT) in the field FORMAT
    format_subfield_list = data_dict['format'].upper().split(':')
    try:
        gt_position = format_subfield_list.index('GT')
    except Exception as e:
        raise xlib.ProgramException(e, 'L007', 'GT', data_dict['chrom'], data_dict['pos'])

    # build the list of sample genotypes of a variant
    sample_data_list = []
    sample_gt_list = []
    for i in range(sample_number):
        sample_data_list.append(data_dict['sample_list'][i].split(':'))
        sample_gt_list.append(sample_data_list[i][gt_position])

    # build the lists of the left and right side of sample genotypes of a variant
    sample_gt_left_list = []
    sample_sep_list = []
    sample_gt_right_list = []
    for i in range(sample_number):
        sep = '/'
        sep_pos = sample_gt_list[i].find(sep)
        if sep_pos == -1:
            sep = '|'
            sep_pos = sample_gt_list[i].find(sep)
        if sep_pos == -1:
            raise xlib.ProgramException('', 'L008', 'GT', data_dict['chrom'], data_dict['pos'])
        sample_sep_list.append(sep)
        sample_gt_left_list.append(sample_gt_list[i][:sep_pos])
        sample_gt_right_list.append(sample_gt_list[i][sep_pos+1:])

    # if there is missing data, impute it
    if variant_id in snp_id_1_list:

        if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - There is missing data')

        # get the linkage disequilibrium dictionary
        semaphore.acquire()
        ld_list = xsqlite.get_vcf_linkage_disequilibrium_list(conn, variant_id)
        semaphore.release()

        # build the genotype text before imputation
        genotype_text_before_imputation = ''
        for i in range(sample_number):
            genotype_text_before_imputation += f'{str(sample_gt_left_list[i])}{sample_sep_list[i]}{str(sample_gt_right_list[i])} '

        # get data of the variant from table "vcf_snps"
        semaphore.acquire()
        snp_data_dict_1 = xsqlite.get_snp_data_dict(conn, variant_id)
        semaphore.release()
        pseudobinary_sample_gt_list_1 = xlib.split_literal_to_integer_list(snp_data_dict_1['sample_gt_list'])
        sample_withmd_list = xlib.split_literal_to_integer_list(snp_data_dict_1['sample_withmd_list'])
        if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - sample_withmd_list: {sample_withmd_list}')

        # get the list with SNPs with the highest r^2 values calculated with respect to the current variant identification
        selected_snp_id_2_list = get_selected_snp_id_2_list(ld_list, minimum_r2, snps_num, inds_wmd=False)
        if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - selected_snp_id_2_list: {selected_snp_id_2_list}')

        # get the complete list of SNPs considered (the current variant id is the first)
        selected_snp_id_list = [variant_id] + selected_snp_id_2_list

        # initialize the list of symbolic genotype of samples
        symbolic_genotype_list = []
        for i in range(sample_number):
            symbolic_genotype_list.append('')

        # build secuences of samples
        for selected_snp_id in selected_snp_id_list:

            # get data of the selected SNP from table "vcf_snps"
            semaphore.acquire()
            snp_data_dict_2 = xsqlite.get_snp_data_dict(conn, selected_snp_id)
            semaphore.release()
            ref_2 = snp_data_dict_2['ref']
            alt_2 = snp_data_dict_2['alt']
            pseudobinary_sample_gt_list_2 = xlib.split_literal_to_integer_list(snp_data_dict_2['sample_gt_list'])

            for i in range(sample_number):
                # 0b00 -> 0
                if pseudobinary_sample_gt_list_2[i] == 0:
                    allele_list = [ref_2, ref_2]
                # 0b01 -> 1
                elif pseudobinary_sample_gt_list_2[i] == 1:
                    allele_list = [ref_2, alt_2]
                # 0b11 -> 3
                elif pseudobinary_sample_gt_list_2[i] == 3:
                    allele_list = [alt_2, alt_2]
                # 0b111 -> 7
                elif pseudobinary_sample_gt_list_2[i] == 7:
                    allele_list = ['N','N']
                allele_list.sort()
                allele_list_text = ''.join(allele_list)
                if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - i: {i} - ref_2: {ref_2} - alt_2: {alt_2}')
                if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - allele_list: {allele_list}')
                if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - allele_list_text: {allele_list_text}')
                symbolic_genotype_list[i] = f'{symbolic_genotype_list[i]}{alleles2symbol_dict[allele_list_text]}'

        if variant_id in tvi_list:
            for i in range(sample_number):
                if i in sample_withmd_list:
                    mark = '<---'
                else:
                    mark = ''
                if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - symbolic_genotype_list[{i:03d}]: {symbolic_genotype_list[i]} {mark}')

        # build the list with numeric haplotypes of each sample
        numeric_haplotype_3dlist = []
        for i in range(sample_number):
            numeric_haplotype_2dlist = []
            # the first nucleotide is not present to SOM !!!
            for j in range(1, len(symbolic_genotype_list[i])):
                numeric_haplotype_1dlist = []
                for symbol in symbol_list:
                    if symbol == symbolic_genotype_list[i][j]:
                        numeric_haplotype_1dlist.append(1)
                    else:
                        numeric_haplotype_1dlist.append(0)
                numeric_haplotype_2dlist.append(numeric_haplotype_1dlist)
            numeric_haplotype_3dlist.append(numeric_haplotype_2dlist)

        # calculate the most frequent genotype in the current variant
        counter_0_0 = 0
        counter_0_1 = 0
        counter_1_1 = 0
        for i in range(sample_number):
            # 0b00 -> 0
            if pseudobinary_sample_gt_list_1[i] == 0:
                counter_0_0 += 1
            # 0b01 -> 1
            elif pseudobinary_sample_gt_list_1[i] == 1:
                counter_0_1 += 1
            # 0b11 -> 3
            elif pseudobinary_sample_gt_list_1[i] == 3:
                counter_1_1 += 1
        if counter_0_0 > 0 or counter_0_1 > 0 or counter_1_1 > 0:
            if counter_0_0  == max(counter_0_0, counter_0_1, counter_1_1):
                sample_gt_left_mf = 0
                sample_gt_right_mf = 0
            elif counter_0_1  == max(counter_0_0, counter_0_1, counter_1_1):
                sample_gt_left_mf = 0
                sample_gt_right_mf = 1
            elif counter_1_1  == max(counter_0_0, counter_0_1, counter_1_1):
                sample_gt_left_mf = 1
                sample_gt_right_mf = 1
        if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - Most frequent genotype: sample_gt_left_mf: {sample_gt_left_mf} - sample_gt_right_mf: {sample_gt_right_mf}')

        # when the length of symbolic genotypes is equal to 1
        if len(symbolic_genotype_list[0]) == 1:

            # set the most frequent genotype as genotype of individuals with missing data
            for sample_withmd in sample_withmd_list:
                sample_gt_left_list[sample_withmd] = sample_gt_left_mf
                sample_gt_right_list[sample_withmd] = sample_gt_right_mf

        # when the length of symbolic genotypes is grater than 1
        elif len(symbolic_genotype_list[0]) > 1:

            # build the input data to the SOM algorith
            input_data_list = []
            for i in range(sample_number):
                numeric_haplotype_list = []
                for j in range(len(numeric_haplotype_3dlist[i])):
                    numeric_haplotype_list += numeric_haplotype_3dlist[i][j]
                input_data_list.append(numeric_haplotype_list)

            # build the training data corresponding to samples without missing data from the input data
            training_data_list = input_data_list.copy()
            training_label_list = sample_label_list.copy()
            for i in sorted(sample_withmd_list, reverse=True):
                training_data_list.pop(i)
                training_label_list.pop(i)

            # build the test data corresponding to samples with missing data from the input data
            test_data_list = []
            test_label_list = []
            for i in sample_withmd_list:
                test_data_list.append(input_data_list[i])
                test_label_list.append(sample_label_list[i])

            # create a new SOM 5x5 instance and train the SOM algorith
            som_shape_tup = (xdim, ydim)
            som = minisom.MiniSom(x=som_shape_tup[0], y=som_shape_tup[1], input_len=len(input_data_list[0]),
                                sigma=sigma, learning_rate=learning_rate, decay_function=minisom.asymptotic_decay,
                                neighborhood_function='gaussian', topology='rectangular', activation_distance='euclidean', random_seed=None)

            # initialize the weights to span the first two principal components
            som.pca_weights_init(data=training_data_list)

            # train the SOM
            som.train(data=training_data_list, num_iteration=num_iteration, random_order=False, verbose=False)

            # get a dictionary with the number of samples from a given label in each position
            labels_map_dict = som.labels_map(data=training_data_list, labels=training_label_list)
            # -- if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - labels_map_dict:\n{labels_map_dict}')

            # get a dictionary with samples in each coordinates
            samples_in_coordinates_dict = {}
            for coordinates_tup in sorted(labels_map_dict.keys()):
                label_list = list(labels_map_dict[coordinates_tup].keys())
                samples_in_coordinates_dict[coordinates_tup] = label_list

            # get the dictionary with related labels in the same coordinates
            related_label_dict = {}
            if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - Labels-sequences in coordenates ({len(samples_in_coordinates_dict.keys())}):')
            for coordinates_tup in sorted(samples_in_coordinates_dict.keys()):
                if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} -     coordinates_tup: {coordinates_tup}')
                label_list = samples_in_coordinates_dict[coordinates_tup]
                for label_id in label_list:
                    if label_dict[label_id] in sample_withmd_list:
                        related_label_dict[label_dict[label_id]] = label_list
                    seq = symbolic_genotype_list[label_dict[label_id]]
                    if int(label_id) in sample_withmd_list:
                        mark = '<---'
                    else:
                        mark = ''
                    if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} -         label_id: {label_id} - seq: {seq} {mark}')

            # get the coordinates of the winning neuron for the sample with missing data
            winning_neuron_coordinates_list = []
            for i in sample_withmd_list:
                winning_neuron_coordinates_tup = som.winner(input_data_list[i])
                winning_neuron_coordinates_list.append(winning_neuron_coordinates_tup)
                seq = symbolic_genotype_list[i]
                if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - label_id: {sample_label_list[i]} - seq: {seq} - winning_neuron_coordinates_tup:{winning_neuron_coordinates_tup}')

            # update the genotypes with missing data in the data of sequence records
            for i in range(len(sample_withmd_list)):    # pylint: disable=consider-using-enumerate
                coordinates_tup = winning_neuron_coordinates_list[i]
                try:
                    related_label_list = samples_in_coordinates_dict[coordinates_tup]
                except KeyError:
                    if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - sample_withmd_list[{i}]: {sample_withmd_list[i]} - there are not related samples in winning_neuron_coordinates_tup => most frequent genotype')
                    sample_gt_left_list[sample_withmd_list[i]] = sample_gt_left_mf
                    sample_gt_right_list[sample_withmd_list[i]] = sample_gt_right_mf
                else:
                    # method MF: the most frequent genotype in the neuron
                    if genotype_imputation_method == 'MF':
                        counter_0_0 = 0
                        counter_0_1 = 0
                        counter_1_1 = 0
                        for related_label in related_label_list:
                            # 0b00 -> 0
                            if pseudobinary_sample_gt_list_1[label_dict[related_label]] == 0:
                                counter_0_0 += 1
                            # 0b01 -> 1
                            elif pseudobinary_sample_gt_list_1[label_dict[related_label]] == 1:
                                counter_0_1 += 1
                            # 0b11 -> 3
                            elif pseudobinary_sample_gt_list_1[label_dict[related_label]] == 3:
                                counter_1_1 += 1
                        if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - sample_withmd_list[{i}]: {sample_withmd_list[i]} - counter_0_0: {counter_0_0} - counter_0_1: {counter_0_1} - counter_1_1: {counter_1_1}')
                        if counter_0_0 > 0 or counter_0_1 > 0 or counter_1_1 > 0:
                            if counter_0_0  == max(counter_0_0, counter_0_1, counter_1_1):
                                sample_gt_left_list[sample_withmd_list[i]] = 0
                                sample_gt_right_list[sample_withmd_list[i]] = 0
                            elif counter_0_1  == max(counter_0_0, counter_0_1, counter_1_1):
                                sample_gt_left_list[sample_withmd_list[i]] = 0
                                sample_gt_right_list[sample_withmd_list[i]] = 1
                            elif counter_1_1  == max(counter_0_0, counter_0_1, counter_1_1):
                                sample_gt_left_list[sample_withmd_list[i]] = 1
                                sample_gt_right_list[sample_withmd_list[i]] = 1
                    # method CK: the genotype of the closest kinship individual
                    elif genotype_imputation_method == 'CK':
                        related_sample_id_list = [int(x) for x in related_label_list]
                        most_related_sample_id = get_most_related_sample_id(kinship_dict, r_estimator, sample_withmd_list[i], related_sample_id_list)
                        sample_gt_left_list[sample_withmd_list[i]] = sample_gt_left_list[most_related_sample_id]
                        sample_gt_right_list[sample_withmd_list[i]] = sample_gt_right_list[most_related_sample_id]
                        if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - sample_withmd_list[{i}]: {sample_withmd_list[i]} - most_related_sample_id: {most_related_sample_id}')
                if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} -     sample_gt_left_list[{sample_withmd_list[i]}]: {sample_gt_left_list[sample_withmd_list[i]]} - sample_gt_right_list[{sample_withmd_list[i]}]: {sample_gt_right_list[sample_withmd_list[i]]}')

            # add 1 to the imputed variant counter
            is_variant_imputed = True

        # build the genotype text after imputation
        genotype_text_after_imputation = ''
        for i in range(sample_number):
            genotype_text_after_imputation += f'{str(sample_gt_left_list[i])}{sample_sep_list[i]}{str(sample_gt_right_list[i])} '
        if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - genotype list before imputation: {genotype_text_before_imputation}')
        if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - genotype list  after imputation: {genotype_text_after_imputation}')

    # if there are no mising data
    else:

        if variant_id in tvi_list: xlib.Message.print('trace', f'thread_id: {thread_id} - variant_id: {variant_id} - There is no missing data')

    # rebuild the list of the field GT for every sample
    for i in range(sample_number):
        sample_gt_list[i] = f'{sample_gt_left_list[i]}{sample_sep_list[i]}{sample_gt_right_list[i]}'

    # rebuild the sample genotype data list and their corresponding record data
    sample_list = []
    for i in range(sample_number):
        sample_data_list[i][gt_position] = sample_gt_list[i]
        sample_list.append(':'.join(sample_data_list[i]))

    # rebuild the variant record
    sample_list_text = '\t'.join(sample_list)
    output_vcf_record = f'{data_dict["chrom"]}\t{data_dict["pos"]}\t{data_dict["id"]}\t{data_dict["ref"]}\t{data_dict["alt"]}\t{data_dict["qual"]}\t{data_dict["filter"]}\t{data_dict["info"]}\t{data_dict["format"]}\t{sample_list_text}\n'

    # update the result list
    result_list[thread_id] = {'output_vcf_record': output_vcf_record, 'is_variant_imputed': is_variant_imputed}

#-------------------------------------------------------------------------------

def get_snp_dict_dict(snps_file):
    '''
    Get the SNP dictionary from a file saved by the program calculate-genotype-data.py.
    '''

    # initialize the SNP dictionary
    snp_dict = {}

    # open the SNPs file
    if snps_file.endswith('.gz'):
        try:
            snps_file_id = gzip.open(snps_file, mode='rt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', snps_file)
    else:
        try:
            snps_file_id = open(snps_file, mode='r', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', snps_file)

    # initialize the header record control
    header_record = True

    # initialize the record counter
    record_counter = 0

    # read the first record
    record = snps_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # process the header record
        if header_record:
            header_record = False

        # process data records
        else:

            # extract data
            # record format: "variant_id";"ref";"alt";"sample_gt_list";"sample_withmd_list"
            data_list = []
            begin = 0
            for end in [i for i, chr in enumerate(record) if chr == ';']:
                data_list.append(record[begin:end].strip())
                begin = end + 1
            data_list.append(record[begin:].strip('\n').strip())
            try:
                variant_id = data_list[0].replace('"','')
                reference_allele = data_list[1].replace('"','')
                alternative_allele = data_list[2].replace('"','')
                sample_gt_list_text = data_list[3].replace('"','')
                binary_sample_gt_list = [int(bin(x),2) for x in xlib.split_literal_to_integer_list(sample_gt_list_text)]
                sample_withmd_list_text = data_list[4].replace('"','')
                sample_withmd_list = xlib.split_literal_to_integer_list(sample_withmd_list_text)
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(snps_file), record_counter)

            # load SNP data into the dictionary
            snp_dict[variant_id] = {'ref': reference_allele, 'alt': alternative_allele, 'gt': binary_sample_gt_list, 'md': sample_withmd_list}

            # print counters
            xlib.Message.print('verbose', f'\rLD file: {record_counter} processed records')

        # read the next record
        record = snps_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close alignments file
    snps_file_id.close()

    # return the SNP dictionary
    return snp_dict

#-------------------------------------------------------------------------------

def get_selected_snp_id_2_list(ld_list, minimum_r2, snps_num, inds_wmd):
    '''
    Get a list of snps_num identification of snp_id_2 with highest r^2 values
    whose value is greater than or iqual to minimum_r2.
    '''

    # sort the list by r^2 in descending order
    ordered_ld_list = sorted(ld_list, key=lambda x:x[2], reverse=True)

    # build the list of snp_id_2 with the highest r^2
    selected_snp_id_2_list = []
    i = 0
    counter = 0
    while i < len(ordered_ld_list) and counter < snps_num:
        if ordered_ld_list[i][2] >= minimum_r2:
            if inds_wmd or ordered_ld_list[i][3] == '':
                selected_snp_id_2_list.append(ordered_ld_list[i][0])
                counter += 1
            i += 1
        else:
            break

    # return the list of snp_id_2 with the highest r^2
    return selected_snp_id_2_list

#-------------------------------------------------------------------------------

def get_most_related_sample_id(kinship_dict, r_estimator, sample_wmd_id, related_sample_id_list):
    '''
    Get the most related sample identification of the sample_wmd_id using the kinship dictionary.
    '''

    # initialize the most related sample identification
    most_related_sample_id = -999

    # initialize the maximum kinship value
    max_r = -999

    # get the sample identication with the highest kinship value
    for related_sample_id in related_sample_id_list:
        if sample_wmd_id < related_sample_id:
            if r_estimator == 'rbeta':
                r = kinship_dict[sample_wmd_id][related_sample_id]['rbeta']
            elif r_estimator == 'rw':
                r = kinship_dict[sample_wmd_id][related_sample_id]['rw']
            elif r_estimator == 'ru':
                r = kinship_dict[sample_wmd_id][related_sample_id]['ru']
        else:
            if r_estimator == 'rbeta':
                r = kinship_dict[related_sample_id][sample_wmd_id]['rbeta']
            elif r_estimator == 'rw':
                r = kinship_dict[related_sample_id][sample_wmd_id]['rw']
            elif r_estimator == 'ru':
                r = kinship_dict[related_sample_id][sample_wmd_id]['ru']
        if r > max_r:
            max_r = r
            most_related_sample_id = related_sample_id

    # return the most related sample identification
    return most_related_sample_id

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
