#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program calculates the global identity percentage of set of files with alignment
of sequences in FASTA format

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
import os
import re
import sys

import Bio.AlignIO

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

    # calculate the global identity percentage of set of files with alignment of sequences
    calculate_global_alignment_identity(args.input_dir, args.pattern, args.output_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program calculates the global identity percentage of set of files with alignment of sequences in FASTA format.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--indir', dest='input_dir', help='Path of the directory where cluster files with alignment of sequences are located(mandatory).')
    parser.add_argument('--pattern', dest='pattern', help='Pattern for selecting cluster files with alignment of sequences (mandatory).')
    parser.add_argument('--out', dest='output_file', help='Path of file where the global identity percentage is saved (mandatory).')
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
        xlib.Message.print('error', '*** The path of the directory where cluster files with alignment of sequences are located is not indicated in the input arguments.')
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

def calculate_global_alignment_identity(input_dir, pattern, output_file):
    '''
    Calculate the global identity percentage of set of files with alignment of
    sequences in FASTA format
    '''

    # initialize the cluster counter
    cluster_counter = 0

    # initialize the summation of identity percentages
    sum_identity_percentages = 0

    # initialize the summation of sequences
    sum_sequence_number = 0

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

        # calculate the alignment identity of each cluster file
        (identity_porcentage, sequence_number) = calculate_cluster_alignment_identity(cluster_file)

        # update the cluster counter and summation of identity percentages (only if the cluster has more than one sequence)
        if sequence_number > 1:
            cluster_counter += 1
            sum_identity_percentages += identity_porcentage

        # update the summation of sequences
        sum_sequence_number += sequence_number

        # write output data
        output_file_id.write(f'{os.path.basename(cluster_file)};{identity_porcentage};{sequence_number}\n')

    # calculate the global identity percentage
    if len(cluster_file_list) == 0:
        xlib.Message.print('info', 'Global identity percentage is not calculated because there are not files selected using the pattern.\n')
    elif cluster_counter == 0:
        xlib.Message.print('info', 'Global identity percentage is not calculated because there are not files with several sequences.\n')
    else:
        global_identity_percentage = sum_identity_percentages / cluster_counter
        xlib.Message.print('info', f'Global identity percentage: {global_identity_percentage:.2f}%\n')

    # save the global identity percentage in the output file
    if cluster_counter > 0:

        # write the identity percentage
        output_file_id.write(f'global identity percentage;{global_identity_percentage};{sum_sequence_number}\n')

        # close the output file
        output_file_id.close()

#-------------------------------------------------------------------------------

def calculate_cluster_alignment_identity(alignment_file):
    '''
    Calculates the global identity percentage of a file with alignment of
    sequences in FASTA format
    '''

    # get the sequences aligned
    try:
        alignment = Bio.AlignIO.read(alignment_file, 'fasta')
    except Exception as e:
        raise xlib.ProgramException(e, 'F001', alignment_file)
    xlib.Message.print('info', f'File: {os.path.basename(alignment_file)}')
    xlib.Message.print('info', alignment)

    # get the total lenght of the alignment
    total_length = len(alignment[0])

    # initialize the count of identical position
    identical_count = 0

    for i in range(total_length):
        column = alignment[:, i]
        xlib.Message.print('verbose', f'column {i}: {column} - {set(column)}\n')
        if len(set(column)) == 1:
            identical_count += 1

    # calculate the identity percentage
    identity_percentage = (identical_count / total_length) * 100
    xlib.Message.print('info', f'Identify percentage: {identity_percentage:.2f}%')

    # return the identity percentage and sequence number
    return identity_percentage, len(alignment)

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
