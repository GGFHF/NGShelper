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
This program prints data of a selected variant list.
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

    # print selected variants of a VCF file
    print_variants(args.input_vcf_file, args.sample_file, args.sp1_id, args.sp2_id, args.hybrid_id, args.output_dir, args.variant_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program prints data of a selected variant list.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='input_vcf_file', help='Path of input VCF file (mandatory).')
    parser.add_argument('--samples', dest='sample_file', help='Path of the sample file in the following record format: "sample_id;species_id;mother_id" (mandatory).')
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species (mandatory).')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--variants', dest='variant_list', help='Variant identification list to print with format seq_id_1-pos_1,seq_id_2-pos_2,...,seq_id_n-pos_n.')
    parser.add_argument('--outdir', dest='output_dir', help='Path of output directoty where files with selected variant data are saved (mandatory).')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')

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

    # check "variant_list"
    if args.variant_list is None or args.variant_list == 'NONE':
        args.variant_list = []
    else:
        args.variant_list = xlib.split_literal_to_string_list(args.variant_list)

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

def print_variants(vcf_file, sample_file, sp1_id, sp2_id, hybrid_id, output_dir, selected_variant_list):
    '''
    Filter and fixes variant data of a VCF file.
    '''

    # initialize the found variant list
    found_variant_list = []

    # initialize the sample number
    sample_number = 0

    # get the sample data
    sample_dict = xlib.get_sample_data(sample_file, sp1_id, sp2_id, hybrid_id)

    # initialize the sample, species and mother identification lists per variant and their maximum identification length 
    sample_id_list = []
    sample_id_max_len = 0
    species_id_list = []
    species_id_max_len = 0
    mother_id_list = []
    mother_id_max_len = 0

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

    # initialize counters
    input_record_counter = 0
    total_variant_counter = 0

    # read the first record of input VCF file
    (record, key, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

    # while there are records in input VCF file
    try:
        while record != '':

            # process metadata records
            while record != '' and record.startswith('##'):

                # add 1 to the read sequence counter
                input_record_counter += 1

                # print the counters
                xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Found variants ... {len(found_variant_list):8d}')

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
                        sample_id = sample_dict[record_data_list[i]]['sample_id']
                        species_id = sample_dict[record_data_list[i]]['species_id']
                        mother_id = sample_dict[record_data_list[i]]['mother_id']
                    except Exception as e:
                        raise xlib.ProgramException(e, 'L002', record_data_list[i])
                    sample_id_list.append(sample_id)
                    if len(sample_id) > sample_id_max_len: sample_id_max_len = len(sample_id)
                    species_id_list.append(species_id)
                    if len(species_id) > species_id_max_len: species_id_max_len = len(species_id)
                    mother_id_list.append(mother_id)
                    if len(mother_id) > mother_id_max_len: mother_id_max_len = len(mother_id)

                # check if the sample species list is empty
                if species_id_list == []:
                    raise xlib.ProgramException('', 'L003')

                # set the sample number
                sample_number = len(species_id_list)

                # print the counters
                xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Found variants ... {len(found_variant_list):8d}')

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
                    if sample_gt_list[i] not in xlib.get_md_code_list():
                        try:
                            sample_gt_left_list.append(int(sample_gt_list[i][:sep_pos]))
                            sample_gt_right_list.append(int(sample_gt_list[i][sep_pos+1:]))
                        except Exception as e:
                            raise xlib.ProgramException(e, 'L008', 'GT', data_dict['chrom'], data_dict['pos'])
                    else:
                        sample_gt_left_list.append(-1)
                        sample_gt_right_list.append(-1)

                # if the variant is in selected variant list
                if variant_id in selected_variant_list:

                    # add variant identification to the found variant list
                    found_variant_list.append(variant_id)

                    # set the output_file for saving the current variant data
                    if vcf_file.endswith('.gz'):
                        file_name, file_extension = os.path.splitext(os.path.basename(vcf_file[:-3]))
                    else:
                        file_name, file_extension = os.path.splitext(os.path.basename(vcf_file))
                    output_file = f'{output_dir}/{file_name}-{variant_id}.txt'

                    # open the output file
                    try:
                        output_file_id = open(output_file, mode='w', encoding='iso-8859-1', newline='\n')
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F003', output_file)

                    # print variant data
                    output_file_id.write(f'Variant: {variant_id}\n')
                    output_file_id.write('\n')
                    output_file_id.write(f' CHROM: {data_dict["chrom"]}\n')
                    output_file_id.write(f'   POS: {data_dict["pos"]}\n')
                    output_file_id.write(f'    ID: {data_dict["id"]}\n')
                    output_file_id.write(f'   REF: {data_dict["ref"]}\n')
                    output_file_id.write(f'   ALT: {data_dict["alt"]}\n')
                    output_file_id.write(f'  QUAL: {data_dict["qual"]}\n')
                    output_file_id.write(f'FILTER: {data_dict["filter"]}\n')
                    output_file_id.write(f'  INFO: {data_dict["info"]}\n')
                    output_file_id.write(f'FORMAT: {data_dict["format"]}\n')
                    output_file_id.write('\n')
                    output_file_id.write('Samples:\n')
                    for i in range(sample_number):
                        # -- output_file_id.write(f'{i:>6} - Sample id: {sample_id_list[i]:{sample_id_max_len}} - Species: {species_id_list[i]:{species_id_max_len}} - Mother id: {mother_id_list[i]:{mother_id_max_len}} - Left genotype: {sample_gt_left_list[i]:>2} - Right genotype: {sample_gt_right_list[i]: >2}\n')
                        output_file_id.write(f'{i:>6} - Sample id: {sample_id_list[i]:{sample_id_max_len}} - Species: {species_id_list[i]:{species_id_max_len}} - Mother id: {mother_id_list[i]:{mother_id_max_len}} - Genotype: {sample_gt_list[i]}\n')

                    # close output file
                    output_file_id.close()

                # print the counters
                xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Found variants ... {len(found_variant_list):8d}')

                # check if all variant are found
                if len(found_variant_list) == len(selected_variant_list):
                    raise xlib.BreakAllLoops

                # read the next record of the input VCF file
                (record, key, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

    except xlib.BreakAllLoops:
        pass

    xlib.Message.print('verbose', '\n')

    # control the printed variant counter
    if len(found_variant_list) == 0:
        xlib.Message.print('info', 'The selected variants are not found.')
    elif len(found_variant_list) < len(selected_variant_list):
        xlib.Message.print('info', 'There are variants non-found.')
    else:
        xlib.Message.print('info', 'All variants are found.')

    # close VCF file
    vcf_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The file {os.path.basename(output_file)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
