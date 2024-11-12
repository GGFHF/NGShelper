#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program builds the allele frequency from a VCF file in the format required
by SimHyb application.

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
import math
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

    # build the allele frequency
    build_allele_frequency(args.vcf_file, args.sample_file, args.sp1_id, args.sp2_id, args.hybrid_id, args.output_dir, args.variant_number_per_file, args.allele_transformation, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program builds the allele frequency from a VCF file in the format required by SimHyb application.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='vcf_file', help='Path of input VCF file (mandatory).')
    parser.add_argument('--samples', dest='sample_file', help='Path of the sample file in the following record format: "sample_id;species_id;mother_id" (mandatory).')
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species (mandatory).')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--outdir', dest='output_dir', help='Path of output directoty where files for SimHyb application are saved (mandatory).')
    parser.add_argument('--varnum', dest='variant_number_per_file', help=f'Variant number per file, the allele frequency data will be splitted in several if the total variant number is greater than this argument; default: {xlib.Const.DEFAULT_VARIANT_NUMBER_PER_FILE}.')
    parser.add_argument('--trans', dest='allele_transformation', help=f'Transformation of the allele symbol: {xlib.get_allele_transformation_code_list_text()}; default: NONE.')
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
        xlib.Message.print('error', '*** The identification of the first species is not indicated in the input arguments.')
        OK = False

    # check "sp2_id"
    if args.sp2_id is None:
        xlib.Message.print('error', '*** The identification of the second species is not indicated in the input arguments.')
        OK = False

    # check "hybrid_id"
    if args.hybrid_id is None:
        args.hybrid_id = 'NONE'

    # check "output_dir"
    if args.output_dir is None:
        xlib.Message.print('error', '*** The output directy is not indicated in the input arguments.')
        OK = False
    elif not os.path.isdir(args.output_dir):
        xlib.Message.print('error', '*** The output directy does not exist.')
        OK = False

    # check "variant_number_per_file"
    if args.variant_number_per_file is None:
        args.variant_number_per_file = xlib.Const.DEFAULT_VARIANT_NUMBER_PER_FILE
    elif not xlib.check_int(args.variant_number_per_file, minimum=1):
        xlib.Message.print('error', 'The variant number per file has to be an integer number greater than 0.')
        OK = False
    else:
        args.variant_number_per_file = int(args.variant_number_per_file)

    # check "allele_transformation"
    if args.allele_transformation is None:
        args.allele_transformation = 'NONE'
    elif not xlib.check_code(args.allele_transformation, xlib.get_allele_transformation_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The allele transformation has to be {xlib.get_allele_transformation_code_list_text()}.')
        OK = False
    else:
        args.allele_transformation = args.allele_transformation.upper()

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

def build_allele_frequency(vcf_file, sample_file, sp1_id, sp2_id, hybrid_id, output_dir, variant_number_per_file, allele_transformation, tvi_list):
    '''
    Filter and fixes variant data of a VCF file.
    '''

    # initialize the sample number
    sample_number = 0

    # initialize counters
    input_record_counter = 0
    total_variant_counter = 0

    # get the sample data
    sample_dict = xlib.get_sample_data(sample_file, sp1_id, sp2_id, hybrid_id)

    # initialize the sample species and mother identification lists per variant
    species_id_list = []
    mother_id_list = []

    # initialize the maximum allele number per varaint
    maximum_allele_number = 0

    # initialize allele frequency dictionaries
    allele_frequency_dict_1 = {}
    allele_frequency_dict_2 = {}

    # initialize ATCG conversión dictionary
    # A -> 1; T -> 2; C -> 3; G -> 4
    atcg = 'ATCG'
    atcg_conversion_dict = {}

    # open the input VCF file
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

    # read the first record of input VCF file
    (record, key, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

    # while there are records in input VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... { total_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, key, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

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
                raise xlib.ProgramException(e, 'L003')

            # set the sample number
            sample_number = len(species_id_list)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, key, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

        # process variant record
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add set the variant identification
            variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'

            # add 1 to the read sequence counter
            input_record_counter += 1

            # add 1 to the total variant counter
            total_variant_counter += 1

            if variant_id in tvi_list: xlib.Message.print('trace', f'\n\n\n\nseq_id: {data_dict["chrom"]} - position {data_dict["pos"]}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'total_variant_counter: {total_variant_counter}')

            # get the reference bases (field REF) and alternative alleles (field ALT)
            reference_bases = data_dict['ref']
            alternative_alleles = data_dict['alt']

            # build the alternative alleles list from field ALT
            alternative_allele_list = data_dict['alt'].split(',')

            # build ATCG conversion list
            atcg_conversion_list = []
            index = atcg.find(reference_bases.upper())
            if index == -1:
                raise xlib.ProgramException('', 'L016', variant_id)
            else:
                atcg_conversion_list.append(index + 1)
            for i in range(len(alternative_allele_list)):
                index = atcg.find(alternative_allele_list[i].upper())
                if index == -1:
                    raise xlib.ProgramException('', 'L016', variant_id)
                else:
                    atcg_conversion_list.append(index + 1)
            atcg_conversion_dict[total_variant_counter] = atcg_conversion_list

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
            sample_gt_right_list = []
            for i in range(sample_number):
                sep = '/'
                sep_pos = sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    sep = '|'
                    sep_pos = sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    raise xlib.ProgramException('L008', 'GT', data_dict['chrom'], data_dict['pos'])
                sample_gt_left_list.append(sample_gt_list[i][:sep_pos])
                sample_gt_right_list.append(sample_gt_list[i][sep_pos+1:])

            if variant_id in tvi_list: xlib.Message.print('trace', f'reference_bases: {reference_bases}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'alternative_allele_list: {alternative_allele_list}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'sample_gt_list: {sample_gt_list}')

            # get the allele counters per species
            allele_counter_dict_1 = {}
            allele_counter_dict_2 = {}
            allele_counter_dict_h = {}
            for i in range(sample_number):
                # only when the sample is an adult
                if mother_id_list[i] == 'NONE':
                    if sample_gt_left_list[i] != xlib.get_md_symbol():
                        if species_id_list[i] == sp1_id:
                            allele_counter_dict_1[sample_gt_left_list[i]] = allele_counter_dict_1.get(sample_gt_left_list[i], 0) + 1
                        elif species_id_list[i] == sp2_id:
                            allele_counter_dict_2[sample_gt_left_list[i]] = allele_counter_dict_2.get(sample_gt_left_list[i], 0) + 1
                        else:
                            allele_counter_dict_h[sample_gt_left_list[i]] = allele_counter_dict_h.get(sample_gt_left_list[i], 0) + 1
                    if sample_gt_right_list[i] != xlib.get_md_symbol():
                        if species_id_list[i] == sp1_id:
                            allele_counter_dict_1[sample_gt_right_list[i]] = allele_counter_dict_1.get(sample_gt_right_list[i], 0) + 1
                        elif species_id_list[i] == sp2_id:
                            allele_counter_dict_2[sample_gt_right_list[i]] = allele_counter_dict_2.get(sample_gt_right_list[i], 0) + 1
                        else:
                            allele_counter_dict_h[sample_gt_right_list[i]] = allele_counter_dict_h.get(sample_gt_right_list[i], 0) + 1
            if variant_id in tvi_list: xlib.Message.print('trace', f'allele_counter_dict_1: {allele_counter_dict_1}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'allele_counter_dict_2: {allele_counter_dict_2}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'allele_counter_dict_h: {allele_counter_dict_h}')

            # calculate the maximum allele number
            if maximum_allele_number < len(allele_counter_dict_1.keys()):
                maximum_allele_number = len(allele_counter_dict_1.keys())
            if maximum_allele_number < len(allele_counter_dict_2.keys()):
                maximum_allele_number = len(allele_counter_dict_2.keys())

            # calculate the variant allele frecuencies per species
            allele_frequency_dict_1[total_variant_counter] = {}
            sp1_allele_total = 0
            for allele in allele_counter_dict_1.keys():
                sp1_allele_total += allele_counter_dict_1[allele]
            for allele in allele_counter_dict_1.keys():
                allele_frequency_dict_1[total_variant_counter][allele] = allele_counter_dict_1[allele] / sp1_allele_total
                if variant_id in tvi_list: xlib.Message.print('trace', f'allele_frequency_dict_1[{total_variant_counter}][{allele}]: {allele_frequency_dict_1[total_variant_counter][allele]}')
            allele_frequency_dict_2[total_variant_counter] = {}
            sp2_allele_total = 0
            for allele in allele_counter_dict_2.keys():
                sp2_allele_total += allele_counter_dict_2[allele]
            for allele in allele_counter_dict_2.keys():
                allele_frequency_dict_2[total_variant_counter][allele] = allele_counter_dict_2[allele] / sp2_allele_total
                if variant_id in tvi_list: xlib.Message.print('trace', f'allele_frequency_dict_2[{total_variant_counter}][{allele}]: {allele_frequency_dict_2[total_variant_counter][allele]}')

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, key, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

    xlib.Message.print('verbose', '\n')

    # close the VCF file
    vcf_file_id.close()

    # calculate the output SimHyb file number
    simhyb_file_num = math.ceil(total_variant_counter / variant_number_per_file)

    # initialize the begin and end variant
    begin_variant = 1
    end_variant =  variant_number_per_file if variant_number_per_file < total_variant_counter else total_variant_counter

    # write the variant allele frecuencies per species in the output SimHyb files
    for i in range(simhyb_file_num):

        xlib.Message.print('trace', '\n\n\n\nbegin_variant: {} - end_variant: {}'.format(begin_variant, end_variant))

        # set the SimHyb file name
        if vcf_file.endswith('.gz'):
            file_name, file_extension = os.path.splitext(os.path.basename(vcf_file[:-3]))
        else:
            file_name, file_extension = os.path.splitext(os.path.basename(vcf_file))
        if simhyb_file_num == 1:
            current_simhyb_file = f'{output_dir}/{file_name}-allelefreq.csv'
        else:
            current_simhyb_file = f'{output_dir}/{file_name}-allelefreq-{i:03d}.csv'

        # open the output SimHyb file
        if current_simhyb_file.endswith('.gz'):
            try:
                current_simhyb_file_id = gzip.open(current_simhyb_file, mode='wt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise xlib.ProgramException(e, 'F004', current_simhyb_file)
        else:
            try:
                current_simhyb_file_id = open(current_simhyb_file, mode='w', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise xlib.ProgramException(e, 'F003', current_simhyb_file)

        # write allele frequency records
        for i in range(maximum_allele_number):

            xlib.Message.print('trace', f'i: {i}')

            # initialize the variable to control the record begin
            is_begin = True

            # species 1
            for j in range(begin_variant, end_variant + 1):

                xlib.Message.print('trace', f'j: {j}')

                # get the allele and its frequency
                variant_data_dict = allele_frequency_dict_1.get(j, {})

                xlib.Message.print('trace', f'variant_data_dict: {variant_data_dict}')

                if variant_data_dict == {}:
                    allele = 0
                    allele_frequency = 0
                else:
                    allele_list = sorted(variant_data_dict.keys())
                    if i < len(allele_list):
                        allele = allele_list[i]
                        allele_frequency = variant_data_dict[allele]
                        if allele_transformation == 'ADD100' and xlib.check_int(allele):
                            allele = int(allele) + 100
                        elif allele_transformation == 'ATCG':
                            allele = atcg_conversion_dict[j][int(allele)]
                    else:
                        allele = 0
                        allele_frequency = 0

                # write the part of this record corresponding with the sample
                if is_begin:
                    record_part = f'{allele};{allele_frequency}'
                    is_begin = False
                else:
                    record_part = f';{allele};{allele_frequency}'
                current_simhyb_file_id.write(record_part)

            # species 2
            for j in range(begin_variant, end_variant + 1):

                # get the allele and its frequency
                variant_data_dict = allele_frequency_dict_2.get(j, {})
                if variant_data_dict == {}:
                    allele = 0
                    allele_frequency = 0
                else:
                    allele_list = sorted(variant_data_dict.keys())
                    if i < len(allele_list):
                        allele = allele_list[i]
                        allele_frequency = variant_data_dict[allele]
                        if allele_transformation == 'ADD100' and xlib.check_int(allele):
                            allele = int(allele) + 100
                        elif allele_transformation == 'ATCG':
                            allele = atcg_conversion_dict[j][int(allele)]
                    else:
                        allele = 0
                        allele_frequency = 0

                # write the part of this record corresponding with the variant
                record_part = f';{allele};{allele_frequency}'
                current_simhyb_file_id.write(record_part)

            # write the end of the record
            current_simhyb_file_id.write('\n')

        # close SymHyb file
        current_simhyb_file_id.close()

        # print OK message
        xlib.Message.print('info', f'The SimHyb file {os.path.basename(current_simhyb_file)} is created.')

        # set the new begin and end variant
        begin_variant = end_variant + 1
        end_variant =  begin_variant + variant_number_per_file - 1 if begin_variant + variant_number_per_file - 1 < total_variant_counter else total_variant_counter

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
