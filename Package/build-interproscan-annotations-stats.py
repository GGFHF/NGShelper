#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program builds statistics of an InterProScan analysis used by the
MMSEQ2-benchmarking software.

This software has been developed by:

    GI en Especies Leñosas (WooSp)
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

    # build the list of GO and pathways annotations associated to each sequence identifier
    build_interproscan_annotations(args.analysis_file, args.annotations_file, args.stats_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program builds statistics of an InterProScan analysis used by/n' \
         'the MMSEQ2-benchmarking software.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--analysis', dest='analysis_file', help='Path of the InterProScan analysis file (mandatory).')
    parser.add_argument('--annotations', dest='annotations_file', help='Path of output CSV file with annotations per sequence (mandatory).')
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

    # check "analysis_file"
    if args.analysis_file is None:
        xlib.Message.print('error', '*** The InterProScan analysis file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.analysis_file):
        xlib.Message.print('error', f'*** The file {args.analysis_file} does not exist.')
        OK = False

    # check "annotations_file"
    if args.annotations_file is None:
        xlib.Message.print('error', '*** The annotations file is not indicated in the input arguments.')
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

def build_interproscan_annotations(analysis_file, annotations_file, stats_file):
    '''
    Build the list of GO and pathways annotations associated to each sequence identifier
    in an InterProScan analysis.
    '''

    # set the cluster identification
    analysis_file_name = os.path.basename(analysis_file)
    start_pos = analysis_file_name.find('cluster')
    hyphen_pos = analysis_file_name.find('-')
    underscore_pos = analysis_file_name.find('_')
    if hyphen_pos > start_pos and underscore_pos > start_pos:
        end_pos = min(hyphen_pos, underscore_pos)
    elif hyphen_pos > start_pos and underscore_pos < start_pos:
        end_pos = hyphen_pos
    elif hyphen_pos < start_pos and underscore_pos > start_pos:
        end_pos = underscore_pos
    else:
        end_pos = -1
    cluster_id = analysis_file_name[start_pos:end_pos]

    # initialize the annotations dictionary
    annotations_dict = xlib.NestedDefaultDict()

    # initialize the consensus GO terms dictionary
    consensus_goterms_list = []

    # open the InterProScan analysis file
    if analysis_file.endswith('.gz'):
        try:
            analysis_file_id = gzip.open(analysis_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', analysis_file)
    else:
        try:
            analysis_file_id = open(analysis_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', analysis_file)

    # initialize the record counter
    record_counter = 0

    # read the first record
    record = analysis_file_id.readline()

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
        xlib.Message.print('verbose', f'\rInterProScan analysis file: {record_counter} processed records')

        # read the next record
        record = analysis_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close InterProScan analysis file
    analysis_file_id.close()

    # open the annotations file
    try:
        annotations_file_id = open(annotations_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', annotations_file)

    for key, value in annotations_dict.items():

        # get the cluster identification
        # -- cluster_id = key

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

        # write data in the annotations file
        annotations_file_id.write(f'{cluster_id};{"|".join(interpro_goterms_list)};{"|".join(panther_goterms_list)};{"|".join(x_goterms_list)};{"|".join(metacyc_pathways_list)};{"|".join(reactome_pathways_list)};{"|".join(x_pathways_list)}\n')

    # close annotations file
    annotations_file_id.close()

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
