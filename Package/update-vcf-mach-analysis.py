#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program updates the missing data in a VCF file with the results of an
analysis performed using MACH

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

    # updates the missing data in a VCF file with the results of an analysis performed using MACH
    update_vcf_with_mach_analysis(args.md_vcf_file, args.imputed_vcf_file, args.analysis_file, args.variant_file, args.tsi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program updates the missing data in a VCF file with the results of an analysis\n' \
        'performed using MACH.\n'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--mdvcffile', dest='md_vcf_file', help='Path of the VCF file wih missing data (mandatory).')
    parser.add_argument('--impvcffile', dest='imputed_vcf_file', help='Path of the output VCF file with imputed data (mandatory).')
    parser.add_argument('--analfile', dest='analysis_file', help='Path of file with the analysis performed with MACH (mandatory).')
    parser.add_argument('--varfile', dest='variant_file', help='Path of file with variant list (mandatory).')
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
        xlib.Message.print('error', '*** The file with the analysis performed with MACH is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.analysis_file):
        xlib.Message.print('error', f'*** The file {args.analysis_file} does not exist.')
        OK = False

    # check "variant_file"
    if args.variant_file is None:
        xlib.Message.print('error', '*** The file with variant list is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.variant_file):
        xlib.Message.print('error', f'*** The file {args.variant_file} does not exist.')
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
        args.tsi_list = xlib.split_literal_to_text_list(args.tsi_list)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def update_vcf_with_mach_analysis(md_vcf_file, imputed_vcf_file, analysis_file, variant_file, tsi_list):
    '''
    Update the missing data in a VCF file with the results of an analysis performed using MACH.
    '''

    # get the variant identification list of the analysis
    analysis_variant_id_list = get_variant_id_list(variant_file)

    # get the genotype data of the analysis
    (analysis_sample_list, allele_matrix) = get_genotype_data(analysis_file)

    # initialize the sample number in the VCF file with missing data
    md_vcf_sample_number = 0

    # initialize the sample information list from the VCF file with missing data
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

    # read the first record of VCF file with  missing data
    (md_vcf_record, _, md_vcf_data_dict) = xlib.read_vcf_file(md_vcf_file_id, md_vcf_sample_number)

    # while there are records in the VCF file with missing data
    while md_vcf_record != '':

        # process metadata records in the original VCF file with missing data
        while md_vcf_record != '' and md_vcf_record.startswith('##'):

            # add 1 to the record counter
            md_vcf_record_counter += 1

            # write the metadata record
            imputed_vcf_file_id.write(md_vcf_record)

            # print the counters
            xlib.Message.print('verbose', f'\rmd_vcf_record_counter: {md_vcf_record_counter:6d} - md_vcf_variant_counter: {md_vcf_variant_counter:6d}')

            # read the next record of the VCF file with missing data
            (md_vcf_record, _, md_vcf_data_dict) = xlib.read_vcf_file(md_vcf_file_id, md_vcf_sample_number)

        # process the column description record in the original VCF file with missing data
        if md_vcf_record.startswith('#CHROM'):

            # add 1 to the record counter
            md_vcf_record_counter += 1

            # get the record data list
            md_vcf_data_list = md_vcf_data_dict['record_data_list']

            # set the sample number and sample information list
            md_vcf_sample_number = len(md_vcf_data_list) - 9
            md_vcf_sample_list = md_vcf_data_list[9:]

            # check the two sample lists (the order of the samples may change)
            # -- if md_vcf_sample_list != analysis_sample_list:
            if len(md_vcf_sample_list) != len(analysis_sample_list):
                print(f'\nmd_vcf_sample_list:\n{md_vcf_sample_list}')
                print(f'analysis_sample_list:\n{analysis_sample_list}')
                raise xlib.ProgramException('', 'L018', md_vcf_file, analysis_file)

            # write the column description record
            imputed_vcf_file_id.write(md_vcf_record)

            # print the counters
            xlib.Message.print('verbose', f'\rmd_vcf_record_counter: {md_vcf_record_counter:6d} - md_vcf_variant_counter: {md_vcf_variant_counter:6d}')

            # read the next record of the VCF file with missing data
            (md_vcf_record, _, md_vcf_data_dict) = xlib.read_vcf_file(md_vcf_file_id, md_vcf_sample_number)

        # process variant record from the VCF file with missing data
        while md_vcf_record != '' and not md_vcf_record.startswith('##') and not md_vcf_record.startswith('#CHROM'):

            # add 1 to the record counters
            md_vcf_record_counter += 1

            # add 1 to the variant counter
            md_vcf_variant_counter += 1

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

            # get the position of the variant identification in the variant identification list of the analysis
            variant_pos = analysis_variant_id_list.index(variant_id)

            # get the analysis genotype list
            (analysis_gt_left_list, analysis_gt_right_list) = get_analysis_gt_lists(allele_matrix, variant_pos, reference_bases, alternative_allele_list, len(analysis_sample_list))

            # set imputation in missing data (the order of the samples may change)
            for i in range(md_vcf_sample_number):
                if sample_gt_left_list[i] == xlib.get_md_symbol() or sample_gt_right_list[i] == xlib.get_md_symbol():
                    # -- sample_gt_left_list[i] = analysis_gt_left_list[i]
                    # -- sample_gt_right_list[i] = analysis_gt_right_list[i]
                    current_sample = md_vcf_sample_list[i]
                    j = analysis_sample_list.index(current_sample)
                    sample_gt_left_list[i] = analysis_gt_left_list[j]
                    sample_gt_right_list[i] = analysis_gt_right_list[j]

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
            xlib.Message.print('verbose', f'\rmd_vcf_record_counter: {md_vcf_record_counter:6d} - md_vcf_variant_counter: {md_vcf_variant_counter:6d}')

            # read the next record of the VCF file with missing data
            (md_vcf_record, _, md_vcf_data_dict) = xlib.read_vcf_file(md_vcf_file_id, md_vcf_sample_number)

    xlib.Message.print('verbose', '\n')

    # close files
    md_vcf_file_id.close()
    imputed_vcf_file_id.close()

#-------------------------------------------------------------------------------

def get_genotype_data(analysis_file):
    '''
    Get the genotype data (sample identification list and genotype matrix).
    '''

    # initialize the sample identification list
    sample_id_list = []

    # initialize the allele matrix (rows: samples (two row per sample); columns: variants)
    allele_matrix = []
    col_number = 0

    # open the analysis file
    if analysis_file.endswith('.gz'):
        try:
            analysis_file_id = gzip.open(analysis_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', analysis_file)
    else:
        try:
            analysis_file_id = open(analysis_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', analysis_file)

    # initialize analysis record counter
    analysis_record_counter = 0

    # read first record
    record = analysis_file_id.readline()

    # while there are records in the analysis file
    while record != '':

        # add 1 to the analysis record counter
        analysis_record_counter += 1

        # split the record data
        record_data_list = []
        start = 0
        for end in [i for i, chr in enumerate(record) if chr == ' ']:
            record_data_list.append(record[start:end].strip())
            start = end + 1
        record_data_list.append(record[start:].strip('\n').strip())

        # check if there are 3 data
        if len(record_data_list) != 3:
            raise xlib.ProgramException('', 'L014')

        # add the sample identification to the list
        if analysis_record_counter % 2 != 0:
            greater_than_pos =  record_data_list[0].find('>')
            sample_id = record_data_list[0][:greater_than_pos - 1]
            sample_id_list.append(sample_id)

        # get the allele list
        allele_list = list(record_data_list[2])

        # set and verify the column number
        if col_number == 0:
            col_number = len(allele_list)
        elif col_number != len(allele_list):
            raise xlib.ProgramException('', 'L014')

        # append allele list to allele matrix
        allele_matrix.append(allele_list)

        # print the input record counter
        xlib.Message.print('verbose', f'\rProcessed analysis records ... {analysis_record_counter:8d}')

        # read next record
        record = analysis_file_id.readline()

    # close the analysis file
    analysis_file_id.close()

    # return the sample identification list and allele matrix
    return sample_id_list, allele_matrix

#-------------------------------------------------------------------------------

def get_variant_id_list(variant_file):
    '''
    Get the variant identification list.
    '''

    # initialize the variant identification list
    variant_id_list = []

    # open the variant file
    if variant_file.endswith('.gz'):
        try:
            variant_file_id = gzip.open(variant_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', variant_file)
    else:
        try:
            variant_file_id = open(variant_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', variant_file)

    # initialize variant record counter
    variant_record_counter = 0

    # read first record
    record = variant_file_id.readline()

    # while there are records in the variant file
    while record != '':

        # add 1 to the variant record counter
        variant_record_counter += 1

        # get the variant identification
        variant_id = record[2:].strip('\n').strip()

        # remove leading zeros of position
        hyphen_pos = variant_id.find('-')
        seq_id = variant_id[:hyphen_pos]
        position = variant_id[hyphen_pos + 1:]
        variant_id = f'{seq_id}-{position.lstrip("0")}'

        # add the variant identification to list
        variant_id_list.append(variant_id)

        # print the input record counter
        xlib.Message.print('verbose', f'\rProcessed variant records ... {variant_record_counter:8d}')

        # read next record
        record = variant_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close the variant file
    variant_file_id.close()

    # return the variant identification list
    return variant_id_list

#-------------------------------------------------------------------------------

def get_analysis_gt_lists(allele_matrix, variant_pos, reference_bases, alternative_allele_list, sample_number):
    '''
    Get the genotype list of a varint from the analysis data.
    '''

    # initialize the analysis genotype lists
    analysis_gt_left_list = []
    analysis_gt_right_list = []

    # build the analysis genotype list
    for i in range(sample_number):

        # the first allele
        allele_base_1 = allele_matrix[i * 2][variant_pos]
        if allele_base_1.upper() == reference_bases:
            allele_1 = '0'
        elif allele_base_1.upper() == alternative_allele_list[0]:
            allele_1 = '1'
        else:
            allele_1 = '*'

        # the second allele
        allele_base_2 = allele_matrix[i * 2 + 1][variant_pos]
        if allele_base_2.upper() == reference_bases:
            allele_2 = '0'
        elif allele_base_2.upper() == alternative_allele_list[0]:
            allele_2 = '1'
        else:
            allele_2 = '*'

        # sort the alleles
        allele_list = sorted([allele_1, allele_2])

        # add genotype to list
        analysis_gt_left_list.append(f'{allele_list[0]}')
        analysis_gt_right_list.append(f'{allele_list[1]}')

    # return the analysis genotype list
    return analysis_gt_left_list, analysis_gt_right_list

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
