#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program updates the missing data in a VCF file with the results of a
fastPHASE analysis.

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

    # updates the missing data in a VCF file with the results of a fastPHASE analysis
    update_vcf_with_fastphase_analysis(args.input_vcf_file, args.output_vcf_file, args.analysis_dir, args.prefix, args.tsi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program updates the missing data in a VCF file with the results of a fastPHASE analysis.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--invcf', dest='input_vcf_file', help='Path of the VCF file wih missing data (mandatory).')
    parser.add_argument('--outvcf', dest='output_vcf_file', help='Path of the output VCF file with imputed data (mandatory).')
    parser.add_argument('--analdir', dest='analysis_dir', help='Path of directoty where fastPHASE analysis files are saved (mandatory).')
    parser.add_argument('--prefix', dest='prefix', help='Prefix of fastPHASE analysis files (mandatory).')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')
    parser.add_argument('--tsi', dest='tsi_list', help='Sequence identification list to trace with format seq_id,seq_id_2,...,seq_id or NONE; default: NONE.')

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
        xlib.Message.print('error', '*** The VCF file wih missing data is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.input_vcf_file):
        xlib.Message.print('error', f'*** The file {args.input_vcf_file} does not exist.')
        OK = False

    # check "output_vcf_file"
    if args.output_vcf_file is None:
        xlib.Message.print('error', '*** The output VCF file with imputed data is not indicated in the input arguments.')
        OK = False

    # check "analysis_dir"
    if args.analysis_dir is None:
        xlib.Message.print('error', '*** The directory of fastPHASE analysis files is not indicated in the input arguments.')
        OK = False
    elif not os.path.isdir(args.analysis_dir):
        xlib.Message.print('error', '*** The directory of fastPHASE analysis files does not exist.')
        OK = False

    # check "prefix"
    if args.prefix is None:
        xlib.Message.print('error', '*** The prefix of fastPHASE analysis files is not indicated in the input arguments.')
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

    # check "tsi_list"
    if args.tsi_list is None or args.tsi_list == 'NONE':
        args.tsi_list = []
    else:
        args.tsi_list = xlib.split_literal_to_string_list(args.tsi_list)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def update_vcf_with_fastphase_analysis(input_vcf_file, output_vcf_file, analysis_dir, prefix, tsi_list):
    '''
    Updates the missing data in a VCF file with the results of a fastPHASE analysis.
    '''

    # initialize the sample number
    sample_number = 0

    # initialize the sample information list
    sample_info_list = []

    # open the VCF file with missing data
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

    # open the imputed VCF file
    if output_vcf_file.endswith('.gz'):
        try:
            output_vcf_file_id = gzip.open(output_vcf_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_vcf_file)
    else:
        try:
            output_vcf_file_id = open(output_vcf_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_vcf_file)

    # initialize counters
    seq_id_counter = 0
    variant_counter = 0
    record_counter = 0

    # read the first record of VCF file
    (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    # while there are records in the VCF file with missing data
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the VCF record counter
            record_counter += 1

            # write the metadata record
            output_vcf_file_id.write(record)

            # read the next record of the VCF file with missing data
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Seq ids ... {seq_id_counter:8d} - Variants ... {variant_counter:8d}')

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the VCF record counter
            record_counter += 1

            # get the record data list
            record_data_list = data_dict['record_data_list']

            # set the sample number and sample information list
            sample_number = len(record_data_list) - 9
            sample_info_list = record_data_list[9:]

            # write the column description record
            output_vcf_file_id.write(record)

            # read the next record of the VCF file with missing data
            (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Seq ids ... {seq_id_counter:8d} - Variants ... {variant_counter:8d}')

        # process variant records
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add 1 to the sequence identification counter
            seq_id_counter += 1

            # initialize variants per sequence counter
            variants_per_seq_counter = 0

            # save the sequence identification
            old_seq_id = data_dict['chrom']

            # get the genotypes per sample dictionary from imputated sequence by fastPHASE
            genotypes_per_sample_dict = get_genotypes_per_sample_dict(analysis_dir, prefix, old_seq_id)

            # process variant records of the same sequence identification
            while record != '' and not record.startswith('##') and not record.startswith('#CHROM') and data_dict['chrom'] == old_seq_id:

                # add 1 to the VCF record counter
                record_counter += 1

                # add 1 to the total variant counter
                variant_counter += 1

                # set the current sequence identification
                seq_id = data_dict['chrom']

                # set the variant identification
                variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'
                if seq_id in tsi_list: xlib.Message.print('trace', f'\n\n\nnvariant_id: {variant_id}')

                # get the reference bases (field REF) and alternative alleles (field ALT)
                reference_bases = data_dict['ref']
                alternative_alleles = data_dict['alt']
                if seq_id in tsi_list: xlib.Message.print('trace', f'reference_bases: {reference_bases}')
                if seq_id in tsi_list: xlib.Message.print('trace', f'alternative_alleles: {alternative_alleles}')

                # build the alternative allele list
                alternative_allele_list = alternative_alleles.split(',')
                if seq_id in tsi_list: xlib.Message.print('trace', f'alternative_allele_list: {alternative_allele_list}')

                # build the complete allele list
                complete_allele_list = [reference_bases] + alternative_allele_list
                if seq_id in tsi_list: xlib.Message.print('trace', f'complete_allele_list: {complete_allele_list}')

                # build the allele code list
                allele_code_list = ['A', 'T', 'C', 'G']
                for i in range(len(complete_allele_list)):
                    if len(complete_allele_list[i]) > 1 and complete_allele_list[i] != xlib.get_md_symbol():
                        allele_code_list.append(complete_allele_list[i].upper())
                if seq_id in tsi_list: xlib.Message.print('trace', f'allele_code_list: {allele_code_list}')

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
                if seq_id in tsi_list: xlib.Message.print('trace', f'sample_gt_list: {sample_gt_list}')

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
                if variant_id in tsi_list: xlib.Message.print('trace', f'sample_gt_list: {sample_gt_list}')

                # set imputation in missing data
                for i in range(sample_number):
                    if sample_gt_left_list[i] == xlib.get_md_symbol() or sample_gt_right_list[i] == xlib.get_md_symbol():
                        # get left
                        sample_id = sample_info_list[i]
                        impute_sample_gt_left_numeric = genotypes_per_sample_dict[sample_id]['first_genotype_list'][variants_per_seq_counter]
                        impute_sample_gt_left_text = allele_code_list[int(impute_sample_gt_left_numeric) - 1]
                        if impute_sample_gt_left_text == reference_bases:
                            impute_sample_gt_left = '0'
                        else:
                            try:
                                impute_sample_gt_left = str(alternative_allele_list.index(impute_sample_gt_left_text) + 1)
                            except:
                                impute_sample_gt_left = '*'
                        # get right
                        impute_sample_gt_right_numeric = genotypes_per_sample_dict[sample_id]['second_genotype_list'][variants_per_seq_counter]
                        impute_sample_gt_right_text = allele_code_list[int(impute_sample_gt_right_numeric) - 1]
                        if impute_sample_gt_right_text == reference_bases:
                            impute_sample_gt_right = '0'
                        else:
                            try:
                                impute_sample_gt_right = str(alternative_allele_list.index(impute_sample_gt_right_text) + 1)
                            except:
                                impute_sample_gt_right = '*'
                        # oder
                        impute_sample_gt_list = sorted([impute_sample_gt_left, impute_sample_gt_right])
                        # save imputation
                        sample_gt_left_list[i] = impute_sample_gt_list[0]
                        sample_gt_right_list[i] = impute_sample_gt_list[1]

                # rebuild the list of the field GT for every sample
                for i in range(sample_number):
                    sample_gt_list[i] = f'{sample_gt_left_list[i]}{sample_sep_list[i]}{sample_gt_right_list[i]}'

                # rebuild the sample genotype data list and their corresponding record data
                sample_list = []
                for i in range(sample_number):
                    sample_data_list[i][gt_position] = sample_gt_list[i]
                    sample_list.append(':'.join(sample_data_list[i]))
                if variant_id in tsi_list: xlib.Message.print('trace', f'(17) sample_gt_list: {sample_gt_list}')

                # get the sample list as text
                sample_list_text = '\t'.join(sample_list)

                # # save data in the variants per sequence dictionary
                # variants_per_seq_dict[variants_per_seq_counter] = {'chrom': data_dict['chrom'], 'pos': data_dict['pos'], 'id': data_dict['id'], 'ref': data_dict['ref'], 'alt': data_dict['alt'], 'qual': data_dict['qual'], 'filter': data_dict['filter'], 'info': data_dict['info'], 'format': data_dict['format'], 'sample_list_text': sample_list_text}

                # write the variant record
                sample_list_text = '\t'.join(sample_list)
                output_vcf_file_id.write(f'{data_dict["chrom"]}\t{data_dict["pos"]}\t{data_dict["id"]}\t{data_dict["ref"]}\t{data_dict["alt"]}\t{data_dict["qual"]}\t{data_dict["filter"]}\t{data_dict["info"]}\t{data_dict["format"]}\t{sample_list_text}\n')

                # add 1 to the variants per sequence counter
                variants_per_seq_counter += 1

                # read the next record of the VCF file with missing data
                (record, _, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

                # print the counters
                xlib.Message.print('verbose', f'\rProcessed VCF records ... {record_counter:8d} - Seq ids ... {seq_id_counter:8d} - Variants ... {variant_counter:8d}')

    xlib.Message.print('verbose', '\n')

    # close files
    input_vcf_file_id.close()
    output_vcf_file_id.close()

#-------------------------------------------------------------------------------

def get_genotypes_per_sample_dict(analysis_dir, prefix, seq_id):
    '''
    Get the genotypes per sample dictionary from imputated sequence by fastPHASE.
    '''

    # set the path of que fastPHASE analysis file
    fastphase_sequence_file = f'{analysis_dir}{os.sep}{prefix}-{seq_id}_hapguess_switch.out'

    # initialize the genotypes per sample dictionary
    genotypes_per_sample_dict = xlib.NestedDefaultDict()

    # open the fastPHASE sequence file
    if fastphase_sequence_file.endswith('.gz'):
        try:
            fastphase_sequence_file_id = gzip.open(fastphase_sequence_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', fastphase_sequence_file)
    else:
        try:
            fastphase_sequence_file_id = open(fastphase_sequence_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', fastphase_sequence_file)

    # read the first record of the fastPHASE sequence file
    record = fastphase_sequence_file_id.readline()

    # while there are records in the fastPHASE sequence file
    while record != '':

        while record != '' and not record.strip().startswith('#'):

            # read the next record of the fastPHASE sequence file
            record = fastphase_sequence_file_id.readline()

        while record != '' and record.strip().startswith('#'):

            sample_id = record.strip()[1:]

            # read the next record of the fastPHASE sequence file (first genotypes line)
            record = fastphase_sequence_file_id.readline()

            # get the first genotype list
            first_genotype_list = record.strip().split(' ')

            # read the next record of the PHASE fastPHASE sequence file (second genotypes line)
            record = fastphase_sequence_file_id.readline()

            # get the second genotypes list and join with the firts genotype list
            second_genotype_list = record.strip().split(' ')

            # add genotypes lists to the the genotypes per sample dictionary
            genotypes_per_sample_dict[sample_id] = {'first_genotype_list': first_genotype_list, 'second_genotype_list': second_genotype_list}

            # read the next record of the fastPHASE sequence file
            record = fastphase_sequence_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close the fastPHASE sequence file
    fastphase_sequence_file_id.close()

    # return the genotypes per sample dictionary
    return genotypes_per_sample_dict

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
