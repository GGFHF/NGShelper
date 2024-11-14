#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program purges a VCF file.

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

    # if the operation is the change of a value in left and right sides of sample genotypes by a new value
    if args.purge_operation == 'CHAVAL':
        change_value(args.input_vcf_file, args.value, args.new_value, args.output_purged_file)

    # if the operation is the filter of variant containing a determined value in left or right sides of sample genotypes
    elif args.purge_operation == 'FILVAR':
        filter_variant(args.input_vcf_file, args.value, args.output_purged_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program purges a VCF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--vcf', dest='input_vcf_file', help='Path of input VCF file (mandatory).')
    parser.add_argument('--operation', dest='purge_operation', help=f'Purge operation (mandatory): {xlib.get_vcf_purge_code_list_text()}.')
    parser.add_argument('--value', dest='value', help='value to operate (mandatory)')
    parser.add_argument('--nvalue', dest='new_value', help='new value that replaces value when operation in CHAVAR (mandatory); else NONE (default)')
    parser.add_argument('--out', dest='output_purged_file', help='Path of the purged file (mandatory).')
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

    # check "input_vcf_file"
    if args.input_vcf_file is None:
        xlib.Message.print('error', '*** The VCF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.input_vcf_file):
        xlib.Message.print('error', f'*** The file {args.input_vcf_file} does not exist.')
        OK = False

    # check "purge_operation"
    is_ok_purge_operation = False
    if args.purge_operation is None:
        xlib.Message.print('error', '*** The purge operation is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.purge_operation, xlib.get_vcf_purge_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The purge operation has to be {xlib.get_vcf_purge_code_list_text()}.')
        OK = False
    else:
        args.purge_operation = args.purge_operation.upper()
        is_ok_purge_operation = True

    # check "value"
    if args.value is None:
        xlib.Message.print('error', '*** The value to perform the purge operation is not indicated the input arguments.')
        OK = False

    # check "new_value"
    if args.new_value is None and is_ok_purge_operation and args.purge_operation == 'CHAVAR':
        xlib.Message.print('error', '*** The new value to perform the purge operation is not indicated the input arguments.')
        OK = False
    elif args.new_value is None:
        args.new_value = ' NONE'

    # check "output_purged_file"
    if args.output_purged_file is None:
        xlib.Message.print('error', '*** The purged file is not indicated in the input arguments.')
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

def change_value(input_vcf_file, value, new_value, output_purged_file):
    '''
    Change a value in left and right sides of sample genotypes by a new value in a VCF file.
    '''

    # initialize the sample number
    sample_number = 0

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

    # open the output purged file
    if output_purged_file.endswith('.gz'):
        try:
            output_purged_file_id = gzip.open(output_purged_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_purged_file)
    else:
        try:
            output_purged_file_id = open(output_purged_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_purged_file)

    # initialize counters
    input_record_counter = 0
    total_variant_counter = 0
    changed_data = 0

    # read the first record of input VCF file
    (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    # while there are records in input VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # write the metadata record
            output_purged_file_id.write(record)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Changed data ... {changed_data:8d}')

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

            # write the column description record
            output_purged_file_id.write(record)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Changed data ... {changed_data:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process variant record
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # add 1 to the total variant counter
            total_variant_counter += 1

            # get the reference bases (field REF) and alternative alleles (field ALT)
            reference_bases = data_dict['ref']
            alternative_alleles = data_dict['alt']

            # build the alternative alleles list from field ALT
            alternative_allele_list = data_dict['alt'].split(',')

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
                sample_gt_left_list.append(sample_gt_list[i][:sep_pos])
                sample_gt_right_list.append(sample_gt_list[i][sep_pos+1:])

            # change the value in left and right sides of sample genotypes
            for i in range(sample_number):
                if sample_gt_left_list[i] == value:
                    sample_gt_left_list[i] = new_value
                    changed_data += 1
                if sample_gt_right_list[i] == value:
                    sample_gt_right_list[i] = new_value
                    changed_data += 1

            # rebuild the list of the field GT for every sample
            for i in range(sample_number):
                sample_gt_list[i] = f'{sample_gt_left_list[i]}{sample_sep_list[i]}{sample_gt_right_list[i]}'

            # rebuild the alternative alleles and its corresponding record data
            alternative_alleles = ','.join(alternative_allele_list)

            # rebuild the sample genotype data list and their corresponding record data
            sample_list = []
            for i in range(sample_number):
                sample_data_list[i][gt_position] = sample_gt_list[i]
                sample_list.append(':'.join(sample_data_list[i]))

            # write the variant record
            sample_list_text = '\t'.join(sample_list)
            output_purged_file_id.write(f'{data_dict["chrom"]}\t{data_dict["pos"]}\t{data_dict["id"]}\t{reference_bases}\t{alternative_alleles}\t{data_dict["qual"]}\t{data_dict["filter"]}\t{data_dict["info"]}\t{data_dict["format"]}\t{sample_list_text}\n')

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Changed data ... {changed_data:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    xlib.Message.print('verbose', '\n')

    # close files
    input_vcf_file_id.close()
    output_purged_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The purged file {os.path.basename(output_purged_file)} is created.')

#-------------------------------------------------------------------------------

def filter_variant(input_vcf_file, value, output_purged_file):
    '''
    Filter variants containing a determined value in left or right sides of sample genotypes in a VCF file.
    '''

    # initialize the sample number
    sample_number = 0

    # initialize the non-filtered sequence identification list
    non_filtered_seq_id_list = []

    # set the temporal VCF file
    temporal_vcf_file = f'{output_purged_file}.tmp'

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

    # open the temporal VCF file
    if temporal_vcf_file.endswith('.gz'):
        try:
            temporal_vcf_file_id = gzip.open(temporal_vcf_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', temporal_vcf_file)
    else:
        try:
            temporal_vcf_file_id = open(temporal_vcf_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', temporal_vcf_file)

    # initialize counters
    input_record_counter = 0
    total_variant_counter = 0
    filtered_variant_counter = 0

    # read the first record of input VCF file
    (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    # while there are records in input VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # write the metadata record
            temporal_vcf_file_id.write(record)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Filtered variants ... {filtered_variant_counter:8d}')

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

            # write the column description record
            temporal_vcf_file_id.write(record)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Filtered variants ... {filtered_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process variant record
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # add 1 to the total variant counter
            total_variant_counter += 1

            # get the reference bases (field REF) and alternative alleles (field ALT)
            reference_bases = data_dict['ref']
            alternative_alleles = data_dict['alt']

            # build the alternative alleles list from field ALT
            alternative_allele_list = data_dict['alt'].split(',')

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
                sample_gt_left_list.append(sample_gt_list[i][:sep_pos])
                sample_gt_right_list.append(sample_gt_list[i][sep_pos+1:])

            # initialize the control variable to write the variant
            write_the_variant = True

            # detect value in left or right sides of sample genotypes
            for i in range(sample_number):
                if sample_gt_left_list[i] == value or sample_gt_right_list[i] == value:
                    write_the_variant = False
                    break

            # if the process has to write the variant
            if write_the_variant:

                # rebuild the list of the field GT for every sample
                for i in range(sample_number):
                    sample_gt_list[i] = f'{sample_gt_left_list[i]}{sample_sep_list[i]}{sample_gt_right_list[i]}'

                # rebuild the alternative alleles and its corresponding record data
                alternative_alleles = ','.join(alternative_allele_list)

                # rebuild the sample genotype data list and their corresponding record data
                sample_list = []
                for i in range(sample_number):
                    sample_data_list[i][gt_position] = sample_gt_list[i]
                    sample_list.append(':'.join(sample_data_list[i]))

                # add the sequence identification to the non filtered sequence identification list
                if data_dict['chrom'] not in non_filtered_seq_id_list:
                    non_filtered_seq_id_list.append(data_dict['chrom'])

                # write the variant record
                sample_list_text = '\t'.join(sample_list)
                temporal_vcf_file_id.write(f'{data_dict["chrom"]}\t{data_dict["pos"]}\t{data_dict["id"]}\t{reference_bases}\t{alternative_alleles}\t{data_dict["qual"]}\t{data_dict["filter"]}\t{data_dict["info"]}\t{data_dict["format"]}\t{sample_list_text}\n')

            # if the process does not have to write the variant
            else:

                # add 1 to the filtered variant counter
                filtered_variant_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Filtered variants ... {filtered_variant_counter:8d}')

            # read the next record of the input VCF file
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    xlib.Message.print('verbose', '\n')

    # close files
    input_vcf_file_id.close()
    temporal_vcf_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The temporal file {os.path.basename(temporal_vcf_file)} containing the filtered variants is created.')
    xlib.Message.print('info', 'Removing metadata of filtered variants ...')

    # open the temporal VCF file
    if temporal_vcf_file.endswith('.gz'):
        try:
            temporal_vcf_file_id = gzip.open(temporal_vcf_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', temporal_vcf_file)
    else:
        try:
            temporal_vcf_file_id = open(temporal_vcf_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', temporal_vcf_file)

    # open the output purged file
    if output_purged_file.endswith('.gz'):
        try:
            output_purged_file_id = gzip.open(output_purged_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_purged_file)
    else:
        try:
            output_purged_file_id = open(output_purged_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_purged_file)

    # read the first record of temporal VCF file
    record = temporal_vcf_file_id.readline()

    # while there are records in temporal VCF file
    while record != '':

        # process contig records
        if record.startswith('##contig'):

            # get the sequence identification and the position
            seq_id = ''
            i1 = 13
            i2 = record.find(',', i1)
            if i2 > -1:
                seq_id = record[i1:i2]

            # write the record when the sequence identification was not filtered
            if seq_id in non_filtered_seq_id_list:
                output_purged_file_id.write(record)

        # process other records
        else:

            # write record
            output_purged_file_id.write(record)

        # read the next record
        record = temporal_vcf_file_id.readline()

    # close files
    temporal_vcf_file_id.close()
    output_purged_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The purged file {os.path.basename(output_purged_file)} is created.')

    # delete temporal VCF file
    os.remove(temporal_vcf_file)
    xlib.Message.print('info', f'The temporal VCF file {os.path.basename(temporal_vcf_file)} is deleted.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
