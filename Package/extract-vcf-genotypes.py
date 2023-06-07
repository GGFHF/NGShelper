#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program extracts extracts genotype data of every variant from a VCF file.

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

    # extract genotype data of every variant from a VCF file
    extract_vcf_genotypes(args.input_vcf_file, args.imputed_md_id, args.output_genotype_file, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program extracts genotype data of every variant from a VCF file.\n' \
        'compatibility between each mother and its progeny, and imputes missing data of progeny genotypes\n' \
        'according to the selected imputation scenario.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='input_vcf_file', help='Path of input VCF file (mandatory).')
    parser.add_argument('--imd_id', dest='imputed_md_id', help=f'Identification of the alternative allele for imputed missing data; default {xlib.Const.DEFAULT_IMPUTED_MD_ID}')
    parser.add_argument('--out', dest='output_genotype_file', help='Path of genotype data file (mandatory).')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')
    parser.add_argument('--tvi', dest='tvi_list', help='Variant identification list to trace with format seq_id_1-pos_1,seq_id_2-pos_2,...,seq_id_n-pos_n or NONE; default: NONE.')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def check_args(args):
    '''
    Check the input arguments.
    '''

    # initialize the control variable
    OK = True

    # check "input_vcf_file"
    if args.input_vcf_file is None:
        xlib.Message.print('error', '*** The VCF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.input_vcf_file):
        xlib.Message.print('error', f'*** The file {args.input_vcf_file} does not exist.')
        OK = False

    # check "imputed_md_id"
    if args.imputed_md_id is None:
        args.imputed_md_id = xlib.Const.DEFAULT_IMPUTED_MD_ID

    # check "output_genotype_file"
    if args.output_genotype_file is None:
        xlib.Message.print('error', '*** The output genotype data file is not indicated in the input arguments.')
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

def extract_vcf_genotypes(input_vcf_file, imputed_md_id, output_genotype_file, tvi_list):
    '''
    Extract genotype data of every variant from a VCF file.
    '''

    # initialize the sample number
    sample_number = 0

    # initialize the maximum allele number
    maximum_allele_number = 0

    # open the input VCF file
    if input_vcf_file.endswith('.gz'):
        try:
            input_vcf_file_id = gzip.open(input_vcf_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', input_vcf_file)
    else:
        try:
            input_vcf_file_id = open(input_vcf_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', input_vcf_file)

    # set temporal genotype data file name
    if output_genotype_file.endswith('.gz'):
        tmp_genotype_file = f'{output_genotype_file[:-3]}.tmp.gz'
    else:
        tmp_genotype_file = f'{output_genotype_file}.tmp'

    # open the temporal genotype data file
    if tmp_genotype_file.endswith('.gz'):
        try:
            tmp_genotype_file_id = gzip.open(tmp_genotype_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', tmp_genotype_file)
    else:
        try:
            tmp_genotype_file_id = open(tmp_genotype_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', tmp_genotype_file)

    # write the header of the temporal genotype data file
    tmp_genotype_file_id.write('seq_id;position;ref;alt;genotype;counter\n')

    # initialize counters
    input_record_counter = 0
    total_variant_counter = 0

    # read the first record of input VCF file
    (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    # while there are records in input VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # get the record data list
            record_data_list = data_dict['record_data_list']

            # set the sample number
            sample_number = len(record_data_list) - 9

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process variant record
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add set the variant identification
            variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'
            if variant_id in tvi_list: xlib.Message.print('trace', f'\n\n\n\nseq_id: {data_dict["chrom"]} - position {data_dict["pos"]}')

            # add 1 to the read sequence counter
            input_record_counter += 1

            # add 1 to the total variant counter
            total_variant_counter += 1

            # get the reference bases (field REF) and alternative alleles (field ALT)
            reference_bases = data_dict['ref']
            alternative_alleles = data_dict['alt']
            if variant_id in tvi_list: xlib.Message.print('trace', f'reference_bases: {reference_bases} - alternative_alleles: {alternative_alleles}')

            # build the alternative alleles list from field ALT
            alternative_allele_list = data_dict['alt'].split(',')
            try:
                alternative_allele_list.remove(xlib.get_md_symbol())
            except:
                pass

            # set the maximum allele number
            if maximum_allele_number < 1 + len(alternative_allele_list):
                maximum_allele_number = 1 + len(alternative_allele_list)

            # get the position of the genotype (subfield GT) in the field FORMAT
            format_subfield_list = data_dict['format'].upper().split(':')
            try:
                gt_position = format_subfield_list.index('GT')
            except Exception as e:
                raise xlib.ProgramException(e, 'L007', 'GT', data_dict['chrom'], data_dict['pos'])

            # build the list of sample genotypes of a variant
            sample_data_list = []
            sample_gt_list = []
            for i in range(sample_number):
                sample_data_list.append(data_dict['sample_list'][i].split(':'))
                sample_gt_list.append(sample_data_list[i][gt_position])

            # build the lists of the left and right side of sample genotypes of a variant
            sample_gt_left_list = []
            sample_sep_list = []
            sample_gt_right_list = []
            for i in range(sample_number):
                sep = '/'
                sep_pos = sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    sep = '|'
                    sep_pos = sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    raise xlib.ProgramException('', 'L008', 'GT', data_dict['chrom'], data_dict['pos'])
                sample_sep_list.append(sep)
                if sample_gt_list[i][:sep_pos] == xlib.get_md_symbol():
                    sample_gt_left_list.append(xlib.get_md_symbol())
                elif sample_gt_list[i][:sep_pos] == imputed_md_id:
                    sample_gt_left_list.append(99)
                else:
                    sample_gt_left_list.append(int(sample_gt_list[i][:sep_pos]))
                if sample_gt_list[i][sep_pos+1:] == xlib.get_md_symbol():
                    sample_gt_right_list.append(xlib.get_md_symbol())
                elif sample_gt_list[i][sep_pos+1:] == imputed_md_id:
                    sample_gt_right_list.append(99)
                else:
                    sample_gt_right_list.append(int(sample_gt_list[i][sep_pos+1:]))

            # initialize genotype counter dictionary
            genotype_counter_dict = {}
            for j in range(1 + len(alternative_allele_list) + 1):
                for k in range(j, 1 + len(alternative_allele_list) + 1):
                    if j != (1 + len(alternative_allele_list)) and k != (1 + len(alternative_allele_list)):
                        genotype_counter_dict[f'{j}/{k}'] = 0
                    elif j != (1 + len(alternative_allele_list)) and k == (1 + len(alternative_allele_list)):
                        genotype_counter_dict[f'{j}/99'] = 0
                    elif j == (1 + len(alternative_allele_list)) and k != (1 + len(alternative_allele_list)):
                        genotype_counter_dict[f'99/{k}'] = 0
                    elif j == (1 + len(alternative_allele_list)) and k == (1 + len(alternative_allele_list)):
                        genotype_counter_dict['99/99'] = 0
            if variant_id in tvi_list: xlib.Message.print('trace', f'genotype_counter_dict: {genotype_counter_dict}')

            # initialize missing data counter
            md_counter = 0

            # count genotypes
            for i in range(sample_number):
                if sample_gt_left_list[i] == xlib.get_md_symbol() or sample_gt_right_list == xlib.get_md_symbol():
                    md_counter += 1
                else:
                    if sample_gt_left_list[i] <= sample_gt_right_list[i]:
                        j = sample_gt_left_list[i]
                        k = sample_gt_right_list[i]
                    else:
                        j = sample_gt_right_list[i]
                        k = sample_gt_left_list[i]
                    genotype_counter_dict[f'{j}/{k}'] = genotype_counter_dict[f'{j}/{k}'] + 1
            if variant_id in tvi_list: xlib.Message.print('trace', f'genotype_counter_dict: {genotype_counter_dict}')

            # write the variant gewnotype count records
            for key in genotype_counter_dict.keys():
                tmp_genotype_file_id.write(f'{data_dict["chrom"]};{data_dict["pos"]};{reference_bases};{alternative_alleles};{key};{genotype_counter_dict[key]}\n')
            tmp_genotype_file_id.write(f'{data_dict["chrom"]};{data_dict["pos"]};{reference_bases};{alternative_alleles};{xlib.get_md_symbol()};{md_counter}\n')

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    xlib.Message.print('verbose', '\n')

    # close files
    input_vcf_file_id.close()
    tmp_genotype_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The file {os.path.basename(tmp_genotype_file)} is created.')

    # open the temporal genotype data file
    if tmp_genotype_file.endswith('.gz'):
        try:
            tmp_genotype_file_id = gzip.open(tmp_genotype_file, mode='rt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', tmp_genotype_file)
    else:
        try:
            tmp_genotype_file_id = open(tmp_genotype_file, mode='r', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', tmp_genotype_file)

    # open the genotype data file
    if output_genotype_file.endswith('.gz'):
        try:
            output_genotype_file_id = gzip.open(output_genotype_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_genotype_file)
    else:
        try:
            output_genotype_file_id = open(output_genotype_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_genotype_file)

    # initialize record counters
    input_record_counter = 0

    # write the header of the genotype data file
    maximum_variant_list = []
    for j in range(maximum_allele_number + 1):
        for k in range(j, maximum_allele_number + 1):
            if j != (maximum_allele_number) and k != (maximum_allele_number):
                maximum_variant_list.append(f'{j}/{k}')
            elif j != (maximum_allele_number) and k == (maximum_allele_number):
                maximum_variant_list.append(f'{j}/99')
            elif j == (maximum_allele_number) and k != (maximum_allele_number):
                maximum_variant_list.append(f'99/{k}')
            elif j == (maximum_allele_number) and k == (maximum_allele_number):
                maximum_variant_list.append('99/99')
    maximum_variant_list.append('.')
    if variant_id in tvi_list: xlib.Message.print('trace', f'maximum_variant_list: {maximum_variant_list}')
    output_genotype_file_id.write('seq_id;position;ref;alt;{0}\n'.format(';'.join(maximum_variant_list)))

    # read the first record of the temporal genotype data file
    (record, _, data_dict) = read_temporal_genotype_data_file_record(tmp_genotype_file, tmp_genotype_file_id, input_record_counter)

    # set the first record control variable
    first_record = True

    # while there are records in the temporal genotype data file
    while record != '':

        # the header record
        if first_record:

            # set the first record control variable
            first_record = False

            # read the next record of the temporal genotype data file
            (record, _, data_dict) = read_temporal_genotype_data_file_record(tmp_genotype_file, tmp_genotype_file_id, input_record_counter)

        # data records
        else:

            # save old values
            old_seq_id = data_dict['seq_id']
            old_position = data_dict['position']
            old_ref = data_dict['ref']
            old_alt = data_dict['alt']

            # initialize genotype counter dictionary
            genotype_counter_dict = {}
            for j in range(maximum_allele_number + 1):
                for k in range(j, maximum_allele_number + 1):
                    if j != maximum_allele_number and k != maximum_allele_number:
                        genotype_counter_dict[f'{j}/{k}'] = 0
                    elif j != maximum_allele_number and k == maximum_allele_number:
                        genotype_counter_dict[f'{j}/99'] = 0
                    elif j == maximum_allele_number and k != maximum_allele_number:
                        genotype_counter_dict[f'99/{k}'] = 0
                    elif j == maximum_allele_number and k == maximum_allele_number:
                        genotype_counter_dict['99/99'] = 0
            genotype_counter_dict['.'] = 0
            if f'{old_seq_id}-{old_position}' in tvi_list: xlib.Message.print('trace', f'***genotype_counter_dict: {genotype_counter_dict}')

            # while there are records in the temporal genotype data file and the same variant
            while record != '' and data_dict['seq_id'] == old_seq_id and data_dict['position'] == old_position:

                # save the genotype counter in the genotype counter dictionary
                genotype_counter_dict[data_dict['genotype']] = data_dict['counter']

                # read the next record of the temporal genotype data file
                (record, _, data_dict) = read_temporal_genotype_data_file_record(tmp_genotype_file, tmp_genotype_file_id, input_record_counter)

            if f'{old_seq_id}-{old_position}' in tvi_list: xlib.Message.print('trace', f'***genotype_counter_dict: {genotype_counter_dict}')

            # write the variant gewnotype count records
            genotype_counter_list = []
            if sample_number - int(genotype_counter_dict['.']) > 0:
                for j in range(maximum_allele_number + 1):
                    for k in range(j, maximum_allele_number + 1):
                        if j != (maximum_allele_number) and k != (maximum_allele_number):
                            genotype_counter_list.append(str(int(genotype_counter_dict[f'{j}/{k}'])/(sample_number - int(genotype_counter_dict['.']))))
                        elif j != (maximum_allele_number) and k == (maximum_allele_number):
                            genotype_counter_list.append(str(int(genotype_counter_dict[f'{j}/99'])/(sample_number - int(genotype_counter_dict['.']))))
                        elif j == (maximum_allele_number) and k != (maximum_allele_number):
                            genotype_counter_list.append(str(int(genotype_counter_dict[f'99/{k}'])/(sample_number - int(genotype_counter_dict['.']))))
                        elif j == (maximum_allele_number) and k == (maximum_allele_number):
                            genotype_counter_list.append(str(int(genotype_counter_dict['99/99'])/(sample_number - int(genotype_counter_dict['.']))))
            genotype_counter_list.append(genotype_counter_dict['.'])
            genotype_counter_list_text = ';'.join(genotype_counter_list)
            output_genotype_file_id.write(f'{old_seq_id};{old_position};{old_ref};{old_alt};{genotype_counter_list_text}\n')

    # close files
    tmp_genotype_file_id.close()
    output_genotype_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The file {os.path.basename(output_genotype_file)} is created.')

#-------------------------------------------------------------------------------

def read_temporal_genotype_data_file_record(file_name, file_id, record_counter):
    '''
    x
    '''

    # initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read next record
    record = file_id.readline()

    # if there is record
    if record != '':

        # remove EOL
        record = record.strip('\n')

        # extract data
        # format: seq_id;position;ref;alt;genotype;counter
        data_list = []
        start = 0
        for end in [i for i, chr in enumerate(record) if chr == ';']:
            data_list.append(record[start:end])
            start = end + 1
        data_list.append(record[start:].strip('\n'))
        try:
            seq_id = data_list[0]
            position = data_list[1]
            ref = data_list[2]
            alt = data_list[3]
            genotype = data_list[4]
            counter = data_list[5]
        except Exception as e:
            raise xlib.ProgramException(e, 'F009', os.path.basename(file_name), record_counter)

        # get the record data dictionary
        data_dict = {'seq_id': seq_id, 'position': position, 'ref': ref, 'alt': alt, 'genotype': genotype, 'counter': counter}

    # if there is not record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
