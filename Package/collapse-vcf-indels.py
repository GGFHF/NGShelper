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
This program collapses the variant records corresponding to an indel in a VCF file.
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

    # collapses the variant records corresponding to an indel in a VCF file
    collapse_indels(args.input_vcf_file, args.sample_file, args.imputed_md_id, args.sp1_id, args.sp2_id, args.hybrid_id, args.output_vcf_file, args.stats_file, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program collapses the variant records corresponding to an indel in a VCF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='input_vcf_file', help='Path of input VCF file (mandatory).')
    parser.add_argument('--samples', dest='sample_file', help='Path of the sample file in the following record format: "sample_id;species_id;mother_id" (mandatory).')
    parser.add_argument('--imd_id', dest='imputed_md_id', help=f'Identification of the alternative allele for imputed missing data; default {xlib.Const.DEFAULT_IMPUTED_MD_ID}')
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species (mandatory).')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--out', dest='output_vcf_file', help='Path of output VCF file (mandatory).')
    parser.add_argument('--stats', dest='stats_file', help='Path of statistics file (mandatory).')
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

    # check "stats_file"
    if args.output_vcf_file is None:
        xlib.Message.print('error', '*** The statistics file is not indicated in the input arguments.')
        OK = False

    # check "stats_file"
    if args.output_vcf_file is None:
        xlib.Message.print('error', '*** The statistics file is not indicated in the input arguments.')
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

def collapse_indels(input_vcf_file, sample_file, imputed_md_id, sp1_id, sp2_id, hybrid_id, output_vcf_file, stats_file, tvi_list):
    '''
    Collapses the variant records corresponding to an indel in a VCF file.
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

    # open the statistics file
    if stats_file.endswith('.gz'):
        try:
            stats_file_id = gzip.open(stats_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', stats_file)
    else:
        try:
            stats_file_id = open(stats_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', stats_file)

    # write the statistics header
    stats_file_id.write( '"seq_id";"position";"records";"length";"imputed"\n')

    # initialize counters
    input_record_counter = 0
    total_variant_counter = 0
    collapsed_variant_counter = 0
    created_indel_counter = 0

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
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Collapsed variants ... {collapsed_variant_counter:8d} - Created indels ... {created_indel_counter}')

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
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Collapsed variants ... {collapsed_variant_counter:8d} - Created indels ... {created_indel_counter}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process variant record
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            xlib.Message.print('trace', f'Iniciando...')

            # set the sequence identification and position control variables
            w_seq_id = data_dict['chrom']
            w_position = int(data_dict['pos'])

            # initialize the record counter of the "actual" variant
            actual_variant_record_counter = 0

            # initialize the reference bases (field REF)
            reference_bases = ''

            # initialize the found best sample list control variable
            found_best_sample_list = False

            # initialize the collapse control variable
            collapse = True

            # process variant records of same "actual" variant 
            while record != '' and not record.startswith('##') and not record.startswith('#CHROM') and data_dict['chrom'] == w_seq_id and int(data_dict['pos']) == w_position + actual_variant_record_counter and collapse:

                xlib.Message.print('trace', f'Inside the loop')
                xlib.Message.print('trace', f'data_dict["chrom"]: {data_dict["chrom"]} - w_seq_id: {w_seq_id} - position: {data_dict["pos"]} - w_position: {w_position} - actual_variant_record_counter: {actual_variant_record_counter}')

                # add set the variant identification
                variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'
                if variant_id in tvi_list: xlib.Message.print('trace', f'\n\n\n\nseq_id: {data_dict["chrom"]} - position {data_dict["pos"]}')

                # add 1 to the read sequence counter
                input_record_counter += 1

                # add 1 to the total variant counter
                total_variant_counter += 1

                # add 1 to the record counter of the "actual" variant
                actual_variant_record_counter += 1

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

                # initialize imputation control variable
                imputed_adult_count = 0

                # check 
                for i in range(sample_number):

                    # only when the sample is adult
                    if mother_id_list[i] == 'NONE':

                        # check if there are imputed data
                        if sample_gt_left_list[i] == imputed_md_id or sample_gt_right_list[i] == imputed_md_id:
                            imputed_adult_count += 1
                
                xlib.Message.print('trace', f'variant_id: {variant_id} - imputed_adult_count: {imputed_adult_count}')

                # concat the current reference bases to the new reference bases
                reference_bases = f'{reference_bases}{data_dict["ref"]}'

                # if there are not imputed adults
                if imputed_adult_count == 0:
                    id = data_dict['id']
                    alternative_alleles = data_dict['alt']
                    qual = data_dict['qual']
                    filter = data_dict['filter']
                    info = data_dict['info']
                    format = data_dict['format']
                    best_sample_list = data_dict['sample_list']
                    collapse = False

                # if there are imputed adults
                else:

                    if actual_variant_record_counter == 1:
                        id = data_dict['id']
                        alternative_alleles = data_dict['alt']
                        qual = data_dict['qual']
                        filter = data_dict['filter']
                        info = data_dict['info']
                        format = data_dict['format']
                        best_sample_list = data_dict['sample_list']
                        if alternative_alleles == xlib.get_md_symbol():
                            found_best_sample_list = True

                    elif not found_best_sample_list and data_dict['alt'] == xlib.get_md_symbol():
                        id = data_dict['id']
                        alternative_alleles = xlib.get_md_symbol()
                        qual = data_dict['qual']
                        filter = data_dict['filter']
                        info = data_dict['info']
                        format = data_dict['format']
                        best_sample_list = data_dict['sample_list']
                        found_best_sample_list = True

                # read the next record of the input VCF file
                xlib.Message.print('trace', f'Reading ...')
                (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)
                if record != '': xlib.Message.print('trace', f'data_dict["chrom"]: {data_dict["chrom"]} - w_seq_id: {w_seq_id} - position: {data_dict["pos"]} - w_position: {w_position} - actual_variant_record_counter: {actual_variant_record_counter}')

            # write the variant record
            xlib.Message.print('trace', f'Writing VCF ...')
            xlib.Message.print('trace', f'w_seq_id: {w_seq_id} - w_position: {w_position} - actual_variant_record_counter: {actual_variant_record_counter}')
            sample_list_text = '\t'.join(best_sample_list)
            output_vcf_file_id.write(f'{w_seq_id}\t{w_position}\t{id}\t{reference_bases}\t{alternative_alleles}\t{qual}\t{filter}\t{info}\t{format}\t{sample_list_text}\n')

            # write the collapsing statistics  record
            xlib.Message.print('trace', f'Writing stats...')
            is_imputed = 'IMPUTED' if imputed_adult_count > 0 else '-'
            stats_file_id.write(f'{w_seq_id};{w_position};{actual_variant_record_counter};{len(reference_bases)};{is_imputed}\n')

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Collapsed variants ... {collapsed_variant_counter:8d} - Created indels ... {created_indel_counter}')

    xlib.Message.print('verbose', '\n')

    # close files
    input_vcf_file_id.close()
    output_vcf_file_id.close()
    stats_file_id.close()

    # print OK message 
    xlib.Message.print('info', f'The file {os.path.basename(output_vcf_file)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
