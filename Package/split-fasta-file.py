#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program splits a FASTA file in several files.

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

    # split the FASTA file in several files
    split_fasta_file(args.input_fasta_file, args.nseq_perfile, args.output_dir)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program splits a FASTA file in several files.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--fasta', dest='input_fasta_file', help='Path of the input FASTA file (mandatory).')
    parser.add_argument('--nseq', dest='nseq_perfile', help='Number of sequences per output file (mandatory).')
    parser.add_argument('--outdir', dest='output_dir', help='Path of the output directory where the files will be saved (mandatory).')
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

    # check "input_fasta_file"
    if args.input_fasta_file is None:
        xlib.Message.print('error', '*** The input FASTA file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.input_fasta_file):
        xlib.Message.print('error', f'*** The file {args.input_fasta_file} does not exist.')
        OK = False

    # check "nseq_perfile"
    if args.nseq_perfile is None:
        xlib.Message.print('error', '*** The number of sequences per output file is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.nseq_perfile, minimum=1):
        xlib.Message.print('error', '*** The number of sequences per output file has to be an integer number greater than or equal to 1.')
        OK = False
    else:
        args.nseq_perfile = int(args.nseq_perfile)

    # check "output_dir"
    if args.output_dir is None:
        xlib.Message.print('error', '*** The path of the output directory where the files will be saved is not indicated in the input arguments.')
        OK = False
    else:
        try:
            if not os.path.exists(os.path.dirname(args.output_dir)):
                os.makedirs(os.path.dirname(args.output_dir))
        except Exception:    #pylint: disable=broad-exception-caught
            xlib.Message.print('error', f'*** The directory {args.output_dir} is not valid.')
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

def split_fasta_file(input_fasta_file, nseq_perfile, output_dir):
    '''
    Split a FASTA file in several files.
    '''

    # initialize the output file counter
    output_file_counter = 0

    # get the prefix of the output FASTA file
    file_name = os.path.basename(input_fasta_file)
    if input_fasta_file.endswith('.gz'):
        file_name = file_name[:-3]
    file_name_fragments = file_name.split('.')

    # open the input FASTA file
    if input_fasta_file.endswith('.gz'):
        try:
            input_fasta_file_id = gzip.open(input_fasta_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', input_fasta_file)
    else:
        try:
            input_fasta_file_id = open(input_fasta_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', input_fasta_file)

    # read the first record
    record = input_fasta_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to the output file counter
        output_file_counter += 1

        # build the name of the output FASTA file
        output_fasta_file = f'{output_dir}{os.sep}{file_name_fragments[0]}-{output_file_counter:03d}.{file_name_fragments[1]}'
        if input_fasta_file.endswith('.gz'):
            output_fasta_file = f'{output_fasta_file}.gz'

        # open the output FASTA file
        if output_fasta_file.endswith('.gz'):
            try:
                output_fasta_file_id = gzip.open(output_fasta_file, mode='wt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise xlib.ProgramException(e, 'F004', output_fasta_file)
        else:
            try:
                output_fasta_file_id = open(output_fasta_file, mode='w', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise xlib.ProgramException(e, 'F003', output_fasta_file)

        # initialize the record counter of the output FASTA file
        output_record_counter = 0

        # initialize the counter of sequence number written
        nseq_written_counter = 0

        # while there are records and the counter of sequence number written is less or equal to sequence number per file
        while record != '' and nseq_written_counter < nseq_perfile:

            # process the head record
            if record.startswith('>'):

                # write sequence identification record
                output_fasta_file_id.write(record)

                # add 1 to the counter of sequence number written
                nseq_written_counter += 1

                # add 1 to the record counter of the output FASTA file
                output_record_counter += 1

                # read the next record
                record = input_fasta_file_id.readline()

            else:
                # control the FASTA format
                raise xlib.ProgramException('', 'F006', output_fasta_file, 'FASTA')

            # while there are records and they are sequence
            while record != '' and not record.startswith('>'):

                # write sequence record
                output_fasta_file_id.write(record)

                # add 1 to the record counter of the output FASTA file
                output_record_counter += 1

                # read the next record
                record = input_fasta_file_id.readline()

            # print the counters
            xlib.Message.print('verbose', f'\rWritten seqs ... {nseq_written_counter:8d} - Written records ... {output_record_counter:8d}')

        # close output FASTA file
        output_fasta_file_id.close()

        xlib.Message.print('verbose', '\n')
        xlib.Message.print('verbose', f'{os.path.basename(output_fasta_file)} is created - Total seqs: {nseq_written_counter:8d} - Total records: {output_record_counter:8d}.')

    # close input FASTA file
    input_fasta_file_id.close()

    xlib.Message.print('verbose', '\n')
    xlib.Message.print('info', 'All output FASTA files are created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
