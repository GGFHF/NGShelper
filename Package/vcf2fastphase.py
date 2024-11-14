#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program converts a VCF file to the fastPHASE input format.

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

    # convert the VCF file to the fastPHASE input format
    convert_vcf_to_fastphase_input(args.vcf_file, args.output_dir, args.tsi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program converts a VCF file to the fastPHASE input format.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--vcf', dest='vcf_file', help='Path of the VCF file (mandatory).')
    parser.add_argument('--outdir', dest='output_dir', help='Path of output directoty where files for fastPHASE application are saved (mandatory).')
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

    # check "vcf_file"
    if args.vcf_file is None:
        xlib.Message.print('error', '*** The variant file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.vcf_file):
        xlib.Message.print('error', f'*** The file {args.vcf_file} does not exist.')
        OK = False

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

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def convert_vcf_to_fastphase_input(vcf_file, output_dir, tsi_list):
    '''
    Convert a VCF file to the fastPHASE input format.
    '''

    # initialize the sample number
    sample_number = 0

    # initialize the sample information list
    sample_info_list = []

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
    seq_id_counter = 0
    variant_counter = 0
    record_counter = 0

    # read the first record of VCF file
    (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

    # while there are records in the VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the VCF record counter
            record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Seq ids ... {seq_id_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record of the VCF file
            (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the VCF record counter
            record_counter += 1

            # get the record data list
            record_data_list = data_dict['record_data_list']

            # set the sample number and sample information list
            sample_number = len(record_data_list) - 9
            sample_info_list = record_data_list[9:]

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Seq ids ... {seq_id_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record of the VCF file
            (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

        # process variant records
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add 1 to the sequence identification counter
            seq_id_counter += 1

            # initialize VCF record counter
            variant_counter = 0

            # save the sequence identification
            old_seq_id = data_dict['chrom']

            # initialize the list of variant positions
            variant_position_list = []

            # initialize the matrix of allele codes (rows: variants; columns: allele code list of each variant)
            allele_code_matrix = []

            # initialize the matrices on left and right sides of genotypes  (rows: variants; columns: samples)
            gtseq_left_matrix = []
            gtseq_right_matrix = []

            # initialize the list of the variant multiallelic status
            variant_multiallelic_status_list = []

            # process variant records of the same sequence identification
            while record != '' and not record.startswith('##') and not record.startswith('#CHROM') and data_dict['chrom'] == old_seq_id:

                # set the current sequence identification
                seq_id = data_dict['chrom']

                # add 1 to the VCF record counter
                record_counter += 1

                # add 1 to the total variant counter
                variant_counter += 1

                # set the variant identification
                variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'
                if seq_id in tsi_list: xlib.Message.print('trace', f'\n\n\nnvariant_id: {variant_id}')

                # append position to the list of variant positions
                variant_position_list.append(data_dict['pos'])
                if seq_id in tsi_list: xlib.Message.print('trace', f'variant_position_list: {variant_position_list}')

                # get the reference bases (field REF) and alternative alleles (field ALT)
                reference_bases = data_dict['ref']
                alternative_alleles = data_dict['alt']
                if seq_id in tsi_list: xlib.Message.print('trace', f'reference_bases: {reference_bases}')
                if seq_id in tsi_list: xlib.Message.print('trace', f'alternative_alleles: {alternative_alleles}')

                # build the alternative allele list
                alternative_allele_list = alternative_alleles.split(',')
                if seq_id in tsi_list: xlib.Message.print('trace', f'alternative_allele_list: {alternative_allele_list}')

                # build the complete allele list
                complete_allele_list = [reference_bases] + alternative_allele_list
                if seq_id in tsi_list: xlib.Message.print('trace', f'complete_allele_list: {complete_allele_list}')

                # build the allele code list
                allele_code_list = ['A', 'T', 'C', 'G']
                for i in range(len(complete_allele_list)):
                    if len(complete_allele_list[i]) > 1 and complete_allele_list[i] != xlib.get_md_symbol():
                        allele_code_list.append(complete_allele_list[i].upper())
                if seq_id in tsi_list: xlib.Message.print('trace', f'allele_code_list: {allele_code_list}')
                allele_code_matrix.append(allele_code_list)

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
                if seq_id in tsi_list: xlib.Message.print('trace', f'sample_gt_list: {sample_gt_list}')

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
                    sample_gt_left_list.append(sample_gt_list[i][:sep_pos])
                    sample_gt_right_list.append(sample_gt_list[i][sep_pos+1:])

                # change the numeric identification of genotypes to its sequence
                sample_gtseq_left_list = []
                sample_gtseq_right_list = []
                for i in range(sample_number):
                    if sample_gt_left_list[i] != xlib.get_md_symbol() and sample_gt_left_list[i]:
                        sample_gtseq_left_list.append(complete_allele_list[int(sample_gt_left_list[i])].upper())
                    else:
                        sample_gtseq_left_list.append(sample_gt_left_list[i])
                    if sample_gt_right_list[i] != xlib.get_md_symbol() and sample_gt_right_list[i]:
                        sample_gtseq_right_list.append(complete_allele_list[int(sample_gt_right_list[i])].upper())
                    else:
                        sample_gtseq_right_list.append(sample_gt_right_list[i])

                # get the allele counters per species
                allele_counter_dict = {}
                for i in range(sample_number):
                    allele_counter_dict[sample_gtseq_left_list[i]] = allele_counter_dict.get(sample_gtseq_left_list[i], 0) + 1
                    allele_counter_dict[sample_gtseq_right_list[i]] = allele_counter_dict.get(sample_gtseq_right_list[i], 0) + 1
                if seq_id in tsi_list: xlib.Message.print('trace', f'allele_counter_dict: {allele_counter_dict}')

                # check if the variant is multiallelic
                allele_counter = 0
                for allele in allele_counter_dict:
                    if allele != xlib.get_md_symbol():
                        allele_counter += 1
                if allele_counter > 2:
                    variant_multiallelic_status = 'M'
                else:
                    variant_multiallelic_status = 'S'
                if seq_id in tsi_list: xlib.Message.print('trace', f'variant_multiallelic_status: {variant_multiallelic_status}')

                # append a row to the matrices (rows: variant; columns: samples) of left and right sides of genotypes using genotype sequences
                gtseq_left_matrix.append(sample_gtseq_left_list)
                gtseq_right_matrix.append(sample_gtseq_right_list)

                # append to the list of the variant multiallelic status
                variant_multiallelic_status_list.append(variant_multiallelic_status)

                # print the counters
                xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Seq ids ... {seq_id_counter:8d} - Variants ... {variant_counter:8d}')

                # read the next record of the VCF file
                (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

            # set output converted file of the sequence
            if vcf_file.endswith('.gz'):
                (file_name, _) = os.path.splitext(os.path.basename(vcf_file[:-3]))
            else:
                (file_name, _) = os.path.splitext(os.path.basename(vcf_file))
            seq_output_converted_file = f'{output_dir}/{file_name}-2fastphase-{old_seq_id}.txt'
            if seq_id in tsi_list: xlib.Message.print('trace', f'\n\n\nseq_output_converted_file: {seq_output_converted_file}')

            # open the output converted file
            if seq_output_converted_file.endswith('.gz'):
                try:
                    seq_output_converted_file_id = gzip.open(seq_output_converted_file, mode='wt', encoding='iso-8859-1', newline='\n')
                except Exception as e:
                    raise xlib.ProgramException(e, 'F004', seq_output_converted_file)
            else:
                try:
                    seq_output_converted_file_id = open(seq_output_converted_file, mode='w', encoding='iso-8859-1', newline='\n')
                except Exception as e:
                    raise xlib.ProgramException(e, 'F003', seq_output_converted_file)

            # order variant position list
            # -- variant_position_list.sort(key=int)

            # write header records
            header_record_1 = f'{sample_number}\n'
            seq_output_converted_file_id.write(header_record_1)
            header_record_2 = f'{len(variant_position_list)}\n'
            seq_output_converted_file_id.write(header_record_2)
            header_record_3 = f'P {" ".join(variant_position_list)}\n'
            seq_output_converted_file_id.write(header_record_3)
            header_record_4 = f'{"".join(variant_multiallelic_status_list)}\n'
            seq_output_converted_file_id.write(header_record_4)

            # write sample records
            for i in range(sample_number):

                # build left and right side lists of variants of a sample
                sample_variant_gt_left_list = []
                sample_variant_gt_right_list = []
                for j in range(len(variant_position_list)):
                    # left
                    if seq_id in tsi_list: xlib.Message.print('trace', f'gtseq_left_matrix[j][i]: {gtseq_left_matrix[j][i]}')
                    if gtseq_left_matrix[j][i] == xlib.get_md_symbol() and variant_multiallelic_status_list[j] == 'S':
                        allele_left = '?'
                    elif gtseq_left_matrix[j][i] == xlib.get_md_symbol() and variant_multiallelic_status_list[j] == 'M':
                        allele_left = '-1'
                    else:
                        try:
                            allele_left = f'{allele_code_matrix[j].index(gtseq_left_matrix[j][i]) + 1}'
                            if seq_id in tsi_list: xlib.Message.print('trace', f'allele_left: {allele_left}')
                        except Exception as e:
                            allele_left = '60'
                    if seq_id in tsi_list: xlib.Message.print('trace', f'allele_left: {allele_left}')
                    sample_variant_gt_left_list.append(allele_left)
                    # right
                    if seq_id in tsi_list: xlib.Message.print('trace', f'gtseq_right_matrix[j][i]: {gtseq_right_matrix[j][i]}')
                    if gtseq_right_matrix[j][i] == xlib.get_md_symbol() and variant_multiallelic_status_list[j] == 'S':
                        allele_right = '?'
                    elif gtseq_right_matrix[j][i] == xlib.get_md_symbol() and variant_multiallelic_status_list[j] == 'M':
                        allele_right = '-1'
                    else:
                        try:
                            allele_right = f'{allele_code_matrix[j].index(gtseq_right_matrix[j][i]) + 1}'
                            if seq_id in tsi_list: xlib.Message.print('trace', f'allele_right: {allele_right}')
                        except Exception as e:
                            allele_right = '60'
                    if seq_id in tsi_list: xlib.Message.print('trace', f'allele_right: {allele_right}')
                    sample_variant_gt_right_list.append(allele_right)
                if seq_id in tsi_list: xlib.Message.print('trace', f'sample_variant_gt_left_list: {sample_variant_gt_left_list}')
                if seq_id in tsi_list: xlib.Message.print('trace', f'sample_variant_gt_right_list: {sample_variant_gt_right_list}')

                # write the first record of the sample
                sample_record_1 = f'#{sample_info_list[i]}\n'
                seq_output_converted_file_id.write(sample_record_1)
                if seq_id in tsi_list: xlib.Message.print('trace', f'sample_record_1: {sample_record_1}'.replace('\n', ''))

                # write the second record of the sample
                sample_record_2 = f'{" ".join(sample_variant_gt_left_list)}\n'
                seq_output_converted_file_id.write(sample_record_2)
                if seq_id in tsi_list: xlib.Message.print('trace', f'sample_record_2: {sample_record_2}'.replace('\n', ''))

                # write the third record of the sample
                sample_record_3 = f'{" ".join(sample_variant_gt_right_list)}\n'
                seq_output_converted_file_id.write(sample_record_3)
                if seq_id in tsi_list: xlib.Message.print('trace', f'sample_record_3: {sample_record_3}'.replace('\n', ''))

            # close file
            seq_output_converted_file_id.close()

            xlib.Message.print('verbose', '\n')

            # print OK message
            xlib.Message.print('info', f'The converted file {os.path.basename(seq_output_converted_file)} is created.')

    # close VCF file
    vcf_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
