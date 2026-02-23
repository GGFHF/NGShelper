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
This program adds the species name to headers in a FASTA file.

This software has been developed by

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

    # adds the species name to headers in the input FASTA file
    add_species_in_headers(args.fasta_file, args.output_file, args.species_name)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program adds the species name to headers in a FASTA file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--species', dest='species_name', help='The species name (mandatory)')
    parser.add_argument('--fasta', dest='fasta_file', help='Path of FASTA file (mandatory)')
    parser.add_argument('--output', dest='output_file', help='Path of a output file where sequences filtered will be saved.')
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

    # check "species_name"
    if args.species_name is None:
        xlib.Message.print('error', '*** The species name is not indicated in the input arguments.')
        OK = False

    # check "fasta_file"
    if args.fasta_file is None:
        xlib.Message.print('error', '*** The input FASTA file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.fasta_file):
        xlib.Message.print('error', f'*** The file {args.fasta_file} does not exist.')
        OK = False

    # check the output_file value
    if args.output_file is None:
        xlib.Message.print('error', '*** The output FASTA file is not indicated in the input arguments.')
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

def add_species_in_headers(fasta_file, output_file, species_name):
    '''
    Add the species name to headers in the input FASTA file.
    '''

    # open the FASTA file
    if fasta_file.endswith('.gz'):
        try:
            fasta_file_id = gzip.open(fasta_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', fasta_file)
    else:
        try:
            fasta_file_id = open(fasta_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', fasta_file)

    # open the ouput file
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

    # initialize record counters
    records_counter = 0

    # read the first record of input FASTA file
    record = fasta_file_id.readline()

    # while there are records in input FASTA file
    while record != '':

        # add 1 to the records counter
        records_counter += 1

        # print the records counter
        xlib.Message.print('verbose', f'\rProcessed records ... {records_counter:8d}')

        # add the species name to header records
        if record.startswith('>'):

            record = f'{record.strip('\n').replace('\t', ' ')} [{species_name}]\n'

        # write the record in the output FASTA file
        output_file_id.write(record)

        # read the next record of input FASTA file
        record = fasta_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close files
    fasta_file_id.close()
    output_file_id.close()

    # print OK message
    print(f'\nThe file {os.path.basename(output_file)} with species name in headers is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
