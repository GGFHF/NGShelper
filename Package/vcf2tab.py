#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program converts a VCF file to a file in tabular format.

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

    # convert the VCF file to a file in tabular format
    convert_vcf_to_tab(args.vcf_file, args.tab_file, args.md_characters, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program converts a VCF file to a file in tabular format.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--vcf', dest='vcf_file', help='Path of the input VCF file (mandatory).')
    parser.add_argument('--tab', dest='tab_file', help='Path of the output file in tabular format (mandatory).')
    parser.add_argument('--mdc', dest='md_characters', help='Characters representing missing data (mandatory).')
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

    # check "vcf_file"
    if args.vcf_file is None:
        xlib.Message.print('error', '*** The input VCF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.vcf_file):
        xlib.Message.print('error', f'*** The file {args.vcf_file} does not exist.')
        OK = False

    # check "tab_file"
    if args.tab_file is None:
        xlib.Message.print('error', '*** The output file in tabular format is not indicated in the input arguments.')
        OK = False

    # check "md_characters"
    if args.md_characters is None:
        xlib.Message.print('error', '*** Characters representing missing data are not indicated in the input arguments.')
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

def convert_vcf_to_tab(vcf_file, tab_file, md_characters, tvi_list):
    '''
    Converts a VCF file to a file in tabular.
    '''

    # initialize the variant identification list
    variant_id_list = []

    # initialize the matrices (rows: variants; columns: samples) on left and right sides of genotypes
    gt_left_matrix = []
    gt_right_matrix = []

    # open the VCF file
    if vcf_file.endswith('.gz'):
        try:
            vcf_file_id = gzip.open(vcf_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', vcf_file)
    else:
        try:
            vcf_file_id = open(vcf_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', vcf_file)

    # initialize counters
    record_counter = 0
    variant_counter = 0

    # read the first record of VCF file
    (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number=0, check_sample_number=False)

    # while there are records in the VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the VCF record counter
            record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record of the VCF file
            (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number=0, check_sample_number=False)

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the VCF record counter
            record_counter += 1

            # get the sample list
            sample_list = record.strip().split('\t')[9:]

            # get the sample number
            sample_number = len(sample_list)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record of the VCF file
            (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number=0, check_sample_number=False)

        # process variant records
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add 1 to the VCF record counter
            record_counter += 1

            # add 1 to the variant counter
            variant_counter += 1

            # set the variant identification and append it to the variant identification list
            variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'
            variant_id_list.append(variant_id)

            # get the reference bases (field REF) and alternative alleles (field ALT)
            reference_bases = data_dict['ref']
            alternative_alleles = data_dict['alt']

            # build the alternative alleles list from field ALT
            alternative_allele_list = alternative_alleles.split(',')

            # check if the variant has more than one alternative allele
            if len(alternative_allele_list) > 1:
                raise xlib.ProgramException('', 'L021', variant_id) from None

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
            if variant_id in tvi_list: xlib.Message.print('trace', f'(4) sample_gt_list: {sample_gt_list}')

            # build the lists of the left and right side of sample genotypes of a variant
            sample_gt_left_list = []
            sample_gt_right_list = []
            for i in range(sample_number):
                sep = '/'
                sep_pos = sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    sep = '|'
                    sep_pos = sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    raise xlib.ProgramException('', 'L008', 'GT', data_dict['chrom'], data_dict['pos'])
                try:
                    # left
                    sample_gt_left = sample_gt_list[i][:sep_pos]
                    if sample_gt_left == xlib.get_md_symbol():
                        sample_gt_left_list.append(md_characters)
                    elif sample_gt_left == '0':
                        sample_gt_left_list.append(reference_bases)
                    else:
                        sample_gt_left_list.append(alternative_allele_list[0])
                    # right
                    sample_gt_right = sample_gt_list[i][sep_pos+1:]
                    if sample_gt_right == xlib.get_md_symbol():
                        sample_gt_right_list.append(md_characters)
                    elif sample_gt_right == '0':
                        sample_gt_right_list.append(reference_bases)
                    else:
                        sample_gt_right_list.append(alternative_allele_list[0])
                except Exception as e:
                    raise xlib.ProgramException(e, 'L008', 'GT', data_dict['chrom'], data_dict['pos'])

            # append a row to the matrices (rows: variant; columns: samples) of left and right sides of genotypes
            gt_left_matrix.append(sample_gt_left_list)
            gt_right_matrix.append(sample_gt_right_list)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record of the VCF file
            (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number=0, check_sample_number=False)

    xlib.Message.print('verbose', '\n')

    # close the VCF file
    vcf_file_id.close()

    # open the output file in tabular format
    if tab_file.endswith('.gz'):
        try:
            tab_file_id = gzip.open(tab_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', tab_file)
    else:
        try:
            tab_file_id = open(tab_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', tab_file)

    # write header record
    variant_id_list_text = '\t'.join(variant_id_list)
    tab_file_id.write(f'ID/SNP\t{variant_id_list_text}\n')

    # write sample records
    for i in range(sample_number):

        # build left and right side lists of variants of a sample
        sample_variant_gt_list = []
        for j in range(len(gt_left_matrix)):    #pylint: disable=consider-using-enumerate
            sample_variant_gt_list.append(f'{gt_left_matrix[j][i]}\t{gt_right_matrix[j][i]}')

        # write the sample record
        sample_variant_gt_left_list_text = '\t'.join(sample_variant_gt_list)
        tab_file_id.write(f'{sample_list[i]}\t{sample_variant_gt_left_list_text}\n')

    # close file
    tab_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The converted file {os.path.basename(tab_file)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
