#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program gets the gene identification corresponding to transcripts from a GFF file.

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

    # get the gene identification corresponding to transcripts from a GFF file
    get_transcripts_geneid(args.gff_file, args.gff_format, args.transcripts_geneid_file, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program gets the gene identification corresponding to transcripts from a GFF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--gff', dest='gff_file', help='Path of the GFF file (mandatory).')
    parser.add_argument('--format', dest='gff_format', help='The format of the transcript GFF file: GFF3; default: GFF3.')
    parser.add_argument('--out', dest='transcripts_geneid_file', help='Path of the file with transcripts gene identifications (mandatory).')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')
    parser.add_argument('--tvi', dest='tvi_list', help='Genomic sequence identification list to trace with format seq_id_1,seq_id_2,...,seq_id_n or NONE; default: NONE.')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def check_args(args):
    '''
    Check the input arguments.
    '''

    # initialize the control variable
    OK = True

    # check "gff_file"
    if args.gff_file is None:
        xlib.Message.print('error', '*** The input GFF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.gff_file):
        xlib.Message.print('error', f'*** The file {args.gff_file} does not exist.')
        OK = False

    # check "gff_format"
    if args.gff_format is None:
        args.gff_format = 'GFF3'
    elif args.gff_format.upper() != 'GFF3':
        xlib.Message.print('error', '*** The format of the GFF file has to be GFF3.')
        OK = False
    else:
        args.gff_format = args.gff_format.upper()

    # check "transcripts_geneid_file"
    if args.transcripts_geneid_file is None:
        xlib.Message.print('error', '*** The output FASTA file with the RNA sequences is not indicated in the input arguments.')
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

    # check "tvi_list"
    if args.tvi_list is None or args.tvi_list == 'NONE':
        args.tvi_list = []
    else:
        args.tvi_list = xlib.split_literal_to_text_list(args.tvi_list)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def get_transcripts_geneid(gff_file, gff_format, transcripts_geneid_file, tvi_list):
    '''
    Gets the gene identification corresponding to transcripts from a GFF file.
    '''

    # open the input GFF file
    if gff_file.endswith('.gz'):
        try:
            gff_file_id = gzip.open(gff_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', gff_file)
    else:
        try:
            gff_file_id = open(gff_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', gff_file)

    # open the file with transcripts gene identifications
    if transcripts_geneid_file.endswith('.gz'):
        try:
            transcripts_geneid_file_id = gzip.open(transcripts_geneid_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', transcripts_geneid_file)
    else:
        try:
            transcripts_geneid_file_id = open(transcripts_geneid_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', transcripts_geneid_file)

    # write the head of the file with transcripts gene identifications
    transcripts_geneid_file_id.write('seq_id;gene_id\n')

    # initialize counters
    record_counter = 0
    gene_ids_counter = 0

    # read the first record of input GFF file
    record = gff_file_id.readline()

    # while there are records in the input GFF file
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # process data records
        if not record.startswith('#'):

            # extract data
            # record format: seq_id <field_sep> source <field_sep> type <field_sep> start <field_sep> end <field_sep> score <field_sep> strand <field_sep> phase <field_sep> attributes <record_sep>
            field_sep = '\t'
            record_sep = '\n'
            data_list = re.split(field_sep, record.replace(record_sep,''))
            try:
                seq_id = data_list[0].strip()
                type = data_list[2].strip()
                attributes = data_list[8].strip()
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(gff_file), record_counter)

            # only the type "gene"is considerer
            if type == 'gene':

                # add 1 to the gene identifications counter
                gene_ids_counter += 1

                # get "gene_id" data from "attributes"
                gene_id = xlib.get_na()
                literal = 'gene_id='
                pos_1 = attributes.find(literal)
                if pos_1 > -1:
                    pos_2 = attributes.find(';', pos_1 + len(literal) + 1)
                    gene_id = attributes[pos_1 + len(literal):pos_2]

                # write the gene identification in the file with transcripts gene identifications
                transcripts_geneid_file_id.write(f'{seq_id};{gene_id}\n')

        # print record counter
        xlib.Message.print('verbose', f'\rGFF file records: {record_counter:8d} - Genes identifications: {gene_ids_counter:8d}')

        # read the next record of input GFF file
        record = gff_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close files
    gff_file_id.close()
    transcripts_geneid_file_id.close()

    # print OK message
    xlib.Message.print('verbose', f'\nThe file {os.path.basename(transcripts_geneid_file)} containing transcripts gene identifications is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
