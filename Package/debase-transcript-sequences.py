#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program debases sequences from a transcript FASTA file.

This software has been developed by:

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

    # debase sequences from a transcript FASTA file
    debase_sequences(args.fasta_file, args.output_file, args.fragmentation_probability, args.max_fragment_number, args.max_end_shortening, args.min_fragment_length, args.mutation_probability, args.max_mutation_number, args.indel_probability, args.max_mutation_size)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program debases sequences from a transcript FASTA file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--fasta', dest='fasta_file', help='Path of transcript FASTA file (mandatory)')
    parser.add_argument('--output', dest='output_file', help='Path of FASTA file with debased sequences (mandatory)')
    parser.add_argument('--fragprob', dest='fragmentation_probability', help=f'Fragmentation probability ({xlib.Const.FRAGPROB_LOWEST} <= fragprob <= {xlib.Const.FRAGPROB_UPPEST}) (mandatory)')
    parser.add_argument('--maxfragnum', dest='max_fragment_number', help=f'Maximum fragment number ({xlib.Const.MAXFRAGNUM_LOWEST} <= maxfragnum <= {xlib.Const.MAXFRAGNUM_UPPEST}) (mandatory)')
    parser.add_argument('--maxshortening', dest='max_end_shortening', help=f'Maximum shortening of a fragment end ({xlib.Const.MAXSHORTENING_LOWEST} <= maxshortening <= {xlib.Const.MAXSHORTENING_UPPEST}) (mandatory)')
    parser.add_argument('--minfraglen', dest='min_fragment_length', help='Minimum fragment length; shorter fragments are not considered (mandatory)')
    parser.add_argument('--mutprob', dest='mutation_probability', help=f'Mutation probability ({xlib.Const.MUTPROB_LOWEST} <= mutprob <= {xlib.Const.MUTPROB_UPPEST}) (mandatory)')
    parser.add_argument('--maxmutnum', dest='max_mutation_number', help=f'Maximum mutation number ({xlib.Const.MAXMUTNUM_LOWEST} <= maxmutnum <= {xlib.Const.MAXMUTNUM_UPPEST}) (mandatory)')
    parser.add_argument('--indelprob', dest='indel_probability', help=f'Insertion/deletion probability ({xlib.Const.INDELPROB_LOWEST} <= indelprob <= {xlib.Const.INDELPROB_UPPEST}) (mandatory)')
    parser.add_argument('--maxmutsize', dest='max_mutation_size', help=f'Maximum mutation size ({xlib.Const.MAXMUTSIZE_LOWEST} <= maxmutsize <= {xlib.Const.MAXMUTSIZE_UPPEST}) (mandatory)')
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

    # check "output_file"
    if args.output_file is None:
        xlib.Message.print('error', '*** The FASTA file with debased sequences is not indicated in the input arguments.')
        OK = False

    # check "fragmentation_probability"
    if args.fragmentation_probability is None:
        xlib.Message.print('error', '*** The fragmentation probability is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.fragmentation_probability, minimum=xlib.Const.FRAGPROB_LOWEST, maximum=xlib.Const.FRAGPROB_UPPEST):
        xlib.Message.print('error', f'The fragmentation probability has to be a float number between {xlib.Const.FRAGPROB_LOWEST} and {xlib.Const.FRAGPROB_UPPEST}.')
        OK = False
    else:
        args.fragmentation_probability = float(args.fragmentation_probability)

    # check "max_fragment_number"
    if args.max_fragment_number is None:
        xlib.Message.print('error', '*** The maximum fragment number is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.max_fragment_number, minimum=xlib.Const.MAXFRAGNUM_LOWEST, maximum=xlib.Const.MAXFRAGNUM_UPPEST):
        xlib.Message.print('error', f'The maximum fragment number has to be a integer number between {xlib.Const.MAXFRAGNUM_LOWEST} and {xlib.Const.MAXFRAGNUM_UPPEST}.')
        OK = False
    else:
        args.max_fragment_number = int(args.max_fragment_number)

    # check "max_end_shortening"
    if args.max_end_shortening is None:
        xlib.Message.print('error', '*** The maximum shortening of a fragment end is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.max_end_shortening, minimum=xlib.Const.MAXSHORTENING_LOWEST, maximum=xlib.Const.MAXSHORTENING_UPPEST):
        xlib.Message.print('error', f'The maximum shortening of a fragment end has to be a integer number between {xlib.Const.MAXSHORTENING_LOWEST} and {xlib.Const.MAXSHORTENING_UPPEST}.')
        OK = False
    else:
        args.max_end_shortening = int(args.max_end_shortening)

    # check "min_fragment_length"
    if args.min_fragment_length is None:
        xlib.Message.print('error', '*** The minimum fragment length is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.min_fragment_length, minimum=1):
        xlib.Message.print('error', 'The minimum fragment length has to be a integer number greater than 0.')
        OK = False
    else:
        args.min_fragment_length = int(args.min_fragment_length)

    # check "mutation_probability"
    if args.mutation_probability is None:
        xlib.Message.print('error', '*** The mutation probability is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.mutation_probability, minimum=xlib.Const.MUTPROB_LOWEST, maximum=xlib.Const.MUTPROB_UPPEST):
        xlib.Message.print('error', f'The mutation probability has to be a float number between {xlib.Const.MUTPROB_LOWEST} and {xlib.Const.MUTPROB_UPPEST}')
        OK = False
    else:
        args.mutation_probability = float(args.mutation_probability)

    # check "max_mutation_number"
    if args.max_mutation_number is None:
        xlib.Message.print('error', '*** The maximum mutation number is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.max_mutation_number, minimum=xlib.Const.MAXMUTNUM_LOWEST, maximum=xlib.Const.MAXMUTNUM_UPPEST):
        xlib.Message.print('error', f'The maximum mutation number has to be a integer number between {xlib.Const.MAXMUTNUM_LOWEST} and {xlib.Const.MAXMUTNUM_UPPEST}.')
        OK = False
    else:
        args.max_mutation_number = int(args.max_mutation_number)

    # check "indel_probability"
    if args.indel_probability is None:
        xlib.Message.print('error', '*** The insertion/deletion probability is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_float(args.indel_probability, minimum=xlib.Const.INDELPROB_LOWEST, maximum=xlib.Const.INDELPROB_UPPEST):
        xlib.Message.print('error', f'The insertion/deletion probability has to be a float number between {xlib.Const.INDELPROB_LOWEST} and {xlib.Const.INDELPROB_UPPEST}.')
        OK = False
    else:
        args.indel_probability = float(args.indel_probability)

    # check "max_mutation_size"
    if args.max_mutation_size is None:
        xlib.Message.print('error', '*** The maximum mutation size size is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.max_mutation_size, minimum=xlib.Const.MAXMUTSIZE_LOWEST, maximum=xlib.Const.MAXMUTSIZE_UPPEST):
        xlib.Message.print('error', f'The maximum mutation size size has to be a integer number between {xlib.Const.MAXMUTSIZE_LOWEST} and {xlib.Const.MAXMUTSIZE_UPPEST}.')
        OK = False
    else:
        args.max_mutation_size = int(args.max_mutation_size)

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

def debase_sequences(fasta_file, output_file, fragmentation_probability, max_fragment_number, max_end_shortening, min_fragment_length, mutation_probability, max_mutation_number, indel_probability, max_mutation_size):
    '''
    Debase sequences from a transcript FASTA file.
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

    # open the debased sequences file
    if output_file.endswith('.gz'):
        try:
            output_file_id = gzip.open(output_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_file)
    else:
        try:
            output_file_id = open(output_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_file)

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

        # initialize the sequence list
        seq_list = []

        xlib.Message.print('trace', f'\nid: {id}')

        # determine the fragmentation of the sequence
        if fragmentation_probability > random.random():

            # get the fragment number
            fragment_number = random.randrange(2, max_fragment_number + 1)

            # get the cut points
            cut_point_list = []
            for i in range(fragment_number):
                cut_point_list.append(random.randrange(2, len(seq)))

            # sort the cut points
            cut_point_list.sort()

            xlib.Message.print('trace', f'fragment_number: {fragment_number} - cut_point_list: {cut_point_list}')

            # get the fragment sequences
            init = 0
            for i in range(fragment_number):
                initial_fragment_seq = seq[init:cut_point_list[i]]
                left_end_shortening = random.randrange(0, max_end_shortening + 1)
                right_end_shortening = random.randrange(0, max_end_shortening + 1)
                if right_end_shortening == 0:
                    fragment_seq = initial_fragment_seq[left_end_shortening:]
                else:
                    fragment_seq = initial_fragment_seq[left_end_shortening:-right_end_shortening]
                if len(fragment_seq) > 0:
                    seq_list.append(fragment_seq)
                init = cut_point_list[i]

                xlib.Message.print('trace', f'initial_fragment_seq: {initial_fragment_seq}')
                xlib.Message.print('trace', f'left_end_shortening: {left_end_shortening} - right_end_shortening: {right_end_shortening}')
                xlib.Message.print('trace', f'fragment_seq: {fragment_seq}')

        # there is not fragmentation
        else:
            seq_list.append(seq)

        xlib.Message.print('trace', f'len(seq_list): {len(seq_list)}')

        # determine mutations of the sequence
        if mutation_probability > random.random():

            # get the mutation number
            mutation_number = random.randrange(1, max_mutation_number + 1)

            xlib.Message.print('trace', f'mutation_number: {mutation_number}')

            # calculate mutations
            for i in range(mutation_number):

                # determine the fragment where the mutation is locate
                j = random.randrange(0, len(seq_list))

                # mutate the fragment
                seq_list[j] = mutate_sequence(seq_list[j], indel_probability, max_mutation_size)

                xlib.Message.print('trace', f'fragment mutate: {j}')
                xlib.Message.print('trace', f'mutated fragment_seq: {seq_list[j]}')

        # write sequences whose lenght is greater than or equeal to the minimum fragment length
        for i in range(len(seq_list)):
            if len(seq_list[i]) >= min_fragment_length:

                # write the header record
                if len(seq_list) == 1:
                    output_file_id.write(f'>{id}\n')
                else:
                    output_file_id.write(f'>{id}-FRAGMENT{i + 1}\n')

                # write the sequence
                j = 0
                while j < len(seq_list[i]) - xlib.Const.FASTA_RECORD_LEN:
                    output_file_id.write(f'{seq_list[i][j:j + xlib.Const.FASTA_RECORD_LEN]}\n')
                    j += xlib.Const.FASTA_RECORD_LEN
                output_file_id.write(f'{seq_list[i][j:]}\n')

                # add 1 to the written sequence counter
                written_seq_counter += 1

        # print the counters
        xlib.Message.print('verbose', f'\rTranscripts seqs ... {read_seq_counter:8d} - Output seqs ... {written_seq_counter:8d}')

    # close files
    fasta_file_id.close()
    output_file_id.close()

    # print OK message
    xlib.Message.print('verbose', f'\nThe file {os.path.basename(output_file)} containing debased sequences is created.')

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
