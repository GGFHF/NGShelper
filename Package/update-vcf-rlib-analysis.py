#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program updates the missing data in a VCF file with the results of an
analysis performed using an R library such as bpca, missForest, nipals, nlpca,
ppca or svdImpute. The row of result matrix must layout similar to a VCF file
with the format: 
    seq_id \t possition \t genotype-1 \t genotype-2 \t ... \t genotype-n
The first row must contain the list of sample identifiers separated by the
character '\t' 

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

    # updates the missing data in a VCF file with the results of an analysis performed using an R library
    update_vcf_with_rlib_analysis(args.md_vcf_file, args.imputed_vcf_file, args.analysis_file, args.tsi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program updates the missing data in a VCF file with the results of an analysis\n' \
        'performed using a R library such as bpca, missForest, nipals, nlpca, ppca or svdImpute.\n' \
        'The row of result matrix must layout similar to a VCF file with the format: \n' \
        '    seq_id \\t possition \\t genotype-1 \\t genotype-2 \\t ... \\t genotype-n \n' \
        'The first row must contain the list of sample identifiers separated by the character "\\t"'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--mdvcffile', dest='md_vcf_file', help='Path of the VCF file wih missing data (mandatory).')
    parser.add_argument('--impvcffile', dest='imputed_vcf_file', help='Path of the output VCF file with imputed data (mandatory).')
    parser.add_argument('--analfile', dest='analysis_file', help='Path of result analysis file performed with an R library (mandatory).')
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

    # check "md_vcf_file"
    if args.md_vcf_file is None:
        xlib.Message.print('error', '*** The VCF file wih missing data is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.md_vcf_file):
        xlib.Message.print('error', f'*** The file {args.md_vcf_file} does not exist.')
        OK = False

    # check "imputed_vcf_file"
    if args.imputed_vcf_file is None:
        xlib.Message.print('error', '*** The output VCF file with imputed data is not indicated in the input arguments.')
        OK = False

    # check "analysis_file"
    if args.analysis_file is None:
        xlib.Message.print('error', '*** The result analysis file performed with an R library is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.analysis_file):
        xlib.Message.print('error', f'*** The file {args.analysis_file} does not exist.')
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

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def update_vcf_with_rlib_analysis(md_vcf_file, imputed_vcf_file, analysis_file, tsi_list):
    '''
    Updates the missing data in a VCF file with the results an analysis performed using an R library.
    '''

    # initialize the sample number
    md_vcf_sample_number = 0

    # initialize the sample information list
    md_vcf_sample_list = []

    # open the VCF file with missing data
    if md_vcf_file.endswith('.gz'):
        try:
            md_vcf_file_id = gzip.open(md_vcf_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', md_vcf_file)
    else:
        try:
            md_vcf_file_id = open(md_vcf_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', md_vcf_file)

    # open the result analysis file
    if analysis_file.endswith('.gz'):
        try:
            analysis_file_id = gzip.open(analysis_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', analysis_file) from None
    else:
        try:
            analysis_file_id = open(analysis_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', analysis_file) from None

    # open the imputed VCF file
    if imputed_vcf_file.endswith('.gz'):
        try:
            imputed_vcf_file_id = gzip.open(imputed_vcf_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', imputed_vcf_file)
    else:
        try:
            imputed_vcf_file_id = open(imputed_vcf_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', imputed_vcf_file)

    # initialize counters
    md_vcf_record_counter = 0
    md_vcf_variant_counter = 0
    analysis_record_counter = 0
    analysis_variant_counter = 0

    # read the first record of VCF file
    (md_vcf_record, md_vcf_key, md_vcf_data_dict) = xlib.read_vcf_file(md_vcf_file_id, md_vcf_sample_number)

    # read the first record of result analysis file and get the sample list
    analysis_record = analysis_file_id.readline()
    analysis_record_counter += 1
    analysis_sample_list = [item.strip('"') for item in analysis_record.strip('\n').split()]

    # read the next record of  the result analysis file
    (analysis_record, analysis_key, analysis_data_dict) = read_analysis_file(analysis_file_id)

    # while there are records in the VCF file with missing data or in analysis file
    while md_vcf_record != '' or analysis_record != '':

        # process metadata records in the original VCF file with missing data
        while md_vcf_record != '' and md_vcf_record.startswith('##'):

            # add 1 to the record counter
            md_vcf_record_counter += 1

            # write the metadata record
            imputed_vcf_file_id.write(md_vcf_record)

            # print the counters
            xlib.Message.print('verbose', f'\rmd_vcf_record_counter: {md_vcf_record_counter:6d} - md_vcf_variant_counter: {md_vcf_variant_counter:6d} - analysis_record_counter: {analysis_record_counter:6d} | analysis_variant_counter: {analysis_variant_counter:6d}')

            # read the next record of the VCF file with missing data
            (md_vcf_record, md_vcf_key, md_vcf_data_dict) = xlib.read_vcf_file(md_vcf_file_id, md_vcf_sample_number)

        # process the column description record in the original VCF file with missing data
        if md_vcf_record.startswith('#CHROM'):

            # add 1 to the record counter
            md_vcf_record_counter += 1

            # get the record data list
            md_vcf_data_list = md_vcf_data_dict['record_data_list']

            # set the sample number and sample information list
            md_vcf_sample_number = len(md_vcf_data_list) - 9
            md_vcf_sample_list = md_vcf_data_list[9:]

            # check the two sample list are equal
            if md_vcf_sample_list != analysis_sample_list:
                print(f'\nmd_vcf_sample_list:\n{md_vcf_sample_list}')
                print(f'analysis_sample_list:\n{analysis_sample_list}')
                raise xlib.ProgramException('', 'L018', md_vcf_file, analysis_file)

            # write the column description record
            imputed_vcf_file_id.write(md_vcf_record)

            # print the counters
            xlib.Message.print('verbose', f'\rmd_vcf_record_counter: {md_vcf_record_counter:6d} - md_vcf_variant_counter: {md_vcf_variant_counter:6d} - analysis_record_counter: {analysis_record_counter:6d} | analysis_variant_counter: {analysis_variant_counter:6d}')

            # read the next record of the VCF file with missing data
            (md_vcf_record, md_vcf_key, md_vcf_data_dict) = xlib.read_vcf_file(md_vcf_file_id, md_vcf_sample_number)

        # process the variant record when the variant in the original VCF file with missing data is less than the variant in the analysis file
        while md_vcf_record != '' and not md_vcf_record.startswith('##') and not md_vcf_record.startswith('#CHROM') and md_vcf_key < analysis_key:

            print(f'solo md_vcf - variante: {md_vcf_key} ')

            # add 1 to the record counter
            md_vcf_record_counter += 1

            # add 1 to the variant counter
            md_vcf_variant_counter += 1

            # write the column description record
            imputed_vcf_file_id.write(md_vcf_record)

            # print the counters
            xlib.Message.print('verbose', f'\rmd_vcf_record_counter: {md_vcf_record_counter:6d} - md_vcf_variant_counter: {md_vcf_variant_counter:6d} - analysis_record_counter: {analysis_record_counter:6d} | analysis_variant_counter: {analysis_variant_counter:6d}')

            # read the next record of the VCF file with missing data
            (md_vcf_record, md_vcf_key, md_vcf_data_dict) = xlib.read_vcf_file(md_vcf_file_id, md_vcf_sample_number)

        # process the the variant in the analysis file is less than variant record when the variant in the original VCF file with missing data
        while analysis_record != '' and analysis_key < md_vcf_key:

            print(f'solo nalysis_vcf - variante: {analysis_key} ')

            # add 1 to the record counter
            analysis_record_counter += 1

            # add 1 to the variant counter
            analysis_variant_counter += 1

            # read the next record of  the result analysis file
            (analysis_record, analysis_key, analysis_data_dict) = read_analysis_file(analysis_file_id)

            # print the counters
            xlib.Message.print('verbose', f'\rmd_vcf_record_counter: {md_vcf_record_counter:6d} - md_vcf_variant_counter: {md_vcf_variant_counter:6d} - analysis_record_counter: {analysis_record_counter:6d} | analysis_variant_counter: {analysis_variant_counter:6d}')

        # process variant record when the variant in the original VCF file with missing data is equal to the variant in the analysis file
        while md_vcf_record != '' and not md_vcf_record.startswith('##') and not md_vcf_record.startswith('#CHROM') and analysis_record != ''  and md_vcf_key == analysis_key:

            # add 1 to the record counters
            md_vcf_record_counter += 1
            analysis_record_counter += 1

            # set the current sequence identification
            seq_id = md_vcf_data_dict['chrom']

            # set the variant identification
            variant_id = f'{md_vcf_data_dict["chrom"]}-{md_vcf_data_dict["pos"]}'
            if seq_id in tsi_list: xlib.Message.print('trace', f'\n\n\nnvariant_id: {variant_id}')

            # get the reference bases (field REF) and alternative alleles (field ALT)
            reference_bases = md_vcf_data_dict['ref']
            alternative_alleles = md_vcf_data_dict['alt']
            if seq_id in tsi_list: xlib.Message.print('trace', f'reference_bases: {reference_bases}')
            if seq_id in tsi_list: xlib.Message.print('trace', f'alternative_alleles: {alternative_alleles}')

            # build the alternative allele list
            alternative_allele_list = alternative_alleles.split(',')
            if seq_id in tsi_list: xlib.Message.print('trace', f'alternative_allele_list: {alternative_allele_list}')

            # build the complete allele list
            complete_allele_list = [reference_bases] + alternative_allele_list
            if seq_id in tsi_list: xlib.Message.print('trace', f'complete_allele_list: {complete_allele_list}')

            # get the position of the genotype (subfield GT) in the field FORMAT
            format_subfield_list = md_vcf_data_dict['format'].upper().split(':')
            try:
                gt_position = format_subfield_list.index('GT')
            except Exception as e:
                raise xlib.ProgramException(e, 'L007', 'GT', md_vcf_data_dict['chrom'], md_vcf_data_dict['pos'])

            # build the list of sample genotypes of a variant
            sample_data_list = []
            sample_gt_list = []
            for i in range(md_vcf_sample_number):
                sample_data_list.append(md_vcf_data_dict['sample_list'][i].split(':'))
                sample_gt_list.append(sample_data_list[i][gt_position])
            if seq_id in tsi_list: xlib.Message.print('trace', f'sample_gt_list: {sample_gt_list}')

            # build the lists of the left and right side of sample genotypes of a variant
            sample_gt_left_list = []
            sample_sep_list = []
            sample_gt_right_list = []
            for i in range(md_vcf_sample_number):
                sep = '/'
                sep_pos = sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    sep = '|'
                    sep_pos = sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    raise xlib.ProgramException('', 'L008', 'GT', md_vcf_data_dict['chrom'], md_vcf_data_dict['pos'])
                sample_sep_list.append(sep)
                sample_gt_left_list.append(sample_gt_list[i][:sep_pos])
                sample_gt_right_list.append(sample_gt_list[i][sep_pos+1:])
            if variant_id in tsi_list: xlib.Message.print('trace', f'sample_gt_list: {sample_gt_list}')

            # get the list of imputed sample data
            imputed_sample_data_list = analysis_data_dict['sample_list']

            # set imputation in missing data
            for i in range(md_vcf_sample_number):
                if sample_gt_left_list[i] == xlib.get_md_symbol() or sample_gt_right_list[i] == xlib.get_md_symbol():
                    if imputed_sample_data_list[i] == '0':
                        sample_gt_left_list[i] = '0'
                        sample_gt_right_list[i] = '0'
                    elif imputed_sample_data_list[i] == '1':
                        sample_gt_left_list[i] = '0'
                        sample_gt_right_list[i] = '1'
                    elif imputed_sample_data_list[i] == '2':
                        sample_gt_left_list[i] = '1'
                        sample_gt_right_list[i] = '1'

            # rebuild the list of the field GT for every sample
            for i in range(md_vcf_sample_number):
                sample_gt_list[i] = f'{sample_gt_left_list[i]}{sample_sep_list[i]}{sample_gt_right_list[i]}'

            # rebuild the sample genotype data list and their corresponding record data
            sample_list = []
            for i in range(md_vcf_sample_number):
                sample_data_list[i][gt_position] = sample_gt_list[i]
                sample_list.append(':'.join(sample_data_list[i]))
            if variant_id in tsi_list: xlib.Message.print('trace', f'(17) sample_gt_list: {sample_gt_list}')

            # get the sample list as text
            sample_list_text = '\t'.join(sample_list)

            # write the variant record
            sample_list_text = '\t'.join(sample_list)
            imputed_vcf_file_id.write(f'{md_vcf_data_dict["chrom"]}\t{md_vcf_data_dict["pos"]}\t{md_vcf_data_dict["id"]}\t{md_vcf_data_dict["ref"]}\t{md_vcf_data_dict["alt"]}\t{md_vcf_data_dict["qual"]}\t{md_vcf_data_dict["filter"]}\t{md_vcf_data_dict["info"]}\t{md_vcf_data_dict["format"]}\t{sample_list_text}\n')

            # print the counters
            xlib.Message.print('verbose', f'\rmd_vcf_record_counter: {md_vcf_record_counter:6d} - md_vcf_variant_counter: {md_vcf_variant_counter:6d} - analysis_record_counter: {analysis_record_counter:6d} | analysis_variant_counter: {analysis_variant_counter:6d}')

            # read the next record of the VCF file with missing data
            (md_vcf_record, md_vcf_key, md_vcf_data_dict) = xlib.read_vcf_file(md_vcf_file_id, md_vcf_sample_number)

            # read the next record of the analysis file
            (analysis_record, analysis_key, analysis_data_dict) = read_analysis_file(analysis_file_id)

    xlib.Message.print('verbose', '\n')

    # close files
    md_vcf_file_id.close()
    imputed_vcf_file_id.close()

#-------------------------------------------------------------------------------

def read_analysis_file(analysis_file_id):
    '''
    Read a VCF file record.
    '''

    # initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read record
    record = analysis_file_id.readline()
    if record != '':

        # split the record data
        record_data_list = []
        start = 0
        for end in [i for i, chr in enumerate(record) if chr == '\t']:
            record_data_list.append(record[start:end].strip())
            start = end + 1
        record_data_list.append(record[start:].strip('\n').strip())

        # extract data from the record
        hyphen_pos = record_data_list[0].find('-')
        chrom = record_data_list[0][0:hyphen_pos].strip('"')
        pos = record_data_list[0][hyphen_pos+1:].strip('"')
        sample_list = []
        for i in range(len(record_data_list) - 1):
            sample_list.append(record_data_list[i + 1].strip('\n'))

        # set the key
        key = f'{chrom}-{int(pos):09d}'

        # get the record data dictionary
        data_dict = {'chrom': chrom, 'pos': pos, 'sample_list': sample_list}

    # if there is not any record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
