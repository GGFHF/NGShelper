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
This program treats the VCF output file of impute-adults.py, checks the genotype compatibility
between each mother and its progeny, and imputes missing data of progeny genotypes according
to the selected imputation scenario.
'''

#-------------------------------------------------------------------------------

import argparse
import gzip
import os
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

    # impute progenies in VCF file perviouly treated by impute-adults.py
    impute_progenies(args.input_vcf_file, args.sample_file, args.scenario, args.imputed_md_id, args.sp1_id, args.sp2_id, args.hybrid_id, args.output_vcf_file, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program treats the VCF output file of impute-adults.py, checks the genotype\n' \
        'compatibility between each mother and its progeny, and imputes missing data of progeny genotypes\n' \
        'according to the selected imputation scenario.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='input_vcf_file', help='Path of input VCF file (mandatory).')
    parser.add_argument('--samples', dest='sample_file', help='Path of the sample file in the following record format: "sample_id;species_id;mother_id" (mandatory).')
    parser.add_argument('--scenario', dest='scenario', help=f'Scenario (mandatory): {xlib.get_scenario_code_list_text()}.')
    parser.add_argument('--imd_id', dest='imputed_md_id', help=f'Identification of the alternative allele for imputed missing data; default {xlib.Const.DEFAULT_IMPUTED_MD_ID}')
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species (mandatory).')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--out', dest='output_vcf_file', help='Path of output VCF file (mandatory).')
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

    # check "input_vcf_file"
    if args.input_vcf_file is None:
        xlib.Message.print('error', '*** The VCF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.input_vcf_file):
        xlib.Message.print('error', f'*** The file {args.input_vcf_file} does not exist.')
        OK = False

    # check "sample_file"
    if args.sample_file is None:
        xlib.Message.print('error', '*** The sample file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.sample_file):
        xlib.Message.print('error', f'*** The file {args.sample_file} does not exist.')
        OK = False

    # check "scenario"
    if args.scenario is None:
        xlib.Message.print('error', '*** The scenario is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.scenario, xlib.get_scenario_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The scenario has to be {xlib.get_scenario_code_list_text()}.')
        OK = False

    # check "imputed_md_id"
    if args.imputed_md_id is None:
        args.imputed_md_id = xlib.Const.DEFAULT_IMPUTED_MD_ID

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

    # check "output_vcf_file"
    if args.output_vcf_file is None:
        xlib.Message.print('error', '*** The output VCF file is not indicated in the input arguments.')
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

    # check the identification set
    if OK:
        if args.sp1_id == args.sp2_id or \
           args.hybrid_id is not None and (args.sp1_id == args.hybrid_id or args.sp2_id == args.hybrid_id):
            xlib.Message.print('error', 'The identifications must be different.')
            OK = False

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def impute_progenies(input_vcf_file, sample_file, scenario, imputed_md_id, sp1_id, sp2_id, hybrid_id, output_vcf_file, tvi_list):
    '''
    Impute progenies in VCF file perviouly treated by impute-adults.py.
    '''

    # initialize the sample number
    sample_number = 0

    # get the sample data
    sample_dict = xlib.get_sample_data(sample_file, sp1_id, sp2_id, hybrid_id)

    # initialize the sample, species and mother identification lists per variant
    sample_id_list = []
    species_id_list = []
    mother_id_list = []

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
    (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    # while there are records in input VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # write the metadata record
            output_vcf_file_id.write(record)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Imputed variants ... {imputed_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # get the record data list
            record_data_list = data_dict['record_data_list']

            # build the sample species and mother identification lists per variant
            for i in range(9, len(record_data_list)):
                try:
                    sample_id = sample_dict[record_data_list[i]]['sample_id']
                    species_id = sample_dict[record_data_list[i]]['species_id']
                    mother_id = sample_dict[record_data_list[i]]['mother_id']
                except Exception as e:
                    raise xlib.ProgramException(e, 'L002', record_data_list[i])
                sample_id_list.append(sample_id)
                species_id_list.append(species_id)
                mother_id_list.append(mother_id)

            # check if the sample species list is empty
            if species_id_list == []:
                raise xlib.ProgramException('', 'L003')

            # set the sample number
            sample_number = len(species_id_list)

            # write the column description record
            output_vcf_file_id.write(record)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Imputed variants ... {imputed_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process variant record
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add set the variant identification
            variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'

            # add 1 to the read sequence counter
            input_record_counter += 1

            # add 1 to the total variant counter
            total_variant_counter += 1

            if variant_id in tvi_list: xlib.Message.print('trace', f'\n\n\n\nseq_id: {data_dict["chrom"]} - position {data_dict["pos"]}')

            # get the combined depth across samples (subfield DP) from field INFO
            info_field_list = data_dict['info'].upper().split(';')
            dp = -1
            for i in range(len(info_field_list)):
                if info_field_list[i].startswith('DP='):
                    try:
                        dp = int(info_field_list[i][3:])
                    except Exception as e:
                        raise xlib.ProgramException(e, 'L008', 'DP', data_dict['chrom'], data_dict['pos'])
                    break
            if dp == -1:
                raise xlib.ProgramException('', 'L007', 'DP', data_dict['chrom'], data_dict['pos'])

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
            if variant_id in tvi_list: xlib.Message.print('trace', f'sample_gt_list: {sample_gt_list}')

            if variant_id in tvi_list:
                literal = ' '
                for i in range(sample_number):
                    literal += f'{str(sample_gt_left_list[i])}{sample_sep_list[i]}{str(sample_gt_right_list[i])} '
                xlib.Message.print('trace', f'genotype list before imputation revision: {literal}')

            # initialize imputation control variable
            is_variant_imputed = False

            # impute depending on the genotype compatibility between the sample and its mother
            # A: any allele different to imputed (I) and missing data (M) ones
            # B: other allele different to A and imputed (I) and missing data (M) ones
            # *: a allele different to mother alleles and  missing data (M) one
            # **: a allele different to * and mother alleles and  missing data (M) one
            # #: any allele different to missing data (M) one
            # ##: any allele different to # and missing data (M) one
            # M (P): missing data allele
            # I (99): imputed allele
            for i in range(sample_number):

                # only when the sample is progeny
                if mother_id_list[i] != 'NONE':

                    # get the sample identification
                    sample_id = sample_id_list[i]

                    # get the index of the mother in lists
                    j = sample_id_list.index(mother_id_list[i])

                    # get the list of the mother distinct alleles
                    if sample_gt_left_list[j] == sample_gt_right_list[j]:
                        mother_gt_list = [sample_gt_left_list[j]]
                    else:
                        mother_gt_list = [sample_gt_left_list[j], sample_gt_right_list[j]]

                    # get the list of imputed and missing data alleles
                    M_I_list = [imputed_md_id, xlib.get_md_symbol()]

                    # get the list of mother distinct alleles plus missing data allele
                    mother_gt_plus_M_list = mother_gt_list + [xlib.get_md_symbol()]

                    # get the list of mother distinct alleles plus imputed and missing data alleles
                    # -- mother_gt_plus_M_I_list = mother_gt_list + M_I_list

                    # revision when the scenario is '0' (no imputation) or '2' (maximum possible imputation)
                    if scenario in ['0', '2']:

                        # mother alleles: A/A
                        if len(mother_gt_list) == 1 and imputed_md_id not in mother_gt_list and xlib.get_md_symbol() not in mother_gt_list:

                            # progeny alleles: A/# -> progeny alleles: A/#   OR   progeny alleles: #/A -> progeny alleles: #/A
                            if sample_gt_left_list[i] in mother_gt_list and sample_gt_right_list[i] != xlib.get_md_symbol() or \
                                sample_gt_left_list[i] != xlib.get_md_symbol() and sample_gt_right_list[i] in mother_gt_list:

                                pass

                            # progeny alleles: */* -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: */** -> progeny alleles: M/M
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list and \
                                sample_gt_right_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: M/M -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                pass

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # mother alleles: A/I
                        elif len(mother_gt_list) == 2 and imputed_md_id in mother_gt_list:

                            # progeny alleles: A/A -> progeny alleles: A/I
                            if sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] in mother_gt_list and sample_gt_left_list[i] != imputed_md_id:

                                sample_gt_right_list[i] = imputed_md_id
                                is_variant_imputed = True

                            # progeny alleles: A/* -> progeny alleles: A/*    OR   progeny alleles: */A -> progeny alleles: */A
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] != imputed_md_id and sample_gt_right_list[i] != imputed_md_id and \
                                (sample_gt_left_list[i] in mother_gt_list and sample_gt_right_list[i] not in mother_gt_list or \
                                 sample_gt_left_list[i] not in mother_gt_list and sample_gt_right_list[i] in mother_gt_list):

                                pass

                            # progeny alleles: */* -> progeny alleles: */I
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list:

                                sample_gt_right_list[i] = imputed_md_id
                                is_variant_imputed = True

                            # progeny alleles: */** -> progeny alleles: M/M
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list and \
                                sample_gt_right_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: M/M -> progeny alleles: I/I
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                sample_gt_left_list[i] = imputed_md_id
                                sample_gt_right_list[i] = imputed_md_id
                                is_variant_imputed = True

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # mother alleles: A/B
                        elif len(mother_gt_list) == 2 and imputed_md_id not in mother_gt_list and xlib.get_md_symbol() not in mother_gt_list:

                            # progeny alleles: A/# -> progeny alleles: A/#   OR   progeny alleles: #/A -> progeny alleles: #/A   OR
                            # progeny alleles: B/# -> progeny alleles: B/#   OR   progeny alleles: #/B -> progeny alleles: #/B
                            if sample_gt_left_list[i] in mother_gt_list and sample_gt_right_list[i] != xlib.get_md_symbol() or \
                                sample_gt_left_list[i] != xlib.get_md_symbol() and sample_gt_right_list[i] in mother_gt_list:

                                pass

                            # progeny alleles: */* -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: */** -> progeny alleles: M/M
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list and \
                                sample_gt_right_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: M/M -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                pass

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # mother alleles: I/I
                        elif len(mother_gt_list) == 1 and imputed_md_id in mother_gt_list:

                            # progeny alleles: A/A -> progeny alleles: A/I
                            if sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in M_I_list:

                                sample_gt_right_list[i] = imputed_md_id
                                is_variant_imputed = True

                            # progeny alleles: A/B -> progeny alleles: M/M
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in M_I_list and \
                                sample_gt_right_list[i] not in M_I_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: M/M -> progeny alleles: I/I
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                sample_gt_left_list[i] = imputed_md_id
                                sample_gt_right_list[i] = imputed_md_id
                                is_variant_imputed = True

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # mother alleles: M/M
                        elif len(mother_gt_list) == 1 and xlib.get_md_symbol() in mother_gt_list:

                            # progeny alleles: */* -> progeny alleles: */*
                            if sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] != xlib.get_md_symbol():

                                pass

                            # progeny alleles: */** -> progeny alleles: */**
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i]  != xlib.get_md_symbol() and \
                                sample_gt_right_list[i]  != xlib.get_md_symbol():

                                pass

                            # progeny alleles: M/M -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                pass

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # in any other mother alleles
                        else:

                            raise xlib.ProgramException('', 'L009', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                    # revision when the scenario is '1' (standard)
                    elif scenario == '1':

                        # mother alleles: A/A
                        if len(mother_gt_list) == 1 and imputed_md_id not in mother_gt_list and xlib.get_md_symbol() not in mother_gt_list:

                            # progeny alleles: A/# -> progeny alleles: A/#   OR   progeny alleles: #/A -> progeny alleles: #/A
                            if sample_gt_left_list[i] in mother_gt_list and sample_gt_right_list[i] != xlib.get_md_symbol() or \
                                sample_gt_left_list[i] != xlib.get_md_symbol() and sample_gt_right_list[i] in mother_gt_list:

                                pass

                            # progeny alleles: */* -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: */** -> progeny alleles: M/M
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list and \
                                sample_gt_right_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: M/M -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                pass

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # mother alleles: A/B
                        elif len(mother_gt_list) == 2 and imputed_md_id not in mother_gt_list and xlib.get_md_symbol() not in mother_gt_list:

                            # progeny alleles: A/# -> progeny alleles: A/#   OR   progeny alleles: #/A -> progeny alleles: #/A   OR
                            # progeny alleles: B/# -> progeny alleles: B/#   OR   progeny alleles: #/B -> progeny alleles: #/B
                            if sample_gt_left_list[i] in mother_gt_list and sample_gt_right_list[i] != xlib.get_md_symbol() or \
                                sample_gt_left_list[i] != xlib.get_md_symbol() and sample_gt_right_list[i] in mother_gt_list:

                                pass

                            # progeny alleles: */* -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: */** -> progeny alleles: M/M
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list and \
                                sample_gt_right_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: M/M -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                pass

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # mother alleles: I/I
                        elif len(mother_gt_list) == 1 and imputed_md_id in mother_gt_list:

                            # progeny alleles: #/# -> progeny alleles: #/I
                            if sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] != xlib.get_md_symbol():

                                sample_gt_right_list[i] = imputed_md_id
                                is_variant_imputed = True

                            # progeny alleles: #/## -> progeny alleles: M/M
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] != xlib.get_md_symbol() and \
                                sample_gt_right_list[i] != xlib.get_md_symbol():

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: M/M -> progeny alleles: I/I
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                sample_gt_left_list[i] = imputed_md_id
                                sample_gt_right_list[i] = imputed_md_id
                                is_variant_imputed = True

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # mother alleles: M/M
                        elif len(mother_gt_list) == 1 and xlib.get_md_symbol() in mother_gt_list:

                            # progeny alleles: */* -> progeny alleles: */*
                            if sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] != xlib.get_md_symbol():

                                pass

                            # progeny alleles: */** -> progeny alleles: */**
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i]  != xlib.get_md_symbol() and \
                                sample_gt_right_list[i]  != xlib.get_md_symbol():

                                pass

                            # progeny alleles: M/M -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                pass

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # in any other mother alleles
                        else:

                            raise xlib.ProgramException('', 'L009', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                    # revision when the scenario is '3' (maximum possible missing data)
                    elif scenario == '3':

                        # mother alleles: A/A
                        if len(mother_gt_list) == 1 and imputed_md_id not in mother_gt_list and xlib.get_md_symbol() not in mother_gt_list:

                            # progeny alleles: A/# -> progeny alleles: A/#   OR   progeny alleles: #/A -> progeny alleles: #/A
                            if sample_gt_left_list[i] in mother_gt_list and sample_gt_right_list[i] != xlib.get_md_symbol() or \
                                sample_gt_left_list[i] != xlib.get_md_symbol() and sample_gt_right_list[i] in mother_gt_list:

                                pass

                            # progeny alleles: */* -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: */** -> progeny alleles: M/M
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list and \
                                sample_gt_right_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: M/M -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                pass

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # mother alleles: A/M
                        elif len(mother_gt_list) == 2 and xlib.get_md_symbol() in mother_gt_list:

                            # progeny alleles: A/A -> progeny alleles: A/M
                            if sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] in mother_gt_list and sample_gt_left_list[i] != imputed_md_id:

                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: A/* -> progeny alleles: A/*    OR   progeny alleles: */A -> progeny alleles: */A
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in M_I_list and sample_gt_right_list[i] not in M_I_list and \
                                (sample_gt_left_list[i] in mother_gt_list and sample_gt_right_list[i] not in mother_gt_list or \
                                 sample_gt_left_list[i] not in mother_gt_list and sample_gt_right_list[i] in mother_gt_list):

                                pass

                            # progeny alleles: */* -> progeny alleles: */M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list:

                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: */** -> progeny alleles: M/M
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list and \
                                sample_gt_right_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: M/M -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                pass

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # mother alleles: A/B
                        elif len(mother_gt_list) == 2 and imputed_md_id not in mother_gt_list and xlib.get_md_symbol() not in mother_gt_list:

                            # progeny alleles: A/# -> progeny alleles: A/#   OR   progeny alleles: #/A -> progeny alleles: #/A   OR
                            # progeny alleles: B/# -> progeny alleles: B/#   OR   progeny alleles: #/B -> progeny alleles: #/B
                            if sample_gt_left_list[i] in mother_gt_list and sample_gt_right_list[i] != xlib.get_md_symbol() or \
                                sample_gt_left_list[i] != xlib.get_md_symbol() and sample_gt_right_list[i] in mother_gt_list:

                                pass

                            # progeny alleles: */* -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: */** -> progeny alleles: M/M
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in mother_gt_plus_M_list and \
                                sample_gt_right_list[i] not in mother_gt_plus_M_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: M/M -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                pass

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # mother alleles: I/I
                        elif len(mother_gt_list) == 1 and imputed_md_id in mother_gt_list:

                            # progeny alleles: A/A -> progeny alleles: A/I
                            if sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in M_I_list:

                                sample_gt_right_list[i] = imputed_md_id
                                is_variant_imputed = True

                            # progeny alleles: A/B -> progeny alleles: M/M
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i] not in M_I_list and \
                                sample_gt_right_list[i] not in M_I_list:

                                sample_gt_left_list[i] = xlib.get_md_symbol()
                                sample_gt_right_list[i] = xlib.get_md_symbol()
                                is_variant_imputed = True

                            # progeny alleles: M/M -> progeny alleles: I/I
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                sample_gt_left_list[i] = imputed_md_id
                                sample_gt_right_list[i] = imputed_md_id
                                is_variant_imputed = True

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # mother alleles: M/M
                        elif len(mother_gt_list) == 1 and xlib.get_md_symbol() in mother_gt_list:

                            # progeny alleles: */* -> progeny alleles: */*
                            if sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] != xlib.get_md_symbol():

                                pass

                            # progeny alleles: */** -> progeny alleles: */**
                            elif sample_gt_left_list[i] != sample_gt_right_list[i] and \
                                sample_gt_left_list[i]  != xlib.get_md_symbol() and \
                                sample_gt_right_list[i]  != xlib.get_md_symbol():

                                pass

                            # progeny alleles: M/M -> progeny alleles: M/M
                            elif sample_gt_left_list[i] == sample_gt_right_list[i] and \
                                sample_gt_left_list[i] == xlib.get_md_symbol():

                                pass

                            # in any other progeny alleles
                            else:

                                raise xlib.ProgramException('', 'L010', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

                        # in any other mother alleles
                        else:

                            raise xlib.ProgramException('', 'L009', data_dict['chrom'], data_dict['pos'], sample_id, scenario, ','.join(mother_gt_list), sample_gt_list[i])

            # add 1 to the imputed variant counter
            if is_variant_imputed == True:
                imputed_variant_counter += 1

            if variant_id in tvi_list:
                literal = ' '
                for i in range(sample_number):
                    literal += f'{str(sample_gt_left_list[i])}{sample_sep_list[i]}{str(sample_gt_right_list[i])} '
                xlib.Message.print('trace', f' genotype list after imputation revision: {literal}')

            # rebuild the list of the field GT for every sample
            for i in range(sample_number):
                sample_gt_list[i] = f'{sample_gt_left_list[i]}{sample_sep_list[i]}{sample_gt_right_list[i]}'

            # rebuild the sample genotype data list and their corresponding record data
            sample_list = []
            for i in range(sample_number):
                sample_data_list[gt_position] = sample_gt_list[i]
                sample_list.append(':'.join(sample_data_list))
            if variant_id in tvi_list: xlib.Message.print('trace', f'(17) sample_gt_list: {sample_gt_list}')

            # write the variant record
            sample_list_text = '\t'.join(sample_list)
            output_vcf_file_id.write(f'{data_dict["chrom"]}\t{data_dict["pos"]}\t{data_dict["id"]}\t{data_dict["ref"]}\t{data_dict["alt"]}\t{data_dict["qual"]}\t{data_dict["filter"]}\t{data_dict["info"]}\t{data_dict["format"]}\t{sample_list_text}\n')

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Imputed variants ... {imputed_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    xlib.Message.print('verbose', '\n')

    # close files
    input_vcf_file_id.close()
    output_vcf_file_id.close()

    # print OK message 
    xlib.Message.print('info', f'The file {os.path.basename(output_vcf_file)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
