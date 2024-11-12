#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program converts a VCF file to the Structure input formats.

This software has been developed by:

    GI en Especies Leñosas (WooSp)
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

    # convert the VCF file
    convert_vcf_to_structure(args.vcf_file, args.sample_file, args.sp1_id, args.sp2_id, args.hybrid_id, args.imputed_md_id, args.new_md_id, args.allele_transformation, args.structure_input_format, args.output_converted_file, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program converts a VCF file to the Structure input formats.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='vcf_file', help='Path of the VCF file (mandatory).')
    parser.add_argument('--samples', dest='sample_file', help='Path of the sample file in the following record format: "sample_id;species_id;mother_id" (mandatory).')
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species (mandatory).')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--imd_id', dest='imputed_md_id', help=f'Identification of the alternative allele for imputed missing data; default {xlib.Const.DEFAULT_IMPUTED_MD_ID}')
    parser.add_argument('--new_mdi', dest='new_md_id', help=f'New identification of missing data which will replace "."); default: {xlib.Const.DEFAULT_NEW_MD_ID}.')
    parser.add_argument('--trans', dest='allele_transformation', help=f'Transformation of the allele symbol: {xlib.get_allele_transformation_code_list_text()}; default: NONE.')
    parser.add_argument('--out', dest='output_converted_file', help='Path of the converted file (mandatory).')
    parser.add_argument('--format', dest='structure_input_format', help=f'Structure file format (mandatory): {xlib.get_structure_input_format_code_list_text()}.')
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
        xlib.Message.print('error', '*** The VCF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.vcf_file):
        xlib.Message.print('error', f'*** The file {args.vcf_file} does not exist.')
        OK = False

    # check "sample_file"
    if args.sample_file is None:
        xlib.Message.print('error', '*** The sample file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.sample_file):
        xlib.Message.print('error', f'*** The file {args.sample_file} does not exist.')
        OK = False

    # check "sp1_id"
    if args.sp1_id is None:
        xlib.Message.print('error', '*** The identification of the first species is not indicated the input arguments.')
        OK = False

    # check "sp2_id"
    if args.sp2_id is None:
        xlib.Message.print('error', '*** The identification of the second species is not indicated in the input arguments.')
        OK = False

    # check "hybrid_id"
    if args.hybrid_id is None:
        args.hybrid_id = 'NONE'

    # check "imputed_md_id"
    if args.imputed_md_id is None:
        args.imputed_md_id = xlib.Const.DEFAULT_IMPUTED_MD_ID

    # check "new_md_id"
    if args.new_md_id is None:
        args.new_md_id = xlib.Const.DEFAULT_NEW_MD_ID

    # check "allele_transformation"
    if args.allele_transformation is None:
        args.allele_transformation = 'NONE'
    elif not xlib.check_code(args.allele_transformation, xlib.get_allele_transformation_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The allele transformation has to be {xlib.get_allele_transformation_code_list_text()}.')
        OK = False
    else:
        args.allele_transformation = args.allele_transformation.upper()

    # check "output_converted_file"
    if args.output_converted_file is None:
        xlib.Message.print('error', '*** The converted file is not indicated in the input arguments.')
        OK = False

    # check "structure_input_format"
    if args.structure_input_format is None:
        xlib.Message.print('error', '*** The Structure input format is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.structure_input_format, xlib.get_structure_input_format_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The Structure input format has to be {xlib.get_structure_input_format_code_list_text()}.')
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

def convert_vcf_to_structure(vcf_file, sample_file, sp1_id, sp2_id, hybrid_id, imputed_md_id, new_md_id, allele_transformation, structure_input_format, output_converted_file, tvi_list):
    '''
    Convert a VCF file to the Structure input formats.
    '''

    # initialize the sample number
    sample_number = 0

    # initialize the sample information list
    sample_info_list = []

    # initialize the variant code list
    variant_code_list = []

    # initialize the matrices (rows: variants; columns: samples) on left and right sides of genotypes
    gt_left_matrix = []
    gt_right_matrix = []

    # get the sample data
    sample_dict = xlib.get_sample_data(sample_file, sp1_id, sp2_id, hybrid_id)

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
    (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

    # while there are records in the VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the VCF record counter
            record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record of the VCF file
            (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the VCF record counter
            record_counter += 1

            # get the record data list
            record_data_list = data_dict['record_data_list']

            # build the sample information list
            for i in range(9, len(record_data_list)):
                try:
                    species_id = sample_dict[record_data_list[i]]['species_id']
                except Exception as e:
                    raise xlib.ProgramException(e, 'L002', record_data_list[i])
                if species_id == sp1_id:
                    numeric_species_id = 1
                elif species_id == sp2_id:
                    numeric_species_id = 2
                else:
                    numeric_species_id = 3
                sample_info_list.append([record_data_list[i], numeric_species_id])

            # check if the sample information list is empty
            if sample_info_list == []:
                raise xlib.ProgramException('', 'L003')

            # set the sample number
            sample_number = len(sample_info_list)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record of the VCF file
            (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

        # process variant records
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add set the variant identification
            variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'

            # add 1 to the VCF record counter
            record_counter += 1

            # add 1 to the variant counter
            variant_counter += 1

            # append variant code to the variant code list and write the code and its sequence identification and position in the variant file
            id = f'{data_dict["chrom"]}-{data_dict["pos"]}'
            variant_code_list.append(id)

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
                    if sample_gt_list[i][:sep_pos] == xlib.get_md_symbol():
                        sample_gt_left_list.append(new_md_id)
                    else:
                        sample_gt_left_list.append(sample_gt_list[i][:sep_pos])
                    if sample_gt_list[i][sep_pos+1:] == xlib.get_md_symbol():
                        sample_gt_right_list.append(new_md_id)
                    else:
                        sample_gt_right_list.append(sample_gt_list[i][sep_pos+1:])
                except Exception as e:
                    raise xlib.ProgramException(e, 'L008', 'GT', data_dict['chrom'], data_dict['pos'])

            # append a row to the matrices (rows: variant; columns: samples) of left and right sides of genotypes
            gt_left_matrix.append(sample_gt_left_list)
            gt_right_matrix.append(sample_gt_right_list)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record of the VCF file
            (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

    xlib.Message.print('verbose', '\n')

    # close the VCF file
    vcf_file_id.close()

    # review the imputed missing data when the type of the converted file is 2
    if structure_input_format == '2':

        # detect variants with any imputed missing data
        excluded_variant_index_list = []
        for i in range(len(gt_left_matrix)):
            for j in range(sample_number):
                if gt_left_matrix[i][j] == imputed_md_id or gt_right_matrix[i][j] == imputed_md_id:
                    excluded_variant_index_list.append(i)
                    break
        xlib.Message.print('trace', 'excluded_variant_index_list: {}'.format(excluded_variant_index_list))

        # remove data of variants with any imputed missing data
        excluded_variant_index_list.reverse()
        for k in excluded_variant_index_list:
            variant_code_list.pop(k)
            gt_left_matrix.pop(k)
            gt_right_matrix.pop(k)

    # open the output converted file
    if output_converted_file.endswith('.gz'):
        try:
            output_converted_file_id = gzip.open(output_converted_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_converted_file)
    else:
        try:
            output_converted_file_id = open(output_converted_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_converted_file)

    # write header record
    variant_code_list_text = '\t'.join(variant_code_list)
    output_converted_file_id.write(f'sample_id\tspecies_id\t{variant_code_list_text}\n')

    # write sample records
    for i in range(sample_number):

        # build left and right side lists of variants of a sample
        sample_variant_gt_left_list = []
        sample_variant_gt_right_list = []
        for j in range(len(gt_left_matrix)):
            # left
            if xlib.check_int(gt_left_matrix[j][i]) and allele_transformation == 'ADD100':
                allele_left = str(int(gt_left_matrix[j][i]) + 100)
            else:
                allele_left = gt_left_matrix[j][i]
            sample_variant_gt_left_list.append(allele_left)
            # right
            if xlib.check_int(gt_right_matrix[j][i]) and allele_transformation == 'ADD100':
                allele_right = str(int(gt_right_matrix[j][i]) + 100)
            else:
                allele_right = gt_right_matrix[j][i]
            sample_variant_gt_right_list.append(allele_right)

        # write the first record of the sample
        sample_variant_gt_left_list_text = '\t'.join(sample_variant_gt_left_list)
        output_converted_file_id.write(f'{sample_info_list[i][0]}\t{sample_info_list[i][1]}\t{sample_variant_gt_left_list_text}\n')
        # -- output_converted_file_id.write(f'{sample_info_list[i][0]};{sample_info_list[i][1]};{";".join(sample_variant_gt_left_list)}\n')

        # write the second record of the sample
        sample_variant_gt_right_list_text = '\t'.join(sample_variant_gt_right_list)
        output_converted_file_id.write(f'{sample_info_list[i][0]}\t{sample_info_list[i][1]}\t{sample_variant_gt_right_list_text}\n')
        # -- output_converted_file_id.write(f'{sample_info_list[i][0]};{sample_info_list[i][1]};{";".join(sample_variant_gt_right_list)}\n')

    # close file
    output_converted_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The converted file {os.path.basename(output_converted_file)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
