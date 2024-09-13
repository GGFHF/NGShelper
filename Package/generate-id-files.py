#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program generates template files with random sample identifiers for use with VCF files.

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
import os
import random
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

    # generate files with sample identifiers for use with VCF files
    generate_id_files(args.sp1_id, args.sp1_total_individuals, args.sp1_selected_individuals, args.sp2_id, args.sp2_total_individuals, args.sp2_selected_individuals, args.hybrid_id, args.hybrid_total_individuals, args.hybrid_selected_individuals, args.sample_id_file_1, args.sample_id_file_2)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program generates template files with random sample identifiers for use with VCF files.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp1_totinds', dest='sp1_total_individuals', help='Total individuals number of the first species (mandatory)')
    parser.add_argument('--sp1_selinds', dest='sp1_selected_individuals', help='Selected individuals number of the first species (mandatory).')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species or NONE; default NONE.')
    parser.add_argument('--sp2_totinds', dest='sp2_total_individuals', help='Total individuals number of the second species or 0; default 0.')
    parser.add_argument('--sp2_selinds', dest='sp2_selected_individuals', help='Selected individuals number of the second species or 0; default 0.')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--hyb_totinds', dest='hybrid_total_individuals', help='Total individuals number of the hybrid or 0; default 0.')
    parser.add_argument('--hyb_selinds', dest='hybrid_selected_individuals', help='Selected individuals number of the hybrid (mandatory).')
    parser.add_argument('--outfile1', dest='sample_id_file_1', help='Path of the sample identification file 1 (mandatory).')
    parser.add_argument('--outfile2', dest='sample_id_file_2', help='Path of the sample identification file 2 (mandatory).')
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

    # check "sp1_id"
    if args.sp1_id is None:
        xlib.Message.print('error', '*** The identification of the first species is not indicated in the input arguments.')
        OK = False

    # check "sp1_total_individuals"
    if not xlib.check_int(args.sp1_total_individuals, minimum=1):
        xlib.Message.print('error', 'The total individuals number of the first species has to be an integer number greater than or equal to 1.')
        OK = False
    else:
        args.sp1_total_individuals = int(args.sp1_total_individuals)

    # check "sp1_selected_individuals"
    if not xlib.check_int(args.sp1_selected_individuals, minimum=1):
        xlib.Message.print('error', 'The selected individuals number of the first species has to be an integer number greater than or equal to 1.')
        OK = False
    else:
        args.sp1_selected_individuals = int(args.sp1_selected_individuals)

    # check "sp2_id"
    if args.sp2_id is None:
        args.sp2_id = 'NONE'

    # check "sp2_total_individuals"
    if args.sp2_total_individuals is None:
        args.sp2_total_individuals = 0
    elif not xlib.check_int(args.sp2_total_individuals, minimum=0):
        xlib.Message.print('error', 'The total individuals number of the second species has to be an integer number greater than or equal to 1 or 0 of sp2_id is NONE.')
        OK = False
    else:
        args.sp2_total_individuals = int(args.sp2_total_individuals)

    # check "sp2_selected_individuals"
    if args.sp2_selected_individuals is None:
        args.sp2_selected_individuals = 0
    elif not xlib.check_int(args.sp2_selected_individuals, minimum=0):
        xlib.Message.print('error', 'The total individuals number of the second species has to be an integer number greater than or equal to 1 or 0 of sp2_id is NONE.')
        OK = False
    else:
        args.sp2_selected_individuals = int(args.sp2_selected_individuals)

    # check "hybrid_id"
    if args.hybrid_id is None:
        args.hybrid_id = 'NONE'

    # check "hybrid_total_individuals"
    if args.hybrid_total_individuals is None:
        args.hybrid_total_individuals = 0
    elif not xlib.check_int(args.hybrid_total_individuals, minimum=0):
        xlib.Message.print('error', 'The total individuals number of the hybrid has to be an integer number greater than or equal to 1 or 0 of hybrid_id is NONE.')
        OK = False
    else:
        args.hybrid_total_individuals = int(args.hybrid_total_individuals)

    # check "hybrid_selected_individuals"
    if args.hybrid_selected_individuals is None:
        args.hybrid_selected_individuals = 0
    elif not xlib.check_int(args.hybrid_selected_individuals, minimum=0):
        xlib.Message.print('error', 'The total individuals number of the hybrid has to be an integer number greater than or equal to 1 or 0 of hybrid_id is NONE.')
        OK = False
    else:
        args.hybrid_selected_individuals = int(args.hybrid_selected_individuals)

    # check "sample_id_file_1"
    if args.sample_id_file_1 is None:
        xlib.Message.print('error', '*** The sample identification file 1 is not indicated in the input arguments.')
        OK = False

    # check "sample_id_file_2"
    if args.sample_id_file_2 is None:
        xlib.Message.print('error', '*** The sample identification file 2 is not indicated in the input arguments.')
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

