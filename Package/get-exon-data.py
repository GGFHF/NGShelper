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
This program parses a GAMP alignment in order to get data about the coverage, identity and coordinates of exons.
'''

#-------------------------------------------------------------------------------

import argparse
import gzip
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

    # extract sequences
    get_exon_data(args.alignment_file, args.output_dir)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program parses a GAMP alignment in order to get data about the coverage, identity and coordinates of exons.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--alignment', dest='alignment_file', help='Path of GMAP alignment file (mandatory)')
    parser.add_argument('--outdir', dest='output_dir', help='Path of output directoty where files with exons data are saved (mandatory).')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def check_args(args):
    '''
    Verity the input arguments.
    '''

    # initialize the control variable
    OK = True

    # check "alignment_file"
    if args.alignment_file is None:
        xlib.Message.print('error', '*** The input alignment file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.alignment_file):
        xlib.Message.print('error', f'*** The file {args.alignment_file} does not exist.')
        OK = False

    # check "output_dir"
    if args.output_dir is None:
        xlib.Message.print('error', '*** The output directy is not indicated in the input arguments.')
        OK = False
    elif not os.path.isdir(args.output_dir):
        xlib.Message.print('error', '*** The output directy does not exist.')
        OK = False

    # check "verbose"
    if args.verbose is None:
        args.verbose = xlib.Const.DEFAULT_VERBOSE
    elif args.verbose.upper() not in get_verbose_code_list():
        xlib.Message.print('error', f'The verbose has to be {get_verbose_code_list_text()}.')
        OK = False
    if args.verbose.upper() == 'Y':
        xlib.Message.set_verbose_status(True)

    # check "trace"
    if args.trace is None:
        args.trace = xlib.Const.DEFAULT_TRACE
    elif args.trace.upper() not in get_trace_code_list():
        xlib.Message.print('error', f'The trace has to be {get_trace_code_list_text()}.')
        OK = False
    if args.trace.upper() == 'Y':
        xlib.Message.set_trace_status(True)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def get_exon_data(alignment_file, output_dir):
    '''
    '''

    # open the alignment file
    if alignment_file.endswith('.gz'):
        try:
            alignment_file_id = gzip.open(alignment_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', alignment_file)
    else:
        try:
            alignment_file_id = open(alignment_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', alignment_file)

    # set the exon data file
    exon_data_file = f'{output_dir}/exon-data.csv'

    # open the exon data file
    if exon_data_file.endswith('.gz'):
        try:
            exon_data_file_id = gzip.open(exon_data_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', exon_data_file)
    else:
        try:
            exon_data_file_id = open(exon_data_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', exon_data_file)

    # write head record of the exon data file
    exon_data_file_id.write('"assembly_id";"genomic_seq_id";"assembly_coverage";"exon";"exon_strand";"exon_coordinates";"exon_percent_identity"\n')

    # set the file of assembly identification with 0 paths
    assembly_ids_0paths_file = f'{output_dir}/assembly-ids-0paths.txt'

    # open the file of assembly identification with 0 paths
    try:
        assembly_ids_0paths_file_id = open(assembly_ids_0paths_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', assembly_ids_0paths_file)

    # set the file of assembly identification with 1 path
    assembly_ids_1path_file = f'{output_dir}/assembly-ids-1path.txt'

    # open the file of assembly identification with 1 path
    try:
        assembly_ids_1path_file_id = open(assembly_ids_1path_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', assembly_ids_1path_file)

    # set the file of assembly identification with n paths (n > 1)
    assembly_ids_npaths_file = f'{output_dir}/assembly-ids-npaths.txt'

    # open the file of assembly identification with n paths
    try:
        assembly_ids_npaths_file_id = open(assembly_ids_npaths_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', assembly_ids_npaths_file)

    # initialize record counters
    alignment_counter = 0
    exon_counter = 0
 
    # read the first record of alignment file
    record = alignment_file_id.readline()

    # while there are records in alignment file
    while record != '':

        # process the head record 
        if record.startswith('>'):

            # add 1 to the alignment counter
            alignment_counter += 1

            # initialize alignment data
            assembly_id = ''
            genomic_seq_id = ''
            path_num = 0
            assembly_coverage = 0
            exon_num = 0
            exon_strand_list =  []
            exon_coordinates_list =  []
            exon_percent_identity_list = []

            # extract the identification
            assembly_id = record[1:].strip('\n')

            # read the next record
            record = alignment_file_id.readline()

        else:

            # control the FASTA format
            raise xlib.ProgramException('F006', alignment_file, 'FASTA')

        # while there are records and they are sequence
        while record != '' and not record.startswith('>'):

            # get exon data
            if record.startswith('Paths'):

                # get the path number
                try:
                    path_num = int(record[record.find('(') + 1:record.find(')')])
                except Exception as e:
                    raise xlib.ProgramException(e, 'F010', 'path number', assembly_id)

                # if path number is equal to 0, there are not exon data
                if path_num > 0:

                    # read the next record
                    record = alignment_file_id.readline()

                    # get the genomic sequence identification
                    try:
                        text = 'genome'
                        start = record.find(text)+len(text)
                        end = record[start:].find(':')
                        genomic_seq_id = record[start:start + end].strip()
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'genomic squence identification', assembly_id)

                    # read until the number of exons
                    exon_num_text = 'Number of exons:'
                    while record != '' and not record.strip().startswith(exon_num_text):
                        record = alignment_file_id.readline()

                    # get the exon number
                    try:
                        start = record.find(exon_num_text)+len(exon_num_text)
                        exon_num = int(record[start:].strip())
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'exon number', assembly_id)

                    # read until the coverage
                    assembly_coverage_text = 'Coverage:'
                    while record != '' and not record.strip().startswith(assembly_coverage_text):
                        record = alignment_file_id.readline()

                    # get the assembly_coverage
                    try:
                        start = record.find(assembly_coverage_text)+len(assembly_coverage_text)
                        end = record[start:].find('(')
                        assembly_coverage = float(record[start:start + end].strip())
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'assembly coverage', assembly_id)

                    # read records until the alignment for path 1
                    while record != '' and not record.strip().startswith('Alignment for path 1:'):
                        record = alignment_file_id.readline()

                    # read records until the first exon data
                    record = alignment_file_id.readline()
                    while record != '' and record == '\n':
                        record = alignment_file_id.readline()

                    # get the exon data
                    for i in range(exon_num):

                        # get the strand
                        try:
                            exon_strand = record.strip()[0]
                            exon_strand_list.append(exon_strand)
                        except Exception as e:
                            print(f'i: {i}')
                            print(f'record: {record.strip()}')
                            raise xlib.ProgramException(e, 'F010', 'exon strand', assembly_id)

                        # get the coordinates
                        try:
                            exon_coordinates = record[record.find(':') + 1:record.find('(')].strip()
                            exon_coordinates_list.append(exon_coordinates)
                        except Exception as e:
                            raise xlib.ProgramException(e, 'F010', 'exon coordinates', assembly_id)

                        # get the percent identity
                        try:
                            exon_percent_identity = float(record[record.find(')') + 1:record.find('%')].strip())
                            exon_percent_identity_list.append(exon_percent_identity)
                        except Exception as e:
                            raise xlib.ProgramException(e, 'F010', 'exon percent identity', assembly_id)

                        # read the next record
                        record = alignment_file_id.readline()

            else:
                pass

            # read the next record of alignment file
            record = alignment_file_id.readline()

        # write the exon data (only when the path number is equal to 1) and assembly identification in their corresponding files
        if path_num == 0:
            assembly_ids_0paths_file_id.write(f'{assembly_id}\n')
        elif path_num == 1:
            # write the exon data
            for i in range(exon_num):
                exon_data_file_id.write(f'"{assembly_id}";"{genomic_seq_id}";{assembly_coverage};{i +1};"{exon_strand_list[i]}";"{exon_coordinates_list[i]}";{exon_percent_identity_list[i]}\n')
                exon_counter += 1
            # write the assembly identification
            assembly_ids_1path_file_id.write(f'{assembly_id}\n')
        else:
            assembly_ids_npaths_file_id.write(f'{assembly_id}\n')

        # print the counters
        xlib.Message.print('verbose', f'\rAlignments ... {alignment_counter:8d} - Exons ... {exon_counter:8d}')

    # close files
    alignment_file_id.close()
    exon_data_file_id.close()
    assembly_ids_0paths_file_id.close()
    assembly_ids_1path_file_id.close()
    assembly_ids_npaths_file_id.close()

    # print OK message 
    xlib.Message.print('verbose', f'\nThe file {os.path.basename(exon_data_file)} containing the extacted sequences is created.')

#-------------------------------------------------------------------------------
    
def get_verbose_code_list():
    '''
    Get the code list of "verbose".
    '''

    return ['Y', 'N']

#-------------------------------------------------------------------------------
    
def get_verbose_code_list_text():
    '''
    Get the code list of "verbose" as text.
    '''

    return 'Y (yes) or N (no)'

#-------------------------------------------------------------------------------
    
def get_trace_code_list():
    '''
    Get the code list of "trace".
    '''

    return ['Y', 'N']

#-------------------------------------------------------------------------------
    
def get_trace_code_list_text():
    '''
    Get the code list of "trace" as text.
    '''

    return 'Y (yes) or N (no)'

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
