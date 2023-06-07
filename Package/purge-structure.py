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
    if args.structure_input_format == '2' and args.purge_operation in ['DELCOL', 'CHAVAL']:
        purge_structure_input_format_2(args.input_structure_file, args.purge_operation, args.value, args.new_value, args.output_purged_file)

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
    parser.add_argument('--structure', dest='input_structure_file', help='Path of the Structure input file (mandatory).')
    parser.add_argument('--format', dest='structure_input_format', help=f'Structure input format (mandatory): {xlib.get_structure_input_format_code_list_text()}.')
    parser.add_argument('--operation', dest='purge_operation', help=f'Purge operation (mandatory): {xlib.get_structure_purge_code_list_text()}.')
    parser.add_argument('--value', dest='value', help='value to operate (mandatory)')
    parser.add_argument('--nvalue', dest='new_value', help='new value that replaces value when operation in CHAVAL (mandatory); else NONE (default)')
    parser.add_argument('--out', dest='output_purged_file', help='Path of the purged file (mandatory).')
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

    # check "structure_input_format"
    if args.structure_input_format is None:
        xlib.Message.print('error', '*** The Structure input format is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.structure_input_format, xlib.get_structure_input_format_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The Structure input format has to be {xlib.get_structure_input_format_code_list_text()}.')
        OK = False

    # check "purge_operation"
    is_ok_purge_operation = False
    if args.purge_operation is None:
        xlib.Message.print('error', '*** The purge operation is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.purge_operation, xlib.get_strcuture_purge_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The purge operation has to be {xlib.get_structure_purge_code_list_text()}.')
        OK = False
    else:
        args.purge_operation = args.purge_operation.upper()
        is_ok_purge_operation = True

    # check "value"
    if args.value is None:
        xlib.Message.print('error', '*** The value to perform the purge operation is not indicated the input arguments.')
        OK = False

    # check "new_value"
    if args.new_value is None and is_ok_purge_operation and args.purge_operation == 'CHAVAL':
        xlib.Message.print('error', '*** The new value to perform the purge operation is not indicated the input arguments.')
        OK = False
    elif args.new_value is None:
        args.new_value = ' NONE'

    # check "output_purged_file"
    if args.output_purged_file is None:
        xlib.Message.print('error', '*** The purged file is not indicated in the input arguments.')
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

def purge_structure_input_format_2(input_structure_file, purge_operation, value, new_value, output_purged_file):
    '''
    Purge a Structure file with format in two lines: one allele in different rows.
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
            print(f'col_number: {col_number}')
        elif col_number != len(record_data_list):
            print(f'record_data_list: {len(record_data_list)}')
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


    # if the operation is the change of a value by a new value
    if purge_operation == 'CHAVAL':

        # change the value
        for i in range(row_number):
            for j in range(col_number):
                if data_matrix[i][j] == value:
                    data_matrix[i][j] = new_value
                    xlib.Message.print('verbose', f'\rChanging data of the row {i + 1:d} - column {j + 1:d}')

        xlib.Message.print('verbose', '\n')

    # if the operation is the deletion of columns containing a determined value
    elif purge_operation == 'DELCOL':

        # detect columns with the determined value
        excluded_col_index_list = []
        for i in range(col_number):
            for j in range(row_number):
                if data_matrix[j][i] == value:
                    excluded_col_index_list.append(i)
                    break
        xlib.Message.print('trace', 'excluded_col_index_list: {}'.format(excluded_col_index_list))

        # delete columns containing the determined value
        excluded_col_index_list.reverse()
        for k in range(row_number):
            for l in excluded_col_index_list:
                data_matrix[k].pop(l)
            xlib.Message.print('verbose', f'\rDeleting columns of the row {k + 1:d}')

        xlib.Message.print('verbose', '\n')

    # open the output purged file
    if output_purged_file.endswith('.gz'):
        try:
            output_purged_file_id = gzip.open(output_purged_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_purged_file)
    else:
        try:
            output_purged_file_id = open(output_purged_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_purged_file)

    # initialize output record counter
    output_record_counter = 0

    # write data matrix
    for i in range(row_number):

        # write the record corresponding to the row
        data_matrix_i_text = '\t'.join(data_matrix[i])
        output_purged_file_id.write(f'{data_matrix_i_text}\n')

        # add 1 to the output record counter
        output_record_counter += 1
        xlib.Message.print('verbose', f'\rWritten output records ... {output_record_counter:8d}')

    xlib.Message.print('verbose', '\n')

    # close file
    output_purged_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The purged file {os.path.basename(output_purged_file)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
