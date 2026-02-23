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
This program gets data from a GFF file yielded by Liftoff.

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

    # get data from a GFF file yielded by Liftoff
    get_liftoff_gff_data(args.reference_species_id, args.target_species_id, args.gff_file, args.gff_gene_data_file, args.gff_cds_data_file, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program gets data from a GFF file yielded by Liftoff.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--rspecies', dest='reference_species_id', help='Reference species identification (mandatory).')
    parser.add_argument('--tspecies', dest='target_species_id', help='Target species identification (mandatory).')
    parser.add_argument('--gff', dest='gff_file', help='Path of the GFF file yielded by Liftoff (mandatory).')
    parser.add_argument('--gene-file', dest='gff_gene_data_file', help='Path of the CSV file with Liftoff GFF gene data (mandatory).')
    parser.add_argument('--cds-file', dest='gff_cds_data_file', help='Path of the CSV file with Liftoff GFF CDS data (mandatory).')
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

    # check "reference_species_id"
    if args.reference_species_id is None:
        xlib.Message.print('error', '*** The reference species identification is not indicated in the input arguments.')
        OK = False

    # check "target_species_id"
    if args.reference_species_id is None:
        xlib.Message.print('error', '*** The target species identification is not indicated in the input arguments.')
        OK = False

    # check "gff_file"
    if args.gff_file is None:
        xlib.Message.print('error', '*** The input GFF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.gff_file):
        xlib.Message.print('error', f'*** The file {args.gff_file} does not exist.')
        OK = False

    # check "gff_gene_data_file"
    if args.gff_gene_data_file is None:
        xlib.Message.print('error', '*** The output CSV file with Liftoff GFF gene data is not indicated in the input arguments.')
        OK = False

    # check "gff_cds_data_file"
    if args.gff_cds_data_file is None:
        xlib.Message.print('error', '*** The output CSV file with Liftoff GFF CDS data is not indicated in the input arguments.')
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

def get_liftoff_gff_data(reference_species_id, target_species_id, gff_file, gff_gene_data_file, gff_cds_data_file, tvi_list):
    '''
    Get data from a GFF file yielded by Liftoff.
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

    # open the file with Liftoff GFF gene data
    if gff_gene_data_file.endswith('.gz'):
        try:
            gff_gene_data_file_id = gzip.open(gff_gene_data_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', gff_gene_data_file)
    else:
        try:
            gff_gene_data_file_id = open(gff_gene_data_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', gff_gene_data_file)

    # write the head of the file with Liftoff GFF gene data
    gff_gene_data_file_id.write('reference_species_id;target_species_id;reference_gene_id;target_seq_id;target_start;target_end;target_strand;reference_protein_id_list\n')

    # open the file with Liftoff GFF data
    if gff_cds_data_file.endswith('.gz'):
        try:
            gff_cds_data_file_id = gzip.open(gff_cds_data_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', gff_cds_data_file)
    else:
        try:
            gff_cds_data_file_id = open(gff_cds_data_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', gff_cds_data_file)

    # write the head of the file with Liftoff GFF data
    gff_cds_data_file_id.write('reference_species_id;target_species_id;reference_protein_id;target_seq_id;target_start;target_end;target_strand\n')

    # initialize data of the first output file record
    target_gene_seq_id = ''
    target_gene_start = 0
    target_gene_end = 0
    target_gene_strand = ''
    reference_gene_id = ''
    reference_protein_id_list = []

    # initialize control of the first gene
    is_first_gene = True

    # initialize counters
    record_counter = 0
    gene_ids_counter = 0

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

                # when the first gene is found:
                if is_first_gene:
                    is_first_gene = False

                # if there are data of a previous "gene"
                else:

                    # write the record of file with Liftoff GFF gene data
                    reference_protein_id_list_text = '|'.join(sorted(reference_protein_id_list))
                    gff_gene_data_file_id.write(f'{reference_species_id};{target_species_id};{reference_gene_id};{target_gene_seq_id};{target_gene_start};{target_gene_end};{target_gene_strand};{reference_protein_id_list_text}\n')

                # get "gene_id" data from "attributes"
                gene_id = xlib.get_na()
                literal = 'ID='
                pos_1 = data_dict['attributes'].find(literal)
                if pos_1 > -1:
                    pos_2 = data_dict['attributes'].find(';', pos_1 + len(literal) + 1)
                    gene_id = data_dict['attributes'][pos_1 + len(literal):pos_2]

                # set data
                target_gene_seq_id = data_dict['seq_id']
                target_gene_start = data_dict['start']
                target_gene_end = data_dict['end']
                target_gene_strand = data_dict['strand']
                reference_gene_id = gene_id
                reference_protein_id_list = []

                # add 1 to the gene identifications counter
                gene_ids_counter += 1

            # when the sequence type is "CDS"
            elif data_dict['seq_type'] == 'CDS':

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

                # add protein_id to reference_protein_id_list
                if protein_id != xlib.get_na() and protein_id not in reference_protein_id_list:
                    reference_protein_id_list.append(protein_id)

                # write the record of file with Liftoff GFF CDS data
                if protein_id != xlib.get_na():
                    gff_cds_data_file_id.write(f'{reference_species_id};{target_species_id};{protein_id};{data_dict['seq_id']};{data_dict['start']};{data_dict['end']};{data_dict['strand']}\n')

        # print record counter
        xlib.Message.print('verbose', f'\rGFF file records: {record_counter:8d} - Genes identifications: {gene_ids_counter:8d}')

        # read the next record of input GFF file
        (record, _, data_dict) = xlib.read_gff_file(gff_file_id)

    # if there are data of a previous "gene"
    if not is_first_gene:

        # write the record of file with Liftoff GFF gene data
        reference_protein_id_list_text = '|'.join(sorted(reference_protein_id_list))
        gff_gene_data_file_id.write(f'{reference_species_id};{target_species_id};{reference_gene_id};{target_gene_seq_id};{target_gene_start};{target_gene_end};{target_gene_strand};{reference_protein_id_list_text}\n')

    xlib.Message.print('verbose', '\n')

    # close files
    gff_file_id.close()
    gff_gene_data_file_id.close()

    # print OK message
    xlib.Message.print('info', 'The files containing GFF file data are created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
