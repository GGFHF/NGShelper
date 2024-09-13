#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program purges a Structure file.

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

    # purge the Structure file
    if args.swap_type == '2TO1':
        swap_structure_2to1(args.input_structure_file, args.output_structure_file, args.info_col_number)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program purges a Structure input file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--input', dest='input_structure_file', help='Path of the Structure input file (mandatory).')
    parser.add_argument('--out', dest='output_structure_file', help='Path of the purged file (mandatory).')
    parser.add_argument('--type', dest='swap_type', help=f'Swap type (mandatory): {xlib.get_structure_swap_type_code_list_text()}.')
    parser.add_argument('--infocols', dest='info_col_number', help=f'Number of columns with identification data; default: {xlib.Const.DEFAULT_STRUCTURE_INFO_COL_NUMBER}.')
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

    # check "input_structure_file"
    if args.input_structure_file is None:
        xlib.Message.print('error', '*** The Structure input file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.input_structure_file):
        xlib.Message.print('error', f'*** The file {args.input_structure_file} does not exist.')
        OK = False

    # check "output_structure_file"
    if args.output_structure_file is None:
        xlib.Message.print('error', '*** The Structure output file is not indicated in the input arguments.')
        OK = False

    # check "swap_type"
    if args.swap_type is None:
        xlib.Message.print('error', '*** The purge operation is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.swap_type, xlib.get_structure_swap_type_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The purge operation has to be {xlib.get_structure_swap_type_code_list_text()}.')
        OK = False
    else:
        args.swap_type = args.swap_type.upper()

    # check "info_col_number"
    if args.info_col_number is None:
        args.info_col_number = xlib.Const.DEFAULT_STRUCTURE_INFO_COL_NUMBER
    elif not xlib.check_int(args.info_col_number, minimum=1):
        xlib.Message.print('error', 'The number of columns with identification data has to be an integer number greater than  or equal to 1.')
        OK = False
    else:
        args.info_col_number = int(args.info_col_number)

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

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def swap_structure_2to1(input_structure_file, output_structure_file, info_col_number):
    '''
    Swap a Structure file with in two lines format (one allele in different rows)
    to another one in one line format (one allele in different columns).
    '''

    # initialize the data matrix (rows: samples (first row is the header); columns: variants)
    data_matrix = []
    row_number = 0
    col_number = 0

    # open the input Structure file
    if input_structure_file.endswith('.gz'):
        try:
            input_structure_file_id = gzip.open(input_structure_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', input_structure_file)
    else:
        try:
            input_structure_file_id = open(input_structure_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', input_structure_file)

    # initialize input record counter
    input_record_counter = 0

    # read first record
    record = input_structure_file_id.readline()

    # while there are records in the Structure file
    while record != '':

        # add 1 to the record counter
        input_record_counter += 1

        # split the record data
        record_data_list = []
        start = 0
        for end in [i for i, chr in enumerate(record) if chr == '\t']:
            record_data_list.append(record[start:end].strip())
            start = end + 1
        record_data_list.append(record[start:].strip('\n').strip())

        # set and verify the column number
        if col_number == 0:
            col_number = len(record_data_list)
        elif col_number != len(record_data_list):
            raise xlib.ProgramException('', 'L014')

        # append record data to data matrix
        data_matrix.append(record_data_list)

        # print the input record counter
        xlib.Message.print('verbose', f'\rProcessed input records ... {input_record_counter:8d}')

        # read next record
        record = input_structure_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # set the row number
    row_number = input_record_counter

    # close the Structure file
    input_structure_file_id.close()

    # open the output purged file
    if output_structure_file.endswith('.gz'):
        try:
            output_structure_file_id = gzip.open(output_structure_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_structure_file)
    else:
        try:
            output_structure_file_id = open(output_structure_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_structure_file)

    # initialize output record counter
    output_record_counter = 0

    # write the head record
    data_list = []
    for j in range(info_col_number):
        data_list.append(data_matrix[0][j])
    for j in range(info_col_number, col_number):
        data_list.append(data_matrix[0][j])
        data_list.append(data_matrix[0][j])
    head_record = '\t'.join(data_list)
    output_structure_file_id.write(f'{head_record}\n')
    xlib.Message.print('verbose', f'\rWritten output records ... {output_record_counter:8d}')

    # write data record
    for i in range(1, row_number, 2):
        data_list = []
        for j in range(info_col_number):
            data_list.append(data_matrix[i][j])
        for j in range(info_col_number, col_number):
            data_list.append(data_matrix[i][j])
            data_list.append(data_matrix[i + 1][j])
        head_record = '\t'.join(data_list)
        output_structure_file_id.write(f'{head_record}\n')
        output_record_counter += 1
        xlib.Message.print('verbose', f'\rWritten output records ... {output_record_counter:8d}')

    xlib.Message.print('verbose', '\n')

    # close file
    output_structure_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The output file {os.path.basename(output_structure_file)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
