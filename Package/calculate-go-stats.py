#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program calculates GO term statistics generated by annotation applications.

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

    # build the dictionary of GO ontology data
    go_ontology_dict = xlib.build_go_ontology_dict(args.ontology_file)

    # calculate annotation statistics
    if args.app == 'BLAST2GO':
        calculate_blast2go_go_stats(args.annotation_file, go_ontology_dict, args.output_dir)
    elif args.app == 'ENTAP':
        calculate_entap_go_stats(args.annotation_file, go_ontology_dict, args.output_dir)
    elif args.app == 'TOA':
        calculate_toa_go_stats(args.annotation_file, go_ontology_dict, args.output_dir, args.toa_go_selection)
    elif args.app == 'TRAPID':
        calculate_trapid_go_stats(args.annotation_file, go_ontology_dict, args.output_dir)
    elif args.app == 'TRINOTATE':
        calculate_trinotate_go_stats(args.annotation_file, go_ontology_dict, args.output_dir)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program calculates GO term statistics generated by annotation applications.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--app', dest='app', help=f'Application (mandatory): {xlib.get_go_app_code_list_text()}.')
    parser.add_argument('--annotation', dest='annotation_file', help='Path of annotation file in CSV or TSV format (mandatory).')
    parser.add_argument('--ontology', dest='ontology_file', help='Path of the GO ontology file (mandatory).')
    parser.add_argument('--outdir', dest='output_dir', help='Path of output directoty where GO term statistics saved (mandatory).')
    parser.add_argument('--toasel', dest='toa_go_selection', help=f'GO terms seleccion (TOA app): {xlib.get_toa_go_seleccion_code_list_text()}; default: {xlib.Const.DEFAULT_TOA_GO_SELECCTION}.')
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

    # check "app"
    if args.app is None:
        xlib.Message.print('error', '*** The application is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.app, xlib.get_go_app_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The application has to be {xlib.get_go_app_code_list_text()}.')
        OK = False
    else:
        args.app = args.app.upper()

    # check "annotation_file"
    if args.annotation_file is None:
        xlib.Message.print('error', '*** The annotation file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.annotation_file):
        xlib.Message.print('error', f'*** The file {args.annotation_file} does not exist.')
        OK = False

    # check "ontology_file"
    if args.ontology_file is None:
        xlib.Message.print('error', '*** The ontology file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.ontology_file):
        xlib.Message.print('error', f'*** The file {args.ontology_file} does not exist.')
        OK = False

    # check "output_dir"
    if args.output_dir is None:
        xlib.Message.print('error', '*** The output directy is not indicated in the input arguments.')
        OK = False
    elif not os.path.isdir(args.output_dir):
        xlib.Message.print('error', '*** The output directy does not exist.')
        OK = False

    # check "toa_go_selection"
    if args.toa_go_selection is None:
        args.toa_go_selection = xlib.Const.DEFAULT_TOA_GO_SELECCTION
    elif not xlib.check_code(args.toa_go_selection, xlib.get_toa_go_seleccion_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The GO terms seleccion (TOA app) has to be {xlib.get_toa_go_seleccion_code_list_text()}.')
        OK = False
    else:
        args.toa_go_selection = args.toa_go_selection.upper()

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

def calculate_blast2go_go_stats(annotation_file, go_ontology_dict, output_dir):
    '''
    Calculate GO term statistics of a Blast2GO annotation file.
    '''

    # initialize the dictionaries
    go_frequency_dict = xlib.NestedDefaultDict()
    go_per_seq_dict = xlib.NestedDefaultDict()
    seq_per_go_dict = xlib.NestedDefaultDict()

    # open the annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', annotation_file)
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', annotation_file)

    # initialize the annotation counter
    annotation_counter = 0

    # read the first record of the annotation file (header)
    annotation_file_id.readline()

    # read the next record of the annotation file (first data record)
    (record, key, data_dict) = xlib.read_blast2go_annotation_record(annotation_file, annotation_file_id, annotation_counter)
    xlib.Message.print('trace', f'key: {key} - record: {record}')

    # while there are records
    while record != '':

        # add 1 to the annotation counter
        annotation_counter += 1

        # extract GO term identifications and add them into the GO identification list
        # go_ids format: "aspect1:GO:id1;aspect2:GO:id2;...;aspectn:GO:idn"
        # aspect values values: P (biological process), F (molecular function), C (cellular component)
        go_id_list_1 = []
        if data_dict['go_ids'] != '':
            seq_go_id_list = data_dict['go_ids'].split(';')
            for i in range(len(seq_go_id_list)):
                go_id_list_1.append(seq_go_id_list[i].strip()[2:])

        # extract InterPro GO term identifications and add them into the GO identification list
        # interpro_go_ids format: "aspect1:GO:id1;aspect2:GO:id2;...;aspectn:GO:idn"
        # aspect values values: P (biological process), F (molecular function), C (cellular component)
        go_id_list_2 = []
        if data_dict['interpro_go_ids'] not in ['', 'no GO terms', 'no IPS match']:
            seq_go_id_list = data_dict['interpro_go_ids'].split(';')
            for i in range(len(seq_go_id_list)):
                go_id_list_2.append(seq_go_id_list[i].strip()[2:])

        # concat GO identification lists
        go_id_list = go_id_list_1 + go_id_list_2

        # increase the GO term counters in the go term frequency dictionary
        for i in range(len(go_id_list)):
            go_id = go_id_list[i]
            counter = go_frequency_dict.get(go_id, 0)
            go_frequency_dict[go_id] = counter + 1

        # add GO term identifications in the go terms per sequence dictionary
        seq_go_list = go_per_seq_dict.get(data_dict['seq_name'], [])
        for go_id in go_id_list:
            if go_id not in seq_go_list:
                seq_go_list.append(go_id)
        go_per_seq_dict[data_dict['seq_name']] = seq_go_list

        # add sequence identication in the sequences per GO term dictionary
        for go_id in go_id_list:
            go_seq_list = seq_per_go_dict.get(go_id, [])
            if data_dict['seq_name'] not in go_seq_list:
                go_seq_list.append(data_dict['seq_name'])
                seq_per_go_dict[go_id] = go_seq_list

        xlib.Message.print('verbose', f'\rAnnotation file: {annotation_counter} processed records')

        # read the next record of the annotation file
        (record, key, data_dict) = xlib.read_blast2go_annotation_record(annotation_file, annotation_file_id, annotation_counter)
        xlib.Message.print('trace', f'key: {key} - record: {record}')

    xlib.Message.print('verbose', '\n')

    # print summary
    xlib.Message.print('info', f'{annotation_counter} annotation records in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # write the GO term frequency
    go_frequency_file = f'{output_dir}/blast2go-go-frequency.csv'
    write_go_frequency(go_frequency_dict, go_ontology_dict, go_frequency_file)
    xlib.Message.print('info', f'The file {os.path.basename(go_frequency_file)} is generated.')

    # write go terms per sequence
    go_per_seq_file = f'{output_dir}/blast2go-go-per-seq.csv'
    write_go_per_seq(go_per_seq_dict, go_ontology_dict, go_per_seq_file)
    xlib.Message.print('info', f'The file {os.path.basename(go_per_seq_file)} is generated.')

    # write sequence identification per go term
    seq_per_go_file = f'{output_dir}/blast2go-seq-per-go.csv'
    write_seq_per_go(seq_per_go_dict, go_ontology_dict, seq_per_go_file)
    xlib.Message.print('info', f'The file {os.path.basename(seq_per_go_file)} is generated.')

#-------------------------------------------------------------------------------

def calculate_entap_go_stats(annotation_file, go_ontology_dict, output_dir):
    '''
    Calculate GO term statistics of a EnTAP annotation file.
    '''

    # initialize the dictionaries
    go_frequency_dict = xlib.NestedDefaultDict()
    go_per_seq_dict = xlib.NestedDefaultDict()
    seq_per_go_dict = xlib.NestedDefaultDict()

    # open the annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', annotation_file)
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', annotation_file)

    # initialize the annotation counter
    annotation_counter = 0

    # read the first record of the annotation file (header)
    annotation_file_id.readline()

    # read the next record of the annotation file (first data record)
    (record, key, data_dict) = xlib.read_entap_runn_annotation_record(annotation_file, annotation_file_id, annotation_counter)
    xlib.Message.print('trace', f'key: {key} - record: {record}')

    # while there are records
    while record != '':

        # add 1 to the annotation counter
        annotation_counter += 1

        # extract biological GO term identifications and add them into the GO identification list
        # go_biological format: "GO:id1-desc1,GO:id2-desc2,...,GO:idn-descn"
        go_id_list_1 = []
        if data_dict['eggnog_go_biological'] != '':
            seq_go_data_list_1 = data_dict['eggnog_go_biological'].split(',')
            for go_data in seq_go_data_list_1:
                if go_data.strip().startswith('GO:'):
                    go_id_list_1.append(go_data[:10])

        # extract cellular GO terms identifications and add them into the GO identification list
        # go_cellular format: "GO:id1-desc1,GO:id2-desc2,...,GO:idn-descn"
        go_id_list_2 = []
        if data_dict['eggnog_go_cellular'] != '':
            seq_go_data_list_2 = data_dict['eggnog_go_cellular'].split(',')
            for go_data in seq_go_data_list_2:
                if go_data.strip().startswith('GO:'):
                    go_id_list_2.append(go_data[:10])

        # extract molecular GO term identifications and add them into the GO identification list
        # go_molecular format: "GO:id1-desc1,GO:id2-desc2,...,GO:idn-descn"
        go_id_list_3 = []
        if data_dict['eggnog_go_molecular'] != '':
            seq_go_data_list_3 = data_dict['eggnog_go_molecular'].split(',')
            for go_data in seq_go_data_list_3:
                if go_data.strip().startswith('GO:'):
                    go_id_list_3.append(go_data[:10])

        # concat GO identification lists
        go_id_list = go_id_list_1 + go_id_list_2 + go_id_list_3

        # increase the GO term counters in the go term frequency dictionary
        for i in range(len(go_id_list)):
            go_id = go_id_list[i]
            counter = go_frequency_dict.get(go_id, 0)
            go_frequency_dict[go_id] = counter + 1

        # add GO term identifications in the go term per sequence dictionary
        seq_go_list = go_per_seq_dict.get(data_dict['query_sequence'], [])
        for go_id in go_id_list:
            if go_id not in seq_go_list:
                seq_go_list.append(go_id)
        go_per_seq_dict[data_dict['query_sequence']] = seq_go_list

        # add sequence identication in the sequences per GO term dictionary
        for go_id in go_id_list:
            go_seq_list = seq_per_go_dict.get(go_id, [])
            if data_dict['query_sequence'] not in go_seq_list:
                go_seq_list.append(data_dict['query_sequence'])
                seq_per_go_dict[go_id] = go_seq_list

        xlib.Message.print('verbose', f'\rAnnotation file: {annotation_counter} processed records')

        # read the next record of the annotation file
        (record, key, data_dict) = xlib.read_entap_runn_annotation_record(annotation_file, annotation_file_id, annotation_counter)
        xlib.Message.print('trace', f'key: {key} - record: {record}')

    xlib.Message.print('verbose', '\n')

    # print summary
    xlib.Message.print('info', f'{annotation_counter} annotation records in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # write the GO term frequency
    go_frequency_file = f'{output_dir}/entap-go-frequency.csv'
    write_go_frequency(go_frequency_dict, go_ontology_dict, go_frequency_file)
    xlib.Message.print('info', f'The file {os.path.basename(go_frequency_file)} is generated.')

    # write go terms per sequence
    go_per_seq_file = f'{output_dir}/entap-go-per-seq.csv'
    write_go_per_seq(go_per_seq_dict, go_ontology_dict, go_per_seq_file)
    xlib.Message.print('info', f'The file {os.path.basename(go_per_seq_file)} is generated.')

    # write sequence identification per go term
    seq_per_go_file = f'{output_dir}/entap-seq-per-go.csv'
    write_seq_per_go(seq_per_go_dict, go_ontology_dict, seq_per_go_file)
    xlib.Message.print('info', f'The file {os.path.basename(seq_per_go_file)} is generated.')

#-------------------------------------------------------------------------------

def calculate_toa_go_stats(annotation_file, go_ontology_dict, output_dir, toa_go_selection):
    '''
    Calculate GO term statistics of a TOA annotation file (only the sequence with the lowest e-Value is considered).
    '''

    # initialize the statistics dictionaries
    go_frequency_dict = xlib.NestedDefaultDict()
    go_per_seq_dict = xlib.NestedDefaultDict()
    seq_per_go_dict = xlib.NestedDefaultDict()

    # open the annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', annotation_file)
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', annotation_file)

    # initialize the annotation counter
    annotation_counter = 0

    # read the first record of the annotation file (header)
    annotation_file_id.readline()

    # read the secord record of the annotation file (first data record)
    (record, key, data_dict) = xlib.read_toa_annotation_record(annotation_file, annotation_file_id, 'MERGER', annotation_counter)
    xlib.Message.print('trace', f'key: {key} - record: {record}')

    # while there are records
    while record != '':

        # initialize the old sequence identification
        old_nt_seq_id = data_dict['nt_seq_id']

        # initialize the minimum e-value and go identification list of the sequence hit/hsp with less e-value
        min_evalue = 9999
        min_evalue_go_id_list = []

        # while there are records and the same sequence identification
        while record != '' and data_dict['nt_seq_id'] == old_nt_seq_id:

            # add 1 to the annotation counter
            annotation_counter += 1

            # extract the GO term identifications and add them into the GO identification list
            # go_id format: "GO:id1*id2*...*idn"
            if data_dict['go_id'] != '':
                go_id_list = data_dict['go_id'][3:].split('*')
            else:
                go_id_list = []

            # save the go identification list of the sequence hit/hsp with less e-value
            if toa_go_selection == 'LEV': # the lowest e-value (GO data can be empty) is considered
                if float(data_dict['hsp_evalue']) < min_evalue:
                    min_evalue_go_id_list = go_id_list
                    min_evalue = float(data_dict['hsp_evalue'])
            elif toa_go_selection == 'LEVWD': # the lowest e-value with GO data not empty is considered
                if float(data_dict['hsp_evalue']) < min_evalue and go_id_list:
                    min_evalue_go_id_list = go_id_list
                    min_evalue = float(data_dict['hsp_evalue'])

            xlib.Message.print('verbose', f'\rAnnotation file: {annotation_counter} processed records')

            # read the next record of the annotation file
            (record, key, data_dict) = xlib.read_toa_annotation_record(annotation_file, annotation_file_id, 'MERGER', annotation_counter)
            xlib.Message.print('trace', f'key: {key} - record: {record}')

        # increase the GO term counter in the go term frequency dictionary
        for i in range(len(min_evalue_go_id_list)):
            go_id = f'GO:{min_evalue_go_id_list[i]}'
            frequency = go_frequency_dict.get(go_id, 0)
            go_frequency_dict[go_id] = frequency + 1

        # add GO term identifications in the blastx go terms per sequence dictionary
        seq_go_list = go_per_seq_dict.get(old_nt_seq_id, [])
        for i in range(len(min_evalue_go_id_list)):
            go_id = f'GO:{min_evalue_go_id_list[i]}'
            if go_id not in seq_go_list:
                seq_go_list.append(go_id)
        go_per_seq_dict[old_nt_seq_id] = seq_go_list

        # add sequence identication in the blastx sequences per GO term dictionary
        for i in range(len(min_evalue_go_id_list)):
            go_id = f'GO:{min_evalue_go_id_list[i]}'
            go_seq_list = seq_per_go_dict.get(go_id, [])
            if old_nt_seq_id not in go_seq_list:
                go_seq_list.append(old_nt_seq_id)
                seq_per_go_dict[go_id] = go_seq_list

    xlib.Message.print('verbose', '\n')

    # print summary
    xlib.Message.print('info', f'{annotation_counter} annotation records in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # write the GO term frequency
    go_frequency_file = f'{output_dir}/toa-go-frequency.csv'
    write_go_frequency(go_frequency_dict, go_ontology_dict, go_frequency_file)
    xlib.Message.print('info', f'The file {os.path.basename(go_frequency_file)} is generated.')

    # write go terms per sequence
    go_per_seq_file = f'{output_dir}/toa-go-per-seq.csv'
    write_go_per_seq(go_per_seq_dict, go_ontology_dict, go_per_seq_file)
    xlib.Message.print('info', f'The file {os.path.basename(go_per_seq_file)} is generated.')

    # write sequence identification per go term
    seq_per_go_file = f'{output_dir}/toa-seq-per-go.csv'
    write_seq_per_go(seq_per_go_dict, go_ontology_dict, seq_per_go_file)
    xlib.Message.print('info', f'The file {os.path.basename(seq_per_go_file)} is generated.')

#-------------------------------------------------------------------------------

def calculate_trapid_go_stats(annotation_file, go_ontology_dict, output_dir):
    '''
    Calculate GO term statistics of a TRAPID annotation file.
    '''

    # initialize the dictionaries
    go_frequency_dict = xlib.NestedDefaultDict()
    go_per_seq_dict = xlib.NestedDefaultDict()
    seq_per_go_dict = xlib.NestedDefaultDict()

    # open the annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', annotation_file)
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', annotation_file)

    # initialize the annotation counter
    annotation_counter = 0

    # read the first record of the annotation file (header)
    annotation_file_id.readline()

    # read the next record of the annotation file (first data record)
    (record, key, data_dict) = xlib.read_trapid_annotation_record(annotation_file, annotation_file_id, annotation_counter)
    xlib.Message.print('trace', f'key: {key} - record: {record}')

    # while there are records
    while record != '':

        # add 1 to the annotation counter
        annotation_counter += 1

        # increase the GO term counter in the go term frequency dictionary
        frequency = go_frequency_dict.get(data_dict['go'], 0)
        go_frequency_dict[data_dict['go']] = frequency + 1

        # add GO term identification in the go term per sequence dictionary
        seq_go_list = go_per_seq_dict.get(data_dict['transcript_id'], [])
        if data_dict['go'] not in seq_go_list:
            seq_go_list.append(data_dict['go'])
            go_per_seq_dict[data_dict['transcript_id']] = seq_go_list

        # add sequence identication in the sequences per GO term dictionary
        go_seq_list = seq_per_go_dict.get(data_dict['go'], [])
        if data_dict['transcript_id'] not in go_seq_list:
            go_seq_list.append(data_dict['transcript_id'])
            seq_per_go_dict[data_dict['go']] = go_seq_list

        xlib.Message.print('verbose', f'\rAnnotation file: {annotation_counter} processed records')

        # read the next record of the annotation file
        (record, key, data_dict) = xlib.read_trapid_annotation_record(annotation_file, annotation_file_id, annotation_counter)
        xlib.Message.print('trace', f'key: {key} - record: {record}')

    xlib.Message.print('verbose', '\n')

    # print summary
    xlib.Message.print('info', f'{annotation_counter} annotation records in annotation file.'.format())

    # close annotation file
    annotation_file_id.close()

    # write the GO term frequency
    go_frequency_file = f'{output_dir}/trapid-go-frequency.csv'
    write_go_frequency(go_frequency_dict, go_ontology_dict, go_frequency_file)
    xlib.Message.print('info', f'The file {os.path.basename(go_frequency_file)} is generated.')

    # write go terms per sequence
    go_per_seq_file = f'{output_dir}/trapid-go-per-seq.csv'
    write_go_per_seq(go_per_seq_dict, go_ontology_dict, go_per_seq_file)
    xlib.Message.print('info', f'The file {os.path.basename(go_per_seq_file)} is generated.')

    # write sequence identification per go term
    seq_per_go_file = f'{output_dir}/trapid-seq-per-go.csv'
    write_seq_per_go(seq_per_go_dict, go_ontology_dict, seq_per_go_file)
    xlib.Message.print('info', f'The file {os.path.basename(seq_per_go_file)} is generated.')

#-------------------------------------------------------------------------------

def calculate_trinotate_go_stats(annotation_file, go_ontology_dict, output_dir):
    '''
    Calculate GO term statistics of a Trinotate annotation file.
    '''

    # initialize the dictionaries
    blastx_go_frequency_dict = xlib.NestedDefaultDict()
    blastx_go_per_seq_dict = xlib.NestedDefaultDict()
    blastx_seq_per_go_dict = xlib.NestedDefaultDict()
    blastp_go_frequency_dict = xlib.NestedDefaultDict()
    blastp_go_per_seq_dict = xlib.NestedDefaultDict()
    blastp_seq_per_go_dict = xlib.NestedDefaultDict()

    # open the annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', annotation_file)
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', annotation_file)

    # initialize the annotation counter
    annotation_counter = 0

    # read the first record of the annotation file (header)
    annotation_file_id.readline()

    # read the next record of the annotation file (first data record)
    (record, key, data_dict) = xlib.read_trinotate_annotation_record(annotation_file, annotation_file_id, annotation_counter)
    xlib.Message.print('trace', f'key: {key} - record: {record}')

    # while there are records
    while record != '':

        # add 1 to the annotation counter
        annotation_counter += 1

        # extract blastx GO term identifications and add them into the GO identification list
        # gene_ontology_blastx format: GO:id1^aspect1^desc1`GO:id2^aspect2^desc2`...`GO:idn^aspectn^descn
        # aspect values: biological process (P), molecular function (F), cellular component (C)
        blastx_go_id_list = []
        if data_dict['gene_ontology_blastx'] != '.':
            go_data_list = data_dict['gene_ontology_blastx'].split(r'`')
            for go_data in go_data_list:
                (go_id, _, _) = go_data.split('^')
                blastx_go_id_list.append(go_id)

        # increase the GO term counter in the blastx go term frequency dictionary
        for i in range(len(blastx_go_id_list)):
            go_id = blastx_go_id_list[i]
            frequency = blastx_go_frequency_dict.get(go_id, 0)
            blastx_go_frequency_dict[go_id] = frequency + 1

        # add GO term identifications in the blastx go terms per sequence dictionary
        seq_go_list = blastx_go_per_seq_dict.get(data_dict['transcript_id'], [])
        for go_id in blastx_go_id_list:
            if go_id not in seq_go_list:
                seq_go_list.append(go_id)
        blastx_go_per_seq_dict[data_dict['transcript_id']] = seq_go_list

        # add sequence identication in the blastx sequences per GO term dictionary
        for go_id in blastx_go_id_list:
            go_seq_list = blastx_seq_per_go_dict.get(go_id, [])
            if data_dict['transcript_id'] not in go_seq_list:
                go_seq_list.append(data_dict['transcript_id'])
                blastx_seq_per_go_dict[go_id] = go_seq_list

        # extract blastp GO term identifications and add them into the GO identification list
        # gene_ontology_blastp format: GO:id1^aspect1^desc1`GO:id2^aspect2^desc2`...`GO:idn^aspectn^descn
        # aspect values: biological process (P), molecular function (F), cellular component (C)
        blastp_go_id_list = []
        if data_dict['gene_ontology_blastp'] != '.':
            go_data_list = data_dict['gene_ontology_blastp'].split(r'`')
            for go_data in go_data_list:
                (go_id, _, _) = go_data.split('^')
                blastp_go_id_list.append(go_id)

        # increase the GO term counter in the blastp go term frequency dictionary
        for i in range(len(blastp_go_id_list)):
            go_id = blastp_go_id_list[i]
            frequency = blastp_go_frequency_dict.get(go_id, 0)
            blastp_go_frequency_dict[go_id] = frequency + 1

        # add GO term identifications in the blastp go terms per sequence dictionary
        seq_go_list = blastp_go_per_seq_dict.get(data_dict['transcript_id'], [])
        for go_id in blastp_go_id_list:
            if go_id not in seq_go_list:
                seq_go_list.append(go_id)
        blastp_go_per_seq_dict[data_dict['transcript_id']] = seq_go_list

        # add sequence identication in the blastp sequences per GO term dictionary
        for go_id in blastp_go_id_list:
            go_seq_list = blastp_seq_per_go_dict.get(go_id, [])
            if data_dict['transcript_id'] not in go_seq_list:
                go_seq_list.append(data_dict['transcript_id'])
                blastp_seq_per_go_dict[go_id] = go_seq_list

        xlib.Message.print('verbose', f'\rAnnotation file: {annotation_counter} processed records')

        # read the next record of the annotation file
        (record, key, data_dict) = xlib.read_trinotate_annotation_record(annotation_file, annotation_file_id, annotation_counter)
        xlib.Message.print('trace', f'key: {key} - record: {record}')

    xlib.Message.print('verbose', '\n')

    # print summary
    xlib.Message.print('info', f'{annotation_counter} annotation records in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # write the GO term frequency
    blastx_go_frequency_file = f'{output_dir}/trinotate-blastx-go-frequency.csv'
    write_go_frequency(blastx_go_frequency_dict, go_ontology_dict, blastx_go_frequency_file)
    xlib.Message.print('info', f'The file {os.path.basename(blastx_go_frequency_file)} is generated.')
    blastp_go_frequency_file = f'{output_dir}/trinotate-blastp-go-frequency.csv'
    write_go_frequency(blastp_go_frequency_dict, go_ontology_dict, blastp_go_frequency_file)
    xlib.Message.print('info', f'The file {os.path.basename(blastp_go_frequency_file)} is generated.')

    # write go terms per sequence
    blastx_go_per_seq_file = f'{output_dir}/trinotate-blastx-go-per-seq.csv'
    write_go_per_seq(blastx_go_per_seq_dict, go_ontology_dict, blastx_go_per_seq_file)
    xlib.Message.print('info', f'The file {os.path.basename(blastx_go_per_seq_file)} is generated.')
    blastp_go_per_seq_file = f'{output_dir}/trinotate-blastp-go-per-seq.csv'
    write_go_per_seq(blastp_go_per_seq_dict, go_ontology_dict, blastp_go_per_seq_file)
    xlib.Message.print('info', f'The file {os.path.basename(blastp_go_per_seq_file)} is generated.')

    # write sequence identification per go term
    blastx_seq_per_go_file = f'{output_dir}/trinotate-blastx-seq-per-go.csv'
    write_seq_per_go(blastx_seq_per_go_dict, go_ontology_dict, blastx_seq_per_go_file)
    xlib.Message.print('info', f'The file {os.path.basename(blastx_seq_per_go_file)} is generated.')
    blastp_seq_per_go_file = f'{output_dir}/trinotate-blastp-seq-per-go.csv'
    write_seq_per_go(blastp_seq_per_go_dict, go_ontology_dict, blastp_seq_per_go_file)
    xlib.Message.print('info', f'The file {os.path.basename(blastp_seq_per_go_file)} is generated.')

#-------------------------------------------------------------------------------

def write_go_frequency(go_frequency_dict, go_ontology_dict, go_id_stats_file):
    '''
    Write GO term frequency.
    '''

    # open the file of statistics
    if go_id_stats_file.endswith('.gz'):
        try:
            go_id_stats_file_id = gzip.open(go_id_stats_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', go_id_stats_file)
    else:
        try:
            go_id_stats_file_id = open(go_id_stats_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', go_id_stats_file)

    # write the header in the file of statistics
    go_id_stats_file_id.write( '"go_term";"name";"namespace";"count"\n')

    # write data in the file of statistics
    for go_id in sorted(go_frequency_dict.keys()):
        go_name = go_ontology_dict[go_id]['go_name']
        namespace = go_ontology_dict[go_id]['namespace']
        go_id_stats_file_id.write(f'"{go_id}";"{go_name}";"{namespace}";{go_frequency_dict[go_id]}\n')

    # close the file of statistics
    go_id_stats_file_id.close()

#-------------------------------------------------------------------------------

def write_go_per_seq(go_per_seq_dict, go_ontology_dict, stats_file):
    '''
    Write GO terms per sequence (each record is a pair sequence identification-go term).
    '''

    # open the file of statistics
    if stats_file.endswith('.gz'):
        try:
            stats_file_id = gzip.open(stats_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', stats_file)
    else:
        try:
            stats_file_id = open(stats_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', stats_file)

    # write the header in the file of statistics
    stats_file_id.write( '"seq_id";"go_id";"namespace"\n')

    # write data in the file of statistics
    for seq_id in sorted(go_per_seq_dict.keys()):
        go_id_list = go_per_seq_dict[seq_id]
        for go_id in sorted(go_id_list):
            namespace = go_ontology_dict[go_id]['namespace']
            stats_file_id.write(f'"{seq_id}";"{go_id}";"{namespace}"\n')

    # close the file of statistics
    stats_file_id.close()

#-------------------------------------------------------------------------------

def write_seq_per_go(seq_per_go_dict, go_ontology_dict, stats_file):
    '''
    Write sequences identifications per GO terms (each record is a pair sequence go term-identification).
    '''

    # open the file of statistics
    if stats_file.endswith('.gz'):
        try:
            stats_file_id = gzip.open(stats_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', stats_file)
    else:
        try:
            stats_file_id = open(stats_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', stats_file)

    # write the header in the file of statistics
    stats_file_id.write( '"go_id";"namespace";"seq_id"\n')

    # write data in the file of statistics
    for go_id in sorted(seq_per_go_dict.keys()):
        seq_id_list = seq_per_go_dict[go_id]
        for seq_id in sorted(seq_id_list):
            namespace = go_ontology_dict[go_id]['namespace']
            stats_file_id.write(f'"{go_id}";"{namespace}";"{seq_id}"\n')

    # close the file of statistics
    stats_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
