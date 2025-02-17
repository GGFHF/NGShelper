#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program converts a file in tabular format to a VCF file.

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

    # convert the file in tabular format to VCF
    convert_tab_to_vcf (args.tab_file, args.vcf_file, args.md_characters)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program converts a file in tabular format to a VCF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--tab', dest='tab_file', help='Path of the input file in tabular format (mandatory).')
    parser.add_argument('--vcf', dest='vcf_file', help='Path of the output VCF file (mandatory).')
    parser.add_argument('--mdc', dest='md_characters', help='Characters representing missing data (mandatory).')
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

    # check "tab_file"
    if args.tab_file is None:
        xlib.Message.print('error', '*** The input file in tabular format is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.tab_file):
        xlib.Message.print('error', f'*** The file {args.tab_file} does not exist.')
        OK = False

    # check "vcf_file"
    if args.vcf_file is None:
        xlib.Message.print('error', '*** The output VCF file is not indicated in the input arguments.')
        OK = False

    # check "md_characters"
    if args.md_characters is None:
        xlib.Message.print('error', '*** Characters representing missing data are not indicated in the input arguments.')
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

def convert_tab_to_vcf (tab_file, vcf_file, md_characters):
    '''
    Convert a file in tabular format to a VCF file.
    '''

    # initialize the sample identification list and sample number
    sample_id_list = []
    sample_number = 0

    # initialize the genotype data dictionary
    genotype_dict = xlib.NestedDefaultDict()

    # initialize the record counter of the file in tabular format
    input_record_counter = 0

    # initialize the header record control
    header_record = True

    # open the file in tabular format
    if tab_file.endswith('.gz'):
        try:
            tab_file_id = gzip.open(tab_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', tab_file)
    else:
        try:
            tab_file_id = open(tab_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', tab_file)

    # read the first record
    record = tab_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        input_record_counter += 1

        # process the header record with the variant identifications
        if header_record:

            # extract header data
            # record format: ID/SNP	variant_id_1	variant_id_2	variant_id_3	...	variant_id_n
            data_list = []
            begin = 0
            for end in [i for i, chr in enumerate(record) if chr == '\t']:
                data_list.append(record[begin:end].strip())
                begin = end + 1
            data_list.append(record[begin:].strip('\n').strip())

            # set the variant id list
            variant_id_list = [x for x in data_list[1:] if x != '']

            # set False to header_record
            header_record = False

        # process data records with the genotypes of samples
        else:

            # extract data
            # record format: sample_id	genotype_1_variant_id_1	genotype_2_variant_id_1	genotype_1_variant_id_2	genotype_2_variant_id_2	genotype_1_variant_id_3	genotype_2_variant_id_3	...	genotype_1_variant_id_n	genotype_2_variant_id_n
            data_list = []
            begin = 0
            for end in [i for i, chr in enumerate(record) if chr == '\t']:
                data_list.append(record[begin:end].strip())
                begin = end + 1
            data_list.append(record[begin:].strip('\n').strip())

            # get the sample identification
            sample_id = data_list[0]

            # insert the sample identification into the sample identification list
            sample_id_list.append(sample_id)

            # check the variant number with the genotype number
            if (len(variant_id_list) * 2) != (len(data_list) - 1):
                raise xlib.ProgramException('', 'L022', sample_id)

            # insert genotype data into the genotype dictionary
            i = 0
            while i < (len(data_list[1:]) / 2):
                genotype = f'{data_list[i * 2 + 1]}{data_list[i * 2 + 2]}'
                genotype_dict[i][sample_number] = genotype
                i += 1
            # add 1 to sample number
            sample_number += 1

        # print counter
        xlib.Message.print('verbose', f'\rTabular file: {input_record_counter} records')

        # read the next record
        record = tab_file_id.readline()

    xlib.Message.print('verbose', '\n')
    xlib.Message.print('verbose', f'Sample number: {len(sample_id_list)}\n')
    xlib.Message.print('verbose', f'Variant number: {len(variant_id_list)}\n')

    # open the output VCF file
    if vcf_file.endswith('.gz'):
        try:
            vcf_file_id = gzip.open(vcf_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', vcf_file)
    else:
        try:
            vcf_file_id = open(vcf_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', vcf_file)

    # initialize the record counter of the VCF file
    output_record_counter = 0

    # write the column description record
    sample_id_list_text = '\t'.join(sample_id_list)
    record = f'#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{sample_id_list_text}\n'
    vcf_file_id.write(record)

    # add 1 to record counter
    output_record_counter += 1

    # print counter
    xlib.Message.print('verbose', f'\rVCF file: {output_record_counter} records')

    # process the variant records
    for i in range(len(variant_id_list)):    # pylint: disable=consider-using-enumerate

        # get the variant identification
        variant_id = variant_id_list[i]

        # set fixed columns
        ID = '.'
        QUAL = '.'
        FILTER = '.'
        INFO = '.'
        FORMAT = 'GT'

        # set the sequence identification and position
        sep_pos = variant_id.find('-')
        seq_id = variant_id[:sep_pos]
        position = variant_id[sep_pos + 1:]

        # set columns REF and ALT
        allele_set = set()
        allele_counter_dict = {}
        for j in range(len(sample_id_list)):
            genotype = genotype_dict[i][j]
            if genotype[0] != md_characters:
                allele_set.add(genotype[0])
            if genotype[1] != md_characters:
                allele_set.add(genotype[1])
            allele_counter_dict[genotype[0]] = allele_counter_dict.get(genotype[0], 0) + 1
            allele_counter_dict[genotype[1]] = allele_counter_dict.get(genotype[1], 0) + 1
        allele_list = list(allele_set)
        if len(allele_list) > 2:
            raise xlib.ProgramException('', 'L021', variant_id)
        elif len(allele_list) == 1:
            REF = allele_list[0]
            ALT = '.'
        elif allele_counter_dict[allele_list[0]] >= allele_counter_dict[allele_list[1]]:
            REF = allele_list[0]
            ALT = allele_list[1]
        else:
            REF = allele_list[1]
            ALT = allele_list[0]

        # set genotype column
        genotype_list = []
        for j in range(len(sample_id_list)):
            genotype = genotype_dict[i][j]
            if genotype[0] == md_characters and genotype[1] == md_characters:
                allele_1 = xlib.get_md_symbol()
                allele_2 = xlib.get_md_symbol()
            elif genotype[0] == md_characters and genotype[1] != md_characters:
                allele_1 = xlib.get_md_symbol()
                if genotype[1] == REF:
                    allele_2 = '0'
                else:
                    allele_2 = '1'
            elif genotype[0] != md_characters and genotype[1] == md_characters:
                if genotype[0] == REF:
                    allele_1 = '0'
                else:
                    allele_1 = '1'
                allele_2 = xlib.get_md_symbol()
            elif genotype[0] != md_characters and genotype[1] != md_characters:
                if genotype[0] == REF:
                    allele_1 = '0'
                else:
                    allele_1 = '1'
                if genotype[1] == REF:
                    allele_2 = '0'
                else:
                    allele_2 = '1'
            genotype_list.append(f'{allele_1}/{allele_2}')
        genotype_list_text = '\t'.join(genotype_list)

        # write the variant record
        record = f'{seq_id}\t{position}\t{ID}\t{REF}\t{ALT}\t{QUAL}\t{FILTER}\t{INFO}\t{FORMAT}\t{genotype_list_text}\n'
        vcf_file_id.write(record)

        # add 1 to record counter
        output_record_counter += 1

        # print counter
        xlib.Message.print('verbose', f'\rVCF file: {output_record_counter} records')

    xlib.Message.print('verbose', '\n')

    # close files
    tab_file_id.close()
    vcf_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
