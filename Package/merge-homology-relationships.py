#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=unnecessary-pass

#-------------------------------------------------------------------------------

'''
This program merges the homology files of species related.

WARNING: All files must CSV and have the same record format.

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
import re
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

    # merge the homology files of species related
    merge_homology_relationships(args.input_dir, args.pattern, args.output_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program merges the homology files of species related.' \
        'WARNING: All files must CSV and have the same record format.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--indir', dest='input_dir', help='Path of the directory where homology files of species related are located (mandatory).')
    parser.add_argument('--pattern', dest='pattern', help='Pattern for selecting homology files (mandatory).')
    parser.add_argument('--out', dest='output_file', help='Path of file with homology relationships merged is saved (mandatory).')
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

    # check "input_dir"
    if args.input_dir is None:
        xlib.Message.print('error', '*** The path of the directory where homology files are located is not indicated in the input arguments.')
        OK = False
    elif not os.path.exists(os.path.dirname(args.input_dir)):
        xlib.Message.print('error', f'*** The directory {args.input_dir} does not exist.')
        OK = False

    # check "pattern"
    if args.pattern is None:
        xlib.Message.print('error', '*** The pattern for selecting homology files is not indicated in the input arguments.')
        OK = False

    # check "output_file"
    if args.output_file is None:
        xlib.Message.print('error', '*** The file with homology relationships merged is not indicated in the input arguments.')
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

def merge_homology_relationships(input_dir, pattern, output_file):
    '''
    Merges the homology files of species related.
    WARNING: All files must CSV and have the same record format.
    '''

    # initialize the records set
    records_set = set()

    # get the list of the homology files
    homology_files_list = []
    for homology_file in os.listdir(input_dir):
        if re.match(pattern, homology_file):
            homology_files_list.append(f'{input_dir}{os.sep}{homology_file}')

    # initialize the header text and columns number
    header_text = ''
    columns_number = 0

    # for each homology file in the list of homology files
    for homology_file in sorted(homology_files_list):

        # open the current homology file
        if homology_file.endswith('.gz'):
            try:
                homology_file_id = gzip.open(homology_file, mode='rt', encoding='iso-8859-1')
            except Exception as e:
                raise xlib.ProgramException(e, 'F002',  homology_file)
        else:
            try:
                homology_file_id = open(homology_file, mode='r', encoding='iso-8859-1')
            except Exception as e:
                raise xlib.ProgramException(e, 'F001', homology_file)

        # initialize the record counter
        record_counter = 0

        # initialize the header record control
        header_record = True

        # read the first record of current homology file
        record = homology_file_id.readline()

        # while there are records in the current homology file
        while record != '':

            # add 1 to record counter
            record_counter += 1

            # header record
            if header_record:

                # save the header text of the first homology file  ant its columns number
                if header_text == '':
                    header_text = record.strip()
                    columns_number = len(record.strip().split(';'))

                # other molology files
                else:

                    # check the columns number
                    if len(record.strip().split(';')) != columns_number:
                        raise xlib.ProgramException('', 'F009', record_counter, homology_file)

                # set False to the header record control
                header_record = False

            # records with homology relationships
            else:

                # check the columns number
                if len(record.strip().split(';')) != columns_number:
                    raise xlib.ProgramException('', 'F009', record_counter, homology_file)

                # add record to the records set
                records_set.add(record.strip())

            # read the next record of current homology file
            record = homology_file_id.readline()

        # close the current homology file
        homology_file_id.close()

    # open the file with homology relationships merged
    if output_file.endswith('.gz'):
        try:
            output_file_id = gzip.open(output_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_file)
    else:
        try:
            output_file_id = open(output_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_file)

    # write the head of the file with homology relationships merged
    output_file_id.write(f'{header_text}\n')

    # write the records set in the file with homology relationships merged
    for record in records_set:
        output_file_id.write(f'{record}\n')

    # close the file with homology relationships merged
    output_file_id.close()

    # print OK message
    xlib.Message.print('info', 'The file with the homology files merged is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
