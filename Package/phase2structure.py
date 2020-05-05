#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

'''
This software has been developed by:

    GI Sistemas Naturales e Historia Forestal (formerly known as GI Genetica, Fisiologia e Historia Forestal)
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

'''
This program converts a output PHASE files to the input Structure format in two lines.
'''

#-------------------------------------------------------------------------------

import argparse
import gzip
import os
import re
import sys

import xlib

#-------------------------------------------------------------------------------

def main(argv):
    '''
    Main line of the program.
    '''

    # check the operating system
    xlib.check_os()

    # get and check the arguments
    parser = build_parser()
    args = parser.parse_args()
    check_args(args)

    # convert a PHASE files to Structure file
    convert_phase_to_structure(args.phase_dir, args.phase_extension, args.sample_file, args.sp1_id, args.sp2_id, args.hybrid_id, args.structure_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program converts a output PHASE files to the input Structure format in two lines.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--phasedir', dest='phase_dir', help='Path of the PHASE file directory (mandatory).')
    parser.add_argument('--phaseext', dest='phase_extension', help='Extension of PHASE files (mandatory).')
    parser.add_argument('--samples', dest='sample_file', help='Path of the sample file in the following record format: "sample_id;species_id;mother_id" (mandatory).')
    parser.add_argument('--sp1_id', dest='sp1_id', help='Identification of the first species (mandatory)')
    parser.add_argument('--sp2_id', dest='sp2_id', help='Identification of the second species (mandatory).')
    parser.add_argument('--hyb_id', dest='hybrid_id', help='Identification of the hybrid or NONE; default NONE.')
    parser.add_argument('--structure', dest='structure_file', help='Path of the converted Structure file (mandatory).')
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

    # check "phase_dir"
    if args.phase_dir is None:
        xlib.Message.print('error', '*** The PHASE file directory is not indicated in the input arguments.')
        OK = False
    elif not os.path.isdir(args.phase_dir):
        xlib.Message.print('error', f'*** The directory {args.phase_dir} does not exist.')
        OK = False

    # check "phase_extension"
    if args.phase_extension is None:
        xlib.Message.print('error', '*** The extension of PHASE files is not indicated in the input arguments.')
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
        xlib.Message.print('error', '*** The identification of the first species is not indicated the input arguments.')
        OK = False

    # check "sp2_id"
    if args.sp2_id is None:
        xlib.Message.print('error', '*** The identification of the second species is not indicated in the input arguments.')
        OK = False

    # check "hybrid_id"
    if args.hybrid_id is None:
        args.hybrid_id = 'NONE'

    # check "structure_file"
    if args.structure_file is None:
        xlib.Message.print('error', '*** The converted Structure file is not indicated in the input arguments.')
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

def convert_phase_to_structure(phase_dir, phase_extension, sample_file, sp1_id, sp2_id, hybrid_id, structure_file):
    '''
    Convert a output PHASE output files to the input Structure format in two lines.
    '''

    # intializa the sample haplotype dictionary
    sample_haplotype_dict = {}

    # initialize the PHASE file list
    phase_file_list = []

    # bestpairs_summary pattern
    # format: #sample_id: (gt_left,gt_right)
    bestpairs_summary_pattern = re.compile(r'^#(.*): \((.*),(.*)\)$')

    # get the sample data
    sample_dict = xlib.get_sample_data(sample_file, sp1_id, sp2_id, hybrid_id)

    # get the sorted directory file list
    file_list = sorted(os.listdir(phase_dir))

    # initialize file counter
    file_counter = 0

    # for each file in the PHASE file list
    for file in file_list:

        # check the extension
        if file.endswith(phase_extension):

            # add 1 to the file counter
            file_counter += 1

            # concat the directory to the name of the PHASE file 
            phase_file = f'{phase_dir}/{file}'

            # open the PHASE file
            if phase_file.endswith('.gz'):
                try:
                    phase_file_id = gzip.open(phase_file, mode='rt', encoding='iso-8859-1')
                except Exception as e:
                    raise xlib.ProgramException(e, 'F002', phase_file)
            else:
                try:
                    phase_file_id = open(phase_file, mode='r', encoding='iso-8859-1')
                except Exception as e:
                    raise xlib.ProgramException(e, 'F001', phase_file)

            # initialize the control variable of file with data
            is_there_data = False

            # initialize control variable of bestpairs summary
            is_bestpairs_summary = False

            # read the first record of the PHASE file
            record = phase_file_id.readline()

            # while there are records in the PHASE file
            while record != '' and not record.startswith('END BESTPAIRS_SUMMARY'):

                is_there_data = True

                # when the record is a bestpairs summary data one
                if is_bestpairs_summary:

                    # extract the data 
                    try:
                        mo = bestpairs_summary_pattern.match(record)
                        sample_id = mo.group(1).strip()
                        gt_left = mo.group(2).strip()
                        gt_right = mo.group(3).strip()
                    except Exception as e:
                        raise xlib.ProgramException(e, 'D001', record.strip('\n'), phase_file)

                    # update the haplotype of the sample
                    sample_haplotype_dict[sample_id] = sample_haplotype_dict.get(sample_id, []) + [[gt_left, gt_right]]

                # when the record is the begin of the bestpairs summary
                if record.startswith('BEGIN BESTPAIRS_SUMMARY'):
                    is_bestpairs_summary = True

                # read the next record of the PHASE file
                record = phase_file_id.readline()

            # if there are data in the file, add the file name to PHASE file list
            if is_there_data:
                phase_file_list.append(file)

            # print the counters
            xlib.Message.print('verbose', f'\rProcessed PHASE files ... {file_counter:8d}.')

            # close PHASE file
            phase_file_id.close()

    xlib.Message.print('verbose', '\n')

    # initialize the sequence number
    #sequence_number = -1

    # open the Structure file
    if structure_file.endswith('.gz'):
        try:
            structure_file_id = gzip.open(structure_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F004', structure_file)
    else:
        try:
            structure_file_id = open(structure_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', structure_file)

    # initialize written record counter
    written_record_counter = 0

    # write header record
    phase_file_list_text = '\t'.join(phase_file_list)
    structure_file_id.write(f'sample_id\tspecies_id\t{phase_file_list_text}\n')
    written_record_counter += 1

    # for every sample
    for sample_id in sorted(sample_haplotype_dict.keys()):

        # build the genotype lists
        gt_left_list = []
        gt_right_list = []
        for i in range (len(sample_haplotype_dict[sample_id])):
            gt_left_list.append(sample_haplotype_dict[sample_id][i][0])
            gt_right_list.append(sample_haplotype_dict[sample_id][i][1])

        # check the sequence number
        if len(sample_haplotype_dict[sample_id]) != len(phase_file_list):
            raise xlib.ProgramException('', 'L012')

        # get the species identificacion of the sample
        try:
            species_id = sample_dict[sample_id]['species_id']
        except Exception as e:
            raise xlib.ProgramException(e, 'L002', sample_id)
        if species_id == sp1_id:
            numeric_species_id = 1
        elif species_id == sp2_id:
            numeric_species_id = 2
        else:
            numeric_species_id = 3

        # write the record corresponding to the left genotype list
        gt_left_list_text = '\t'.join(gt_left_list)
        structure_file_id.write(f'{sample_id}\t{numeric_species_id}\t{gt_left_list_text}\n')
        written_record_counter += 1

        # write the record corresponding to the right genotype list
        gt_right_list_text = '\t'.join(gt_right_list)
        structure_file_id.write(f'{sample_id}\t{numeric_species_id}\t{gt_right_list_text}\n')
        written_record_counter += 1

        # print the written record counter
        xlib.Message.print('verbose', f'\rWritten Structure records ... {written_record_counter:8d}.')

    xlib.Message.print('verbose', '\n')

    # close Structure file
    structure_file_id.close()

    # print OK message 
    xlib.Message.print('info', f'The converted file {os.path.basename(structure_file)} is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
