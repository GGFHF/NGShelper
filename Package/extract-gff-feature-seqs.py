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
This program extracts sequences of features (genes, CDS) from a NCBI GFF file.

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
import sys

from Bio import SeqIO

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

    # extract sequences of features (genes, RNAs, CDS) from a GFF file
    extract_gff_feature_seqs(args.genome_file, args.gff_file, args.gene_file, args.cds_file, args.concatenated_cds_file, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program extracts sequences of features (genes, CDS) from a GFF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--genome', dest='genome_file', help='Path of the FASTA genome file (mandatory)')
    parser.add_argument('--gff', dest='gff_file', help='Path of the GFF file corresponding to the genome file (mandatory).')
    parser.add_argument('--gene-file', dest='gene_file', help='Path of the output FASTA file with the gene sequences (mandatory).')
    parser.add_argument('--cds-file', dest='cds_file', help='Path of the output FASTA file with the CDS sequences (mandatory).')
    parser.add_argument('--concds-file', dest='concatenated_cds_file', help='Path of the output FASTA file with the concatenated sequences of the same protein (mandatory).')
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

    # check "genome_file"
    if args.genome_file is None:
        xlib.Message.print('error', '*** The FASTA genome file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.genome_file):
        xlib.Message.print('error', f'*** The file {args.genome_file} does not exist.')
        OK = False

    # check "gff_file"
    if args.gff_file is None:
        xlib.Message.print('error', '*** The input GFF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.gff_file):
        xlib.Message.print('error', f'*** The file {args.gff_file} does not exist.')
        OK = False

    # check "gene_file"
    if args.gene_file is None:
        xlib.Message.print('error', '*** The output FASTA file with the gene sequences is not indicated in the input arguments.')
        OK = False

    # check "cds_file"
    if args.cds_file is None:
        xlib.Message.print('error', '*** The output FASTA file with the CDS sequences is not indicated in the input arguments.')
        OK = False

    # check "concatenated_cds_file"
    if args.concatenated_cds_file is None:
        xlib.Message.print('error', '*** The output FASTA file with the concatenated sequences of the same protein is not indicated in the input arguments.')
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

def extract_gff_feature_seqs(genome_file, gff_file, gene_file, cds_file, concatenated_cds_file, tvi_list):
    '''
    Extract sequences of features (genes, CDS) from a GFF file.
    '''

    # get genome dictionary
    genome_dict = SeqIO.to_dict(SeqIO.parse(genome_file, 'fasta'))

    # initialize previous cds group data
    old_gene_id = xlib.get_na()
    old_protein_id = xlib.get_na()
    old_cds_group_id = xlib.get_na()
    old_cds_group_strand = xlib.get_na()

    # initialize cds group data list
    cds_group_data_list = []

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

    # open the file with gene sequences
    if gene_file.endswith('.gz'):
        try:
            gene_file_id = gzip.open(gene_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', gene_file)
    else:
        try:
            gene_file_id = open(gene_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', gene_file)

    # open the file with CDS sequences
    if cds_file.endswith('.gz'):
        try:
            cds_file_id = gzip.open(cds_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', cds_file)
    else:
        try:
            cds_file_id = open(cds_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', cds_file)

    # open the file with concatenated CDS sequences
    if concatenated_cds_file.endswith('.gz'):
        try:
            concatenated_cds_file_id = gzip.open(concatenated_cds_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', concatenated_cds_file)
    else:
        try:
            concatenated_cds_file_id = open(concatenated_cds_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', concatenated_cds_file)

    # initialize counters
    record_counter = 0
    gene_counter = 0
    cds_counter = 0
    concatenated_cds_counter = 0

    # read the first record of input GFF file
    (record, _, data_dict) = xlib.read_gff_file(gff_file_id)

    # while there are records in the input GFF file
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # process data records
        if not record.startswith('#') and record != '\n':

            # extract the genome sequence corresponding to the feature
            genome_seq = xlib.get_genome_seq(genome_dict, data_dict['seq_id'], int(data_dict['start']), int(data_dict['end']), data_dict['strand'])

            # when th sequence type "gene"
            if data_dict['seq_type'] == 'gene':

                # add 1 to the gene counter
                gene_counter += 1

                # get "gene_id" data from "attributes"
                gene_id = xlib.get_na()
                literal = 'ID='
                pos_1 = data_dict['attributes'].find(literal)
                if pos_1 > -1:
                    pos_2 = data_dict['attributes'].find(';', pos_1 + len(literal) + 1)
                    gene_id = data_dict['attributes'][pos_1 + len(literal):pos_2]

                # write the record of file with gene sequences
                gene_file_id.write(f'>{gene_id} (seq_id:{data_dict['seq_id']}|start:{data_dict['start']}|end:{data_dict['end']}|strand:{data_dict['strand']})\n')
                gene_file_id.write(f'{genome_seq}\n')

            # when the sequence type is "CDS"
            elif data_dict['seq_type'] == 'CDS':

                # add 1 to the CDS counter
                cds_counter += 1

                # get "cds_id" data from "attributes"
                cds_id = xlib.get_na()
                literal = 'ID='
                pos_1 = data_dict['attributes'].find(literal)
                if pos_1 > -1:
                    pos_2 = data_dict['attributes'].find(';', pos_1 + len(literal) + 1)
                    cds_id = data_dict['attributes'][pos_1 + len(literal):pos_2]

                # build the CDS group identification (CDS identification without order number) and its data
                cds_group_id = xlib.get_na()
                literal_1 = '-cds'
                literal_2 = '.cds'
                literal_3 = ':cds'
                literal_4 = ':CDS'
                pos_2 = max(cds_id.find(literal_1), cds_id.find(literal_2), cds_id.find(literal_3), cds_id.find(literal_4))
                if pos_2 > -1:
                    cds_group_id = cds_id[:pos_2]
                else:
                    cds_group_id = cds_id

                # get "protein_id" data from "attributes"
                protein_id = xlib.get_na()
                # NCBI Genome assemblies
                literal = 'protein_id='
                pos_1 = data_dict['attributes'].find(literal)
                if pos_1 > -1:
                    pos_2 = data_dict['attributes'].find(';', pos_1 + len(literal) + 1)
                    if pos_2 > -1:
                        protein_id = data_dict['attributes'][pos_1 + len(literal):pos_2]
                    else:
                        protein_id = data_dict['attributes'][pos_1 + len(literal):]
                else:
                    # CNCB-NGDC assemblies
                    literal = 'Protein_Accession='
                    pos_1 = data_dict['attributes'].find(literal)
                    if pos_1 > -1:
                        pos_2 = data_dict['attributes'].find(';', pos_1 + len(literal) + 1)
                        if pos_2 > -1:
                            protein_id = data_dict['attributes'][pos_1 + len(literal):pos_2]
                        else:
                            protein_id = data_dict['attributes'][pos_1 + len(literal):]

                # write the record of file with CDS sequences
                cds_file_id.write(f'>{cds_id} (seq_id:{data_dict['seq_id']}|start:{data_dict['start']}|end:{data_dict['end']}|strand:{data_dict['strand']}|phase:{data_dict['phase']})\n')
                cds_file_id.write(f'{genome_seq}\n')

                # when the CDS group identification has changed
                if cds_group_id != old_cds_group_id:

                    # if there are items in the CDS group identification
                    if len(cds_group_data_list) > 0:

                        # add 1 to the CDS counter
                        concatenated_cds_counter += 1

                        # order the start position of the CDS group data list depending on strand
                        sorted_cds_group_data_list = []
                        if old_cds_group_strand == '+':
                            sorted_cds_group_data_list = sorted(cds_group_data_list, key=lambda x: x[0], reverse=False)
                        else:
                            sorted_cds_group_data_list = sorted(cds_group_data_list, key=lambda x: x[0], reverse=True)

                        # build the CDS group sequence
                        cds_group_seq = ''
                        for cds_group_data in sorted_cds_group_data_list:
                            cds_group_seq += cds_group_data[2][cds_group_data[1]:]

                        # write the record of file with concatenated CDS sequences
                        concatenated_cds_file_id.write(f'>{old_cds_group_id} (gene_id:{old_gene_id}|protein_id:{old_protein_id})\n')
                        concatenated_cds_file_id.write(f'{cds_group_seq}\n')

                    # set previous cds group data
                    old_gene_id = gene_id
                    old_protein_id = protein_id
                    old_cds_group_id = cds_group_id
                    old_cds_group_strand = data_dict['strand']

                    # initialize cds group data list
                    cds_group_data_list = []

                # add CDS data to  the CDS group data list
                cds_group_data_list.append([data_dict['start'], int(data_dict['phase']), genome_seq])

        # print record counter
        xlib.Message.print('verbose', f'\rGFF file records: {record_counter:8d} - Genes: {gene_counter:8d} - CDS: {cds_counter:8d} - Concatenated CDS: {concatenated_cds_counter:8d}')

        # read the next record of input GFF file
        (record, _, data_dict) = xlib.read_gff_file(gff_file_id)

    # order the start position of the CDS group data list depending on strand
    sorted_cds_group_data_list = []
    if old_cds_group_strand == '+':
        sorted_cds_group_data_list = sorted(cds_group_data_list, key=lambda x: x[0], reverse=False)
    else:
        sorted_cds_group_data_list = sorted(cds_group_data_list, key=lambda x: x[0], reverse=True)

    # build the CDS group sequence
    cds_group_seq = ''
    for cds_group_data in sorted_cds_group_data_list:
        cds_group_seq += cds_group_data[2][cds_group_data[1]:]

    # write the record of file with concatenated CDS sequences
    concatenated_cds_file_id.write(f'>{old_cds_group_id} (gene_id:{old_gene_id}|protein_id:{old_protein_id})\n')
    concatenated_cds_file_id.write(f'{cds_group_seq}\n')

    xlib.Message.print('verbose', '\n')

    # close files
    gff_file_id.close()
    gene_file_id.close()
    cds_file_id.close()
    concatenated_cds_file_id.close()

    # print OK message
    xlib.Message.print('info', 'The files containing genome sequences are created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
