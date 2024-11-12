#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program calculates statistics of a transcriptome.

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

    # calculate statistics of a transcriptome
    calculate_statistics(args.transcriptome_file, args.output_directory)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program calculates statistics of a transcriptome.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--transcriptome', dest='transcriptome_file', help='Path of a transcriptome file in FASTA format (mandatory)')
    parser.add_argument('--output', dest='output_directory', help='Path of a directory where the results will be saved (mandatory)')
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

    # check transcriptome_file
    if args.transcriptome_file is None:
        xlib.Message.print('error', '*** A transcritpme file in Fasta format is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.transcriptome_file):
        xlib.Message.print('error', f'*** The file {args.transcriptome_file} does not exist.')
        OK = False

    # check output_directory
    if args.output_directory is None:
        xlib.Message.print('error', '*** A directory where the results will be saved base is not indicated in the input arguments.')
        OK = False
    else:
        try:
            if not os.path.exists(args.output_directory):
                os.makedirs(args.output_directory)
        except Exception as e:
            xlib.Message.print('error', f'*** The directory {args.output_directory} is not valid.')
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

def calculate_statistics(transcriptome_file, output_directory):
    '''
    Calculate statistics of a transcriptome.
    '''

    # initialize the transcript length dictionary
    transcript_len_dict = {}

    # open the transcriptome file
    if transcriptome_file.endswith('.gz'):
        try:
            transcriptome_file_id = gzip.open(transcriptome_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', transcriptome_file)
    else:
        try:
            transcriptome_file_id = open(transcriptome_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', transcriptome_file)

    # initialize the transcript count
    transcript_count = 0

    # set the pattern of the head records (>transcriptome_info)
    pattern = r'^>(.*)$'

    # read the first record
    record = transcriptome_file_id.readline()

    # while there are records
    while record != '':

        # process the head record
        if record.startswith('>'):

            # extract the data
            mo = re.search(pattern, record)
            transcript_info = mo.group(1)

            # initialize the transcript sequence
            transcript_seq = ''

            # read the next record
            record = transcriptome_file_id.readline()

        else:

            # control the FASTA format
            raise xlib.ProgramException('', 'F006', transcriptome_file, 'FASTA')

        # while there are records and they are sequence
        while record != '' and not record.startswith('>'):

            # concatenate the record to the transcript sequence
            transcript_seq += record.strip()

            # read the next record
            record = transcriptome_file_id.readline()

        # calculae transcript len and update the dictionary
        transcript_len = len(transcript_seq)
        transcript_len_count = transcript_len_dict.get(transcript_len, 0)
        transcript_len_dict[transcript_len] = transcript_len_count + 1

        # add 1 to trascript count and print it
        transcript_count += 1
        xlib.Message.print('verbose', f'\rProcessed transcripts ... {transcript_count:9d}')

    xlib.Message.print('verbose', '\n')

    # close file
    transcriptome_file_id.close()

    # initialize statistics variables
    len_to_stats_list = [500,1000,5000,10000,25000,50000]
    len_to_stats_list.sort()
    stats_transcript_dict = {}
    transcript_count_0 = 0
    transcript_len_0 = 0
    shortest_transcript = sys.maxsize
    largest_transcript = 0

    # calculate statistics
    xlib.Message.print('info', 'Calculating statistics ...')
    for transcript_len in transcript_len_dict.keys():

        # get the transcript count for this length
        transcript_count = transcript_len_dict[transcript_len]

        # calculate the count and length of all transcripts
        transcript_count_0 += transcript_count
        transcript_len_0 += transcript_len * transcript_count

        # calculate the count and length of transcripts whose length is greater than or equal to an item of the list of statisctics transcript length
        for len_to_stats in len_to_stats_list:
            if transcript_len >= len_to_stats:
                stats_transcript_count = stats_transcript_dict.get(len_to_stats, {}).get('count', 0)
                stats_transcript_len = stats_transcript_dict.get(len_to_stats, {}).get('length', 0)
                stats_transcript_dict[len_to_stats] = {'count': stats_transcript_count + transcript_count, 'length': stats_transcript_len + transcript_len * transcript_count}

        # calculate the shortest and largest transcript
        if shortest_transcript > transcript_len:
            shortest_transcript = transcript_len
        if largest_transcript < transcript_len:
            largest_transcript = transcript_len

    # print statistics
    title = f'{os.path.basename(transcriptome_file)} - Transcriptome Statistics'
    xlib.Message.print('info', title)
    xlib.Message.print('info', '=' * len(title))
    xlib.Message.print('info', f'# transcripts (>= 0 bp): {transcript_count_0}')
    for len_to_stats in len_to_stats_list:
        xlib.Message.print('info', f'# transcripts (>= {len_to_stats} bp): {stats_transcript_dict.get(len_to_stats, {}).get("count", 0)}')
    xlib.Message.print('info', f'total length (>= 0 bp): {transcript_len_0}')
    for len_to_stats in len_to_stats_list:
        xlib.Message.print('info', f'total length (>= {len_to_stats} bp): {stats_transcript_dict.get(len_to_stats, {}).get("length", 0)}')
    xlib.Message.print('info', f'shortest transcript: {shortest_transcript}')
    xlib.Message.print('info', f'largest transcript: {largest_transcript}')

    # write statistics in a file with CSV format
    stats_file_path = output_directory + '/transcriptome-stats.csv'
    try:
        with open(stats_file_path, mode='w', encoding='iso-8859-1') as stats_file_id:
            stats_file_id.write(f'"# transcripts (>= 0 bp)",{transcript_count_0}\n')
            for len_to_stats in len_to_stats_list:
                stats_file_id.write(f'"# transcripts (>= {len_to_stats} bp)",{stats_transcript_dict.get(len_to_stats, {}).get("count", 0)}\n')
            stats_file_id.write(f'"total length (>= 0 bp)",{transcript_len_0}\n')
            for len_to_stats in len_to_stats_list:
                stats_file_id.write(f'"total length (>= {len_to_stats} bp)",{stats_transcript_dict.get(len_to_stats, {}).get("length", 0)}\n')
            stats_file_id.write(f'"shortest transcript",{shortest_transcript}\n')
            stats_file_id.write(f'"largest transcript",{largest_transcript}\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', stats_file_path)

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
