#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program extracts genomic features from a GFF file corresponding to the variant
of a VCF file.

This software has been developed by:

    GI en especies leñosas (WooSp)
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

    # extract genomic features from a GFF file
    extract_ff_features(args.input_gff_file, args.gff_format, args.vcf_file, args.output_gff_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program extracts genomic features from a GFF file corresponding to the variant of a VCF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--gff', dest='input_gff_file', help='Path of the GFF file (mandatory).')
    parser.add_argument('--format', dest='gff_format', help='The format of the transcript GFF file: GFF3; default: GFF3.')
    parser.add_argument('--vcf', dest='vcf_file', help='Path of the VCF file (mandatory).')
    parser.add_argument('--out', dest='output_gff_file', help='Path of the output GFF file with the selected features (mandatory).')
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

    # check "input_gff_file"
    if args.input_gff_file is None:
        xlib.Message.print('error', '*** The input GFF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.input_gff_file):
        xlib.Message.print('error', f'*** The file {args.input_gff_file} does not exist.')
        OK = False

    # check "gff_format"
    if args.gff_format is None:
        args.gff_format = 'GFF3'
    elif args.gff_format.upper() != 'GFF3':
        xlib.Message.print('error', '*** The format of the GFF file has to be GFF3.')
        OK = False
    else:
        args.gff_format = args.gff_format.upper()

    # check "vcf_file"
    if args.vcf_file is None:
        xlib.Message.print('error', '*** The VCF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.vcf_file):
        xlib.Message.print('error', f'*** The file {args.vcf_file} does not exist.')
        OK = False

    # check "output_gff_file"
    if args.output_gff_file is None:
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

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def extract_ff_features(input_gff_file, gff_format, vcf_file, output_gff_file):
    '''
    Extract genomic features from a GFF file corresponding to the variant of a VCF file.
    '''

    # initialize the variant dictionary
    variant_dict = {}

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

            # add the sequence and position to the variant dictionary
            position_list = variant_dict.get(data_dict['chrom'], [])
            try:
                pos = int(data_dict['pos'])
            except Exception as e:
                raise xlib.ProgramException(e, 'L005', data_dict['chrom'], data_dict['pos'])
            position_list.append(pos)
            variant_dict[data_dict['chrom']] = position_list

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record of the VCF file
            (record, _, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number=0, check_sample_number=False)

    xlib.Message.print('verbose', '\n')

    # close VCF file
    vcf_file_id.close()

    # open the input GFF file
    if input_gff_file.endswith('.gz'):
        try:
            input_gff_file_id = gzip.open(input_gff_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', input_gff_file)
    else:
        try:
            input_gff_file_id = open(input_gff_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', input_gff_file)

    # open the output GFF file
    if output_gff_file.endswith('.gz'):
        try:
            output_gff_file_id = gzip.open(output_gff_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_gff_file)
    else:
        try:
            output_gff_file_id = open(output_gff_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_gff_file)

    # initialize counters
    input_record_counter = 0
    output_record_counter = 0

    # read the first record
    record = input_gff_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to input record counter
        input_record_counter += 1

        # process data records
        if not record.startswith('#'):

            # extract data
            # record format: seq_id\tsource\ttype\tstart\tend\tscore\tstrand\tphase\tattributes
            data_list = []
            pos_1 = 0
            for pos_2 in [i for i, chr in enumerate(record) if chr == '\t']:
                data_list.append(record[pos_1:pos_2].strip())
                pos_1 = pos_2 + 1
            data_list.append(record[pos_1:].strip('\n').strip())
            try:
                seq_id = data_list[0]
                start = int(data_list[3])
                end = int(data_list[4])
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(input_gff_file), record_counter)

            # get the position of the sequence identification from the variant dictionary
            position_list = variant_dict.get(seq_id, [])

            # check if the feature has variants
            are_there_variants = False
            found_position_list = []
            for position in position_list:
                if position >= start and position <= end:
                    are_there_variants = True
                    found_position_list.append(str(position))

            # if the feature has variants, write in the output file
            if are_there_variants:
                fragment_id = f'{seq_id[:seq_id.find(".")]}_{"-".join(found_position_list)}'
                output_record = f'{record.strip()}\t{",".join(found_position_list)}\t{fragment_id}\n'
                output_gff_file_id.write(output_record)
                output_record_counter += 1

        # print record counter
        xlib.Message.print('verbose', f'\rGFF file: {input_record_counter} processed records - {output_record_counter} selected records.')

        # read the next record
        record = input_gff_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close files
    input_gff_file_id.close()
    output_gff_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
