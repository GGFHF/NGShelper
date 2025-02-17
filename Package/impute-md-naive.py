#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program imputes genotypes with missing data in a VCF file using a naive process.

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
import threading

import xlib

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

    # impute genotypes with missing data in a VCF file using a naive process
    impute_md_naive(args.threads_num, args.input_vcf_file, args.output_vcf_file, args.imputation_data_file, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program imputes genotypes with missing data in a VCF file using a naive process.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--threads', dest='threads_num', help='Number of threads (mandatory).')
    parser.add_argument('--input_vcf', dest='input_vcf_file', help='Path of the input VCF file (mandatory).')
    parser.add_argument('--output_vcf', dest='output_vcf_file', help='Path of the output VCF file with missing data imputed (mandatory).')
    parser.add_argument('--impdata', dest='imputation_data_file', help='Path of the output file with imputation data (mandatory).')
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

    # check "imputation_data_file"
    if args.imputation_data_file is None:
        xlib.Message.print('error', '*** The output file with imputation data is not indicated in the input arguments.')
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
        args.tvi_list = xlib.split_literal_to_text_list(args.tvi_list)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def impute_md_naive(threads_num, input_vcf_file, output_vcf_file, imputation_data_file, tvi_list):
    '''
    Impute genotypes with missing data in a VCF file using a naive process.
    '''

    xlib.Message.print('verbose', 'Processing the imputation in the VCF file ...\n')
    xlib.Message.print('verbose', f'input_vcf_file: {input_vcf_file}\n')

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
    sample_id_list = []
    sample_label_list = []
    sample_number = 0
    label_dict = {}

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

    # open the output VCF file with missing data imputed
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

    # open the output file with imputation data
    if imputation_data_file.endswith('.gz'):
        try:
            imputation_data_file_id = gzip.open(imputation_data_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', imputation_data_file)
    else:
        try:
            imputation_data_file_id = open(imputation_data_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', imputation_data_file)

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

            # add 1 to the input record counter
            input_record_counter += 1

            # write the metadata record
            output_vcf_file_id.write(record)

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number=0, check_sample_number=False)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Imputed variants ... {imputed_variant_counter:8d}')

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the input record counter
            input_record_counter += 1

            # get the record data list
            record_data_list = data_dict['record_data_list']

            # build sample lists and sample dictionary
            for i in range(9, len(record_data_list)):
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

                # add 1 to the input record counter
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
                threads_list.append(threading.Thread(target=process_variant, args=[thread_id, tvi_list, sample_number, data_dict_list[thread_id], result_list]))
                threads_list[thread_id].start()

            # wait until all threads terminate
            for thread_id in range(w_threads_num):
                threads_list[thread_id].join()

            # process results of threads
            for thread_id in range(w_threads_num):

                # write the variant record
                output_vcf_file_id.write(result_list[thread_id]['output_vcf_record'])

                # if the variant is imputed
                if result_list[thread_id]['is_variant_imputed']:

                    # write the record in the output file with imputation data
                    imputation_data_file_id.write(result_list[thread_id]['imputation_data_record'])

                    # add 1 to imputed variant counter if the variant is imputed
                    imputed_variant_counter += 1

                # print the counters
                xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Imputed variants ... {imputed_variant_counter:8d}')

    xlib.Message.print('verbose', '\n')

    xlib.Message.print('info', f'Processed records: {input_record_counter:8d}')
    xlib.Message.print('info', f'Total variants   : {total_variant_counter:8d}')
    xlib.Message.print('info', f'Imputed variants : {imputed_variant_counter:8d}')

    # close files
    input_vcf_file_id.close()
    output_vcf_file_id.close()
    imputation_data_file_id.close()

#-------------------------------------------------------------------------------

def process_variant(thread_id, tvi_list, sample_number, data_dict, result_list):
    '''
    Process a variant and impute its genotypes with missing data using a naive process if necessary.
    '''

    # initialize the impute variant indicator
    is_variant_imputed = False

    # initialize alleles to symbol dictionary
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
        'NN': 'N'}

    # get the sequence identification, position and variant identification
    seq_id = data_dict['chrom']
    pos = data_dict['pos']
    variant_id = f'{seq_id}-{pos}'

    # get the reference allele and alternative alleles (field ALT)
    reference_allele = data_dict['ref']
    alternative_alleles = data_dict['alt']

    # build the alternative alleles list from field ALT
    alternative_allele_list = alternative_alleles.split(',')

    # initialize list of samples with missing data
    sample_withmd_list = []

    # check if the variant has more than one alternative allele
    if len(alternative_allele_list) > 1:
        raise xlib.ProgramException('L021', variant_id) from None

    # get the position of the genotype (subfield GT) in the field FORMAT
    format_subfield_list = data_dict['format'].upper().split(':')
    try:
        gt_position = format_subfield_list.index('GT')
    except Exception as e:
        raise xlib.ProgramException(e, 'L002', 'GT', data_dict['chrom'], data_dict['pos'])

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
            raise xlib.ProgramException('', 'L003', 'GT', data_dict['chrom'], data_dict['pos'])
        sample_sep_list.append(sep)
        sample_gt_left_list.append(sample_gt_list[i][:sep_pos])
        sample_gt_right_list.append(sample_gt_list[i][sep_pos+1:])

    # get the counter dictionary of genotypes
    counter_dict = collections.Counter(sample_gt_list)

    # get the most frenquent genotype
    most_frequent_gt = ''
    most_frequent_gt_counter = -1
    for gt, counter in counter_dict.items():
        if gt[0] != '.' and gt[2] != '.' and counter > most_frequent_gt_counter:
            most_frequent_gt = gt
            most_frequent_gt_counter = counter

    # impute missing data with the most frequent genotype
    for i in range(sample_number):
        if sample_gt_left_list[i] == '.' or sample_gt_right_list[i] == '.':
            sample_withmd_list.append(i)
            if most_frequent_gt != '':
                sample_gt_left_list[i] = most_frequent_gt[0]
                sample_gt_right_list[i] = most_frequent_gt[2]
                if not is_variant_imputed:
                    is_variant_imputed = True

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

    # save imputation data
    # record format: seq_id;pos;reference_allele;alternative_alleles;sample_withmd_list_text;symbolic_sample_gt_list_text
    if is_variant_imputed:
        sample_withmd_list_text = '_'.join([str(x) for x in sample_withmd_list])
        symbolic_sample_gt_list = []
        for i in range(sample_number):
            symbolic_sample_gt_left = reference_allele if sample_gt_left_list[i] == '0' else alternative_allele_list[0]
            symbolic_sample_gt_right = reference_allele if sample_gt_right_list[i] == '0' else alternative_allele_list[0]
            symbolic_sample_gt = ''.join(sorted([symbolic_sample_gt_left, symbolic_sample_gt_right]))
            symbolic_sample_gt_list.append(alleles2symbol_dict[symbolic_sample_gt])
        symbolic_sample_gt_list_text = ''.join(symbolic_sample_gt_list)
        imputation_data_record = f'{seq_id};{pos};{reference_allele};{alternative_alleles};{sample_withmd_list_text};{symbolic_sample_gt_list_text}\n'
    else:
        imputation_data_record = ''

    # update the result list
    result_list[thread_id] = {'output_vcf_record': output_vcf_record, 'imputation_data_record': imputation_data_record, 'is_variant_imputed': is_variant_imputed}

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
