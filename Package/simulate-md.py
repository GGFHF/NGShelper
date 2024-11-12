#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program simulates missing data in a VCF file.

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
import random
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

    # simulate missing data
    simulate_md(args.input_vcf_file, args.simulation_method, args.md_probability, args.maxperc_ind_wmd, args.output_vcf_file, args.tsi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program simulates missing data in a VCF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='input_vcf_file', help='Path of input VCF file (mandatory).')
    parser.add_argument('--method', dest='simulation_method', help=f'Simulation method (mandatory): {xlib.get_simulation_method_code_list_text()}.')
    parser.add_argument('--mdp', dest='md_probability', help='Probability of a locus having missing data (mandatory).')
    parser.add_argument('--mpiwmd', dest='maxperc_ind_wmd', help=f'Maximum percentage of individuals with missing data in each locus (RANDOM method); default: {xlib.Const.DEFAULT_MAXPERC_IND_WMD}.')
    parser.add_argument('--out', dest='output_vcf_file', help='Path of output VCF file (mandatory).')
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

    # check "input_vcf_file"
    if args.input_vcf_file is None:
        xlib.Message.print('error', '*** The VCF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.input_vcf_file):
        xlib.Message.print('error', f'*** The file {args.input_vcf_file} does not exist.')
        OK = False

    # check "simulation_method"
    if args.simulation_method is None:
        xlib.Message.print('error', '*** The simulation method is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.simulation_method, xlib.get_simulation_method_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The simulation_method has to be {xlib.get_simulation_method_code_list_text()}.')
        OK = False
    else:
        args.simulation_method = args.simulation_method.upper()

    # check "md_probability"
    if args.md_probability is None:
        xlib.Message.print('error', '*** The probability of a locus having missing data is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.md_probability, minimum=0.0, maximum=100.0):
        xlib.Message.print('error', 'The probability of a locus having missing data has to be a float number between 0.0 and 100.0.')
        OK = False
    else:
        args.md_probability = float(args.md_probability)

    # check "maxperc_ind_wmd"
    if args.maxperc_ind_wmd is None:
        args.maxperc_ind_wmd = xlib.Const.DEFAULT_MAXPERC_IND_WMD
    elif not xlib.check_float(args.maxperc_ind_wmd, minimum=0.0, maximum=100.0):
        xlib.Message.print('error', 'The maximum percentage of individuals with missing data in each locus has to be float number between 0.0 and 100.0.')
        OK = False
    else:
        args.maxperc_ind_wmd = int(args.maxperc_ind_wmd)

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

    # check "tsi_list"
    if args.tsi_list is None or args.tsi_list == 'NONE':
        args.tsi_list = []
    else:
        args.tsi_list = xlib.split_literal_to_string_list(args.tsi_list)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def simulate_md(input_vcf_file, simulation_method, md_probability, maxperc_ind_wmd, output_vcf_file, tsi_list):
    '''
    Simulate missing data in a VCF file.
    '''

    # initialize the sample lists and sample number
    # -- sample_name_list = []
    sample_id_list = []
    sample_list = []
    sample_number = 0

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

    # open the VCF file with missing data
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
    variant_wmd_counter = 0

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
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Variants with missing data ... {variant_wmd_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # get the record data list
            record_data_list = data_dict['record_data_list']

            # build sample identification list
            for i in range(9, len(record_data_list)):
                # -- sample_name_list.append(os.path.basename(record_data_list[i]))
                sample_id_list.append(i - 9)

            # set the samples number
            sample_number = len(sample_id_list)
            xlib.Message.print('trace', f'sample_number: {sample_number}')

            # write the column description record
            output_vcf_file_id.write(record)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Variants with missing data ... {variant_wmd_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process variant record
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # set the sequence identification
            seq_id = data_dict['chrom']

            # add set the variant identification
            variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'

            # add 1 to the read sequence counter
            input_record_counter += 1

            # add 1 to the total variant counter
            total_variant_counter += 1

            if seq_id in tsi_list: xlib.Message.print('trace', f'\n\n\n\nseq_id: {data_dict["chrom"]} - position {data_dict["pos"]}')

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
            if seq_id in tsi_list: xlib.Message.print('trace', f'(1) INDEL?: {is_indel}')

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

            # simulate missing data when method is RANDOM
            if simulation_method == 'RANDOM':
                if md_probability > random.random():

                    xlib.Message.print('trace', f'\n\nseq_id: {data_dict["chrom"]} - position {data_dict["pos"]}')

                    # build the genotype text before simulation
                    genotype_text_before_simulation = ''
                    for i in range(sample_number):
                        genotype_text_before_simulation += f'{str(sample_gt_left_list[i])}{sample_sep_list[i]}{str(sample_gt_right_list[i])} '

                    # get the number of individuals with missing data
                    perc_ind_wmd = random.uniform(0., maxperc_ind_wmd)
                    num_ind_wmd = max(1, round(sample_number * perc_ind_wmd / 100))

                    # get the list of individuals with missing data
                    ind_id_wmd_list = []
                    w_sample_id_list = sample_id_list.copy()
                    for _ in range(num_ind_wmd):
                        j = random.randrange(0, len(w_sample_id_list))
                        ind_id_wmd_list.append(w_sample_id_list[j])
                        del w_sample_id_list[j]

                    # asign missing data to the individuals
                    for ind_id in ind_id_wmd_list:
                        sample_gt_left_list[ind_id] = xlib.get_md_symbol()
                        sample_gt_right_list[ind_id] = xlib.get_md_symbol()

                    # add 1 to the variant with missing data counter
                    variant_wmd_counter += 1

                    # build the genotype text after simulation
                    genotype_text_after_simulation = ''
                    for i in range(sample_number):
                        genotype_text_after_simulation += f'{str(sample_gt_left_list[i])}{sample_sep_list[i]}{str(sample_gt_right_list[i])} '
                    xlib.Message.print('trace', f'genotype list before simulation: {genotype_text_before_simulation}')
                    xlib.Message.print('trace', f'genotype list  after simulation: {genotype_text_after_simulation}')

            # rebuild the list of the field GT for every sample
            for i in range(sample_number):
                sample_gt_list[i] = f'{sample_gt_left_list[i]}{sample_sep_list[i]}{sample_gt_right_list[i]}'

            # rebuild the sample genotype data list and their corresponding record data
            sample_list = []
            for i in range(sample_number):
                sample_data_list[i][gt_position] = sample_gt_list[i]
                sample_list.append(':'.join(sample_data_list[i]))

            # write the variant record
            sample_list_text = '\t'.join(sample_list)
            output_vcf_file_id.write(f'{data_dict["chrom"]}\t{data_dict["pos"]}\t{data_dict["id"]}\t{data_dict["ref"]}\t{data_dict["alt"]}\t{data_dict["qual"]}\t{data_dict["filter"]}\t{data_dict["info"]}\t{data_dict["format"]}\t{sample_list_text}\n')

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Variants with missing data ... {variant_wmd_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    xlib.Message.print('verbose', '\n')

    # close files
    input_vcf_file_id.close()
    output_vcf_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
