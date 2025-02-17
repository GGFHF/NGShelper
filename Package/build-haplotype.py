#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program builds the haplotype of a sample set from a VCF file.

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

    # build_haplotype
    build_haplotype(args.input_vcf_file, args.sample_file, args.imputed_md_id, args.sp1_id, args.sp2_id, args.hybrid_id, args.haplotype_file, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program builds the haplotype of a sample set from a VCF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--vcf', dest='input_vcf_file', help='Path of the VCF file (mandatory).')
    parser.add_argument('--samples', dest='sample_file', help='Path of the sample file in the following record format: "sample_id;species_id;mother_id" (mandatory).')
    parser.add_argument('--imd_id', dest='imputed_md_id', help=f'Identification of the alternative allele for imputed missing data; default {xlib.Const.DEFAULT_IMPUTED_MD_ID}')
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species (mandatory).')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--out', dest='haplotype_file', help='Path of the haplotype file (mandatory).')
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

    # check "sample_file"
    if args.sample_file is None:
        xlib.Message.print('error', '*** The sample file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.sample_file):
        xlib.Message.print('error', f'*** The file {args.sample_file} does not exist.')
        OK = False

    # check "imputed_md_id"
    if args.imputed_md_id is None:
        args.imputed_md_id = xlib.Const.DEFAULT_IMPUTED_MD_ID

    # check "sp1_id"
    if args.sp1_id is None:
        xlib.Message.print('error', '*** The identification of the first species is not indicated in the input arguments.')
        OK = False

    # check "sp2_id"
    if args.sp2_id is None:
        xlib.Message.print('error', '*** The identification of the second species is not indicated in the input arguments.')
        OK = False

    # check "hybrid_id"
    if args.hybrid_id is None:
        args.hybrid_id = 'NONE'

    # check "haplotype_file"
    if args.haplotype_file is None:
        xlib.Message.print('error', '*** The converted file is not indicated in the input arguments.')
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

def build_haplotype(input_vcf_file, sample_file, imputed_md_id, sp1_id, sp2_id, hybrid_id, haplotype_file, tvi_list):
    '''
    Builds the haplotype of a sample set from a VCF file.
    '''

    # initialize the sample number
    sample_number = 0

    # initialize counters
    input_record_counter = 0
    total_variant_counter = 0
    total_seq_counter = 0

    # initialize the sample information list
    sample_info_list = []

    # initialize the sequence code list
    seq_code_list = []

    # initialize the haplotype matrix (rows: sequences; columns: samples)
    haplotype_matrix = []

    # get the sample data
    sample_dict = xlib.get_sample_data(sample_file, sp1_id, sp2_id, hybrid_id)

    # open the VCF file
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

    # read the first record of the VCF file
    (record, key, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

    # while there are records in the VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Total seqs ... {total_seq_counter:8d}')

            # read the next record of the VCF file
            (record, key, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # get the record data list
            record_data_list = data_dict['record_data_list']

            # build the sample information list
            for i in range(9, len(record_data_list)):
                try:
                    species_id = sample_dict[record_data_list[i]]['species_id']
                except Exception as e:
                    raise xlib.ProgramException(e, 'L002', record_data_list[i])
                if species_id == sp1_id:
                    numeric_species_id = 1
                elif species_id == sp2_id:
                    numeric_species_id = 2
                else:
                    numeric_species_id = 3
                sample_info_list.append([record_data_list[i], numeric_species_id])

            # check if the sample information list is empty
            if not sample_info_list:
                raise xlib.ProgramException('', 'L003')

            # set the sample number
            sample_number = len(sample_info_list)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Total seqs ... {total_seq_counter:8d}')

            # read the next record of the VCF file
            (record, key, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

        # process variant records
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add set the variant identification
            variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'

            # add 1 to the total sequence counter
            total_seq_counter += 1

            # set the old key
            old_key = key

            # append sequence identification to the sequence code list
            seq_code_list.append(data_dict['chrom'])

            # initialize the sequence haplotype list
            seq_haplotype_list = []

            while record != '' and not record.startswith('##') and not record.startswith('#CHROM') and old_key == key:

                # add 1 to the read sequence counter
                input_record_counter += 1

                # add 1 to the total variant counter
                total_variant_counter += 1

                if variant_id in tvi_list: xlib.Message.print('trace', f'\n\n\n\nseq_id: {data_dict["chrom"]} - position {data_dict["pos"]}')

                # get the reference bases (field REF) and alternative alleles (field ALT)
                reference_bases = data_dict['ref']
                alternative_alleles = data_dict['alt']
                if variant_id in tvi_list: xlib.Message.print('trace', f'reference_bases: {reference_bases}')

                # build the alternative alleles list from field ALT
                alternative_allele_list = data_dict['alt'].split(',')
                if variant_id in tvi_list: xlib.Message.print('trace', f'alternative_allele_list: {alternative_allele_list}')

                # check if the variant is an indel (to SAMtools/BCFtools and Freebayes)
                is_indel = False
                if len(reference_bases) > 1:
                    is_indel = True
                else:
                    for alternative_allele in alternative_allele_list:
                        if len(alternative_allele) > 1:
                            is_indel = True
                            break
                if variant_id in tvi_list: xlib.Message.print('trace', f'INDEL?: {is_indel}')

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

                # build the sample nucleotide list of a variant
                sample_nuclotide_list = []
                for i in range(sample_number):

                    # if the variant is not an INDEL:
                    if not is_indel:
                        sep = '/'
                        sep_pos = sample_gt_list[i].find(sep)
                        if sep_pos == -1:
                            sep = '|'
                            sep_pos = sample_gt_list[i].find(sep)
                        if sep_pos == -1:
                            raise xlib.ProgramException('L008', 'GT', data_dict['chrom'], data_dict['pos'])
                        if sample_gt_list[i][:sep_pos] == xlib.get_md_symbol() or sample_gt_list[i][sep_pos+1:] == xlib.get_md_symbol():
                            nucleotide = 'N'
                        elif sample_gt_list[i][:sep_pos] == imputed_md_id or sample_gt_list[i][sep_pos+1:] == imputed_md_id:
                            nucleotide = 'U'
                        else:
                            try:
                                left_number = int(sample_gt_list[i][:sep_pos])
                                right_number = int(sample_gt_list[i][sep_pos+1:])
                                if left_number == 0:
                                    left_nucleotide = reference_bases
                                else:
                                    left_nucleotide = alternative_allele_list[left_number - 1]
                                if right_number == 0:
                                    right_nucleotide = reference_bases
                                else:
                                    right_nucleotide = alternative_allele_list[right_number - 1]
                                if left_nucleotide == right_nucleotide:
                                    nucleotide = right_nucleotide
                                else:
                                    nucleotide = xlib.get_nucleotide_list_symbol([left_nucleotide, right_nucleotide])
                                    if nucleotide == '':
                                        raise xlib.ProgramException('', 'D004', 'GT', data_dict['chrom'], data_dict['pos'])
                            except Exception as e:
                                raise xlib.ProgramException(e, 'L008', 'GT', data_dict['chrom'], data_dict['pos'])

                    # if the variant is an INDEL
                    else:
                        nucleotide = '_'

                    # append nucleotide to the sample nucleotide list of a variant
                    sample_nuclotide_list.append(nucleotide)

                # concat sample nucleotide list of a variant to sequence haplotype list
                if not seq_haplotype_list:
                    seq_haplotype_list = sample_nuclotide_list
                else:
                    for i in range(sample_number):
                        seq_haplotype_list[i] += f'-{sample_nuclotide_list[i]}'

                # print the counters
                xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - Total seqs ... {total_seq_counter:8d}')

                # read the next record of VCF file
                (record, key, data_dict) = xlib.read_vcf_file(input_vcf_file_id, sample_number)

            # append a row to haplotype matrix (rows: sequences; columns: samples)
            haplotype_matrix.append(seq_haplotype_list)


    xlib.Message.print('verbose', '\n')

    # close the VCF file
    input_vcf_file_id.close()

    # open the output haplotype file
    if haplotype_file.endswith('.gz'):
        try:
            haplotype_file_id = gzip.open(haplotype_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', haplotype_file)
    else:
        try:
            haplotype_file_id = open(haplotype_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', haplotype_file)

    ## write header record
    #header_record = f'sample_id;species_id;{";"'.join(seq_code_list)}\n'
    #haplotype_file_id.write(header_record)

    ## write sample records
    #for i in range(sample_number):

    #    # build the sample haplotype list corresponding to the sample i from the haplotype matrix (rows: sequences; columns: samples)
    #    sample_haplotype_list = []
    #    for j in range(total_seq_counter):
    #        sample_haplotype_list.append(haplotype_matrix[j][i])

    #    # write the record of the sample
    #    sample_record = f'{sample_info_list[i][0]};{sample_info_list[i][1]};{";"".join(sample_haplotype_list)}\n'
    #    haplotype_file_id.write(sample_record)

    # write FASTA sequences per sequence and sample
    for i in range(total_seq_counter):
        for j in range(sample_number):

            # write haplotype identification record
            haplotype_id_record = f'>{seq_code_list[i]}-{sample_info_list[j][0]}\n'
            haplotype_file_id.write(haplotype_id_record)

            #write haplotype sequence record
            haplotype_seq_record = f'{haplotype_matrix[i][j]}\n'
            haplotype_file_id.write(haplotype_seq_record)

    # close file
    haplotype_file_id.close()

    # print OK message
    xlib.Message.print('info', f'The converted file {os.path.basename(haplotype_file)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
