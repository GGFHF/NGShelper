#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program filters a FASTA file according to the sequence length.

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

    # filter sequences
    filter_sequences_bylen(args.fasta_file, args.output_file, args.minlen, args.maxlen)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program filters a FASTA file according to the sequence length.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--fasta', dest='fasta_file', help='Path of FASTA file (mandatory)')
    parser.add_argument('--output', dest='output_file', help='Path of a output file where sequences filtered will be saved.')
    parser.add_argument('--minlen', dest='minlen', help=f'Sequences with length values less than this value will be filtered (default: {xlib.Const.DEFAULT_MINLEN}).')
    parser.add_argument('--maxlen', dest='maxlen', help=f'Sequences with length values greater than this value will be filtered (default: {xlib.Const.DEFAULT_MAXLEN}).')
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

    # check "fasta_file"
    if args.fasta_file is None:
        xlib.Message.print('error', '*** The input FASTA file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.fasta_file):
        xlib.Message.print('error', f'*** The file {args.fasta_file} does not exist.')
        OK = False

    # check the output_file value
    if args.output_file is None:
        xlib.Message.print('error', '*** A output file where sequences filtered will be saved is not indicated in the input arguments.')
        OK = False
    else:
        try:
            if not os.path.exists(os.path.dirname(args.output_file)):
                os.makedirs(os.path.dirname(args.output_file))
        except Exception as e:
            xlib.Message.print('error', f'*** EXCEPTION: "{e}".')
            xlib.Message.print('error', f'*** The directory {os.path.dirname(args.output_file)} of the file {args.output_file} is not valid.')
            OK = False

    # check the minlen value
    if args.minlen is None:
        args.minlen = xlib.Const.DEFAULT_MINLEN
    elif not xlib.check_int(args.minlen, minimum=1):
        xlib.Message.print('error', '*** The minlen has to be a integer number greater than 0.')
        OK = False
    else:
        args.minlen = int(args.minlen)

    # check the maxlen value
    if args.maxlen is None:
        args.maxlen = xlib.Const.DEFAULT_MAXLEN
    elif not xlib.check_int(args.maxlen, minimum=1):
        xlib.Message.print('error', '*** The maxlen has to be a integer number greater than 0.')
        OK = False
    else:
        args.maxlen = int(args.maxlen)

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

    # check if maxlen value is greater or equal than minlen value
    if OK:
        if args.maxlen < args.minlen:
            xlib.Message.print('error', '*** The maxlen value has to be greater than or equal to minlen.')
            OK = False

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def filter_sequences_bylen(fasta_file, output_file, minlen, maxlen):
    '''
    Filter sequences according to their length.
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
    read_seq_counter = 0
    written_seq_counter = 0

    # read the first record of FASTA file
    record = fasta_file_id.readline()

    # while there are records in FASTA file
    while record != '':

        # process the head record
        if record.startswith('>'):

            # extract the identification
            id = record[1:].strip('\n')

            # initialize the sequence
            seq = ''

            # read the next record
            record = fasta_file_id.readline()

        else:

            # control the FASTA format
            raise xlib.ProgramException('', 'F006', fasta_file, 'FASTA')

        # while there are records and they are sequence
        while record != '' and not record.startswith('>'):

            # concatenate the record to the sequence
            seq += record.strip()

            # read the next record of FASTA file
            record = fasta_file_id.readline()

        # add 1 to the read sequence counter
        read_seq_counter += 1

        # write the sequence if its length is between the minimum and maximum lengths
        if len(seq) >= minlen and len(seq) <= maxlen:
            try:
                output_file_id.write(f'>{id}\n')
                output_file_id.write(f'{seq}\n')
            except Exception as e:
                raise xlib.ProgramException(e, 'F001', output_file)
            # add 1 to save trascripts count
            written_seq_counter += 1

        # print the counters
        xlib.Message.print('verbose', f'\rProcessed seqs ... {read_seq_counter:8d} - Extracted seqs ... {written_seq_counter:8d}')

    xlib.Message.print('verbose', '\n')

    # close files
    fasta_file_id.close()
    output_file_id.close()

    # print OK message
    print(f'\nThe file {os.path.basename(output_file)} containing the selected sequences is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
