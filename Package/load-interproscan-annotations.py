#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program loads the InterProScan annotations into the database a SQLite
database.

This software has been developed by:

    GI en especies leñosas (WooSp)
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
import re
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

    # load the InterProScan annotations into the database a SQLite database
    load_interproscan_annotations(conn, args.annotation_file, args.stats_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads InterProScan annotations into a SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--annotations', dest='annotation_file', help='Path of the InterProScan annotation file (mandatory).')
    parser.add_argument('--stats', dest='stats_file', help='Path of output CSV file with statistics or NONE; default: NONE.')
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

    # check "annotation_file"
    if args.annotation_file is None:
        xlib.Message.print('error', '*** The input InterProScan annotation file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.annotation_file):
        xlib.Message.print('error', f'*** The file {args.annotation_file} does not exist.')
        OK = False

    # check "stats_file"
    if args.stats_file is None or args.stats_file.upper() == 'NONE':
        args.stats_file = 'NONE'

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

def load_interproscan_annotations(conn, annotation_file, stats_file):
    '''
    Load the InterProScan annotations into the database a SQLite database.
    '''

    # initialize the annotations dictionary
    annotations_dict = xlib.NestedDefaultDict()

    # initialize the consensus GO terms dictionary
    consensus_goterms_list = []

    # open the InterProScan annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', annotation_file)
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', annotation_file)

    # initialize the record counter
    record_counter = 0

    # read the first record
    record = annotation_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # extract data
        # record format: protein_accession <field_sep> sequence_md5_digest <field_sep> sequence_length <field_sep> analysis <field_sep> signature_accession <field_sep> signature_description <field_sep> start_location <field_sep> stop_location <field_sep> score <field_sep> status <field_sep> date <field_sep> interpro_annotations_accession <field_sep> interpro_annotations_description <field_sep> go_annotations <field_sep> pathways_annotations <record_sep>
        field_sep = '\t'
        record_sep = '\n'
        data_list = re.split(field_sep, record.replace(record_sep,''))
        try:
            protein_accesion = data_list[0].strip()
            go_annotations_string = data_list[13].strip()
            pathways_annotations_string = data_list[14].strip()
        except Exception as e:
            go_annotations_string = '-'
            pathways_annotations_string = '-'

        # update the GO annotations lists of the sequence
        goterms_list = annotations_dict.get(protein_accesion, {}).get('goterms', [])
        if go_annotations_string != '-':
            goterms_set = set(goterms_list + go_annotations_string.split('|'))
            goterms_list = sorted(goterms_set)
        annotations_dict[protein_accesion]['goterms'] = goterms_list

        # update the pathway annotations of the sequence
        pathways_list = annotations_dict.get(protein_accesion, {}).get('pathways', [])
        if pathways_annotations_string != '-':
            pathways_set = set(pathways_list + pathways_annotations_string.split('|'))
            pathways_list = sorted(pathways_set)
        annotations_dict[protein_accesion]['pathways'] = pathways_list

        # print counters
        xlib.Message.print('verbose', f'\rInterProScan annotation file: {record_counter} processed records')

        # read the next record
        record = annotation_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close InterProScan annotation file
    annotation_file_id.close()

    # drop the table "interproscan_annotations" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "interproscan_annotations" ...\n')
    xsqlite.drop_interproscan_annotations(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create the table "interproscan_annotations"
    xlib.Message.print('verbose', 'Creating the table "interproscan_annotations" ...\n')
    xsqlite.create_interproscan_annotations(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the inserted row counter
    inserted_row_counter = 0

    # insert annotations in the database a SQLite database
    for key, value in annotations_dict.items():

        # get the cluster identification
        cluster_id = key

        # get the GO terms lists
        goterms_list = value['goterms']
        interpro_goterms_list = []
        panther_goterms_list = []
        x_goterms_list = []
        for goterm in goterms_list:
            if goterm.endswith('(InterPro)'):
                interpro_goterms_list.append(goterm[:10])
            elif goterm.endswith('(PANTHER)'):
                panther_goterms_list.append(goterm[:10])
            else:
                x_goterms_list.append(goterm)
        if not goterms_list:
            goterms_list = ['-']
        if not interpro_goterms_list:
            interpro_goterms_list = ['-']
        if not panther_goterms_list:
            panther_goterms_list = ['-']
        if not x_goterms_list:
            x_goterms_list = ['-']

        # get the pathways list
        pathways_list = value['pathways']
        metacyc_pathways_list = []
        reactome_pathways_list = []
        x_pathways_list = []
        for pathway in pathways_list:
            if pathway.startswith('MetaCyc'):
                metacyc_pathways_list.append(pathway)
            elif pathway.startswith('Reactome'):
                reactome_pathways_list.append(pathway)
            else:
                x_pathways_list.append(pathway)
        if not pathways_list:
            pathways_list = ['-']
        if not metacyc_pathways_list:
            metacyc_pathways_list = ['-']
        if not reactome_pathways_list:
            reactome_pathways_list = ['-']
        if not x_pathways_list:
            x_pathways_list = ['-']

        # save the sequence identification and annotations list corresponding to the consensus sequence
        if key.startswith('EMBOSS'):
            consensus_goterms_list = goterms_list

        # initialize the row data dictionary
        row_dict = {}

        # set row data
        row_dict['cluster_id'] = cluster_id
        row_dict['interpro_goterms'] = '|'.join(interpro_goterms_list)
        row_dict['panther_goterms'] = '|'.join(panther_goterms_list)
        row_dict['x_goterms'] = '|'.join(x_goterms_list)
        row_dict['metacyc_pathways'] = '|'.join(metacyc_pathways_list)
        row_dict['reactome_pathways'] = '|'.join(reactome_pathways_list)
        row_dict['x_pathways'] = '|'.join(x_pathways_list)

        # insert data into the table "interproscan_annotations"
        if row_dict['interpro_goterms'] != '-' or row_dict['panther_goterms'] != '-' or row_dict['x_goterms'] != '-' or row_dict['metacyc_pathways'] != '-' or row_dict['reactome_pathways'] != '-' or row_dict['x_pathways'] != '-':
            xsqlite.insert_interproscan_annotations_row(conn, row_dict)
            inserted_row_counter += 1

        # print counters
        xlib.Message.print('verbose', f'\rInterProScan annotation file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

    xlib.Message.print('verbose', '\n')

    # create the index "interproscan_annotations_index" on the table "interproscan_annotations"
    xlib.Message.print('verbose', 'Creating the index on the table "interproscan_annotations" ...\n')
    xsqlite.create_interproscan_annotations_index(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

    # close InterProScan annotation file
    annotation_file_id.close()

    # write statistics if necessary
    if stats_file != 'NONE':

        # open the statistics file
        try:
            stats_file_id = open(stats_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', stats_file)

        # write the statistics record
        if len(annotations_dict) == 0:
            pass
        elif len(annotations_dict) == 1:
            stats_file_id.write(f'{cluster_id};1;1;100.0\n')
        else:
            identical_goterms_number = 0
            for key, value in annotations_dict.items():
                goterms_list = value['goterms']
                if goterms_list == []:
                    goterms_list = ['-']
                if set(goterms_list) == set(consensus_goterms_list):
                    identical_goterms_number += 1
            stats_file_id.write(f'{cluster_id};{len(annotations_dict)};{identical_goterms_number};{identical_goterms_number/len(annotations_dict)*100}\n')

        # close statistics file
        stats_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
