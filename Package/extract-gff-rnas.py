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
This program extracts RNA sequences from a GFF file and its corresponding genome 
FASTA file.
'''

#-------------------------------------------------------------------------------

import argparse
import gzip
import os
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

    # extract RNA sequences from a GFF file and its corresponding genome FASTA file
    extract_gff_rnas(args.gff_file, args.gff_format, args.genome_file, args.rna_file, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program extracts RNA sequences from a GFF file and its corresponding genome FASTA file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--gff', dest='gff_file', help='Path of the GFF file (mandatory).')
    parser.add_argument('--format', dest='gff_format', help='The format of the transcript GFF file: GFF3; default: GFF3.')
    parser.add_argument('--genome', dest='genome_file', help='Path of the FASTA genome file (mandatory)')
    parser.add_argument('--out', dest='rna_file', help='Path of the output FASTA file with the RNA sequences in cDNA format (mandatory).')
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

    # check "genome_file"
    if args.genome_file is None:
        xlib.Message.print('error', '*** The FASTA genome file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.genome_file):
        xlib.Message.print('error', f'*** The file {args.genome_file} does not exist.')
        OK = False

    # check "rna_file"
    if args.rna_file is None:
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
        args.tvi_list = xlib.split_literal_to_string_list(args.tvi_list)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def extract_gff_rnas(gff_file, gff_format, genome_file, rna_file, tvi_list):
    '''
    Extract RNA sequences from a GFF file and its corresponding genome FASTA file.
    '''

    # initialize RNA sequences per seq_id dictionary
    rna_seq_id_dict = {}

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

    # initialize counters
    record_counter = 0
    rna_counter = 0

    # read the first record
    record = gff_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # process data records
        if not record.startswith('#'):

            # extract data
            # record format: seq_id\tsource\ttype\tstart\tend\tscore\tstrand\tphase\tattributes
            data_list = []
            pos_1 = 0
            for pos_2 in [i for i, chr in enumerate(record) if chr == '\t']:
                data_list.append(record[pos_1:pos_2].strip())
                pos_1 = pos_2 + 1
            data_list.append(record[pos_1:].strip('\n').strip())
            try:
                seq_id = data_list[0]
                type = data_list[2]
                start = int(data_list[3])
                end = int(data_list[4])
                attributes = data_list[8]
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(gff_file), record_counter)

            # only the type "mRNA"is considerer
            if type == 'mRNA':

                # add 1 to RNA counter
                rna_counter += 1

                # get "gene" data from "attributes"
                gene = xlib.get_na()
                literal = 'gene='
                pos_1 = attributes.find(literal)
                if pos_1 > -1:
                    pos_2 = attributes.find(';', pos_1 + len(literal) + 1)
                    gene = attributes[pos_1 + len(literal):pos_2]

                # add RNA sequence to RNA sequences per seq_id dictionary
                if rna_seq_id_dict.get(seq_id, {}) == {}:
                    rna_seq_id_dict[seq_id] = {}
                key = f'{start}-{end}'
                rna_seq_id_dict[seq_id][key] = {'start': start, 'end' : end, 'gene': gene}

        # print record counter
        xlib.Message.print('verbose', f'\rGFF file records... {record_counter:8d} - RNA seqs... {rna_counter:8d}')

        # read the next record
        record = gff_file_id.readline()

    xlib.Message.print('verbose', '\n')

    for x in tvi_list: 
        xlib.Message.print('trace', f'RNA seq in {x}: {rna_seq_id_dict.get(x, {})}')

    # close the input GFF file
    gff_file_id.close()

    # open the genome file
    if genome_file.endswith('.gz'):
        try:
            genome_file_id = gzip.open(genome_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', genome_file)
    else:
        try:
            genome_file_id = open(genome_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', genome_file)

    # open the output FASTA file with the RNA sequences
    if rna_file.endswith('.gz'):
        try:
            rna_file_id = gzip.open(rna_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', rna_file)
    else:
        try:
            rna_file_id = open(rna_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', rna_file)

    # initialize record counters
    genomic_seq_counter = 0
    rna_seq_counter = 0
 
    # read the first record of genome file
    record = genome_file_id.readline()

    # while there are records in genome file
    while record != '':

        # process the head record 
        if record.startswith('>'):

            # add 1 to the read sequence counter
            genomic_seq_counter += 1

            # extract the identification
            space_pos = record[1:].find(' ')
            if space_pos > -1:
                id = record[1:space_pos + 1]
            else:
                id = record[1:].strip('\n')

            # initialize the sequence
            seq = ''

            # read the next record
            record = genome_file_id.readline()

        else:

            # control the FASTA format
            raise xlib.ProgramException('F006', genome_file, 'FASTA')

        # while there are records and they are sequence
        while record != '' and not record.startswith('>'):

            # concatenate the record to the sequence
            seq += record.strip()

            # read the next record of genome file
            record = genome_file_id.readline()

        # get RNA sequences corresponding to this genomic sequence
        rna_dict = rna_seq_id_dict.get(id, {})

        # if there are RNAs corresponding to this genomic sequence
        if rna_dict != {}:

            # for each RNA
            for key in rna_dict.keys():

                # get the RNA data
                start = rna_dict[key]['start']
                end = rna_dict[key]['end']
                gene = rna_dict[key]['gene']

                # write the identification record
                rna_file_id.write(f'>seq_id: {id} - start: {start} - end: {end} - gene: {gene}\n')

                # wite the sequence (start and end have 1-base offset in GFF file)
                rna_file_id.write(f'{seq[start - 1:end]}\n')

                # add 1 to the RNA sequence counter
                rna_seq_counter += 1

        # print the counters
        xlib.Message.print('verbose', f'\rGenome seqs... {genomic_seq_counter:8d} - RNA seqs... {rna_seq_counter:8d}')

    # close files
    genome_file_id.close()
    rna_file_id.close()

    # print OK message 
    xlib.Message.print('verbose', f'\nThe file {os.path.basename(rna_file)} containing FASTA RNA sequences in cDNA format cDNA is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
