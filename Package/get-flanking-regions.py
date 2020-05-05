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
This program builds a FASTA file with the flanking genomic region of variants contained in a VCF file.
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

    # extract sequences
    get_flanking_regions(args.vcf_file, args.genome_file, args.flanking_region_file, args.nucleotide_number)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program builds a FASTA file with the flanking genomic region of variants contained in a VCF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='vcf_file', help='Path of the VCF file (mandatory).')
    parser.add_argument('--genome', dest='genome_file', help='Path of the FASTA genome file (mandatory)')
    parser.add_argument('--out', dest='flanking_region_file', help='Path of the output FASTA file with flanking regions (mandatory).')
    parser.add_argument('--nucleotides', dest='nucleotide_number', help=f'Nucleotide number to get in both sides of each variant; default: {xlib.Const.DEFAULT_NUCLEOTIDE_NUMBER}.')
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

    # check "vcf_file"
    if args.vcf_file is None:
        xlib.Message.print('error', '*** The input VCF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.vcf_file):
        xlib.Message.print('error', f'*** The file {args.vcf_file} does not exist.')
        OK = False

    # check "genome_file"
    if args.genome_file is None:
        xlib.Message.print('error', '*** The FASTA genome file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.genome_file):
        xlib.Message.print('error', f'*** The file {args.genome_file} does not exist.')
        OK = False

    # check "flanking_region_file"
    if args.flanking_region_file is None:
        xlib.Message.print('error', '*** The FASTA file with flanking regions is not indicated in the input arguments.')
        OK = False

    # check "nucleotide_number"
    if args.nucleotide_number is None:
        args.nucleotide_number = xlib.Const.DEFAULT_NUCLEOTIDE_NUMBER
    elif not xlib.check_int(args.nucleotide_number, minimum=1):
        xlib.Message.print('error', 'The minimum combined depth across samples has to be an integer number greater than  or equal to 1.')
        OK = False
    else:
        args.nucleotide_number = int(args.nucleotide_number)

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

def get_flanking_regions(vcf_file, genome_file, flanking_region_file, nucleotide_number):
    '''
    Build a FASTA file with the flanking genomic region of variants contained in a VCF file.
    '''

    # initialize the variant dictionary
    variant_dict = {}

    # open the VCF file
    if vcf_file.endswith('.gz'):
        try:
            vcf_file_id = gzip.open(vcf_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', vcf_file)
    else:
        try:
            vcf_file_id = open(vcf_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', vcf_file)

    # initialize counters
    vcf_record_counter = 0
    variant_counter = 0

    # read the first record of VCF file
    record = vcf_file_id.readline()

    # while there are records in VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the VCF file record counter
            vcf_record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rVCF file records ... {vcf_record_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record
            record = vcf_file_id.readline()

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the VCF file record counter
            vcf_record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rVCF file records ... {vcf_record_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record
            record = vcf_file_id.readline()

        # process variant record
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add 1 to the VCF file record counter
            vcf_record_counter += 1

            # add 1 to the variant counter
            variant_counter += 1

            # split the record data
            record_data_list = []
            start = 0
            for end in [i for i, chr in enumerate(record) if chr == '\t']:
                record_data_list.append(record[start:end].strip())
                start = end + 1
            record_data_list.append(record[start:].strip('\n').strip())

            # extract data from the record
            chrom = record_data_list[0]
            pos = record_data_list[1]
            ref = record_data_list[3]
            alt = record_data_list[4]

            # add variant data to the variant dictionary
            if variant_dict.get(chrom, {}) == {}:
                variant_dict[chrom] = {}
            try:
                variant_dict[chrom][int(pos)] = {'ref': ref, 'alt': alt}
            except Exception as e:
                raise xlib.ProgramException(e, 'L005', chrom, pos)

            # print the counters
            xlib.Message.print('verbose', f'\rVCF file records ... {vcf_record_counter:8d} - Variants ... {variant_counter:8d}')

            # read the next record
            record = vcf_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close files
    vcf_file_id.close()

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

    # open the flanking region file
    if flanking_region_file.endswith('.gz'):
        try:
            flanking_region_file_id = gzip.open(flanking_region_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', flanking_region_file)
    else:
        try:
            flanking_region_file_id = open(flanking_region_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', flanking_region_file)

    # initialize record counters
    genomic_seq_counter = 0
    flanking_region_seq_counter = 0
 
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
            raise xlib.ProgramException('', 'F006', genome_file, 'FASTA')

        # while there are records and they are sequence
        while record != '' and not record.startswith('>'):

            # concatenate the record to the sequence
            seq += record.strip()

            # read the next record of genome file
            record = genome_file_id.readline()

        # get the variant position dictionary corresponding to this genomic sequence
        position_dict = variant_dict.get(id, {})

        # if there are positions corresponding to this genomic sequence
        if position_dict != {}:

            # for each position
            for position in position_dict.keys():

                # get the limit of the variant flanking region sequence
                start = position - nucleotide_number if position - nucleotide_number >= 0 else 0
                end = position + nucleotide_number if position + nucleotide_number <= len(seq) else len(seq)

                # write the identification record
                flanking_region_file_id.write(f'>seq_id: {id} - start: {start} - end: {end} - position: {position} - ref: {variant_dict[id][position]["ref"]} alt: {variant_dict[id][position]["alt"]}\n')

                # wite the flanking region sequence
                flanking_region_file_id.write(f'{seq[start:end]}\n')

                # add 1 to the read sequence counter
                flanking_region_seq_counter += 1

        # print the counters
        xlib.Message.print('verbose', f'\rGenome seqs ... {genomic_seq_counter:8d} - Flanking region seqs ... {flanking_region_seq_counter:8d}')

    # close files
    genome_file_id.close()
    flanking_region_file_id.close()

    # print OK message 
    xlib.Message.print('verbose', f'\nThe file {os.path.basename(flanking_region_file)} containing the variant flanking regions is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
