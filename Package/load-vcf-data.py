#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program loads data of a VCF file into SQLite database.

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

    # load data of a VCF file
    load_vcf_data(conn, args.vcf_file, args.sample_file, args.sp1_id, args.sp2_id, args.hybrid_id, args.imputed_md_id, args.new_md_id, args.allele_transformation, args.tvi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads data of a VCF file into SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--vcf', dest='vcf_file', help='Path of input VCF file (mandatory).')
    parser.add_argument('--samples', dest='sample_file', help='Path of the sample file in the following record format: "sample_id;species_id;mother_id" (mandatory).')
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species (mandatory).')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--new_mdi', dest='new_md_id', help=f'New identification of missing data which will replace "."; default: {xlib.Const.DEFAULT_NEW_MD_ID}.')
    parser.add_argument('--imd_id', dest='imputed_md_id', help=f'Identification of the alternative allele for imputed missing data; default {xlib.Const.DEFAULT_IMPUTED_MD_ID}')
    parser.add_argument('--trans', dest='allele_transformation', help=f'Transformation of the allele symbol: {xlib.get_allele_transformation_code_list_text()}; default: NONE.')
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

    # check "sqlite_database"
    if args.sqlite_database is None:
        xlib.Message.print('error', '*** The SQLite database is not indicated in the input arguments.')
        OK = False

    # check "vcf_file"
    if args.vcf_file is None:
        xlib.Message.print('error', '*** The VCF file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.vcf_file):
        xlib.Message.print('error', f'*** The file {args.vcf_file} does not exist.')
        OK = False

    # check "sample_file"
    if args.sample_file is None:
        xlib.Message.print('error', '*** The sample file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.sample_file):
        xlib.Message.print('error', f'*** The file {args.sample_file} does not exist.')
        OK = False

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

    # check "imputed_md_id"
    if args.imputed_md_id is None:
        args.imputed_md_id = xlib.Const.DEFAULT_IMPUTED_MD_ID

    # check "new_md_id"
    if args.new_md_id is None:
        args.new_md_id = xlib.Const.DEFAULT_NEW_MD_ID

    # check "allele_transformation"
    if args.allele_transformation is None:
        args.allele_transformation = 'NONE'
    elif not xlib.check_code(args.allele_transformation, xlib.get_allele_transformation_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** The allele transformation has to be {xlib.get_allele_transformation_code_list_text()}.')
        OK = False
    else:
        args.allele_transformation = args.allele_transformation.upper()

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

    # check the identification set
    if OK:
        if args.sp1_id.upper() == 'NONE' and args.hybrid_id.upper() == 'NONE':
            pass
        elif args.sp1_id == args.sp2_id or \
           args.hybrid_id.upper() != 'NONE' and (args.sp1_id == args.hybrid_id or args.sp2_id == args.hybrid_id):
            xlib.Message.print('error', 'The identifications must be different.')
            OK = False

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def load_vcf_data(conn, vcf_file, sample_file, sp1_id, sp2_id, hybrid_id, imputed_md_id, new_md_id, allele_transformation, tvi_list):
    '''
    Load data of a VCF file.
    '''

    # get the sample data
    sample_dict = xlib.get_sample_data(sample_file, sp1_id, sp2_id, hybrid_id)

    # drop table "vcf_samples" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "vcf_samples" ...\n')
    xsqlite.drop_vcf_samples(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create table "vcf_samples"
    xlib.Message.print('verbose', 'Creating the table "vcf_samples" ...\n')
    xsqlite.create_vcf_samples(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # insert samples data into table "vcf_samples"
    xlib.Message.print('verbose', 'Inserting sample data into the table "vcf_samples" ...\n')
    for key, value in sample_dict.items():
        value['type'] = 'N/A'
        xsqlite.insert_vcf_samples_row(conn, value)
    xlib.Message.print('verbose', 'Data are inserted.\n')

    # create index "vcf_samples_index" with columns "dataset_id" and "gene_id"  (if not exists)
    xlib.Message.print('verbose', 'Creating the index on the table "vcf_samples" (if it does not exist) ...\n')
    xsqlite.create_vcf_samples_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # get the sample type dictionary
    sample_type_dict = xsqlite.get_sample_type_dict(conn)

    # update the type of each sample
    for key in sample_type_dict.keys():
        xsqlite.update_vcf_samples_row(conn, sample_type_dict[key]['sample_id'], sample_type_dict[key]['type'])

    # drop table "vcf_variants" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "vcf_variants" ...\n')
    xsqlite.drop_vcf_variants(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create table "vcf_variants"
    xlib.Message.print('verbose', 'Creating the table "vcf_variants" ...\n')
    xsqlite.create_vcf_variants(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # drop table "vcf_alleles" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "vcf_alleles" ...\n')
    xsqlite.drop_vcf_alleles(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create table "vcf_alleles"
    xlib.Message.print('verbose', 'Creating the table "vcf_alleles" ...\n')
    xsqlite.create_vcf_alleles(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # drop table "vcf_samples_alleles" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "vcf_samples_alleles" ...\n')
    xsqlite.drop_vcf_samples_alleles(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create table "vcf_samples_alleles"
    xlib.Message.print('verbose', 'Creating the table "vcf_samples_alleles" ...\n')
    xsqlite.create_vcf_samples_alleles(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # drop table "vcf_samples_genotypes" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "vcf_samples_genotypes" ...\n')
    xsqlite.drop_vcf_samples_genotypes(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create table "vcf_samples_genotypes"
    xlib.Message.print('verbose', 'Creating the table "vcf_samples_genotypes" ...\n')
    xsqlite.create_vcf_samples_genotypes(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the row data dictionary corresponding to the tables "vcf_variants", "vcf_alleles", "vcf_samples_alleles" and "vcf_samples_genotypes"
    vcf_variants_row_dict = {}
    vcf_alleles_row_dict = {}
    vcf_samples_alleles_row_dict = {}
    vcf_samples_genotypes_row_dict = {}

    # build the list of imputed and missing data alleles
    M_I_list = [imputed_md_id, xlib.get_md_symbol()]

    # initialize the sample number
    sample_number = 0

    # initialize counters
    input_record_counter = 0
    total_variant_counter = 0
    vcf_variants_inserted_row_counter = 0
    vcf_alleles_inserted_row_counter = 0
    vcf_samples_alleles_inserted_row_counter = 0
    vcf_samples_genotypes_inserted_row_counter = 0

    # initialize the sample species and mother identification lists per variant
    sample_id_list = []
    species_id_list = []
    mother_id_list = []

    # open the input VCF file
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

    # read the first record of input VCF file
    (record, key, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

    # while there are records in input VCF file
    while record != '':

        # process metadata records
        while record != '' and record.startswith('##'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - vcf_variants ... {vcf_variants_inserted_row_counter:8d} - vcf_alleles ... {vcf_alleles_inserted_row_counter:8d} - vcf_samples_alleles ... {vcf_samples_alleles_inserted_row_counter:8d} - vcf_samples_genotypes ... {vcf_samples_genotypes_inserted_row_counter:8d}')

            # read the next record of the input VCF file
            (record, key, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

        # process the column description record
        if record.startswith('#CHROM'):

            # add 1 to the read sequence counter
            input_record_counter += 1

            # get the record data list
            record_data_list = data_dict['record_data_list']

            # build the sample species and mother identification lists per variant
            for i in range(9, len(record_data_list)):
                try:
                    sample_id = record_data_list[i]
                    species_id = sample_dict[record_data_list[i]]['species_id']
                    mother_id = sample_dict[record_data_list[i]]['mother_id']
                except Exception as e:
                    raise xlib.ProgramException(e, 'L002', record_data_list[i])
                sample_id_list.append(sample_id)
                species_id_list.append(species_id)
                mother_id_list.append(mother_id)

            # check if the sample species list is empty
            if not species_id_list:
                raise xlib.ProgramException('', 'L003')

            # set the sample number
            sample_number = len(species_id_list)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - vcf_variants ... {vcf_variants_inserted_row_counter:8d} - vcf_alleles ... {vcf_alleles_inserted_row_counter:8d} - vcf_samples_alleles ... {vcf_samples_alleles_inserted_row_counter:8d} - vcf_samples_genotypes ... {vcf_samples_genotypes_inserted_row_counter:8d}')

            # read the next record of the input VCF file
            (record, key, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

        # process variant record
        while record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

            # add set the variant identification
            variant_id = f'{data_dict["chrom"]}-{data_dict["pos"]}'

            # add 1 to the read sequence counter
            input_record_counter += 1

            # add 1 to the total variant counter
            total_variant_counter += 1

            if variant_id in tvi_list: xlib.Message.print('trace', f'\n\n\n\nseq_id: {data_dict["chrom"]} - position {data_dict["pos"]}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'total_variant_counter: {total_variant_counter}')

            # get the reference bases (field REF) and alternative alleles (field ALT)
            reference_bases = data_dict['ref']
            alternative_alleles = data_dict['alt']

            # build the alternative alleles list from field ALT
            alternative_allele_list = data_dict['alt'].split(',')

            # build the alleles list from reference bases and alternative alleles list
            if alternative_alleles == xlib.get_md_symbol():
                alleles_list = [reference_bases]
            else:
                alleles_list = [reference_bases] + alternative_allele_list

            # check if the variant is an indel (both SAMtools/BCFtools and Freebayes) or SNP or multiallelic or N/A
            variant_type = ''
            if alternative_alleles == xlib.get_md_symbol():
                variant_type = 'N/A'
            else:
                is_indel = False
                if len(reference_bases) > 1:
                    is_indel = True
                else:
                    for alternative_allele in alternative_allele_list:
                        if len(alternative_allele) > 1:
                            is_indel = True
                            break
                if is_indel:
                    variant_type = 'INDEL'
                elif len(alternative_allele_list) > 1:
                    variant_type = 'MULTIALLELIC'
                else:
                    variant_type = 'SNP'

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
            sample_gt_right_list = []
            for i in range(sample_number):
                sep = '/'
                sep_pos = sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    sep = '|'
                    sep_pos = sample_gt_list[i].find(sep)
                if sep_pos == -1:
                    raise xlib.ProgramException('', 'L008', 'GT', data_dict['chrom'], data_dict['pos'])
                sample_gt_left_list.append(sample_gt_list[i][:sep_pos])
                sample_gt_right_list.append(sample_gt_list[i][sep_pos+1:])

            if variant_id in tvi_list: xlib.Message.print('trace', f'reference_bases: {reference_bases}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'alternative_allele_list: {alternative_allele_list}')
            if variant_id in tvi_list: xlib.Message.print('trace', f'sample_gt_list: {sample_gt_list}')

            # set data and insert row into the table "vcf_variants"
            vcf_variants_row_dict['variant_id'] = variant_id
            vcf_variants_row_dict['seq_id'] = data_dict['chrom']
            vcf_variants_row_dict['position'] = data_dict['pos']
            vcf_variants_row_dict['reference_bases'] = reference_bases
            vcf_variants_row_dict['alternative_alleles'] = alternative_alleles
            vcf_variants_row_dict['variant_type'] = variant_type
            xsqlite.insert_vcf_variants_row(conn, vcf_variants_row_dict)
            vcf_variants_inserted_row_counter += 1

            # set data and insert rows into the table "vcf_alleles"
            vcf_alleles_row_dict['variant_id'] = variant_id
            # reference bases and alternative alleles
            for j in range(len(alleles_list)):
                vcf_alleles_row_dict['allele_id'] = str(j)
                vcf_alleles_row_dict['bases'] = alleles_list[j]
                if xlib.check_int(j) and allele_transformation == 'ADD100':
                    structure_allele_id = str(int(j) + 100)
                else:
                    structure_allele_id = j
                vcf_alleles_row_dict['structure_allele_id'] = structure_allele_id
                xsqlite.insert_vcf_alleles_row(conn, vcf_alleles_row_dict)
                vcf_alleles_inserted_row_counter += 1
            # missing data
            vcf_alleles_row_dict['allele_id'] = xlib.get_md_symbol()
            vcf_alleles_row_dict['bases'] = 'N/D'
            if xlib.check_int(new_md_id) and allele_transformation == 'ADD100':
                structure_allele_id = str(int(new_md_id) + 100)
            else:
                structure_allele_id = new_md_id
            vcf_alleles_row_dict['structure_allele_id'] = structure_allele_id
            xsqlite.insert_vcf_alleles_row(conn, vcf_alleles_row_dict)
            vcf_alleles_inserted_row_counter += 1
            # imputed missing data
            vcf_alleles_row_dict['allele_id'] = imputed_md_id
            vcf_alleles_row_dict['bases'] = 'N/D'
            if xlib.check_int(imputed_md_id) and allele_transformation == 'ADD100':
                structure_allele_id = str(int(imputed_md_id) + 100)
            else:
                structure_allele_id = imputed_md_id
            vcf_alleles_row_dict['structure_allele_id'] = structure_allele_id
            xsqlite.insert_vcf_alleles_row(conn, vcf_alleles_row_dict)
            vcf_alleles_inserted_row_counter += 1

            # set data and insert rows into the table "vcf_samples_alleles"
            vcf_samples_alleles_row_dict['variant_id'] = variant_id
            for i in range(sample_number):
                vcf_samples_alleles_row_dict['sample_id'] = sample_id_list[i]

                # initialize genotype distribution dictionary
                genotype_distribution_dict = {}
                for j in range(len(alleles_list)):
                    genotype_distribution_dict[alleles_list[j]] = 0
                for j in range(len(M_I_list)):
                    genotype_distribution_dict[M_I_list[j]] = 0

                # calculate genotype distribution dictionary
                if sample_gt_left_list[i] in M_I_list:
                    genotype_distribution_dict[sample_gt_left_list[i]] += 1
                else:
                    genotype_distribution_dict[alleles_list[int(sample_gt_left_list[i])]] += 1
                if sample_gt_right_list[i] in M_I_list:
                    genotype_distribution_dict[sample_gt_right_list[i]] += 1
                else:
                    genotype_distribution_dict[alleles_list[int(sample_gt_right_list[i])]] += 1

                # calculate precuency and insert rows for reference bases and alternative alleles
                for j in range(len(alleles_list)):
                    if genotype_distribution_dict[alleles_list[j]] > 0:
                        # -- vcf_samples_alleles_row_dict['allele_id'] = alleles_list[j]
                        vcf_samples_alleles_row_dict['allele_id'] = j
                        vcf_samples_alleles_row_dict['frecuency'] = genotype_distribution_dict[alleles_list[j]] / 2
                        xsqlite.insert_vcf_samples_alleles_row(conn, vcf_samples_alleles_row_dict)
                        vcf_samples_alleles_inserted_row_counter += 1

                # calculate precuency and insert rows for imputed missing data
                if genotype_distribution_dict[imputed_md_id] > 0:
                    vcf_samples_alleles_row_dict['allele_id'] = imputed_md_id
                    vcf_samples_alleles_row_dict['frecuency'] = genotype_distribution_dict[imputed_md_id] / 2
                    xsqlite.insert_vcf_samples_alleles_row(conn, vcf_samples_alleles_row_dict)
                    vcf_samples_alleles_inserted_row_counter += 1

                # calculate precuency and insert rows for missing data
                if genotype_distribution_dict[xlib.get_md_symbol()] > 0:
                    vcf_samples_alleles_row_dict['allele_id'] = xlib.get_md_symbol()
                    vcf_samples_alleles_row_dict['frecuency'] = genotype_distribution_dict[xlib.get_md_symbol()] / 2
                    xsqlite.insert_vcf_samples_alleles_row(conn, vcf_samples_alleles_row_dict)
                    vcf_samples_alleles_inserted_row_counter += 1

            # set data and insert rows into the table "vcf_samples_genotypes"
            vcf_samples_genotypes_row_dict['variant_id'] = variant_id
            for i in range(sample_number):
                vcf_samples_genotypes_row_dict['sample_id'] = sample_id_list[i]
                vcf_samples_genotypes_row_dict['gt_left'] = sample_gt_left_list[i]
                vcf_samples_genotypes_row_dict['gt_right'] = sample_gt_right_list[i]
                xsqlite.insert_vcf_samples_genotypes_row(conn, vcf_samples_genotypes_row_dict)
                vcf_samples_genotypes_inserted_row_counter += 1

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed records ... {input_record_counter:8d} - Total variants ... {total_variant_counter:8d} - vcf_variants ... {vcf_variants_inserted_row_counter:8d} - vcf_alleles ... {vcf_alleles_inserted_row_counter:8d} - vcf_samples_alleles ... {vcf_samples_alleles_inserted_row_counter:8d} - vcf_samples_genotypes ... {vcf_samples_genotypes_inserted_row_counter:8d}')

            # read the next record of the input VCF file
            (record, key, data_dict) = xlib.read_vcf_file(vcf_file_id, sample_number)

    xlib.Message.print('verbose', '\n')

    # create the index "vcf_variants_index" on the table "vcf_variants"
    xlib.Message.print('verbose', 'Creating the index on the table "vcf_variants" ...\n')
    xsqlite.create_vcf_variants_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # create the index "vcf_alleles_index" on the table "vcf_alleles"
    xlib.Message.print('verbose', 'Creating the index on the table "vcf_alleles" ...\n')
    xsqlite.create_vcf_alleles_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # create the index "vcf_samples_alleles_index" on the table "vcf_samples_alleles"
    xlib.Message.print('verbose', 'Creating the index on the table "vcf_samples_alleles" ...\n')
    xsqlite.create_vcf_samples_alleles_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # create the index "vcf_samples_genotypes_index" on the table "vcf_samples_genotypes"
    xlib.Message.print('verbose', 'Creating the index on the table "vcf_samples_genotypes" ...\n')
    xsqlite.create_vcf_samples_genotypes_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

    # close the VCF file
    vcf_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
