#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program filters a SSR file selecting SSRs included in a COS.

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

    # filter SSRs
    filter_ssrs(args.cos_file, args.ssr_file, args.output_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program filters a SSR file selecting SSRs included in a COS.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--cos', dest='cos_file', help='Path of COS file in FASTA format (mandatory)')
    parser.add_argument('--ssr', dest='ssr_file', help='Path of SSR file in TSV format (mandatory)')
    parser.add_argument('--output', dest='output_file', help='Path of a output file where filtered SSRs will be saved.')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def check_args(args):
    '''
    Verity the input arguments data.
    '''

    # initialize the control variable
    OK = True

    # check "cos_file"
    if args.cos_file is None:
        xlib.Message.print('error', '*** The input COS file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.cos_file):
        xlib.Message.print('error', f'*** The file {args.cos_file} does not exist.')
        OK = False

    # check "ssr_file"
    if args.ssr_file is None:
        xlib.Message.print('error', '*** The input SSR file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.ssr_file):
        xlib.Message.print('error', f'*** The file {args.ssr_file} does not exist.')
        OK = False

    # check the output_file value
    if args.output_file is None:
        xlib.Message.print('error', '*** A output file where filtered SSR will be saved is not indicated in the input arguments.')
        OK = False
    else:
        try:
            if not os.path.exists(os.path.dirname(args.output_file)):
                os.makedirs(os.path.dirname(args.output_file))
        except Exception as e:
            xlib.Message.print('error', f'*** EXCEPTION: "{e}".')
            xlib.Message.print('error', f'*** The directory {os.path.dirname(args.output_file)} of the file {args.output_file} is not valid.')
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

def filter_ssrs(cos_file, ssr_file, output_file):
    '''
    Filter a SSR file transcripts selecting SSRs included in a COS.
    '''

    # initialize the contig dictionary
    contig_dict = xlib.NestedDefaultDict()

    # open the COS file
    if cos_file.endswith('.gz'):
        try:
            cos_file_id = gzip.open(cos_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', cos_file)
    else:
        try:
            cos_file_id = open(cos_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', cos_file)

    # initialize counters
    cos_record_counter = 0
    cos_seq_counter = 0

    # read the first record of COS file
    record = cos_file_id.readline()
    cos_record_counter += 1

    # while there are records in COS file
    while record != '':

        # process the head record
        if record.startswith('>'):

            # add 1 to the COS sequences counter
            cos_seq_counter += 1

            # extract head data
            head_data = record[1:].strip('\n')
            head_data_list = []
            pos_1 = 0
            for pos_2 in [i for i, char in enumerate(head_data) if char == ':']:
                head_data_list.append(head_data[pos_1:pos_2])
                pos_1 = pos_2 + 1
            head_data_list.append(head_data[pos_1:].strip('\n'))
            try:
                contig_name = head_data_list[2]
                cos_star_end = head_data_list[3]
                pos_sep = head_data_list[3].find('-')
                cos_start = int(head_data_list[3][:pos_sep])
                cos_end = int(head_data_list[3][pos_sep+1:])
            except Exception as e:
                raise xlib.ProgramException(e, 'F006', os.path.basename(cos_file), cos_record_counter)

            # initialize the COS sequence
            cos_seq = ''

            # read the next record
            record = cos_file_id.readline()
            cos_record_counter += 1

        else:

            # control the FASTA format
            raise xlib.ProgramException('', 'F006', cos_file, 'FASTA')

        # while there are records and they are COS sequence
        while record != '' and not record.startswith('>'):

            # concatenate the record to the COS sequence
            cos_seq += record.strip()

            # read the next record of COS file
            record = cos_file_id.readline()
            cos_record_counter += 1

        # add item in the COS dictionary
        # -- contig_dict[contig_id][cos_star_end] = {'cos_start': cos_start, 'cos_end': cos_end, 'cos_seq': cos_seq}
        contig_dict[contig_name][cos_star_end] = {'cos_start': cos_start, 'cos_end': cos_end}

        # print the COST sequence counter
        xlib.Message.print('verbose', f'\rProcessed COS seqs ... {cos_seq_counter:8d}')

    xlib.Message.print('verbose', '\n')

    # close files
    cos_file_id.close()

    # open the input SSR file
    if ssr_file.endswith('.gz'):
        try:
            ssr_file_id = gzip.open(ssr_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', ssr_file)
    else:
        try:
            ssr_file_id = open(ssr_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', ssr_file)

    # open the ouput SSR file
    if output_file.endswith('.gz'):
        try:
            output_file_id = gzip.open(output_file, mode='wt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', output_file)
    else:
        try:
            output_file_id = open(output_file, mode='w', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', output_file)

    # initialize counters
    input_record_counter = 0
    output_record_counter = 0

    # read the first record of SSR file
    record = ssr_file_id.readline()
    input_record_counter += 1

    # while there are records in input SSR file
    while record != '':

        # when record is the head
        if input_record_counter == 1:
            output_file_id.write(record)
            output_record_counter += 1

        # when record is not the head
        else:

            # extract SSR data
            ssr_data = record[1:].strip('\n')
            ssr_data_list = []
            pos_1 = 0
            for pos_2 in [i for i, char in enumerate(ssr_data) if char == '\t']:
                ssr_data_list.append(ssr_data[pos_1:pos_2])
                pos_1 = pos_2 + 1
            ssr_data_list.append(ssr_data[pos_1:].strip('\n'))
            try:
                contig_name = ssr_data_list[0][:ssr_data_list[0].find(' ')]
                ssr_start = int(ssr_data_list[2])
                ssr_end = int(ssr_data_list[3])
            except Exception as e:
                raise xlib.ProgramException(e, 'F006', os.path.basename(cos_file), cos_record_counter)

            # get COS data of the contig
            cos_data_dict = contig_dict.get(contig_name, {})

            # write the SSR when it is into a COS
            for _, cos_data_dict in cos_data_dict.items():
                cos_start = cos_data_dict['cos_start']
                cos_end = cos_data_dict['cos_end']
                if ssr_start <= cos_end and ssr_end >= cos_start:
                    output_file_id.write(record)
                    output_record_counter += 1
                    break

        # print the COST sequence counter
        xlib.Message.print('verbose', f'\rInput records ... {input_record_counter:8d} - Output records ... {output_record_counter:8d}')

        # read the next record of SSR file
        record = ssr_file_id.readline()
        input_record_counter += 1

    xlib.Message.print('verbose', '\n')

    # close files
    ssr_file_id.close()
    output_file_id.close()

    # print OK message
    print(f'\nThe file {os.path.basename(output_file)} containing the selected SSRs is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
