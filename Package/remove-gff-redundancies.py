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
This program removes redundancies (mRNAs with the same concatenated CDS sequence
and their corresponding features in a gene) in a GFF file.

WARNING: The features supported are: "region", "gene", "pseudogene", "mRNA", "exon",
"CDS", "five_prime_UTR", "three_prime_UTR", "lnc_RNA", "ncRNA", "snoRNA", "snRNA",
"tRNA", "rRNA", "transcript" and "cDNA_match".

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
import copy
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

    # remove redundancies (mRNAs with the same concatenated CDS sequence and their corresponding features in a gene) in a GFF file
    remove_gff_redundancies(conn, args.input_gff_file, args.output_gff_file, args.removed_redundancies_file, args.tgi_list)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program removes redundancies (mRNAs with the same concatenated CDS sequence\n' \
        'and their corresponding features in a gene) in a GFF file.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--input-gff', dest='input_gff_file', help='Path of the GFF file to remove redundancies (mandatory).')
    parser.add_argument('--output-gff', dest='output_gff_file', help='Path of the output GFF file without redundancies (mandatory).')
    parser.add_argument('--redundancies', dest='removed_redundancies_file', help='Path of the file with removed redundancies or NONE; default: NONE.')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {xlib.get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {xlib.get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')
    parser.add_argument('--tgi', dest='tgi_list', help='Gene identification list to trace with format gene_id_1,gene_id_2,...,gene_id_n or NONE; default: NONE.')

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

    # check "input_gff_file"
    if args.input_gff_file is None:
        xlib.Message.print('error', '*** The input GFF filethe GFF file to remove redundancies is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.input_gff_file):
        xlib.Message.print('error', f'*** The file {args.input_gff_file} does not exist.')
        OK = False

    # check "output_gff_file"
    if args.output_gff_file is None:
        xlib.Message.print('error', '*** The output GFF file without redundancies is not indicated in the input arguments.')
        OK = False

    # check "removed_redundancies_file"
    if args.removed_redundancies_file is None or args.removed_redundancies_file.upper() == 'NONE':
        args.removed_redundancies_file = 'NONE'

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

    # check "tgi_list"
    if args.tgi_list is None or args.tgi_list == 'NONE':
        args.tgi_list = []
    else:
        args.tgi_list = xlib.split_literal_to_text_list(args.tgi_list)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def remove_gff_redundancies(conn, input_gff_file, output_gff_file, removed_redundancies_file, tgi_list):
    '''
    Remove redundancies (mRNAs with the same concatenated CDS sequence and their
    corresponding features in a gene) in a GFF file.
    '''

    # initialize gene features list
    gene_features_list = []

    # open the input GFF file
    if input_gff_file.endswith('.gz'):
        try:
            input_gff_file_id = gzip.open(input_gff_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', input_gff_file)
    else:
        try:
            input_gff_file_id = open(input_gff_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', input_gff_file)

    # open the output GFF file
    if output_gff_file.endswith('.gz'):
        try:
            output_gff_file_id = gzip.open(output_gff_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_gff_file)
    else:
        try:
            output_gff_file_id = open(output_gff_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_gff_file)

    # write sequences without annotations if necessary
    if removed_redundancies_file != 'NONE':

        # open the file with sequences without annotations
        if removed_redundancies_file.endswith('.gz'):
            try:
                removed_redundancies_file_id = gzip.open(removed_redundancies_file, mode='wt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise xlib.ProgramException(e, 'F004', removed_redundancies_file)
        else:
            try:
                removed_redundancies_file_id = open(removed_redundancies_file, mode='w', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise xlib.ProgramException(e, 'F003', removed_redundancies_file)

    # initialize counters
    input_record_counter = 0
    output_record_counter = 0
    removed_redundancy_counter = 0

    # read the first record of input GFF file
    (record, _, data_dict) = xlib.read_gff_file(input_gff_file_id)

    # while there are records in the input GFF file
    while record != '':

        # process comment and "region" records
        while record != '' and (record.startswith('#') or record == '\n' or data_dict['seq_type'] == 'region'):

            # add 1 to input record counter
            input_record_counter += 1

            # add 1 to output record counter
            output_record_counter += 1

            # write the record in the output GFF file
            output_gff_file_id.write(record)

            # print record counter
            xlib.Message.print('verbose', f'\rInput GFF file records: {input_record_counter:8d} - Output GFF file records: {output_record_counter:8d} - Removed redundancies: {removed_redundancy_counter:8d}')

            # read the next record of input GFF file
            (record, _, data_dict) = xlib.read_gff_file(input_gff_file_id)

        # when the feature is "gene" or "pseudogene"
        while record != '' and not record.startswith('#') and record != '\n' and data_dict['seq_type'] in ['gene', 'pseudogene']:

            # add 1 to input record counter
            input_record_counter += 1

            # get "gene_id" data from "attributes"
            gene_id = xlib.get_na()
            literal = 'ID='
            pos_1 = data_dict['attributes'].find(literal)
            if pos_1 > -1:
                pos_2 = data_dict['attributes'].find(';', pos_1 + len(literal) + 1)
                gene_id = data_dict['attributes'][pos_1 + len(literal):pos_2]

            # add 1 to output record counter
            output_record_counter += 1

            # write the record in the output GFF file
            output_gff_file_id.write(record)

            # print record counter
            xlib.Message.print('verbose', f'\rInput GFF file records: {input_record_counter:8d} - Output GFF file records: {output_record_counter:8d} - Removed redundancies: {removed_redundancy_counter:8d}')

            # read the next record of input GFF file
            (record, _, data_dict) = xlib.read_gff_file(input_gff_file_id)

        # when the feature is "mRNA" or "exon" or "CDS" or "five_prime_UTR" or "three_prime_UTR" or "lnc_RNA"  or "ncRNA" or "snoRNA" or "snRNA" or "tRNA" or "rRNA" or "transcript" or "cDNA_match"
        while record != '' and not record.startswith('#') and record != '\n' and data_dict['seq_type'] in ['mRNA', 'exon', 'CDS', 'five_prime_UTR', 'three_prime_UTR', 'lnc_RNA', 'ncRNA', 'snoRNA', 'snRNA', 'tRNA', 'rRNA', 'transcript', 'cDNA_match']:

            # add 1 to input record counter
            input_record_counter += 1

            gene_features_list.append({'seq_id': data_dict['seq_id'], 'source': data_dict['source'], 'seq_type': data_dict['seq_type'], 'start': data_dict['start'], 'end': data_dict['end'], 'score': data_dict['score'], 'strand': data_dict['strand'], 'phase': data_dict['phase'], 'attributes': data_dict['attributes'], 'OK': True})

            # read the next record of input GFF file
            (record, _, data_dict) = xlib.read_gff_file(input_gff_file_id)

        # when the gene features list is not empty
        if gene_features_list:

            if gene_id in tgi_list:
                xlib.Message.print('trace', '\n')
                xlib.Message.print('trace', '************************************')
                xlib.Message.print('trace', f'gene_id: {gene_id}')
                xlib.Message.print('trace', '************************************')

            # detect redundancies in the gene features list
            reviewed_gene_features_list = detect_gene_redundancies(conn, gene_features_list, gene_id, tgi_list)

            if gene_id in tgi_list:
                xlib.Message.print('trace', 'reviewed_gene_features_list:')
                for feature_data in reviewed_gene_features_list:
                    xlib.Message.print('trace', f'    seq_id: {feature_data["seq_id"]} - seq_type: {feature_data["seq_type"]} - start: {feature_data["start"]} - end: {feature_data["end"]} - OK: {feature_data['OK']}')

            # write records corresponding to the gene features list
            for feature_data in reviewed_gene_features_list:

                # write the record in the output GFF file when OK is True
                if feature_data['OK']:

                    # add 1 to output record counter
                    output_record_counter += 1

                    # write the record
                    output_gff_file_id.write((f'{feature_data["seq_id"]}\t{feature_data["source"]}\t{feature_data["seq_type"]}\t{feature_data["start"]}\t{feature_data["end"]}\t{feature_data["score"]}\t{feature_data["strand"]}\t{feature_data["phase"]}\t{feature_data["attributes"]}\n'))

                # write the record in the removed redundancies file when OK is False
                else:

                    # add 1 to output record counter
                    removed_redundancy_counter += 1

                    # write the record
                    if  removed_redundancies_file != 'NONE':
                        removed_redundancies_file_id.write((f'{feature_data["seq_id"]}\t{feature_data["source"]}\t{feature_data["seq_type"]}\t{feature_data["start"]}\t{feature_data["end"]}\t{feature_data["score"]}\t{feature_data["strand"]}\t{feature_data["phase"]}\t{feature_data["attributes"]}\n'))

                # print record counter
                xlib.Message.print('verbose', f'\rInput GFF file records: {input_record_counter:8d} - Output GFF file records: {output_record_counter:8d} - Removed redundancies: {removed_redundancy_counter:8d}')

            # initialize the gene features list
            gene_features_list = []

            if gene_id in tgi_list: xlib.Message.print('trace', '\n')

    xlib.Message.print('verbose', '\n')

    # close files
    input_gff_file_id.close()
    output_gff_file_id.close()

    # print OK message
    xlib.Message.print('info', 'The GFF file without redundancies is created.')

#-------------------------------------------------------------------------------

def detect_gene_redundancies(conn, gene_features_list, gene_id, tgi_list):
    '''
    Detect redundancies of mRNAs with the same concatenated CDS sequence
    and their corresponding features in a gene.
    '''

    # intialize the list with gene features reviewed
    reviewed_gene_features_list = copy.deepcopy(gene_features_list)

    # intialize the mRNA data
    mrna_found = False
    cds_found = False
    mrna_data_list = []
    mrna_id = xlib.get_na()
    mrna_start_index = 0
    mrna_end_index = 0
    cds_group_id = xlib.get_na()
    cluster_id = xlib.get_na()
    cluster_id_counters_dict = {}

    # build the list with mNRA data
    for index, feature_data in enumerate(reviewed_gene_features_list):

        # when the feature is "mRNA"
        if feature_data['seq_type'] == 'mRNA':

            # if the previous features belong to a mRNA
            if mrna_found:

                # get the cluster identification corresponding to the
                cluster_id = xsqlite.get_mmseqs2_concatenated_cds_cluster_id_1(conn, cds_group_id)

                # append data corresponding to the previous mRNA
                mrna_data_list.append([mrna_id, mrna_start_index, mrna_end_index, cluster_id])

            # set indicator of mRNA found to True
            mrna_found = True

            # set the index when starts the features of the current mRNA
            mrna_start_index = index

            # set the index when ends the features of the current mRNA
            mrna_end_index = index

            # get "mrna_id" data from "attributes"
            mrna_id = xlib.get_na()
            literal = 'ID='
            pos_1 = feature_data['attributes'].find(literal)
            if pos_1 > -1:
                pos_2 = feature_data['attributes'].find(';', pos_1 + len(literal) + 1)
                mrna_id = feature_data['attributes'][pos_1 + len(literal):pos_2]

            # -- if gene_id in tgi_list: xlib.Message.print('trace', f'mrna_id: {mrna_id} - mrna_start_index: {mrna_start_index} - mrna_end_index: {mrna_end_index} - cds_group_id: {cds_group_id}' )

            # initialize the CDS group identification
            cds_group_id = xlib.get_na()

        # when a mRNA is processing and the feature is "exon"
        elif mrna_found and feature_data['seq_type'] == 'exon':

            # update the index when ends the features of the current mRNA
            mrna_end_index = index

            # -- if gene_id in tgi_list: xlib.Message.print('trace', f'mrna_id: {mrna_id} - mrna_start_index: {mrna_start_index} - mrna_end_index: {mrna_end_index} - cds_group_id: {cds_group_id}' )

        # when a mRNA is processing and the feature is "CDS"
        elif mrna_found and feature_data['seq_type'] == 'CDS':

            # set indicator of CDS found to True
            cds_found = True

            # update the index when ends the features of the current mRNA
            mrna_end_index = index

            # get "cds_id" data from "attributes"
            cds_id = xlib.get_na()
            literal = 'ID='
            pos_1 = feature_data['attributes'].find(literal)
            if pos_1 > -1:
                pos_2 = feature_data['attributes'].find(';', pos_1 + len(literal) + 1)
                cds_id = feature_data['attributes'][pos_1 + len(literal):pos_2]

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

            # -- if gene_id in tgi_list: xlib.Message.print('trace', f'mrna_id: {mrna_id} - mrna_start_index: {mrna_start_index} - mrna_end_index: {mrna_end_index} - cds_group_id: {cds_group_id}' )

        # when a mRNA is processing and the feature is "five_prime_UTR" or "three_prime_UTR"
        elif mrna_found and feature_data['seq_type'] in ['five_prime_UTR', 'three_prime_UTR']:

            # update the index when ends the features of the current mRNA
            mrna_end_index = index

            # -- if gene_id in tgi_list: xlib.Message.print('trace', f'mrna_id: {mrna_id} - mrna_start_index: {mrna_start_index} - mrna_end_index: {mrna_end_index} - cds_group_id: {cds_group_id}' )

        # when the feature is "lnc_RNA" or "ncRNA" or "snoRNA" or "snRNA" or "tRNA" or "rRNA" or "transcript" or "cDNA_match"
        elif feature_data['seq_type'] in ['lnc_RNA', 'ncRNA', 'snoRNA', 'snRNA', 'tRNA', 'rRNA', 'transcript', 'cDNA_match']:

            # if the previous features belong to a mRNA
            if mrna_found and cds_found:

                # get the cluster identification corresponding to the
                cluster_id = xsqlite.get_mmseqs2_concatenated_cds_cluster_id_1(conn, cds_group_id)

                # append data corresponding to the previous mRNA
                mrna_data_list.append([mrna_id, mrna_start_index, mrna_end_index, cluster_id])

            # set indicator of mRNA and CDS found to False
            mrna_found = False
            cds_found = False

    # append data of the last mRNA if necessary
    if mrna_found and cds_found:

        # get the cluster identification corresponding to the
        cluster_id = xsqlite.get_mmseqs2_concatenated_cds_cluster_id_1(conn, cds_group_id)

        # append data corresponding to the previous mRNA
        mrna_data_list.append([mrna_id, mrna_start_index, mrna_end_index, cluster_id])

    if gene_id in tgi_list:
        xlib.Message.print('trace', 'mrna_data_list:')
        for mrna_data in mrna_data_list:
            xlib.Message.print('trace', f'    {mrna_data}')

    # review mRNAs with repeated concatenated CDS clusters
    for index, mrna_data in enumerate(mrna_data_list):

        # get the counter of the CDS group identification and add 1
        cds_group_id_counter = cluster_id_counters_dict.get(mrna_data[3], 0)

        # get the counter of the CDS group identification and add 1
        cds_group_id_counter += 1

        # update the counter of the CDS group identification
        cluster_id_counters_dict[mrna_data[3]] = cds_group_id_counter

        # mark mRNAs with repeated concatenated CDS clusters and theirs features
        if cds_group_id_counter > 1:
            for i in range(mrna_data[1] ,mrna_data[2] +1):
                reviewed_gene_features_list[i]['OK'] = False

    if gene_id in tgi_list: xlib.Message.print('trace', f'cluster_id_counters_dict:\n    {cluster_id_counters_dict}')

    # return the list with gene features reviewed
    return reviewed_gene_features_list

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
