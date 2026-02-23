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
This program loads gene and protein sequences of a species using their FASTA and
GFF files into a SQLite database.

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

    # when the genome file is a path:
    if args.genome_fasta_file != 'NONE':

        # load the genome sequences into the SQLite database
        load_genome_seqs(conn, args.species_id, args.genome_fasta_file, args.gff_file)

    # when the genome file is a path:
    if args.protein_fasta_file != 'NONE':

        # load the protein sequences into the SQLite database
        load_protein_seqs(conn, args.species_id, args.protein_fasta_file, args.server)
        pass

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into the SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads gene and protein sequences of a species using their FASTA and GFF files\n' \
        'into a SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--server', dest='server', help=f'Server where the species FASTA and GFF file were downloaded: {xlib.get_bioinformatics_server_code_list_text()} (mandatory)')
    parser.add_argument('--species', dest='species_id', help='Species identification (mandatory)')
    parser.add_argument('--genome', dest='genome_fasta_file', help='Path of the genome FASTA file or NONE (mandatory)')
    parser.add_argument('--gff', dest='gff_file', help='Path of the GFF file corresponding to the genome file or NONE.')
    parser.add_argument('--proteins', dest='protein_fasta_file', help='Path of the protein FASTA file or NONE.')
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

    # check "sqlite_database"
    if args.sqlite_database is None:
        xlib.Message.print('error', '*** The database is not indicated in the input arguments.')
        OK = False

    # check "server"
    if not xlib.check_code(args.server, xlib.get_bioinformatics_server_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** Server has to be {xlib.get_bioinformatics_server_code_list_text()}.')
        OK = False
    else:
        args.server = args.server.upper()

    # check "genome_fasta_file"
    if args.genome_fasta_file.upper() == 'NONE':
        args.genome_fasta_file = 'NONE'
    elif args.genome_fasta_file is None:
        args.genome_fasta_file = 'NONE'
    elif not os.path.isfile(args.genome_fasta_file):
        xlib.Message.print('error', f'*** The file {args.genome_fasta_file} does not exist.')
        OK = False

    # check "gff_file"
    if args.gff_file.upper() == 'NONE':
        args.gff_file = 'NONE'
    elif args.gff_file is None:
        args.gff_file = 'NONE'
    elif not os.path.isfile(args.gff_file):
        xlib.Message.print('error', f'*** The file {args.gff_file} does not exist.')
        OK = False

    # check "protein_fasta_file"
    if args.protein_fasta_file.upper() == 'NONE':
        args.protein_fasta_file = 'NONE'
    elif args.protein_fasta_file is None:
        args.protein_fasta_file = 'NONE'
    elif not os.path.isfile(args.protein_fasta_file):
        xlib.Message.print('error', f'*** The file {args.protein_fasta_file} does not exist.')
        OK = False

    # check "genome_fasta_file" and "protein_fasta_file"
    if args.genome_fasta_file == 'NONE' and args.protein_fasta_file == 'NONE':
        xlib.Message.print('error', '*** The genome FASTA file and protein FASTA file can not both be NONE at the same time.')
        OK = False

    # check "genome_fasta_file" and gff_file"
    if args.genome_fasta_file == 'NONE' and args.gff_file != 'NONE' or args.genome_fasta_file != 'NONE' and args.gff_file == 'NONE':
        xlib.Message.print('error', '*** The genome FASTA file and its GFF file must be both a file path or be both NONE.')
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

def load_genome_seqs(conn, species_id, genome_fasta_file, gff_file):
    '''
    Load the genome sequences into the SQLite databaseusing the genome FASTA file
    and its GFF file.
    '''

    # check the table "species_gene_seqs"
    xlib.Message.print('verbose', 'Checking the table "species_gene_seqs" ...\n')
    species_gene_seqs_control = xsqlite.check_species_gene_seqs(conn)
    xlib.Message.print('verbose', f'Control: {species_gene_seqs_control}.\n')

    # when the table "species_gene_seqs" has rows
    if species_gene_seqs_control == 1:
        xlib.Message.print('verbose', f'Deleting rows from the table "species_gene_seqs" coresponding to {species_id} ...\n')
        xsqlite.delete_species_gene_seqs_rows(conn, species_id)
        xlib.Message.print('verbose', 'Rows are deleted.\n')

    # where there are not rows
    else:
        xlib.Message.print('verbose', 'Dropping the table "species_gene_seqs" ...\n')
        xsqlite.drop_species_gene_seqs(conn)
        xlib.Message.print('verbose', 'The table is dropped.\n')
        xlib.Message.print('verbose', 'Creating the table "species_gene_seqs" ...\n')
        xsqlite.create_species_gene_seqs(conn)
        xlib.Message.print('verbose', 'The table is created.\n')

    # get genome dictionary
    genome_dict = SeqIO.to_dict(SeqIO.parse(genome_fasta_file, 'fasta'))

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
    gene_counter = 0

    # read the first record of input GFF file
    (record, _, data_dict) = xlib.read_gff_file(gff_file_id)

    # while there are records in the input GFF file
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # process data records
        if not record.startswith('#') and record != '\n':

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
                # extract the genome sequence
                seq = xlib.get_genome_seq(genome_dict, data_dict['seq_id'], int(data_dict['start']), int(data_dict['end']), data_dict['strand'])

                # set the row dictionary
                row_dict = {'gene_id': gene_id, 'species_id': species_id, 'seq': seq}

                # insert gene data into the table "species_gene_seqs"
                xsqlite.insert_species_gene_seqs_row(conn, row_dict)

        # print record counter
        xlib.Message.print('verbose', f'\rGFF file records: {record_counter:8d} - Genes: {gene_counter:8d}')

        # read the next record of input GFF file
        (record, _, data_dict) = xlib.read_gff_file(gff_file_id)

    xlib.Message.print('verbose', '\n')

    # create the index "species_gene_seqs_index" on the table "species_gene_seqs" if it is new
    if species_gene_seqs_control == 0:
        xlib.Message.print('verbose', 'Creating the index on the table "species_gene_seqs" ...\n')
        xsqlite.create_species_gene_seqs_index(conn)
        xlib.Message.print('verbose', 'The index is created.\n')

    # close GFF file
    gff_file_id.close()

    # print OK message
    xlib.Message.print('info', 'The gene sequences are loaded into the SQLite database.')

#-------------------------------------------------------------------------------

def load_protein_seqs(conn, species_id, protein_fasta_file, server):
    '''
    Load the protein sequences into the SQLite database using the protein FASTA file.
    '''

    # check the table "species_protein_seqs"
    xlib.Message.print('verbose', 'Checking the table "species_protein_seqs" ...\n')
    species_protein_seqs_control = xsqlite.check_species_protein_seqs(conn)
    xlib.Message.print('verbose', f'Control: {species_protein_seqs_control}.\n')

    # when the table "species_protein_seqs" has rows
    if species_protein_seqs_control == 1:
        xlib.Message.print('verbose', f'Deleting rows from the table "species_protein_seqs" coresponding to {species_id} ...\n')
        xsqlite.delete_species_protein_seqs_rows(conn, species_id)
        xlib.Message.print('verbose', 'Rows are deleted.\n')

    # where there are not rows
    else:
        xlib.Message.print('verbose', 'Dropping the table "species_protein_seqs" ...\n')
        xsqlite.drop_species_protein_seqs(conn)
        xlib.Message.print('verbose', 'The table is dropped.\n')
        xlib.Message.print('verbose', 'Creating the table "species_protein_seqs" ...\n')
        xsqlite.create_species_protein_seqs(conn)
        xlib.Message.print('verbose', 'The table is created.\n')

    # set the cutting character in the identification of a FASTA sequence
    cutting_char = ''
    if server == xlib. get_ncbi_server_code():
        cutting_char = ' '
    elif server == xlib. get_cncb_ngdc_server_code():
        cutting_char = '\t'

    # open the FASTA sequence file
    if protein_fasta_file.endswith('.gz'):
        try:
            protein_fasta_file_id = gzip.open(protein_fasta_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', protein_fasta_file) from e
    else:
        try:
            protein_fasta_file_id = open(protein_fasta_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', protein_fasta_file) from e

    # initialize record counters
    fasta_seq_counter = 0

    # read the first record of FASTA sequnece file
    record = protein_fasta_file_id.readline()

    # while there are records in FASTA sequnece file
    while record != '':

        # process the head record
        if record.startswith('>'):

            # extract the identification
            blank_space_pos = record.find(cutting_char)
            protein_id = record[1:blank_space_pos].strip('\n')

            # initialize the sequence
            seq = ''

            # read the next record
            record = protein_fasta_file_id.readline()

        else:

            # control the FASTA format
            raise xlib.ProgramException('', 'F006', protein_fasta_file, 'FASTA')

        # while there are records and they are sequence
        while record != '' and not record.startswith('>'):

            # concatenate the record to the sequence
            seq += record.strip()

            # read the next record of FASTA sequnece file
            record = protein_fasta_file_id.readline()

        # add 1 to the read sequence counter
        fasta_seq_counter += 1

        # set the row dictionary
        row_dict = {'protein_id': protein_id, 'species_id': species_id, 'seq': seq}

        # insert protein data into the table "species_gene_seqs"
        xsqlite.insert_species_protein_seqs_row(conn, row_dict)

        # print the counters
        xlib.Message.print('verbose', f'\r{os.path.basename(protein_fasta_file)} processed seqs ... {fasta_seq_counter:8d}')

    xlib.Message.print('verbose', '\n')

    # create the index "species_protein_seqs_index" on the table "species_protein_seqs" if it is new
    if species_protein_seqs_control == 0:
        xlib.Message.print('verbose', 'Creating the index on the table "species_protein_seqs" ...\n')
        xsqlite.create_species_protein_seqs_index(conn)
        xlib.Message.print('verbose', 'The index is created.\n')

    # close protein FASTA file
    protein_fasta_file_id.close()

    # print OK message
    xlib.Message.print('info', 'The protein sequences are loaded into the SQLite database.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
