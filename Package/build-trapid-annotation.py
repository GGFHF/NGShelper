#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program builds functional annotation data corresponding to a TRAPID run.

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

    # build functional annotation data corresponding to a TRAPID run
    build_trapid_annotation(args.transcripts_with_go_file, args.transcripts_with_gf_file, args.transcripts_with_ko_file, args.annotation_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program builds functional annotation data corresponding to a TRAPID run.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--go', dest='transcripts_with_go_file', help='Path of transcripts with GO file (mandatory).')
    parser.add_argument('--gf', dest='transcripts_with_gf_file', help='Path of transcripts with GF file (mandatory).')
    parser.add_argument('--ko', dest='transcripts_with_ko_file', help='Path of transcripts with KO file (mandatory).')
    parser.add_argument('--annotation', dest='annotation_file', help='Path of annotation file in CSV format (mandatory).')
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

    # check "transcripts_with_go_file"
    if args.transcripts_with_go_file is None:
        xlib.Message.print('error', '*** The transcripts with GO file is not indicated in the options.')
        OK = False
    elif not os.path.isfile(args.transcripts_with_go_file):
        xlib.Message.print('error', f'*** The file {args.transcripts_with_go_file} does not exist.')
        OK = False

    # check "transcripts_with_gf_file"
    if args.transcripts_with_gf_file is None:
        xlib.Message.print('error', '*** The transcripts with GF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.transcripts_with_gf_file):
        xlib.Message.print('error', f'*** The file {args.transcripts_with_gf_file} does not exist.')
        OK = False

    # check "transcripts_with_ko_file"
    if args.transcripts_with_ko_file is None:
        xlib.Message.print('error', '*** The transcripts with KO file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.transcripts_with_ko_file):
        xlib.Message.print('error', f'*** The file {args.transcripts_with_ko_file} does not exist.')
        OK = False

    # check "annotation_file"
    if args.annotation_file is None:
        xlib.Message.print('error', '*** The annotation file is not indicated in the input arguments.')
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

def build_trapid_annotation(transcripts_with_go_file, transcripts_with_gf_file, transcripts_with_ko_file, annotation_file):
    '''
    Build functional annotation data corresponding to a TRAPID run.
    '''

    # initialize the annotation dictionary
    annotation_dict = xlib.NestedDefaultDict()

    # get GO annotations
    annotation_dict = get_go_annotations(transcripts_with_go_file, annotation_dict)

    # get GF annotations
    annotation_dict = get_gf_annotations(transcripts_with_gf_file, annotation_dict)

    # get KO annotations
    annotation_dict = get_ko_annotations(transcripts_with_ko_file, annotation_dict)

    # open the output annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', annotation_file)
    else:
        try:
            annotation_file_id = open(annotation_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', annotation_file)

    # write header record
    annotation_file_id.write('"transcript_id";"go_id";"go_desc";"gf_id";"ko_id";"ko_desc"\n')

    ## write transcript records
    for transcript_id in sorted(annotation_dict.keys()):
        go_id = annotation_dict.get(transcript_id, {}).get('go_id', '')
        go_desc = annotation_dict.get(transcript_id, {}).get('go_desc', '')
        gf_id = annotation_dict.get(transcript_id, {}).get('gf_id', '')
        ko_id = annotation_dict.get(transcript_id, {}).get('ko_id', '')
        ko_desc = annotation_dict.get(transcript_id, {}).get('ko_desc', '')
        annotation_file_id.write(f'"{transcript_id}";"{go_id}";"{go_desc}";"{gf_id}";"{ko_id}";"{ko_desc}"\n')

    # close annotation file
    annotation_file_id.close()

#-------------------------------------------------------------------------------

def get_go_annotations(transcripts_with_go_file, annotation_dict):
    '''
    x
    '''

    # initialize the record counter
    record_counter = 0

    # open the transcripts with GO file
    if transcripts_with_go_file.endswith('.gz'):
        try:
            transcripts_with_go_file_id = gzip.open(transcripts_with_go_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', transcripts_with_go_file)
    else:
        try:
            transcripts_with_go_file_id = open(transcripts_with_go_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', transcripts_with_go_file)

    # read the first record
    record = transcripts_with_go_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # process data records
        if not record.startswith('#'):

            # extract data
            # record format: counter	transcript_id	go	evidence_code	is_hidden	description
            data_list = []
            begin = 0
            for end in [i for i, chr in enumerate(record) if chr == '\t']:
                data_list.append(record[begin:end].strip())
                begin = end + 1
            data_list.append(record[begin:].strip('\n').strip())
            try:
                transcript_id = data_list[1]
                go = data_list[2]
                description = data_list[5]
            except Exception as e:
                raise xlib.ProgramException(e, 'F006', os.path.basename(transcripts_with_go_file), record_counter)

            # change quotation marks in "description"
            description = description.replace("'", '|')

            # insert data into annotation dictionary
            go_id_w = annotation_dict.get(transcript_id, {}).get('go_id', '')
            go_id_w = go if go_id_w == '' else f'{go_id_w}*{go}'
            go_desc_w = annotation_dict.get(transcript_id, {}).get('go_desc', '')
            go_desc_w = description if go_desc_w == '' else f'{go_desc_w}*{description}'
            gf_id_w = annotation_dict.get(transcript_id, {}).get('gf_id', '')
            ko_id_w = annotation_dict.get(transcript_id, {}).get('ko_id', '')
            ko_desc_w = annotation_dict.get(transcript_id, {}).get('ko_desc', '')
            annotation_dict[transcript_id] = {'go_id': go_id_w, 'go_desc': go_desc_w, 'gf_id': gf_id_w, 'ko_id': ko_id_w, 'ko_desc': ko_desc_w}

            # print counters
            xlib.Message.print('verbose', f'\rProcessed records of transcripts with GO file: {record_counter}')

        # read the next record
        record = transcripts_with_go_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close transcripts with GO file
    transcripts_with_go_file_id.close()

    # return the annotation dictionary
    return annotation_dict

#-------------------------------------------------------------------------------

def get_gf_annotations(transcripts_with_gf_file, annotation_dict):
    '''
    x
    '''

    # initialize the record counter
    record_counter = 0

    # open the transcripts with GF file
    if transcripts_with_gf_file.endswith('.gz'):
        try:
            transcripts_with_gf_file_id = gzip.open(transcripts_with_gf_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', transcripts_with_gf_file)
    else:
        try:
            transcripts_with_gf_file_id = open(transcripts_with_gf_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', transcripts_with_gf_file)

    # read the first record
    record = transcripts_with_gf_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # process data records
        if not record.startswith('#'):

            # extract data
            # record format: counter	transcript_id	gf_id
            data_list = []
            begin = 0
            for end in [i for i, chr in enumerate(record) if chr == '\t']:
                data_list.append(record[begin:end].strip())
                begin = end + 1
            data_list.append(record[begin:].strip('\n').strip())
            try:
                transcript_id = data_list[1]
                gf_id = data_list[2]
            except Exception as e:
                raise xlib.ProgramException(e, 'F006', os.path.basename(transcripts_with_gf_file), record_counter)

            # insert data into annotation dictionary
            if gf_id != '':
                go_id_w = annotation_dict.get(transcript_id, {}).get('go_id', '')
                go_desc_w = annotation_dict.get(transcript_id, {}).get('go_desc', '')
                gf_id_w = annotation_dict.get(transcript_id, {}).get('gf_id', '')
                gf_id_w = gf_id if gf_id_w == '' else f'{gf_id_w}*{gf_id}'
                ko_id_w = annotation_dict.get(transcript_id, {}).get('ko_id', '')
                ko_desc_w = annotation_dict.get(transcript_id, {}).get('ko_desc', '')
                annotation_dict[transcript_id] = {'go_id': go_id_w, 'go_desc': go_desc_w, 'gf_id': gf_id_w, 'ko_id': ko_id_w, 'ko_desc': ko_desc_w}

            # print counters
            xlib.Message.print('verbose', f'\rProcessed records of transcripts with GF file: {record_counter}')

        # read the next record
        record = transcripts_with_gf_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close transcripts with GF file
    transcripts_with_gf_file_id.close()

    # return the annotation dictionary
    return annotation_dict

#-------------------------------------------------------------------------------

def get_ko_annotations(transcripts_with_ko_file, annotation_dict):
    '''
    x
    '''

    # initialize the record counter
    record_counter = 0

    # open the transcripts with KO file
    if transcripts_with_ko_file.endswith('.gz'):
        try:
            transcripts_with_ko_file_id = gzip.open(transcripts_with_ko_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', transcripts_with_ko_file)
    else:
        try:
            transcripts_with_ko_file_id = open(transcripts_with_ko_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', transcripts_with_ko_file)

    # read the first record
    record = transcripts_with_ko_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # process data records
        if not record.startswith('#'):

            # extract data
            # record format: counter	transcript_id	ko	description
            data_list = []
            begin = 0
            for end in [i for i, chr in enumerate(record) if chr == '\t']:
                data_list.append(record[begin:end].strip())
                begin = end + 1
            data_list.append(record[begin:].strip('\n').strip())
            try:
                transcript_id = data_list[1]
                ko = data_list[2]
                description = data_list[3]
            except Exception as e:
                raise xlib.ProgramException(e, 'F006', os.path.basename(transcripts_with_ko_file), record_counter)

            # change quotation marks in "description"
            description = description.replace("'", '|')

            # insert data into annotation dictionary
            go_id_w = annotation_dict.get(transcript_id, {}).get('go_id', '')
            go_desc_w = annotation_dict.get(transcript_id, {}).get('go_desc', '')
            gf_id_w = annotation_dict.get(transcript_id, {}).get('gf_id', '')
            ko_id_w = annotation_dict.get(transcript_id, {}).get('ko_id', '')
            ko_id_w = ko if ko_id_w == '' else f'{ko_id_w}*{ko}'
            ko_desc_w = annotation_dict.get(transcript_id, {}).get('ko_desc', '')
            ko_desc_w = description if ko_desc_w == '' else f'{ko_desc_w}*{description}'
            annotation_dict[transcript_id] = {'go_id': go_id_w, 'go_desc': go_desc_w, 'gf_id': gf_id_w, 'ko_id': ko_id_w, 'ko_desc': ko_desc_w}

            # print counters
            xlib.Message.print('verbose', f'\rProcessed records of transcripts with KO file: {record_counter}')

        # read the next record
        record = transcripts_with_ko_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close transcripts with KO file
    transcripts_with_ko_file_id.close()

    # return the annotation dictionary
    return annotation_dict

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
