#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program calculates the enrichment analysis of GO terms, Metacyc pathways, KEGG KOs and KEGG pathways
from a annotation file and the gymnoTOA database.

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

import numpy as np
import scipy.stats as stats

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

    # calculate the GO term enrichment analysis
    calculate_goterm_enrichment_analysis(conn, args.app, args.annotation_file, args.species_name, args.fdr_method, args.min_seqnum_annotations, args.min_seqnum_species, args.goea_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program calculates the enrichment analysis of GO terms in\n' \
                  'a (gymntoTOA, TOA, EnTAP or TRAPID) annotation file and the gymnoTOA database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--app', dest='app', help=f'Application (mandatory): {xlib.get_go_app_code_list_2_text()}.')
    parser.add_argument('--annotations', dest='annotation_file', help='Path of annotation file in CSV format (mandatory).')
    parser.add_argument('--species', dest='species_name', help=f'The species name or "{xlib.get_all_species_code()}" (mandatory).')
    parser.add_argument('--method', dest='fdr_method', help=f'Method used in FDR calcutation: {xlib.get_fdr_method_code_list_text()}; default: {xlib.Const.DEFAULT_FDR_METHOD}.')
    parser.add_argument('--msqannot', dest='min_seqnum_annotations', help=f'Minimum sequence number in annotation; default: {xlib.Const.DEFAULT_MIN_SEQNUM_ANNOTATIONS}.')
    parser.add_argument('--msqspec', dest='min_seqnum_species', help=f'Minimum sequence number in species; default: {xlib.Const.DEFAULT_MIN_SEQNUM_SPECIES}.')
    parser.add_argument('--goea', dest='goea_file', help='Path of the GO term enrichment analysis file (mandatory).')
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
        xlib.Message.print('error', '*** The SQLite database is not indicated in the input arguments.')
        OK = False
        OK = False

    # check "app"
    if args.app is None:
        xlib.Message.print('error', '*** The application is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_code(args.app, xlib.get_go_app_code_list_2(), case_sensitive=False):
        xlib.Message.print('error', f'*** The application has to be {xlib.get_go_app_code_list_2_text()}.')
        OK = False
    else:
        args.app = args.app.upper()

    # check "annotation_file"
    if args.annotation_file is None:
        xlib.Message.print('error', '*** The annotation file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.annotation_file):
        xlib.Message.print('error', f'*** The file {args.annotation_file} does not exist.')
        OK = False

    # check "species"
    if args.species_name is None:
        xlib.Message.print('error', '*** The species is not indicated in the input arguments.')
        OK = False

    # check "fdr_method"
    if args.fdr_method is None:
        args.fdr_method = xlib.Const.DEFAULT_FDR_METHOD
    elif not xlib.check_code(args.fdr_method, xlib.get_fdr_method_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** FDR method has to be {xlib.get_fdr_method_code_list_text()}.')
        OK = False
    else:
        args.fdr_method = args.fdr_method.lower()

    # check "min_seqnum_annotations"
    if args.min_seqnum_annotations is None:
        args.min_seqnum_annotations = xlib.Const.DEFAULT_MIN_SEQNUM_ANNOTATIONS
    elif not xlib.check_int(args.min_seqnum_annotations, minimum=1):
        xlib.Message.print('error', 'The minimum sequence number in annotations has to be an integer number greater than or equal to 1.')
        OK = False
    else:
        args.min_seqnum_annotations = int(args.min_seqnum_annotations)

    # check "min_seqnum_species"
    if args.min_seqnum_species is None:
        args.min_seqnum_species = xlib.Const.DEFAULT_MIN_SEQNUM_SPECIES
    elif not xlib.check_int(args.min_seqnum_species, minimum=1):
        xlib.Message.print('error', 'The minimum sequence number in species has to be an integer number greater than or equal to 1.')
        OK = False
    else:
        args.min_seqnum_species = int(args.min_seqnum_species)

    # check "goea_file"
    if args.goea_file is None:
        xlib.Message.print('error', '*** The GO term enrichment analysis file is not indicated in the input arguments.')
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

def calculate_goterm_enrichment_analysis(conn, app, annotation_file, species_name, fdr_method, min_seqnum_annotations, min_seqnum_species, goea_file):
    '''
    calculates the GO term enrichment analysis from a annotation file and the gymnoTOA database.
    '''

    # build the annotation GO term dictionary
    if app == 'GYMNOTOA':
        (annotation_goterm_dict, annotation_seqs_wgoterms) = build_gymnotoa_annotation_goterm_dict(annotation_file)
    elif app == 'TOA':
        (annotation_goterm_dict, annotation_seqs_wgoterms) = build_toa_annotation_goterm_dict(annotation_file)
    elif app == 'ENTAP-RUNN':
        (annotation_goterm_dict, annotation_seqs_wgoterms) = build_entap_run_annotation_goterm_dict(app, annotation_file)
    elif app == 'ENTAP-RUNP':
        (annotation_goterm_dict, annotation_seqs_wgoterms) = build_entap_run_annotation_goterm_dict(app, annotation_file)
    elif app == 'TRAPID':
        (annotation_goterm_dict, annotation_seqs_wgoterms) = build_trapid_annotation_goterm_dict(annotation_file)

    # get the list of GO term identifications involved in the study
    goterm_id_list = sorted(annotation_goterm_dict.keys())

    # build the species GOterm dictionary
    (species_goterm_dict, species_seqs_wgoterms) = build_species_goterm_dict(conn, species_name, goterm_id_list)

    # get the Gene Ontololy dictionary
    gene_ontology_dict = xsqlite.get_go_ontology_dict(conn, goterm_id_list)

    # initialize the calculations dictionary
    calcultations_dict = xlib.NestedDefaultDict()

    # perform calulations
    for goterm_id in goterm_id_list:

        # get the annotation data
        annotation_seqs_count = annotation_goterm_dict[goterm_id]
        calcultations_dict[goterm_id]['annotation_seqs_count'] = annotation_seqs_count

        # get the species data
        species_seqs_count =  species_goterm_dict.get(goterm_id, 0)
        calcultations_dict[goterm_id]['species_seqs_count'] = species_seqs_count

        # calculate the enrichment
        try:
            enrichment = (annotation_seqs_count / annotation_seqs_wgoterms) / (species_seqs_count / species_seqs_wgoterms)
        except ZeroDivisionError:
            enrichment = xlib.get_na()
        calcultations_dict[goterm_id]['enrichment'] = enrichment

        # calculate the p-value
        if enrichment != xlib.get_na():
            # -- _, pvalue = stats.fisher_exact([[annotation_seqs_count, annotation_seqs_wgoterms], [species_seqs_count, species_seqs_wgoterms]], alternative='two-sided')
            _, pvalue = stats.fisher_exact([[annotation_seqs_count, annotation_seqs_wgoterms], [species_seqs_count, species_seqs_wgoterms]], alternative='greater')
            # -- pvalue = stats.hypergeom.sf(annotation_seqs_count, species_seqs_wgoterms, species_seqs_count, annotation_seqs_wgoterms, loc=0)
            if np.isnan(pvalue):
                pvalue = xlib.get_na()
        else:
            pvalue = xlib.get_na()
        calcultations_dict[goterm_id]['pvalue'] = pvalue

        # initilize the FDR data to N/A
        calcultations_dict[goterm_id]['fdr'] = xlib.get_na()

    # get the GO term identification list sorted by the p-value
    temp_goterm_id_list = []    # each item is [GO term, p-value]
    for goterm_id in goterm_id_list:
        pvalue = calcultations_dict[goterm_id]['pvalue']
        if pvalue != xlib.get_na():
            temp_goterm_id_list.append([goterm_id, pvalue])
    pvalue_sorted_goterm_id_list = sorted(temp_goterm_id_list, key=lambda x: float(x[1]), reverse=False)

    # calculate FDR list corresponding to the p-value list
    fdr_list = stats.false_discovery_control(np.array([x[1] for x in pvalue_sorted_goterm_id_list]), axis=0,  method=fdr_method)

    # update FDR data in  the calculations dictionary
    for i, _ in enumerate(pvalue_sorted_goterm_id_list):
        calcultations_dict[pvalue_sorted_goterm_id_list[i][0]]['fdr'] = fdr_list[i]

    # get the GOterm identification list sorted by the FDR
    temp_goterm_id_list_1 = []    # each item is [GOterm, FDR]
    temp_goterm_id_list_2 = []
    for goterm_id in goterm_id_list:
        fdr = calcultations_dict[goterm_id]['fdr']
        if fdr == xlib.get_na():
            temp_goterm_id_list_2.append(goterm_id)
        else:
            temp_goterm_id_list_1.append([goterm_id, fdr])
    fdr_sorted_goterm_id_list_1 = sorted(temp_goterm_id_list_1, key=lambda x: float(x[1]), reverse=False)
    fdr_sorted_goterm_id_list = [x[0] for x in fdr_sorted_goterm_id_list_1] + temp_goterm_id_list_2

    # open the GO term enrichment analysis file
    if goea_file.endswith('.gz'):
        try:
            goea_file_id = gzip.open(goea_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception:
            raise xlib.ProgramException('F004', goea_file) from None
    else:
        try:
            goea_file_id = open(goea_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', goea_file)

    # write the header
    goea_file_id.write( '"GOterm";"Description";"Namespace";"Sequences# with this GOterm in annotations";"Sequences# with GOterms in annotations";"Sequences# with this GOterm in species";"Sequences# with GOtermss in species";"Enrichment";"p-value";"FDR"\n')

    # write data records
    for goterm_id in fdr_sorted_goterm_id_list:

        # get Gene Ontology data
        description = gene_ontology_dict[goterm_id]['go_name']
        namespace = gene_ontology_dict[goterm_id]['namespace']

        # get the annotation data
        annotation_seqs_count = calcultations_dict[goterm_id]['annotation_seqs_count']

        # get the species data
        species_seqs_count =  calcultations_dict[goterm_id]['species_seqs_count']

        # get the enrichment
        enrichment = calcultations_dict[goterm_id]['enrichment']

        # get the p-value
        pvalue = calcultations_dict[goterm_id]['pvalue']

        # get the FDR
        fdr = calcultations_dict[goterm_id]['fdr']

        # write record
        if annotation_seqs_count >= min_seqnum_annotations and species_seqs_count >= min_seqnum_species:
            goea_file_id.write(f'"{goterm_id}";"{description}";"{namespace}";{annotation_seqs_count};{annotation_seqs_wgoterms};{species_seqs_count};{species_seqs_wgoterms};{enrichment};{pvalue};{fdr}\n')

    # close the GO term enrichment analysis file
    goea_file_id.close()

    xlib.Message.print('verbose', '\n')
    xlib.Message.print('info', f'The file {goea_file} is created.')

#-------------------------------------------------------------------------------

def build_gymnotoa_annotation_goterm_dict(annotation_file):
    '''
    Build the annotation GO term dictionary from a gymnoTOA annotations file.
    '''

    # initialize annotation GO term dictionary
    annotation_goterm_dict = {}

    # initialize the counter of annotations sequences with GO terms
    annotation_seqs_wgoterms = 0

    # open the annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception:
            raise xlib.ProgramException('F002', annotation_file) from None
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception:
            raise xlib.ProgramException('F001', annotation_file) from None

    # initialize the annotation counter
    annotation_counter = 0

    # read the first record of the annotation file (header)
    (record, key, data_dict) = xlib.read_gymnotoa_annotation_record(annotation_file, annotation_file_id, annotation_counter)

    # read the secord record of the annotation file (first data record)
    (record, key, data_dict) = xlib.read_gymnotoa_annotation_record(annotation_file, annotation_file_id, annotation_counter)
    xlib.Message.print('trace', f'key: {key} - record: {record}')

    # while there are records
    while record != '':

        # set the old sequence identification
        old_qseqid = data_dict['qseqid']

        # initialize the minimum e-value and go identification list of the sequence hit/hsp with less e-value
        min_evalue = 9999
        min_evalue_goterm_id_list = []

        # initialize the list of GO term identifications corresponding to the sequence
        goterm_id_list = []

        # while there are records and the same sequence identification
        while record != '' and data_dict['qseqid'] == old_qseqid:

            # add 1 to the annotation counter
            annotation_counter += 1

            # extract the GO term identifications and add them into the GO term identification list
            # goterms format: "goterm_id1|goterm_id2|...|gotermo_idn"
            if data_dict['interpro_goterms'] != '' and data_dict['interpro_goterms'] != '-':
                interpro_goterm_id_list = data_dict['interpro_goterms'].split('|')
                goterm_id_list.extend(interpro_goterm_id_list)
            if data_dict['panther_goterms'] != '' and  data_dict['panther_goterms'] != '-':
                panther_goterm_id_list = data_dict['panther_goterms'].split('|')
                goterm_id_list.extend(panther_goterm_id_list)
            if data_dict['eggnog_goterms'] != '' and  data_dict['eggnog_goterms'] != '-':
                eggnog_goterm_id_list = data_dict['eggnog_goterms'].split('|')
                goterm_id_list.extend(eggnog_goterm_id_list)

            # save the GO identification list of the sequence hit/hsp with less e-value  (if GO data is not empty)
            if goterm_id_list and float(data_dict['evalue']) < min_evalue:
                min_evalue_goterm_id_list = goterm_id_list
                min_evalue = float(data_dict['evalue'])

            xlib.Message.print('verbose', f'\rProcessed annotations: {annotation_counter}')

            # read the next record of the annotation file
            (record, key, data_dict) = xlib.read_gymnotoa_annotation_record(annotation_file, annotation_file_id, annotation_counter)
            xlib.Message.print('trace', f'key: {key} - record: {record}')

        # get the list of GO term identifications without duplicates
        goterm_id_set = set(min_evalue_goterm_id_list)
        goterm_id_list = sorted(goterm_id_set)

        # increase the GO term identifications per sequence in the annotation GOterm dictionary
        if goterm_id_list != []:
            for goterm_id in goterm_id_list:
                counter = annotation_goterm_dict.get(goterm_id, 0)
                annotation_goterm_dict[goterm_id] = counter + 1

        # increase the counter of annotations sequences with GO terms
        if goterm_id_list != []:
            annotation_seqs_wgoterms += 1

    xlib.Message.print('verbose', '\n')

    # print summary
    xlib.Message.print('info', f'{annotation_counter} records read in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # return the annotation GO term dictionary
    return annotation_goterm_dict, annotation_seqs_wgoterms

#-------------------------------------------------------------------------------

def build_toa_annotation_goterm_dict(annotation_file):
    '''
    Build the annotation GO term dictionary from a TOA annotations file.
    '''

    # initialize annotation GO term dictionary
    annotation_goterm_dict = {}

    # initialize the counter of annotations sequences with GO terms
    annotation_seqs_wgoterms = 0

    # open the annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception:
            raise xlib.ProgramException('F002', annotation_file) from None
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception:
            raise xlib.ProgramException('F001', annotation_file) from None

    # initialize the annotation counter
    annotation_counter = 0

    # read the first record of the annotation file (header)
    (record, key, data_dict) = xlib.read_toa_annotation_record(annotation_file, annotation_file_id, 'MERGER', annotation_counter)

    # read the secord record of the annotation file (first data record)
    (record, key, data_dict) = xlib.read_toa_annotation_record(annotation_file, annotation_file_id, 'MERGER', annotation_counter)
    xlib.Message.print('trace', f'key: {key} - record: {record}')

    # while there are records
    while record != '':

        # initialize the old sequence identification
        old_nt_seq_id = data_dict['nt_seq_id']

        # initialize the minimum e-value and go identification list of the sequence hit/hsp with less e-value
        min_evalue = 9999
        min_evalue_go_id_list = []

        # while there are records and the same sequence identification
        while record != '' and data_dict['nt_seq_id'] == old_nt_seq_id:

            # add 1 to the annotation counter
            annotation_counter += 1

            # extract the GO term identifications and add them into the GO identification list
            # go_id format: "GO:id1*id2*...*idn"
            if data_dict['go_id'] != '':
                go_id_list = data_dict['go_id'][3:].split('*')
            else:
                go_id_list = []

            # review format of GO term identifications
            for i, go_id in enumerate(go_id_list):
                if not go_id.startswith('GO:'):
                    go_id_list[i] = f'GO:{go_id}'

            # save the GO identification list of the sequence hit/hsp with less e-value  (if GO data is not empty)
            if float(data_dict['hsp_evalue']) < min_evalue and go_id_list:
                min_evalue_go_id_list = go_id_list
                min_evalue = float(data_dict['hsp_evalue'])

            xlib.Message.print('verbose', f'\rProcessed annotations: {annotation_counter}')

            # read the next record of the annotation file
            (record, key, data_dict) = xlib.read_toa_annotation_record(annotation_file, annotation_file_id, 'MERGER', annotation_counter)
            xlib.Message.print('trace', f'key: {key} - record: {record}')

        # get the list of GO term identifications without duplicates
        goterm_id_set = set(min_evalue_go_id_list)
        goterm_id_list = sorted(goterm_id_set)

        # increase the GO term identifications per sequence in the annotation GOterm dictionary
        if goterm_id_list != []:
            for goterm_id in goterm_id_list:
                counter = annotation_goterm_dict.get(goterm_id, 0)
                annotation_goterm_dict[goterm_id] = counter + 1

        # increase the counter of annotations sequences with GO terms
        if goterm_id_list != []:
            annotation_seqs_wgoterms += 1

    xlib.Message.print('verbose', '\n')

    # print summary
    xlib.Message.print('info', f'{annotation_counter} records read in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # return the annotation GO term dictionary
    return annotation_goterm_dict, annotation_seqs_wgoterms

#-------------------------------------------------------------------------------

def build_entap_run_annotation_goterm_dict(app, annotation_file):
    '''
    Build the annotation GO term dictionary from a EnTAP annotations file.
    '''

    # initialize annotation GO term dictionary
    annotation_goterm_dict = {}

    # initialize the counter of annotations sequences with GO terms
    annotation_seqs_wgoterms = 0

    # open the annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception:
            raise xlib.ProgramException('F002', annotation_file) from None
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception:
            raise xlib.ProgramException('F001', annotation_file) from None

    # initialize the annotation counter
    annotation_counter = 0

    # read the first record of the annotation file (header)
    if app == 'ENTAP-RUNN':
        (record, key, data_dict) = xlib.read_entap_runn_annotation_record(annotation_file, annotation_file_id, annotation_counter)
    elif app == 'ENTAP-RUNP':
        (record, key, data_dict) = xlib.read_entap_runp_annotation_record(annotation_file, annotation_file_id, annotation_counter)

    # read the secord record of the annotation file (first data record)
    if app == 'ENTAP-RUNN':
        (record, key, data_dict) = xlib.read_entap_runn_annotation_record(annotation_file, annotation_file_id, annotation_counter)
    elif app == 'ENTAP-RUNP':
        (record, key, data_dict) = xlib.read_entap_runp_annotation_record(annotation_file, annotation_file_id, annotation_counter)
    xlib.Message.print('trace', f'key: {key} - record: {record}')

    # while there are records
    while record != '':

        # initialize the list of GO term identifications corresponding to the sequence
        goterm_id_list = []

        # add 1 to the annotation counter
        annotation_counter += 1

        # extract the GO term identifications and add them into the GO term identification list
        # goterms format: "goterm_id1,goterm_id2,...,gotermo_idn,"

        if data_dict['eggnog_go_biological'] != '' and data_dict['eggnog_go_biological'] != '-' and data_dict['eggnog_go_biological'] != 'NA':
            eggnog_go_biological_list = data_dict['eggnog_go_biological'].split(',')
            if '' in eggnog_go_biological_list:
                eggnog_go_biological_list.remove('')
            goterm_id_list.extend(eggnog_go_biological_list)
        if data_dict['eggnog_go_cellular'] != '' and  data_dict['eggnog_go_cellular'] != '-' and data_dict['eggnog_go_cellular'] != 'NA':
            eggnog_go_cellular_list = data_dict['eggnog_go_cellular'].split(',')
            if '' in eggnog_go_cellular_list:
                eggnog_go_cellular_list.remove('')
            goterm_id_list.extend(eggnog_go_cellular_list)
        if data_dict['eggnog_go_molecular'] != '' and  data_dict['eggnog_go_molecular'] != '-' and data_dict['eggnog_go_molecular'] != 'NA':
            eggnog_go_molecular_list = data_dict['eggnog_go_molecular'].split(',')
            if '' in eggnog_go_molecular_list:
                eggnog_go_molecular_list.remove('')
            goterm_id_list.extend(eggnog_go_molecular_list)

        # get the list of GO term identifications without duplicates
        goterm_id_set = set(goterm_id_list)
        goterm_id_list = sorted(goterm_id_set)

        # increase the GO term identifications per sequence in the annotation GOterm dictionary
        if goterm_id_list != []:
            for goterm_id in goterm_id_list:
                if not goterm_id.startswith('GO:'):
                    print(f"seq_id: {data_dict['query_sequence']} - goterm_id: {goterm_id}")
                counter = annotation_goterm_dict.get(goterm_id, 0)
                annotation_goterm_dict[goterm_id] = counter + 1

        # increase the counter of annotations sequences with GO terms
        if goterm_id_list != []:
            annotation_seqs_wgoterms += 1

        xlib.Message.print('verbose', f'\rProcessed annotations: {annotation_counter}')

        # read the next record of the annotation file
        if app == 'ENTAP-RUNN':
            (record, key, data_dict) = xlib.read_entap_runn_annotation_record(annotation_file, annotation_file_id, annotation_counter)
        elif app == 'ENTAP-RUNP':
            (record, key, data_dict) = xlib.read_entap_runp_annotation_record(annotation_file, annotation_file_id, annotation_counter)
        xlib.Message.print('trace', f'key: {key} - record: {record}')

    xlib.Message.print('verbose', '\n')

    # print summary
    xlib.Message.print('info', f'{annotation_counter} records read in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # return the annotation GO term dictionary
    return annotation_goterm_dict, annotation_seqs_wgoterms

#-------------------------------------------------------------------------------

def build_trapid_annotation_goterm_dict(annotation_file):
    '''
    Build the annotation GO term dictionary from a TRAPID annotations file.
    '''

    # initialize annotation GO term dictionary
    annotation_goterm_dict = {}

    # initialize the counter of annotations sequences with GO terms
    annotation_seqs_wgoterms = 0

    # open the annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception:
            raise xlib.ProgramException('F002', annotation_file) from None
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception:
            raise xlib.ProgramException('F001', annotation_file) from None

    # initialize the annotation counter
    annotation_counter = 0

    # read the first record of the annotation file (header)
    (record, key, data_dict) = xlib.read_trapid_annotation_record(annotation_file, annotation_file_id, annotation_counter)

    # read the secord record of the annotation file (first data record)
    (record, key, data_dict) = xlib.read_trapid_annotation_record(annotation_file, annotation_file_id, annotation_counter)
    xlib.Message.print('trace', f'key: {key} - record: {record}')

    # while there are records
    while record != '':

        # set the old sequence identification
        old_transcript_id = data_dict['transcript_id']

        # initialize the list of GO term identifications corresponding to the sequence
        goterm_id_list = []

        # while there are records and the same sequence identification
        while record != '' and data_dict['transcript_id'] == old_transcript_id:

            # add 1 to the annotation counter
            annotation_counter += 1

            # extract the GO term identification and add it into the GO term identification list
            go = data_dict['go']
            goterm_id_list.append(go)

            xlib.Message.print('verbose', f'\rProcessed annotations: {annotation_counter}')

            # read the next record of the annotation file
            (record, key, data_dict) = xlib.read_trapid_annotation_record(annotation_file, annotation_file_id, annotation_counter)
            xlib.Message.print('trace', f'key: {key} - record: {record}')

        # get the list of GO term identifications without duplicates
        goterm_id_set = set(goterm_id_list)
        goterm_id_list = sorted(goterm_id_set)

        # increase the GO term identifications per sequence in the annotation GOterm dictionary
        if goterm_id_list != []:
            for goterm_id in goterm_id_list:
                counter = annotation_goterm_dict.get(goterm_id, 0)
                annotation_goterm_dict[goterm_id] = counter + 1

        # increase the counter of annotations sequences with GO terms
        if goterm_id_list != []:
            annotation_seqs_wgoterms += 1

    xlib.Message.print('verbose', '\n')

    # print summary
    xlib.Message.print('info', f'{annotation_counter} records read in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # return the annotation GO term dictionary
    return annotation_goterm_dict, annotation_seqs_wgoterms

#-------------------------------------------------------------------------------

def build_species_goterm_dict(conn, species_name, goterm_id_list):
    '''
    Build the species GO term dictionary from the annotations file.
    '''

    # initialize the species GO term dictionary
    species_goterm_dict = {}

    # initialize the counter of species sequences with GO terms
    species_seqs_wgoterms = 0

    # get the dictionary of the GO terms of each cluster corresponding to the species
    goterms_per_cluster_dict = xsqlite.get_goterms_per_cluster_dict(conn, species_name)

    # initialize the species cluster counter
    species_cluster_counter = 0

    for _, data_dict in goterms_per_cluster_dict.items():

        # add 1 to  the species cluster counter
        species_cluster_counter += 1

        # initialize the list of GO term identifications corresponding to the sequence
        goterm_id_list = []

        # extract the GO term identifications and add them into the GO term identification list
        # goterms format: "goterm_id1,goterm_id2,...,goterm_idn"
        if data_dict['interpro_goterms'] != '' and data_dict['interpro_goterms'] != '-':
            interpro_goterm_list = data_dict['interpro_goterms'].split('|')
            goterm_id_list.extend(interpro_goterm_list)
        if data_dict['panther_goterms'] != '' and  data_dict['panther_goterms'] != '-':
            panther_goterm_list = data_dict['panther_goterms'].split('|')
            goterm_id_list.extend(panther_goterm_list)
        if data_dict['eggnog_goterms'] != '' and  data_dict['eggnog_goterms'] != '-':
            eggnog_goterm_list = data_dict['eggnog_goterms'].split('|')
            goterm_id_list.extend(eggnog_goterm_list)

        # get the list of GO term identifications without duplicates
        goterm_id_set = set(goterm_id_list)
        goterm_id_list = sorted(goterm_id_set)

        # increase the GO term identifications per sequence in the species GOterm dictionary
        if goterm_id_list != []:
            for goterm_id in goterm_id_list:
                counter = species_goterm_dict.get(goterm_id, 0)
                species_goterm_dict[goterm_id] = counter + 1

        # increase the counter of speciess sequences with GO terms
        if goterm_id_list != []:
            species_seqs_wgoterms += 1

        xlib.Message.print('verbose', f'\rProcessed {species_name} clusters: {species_cluster_counter}')

    xlib.Message.print('verbose', '\n')

    # print summary
    xlib.Message.print('info', f'{species_cluster_counter} clusters read.')

    # return the species GOterm dictionary
    return species_goterm_dict, species_seqs_wgoterms

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
