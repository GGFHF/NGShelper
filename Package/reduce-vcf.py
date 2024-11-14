#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program reduces variants from a VCF file.

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
import random
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

    # reduce randomly variants of a VCF file
    if args.reduction_method == 'RANDOM':
        reduce_variants_random_value(args.input_vcf_file, args.removal_probability, args.output_vcf_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program reduces variants from a VCF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='input_vcf_file', help='Path of input VCF file (mandatory).')
    parser.add_argument('--method', dest='reduction_method', help=f'Reduction method (mandatory): {xlib.get_vcf_reduction_code_list_text()}.')
    parser.add_argument('--remprob', dest='removal_probability', help='Removal probability (mandatory)')
    parser.add_argument('--out', dest='output_vcf_file', help='Path of the output VCF file (mandatory).')
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

    # check "reduction_method"
    if args.reduction_method is None:
        xlib.Message.print('error', '*** The reduction method is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.reduction_method, xlib.get_vcf_reduction_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The reduction method has to be {xlib.get_vcf_reduction_code_list_text()}.')
        OK = False
    else:
        args.reduction_method = args.reduction_method.upper()

    # check "removal_probability"
    if args.removal_probability is None:
        xlib.Message.print('error', '*** The removal probability is not indicated the input arguments.')
        OK = False
    elif not xlib.check_float(args.removal_probability, minimum=0.0, maximum=1.0):
        xlib.Message.print('error', 'The removal probability has to be a float number between 0.0 and 1.0.')
        OK = False
    else:
        args.removal_probability = float(args.removal_probability)

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

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def reduce_variants_random_value(input_vcf_file, removal_probability, output_vcf_file):
    '''
    Reduce randomly variants of a VCF file taking account a removal probalility.
    '''

    # initialize the sample number
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

    # initialize counters
    input_record_counter = 0
    input_variant_counter = 0
    output_variant_counter = 0

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
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Input variants ... {input_variant_counter:8d} - Output variants ... {output_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # get the record data list
            record_data_list = data_dict['record_data_list']

            # set the sample number
            sample_number = len(record_data_list) - 9

            # write the column description record
            output_vcf_file_id.write(record)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Input variants ... {input_variant_counter:8d} - Output variants ... {output_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process variant record
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # add 1 to the input variant counter
            input_variant_counter += 1

            # check the removal probability
            if removal_probability < random.random():

                # write the variant record
                output_vcf_file_id.write(record)

                # add 1 to the output variant counter
                output_variant_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Input variants ... {input_variant_counter:8d} - Output variants ... {output_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    xlib.Message.print('verbose', '\n')

    # close files
    input_vcf_file_id.close()
    output_vcf_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The output VCF file {os.path.basename(output_vcf_file)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
