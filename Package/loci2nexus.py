#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

'''
This software has been developed by:

    GI Sistemas Naturales e Historia Forestal (formerly known as GI Genetica, Fisiologia e Historia Forestal)
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

'''
This program builds a Nexus file from a ypirad loci file for a determinated
loci set to be used by BEAST software.
'''

#-------------------------------------------------------------------------------

import argparse
import os
import re
import sys

import xlib

#-------------------------------------------------------------------------------

def main(argv):
    '''
    Main line of the program.
    '''

    # check the operating system
    xlib.check_os()

    # get and check the arguments
    parser = build_parser()
    args = parser.parse_args()
    check_args(args)

    # build Nexus file
    build_nexus_file(args.selection_loci_id_file_path, args.complete_loci_file_path, args.selected_loci_file_path, args.nexus_file_path)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program builds a Nexus file from a ypirad loci file\nfor a determinated loci set to be used by BEAST software.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('-l', '--loci_id_file', dest='selection_loci_id_file_path', help='loci id file path to select (mandatory)')
    parser.add_argument('-c', '--complete_loci_file', dest='complete_loci_file_path', help='complete loci file path (mandatory)')
    parser.add_argument('-s', '--selected_loci_file', dest='selected_loci_file_path', help='selected loci file path (mandatory)')
    parser.add_argument('-n', '--nexus_file', dest='nexus_file_path', help='Nexus file path (mandatory)')
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

    # check selection_loci_id_file_path
    if args.selection_loci_id_file_path is None:
        xlib.Message.print('error', '*** A loci id file path is not indicated in the input arguments.')
        OK = False
    else:
        if not os.path.isfile(args.selection_loci_id_file_path):
            xlib.Message.print('error', f'*** The file {args.selection_loci_id_file_path} does not exist.')
            OK = False

    # check complete_loci_file_path
    if args.complete_loci_file_path is None:
        xlib.Message.print('error', '*** A complete loci file path is not indicated in the input arguments.')
        OK = False
    else:
        if not os.path.isfile(args.complete_loci_file_path):
            xlib.Message.print('error', f'*** The file {args.complete_loci_file_path} does not exist.')
            OK = False
        if not args.complete_loci_file_path.endswith('.loci'):
            xlib.Message.print('error', f'*** The file {args.complete_loci_file_path} does not end in ".loci".')
            OK = False

    # check selected_loci_file_path
    if args.selected_loci_file_path is None:
        xlib.Message.print('error', '*** A selected loci file path is not indicated in the input arguments.')
        OK = False
    else:
        if not args.selected_loci_file_path.endswith('.loci'):
            xlib.Message.print('error', f'*** The file {args.selected_loci_file_path} does not end in ".loci".')
            OK = False

    # check nexus_file_path
    if args.nexus_file_path is None:
        xlib.Message.print('error', '*** A Nexus file path is not indicated in the input arguments.')
        OK = False
    else:
        if not args.nexus_file_path.endswith('.nex'):
            xlib.Message.print('error', f'*** The file {args.nexus_file_path} does not end in ".nex".')
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

def build_nexus_file(selection_loci_id_file_path, complete_loci_file_path, selected_loci_file_path, nexus_file_path):
    '''
    Build a Nexus file from a ypirad loci file for a determinated loci set.
    '''

    # initialize the selected loci id list
    selected_loci_id_list = []
    
    # load the selected loci ids and set the selected loci id list
    try:
        with open(selection_loci_id_file_path) as selected_loci_ids_file_id:
            for record in selected_loci_ids_file_id:
                selected_loci_id_list.append(record[6:].rstrip())
    except Exception as e:
        raise xlib.ProgramException(e, 'F001', selection_loci_id_file_path)
    xlib.Message.print('trace', f'selected_loci_id_list: {selected_loci_id_list}\n')

    # open the complete loci file
    try:
        complete_loci_file_id = open(complete_loci_file_path, mode='r', encoding='iso-8859-1')
    except Exception as e:
        raise xlib.ProgramException(e, 'F001', complete_loci_file_path)

    # open the selected loci file
    try:
        selected_loci_file_id = open(selected_loci_file_path, mode='w', encoding='iso-8859-1')
    except Exception as e:
        raise xlib.ProgramException(e, 'F001', selected_loci_file_path)

    # set the pattern of the locus id records
    pattern1 = r'^\/\/(.*)\|(.*)\|$'

    # set the pattern of the locus information records
    pattern2 = r'^(.*) (.*)$'

    # initialize the list of locus information records
    locus_line_list = []

    # initialize the sequence locus lenght list
    seq_locus_lenght_list = []

    # initialize the taxon id list
    taxon_id_list = []

    # initialize the base count
    base_count = 0
 
    # read the first record of complete loci file
    record = complete_loci_file_id.readline()

    # while there are records
    while record != '':

        # process the locus id record 
        if record.startswith('//'):

            # extract the locus id 
            mo = re.search(pattern1, record)
            locus_id = mo.group(2)

            # when the locus id is a selected locus, write locus information in the selected loci file
            if locus_id in selected_loci_id_list:
                for i in range(len(locus_line_list)):

                    # extract the taxon id and sequence
                    mo = re.search(pattern2, locus_line_list[i])
                    taxon_id = mo.group(1).strip()
                    sequence = mo.group(2).strip()

                    # add the taxon id to taxon id list
                    if taxon_id not in taxon_id_list:
                        taxon_id_list.append(taxon_id)

                    # when the first taxon
                    if i == 0:

                        # add the sequence length to the base count
                        base_count += len(sequence)

                        # add the sequence length to the sequence locus lenght list to the first taxon found
                        seq_locus_lenght_list.append(len(sequence))

                    # write the line to the selected loci file
                    selected_loci_file_id.write(locus_line_list[i])

                # write the locus id record to the selected loci file
                selected_loci_file_id.write(record)

            # initialize the list of locus information records
            locus_line_list = []

        # process a locus information record
        else:

            # add the record to the list of locus information records
            locus_line_list.append(record)

        # read the next record of complete loci file      
        record = complete_loci_file_id.readline()

    # sort the taxon id list
    taxon_id_list.sort()
    xlib.Message.print('trace', f'taxon_id_list: {taxon_id_list}\n')

    # close files
    complete_loci_file_id.close()
    selected_loci_file_id.close()

    # initialize the dictionary of locus information records
    locus_line_dict = {}

    # open the selected loci file
    try:
        selected_loci_file_id = open(selected_loci_file_path, mode='r', encoding='iso-8859-1')
    except Exception as e:
        raise xlib.ProgramException(e, 'F001', selected_loci_file_path)

    # open the Nexus file
    try:
        nexus_file_id = open(nexus_file_path, mode='w', encoding='iso-8859-1')
    except Exception as e:
        raise xlib.ProgramException(e, 'F001', nexus_file_path)

    # write the head records in Nexus file
    nexus_file_id.write( '#nexus\n')
    nexus_file_id.write( 'begin data;\n')
    nexus_file_id.write(f'  dimensions ntax={len(taxon_id_list)} nchar={base_count};\n')
    nexus_file_id.write( '  format datatype=DNA interleave=yes gap=-;\n')
    nexus_file_id.write( '  matrix\n')

    # read the first record of the selected loci file
    record = selected_loci_file_id.readline()

    # while there are records
    while record != '':

        # process the locus id record 
        if record.startswith('//'):

            # get the sequence length of a taxon
            sequence_len = len(locus_line_dict[list(locus_line_dict.keys())[0]])

            # for each taxon, write its information
            for taxon_id in taxon_id_list:

                # get the taxon sequence
                sequence = locus_line_dict.get(taxon_id, 'N' * sequence_len)

                # write the locus information record in the Nexus file
                nexus_file_id.write(f'  {taxon_id:30} {sequence}\n')

            # write a blank line in the Nexus file
            nexus_file_id.write('\n')

            # initialize the dictionary of locus information records
            locus_line_dict = {}

        # process a locus information record
        else:

            # extract the taxon id and sequence
            mo = re.search(pattern2, record)
            taxon_id = mo.group(1).strip()
            sequence = mo.group(2).strip()

            # add the record to the dictionary of locus information records
            locus_line_dict[taxon_id] = sequence 

        # read the next record of selected loci file
        record = selected_loci_file_id.readline()

    # write the tail records in Nexus file
    nexus_file_id.write( '  ;\n')
    nexus_file_id.write( 'end;\n')
    nexus_file_id.write( 'begin assumptions;\n')
    start_position = 1
    for i in range(len(seq_locus_lenght_list)):
        end_position = start_position + seq_locus_lenght_list[i]
        nexus_file_id.write(f'  charset locus_{i + 1} = {start_position}-{end_position - 1};\n')
        start_position = end_position
    nexus_file_id.write( 'end;\n')

    # close files
    selected_loci_file_id.close()
    nexus_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
