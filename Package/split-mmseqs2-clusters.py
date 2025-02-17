#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program splits a *all_seqs.fasta file yielded by MMseqs2 in several files
each containing a sequence cluster.

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

    # split the *all_seqs.fasta file yielded by MMseqs2 in several files each containing a sequence cluster
    split_fasta_file(args.allseqs_file, args.relationship_file, args.output_dir)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program splits a *all_seqs.fasta file yielded by MMseqs2\n' \
        'in several files each containing a sequence cluster.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--allseqs', dest='allseqs_file', help='Path of the *all_seqs.fasta file yielded by MMseqs2 (mandatory).')
    parser.add_argument('--relationships', dest='relationship_file', help='Path of the output file to keep the relationships between sequence identifications and cluster identifications (mandatory).')
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

    # check "allseqs_file"
    if args.allseqs_file is None:
        xlib.Message.print('error', '*** The *all_seqs.fasta is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.allseqs_file):
        xlib.Message.print('error', f'*** The file {args.allseqs_file} does not exist.')
        OK = False

    # check "relationship_file"
    if args.relationship_file is None:
        xlib.Message.print('error', '*** The path of the output file to keep relationships is not indicated in the input arguments.')
        OK = False

    # check "output_dir"
    if args.output_dir is None:
        xlib.Message.print('error', '*** The path of the output directory where the files will be saved is not indicated in the input arguments.')
        OK = False
    else:
        try:
            if not os.path.exists(os.path.dirname(args.output_dir)):
                os.makedirs(os.path.dirname(args.output_dir))
        except Exception:    #pylint: disable=broad-exception-caught
            xlib.Message.print('error', f'*** The directory {os.path.dirname(args.output_dir)} of the file {args.output_dir} is not valid.')
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

def split_fasta_file(allseqs_file, relationship_file, output_dir):
    '''
    Split a *all_seqs.fasta file yielded by MMseqs2 in several files
    each containing a sequence cluster.
    '''

    # initialize the output file counter
    output_file_counter = 0

    # initialize the indicator of output file opened
    is_there_output_file = False

    # open the relationship file
    if relationship_file.endswith('.gz'):
        try:
            relationship_file_id = gzip.open(relationship_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', relationship_file)
    else:
        try:
            relationship_file_id = open(relationship_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', relationship_file)

    # open the *all_seqs.fasta
    if allseqs_file.endswith('.gz'):
        try:
            allseqs_file_id = gzip.open(allseqs_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', allseqs_file)
    else:
        try:
            allseqs_file_id = open(allseqs_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', allseqs_file)

    # initialice the consecutive header record counter
    header_record_counter = 0

    # read the first record
    record = allseqs_file_id.readline()

    # while there are records
    while record != '':

        # process the header record
        if record.startswith('>'):

            # add 1 to the consecutive header record counter
            header_record_counter += 1

            # save the last header record
            last_header_record = record

        if header_record_counter == 2:

            # close the output file if open:
            if is_there_output_file:
                output_fasta_file_id.close()    #pylint: disable=used-before-assignment
                xlib.Message.print('verbose', f'{os.path.basename(output_fasta_file)} is created - Total seqs: {nseq_written_counter:2d}.')

            # add 1 to the output file counter
            output_file_counter += 1

            # build the name of the output FASTA file
            # -- output_fasta_file = f'{output_dir}{os.sep}{file_name_fragments[0]}-cluster{output_file_counter:06d}.{file_name_fragments[1]}'
            output_fasta_file = f'{output_dir}{os.sep}cluster{output_file_counter:06d}.fasta'

            # open the output FASTA file
            try:
                output_fasta_file_id = open(output_fasta_file, mode='w', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise xlib.ProgramException(e, 'F003', output_fasta_file)

            # set the indicator of output file opened
            is_there_output_file = True

            # initialice the consecutive header record counter
            header_record_counter = 0

            # initialize the counter of sequence number written
            nseq_written_counter = 0

        # process the sequence record
        if not record.startswith('>'):

            # write the last header record
            output_fasta_file_id.write(last_header_record)

            # write the sequence record
            output_fasta_file_id.write(record)

            # get the sequence identification
            seq_id = last_header_record[1:last_header_record.find(' ')]

            # get the description
            description_start_pos = last_header_record.find(' ') + 1
            description_end_pos = last_header_record.find('[') - 1
            description = last_header_record[description_start_pos:description_end_pos]

            # get the species
            species_start_pos = last_header_record.find('[') + 1
            species_end_pos = last_header_record.find(']')
            species = last_header_record[species_start_pos:species_end_pos]

            # write the relationship between the cluster and sequence identification and its description and species
            relationship_file_id.write(f'cluster{output_file_counter:06d};{seq_id};{description};{species}\n')

            # add 1 to the counter of sequence number written
            nseq_written_counter += 1

            # initialice the consecutive header record counter
            header_record_counter = 0

        # read the next record
        record = allseqs_file_id.readline()

    # close files
    allseqs_file_id.close()
    if is_there_output_file:
        output_fasta_file_id.close()
        xlib.Message.print('verbose', f'{os.path.basename(output_fasta_file)} is created - Total seqs: {nseq_written_counter:2d}.')

    xlib.Message.print('info', 'All output cluster files are created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
