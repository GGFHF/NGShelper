#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

'''
This software has been developed by:

    GI Sistemas Naturales e Historia Forestal (formerly known as GI Genetica, Fisiologia e Historia Forestal)
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

'''
This program converts a VCF file to the PHASE input format.
'''

#-------------------------------------------------------------------------------

import argparse
import gzip
import os
import re
import sys

import xlib

#-------------------------------------------------------------------------------

def main(argv):
    '''
    Main line of the program.
    '''

    # check the operating system
    xlib.check_os()

    # get and check the arguments
    parser = build_parser()
    args = parser.parse_args()
    check_args(args)

    # convert the VCF file to the PHASE input format
    if args.variant_file == 'NONE':
        convert_vcf_to_phase_input_1(args.vcf_file, args.sample_file, args.sp1_id, args.sp2_id, args.hybrid_id, args.imputed_md_id, args.allele_transformation, args.output_dir, args.tvi_list)
    else:
        variant_dict = get_variant_dict(args.variant_file)
        convert_vcf_to_phase_input_2(args.vcf_file, variant_dict, args.sample_file, args.sp1_id, args.sp2_id, args.hybrid_id, args.imputed_md_id, args.allele_transformation, args.output_dir, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program converts a VCF file to the PHASE input format.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='vcf_file', help='Path of the VCF file (mandatory).')
    parser.add_argument('--variants', dest='variant_file', help='Path of the variant file with record format "seq_id, position, gene_fragment" or NONE; default: NONE.')
    parser.add_argument('--samples', dest='sample_file', help='Path of the sample file with record format "sample_id;species_id;mother_id" (mandatory).')
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species (mandatory).')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--imd_id', dest='imputed_md_id', help=f'Identification of the alternative allele for imputed missing data; default {xlib.Const.DEFAULT_IMPUTED_MD_ID}')
    parser.add_argument('--trans', dest='allele_transformation', help=f'Transformation of the allele symbol: {xlib.get_allele_transformation_code_list_text()}; default: NONE.')
    parser.add_argument('--outdir', dest='output_dir', help='Path of output directoty where files for PHASE application are saved (mandatory).')
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

    # check "variant_file"
    if args.variant_file is None or args.variant_file.upper() == 'NONE':
        args.variant_file = 'NONE'
    elif not os.path.isfile(args.variant_file):
        xlib.Message.print('error', f'*** The file {args.variant_file} does not exist.')
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

    # check "allele_transformation"
    if args.allele_transformation is None:
        args.allele_transformation = 'NONE'
    elif not xlib.check_code(args.allele_transformation, xlib.get_allele_transformation_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The allele transformation has to be {xlib.get_allele_transformation_code_list_text()}.')
        OK = False
    else:
        args.allele_transformation = args.allele_transformation.upper()

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

    # check "tvi_list"
    if args.tvi_list is None or args.tvi_list == 'NONE':
        args.tvi_list = []
    else:
        args.tvi_list = xlib.split_literal_to_string_list(args.tvi_list)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def convert_vcf_to_phase_input_1(vcf_file, sample_file, sp1_id, sp2_id, hybrid_id, imputed_md_id, allele_transformation, output_dir, tvi_list):
    '''
    Convert a VCF file to the PHASE input format.
    '''

    # initialize the sample number
    sample_number = 0

    # initialize the sample information list
    sample_info_list = []

    # get the sample data
    sample_dict = xlib.get_sample_data(sample_file, sp1_id, sp2_id, hybrid_id)

    # initialize the sample species identification list per variant
    species_id_list = []

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
    seq_counter = 0
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
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Seqs ... {seq_counter:8d} - Variants ... {variant_counter:8d}')

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

            # build the sample species list
            for i in range(9, len(record_data_list)):
                try:
                    species_id = sample_dict[record_data_list[i]]['species_id']
                except Exception as e:
                    raise xlib.ProgramException(e, 'L002', record_data_list[i])
                species_id_list.append(species_id)

            # check if the sample species list is empty
            if species_id_list == []:
                raise xlib.ProgramException('', 'L003')

            # set the sample number
            sample_number = len(species_id_list)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Seqs ... {seq_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record of the VCF file
            (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

        # process variant records
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add set the variant identification
            variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'

            # add 1 to the sequence counter
            seq_counter += 1

            # initialize VCF record counter
            variant_counter = 0

            # save the sequence
            old_seq = data_dict['chrom']

            # initialize the list of variant positions
            variant_position_list = []

            # initialize the matrices (rows: variants; columns: samples) on left and right sides of genotypes
            gt_left_matrix = []
            gt_right_matrix = []

            # initialize the list of the variant multiallelic status
            variant_multiallelic_status_list = []

            # process variant records of the same sequence
            while record != '' and not record.startswith('##') and not record.startswith('#CHROM') and data_dict['chrom'] == old_seq:

                # add 1 to the VCF record counter
                record_counter += 1

                # add 1 to the total variant counter
                variant_counter += 1

                # append position to the list of variant positions
                variant_position_list.append(data_dict['pos'])

                # get the position of the genotype (subfield GT) in the field FORMAT
                format_subfield_list = data_dict['format'].upper().split(':')
                try:
                    gt_position = format_subfield_list.index('GT')
                except Exception as e:
                    raise xlib.ProgramException(e, 'L007', 'GT', data_dict['chrom'], data_dict['pos'])

                # build the list of sample genotypes of a variant
                sample_gt_list = []
                for i in range(sample_number):
                    sample_data_list = data_dict['sample_list'][i].split(':')
                    sample_gt_list.append(sample_data_list[gt_position])
                if variant_id in tvi_list: xlib.Message.print('trace', f'sample_gt_list: {sample_gt_list}')

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

                # get the allele counters per species
                allele_counter_dict = {}
                for i in range(sample_number):
                    if sample_gt_left_list[i] != xlib.get_md_symbol():
                        allele_counter_dict[sample_gt_left_list[i]] = allele_counter_dict.get(sample_gt_left_list[i], 0) + 1
                    if sample_gt_right_list[i] != xlib.get_md_symbol():
                        allele_counter_dict[sample_gt_right_list[i]] = allele_counter_dict.get(sample_gt_right_list[i], 0) + 1
                if variant_id in tvi_list: xlib.Message.print('trace', f'allele_counter_dict: {allele_counter_dict}')

                # check if the variant is multiallelic
                if len(allele_counter_dict.keys()) > 2:
                    variant_multiallelic_status = 'M'
                else:
                    variant_multiallelic_status = 'S'
                if variant_id in tvi_list: xlib.Message.print('trace', f'variant_multiallelic_status: {variant_multiallelic_status}.')

                # append a row to the matrices (rows: variant; columns: samples) of left and right sides of genotypes
                gt_left_matrix.append(sample_gt_left_list)
                gt_right_matrix.append(sample_gt_right_list)

                # append to the list of the variant multiallelic status
                variant_multiallelic_status_list.append(variant_multiallelic_status)

                # print the counters
                xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Seqs ... {seq_counter:8d} - Variants ... {variant_counter:8d}')

                # read the next record of the VCF file
                (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

            # set output converted file of the sequence
            if vcf_file.endswith('.gz'):
                (file_name, _) = os.path.splitext(os.path.basename(vcf_file[:-3]))
            else:
                (file_name, _) = os.path.splitext(os.path.basename(vcf_file))
            seq_output_converted_file = f'{output_dir}/{file_name}-2phase-{old_seq}.txt'

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
                    if gt_left_matrix[j][i] == '.' and variant_multiallelic_status_list[j] == 'S':
                        allele_left = '?'
                    elif gt_left_matrix[j][i] == '.' and variant_multiallelic_status_list[j] == 'M':
                        allele_left = '-1'
                    elif xlib.check_int(gt_left_matrix[j][i]) and allele_transformation == 'ADD100':
                        allele_left = str(int(gt_left_matrix[j][i]) + 100)
                    else:
                        allele_left = gt_left_matrix[j][i]
                    sample_variant_gt_left_list.append(allele_left)
                    # right
                    if gt_right_matrix[j][i] == '.' and variant_multiallelic_status_list[j] == 'S':
                        allele_right = '?'
                    elif gt_right_matrix[j][i] == '.' and variant_multiallelic_status_list[j] == 'M':
                        allele_right = '-1'
                    elif xlib.check_int(gt_right_matrix[j][i]) and allele_transformation == 'ADD100':
                        allele_right = str(int(gt_right_matrix[j][i]) + 100)
                    else:
                        allele_right = gt_right_matrix[j][i]
                    sample_variant_gt_right_list.append(allele_right)

                # write the first record of the sample
                sample_record_1 = f'#{sample_info_list[i][0]}\n'
                seq_output_converted_file_id.write(sample_record_1)

                # write the second record of the sample
                sample_record_2 = f'{" ".join(sample_variant_gt_left_list)}\n'
                seq_output_converted_file_id.write(sample_record_2)

                # write the third record of the sample
                sample_record_3 = f'{" ".join(sample_variant_gt_right_list)}\n'
                seq_output_converted_file_id.write(sample_record_3)

            # close file
            seq_output_converted_file_id.close()

            xlib.Message.print('verbose', '\n')

            # print OK message 
            xlib.Message.print('info', f'The converted file {os.path.basename(seq_output_converted_file)} is created.')

    # close VCF file
    vcf_file_id.close()

#-------------------------------------------------------------------------------

def convert_vcf_to_phase_input_2(vcf_file, variant_dict, sample_file, sp1_id, sp2_id, hybrid_id, imputed_md_id, allele_transformation, output_dir, tvi_list):
    '''
    Convert a VCF file to the PHASE input format.
    '''

    xlib.Message.print('trace', f'variant_dict: {variant_dict}')

    # initialize the sample number
    sample_number = 0

    # initialize the sample information list
    sample_info_list = []

    # get the sample data
    sample_dict = xlib.get_sample_data(sample_file, sp1_id, sp2_id, hybrid_id)

    # initialize the sample species identification list per variant
    species_id_list = []

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
    gene_fragment_counter = 0
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
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Genes/fragments ... {gene_fragment_counter:8d} - Variants ... {variant_counter:8d}')

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

            # build the sample species list
            for i in range(9, len(record_data_list)):
                try:
                    species_id = sample_dict[record_data_list[i]]['species_id']
                except Exception as e:
                    raise xlib.ProgramException(e, 'L002', record_data_list[i])
                species_id_list.append(species_id)

            # check if the sample species list is empty
            if species_id_list == []:
                raise xlib.ProgramException('', 'L003')

            # set the sample number
            sample_number = len(species_id_list)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Genes/fragments ... {gene_fragment_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record of the VCF file
            (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

        # process variant records
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add 1 to the gene/fragment counter
            gene_fragment_counter += 1

            # initialize VCF record counter
            variant_counter = 0

            # save the gene/fragment
            old_gene_fragment = variant_dict[f'{data_dict["chrom"]}-{data_dict["pos"]}']

            # initialize the list of variant positions
            variant_position_list = []

            # initialize the matrices (rows: variants; columns: samples) on left and right sides of genotypes
            gt_left_matrix = []
            gt_right_matrix = []

            # initialize the list of the variant multiallelic status
            variant_multiallelic_status_list = []

            # process variant records of the same gene/fragment
            while record != '' and not record.startswith('##') and not record.startswith('#CHROM') and variant_dict[f'{data_dict["chrom"]}-{data_dict["pos"]}'] == old_gene_fragment:

                # add 1 to the VCF record counter
                record_counter += 1

                # add 1 to the total variant counter
                variant_counter += 1

                # set the variant identification
                variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'

                # append position to the list of variant positions
                variant_position_list.append(data_dict['pos'])

                # get the position of the genotype (subfield GT) in the field FORMAT
                format_subfield_list = data_dict['format'].upper().split(':')
                try:
                    gt_position = format_subfield_list.index('GT')
                except Exception as e:
                    raise xlib.ProgramException(e, 'L007', 'GT', data_dict['chrom'], data_dict['pos'])

                # build the list of sample genotypes of a variant
                sample_gt_list = []
                for i in range(sample_number):
                    sample_data_list = data_dict['sample_list'][i].split(':')
                    sample_gt_list.append(sample_data_list[gt_position])
                if variant_id in tvi_list: xlib.Message.print('trace', f'sample_gt_list: {sample_gt_list}')

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

                # get the allele counters per species
                allele_counter_dict = {}
                for i in range(sample_number):
                    if sample_gt_left_list[i] != xlib.get_md_symbol():
                        allele_counter_dict[sample_gt_left_list[i]] = allele_counter_dict.get(sample_gt_left_list[i], 0) + 1
                    if sample_gt_right_list[i] != xlib.get_md_symbol():
                        allele_counter_dict[sample_gt_right_list[i]] = allele_counter_dict.get(sample_gt_right_list[i], 0) + 1
                if variant_id in tvi_list: xlib.Message.print('trace', f'allele_counter_dict: {allele_counter_dict}')

                # check if the variant is multiallelic
                if len(allele_counter_dict.keys()) > 2:
                    variant_multiallelic_status = 'M'
                else:
                    variant_multiallelic_status = 'S'
                if variant_id in tvi_list: xlib.Message.print('trace', f'variant_multiallelic_status: {variant_multiallelic_status}.')

                # append a row to the matrices (rows: variant; columns: samples) of left and right sides of genotypes
                gt_left_matrix.append(sample_gt_left_list)
                gt_right_matrix.append(sample_gt_right_list)

                # append to the list of the variant multiallelic status
                variant_multiallelic_status_list.append(variant_multiallelic_status)

                # print the counters
                xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Genes/fragments ... {gene_fragment_counter:8d} - Variants ... {variant_counter:8d}')

                # read the next record of the VCF file
                (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

            # set output converted file of the sequence
            if vcf_file.endswith('.gz'):
                (file_name, _) = os.path.splitext(os.path.basename(vcf_file[:-3]))
            else:
                (file_name, _) = os.path.splitext(os.path.basename(vcf_file))
            seq_output_converted_file = f'{output_dir}/{file_name}-2phase-{old_gene_fragment}.txt'

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
                    if gt_left_matrix[j][i] == '.' and variant_multiallelic_status_list[j] == 'S':
                        allele_left = '?'
                    elif gt_left_matrix[j][i] == '.' and variant_multiallelic_status_list[j] == 'M':
                        allele_left = '-1'
                    elif xlib.check_int(gt_left_matrix[j][i]) and allele_transformation == 'ADD100':
                        allele_left = str(int(gt_left_matrix[j][i]) + 100)
                    else:
                        allele_left = gt_left_matrix[j][i]
                    sample_variant_gt_left_list.append(allele_left)
                    # right
                    if gt_right_matrix[j][i] == '.' and variant_multiallelic_status_list[j] == 'S':
                        allele_right = '?'
                    elif gt_right_matrix[j][i] == '.' and variant_multiallelic_status_list[j] == 'M':
                        allele_right = '-1'
                    elif xlib.check_int(gt_right_matrix[j][i]) and allele_transformation == 'ADD100':
                        allele_right = str(int(gt_right_matrix[j][i]) + 100)
                    else:
                        allele_right = gt_right_matrix[j][i]
                    sample_variant_gt_right_list.append(allele_right)

                # write the first record of the sample
                sample_record_1 = f'#{sample_info_list[i][0]}\n'
                seq_output_converted_file_id.write(sample_record_1)

                # write the second record of the sample
                sample_record_2 = f'{" ".join(sample_variant_gt_left_list)}\n'
                seq_output_converted_file_id.write(sample_record_2)

                # write the third record of the sample
                sample_record_3 = f'{" ".join(sample_variant_gt_right_list)}\n'
                seq_output_converted_file_id.write(sample_record_3)

            # close file
            seq_output_converted_file_id.close()

            xlib.Message.print('verbose', '\n')

            # print OK message 
            xlib.Message.print('info', f'The converted file {os.path.basename(seq_output_converted_file)} is created.')

    # close VCF file
    vcf_file_id.close()

#-------------------------------------------------------------------------------

def get_variant_dict(variant_file):
    '''
    '''

    # initialize the sequence dictionary
    variant_dict = xlib.NestedDefaultDict()

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

    # initialize the record counter
    record_counter = 0

    # read the first record
    record = variant_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # extract variant data
        # record format: "seq_id";"position";"gene/fragment"
        data_list = []
        begin = 0
        for end in [i for i, chr in enumerate(record) if chr == ';']:
            data_list.append(record[begin:end].strip('"'))
            begin = end + 1
        data_list.append(record[begin:].strip('\n').strip('"'))
        try:
            seq_id = data_list[0]
            position = data_list[1]
            gene_fragment = data_list[2]
        except Exception as e:
            raise xlib.ProgramException('F006', os.path.basename(variant_file), record_counter)

        # add variant to the dictionary
        variant_id = f'{seq_id}-{position}'
        variant_dict[variant_id] = gene_fragment

        # print record counter
        xlib.Message.print('verbose', f'\rProcessed records of {os.path.basename(variant_file)}: {record_counter}')

        # read the next record
        record = variant_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close variant file
    variant_file_id.close()

    # return the variant dictionary
    return variant_dict

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
