#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program calculates statistics of the quercusTOA SQLite database.

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

from Bio import Entrez, SeqIO

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

    # connect to the quercusTOA SQLite database
    conn = xsqlite.connect_database(args.sqlite_database)

    # calculate statistics of the quercusTOA SQLite database
    calculate_quercustoadb_stats(conn, args.stats_file, args.noannot_file)

    # close connection to SQLite database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program calculates statistics of the quercusTOA SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the quercusTOA SQLite database (mandatory).')
    parser.add_argument('--stats', dest='stats_file', help='Path of the statistics file (mandatory).')
    parser.add_argument('--noannot', dest='noannot_file', help='Path of the file with sequences without annotations or NONE; default: NONE.')
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
        xlib.Message.print('error', '*** The quercusTOA SQLite database is not indicated in the input arguments.')
        OK = False

    # check "stats_file"
    if args.stats_file is None:
        xlib.Message.print('error', '*** The statistics file is not indicated in the input arguments.')
        OK = False

    # check "noannot_file"
    if args.noannot_file is None or args.noannot_file.upper() == 'NONE':
        args.noannot_file = 'NONE'

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

def calculate_quercustoadb_stats(conn, stats_file, noannot_file):
    '''
    Calculate statistics of the quercusTOA SQLite database.
    '''

    # open the statistics file
    if stats_file.endswith('.gz'):
        try:
            stats_file_id = gzip.open(stats_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', stats_file)
    else:
        try:
            stats_file_id = open(stats_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', stats_file)

    # get the statistics of the quercusTOA database
    (seqnum_quercus, clusternum_total, clusternum_interproscan_annotations, clusternum_emapper_annotations, clusternum_tair10_ortologs, clusternum_without_annotations, ids_without_annotations_list) = xsqlite.get_quercustoa_db_stats(conn)

    # write records in the statistics file
    stats_file_id.write( '[statistics]\n')
    stats_file_id.write(f'seqnum_quercus = {seqnum_quercus}\n')
    stats_file_id.write(f'clusternum_total = {clusternum_total}\n')
    stats_file_id.write(f'clusternum_interproscan_annotations = {clusternum_interproscan_annotations}\n')
    stats_file_id.write(f'clusternum_emapper_annotations = {clusternum_emapper_annotations}\n')
    stats_file_id.write(f'clusternum_tair10_ortologs = {clusternum_tair10_ortologs}\n')
    stats_file_id.write(f'clusternum_without_annotations = {clusternum_without_annotations}\n')

    # close statistics file
    stats_file_id.close()

    # write sequences without annotations if necessary
    if noannot_file != 'NONE':

        # configure Entrez
        Entrez.email = "user@kkkkkkkk.net"

        # open the file with sequences without annotations
        if noannot_file.endswith('.gz'):
            try:
                noannot_file_id = gzip.open(noannot_file, mode='wt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise xlib.ProgramException(e, 'F004', noannot_file)
        else:
            try:
                noannot_file_id = open(noannot_file, mode='w', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise xlib.ProgramException(e, 'F003', noannot_file)

        # write head in the file with sequences without annotations
        noannot_file_id.write('cluster_id;seq_id;description;aminoacids#\n')

        # write records in the file with sequences without annotations
        for id_without_annotations in ids_without_annotations_list:

            # set cluster_id and seq_id
            cluster_id = id_without_annotations[0]
            seq_id = id_without_annotations[1]

            # consult the protein database
            handle = Entrez.efetch(db='protein', id=seq_id, rettype='gb', retmode='text')
            record = SeqIO.read(handle, 'genbank')
            handle.close()

            # get data
            description = record.description
            num_amino_acids = len(record.seq)

            # write record
            noannot_file_id.write(f'{cluster_id};{seq_id};{description};{num_amino_acids}\n')

        # close  the file with sequences without annotations
        noannot_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
