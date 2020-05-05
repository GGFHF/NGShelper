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
This program extracts sequences from a FASTA file.
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
    extract_sequences(args.fasta_file, args.id_file, args.id_type, args.extract_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program extracts sequences from a FASTA file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--fasta', dest='fasta_file', help='Path of FASTA file (mandatory)')
    parser.add_argument('--id', dest='id_file', help='Path of the sequence identification file in plane text (mandatory)')
    parser.add_argument('--type', dest='id_type', help=f'Type of the identification: {get_id_type_code_list()}; default: {xlib.Const.DEFAULT_ID_TYPE}.')
    parser.add_argument('--extract', dest='extract_file', help='Path of extracted FASTA file (mandatory)')
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

    # check "fasta_file"
    if args.fasta_file is None:
        xlib.Message.print('error', '*** The input FASTA file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.fasta_file):
        xlib.Message.print('error', f'*** The file {args.fasta_file} does not exist.')
        OK = False

    # check "id_file"
    if args.id_file is None:
        xlib.Message.print('error', '*** The sequence identification file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.id_file):
        xlib.Message.print('error', f'*** The file {args.id_file} does not exist.')
        OK = False

    # check "id_type"
    if args.id_type is None:
        args.id_type = xlib.Const.DEFAULT_ID_TYPE
    elif args.id_type.upper() not in get_id_type_code_list():
        xlib.Message.print('error', f'The identification type has to be {get_id_type_code_list_text()}.')
        OK = False
    else:
        args.id_type = args.id_type.upper()

    # check "extract_file"
    if args.extract_file is None:
        xlib.Message.print('error', '*** The extracted FASTA file is not indicated in the input arguments.')
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

def extract_sequences(fasta_file, id_file, id_type, extract_file):
    '''
    '''

    # get the identification data
    (id_list, id_dict) = get_id_data(id_file)

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

    # open the extracted sequences file
    if extract_file.endswith('.gz'):
        try:
            extract_file_id = gzip.open(extract_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', extract_file)
    else:
        try:
            extract_file_id = open(extract_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', extract_file)

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
            raise xlib.ProgramException('F006', fasta_file, 'FASTA')

        # while there are records and they are sequence
        while record != '' and not record.startswith('>'):

            # concatenate the record to the sequence
            seq += record.strip()

            # read the next record of FASTA file
            record = fasta_file_id.readline()

        # add 1 to the read sequence counter
        read_seq_counter += 1

        # write the sequence if its identification is in the identification list
        if id_type == 'LITERAL':

            if id in id_list:

                # write the header record
                extract_file_id.write(f'>{id}\n')

                # write the sequence
                i = 0
                while i < len(seq) - xlib.Const.FASTA_RECORD_LEN:
                    extract_file_id.write(f'{seq[i:i + xlib.Const.FASTA_RECORD_LEN]}\n')
                    i += xlib.Const.FASTA_RECORD_LEN
                extract_file_id.write(f'{seq[i:]}\n')

                # add 1 to the written sequence counter
                written_seq_counter += 1

        elif id_type == 'REGEX':

            for id_item in id_list:

                if bool(re.search(f'^{id_item}$', id)):

                    # write the header record
                    extract_file_id.write(f'>{id}\n')

                    # write the sequence
                    i = 0
                    while i < len(seq) - xlib.Const.FASTA_RECORD_LEN:
                        extract_file_id.write(f'{seq[i:i + xlib.Const.FASTA_RECORD_LEN]}\n')
                        i += xlib.Const.FASTA_RECORD_LEN
                    extract_file_id.write(f'{seq[i:]}\n')

                    # add 1 to the written sequence counter
                    written_seq_counter += 1

                    # exit
                    break

        # print the counters
        xlib.Message.print('verbose', f'\rProcessed seqs ... {read_seq_counter:8d} - Extracted seqs ... {written_seq_counter:8d}')

    # close files
    fasta_file_id.close()
    extract_file_id.close()

    # print OK message 
    xlib.Message.print('verbose', f'\nThe file {os.path.basename(extract_file)} containing the extacted sequences is created.')

#-------------------------------------------------------------------------------

def get_id_data(id_file):
    '''
    '''

    # initialize the list and dictonary of identifications
    id_list = []
    id_dict = {}

    # initialize the identification counter
    id_counter = 0

    # open the identification file
    if id_file.endswith('.gz'):
        try:
            id_file_id = gzip.open(id_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', id_file)
    else:
        try:
            id_file_id = open(id_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', id_file)

    # read the first record
    record = id_file_id.readline()

    # while there are records
    while record != '':

        # add identification to the list and dictionary
        id_list.append(record.strip())
        id_dict[record.strip()] = 0

        # add 1 to the identification counter
        id_counter += 1
        xlib.Message.print('verbose', f'\rIdentifications ... {id_counter}')

        # read the next record
        record = id_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close file
    id_file_id.close()

    # sort the identification list
    if id_list != []:
        id_list.sort()

    # return the list and dictonary of identifications
    return id_list, id_dict

#-------------------------------------------------------------------------------
    
def get_id_type_code_list():
    '''
    Get the code list of "id_type".
    '''

    return ['LITERAL', 'REGEX']

#-------------------------------------------------------------------------------
    
def get_id_type_code_list_text():
    '''
    Get the code list of "id_type" as text.
    '''

    return str(get_id_type_code_list()).strip('[]').replace('\'','').replace(',', ' or')

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
