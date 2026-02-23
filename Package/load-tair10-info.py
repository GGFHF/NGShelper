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
This program loads TAIR 10 peptide infomation into a SQLite database.

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
import random
import re
import sys

import xlib
import xsqlite

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

    # connect to the SQLite database
    conn = xsqlite.connect_database(args.sqlite_database)

    # load TAIR 10 peptide infomation into a SQLite database
    load_tair10_info(conn, args.tair10_fasta_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads TAIR 10 peptide infomation into a SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--tair10', dest='tair10_fasta_file', help='Path of TAIR10 FASTA file (mandatory)')
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

    # check "sqlite_database"
    if args.sqlite_database is None:
        xlib.Message.print('error', '*** The database is not indicated in the input arguments.')
        OK = False

    # check "tair10_fasta_file"
    if args.tair10_fasta_file is None:
        xlib.Message.print('error', '*** The TAIR10 FASTA file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.tair10_fasta_file):
        xlib.Message.print('error', f'*** The file {args.tair10_fasta_file} does not exist.')
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

def load_tair10_info(conn, tair10_fasta_file):
    '''
    Load TAIR 10 peptide infomation into a SQLite database.
    '''

    # drop the table "tair10_info" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "tair10_info" ...\n')
    xsqlite.drop_tair10_info(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create the table "tair10_info"
    xlib.Message.print('verbose', 'Creating the table "tair10_info" ...\n')
    xsqlite.create_tair10_info(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # open the TAIR10 FASTA file
    if tair10_fasta_file.endswith('.gz'):
        try:
            tair10_fasta_file_id = gzip.open(tair10_fasta_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', tair10_fasta_file)
    else:
        try:
            tair10_fasta_file_id = open(tair10_fasta_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', tair10_fasta_file)

    # initialize the record counter
    record_counter = 0

    # initialize the inserted row counter
    inserted_row_counter = 0

    # read the first record of TAIR10 FASTA file
    record = tair10_fasta_file_id.readline()

    # while there are records in TAIR10 FASTA file
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # process the header record
        if record.startswith('>'):

            # add 1 to record counter
            record_counter += 1

            # initialize the row data dictionary
            row_dict = {}

            # extract info
            # header record format: > tair10_peptide_id <field_sep> symbols <field_sep> description <field_sep> genomic_data <record_sep>
            field_sep = r'\|'
            record_sep = '\n'
            data_list = re.split(field_sep, record[1:].replace(record_sep,'').replace('"','').replace("'",''))
            try:
                row_dict['tair10_peptide_id'] = data_list[0].strip()
                row_dict['description'] = data_list[2].strip()
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(tair10_fasta_file), record_counter)

            # insert data into the table "tair10_info"
            xsqlite.insert_tair10_info_row(conn, row_dict)
            inserted_row_counter += 1

            # read the next record
            record = tair10_fasta_file_id.readline()

        else:

            # control the FASTA format
            raise xlib.ProgramException('F006', tair10_fasta_file, 'FASTA')

        # while there are records and they are sequence
        while record != '' and not record.startswith('>'):

            # add 1 to record counter
            record_counter += 1

            # read the next record
            record = tair10_fasta_file_id.readline()

        # print counters
        xlib.Message.print('verbose', f'\rTAIR10 FASTA file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

    xlib.Message.print('verbose', '\n')

    # create the index "tair10_info_index" on the table "tair10_info"
    xlib.Message.print('verbose', 'Creating the index on the table "tair10_info" ...\n')
    xsqlite.create_tair10_info_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

    # close TAIR10 FASTA file
    tair10_fasta_file_id.close()

#-------------------------------------------------------------------------------

def mutate_sequence(seq, indel_probability, max_mutation_size):
    '''
    Mutate the sequence varying several nucleotides or doing a indel.
    '''

    # initialize the new sequence
    new_seq = ''

    # get the mutation size
    mutation_size = random.randrange(1, max_mutation_size + 1)

    # there is an indel
    if indel_probability > random.random():

        # if there is a insertion
        if random.random() < 0.5:

            # get indel initial position
            j = random.randrange(0, len(seq))

            # get the insertion sequence
            insertion_seq = generate_random_sequence(mutation_size).lower()

            # build the new sequence
            new_seq = seq[:j] + insertion_seq + seq[j:]

        # there is a deletion
        else:

            # get indel initial position
            j = random.randrange(0, max(len(seq) - mutation_size, 1))

            # build the new sequence
            new_seq = seq[:j] + seq[(j + mutation_size):]

    # there is a mutation of several nucleotides
    else:

        # get mutation position
        j = random.randrange(0, max(len(seq) - mutation_size, 1))

        # get the mutated nucleotide
        while True:
            mutated_nucleotides = generate_random_sequence(mutation_size).lower()
            # verify that mutated nucleotide is not equal to nucleotide without mutation
            if mutated_nucleotides.upper() != seq[j:j+mutation_size].upper():
                break

        # build the new sequence
        new_seq = seq[:j] + mutated_nucleotides + seq[(j + mutation_size):]

    # return the mutated sequence
    return new_seq

#-------------------------------------------------------------------------------

def generate_random_sequence(length):
    '''
    Generate randomly a nucleotides sequence with the length passed.
    '''

    # the four nucleotides
    nucleotide_list = ['A', 'T', 'C', 'G']

    # initialize the sequence
    seq = ''

    # get randomly a new nucleotide and add it to the sequence
    for _ in range(length):
        radnum = random.randrange(0, 4)
        seq += nucleotide_list[radnum]

    # return the sequence
    return seq

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

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
