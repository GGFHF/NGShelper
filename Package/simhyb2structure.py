#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program converts a output SimHyb file to the input Structure format in two lines.

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

    # convert a SimHyb file to Structure
    convert_simhyb_to_structure(args.simhyb_file, args.header_row_number, args.structure_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program converts a output SimHyb file to the input Structure format in two lines.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--simhyb', dest='simhyb_file', help='Path of the SimHyb file in TSV format (mandatory).')
    parser.add_argument('--headernum', dest='header_row_number', help='Number of the header rows in the SimHyb file (mandatory).')
    parser.add_argument('--structure', dest='structure_file', help='Path of the converted Structure file (mandatory).')
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

    # check "simhyb_file"
    if args.simhyb_file is None:
        xlib.Message.print('error', '*** The SimHyb file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.simhyb_file):
        xlib.Message.print('error', f'*** The file {args.simhyb_file} does not exist.')
        OK = False

    # check "header_row_number"
    if args.header_row_number is None:
        xlib.Message.print('error', '*** The header row number in the SimHyb file is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.header_row_number, minimum=0):
        xlib.Message.print('error', 'The header row number in the SimHyb file has to be an integer number greater than or equalt to 0.')
        OK = False
    else:
        args.header_row_number = int(args.header_row_number)

    # check "structure_file"
    if args.structure_file is None:
        xlib.Message.print('error', '*** The converted Structure file is not indicated in the input arguments.')
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

def convert_simhyb_to_structure(simhyb_file, header_row_number, structure_file):
    '''
    Convert a output SimHyb file to the input Structure format in two lines.
    '''

    # initialize the loci number
    loci_number = -1

    # open the SimHyb file
    if simhyb_file.endswith('.gz'):
        try:
            simhyb_file_id = gzip.open(simhyb_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', simhyb_file)
    else:
        try:
            simhyb_file_id = open(simhyb_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', simhyb_file)

    # open the Structure file
    if structure_file.endswith('.gz'):
        try:
            structure_file_id = gzip.open(structure_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', structure_file)
    else:
        try:
            structure_file_id = open(structure_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', structure_file)

    # initialize record counters
    input_record_counter = 0
    written_record_counter = 0

    # read the first record of the SimHyb file
    record = simhyb_file_id.readline()

    # while there are records in the VCF file
    while record != '':

        # add 1 to input record counter
        input_record_counter += 1

        # when the record has data
        if input_record_counter > header_row_number:

            # extract data
            data_list = []
            start = 0
            for end in [i for i, chr in enumerate(record) if chr == '\t']:
                data_list.append(record[start:end].strip())
                start = end + 1
            last_data = record[start:].strip('\n').strip()
            if last_data != '':
                data_list.append(record[start:].strip('\n').strip())

            # check the loci number
            if loci_number == -1:
                loci_number = len(data_list) - 12
                if (loci_number % 2) == 1:
                    raise xlib.ProgramException('', 'L011')
            elif loci_number != len(data_list) - 12:
                raise xlib.ProgramException('', 'L012')

            # get left and righ genotype lists of loci
            gt_left_list = []
            gt_right_list = []
            for i in range (12, len(data_list)):
                if (i % 2) == 0:
                    gt_left_list.append(data_list[i])
                else:
                    gt_right_list.append(data_list[i])

            # write the record corresponding to the left genotype list
            gt_left_list_text = '\t'.join(gt_left_list)
            structure_file_id.write(f'{data_list[0]}\t{data_list[1]}\t{gt_left_list_text}\n')
            written_record_counter += 1

            # write the record corresponding to the right genotype list
            gt_right_list_text = '\t'.join(gt_right_list)
            structure_file_id.write(f'{data_list[0]}\t{data_list[1]}\t{gt_right_list_text}\n')
            written_record_counter += 1

        # print the counters
        xlib.Message.print('verbose', f'\rProcessed SimHyb records ... {input_record_counter:8d} - Written Structure records ... {written_record_counter:8d}')

        # read the next record of the SimHyb file
        record = simhyb_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close file
    simhyb_file_id.close()
    structure_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The converted file {os.path.basename(structure_file)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
