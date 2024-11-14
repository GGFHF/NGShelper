#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program imputes genotypes with missing data of adult individuals in a VCF file generated in a
hybridization studies of two parental species, hybrids and their half-sib progenies, based on the
relative frequencies of missing data in the adults of both parental species.

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

    # imputate adults
    impute_adults(args.input_vcf_file, args.sample_file, args.fix, args.scenario, args.min_aa_percentage, args.min_md_imputation_percentage, args.imputed_md_id, args.sp1_id, args.sp1_max_md_percentage, args.sp2_id, args.sp2_max_md_percentage, args.hybrid_id, args.min_afr_percentage, args.min_depth, args.output_vcf_file, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program imputes genotypes with missing data of adult individuals in a VCF\n' \
        'file generated in a hybridization studies of two parental species, hybrids and their half-sib\n' \
        'progenies, based on the relative frequencies of missing data in the adults of both parental\n' \
        'species.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='input_vcf_file', help='Path of input VCF file (mandatory).')
    parser.add_argument('--samples', dest='sample_file', help='Path of the sample file in the following record format: "sample_id;species_id;mother_id" (mandatory).')
    parser.add_argument('--fix', dest='fix', help=f'Fix the reference base(s) when there are not samples with this reference (mandatory): {xlib.get_fix_code_list_text()}.')
    parser.add_argument('--scenario', dest='scenario', help=f'Scenario (mandatory): {xlib.get_scenario_code_list_text()}.')
    parser.add_argument('--min_aa', dest='min_aa_percentage', help='Minimum percentage of alternative alleles per species (mandatory).')
    parser.add_argument('--min_mdi', dest='min_md_imputation_percentage', help='Minimum percentage of missing data imputation to a new alternative allele per species (mandatory).')
    parser.add_argument('--imd_id', dest='imputed_md_id', help=f'Identification of the alternative allele for imputed missing data; default {xlib.Const.DEFAULT_IMPUTED_MD_ID}')
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp1_max_md', dest='sp1_max_md_percentage', help='Maximum percentage of missing data of the first species (mandatory).')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species (mandatory).')
    parser.add_argument('--sp2_max_md', dest='sp2_max_md_percentage', help='Maximum percentage of missing data of the second species (mandatory).')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--maf', dest='min_afr_percentage', help='Minimum percentage of allele frequency per species (mandatory).')
    parser.add_argument('--dp', dest='min_depth', help=f'Minimum combined depth across samples; default: {xlib.Const.DEFAULT_MIN_DEPTH}.')
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

    # check "fix"
    if args.fix is None:
        xlib.Message.print('error', '*** Fix is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.fix, xlib.get_fix_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** fix has to be {xlib.get_fix_code_list_text()}.')
        OK = False
    else:
        args.fix = args.fix.upper()

    # check "scenario"
    if args.scenario is None:
        xlib.Message.print('error', '*** The scenario is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.scenario, xlib.get_scenario_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The scenario has to be {xlib.get_scenario_code_list_text()}.')
        OK = False

    # check "min_aa_percentage"
    if args.min_aa_percentage is None:
        xlib.Message.print('error', '*** The minimum percent of alternative alleles per species is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.min_aa_percentage, minimum=0.0, maximum=100.0):
        xlib.Message.print('error', 'The minimum percent of alternative alleles per species has to be a float number between 0.0 and 100.0.')
        OK = False
    else:
        args.min_aa_percentage = float(args.min_aa_percentage)

    # check "min_md_imputation_percentage"
    if args.min_md_imputation_percentage is None:
        xlib.Message.print('error', '*** The minimum percentage of missing data imputation to a new alternative allele per species is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.min_md_imputation_percentage, minimum=0.0, maximum=100.0):
        xlib.Message.print('error', 'The minimum percentage of missing data imputation to a new alternative allele per species has to be a float number between 0.0 and 100.0.')
        OK = False
    else:
        args.min_md_imputation_percentage = float(args.min_md_imputation_percentage)

    # check "imputed_md_id"
    if args.imputed_md_id is None:
        args.imputed_md_id = xlib.Const.DEFAULT_IMPUTED_MD_ID

    # check "sp1_id"
    if args.sp1_id is None:
        xlib.Message.print('error', '*** The identification of the first species is not indicated in the input arguments.')
        OK = False

    # check "sp1_max_md_percentage"
    if args.sp1_max_md_percentage is None:
        xlib.Message.print('error', '*** The maximum percentage of missing data of the first species is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.sp1_max_md_percentage, minimum=0.0, maximum=100.0):
        xlib.Message.print('error', 'The maximum percentage of missing data of the first species has to be a float number between 0.0 and 100.0.')
        OK = False
    else:
        args.sp1_max_md_percentage = float(args.sp1_max_md_percentage)

    # check "sp2_id"
    if args.sp2_id is None:
        xlib.Message.print('error', '*** The identification of the second species is not indicated in the input arguments.')
        OK = False

    # check "sp2_max_md_percentage"
    if args.sp2_max_md_percentage is None:
        xlib.Message.print('error', '*** The maximum percentage of missing data of the second species is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.sp2_max_md_percentage, minimum=0.0, maximum=100.0):
        xlib.Message.print('error', 'The maximum percentage of missing data of the second species has to be a float number between 0.0 and 100.0.')
        OK = False
    else:
        args.sp2_max_md_percentage = float(args.sp2_max_md_percentage)

    # check "hybrid_id"
    if args.hybrid_id is None:
        args.hybrid_id = 'NONE'

    # check "min_afr_percentage"
    if args.min_afr_percentage is None:
        xlib.Message.print('error', '*** The minimum percentage of allele frequency per species is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.min_afr_percentage, minimum=0.0, maximum=100.0):
        xlib.Message.print('error', 'The minimum percentage of allele frequency per species has to be a float number between 0.0 and 100.0.')
        OK = False
    else:
        args.min_afr_percentage = float(args.min_afr_percentage)

    # check "min_depth"
    if args.min_depth is None:
        args.min_depth = xlib.Const.DEFAULT_MIN_DEPTH
    elif not xlib.check_int(args.min_depth, minimum=1):
        xlib.Message.print('error', 'The minimum combined depth across samples has to be an integer number greater than  or equal to 1.')
        OK = False
    else:
        args.min_depth = int(args.min_depth)

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

def impute_adults(input_vcf_file, sample_file, fix, scenario, min_aa_percentage, min_md_imputation_percentage, imputed_md_id, sp1_id, sp1_max_md_percentage, sp2_id, sp2_max_md_percentage, hybrid_id, min_afr_percentage, min_depth, output_vcf_file, tvi_list):
    '''
    Filter and fixes variant data of a VCF file.
    '''

    # initialize the sample number
    sample_number = 0

    # get the sample data
    sample_dict = xlib.get_sample_data(sample_file, sp1_id, sp2_id, hybrid_id)

    # calculate the adult individual number of both species and hybrids
    adult_num_1 = 0
    adult_num_2 = 0
    adult_num_h = 0
    for _, value in sample_dict.items():
        if value['mother_id'] == 'NONE':
            if value['species_id'] == sp1_id:
                adult_num_1 += 1
            elif value['species_id'] == sp2_id:
                adult_num_2 += 1
            else:
                adult_num_h += 1
    xlib.Message.print('verbose', f'{sp1_id} adults: {adult_num_1} - {sp2_id} adults: {adult_num_2} - hybrid adults: {adult_num_h}\n')

    # initialize the sample species and mother identification lists per variant
    species_id_list = []
    mother_id_list = []

    # initialize the non-filtered sequence identification list
    non_filtered_seq_id_list = []

    # set the temporal VCF file
    temporal_vcf_file = f'{output_vcf_file}.tmp'

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

    # open the temporal VCF file
    if temporal_vcf_file.endswith('.gz'):
        try:
            temporal_vcf_file_id = gzip.open(temporal_vcf_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', temporal_vcf_file)
    else:
        try:
            temporal_vcf_file_id = open(temporal_vcf_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', temporal_vcf_file)

    # initialize counters
    input_record_counter = 0
    total_variant_counter = 0
    filtered_variant_counter = 0

    # read the first record of input VCF file
    (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    # while there are records in input VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # write the metadata record
            temporal_vcf_file_id.write(record)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Filtered variants ... {filtered_variant_counter:8d}')

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
                    species_id = sample_dict[record_data_list[i]]['species_id']
                    mother_id = sample_dict[record_data_list[i]]['mother_id']
                except Exception as e:
                    raise xlib.ProgramException(e, 'L002', record_data_list[i])
                species_id_list.append(species_id)
                mother_id_list.append(mother_id)

            # check if the sample species list is empty
            if species_id_list == []:
                raise xlib.ProgramException('', 'L003')

            # set the sample number
            sample_number = len(species_id_list)

            # write the column description record
            temporal_vcf_file_id.write(record)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Filtered variants ... {filtered_variant_counter:8d}')

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

            # get the reference bases (field REF) and alternative alleles (field ALT)
            reference_bases = data_dict['ref']
            alternative_alleles = data_dict['alt']

            # build the alternative alleles list from field ALT
            alternative_allele_list = data_dict['alt'].split(',')

            # check if the variant is an indel (both SAMtools/BCFtools and Freebayes)
            is_indel = False
            if len(reference_bases) > 1:
                is_indel = True
            else:
                for alternative_allele in alternative_allele_list:
                    if len(alternative_allele) > 1:
                        is_indel = True
                        break
            if variant_id in tvi_list: xlib.Message.print('trace', f'(1) INDEL?: {is_indel}')

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
                if sample_gt_list[i] not in xlib.get_md_code_list():
                    try:
                        sample_gt_left_list.append(int(sample_gt_list[i][:sep_pos]))
                        sample_gt_right_list.append(int(sample_gt_list[i][sep_pos+1:]))
                    except Exception as e:
                        raise xlib.ProgramException(e, 'L008', 'GT', data_dict['chrom'], data_dict['pos'])
                else:
                    sample_gt_left_list.append(-1)
                    sample_gt_right_list.append(-1)

            if variant_id in tvi_list: xlib.Message.print('trace', f'(2) reference_bases: {reference_bases}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'(3) alternative_allele_list: {alternative_allele_list}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'(4) sample_gt_list: {sample_gt_list}')

            # fix the reference base(s) when there are not individual with this reference
            if fix.upper() == 'Y':

                # check if there are samples with 0/n or 0|n in their field GT
                found_0_n = False
                for i in range(sample_number):
                    if sample_gt_left_list[i] == 0 or sample_gt_right_list[i] == 0:
                        found_0_n = True
                        break

                # if there is not any sample with 0/n or 0|n in its field GT
                if not found_0_n:

                    # change the reference_base(s) and alternative alleles
                    reference_bases = alternative_allele_list[0]
                    alternative_allele_list = alternative_allele_list[1:]
                    alternative_allele_list = [xlib.get_md_symbol()] if alternative_allele_list == [] else alternative_allele_list
                    if variant_id in tvi_list: xlib.Message.print('trace', '(5) 0 is not found, the reference_bases and alternative_allele_list have been changed.')

                    # fix the of the field GT of every sample
                    for i in range(sample_number):
                        if sample_gt_left_list[i] >= 1:
                            sample_gt_left_list[i] -= 1
                            sample_gt_right_list[i] -= 1

            # calculate the alternative allele counter per allele (2 or higher) and species and their percentages
            aa_counter_list_1 = []
            aa_counter_list_2 = []
            aa_counter_list_h = []
            for _ in range(len(alternative_allele_list)):
                aa_counter_list_1.append(0)
                aa_counter_list_2.append(0)
                aa_counter_list_h.append(0)
            for i in range(sample_number):
                if mother_id_list[i] == 'NONE':
                    if sample_gt_right_list[i] >=2:
                        if species_id_list[i] == sp1_id:
                            aa_counter_list_1[sample_gt_right_list[i] - 1] += 1
                        elif species_id_list[i] == sp2_id:
                            aa_counter_list_2[sample_gt_right_list[i] - 1] += 1
                        else:
                            aa_counter_list_h[sample_gt_right_list[i] - 1] += 1
            if variant_id in tvi_list: xlib.Message.print('trace', f'(6) aa_counter_list_1: {aa_counter_list_1} - aa_counter_list_2 {aa_counter_list_2} - aa_counter_list_h: {aa_counter_list_h}')
            aa_percentage_list_1 = []
            aa_percentage_list_2 = []
            aa_percentage_list_h = []
            for i in range(len(alternative_allele_list)):
                aa_percentage_list_1.append(aa_counter_list_1[i] / adult_num_1 * 100)
                aa_percentage_list_2.append(aa_counter_list_2[i] / adult_num_2 * 100)
                aa_percentage_list_h.append(aa_counter_list_h[i] / adult_num_h * 100) if hybrid_id != 'NONE' else 0
            if variant_id in tvi_list: xlib.Message.print('trace', f'(7) aa_percentage_list_1: {aa_percentage_list_1} - aa_percentage_list_2 {aa_percentage_list_2} - aa_percentage_list_h: {aa_percentage_list_h}')

            # fix the GT field of alternative alleles if the alternative allele percentage is less than the minimum percentage in every species when the variant is not a indel
            if not is_indel:

                for i in range(sample_number):
                    if sample_gt_right_list[i] >= 2:
                        if (species_id_list[i] == sp1_id and aa_percentage_list_1[sample_gt_right_list[i] - 1] < min_aa_percentage) or \
                            (species_id_list[i] == sp2_id and aa_percentage_list_2[sample_gt_right_list[i] - 1] < min_aa_percentage) or \
                            (species_id_list[i] == hybrid_id and aa_percentage_list_h[sample_gt_right_list[i] - 1] < min_aa_percentage):
                            # set missing data
                            if variant_id in tvi_list: xlib.Message.print('trace', f'(8) Setting missing data in i: {i} - sample_gt_left_list[i]: {sample_gt_left_list[i]} - sample_gt_right_list[i]: {sample_gt_right_list[i]}')
                            sample_gt_left_list[i] = -1
                            sample_gt_right_list[i] = -1

            # fix the alternative allele list when a alternative allele does not have any sample
            alternative_allele_counter_list = []
            for _ in range(len(alternative_allele_list)):
                alternative_allele_counter_list.append(0)
            for i in range(sample_number):
                if sample_gt_left_list[i] > 0 :
                    alternative_allele_counter_list[sample_gt_left_list[i] - 1] += 1
                if sample_gt_right_list[i] > 0 :
                    alternative_allele_counter_list[sample_gt_right_list[i] - 1] += 1
            for i in range(len(alternative_allele_counter_list) -1, -1, -1):
                if alternative_allele_counter_list[i] == 0:
                    del alternative_allele_list[i]
                if alternative_allele_list == []:
                    alternative_allele_list = [xlib.get_md_symbol()]
                else:
                    alternative_allele_list
            if variant_id in tvi_list: xlib.Message.print('trace', f'(9) alternative_allele_counter_list: {alternative_allele_counter_list}')

            # calculate the missing data counter per species and their percentages
            md_counter_1 = 0
            md_counter_2 = 0
            md_counter_h = 0
            for i in range(sample_number):
                if mother_id_list[i] == 'NONE':
                    if sample_gt_right_list[i] == -1:
                        if species_id_list[i] == sp1_id:
                            md_counter_1 += 1
                        elif species_id_list[i] == sp2_id:
                            md_counter_2 += 1
                        else:
                            md_counter_h += 1
            md_percentage_1 = md_counter_1 / adult_num_1 * 100
            md_percentage_2 = md_counter_2 / adult_num_2 * 100
            md_percentage_h = md_counter_h / adult_num_h * 100
            if variant_id in tvi_list: xlib.Message.print('trace', f'(10) {sp1_id} missing data: {md_percentage_1:5.2f}% - {sp2_id} missing data: {md_percentage_2:5.2f}% - {hybrid_id} missing data: {md_percentage_h:5.2f}%')

            # when sample is an adult individual, fix the symbol of missing data of the GP field of alternative alleles if the percentage of mising data per species is greater than to the minimum percentage of missing data imputation to a new alternative allele of the corresponding species of the corresponding species or the species is hybrid with the identification of the alternative allele for imputed missing data
            for i in range(sample_number):

                # only when the sample is an adult individual
                if mother_id_list[i] == 'NONE':

                    if sample_gt_right_list[i] == -1 and \
                      (species_id_list[i] == sp1_id and md_percentage_1 > min_md_imputation_percentage or \
                       species_id_list[i] == sp2_id and md_percentage_2 > min_md_imputation_percentage or \
                       species_id_list[i] == hybrid_id and (md_percentage_1 > min_md_imputation_percentage or md_percentage_2 > min_md_imputation_percentage)):

                        sample_gt_left_list[i] = 99
                        sample_gt_right_list[i] = 99

            # get a list with the new order of the alternative alleles
            new_order_list = []
            order = 1
            for i in range(len(alternative_allele_counter_list)):
                if alternative_allele_counter_list[i] > 0:
                    new_order_list.append(order)
                    order += 1
                else:
                    new_order_list.append(0)
            if variant_id in tvi_list: xlib.Message.print('trace', f'(11) new_order_list: {new_order_list}')

            # check if all samples are monomorphic
            monomorphic = True
            left_allele = None
            right_allele = None
            for i in range(sample_number):
                if mother_id_list[i] == 'NONE':
                    if sample_gt_right_list[i] == 99:
                        monomorphic = False
                        break
                    elif sample_gt_right_list[i] != -1:
                        if left_allele == None:
                            left_allele = sample_gt_left_list[i]
                        if right_allele == None:
                            right_allele = sample_gt_right_list[i]
                        if left_allele != sample_gt_left_list[i] or right_allele != sample_gt_right_list[i]:
                            monomorphic = False
                            break
            if variant_id in tvi_list: xlib.Message.print('trace', f'(12) monomorphic: {monomorphic}')

            if variant_id in tvi_list:
                literal = ''
                for i in range(sample_number):
                    literal += f'{str(sample_gt_left_list[i])}{sample_sep_list[i]}{str(sample_gt_right_list[i])} '
                xlib.Message.print('trace', f'(13) genotype list before imputation revision: {literal}')

            # review depending on the scenario
            for i in range(sample_number):

                # only when the sample is an adult individual
                if mother_id_list[i] == 'NONE':

                    # revision when the scenario is '0' (no imputation) or '2' (maximum possible imputation)
                    if scenario in ['0', '2']:

                        # the sample is hybrid
                        if species_id_list[i] == hybrid_id and (md_percentage_1 > min_md_imputation_percentage or md_percentage_2 > min_md_imputation_percentage) and sample_gt_left_list[i] == sample_gt_right_list[i]:
                            sample_gt_right_list[i] = 99
                        elif species_id_list[i] == sp1_id and (md_percentage_1 > min_md_imputation_percentage) and sample_gt_left_list[i] == sample_gt_right_list[i]:
                            sample_gt_right_list[i] = 99
                        elif species_id_list[i] == sp2_id and (md_percentage_2 > min_md_imputation_percentage) and sample_gt_left_list[i] == sample_gt_right_list[i]:
                            sample_gt_right_list[i] = 99

                    # revision when the scenario is '1' (standard)
                    elif scenario == '1':

                        #if sample_gt_right_list[i] == -1:
                        #    sample_gt_left_list[i] = 99
                        #    sample_gt_right_list[i] = 99
                        pass

                    # revision when the scenario is '3' (maximum possible missing data)
                    elif scenario == '3':

                        if sample_gt_left_list[i] == sample_gt_right_list[i]:
                            sample_gt_right_list[i] = -1

            if variant_id in tvi_list:
                literal = ' '
                for i in range(sample_number):
                    literal += f'{str(sample_gt_left_list[i])}{sample_sep_list[i]}{str(sample_gt_right_list[i])} '
                xlib.Message.print('trace', f'(14)  genotype list after imputation revision: {literal}')

            # rebuild the list of the field GT for every sample
            for i in range(sample_number):
                if sample_gt_left_list[i] == -1:
                    left = xlib.get_md_symbol()
                elif sample_gt_left_list[i] == 99:
                    left = imputed_md_id
                else:
                    left = new_order_list[sample_gt_left_list[i] - 1] if sample_gt_left_list[i] > 0 else 0
                if sample_gt_right_list[i] == -1:
                    right = xlib.get_md_symbol()
                elif sample_gt_right_list[i] == 99:
                    right = imputed_md_id
                else:
                    right = new_order_list[sample_gt_right_list[i] - 1] if sample_gt_right_list[i] > 0 else 0
                sample_gt_left_list[i] = left
                sample_gt_right_list[i] = right
                sample_gt_list[i] = f'{sample_gt_left_list[i]}{sample_sep_list[i]}{sample_gt_right_list[i]}'

            # rebuild the alternative alleles and its corresponding record data
            alternative_alleles = ','.join(alternative_allele_list)

            # rebuild the sample genotype data list and their corresponding record data
            sample_list = []
            for i in range(sample_number):
                sample_data_list[i][gt_position] = sample_gt_list[i]
                sample_list.append(':'.join(sample_data_list[i]))

            if variant_id in tvi_list: xlib.Message.print('trace', f'(15) reference_bases: {reference_bases}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'(16) alternative_allele_list: {alternative_allele_list}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'(17) sample_gt_list: {sample_gt_list}')

            # check the allele frecuencies when the variant is not a indel
            allele_frequency_OK = True
            if not is_indel:

                # get the allele counters per species
                allele_counter_dict_1 = {}
                allele_counter_dict_2 = {}
                allele_counter_dict_h = {}
                for i in range(sample_number):
                    if mother_id_list[i] == 'NONE':
                        if sample_gt_right_list[i] != xlib.get_md_symbol():
                            if species_id_list[i] == sp1_id:
                                allele_counter_dict_1[sample_gt_left_list[i]] = allele_counter_dict_1.get(sample_gt_left_list[i], 0) + 1
                                allele_counter_dict_1[sample_gt_right_list[i]] = allele_counter_dict_1.get(sample_gt_right_list[i], 0) + 1
                            elif species_id_list[i] == sp2_id:
                                allele_counter_dict_2[sample_gt_left_list[i]] = allele_counter_dict_2.get(sample_gt_left_list[i], 0) + 1
                                allele_counter_dict_2[sample_gt_right_list[i]] = allele_counter_dict_2.get(sample_gt_right_list[i], 0) + 1
                            else:
                                allele_counter_dict_h[sample_gt_left_list[i]] = allele_counter_dict_h.get(sample_gt_left_list[i], 0) + 1
                                allele_counter_dict_h[sample_gt_right_list[i]] = allele_counter_dict_h.get(sample_gt_right_list[i], 0) + 1
                if variant_id in tvi_list: xlib.Message.print('trace', f'(18) allele_counter_dict_1: {allele_counter_dict_1}')
                if variant_id in tvi_list: xlib.Message.print('trace', f'(19) allele_counter_dict_2: {allele_counter_dict_2}')
                if variant_id in tvi_list: xlib.Message.print('trace', f'(20) allele_counter_dict_h: {allele_counter_dict_h}')

                # check the allele frecuencies per species
                if imputed_md_id in allele_counter_dict_1.keys() and len(allele_counter_dict_1.keys()) > 3 or \
                    imputed_md_id not in allele_counter_dict_1.keys() and len(allele_counter_dict_1.keys()) > 2 or \
                    imputed_md_id in allele_counter_dict_2.keys() and len(allele_counter_dict_2.keys()) > 3 or \
                    imputed_md_id not in allele_counter_dict_2.keys() and len(allele_counter_dict_2.keys()) > 2:
                    allele_frequency_OK = False
                    if variant_id in tvi_list: xlib.Message.print('trace', '(21) multiallelic variant.')
                else:
                    sp1_allele_total = 0
                    for allele in allele_counter_dict_1.keys():
                        sp1_allele_total += allele_counter_dict_1[allele]
                    for allele in allele_counter_dict_1.keys():
                        allele_frequency = allele_counter_dict_1[allele] / sp1_allele_total * 100
                        if allele_frequency < min_afr_percentage:
                            allele_frequency_OK = False
                            if variant_id in tvi_list: xlib.Message.print('trace', f'(20) allele {allele} in species 1 has a frequency {allele_frequency:5.2f}% less than maf')
                    sp2_allele_total = 0
                    for allele in allele_counter_dict_2.keys():
                        sp2_allele_total += allele_counter_dict_2[allele]
                    for allele in allele_counter_dict_2.keys():
                        allele_frequency = allele_counter_dict_2[allele] / sp2_allele_total * 100
                        if allele_counter_dict_2[allele] / sp2_allele_total * 100 < min_afr_percentage:
                            allele_frequency_OK = False
                            if variant_id in tvi_list: xlib.Message.print('trace', f'(21) allele {allele} in species 2 has a frequency {allele_frequency:5.2f}% less than maf')

            # check if there are imputation in adult individuals when the scenario is 0 (no imputation)
            scenario0_are_there_imputations = False
            if scenario == '0':
                for i in range(sample_number):
                    if mother_id_list[i] == 'NONE' and (sample_gt_left_list[i]==imputed_md_id or sample_gt_right_list[i]==imputed_md_id):
                        scenario0_are_there_imputations = True
                        break

            # if DP is less than the minimum combined depth or all samples are monomorphic or the missing data percentage is greater than or equal to the missing data percentage threshold in both species or allele frequency is not OK
            if variant_id in tvi_list: xlib.Message.print('trace', f'(22) dp: {dp} - md_percentage_1: {md_percentage_1:5.2f}% - md_percentage_2: {md_percentage_2:5.2f}% - allele_frequency_OK: {allele_frequency_OK}')
            if dp < min_depth or monomorphic or (md_percentage_1 > sp1_max_md_percentage and md_percentage_2 > sp2_max_md_percentage) or not allele_frequency_OK or scenario0_are_there_imputations:

                # add 1 to the filtered variant counter
                filtered_variant_counter += 1
                if variant_id in tvi_list: xlib.Message.print('trace', '(23) This variant is deleted!!!')

            # in any other case
            else:

                # add the sequence identification to the non filtered sequence identification list
                if data_dict['chrom'] not in non_filtered_seq_id_list:
                    non_filtered_seq_id_list.append(data_dict['chrom'])

                # write the variant record
                sample_list_text = '\t'.join(sample_list)
                temporal_vcf_file_id.write(f'{data_dict["chrom"]}\t{data_dict["pos"]}\t{data_dict["id"]}\t{reference_bases}\t{alternative_alleles}\t{data_dict["qual"]}\t{data_dict["filter"]}\t{data_dict["info"]}\t{data_dict["format"]}\t{sample_list_text}\n')

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Filtered variants ... {filtered_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    xlib.Message.print('verbose', '\n')

    # close files
    input_vcf_file_id.close()
    temporal_vcf_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The temporal file {os.path.basename(temporal_vcf_file)} containing the filtered variants is created.')
    xlib.Message.print('info', 'Removing metadata of filtered variants ...')

    # open the temporal VCF file
    if temporal_vcf_file.endswith('.gz'):
        try:
            temporal_vcf_file_id = gzip.open(temporal_vcf_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', temporal_vcf_file)
    else:
        try:
            temporal_vcf_file_id = open(temporal_vcf_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', temporal_vcf_file)

    # open the output VCF file
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

    # read the first record of temporal VCF file
    record = temporal_vcf_file_id.readline()

    # while there are records in temporal VCF file
    while record != '':

        # process contig records
        if record.startswith('##contig'):

            # get the sequence identification and the position
            seq_id = ''
            i1 = 13
            i2 = record.find(',', i1)
            if i2 > -1:
                seq_id = record[i1:i2]

            # write the record when the sequence identification was not filtered
            if seq_id in non_filtered_seq_id_list:
                output_vcf_file_id.write(record)

        # process other records
        else:

            # write record
            output_vcf_file_id.write(record)

        # read the next record
        record = temporal_vcf_file_id.readline()

    # close files
    temporal_vcf_file_id.close()
    output_vcf_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The file {os.path.basename(output_vcf_file)} containing the filtered variants is created.')

    # delete temporal VCF file
    os.remove(temporal_vcf_file)
    xlib.Message.print('info', f'The temporal VCF file {os.path.basename(temporal_vcf_file)} is deleted.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
