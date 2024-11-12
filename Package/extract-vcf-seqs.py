#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program extracts sequences from a VCF file.

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

    # extract sequences
    extract_sequences(args.vcf_file, args.id_file, args.extract_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program extracts sequences from a VCF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='vcf_file', help='Path of input VCF file (mandatory).')
    parser.add_argument('--id', dest='id_file', help='Path of the sequence identification file in plane text (mandatory)')
    parser.add_argument('--extract', dest='extract_file', help='Path of extracted VCF file (mandatory)')
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

    # check "vcf_file"
    if args.vcf_file is None:
        xlib.Message.print('error', '*** The input VCF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.vcf_file):
        xlib.Message.print('error', f'*** The file {args.vcf_file} does not exist.')
        OK = False

    # check "id_file"
    if args.id_file is None:
        xlib.Message.print('error', '*** The sequence identification file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.id_file):
        xlib.Message.print('error', f'*** The file {args.id_file} does not exist.')
        OK = False

    # check "extract_file"
    if args.extract_file is None:
        xlib.Message.print('error', '*** The extracted VCF file is not indicated in the input arguments.')

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

def extract_sequences(vcf_file, id_file, extract_file):
    '''
    Extract sequences from a VCF file.
    '''

    # get the identification data
    (seq_id_list, seq_id_dict) = xlib.get_id_data(id_file)

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

    # open the output VCF file with the extracted sequences
    if extract_file.endswith('.gz'):
        try:
            extract_file_id = gzip.open(extract_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', extract_file)
    else:
        try:
            extract_file_id = open(extract_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', extract_file)

    # initialize counters
    input_record_counter = 0
    output_record_counter = 0

    # read the first record of VCF file
    record = vcf_file_id.readline()

    # while there are records in VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            if record.startswith('##contig'):

                # get the sequence identification
                seq_id = ''
                i1 = 13
                i2 = record.find(',', i1)
                if i2 > -1:
                    seq_id = record[i1:i2]

                # write the record if the sequence identification is in the sequence identification list
                if seq_id in seq_id_list:
                    extract_file_id.write(record)
                    output_record_counter += 1

            else:

                # write the record
                extract_file_id.write(record)
                output_record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Output records ... {output_record_counter:8d}')

            # read the next record
            record = vcf_file_id.readline()

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # write the record
            extract_file_id.write(record)
            output_record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Output records ... {output_record_counter:8d}')

            # read the next record
            record = vcf_file_id.readline()

        # process variant record
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # get the sequence identification
            seq_id = ''
            tabpos = record.find('\t')
            if tabpos > -1:
                seq_id = record[:tabpos]

            # write the record if the sequence identification is in the sequence identification list
            if seq_id in seq_id_list:
                extract_file_id.write(record)
                output_record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Output records ... {output_record_counter:8d}')

            # read the next record
            record = vcf_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close files
    vcf_file_id.close()
    extract_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The file {os.path.basename(extract_file)} containing the extracted sequences is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
