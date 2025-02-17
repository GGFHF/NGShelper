#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program calculates haplotype statistics per locus from a ipyrad loci file.

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
import operator
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

    # calculate haplotype statistics
    calculate_haplotype_statistics(args.loci_file_path, args.stats_file_path)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program calculates haplotype statistics per locus from a ipyrad loci file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--loci_file', dest='loci_file_path', help='loci file path (mandatory)')
    parser.add_argument('--stats_file', dest='stats_file_path', help='statistics file path in CSV format (mandatory)')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def check_args(args):
    '''
    Verity the input arguments.
    '''

    # initialize the control variable
    OK = True

    # check loci_file_path
    if args.loci_file_path is None:
        xlib.Message.print('error', '*** A loci file path is not indicated in the input arguments.')
        OK = False
    else:
        if not os.path.isfile(args.loci_file_path):
            xlib.Message.print('error', f'*** The file {args.loci_file_path} does not exist.')
            OK = False
        if not args.loci_file_path.endswith('.loci'):
            xlib.Message.print('error', f'*** The file {args.loci_file_path} does not end in ".loci".')
            OK = False

    # check stats_file_path
    if args.stats_file_path is None:
        xlib.Message.print('error', '*** A statistics path is not indicated in the input arguments.')
        OK = False
    else:
        if not args.stats_file_path.endswith('.csv'):
            xlib.Message.print('error', f'*** The file {args.stats_file_path} does not end in ".csv".')
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

def calculate_haplotype_statistics(loci_file_path, stats_file_path):
    '''
    Calculates haplotype statistics per locus.
    '''

    # open the loci file
    try:
        loci_file_id = open(loci_file_path, mode='r', encoding='iso-8859-1')
    except Exception as e:
        raise xlib.ProgramException(e, 'F001', loci_file_path)

    # set the pattern of the locus id records
    pattern1 = r'^\/\/(.*)\|(.*)\|$'

    # set the pattern of the locus information records
    pattern2 = r'^(.*) (.*)$'

    # initialize the list of locus information records
    locus_line_list = []

    # initialize the dictionary of haplotype sequence number by locus
    haplotype_number_by_locus_dict = {}

    # initialize the dictionary of haplotype sequences in the locus
    haplotype_seqs_in_locus_dict = {}

    # read the first record of complete loci file
    record = loci_file_id.readline()

    # while there are records
    while record != '':

        # process the locus id record
        if record.startswith('//'):

            # extract the locus id
            mo = re.search(pattern1, record)
            variant_seq = mo.group(1)
            locus_id = mo.group(2)

            # write in locus statistics
            for i in range(len(locus_line_list)):

                # extract the taxon id and sequence
                mo = re.search(pattern2, locus_line_list[i])
                taxon_id = mo.group(1).strip()
                sequence = mo.group(2).strip()

                # add the sequence to the dictionary of haplotype sequences in the locus
                if sequence not in haplotype_seqs_in_locus_dict:
                    haplotype_seqs_in_locus_dict[sequence] = sequence

            # calculate de variant sequence
            variant_seq = variant_seq[-len(sequence):]
            xlib.Message.print('trace', f'locus_id: {locus_id:8} - variant_seq: >{variant_seq}<\n')

            # add the haplotype sequence number to the dictionary of haplotype sequence number by locus
            haplotype_number_by_locus_dict[locus_id] = len(haplotype_seqs_in_locus_dict.keys())

            # initialize the list of locus information records
            locus_line_list = []

            # initialize the dictionary of haplotype sequences in the locus
            haplotype_seqs_in_locus_dict = {}

        # process a locus information record
        else:

            # add the record to the list of locus information records
            locus_line_list.append(record)

        # read the next record of complete loci file
        record = loci_file_id.readline()

    # close file
    loci_file_id.close()

    # get a list of haplotype sequence number by locus sorted by locus identification
    haplotype_seqs_in_locus_list = sorted(haplotype_number_by_locus_dict.items(), key=operator.itemgetter(1))

    # open the statistics file
    try:
        print()
        with open(stats_file_path, mode='w', encoding='iso-8859-1') as stats_file_id:
            stats_file_id.write('"haplotype number","locus identification"\n')
            for locus_info in haplotype_seqs_in_locus_list:
                stats_file_id.write(f'{locus_info[1]},"locus_{locus_info[0]}"\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F001', stats_file_path)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
