#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program unifies the FASTA files of the consensus sequences of a set of
clusters into a single file.

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

    # unifies the FASTA files of the consensus sequences of a set of clusters into a single file
    unify_consensus_seqs(args.input_dir, args.pattern, args.output_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program unifies the FASTA files of the consensus sequences of a set of clusters into a single file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--indir', dest='input_dir', help='Path of the directory where FASTA files of consensus sequences are located(mandatory).')
    parser.add_argument('--pattern', dest='pattern', help='Pattern for selecting FASTA files of consensus sequences (mandatory).')
    parser.add_argument('--out', dest='output_file', help='Path of FASTA file with unified consensus sequences (mandatory).')
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
        xlib.Message.print('error', '*** The path of the directory where FASTA files of consensus sequences is not indicated in the input arguments.')
        OK = False
    elif not os.path.exists(os.path.dirname(args.input_dir)):
        xlib.Message.print('error', f'*** The directory {args.input_dir} does not exist.')
        OK = False

    # check "pattern"
    if args.pattern is None:
        xlib.Message.print('error', '*** The pattern for selecting cluster files is not indicated in the input arguments.')
        OK = False

    # check "output_file"
    if args.output_file is None:
        xlib.Message.print('error', '*** The file for saving the global identity percentage is not indicated in the input arguments.')
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

def unify_consensus_seqs(input_dir, pattern, output_file):
    '''
    Unify the FASTA files of the consensus sequences of a set of clusters into
    a single file.
    '''

    # initialize the cluster counter
    cluster_counter = 0

    # open the output file
    try:
        output_file_id = open(output_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', output_file)

    # get the list of cluster files
    cluster_file_list = []
    for cluster_file in sorted(os.listdir(input_dir)):
        if re.match(pattern, cluster_file):
            cluster_file_list.append(f'{input_dir}{os.sep}{cluster_file}')

    # for each cluster file in the list of cluster files
    for cluster_file in sorted(cluster_file_list):

        # add 1 to the cluster counter
        cluster_counter += 1

        # get the cluster identification
        asterisk_pos = pattern.find('*')
        last_characters = pattern[asterisk_pos + 1:]
        start_pos = cluster_file.rfind('cluster')
        end_pos = cluster_file.find(last_characters)
        cluster_id = cluster_file[start_pos:end_pos]

        # open the cluster file
        try:
            cluster_file_id = open(cluster_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', cluster_file)


        # read the first record of the cluster file
        record = cluster_file_id.readline()

        # while there are records in cluster file
        while record != '':

            # process the head record
            if record.startswith('>'):

                # initialize the sequence
                seq = ''

                # write the sequence identification
                output_file_id.write(f'>{cluster_id}\n')

                # read the next record
                record = cluster_file_id.readline()

            else:

                # control the FASTA format
                raise xlib.ProgramException('', 'F006', cluster_file, 'FASTA')

            # while there are records and they are sequence
            while record != '' and not record.startswith('>'):

                # concatenate the record to the sequence
                seq += record.strip()

                # read the next record of Fcluster file
                record = cluster_file_id.readline()

            # write the sequence
            output_file_id.write(f'{seq.lstrip("xX").rstrip("xX")}\n')

        xlib.Message.print('verbose', f'processed clusters #: {cluster_counter}\r')

        # close the cluster file
        cluster_file_id.close()

    xlib.Message.print('verbose', '\n')

    # close the output file
    output_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