def generate_id_files(sp1_id, sp1_total_individuals, sp1_selected_individuals, sp2_id, sp2_total_individuals, sp2_selected_individuals, hybrid_id, hybrid_total_individuals, hybrid_selected_individuals, sample_id_file_1, sample_id_file_2):
    '''
    Generate template files with random sample identifiers for use with VCF files.
    '''

    # define the function to get randomly the list of individuals
    def get_individual_id_list(sp_id, total_individuals, selected_individuals):

        total_inds_list = [f'{sp_id}-{x:02d}' for x in range(1, total_individuals + 1)]
        random.shuffle(total_inds_list)
        selected_inds_list = sorted(total_inds_list[0:selected_individuals])
        return selected_inds_list

    # get the list of individuals of the first species
    sp1_ind_id_list = get_individual_id_list(sp1_id, sp1_total_individuals, sp1_selected_individuals)

    # get the list of individuals of the first species
    sp2_ind_id_list = get_individual_id_list(sp2_id, sp2_total_individuals, sp2_selected_individuals)

    # get the list of individuals of the hybrid
    hybrid_ind_id_list = get_individual_id_list(hybrid_id, hybrid_total_individuals, hybrid_selected_individuals)

    # print OK message
    xlib.Message.print('info', f'The converted file {os.path.basename(sample_id_file_1)} is created.')

    # open the sample identification file 1
    try:
        sample_id_file_1_id = open(sample_id_file_1, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', sample_id_file_1)

    # write records corresponding to the first species
    for sp1_ind_id in sp1_ind_id_list:
        sample_id_file_1_id.write(f'{sp1_ind_id}\n')

    # write records corresponding to the second species
    for sp2_ind_id in sp2_ind_id_list:
        sample_id_file_1_id.write(f'{sp2_ind_id}\n')

    # write records corresponding to the hybrid
    for hybrid_ind_id in hybrid_ind_id_list:
        sample_id_file_1_id.write(f'{hybrid_ind_id}\n')

    # close the sample identification file 1
    sample_id_file_1_id.close()

    # open the sample identification file 1
    try:
        sample_id_file_2_id = open(sample_id_file_2, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', sample_id_file_2)

    # write records corresponding to the first species
    for sp1_ind_id in sp1_ind_id_list:
        sample_id_file_2_id.write(f'{sp1_ind_id};{sp1_id};NONE\n')

    # write records corresponding to the second species
    for sp2_ind_id in sp2_ind_id_list:
        sample_id_file_2_id.write(f'{sp2_ind_id};{sp2_id};NONE\n')

    # write records corresponding to the hybrid
    for hybrid_ind_id in hybrid_ind_id_list:
        sample_id_file_2_id.write(f'{hybrid_ind_id};{hybrid_id};NONE\n')

    # close the sample identification file 2
    sample_id_file_2_id.close()

    # print OK message
    xlib.Message.print('info', f'The converted file {os.path.basename(sample_id_file_2)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
