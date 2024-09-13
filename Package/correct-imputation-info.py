#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program corrects columns of info data in a summay file yielded by a SOM imputation process.

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

    # correct columns of info data in a summay file yielded by a SOM imputation process
    correct_imputation_info(args.input_file, args.output_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program corrects columns of info data in a summay file yielded by a SOM imputation process.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--in', dest='input_file', help='Path of the input summay file (mandatory).')
    parser.add_argument('--out', dest='output_file', help='Path of the output summay file (mandatory).')
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

    # check "input_file"
    if args.input_file is None:
        xlib.Message.print('error', '*** The input summay file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.input_file):
        xlib.Message.print('error', f'*** The file {args.input_file} does not exist.')
        OK = False

    # check "output_file"
    if args.output_file is None:
        xlib.Message.print('error', '*** The output summay file is not indicated in the input arguments.')
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

def correct_imputation_info(input_file, output_file):
    '''
    Correct columns of info data in a summay file yielded by a SOM imputation process.
    '''

    # initialize the header record control
    header_record = True

    # open the input file
    if input_file.endswith('.gz'):
        try:
            input_file_id = gzip.open(input_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', input_file)
    else:
        try:
            input_file_id = open(input_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', input_file)

    # initialize the input record counter
    input_record_counter = 0

    # open the output file
    if output_file.endswith('.gz'):
        try:
            output_file_id = gzip.open(output_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', output_file)
    else:
        try:
            output_file_id = open(output_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', output_file)

    # read the first record
    record = input_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        input_record_counter += 1

        # process the header record
        if header_record:
            output_file_id.write(record)
            header_record = False

        # process data records
        else:

            # extract data
            # record format: file_name;algorithm;experiment_id;dataset_id;method;mdp;mpiwmd;dim;sigma;lr;iter;mr2;snps;gim;high_ld_sites;nn;max_dist;ok_genotypes_counter;ko_genotypes_counter;genotypes_withmd_counter;ok_imputed_genotypes_counter;ko_imputed_genotypes_counter;average_accuracy;error_rate;micro_precision;micro_recall;micro_fscore;macro_precision;macro_recall;macro_fscore;macro_precision_zde;macro_recall_zde
            data_list = []
            begin = 0
            for end in [i for i, chr in enumerate(record) if chr == ';']:
                data_list.append(record[begin:end].strip())
                begin = end + 1
            data_list.append(record[begin:].strip('\n').strip())
            try:
                file_name = data_list[0]
                algorithm = data_list[1]
                experiment_id = data_list[2]
                dataset_id = data_list[3]
                method = data_list[4]
                mdp = data_list[5]
                mpiwmd = data_list[6]
                dim = data_list[7]
                sigma = data_list[8]
                lr = data_list[9]
                iter = data_list[10]
                mr2 = data_list[11]
                snps = data_list[12]
                gim = data_list[13]
                high_ld_sites = data_list[14]
                nn = data_list[15]
                max_dist = data_list[16]
                ok_genotypes_counter = data_list[17]
                ko_genotypes_counter = data_list[18]
                genotypes_withmd_counter = data_list[19]
                ok_imputed_genotypes_counter = data_list[20]
                ko_imputed_genotypes_counter = data_list[21]
                average_accuracy = data_list[22]
                error_rate = data_list[23]
                micro_precision = data_list[24]
                micro_recall = data_list[25]
                micro_fscore = data_list[26]
                macro_precision = data_list[27]
                macro_recall = data_list[28]
                macro_fscore = data_list[29]
                macro_precision_zde = data_list[30]
                macro_recall_zde = data_list[31]
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(input_file), input_record_counter)

            # correct "mdp" and "mpiwmd"
            if algorithm.upper() in ['RANDOM', 'NAIVE']:

                if dataset_id == 'MOUSE':
                    pattern = r'^MOUSE-(.*)$'
                    mo = re.search(pattern, experiment_id)
                    process_id = mo.group(1).strip()
                elif dataset_id == 'MOUSEred':
                    pattern = r'^MOUSEred-(.*)$'
                    mo = re.search(pattern, experiment_id)
                    process_id = mo.group(1).strip()
                else:
                    pattern = r'^SUBERINTRO-(.*)-(.*)$'
                    mo = re.search(pattern, experiment_id)
                    process_id = mo.group(2).strip()

                if process_id.startswith('B'):
                    mdp = 0.10
                    mpiwmd = 10
                elif process_id.startswith('C'):
                    mdp = 0.10
                    mpiwmd = 20
                elif process_id.startswith('D'):
                    mdp = 0.10
                    mpiwmd = 30
                elif process_id.startswith('E'):
                    mdp = 0.20
                    mpiwmd = 10
                elif process_id.startswith('F'):
                    mdp = 0.20
                    mpiwmd = 20
                elif process_id.startswith('G'):
                    mdp = 0.20
                    mpiwmd = 30
                elif process_id.startswith('H'):
                    mdp = 0.30
                    mpiwmd = 10
                elif process_id.startswith('I'):
                    mdp = 0.30
                    mpiwmd = 20
                elif process_id.startswith('J'):
                    mdp = 0.30
                    mpiwmd = 30

            # write data into the output file
            output_file_id.write(f'{file_name};{algorithm};{experiment_id};{dataset_id};{method};{mdp};{mpiwmd};{dim};{sigma};{lr};{iter};{mr2};{snps};{gim};{high_ld_sites};{nn};{max_dist};{ok_genotypes_counter};{ko_genotypes_counter};{genotypes_withmd_counter};{ok_imputed_genotypes_counter};{ko_imputed_genotypes_counter};{average_accuracy};{error_rate};{micro_precision};{micro_recall};{micro_fscore};{macro_precision};{macro_recall};{macro_fscore};{macro_precision_zde};{macro_recall_zde}\n')

            # print counters
            xlib.Message.print('verbose', f'\rinput file: {input_record_counter} processed records')

        # read the next record
        record = input_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # close gene_info file
    input_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
