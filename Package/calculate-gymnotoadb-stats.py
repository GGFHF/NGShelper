#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program calculates statistics of the gymnoTOA SQLite database.

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

    # connect to the gymnoTOA SQLite database
    conn = xsqlite.connect_database(args.sqlite_database)

    # calculate statistics of the gymnoTOA SQLite database
    calculate_gymnotoadb_stats(conn, args.stats_file)

    # close connection to SQLite database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program calculates statistics of the gymnoTOA SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the gymnoTOA SQLite database (mandatory).')
    parser.add_argument('--stats', dest='stats_file', help='Path of statistics file (mandatory).')
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
        xlib.Message.print('error', '*** The gymnoTOA SQLite database is not indicated in the input arguments.')
        OK = False

    # check "stats_file"
    if args.stats_file is None:
        xlib.Message.print('error', '*** The statistics file is not indicated in the input arguments.')
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

def calculate_gymnotoadb_stats(conn, stats_file):
    '''
    Calculate statistics of the gymnoTOA SQLite database.
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

    (seqnum_acrogymnospermae, clusternum_total, clusternum_interproscan_annotations, clusternum_emapper_annotations, clusternum_tair10_ortologs, clusternum_without_annotations) = xsqlite.get_gymnotoa_db_stats(conn)

    # write records
    stats_file_id.write( '[statistics]\n')
    stats_file_id.write(f'seqnum_acrogymnospermae = {seqnum_acrogymnospermae}\n')
    stats_file_id.write(f'clusternum_total = {clusternum_total}\n')
    stats_file_id.write(f'clusternum_interproscan_annotations = {clusternum_interproscan_annotations}\n')
    stats_file_id.write(f'clusternum_emapper_annotations = {clusternum_emapper_annotations}\n')
    stats_file_id.write(f'clusternum_tair10_ortologs = {clusternum_tair10_ortologs}\n')
    stats_file_id.write(f'clusternum_without_annotations = {clusternum_without_annotations}\n')

    # close the statistics file
    stats_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
