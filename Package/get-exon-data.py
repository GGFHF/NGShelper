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
This program parses a GAMP alignment (-n 0 -m) in order to get data about the coverage, identity and coordinates of exons.
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

    # extract sequences
    get_exon_data(args.alignment_file, args.output_dir)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program parses a GAMP alignment (-n 0 -m) in order to get data about the coverage, identity and coordinates of exons.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--alignment', dest='alignment_file', help='Path of GMAP alignment file (mandatory)')
    parser.add_argument('--outdir', dest='output_dir', help='Path of output directoty where files with exons data are saved (mandatory).')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {get_verbose_code_list_text()}; default: {xlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {get_trace_code_list_text()}; default: {xlib.Const.DEFAULT_TRACE}.')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def check_args(args):
    '''
    Verity the input arguments.
    '''

    # initialize the control variable
    OK = True

    # check "alignment_file"
    if args.alignment_file is None:
        xlib.Message.print('error', '*** The input alignment file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.alignment_file):
        xlib.Message.print('error', f'*** The file {args.alignment_file} does not exist.')
        OK = False

    # check "output_dir"
    if args.output_dir is None:
        xlib.Message.print('error', '*** The output directy is not indicated in the input arguments.')
        OK = False
    elif not os.path.isdir(args.output_dir):
        xlib.Message.print('error', '*** The output directy does not exist.')
        OK = False

    # check "verbose"
    if args.verbose is None:
        args.verbose = xlib.Const.DEFAULT_VERBOSE
    elif args.verbose.upper() not in get_verbose_code_list():
        xlib.Message.print('error', f'The verbose has to be {get_verbose_code_list_text()}.')
        OK = False
    if args.verbose.upper() == 'Y':
        xlib.Message.set_verbose_status(True)

    # check "trace"
    if args.trace is None:
        args.trace = xlib.Const.DEFAULT_TRACE
    elif args.trace.upper() not in get_trace_code_list():
        xlib.Message.print('error', f'The trace has to be {get_trace_code_list_text()}.')
        OK = False
    if args.trace.upper() == 'Y':
        xlib.Message.set_trace_status(True)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def get_exon_data(alignment_file, output_dir):
    '''
    '''

    # open the alignment file
    if alignment_file.endswith('.gz'):
        try:
            alignment_file_id = gzip.open(alignment_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', alignment_file)
    else:
        try:
            alignment_file_id = open(alignment_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', alignment_file)

    # set the exon data file
    exon_data_file = f'{output_dir}{os.sep}exon-data.csv'

    # open the exon data file
    try:
        exon_data_file_id = open(exon_data_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', exon_data_file)

    # write head record of the exon data file
    exon_data_file_id.write('"assembly_id";"genomic_seq_id";"coverage";"exon";"exon_strand";"exon_coordinates";"exon_percent_identity"\n')

    # set the chimera FASTA file
    chimera_fasta_file = f'{output_dir}/chimeras.fasta'

    # open the chimera FASTA file
    try:
        chimera_fasta_file_id = open(chimera_fasta_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', chimera_fasta_file)

    # set the head record of files with assembly identification
    head_record = 'assembly_id;paths_num;path_id;position;length;genomic_seq_id;coverage;percent_identity;mapped_genes'

    # set the file of assembly identifications of chimeras
    assembly_ids_chimeras_file = f'{output_dir}{os.sep}assembly-ids-chimeras.csv'

    # open the file of assembly identifications of chimeras
    try:
        assembly_ids_chimeras_file_id = open(assembly_ids_chimeras_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', assembly_ids_chimeras_file)

    # write head record of the file of assembly identifications of chimeras
    assembly_ids_chimeras_file_id.write(f'{head_record}\n')

    # set the file of assembly identifications with 0 paths
    assembly_ids_0paths_file = f'{output_dir}{os.sep}assembly-ids-0paths.csv'

    # open the file of assembly identifications with 0 paths
    try:
        assembly_ids_0paths_file_id = open(assembly_ids_0paths_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', assembly_ids_0paths_file)

    # write head record of the file of assembly identifications with 0 paths
    assembly_ids_0paths_file_id.write(f'{head_record}\n')

    # set the file of assembly identifications with 1 path
    assembly_ids_1path_file = f'{output_dir}{os.sep}assembly-ids-1path.csv'

    # open the file of assembly identifications with 1 path
    try:
        assembly_ids_1path_file_id = open(assembly_ids_1path_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', assembly_ids_1path_file)

    # write head record of the file of assembly identifications with 1 paths
    assembly_ids_1path_file_id.write(f'{head_record}\n')

    # set the file of assembly identifications with n paths (n > 1)
    assembly_ids_npaths_file = f'{output_dir}{os.sep}assembly-ids-npaths.csv'

    # open the file of assembly identifications with n paths
    try:
        assembly_ids_npaths_file_id = open(assembly_ids_npaths_file, mode='w', encoding='iso-8859-1', newline='\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F003', assembly_ids_npaths_file)

    # write head record of the file of assembly identifications with n paths
    assembly_ids_npaths_file_id.write(f'{head_record}\n')

    # initialize record counters
    alignment_counter = 0
    exon_counter = 0
 
    # read the first record of alignment file
    record = alignment_file_id.readline()

    # while there are records in alignment file
    while record != '':

        # process the head record 
        if record.startswith('>'):

            # add 1 to the alignment counter
            alignment_counter += 1

            # initialize the chimera control variable
            is_chimera = False

            # initialize alignment data
            assembly_id = '-'
            paths_num = 0

            # initialize data of path 1
            genomic_seq_id_1 = '-'
            position_1 = ''
            length_1 = 0
            coverage_1 = 0
            percent_identity_1 = 0
            seq_1 = ''
            mapped_genes_1 = '-'

            # initialize data of path 2 (these data are necessary when alignment is a chimera)
            genomic_seq_id_2 = '-'
            position_2 = ''
            length_2 = 0
            coverage_2 = 0
            percent_identity_2 = 0
            seq_2 = ''
            mapped_genes_2 = '-'

            # initialize exon data (these data are necessary when there is one path)
            exon_num = 0
            exon_strand_list =  []
            exon_coordinates_list =  []
            exon_percent_identity_list = []

            # extract the identification
            assembly_id = record[1:].strip('\n')

            # read the next record
            record = alignment_file_id.readline()

        else:

            # control the FASTA format
            raise xlib.ProgramException('F006', alignment_file, 'FASTA')

        # while there are records and they are sequence
        while record != '' and not record.startswith('>'):

            # get exon data
            if record.startswith('Paths'):

                # check if the alignment is a chimera:
                if record.find('*** Possible chimera') > -1:

                    # set chimera control variable
                    is_chimera = True

                    # read until the first path
                    text = 'Path 1: query'
                    while record != '' and record.find(text) == -1:
                        record = alignment_file_id.readline()

                    # get the first sequence position
                    start = record.find(text) + len(text)
                    middle = record.find('(')
                    try:
                        position_1 = record[start:middle].strip()
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'position_1', assembly_id)

                    # get the first sequence length
                    end = record.find(')')
                    try:
                        length_1 = int(record[middle+1:end-3].strip())
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'length_1', assembly_id)

                    # get the first genomic sequence identification
                    text = 'genome'
                    start = record.find(text)+len(text)
                    end = record[start:].find(':')
                    try:
                        genomic_seq_id_1 = record[start:start + end].strip()
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'genomic_seq_id_1', assembly_id)

                    # read until the coverage
                    coverage_text = 'Coverage:'
                    while record != '' and not record.strip().startswith(coverage_text):
                        record = alignment_file_id.readline()

                    # get the coverage
                    start = record.find(coverage_text)+len(coverage_text)
                    end = record[start:].find('(')
                    try:
                        coverage_1 = float(record[start:start + end].strip())
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'coverage_1', assembly_id)

                    # read until the percent identity
                    percent_identity_text = 'Percent identity:'
                    while record != '' and not record.strip().startswith(percent_identity_text):
                        record = alignment_file_id.readline()

                    # get the percent identity
                    start = record.find(percent_identity_text)+len(percent_identity_text)
                    end = record[start:].find('(')
                    try:
                        percent_identity_1 = float(record[start:start + end].strip())
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'percent_identity_1', assembly_id)

                    # read until the second path
                    text = 'Path 2: query'
                    while record != '' and record.find(text) == -1:
                        record = alignment_file_id.readline()

                    # get the second sequence position
                    start = record.find(text) + len(text)
                    middle = record.find('(')
                    try:
                        position_2 = record[start:middle].strip()
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'position_2', assembly_id)

                    # get the second sequence length
                    end = record.find(')')
                    try:
                        length_2 = int(record[middle+1:end-3].strip())
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'length_2', assembly_id)

                    # get the second genomic sequence identification
                    text = 'genome'
                    start = record.find(text)+len(text)
                    end = record[start:].find(':')
                    try:
                        genomic_seq_id_2 = record[start:start + end].strip()
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'genomic_seq_id_2', assembly_id)

                    # read until the coverage
                    coverage_text = 'Coverage:'
                    while record != '' and not record.strip().startswith(coverage_text):
                        record = alignment_file_id.readline()

                    # get the coverage
                    start = record.find(coverage_text)+len(coverage_text)
                    end = record[start:].find('(')
                    try:
                        coverage_2 = float(record[start:start + end].strip())
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'coverage_2', assembly_id)

                    # read until the percent identity
                    percent_identity_text = 'Percent identity:'
                    while record != '' and not record.strip().startswith(percent_identity_text):
                        record = alignment_file_id.readline()

                    # get the percent identity
                    start = record.find(percent_identity_text)+len(percent_identity_text)
                    end = record[start:].find('(')
                    try:
                        percent_identity_2 = float(record[start:start + end].strip())
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'percent_identity_2', assembly_id)

                    # get parts of sequence 1
                    is_first_genomic_seq_id_1 = True
                    record = alignment_file_id.readline()
                    while record != '' and record.find('Alignment for path 2') == -1:
                        if record.find(genomic_seq_id_1) > -1:
                            if is_first_genomic_seq_id_1:
                                is_first_genomic_seq_id_1 = False
                                while record != '' and record.find(genomic_seq_id_1) > -1:
                                    record = alignment_file_id.readline()
                            else:
                                i = 0
                                while record != '' and i < 2:
                                    record = alignment_file_id.readline()
                                    i += 1
                                if record == '':
                                    raise xlib.ProgramException('', 'F011', assembly_id)
                                record = record.strip()
                                start = record.find(' ')
                                seq_1 += record[start+1:].replace(' ','')
                        record = alignment_file_id.readline()

                    # get parts of sequence 2
                    is_first_genomic_seq_id_2 = True
                    record = alignment_file_id.readline()
                    while record != '' and not record.startswith('Maps') and not record.startswith('>'):
                        if record.find(genomic_seq_id_2) > -1:
                            if is_first_genomic_seq_id_2:
                                is_first_genomic_seq_id_2 = False
                                while record != '' and record.find(genomic_seq_id_2) > -1:
                                    record = alignment_file_id.readline()
                            else:
                                i = 0
                                while record != '' and i < 2:
                                    record = alignment_file_id.readline()
                                    i += 1
                                if record == '':
                                    raise xlib.ProgramException('', 'F011', assembly_id)
                                record = record.strip()
                                start = record.find(' ')
                                seq_2 += record[start+1:].replace(' ','')
                        record = alignment_file_id.readline()

                    # read records until the map hits for path 1
                    while record != '' and record.strip().find('Map hits for path 1') == -1 and not record.startswith('>'):
                        record = alignment_file_id.readline()

                    if record.strip().find('Map hits for path 1') > -1:
                        record = alignment_file_id.readline()

                    # read records with mapped genes of path 1
                    while record != '' and record != '\n' and record.strip().find('Map hits for path 2') == -1 and not record.startswith('>'):
                        record = record.strip()
                        last_tab_pos = record.rfind('\t')
                        if mapped_genes_1 == '-':
                            mapped_genes_1 = record[last_tab_pos+1:]
                        else:
                            mapped_genes_1 = f'{mapped_genes_1}*{record[last_tab_pos+1:]}'
                        record = alignment_file_id.readline()

                    # read records until the map hits for path 2
                    while record != '' and record.strip().find('Map hits for path 2') == -1 and not record.startswith('>'):
                        record = alignment_file_id.readline()

                    if record.strip().find('Map hits for path 2') > -1:
                        record = alignment_file_id.readline()

                    # read records with maped genes of path 2
                    while record != '' and record != '\n' and not record.startswith('>'):
                        record = record.strip()
                        last_tab_pos = record.rfind('\t')
                        if mapped_genes_2 == '-':
                            mapped_genes_2 = record[last_tab_pos+1:]
                        else:
                            mapped_genes_2 = f'{mapped_genes_2}*{record[last_tab_pos+1:]}'
                        record = alignment_file_id.readline()

                # when the align is not a chimera
                elif not is_chimera:
                    # get the path number
                    try:
                        paths_num = int(record[record.find('(') + 1:record.find(')')])
                    except Exception as e:
                        raise xlib.ProgramException(e, 'F010', 'path_num', assembly_id)

                    # if path number is equal to 0, there are not exon data
                    if paths_num == 0:

                        # read records until the next transcript or EOF
                        record = alignment_file_id.readline()
                        while record != '' and not record.startswith('>'):
                            record = alignment_file_id.readline()

                    # if path number is greater than to 0, there are exon data
                    elif paths_num > 0:

                        # read until the first path
                        text = 'Path 1: query'
                        while record != '' and record.find(text) == -1:
                            record = alignment_file_id.readline()

                        # get the first sequence position
                        start = record.find(text) + len(text)
                        middle = record.find('(')
                        try:
                            position_1 = record[start:middle].strip()
                        except Exception as e:
                            raise xlib.ProgramException(e, 'F010', 'position_1', assembly_id)

                        # get the first sequence length
                        end = record.find(')')
                        try:
                            length_1 = int(record[middle+1:end-3].strip())
                        except Exception as e:
                            raise xlib.ProgramException(e, 'F010', 'length_1', assembly_id)

                        # get the genomic sequence identification
                        text = 'genome'
                        start = record.find(text)+len(text)
                        end = record[start:].find(':')
                        try:
                            genomic_seq_id_1 = record[start:start + end].strip()
                        except Exception as e:
                            raise xlib.ProgramException(e, 'F010', 'genomic_seq_id_1', assembly_id)

                        # read until the number of exons
                        exon_num_text = 'Number of exons:'
                        while record != '' and not record.strip().startswith(exon_num_text):
                            record = alignment_file_id.readline()

                        # get the exon number
                        start = record.find(exon_num_text)+len(exon_num_text)
                        try:
                            exon_num = int(record[start:].strip())
                        except Exception as e:
                            raise xlib.ProgramException(e, 'F010', 'exon_num', assembly_id)

                        # read until the coverage
                        coverage_text = 'Coverage:'
                        while record != '' and not record.strip().startswith(coverage_text):
                            record = alignment_file_id.readline()

                        # get the coverage
                        start = record.find(coverage_text)+len(coverage_text)
                        end = record[start:].find('(')
                        try:
                            coverage_1 = float(record[start:start + end].strip())
                        except Exception as e:
                            raise xlib.ProgramException(e, 'F010', 'coverage_1', assembly_id)

                        # read until the percent identity
                        percent_identity_text = 'Percent identity:'
                        while record != '' and not record.strip().startswith(percent_identity_text):
                            record = alignment_file_id.readline()

                        # get the percent identity
                        start = record.find(percent_identity_text)+len(percent_identity_text)
                        end = record[start:].find('(')
                        try:
                            percent_identity_1 = float(record[start:start + end].strip())
                        except Exception as e:
                            raise xlib.ProgramException(e, 'F010', 'percent_identity_1', assembly_id)

                        # read records until the alignment for path 1
                        while record != '' and not record.strip().startswith('Alignment for path 1:'):
                            record = alignment_file_id.readline()

                        # read records until the first exon data
                        record = alignment_file_id.readline()
                        while record != '' and record == '\n':
                            record = alignment_file_id.readline()

                        # get the exon data
                        for i in range(exon_num):

                            # get the strand
                            try:
                                exon_strand = record.strip()[0]
                                exon_strand_list.append(exon_strand)
                            except Exception as e:
                                print(f'i: {i}')
                                print(f'record: {record.strip()}')
                                raise xlib.ProgramException(e, 'F010', 'exon_strand', assembly_id)

                            # get the coordinates
                            try:
                                exon_coordinates = record[record.find(':') + 1:record.find('(')].strip()
                                exon_coordinates_list.append(exon_coordinates)
                            except Exception as e:
                                raise xlib.ProgramException(e, 'F010', 'exon_coordinates', assembly_id)

                            # get the percent identity
                            try:
                                exon_percent_identity = float(record[record.find(')') + 1:record.find('%')].strip())
                                exon_percent_identity_list.append(exon_percent_identity)
                            except Exception as e:
                                raise xlib.ProgramException(e, 'F010', 'exon_percent_identity', assembly_id)

                            # read next record
                            record = alignment_file_id.readline()


                        # read records until the map hits for path 1
                        while record != '' and record.strip().find('Map hits for path 1') == -1 and not record.startswith('>'):
                            record = alignment_file_id.readline()

                        if record.strip().find('Map hits for path 1') > -1:
                            record = alignment_file_id.readline()

                        # read records with maped genes of path 1
                        while record != '' and record != '\n' and not record.startswith('>'):
                            record = record.strip()
                            last_tab_pos = record.rfind('\t')
                            if mapped_genes_1 == '-':
                                mapped_genes_1 = record[last_tab_pos+1:]
                            else:
                                mapped_genes_1 = f'{mapped_genes_1}*{record[last_tab_pos+1:]}'
                            record = alignment_file_id.readline()

                        # read records until the next transcript or EOF
                        record = alignment_file_id.readline()
                        while record != '' and not record.startswith('>'):
                            record = alignment_file_id.readline()

            else:

                # read the next record of alignment file
                record = alignment_file_id.readline()

        # write the exon data (only when the path number is equal to 1) and assembly identification in their corresponding files
        if is_chimera:
            seq_1 = re.sub('[0123456789]', '', seq_1)
            seq_2 = re.sub('[0123456789]', '', seq_2)
            # check sequence length
            if length_1 != len(seq_1) or length_2 != len(seq_2):
                print(f'seq_1: {seq_1}')
                print(f'length_1: {length_1} - len(seq_1): {len(seq_1)}')
                print(f'seq_2: {seq_2}')
                print(f'length_2: {length_2} - len(seq_2): {len(seq_2)}')
                raise xlib.ProgramException('', 'F011', assembly_id)
            # write the FASTA sequences
            if assembly_id.startswith('TRINITY'):
                isoform_pos = assembly_id.find('_i')
                space_pos = assembly_id.find(' ')
                assembly_id_1 = f'{assembly_id[:isoform_pos]}-1{assembly_id[isoform_pos:space_pos]}'
                chimera_fasta_file_id.write(f'>{assembly_id_1}\n')
                chimera_fasta_file_id.write(f'{seq_1}\n')
                assembly_id_2 = f'{assembly_id[:isoform_pos]}-2{assembly_id[isoform_pos:space_pos]}'
                chimera_fasta_file_id.write(f'>{assembly_id_2}\n')
                chimera_fasta_file_id.write(f'{seq_2}\n')
            else:
                chimera_fasta_file_id.write(f'>{assembly_id}-{position_1}\n')
                chimera_fasta_file_id.write(f'{seq_1}\n')
                chimera_fasta_file_id.write(f'>{assembly_id}-{position_2}\n')
                chimera_fasta_file_id.write(f'{seq_2}\n')
            # write the assembly identification
            assembly_ids_chimeras_file_id.write(f'{assembly_id};c;1;{position_1};{length_1};{genomic_seq_id_1};{coverage_1};{percent_identity_1};{mapped_genes_1}\n')
            assembly_ids_chimeras_file_id.write(f'{assembly_id};c;2;{position_2};{length_2};{genomic_seq_id_2};{coverage_2};{percent_identity_2};{mapped_genes_2}\n')
        else:
            if paths_num == 0:
                # write the assembly identification
                assembly_ids_0paths_file_id.write(f'{assembly_id};{paths_num};0;{position_1};{length_1};{genomic_seq_id_1};{coverage_1};{percent_identity_1};{mapped_genes_1}\n')
            elif paths_num == 1:
                # write the exon data
                for i in range(exon_num):
                    exon_data_file_id.write(f'"{assembly_id}";"{genomic_seq_id_1}";{coverage_1};{i +1};"{exon_strand_list[i]}";"{exon_coordinates_list[i]}";{exon_percent_identity_list[i]}\n')
                    exon_counter += 1
                # write the assembly identification
                assembly_ids_1path_file_id.write(f'{assembly_id};{paths_num};1;{position_1};{length_1};{genomic_seq_id_1};{coverage_1};{percent_identity_1};{mapped_genes_1}\n')
            else:
                assembly_ids_npaths_file_id.write(f'{assembly_id};{paths_num};1;{position_1};{length_1};{genomic_seq_id_1};{coverage_1};{percent_identity_1};{mapped_genes_1}\n')

        # print the counters
        xlib.Message.print('verbose', f'\rAlignments ... {alignment_counter:8d} - Exons ... {exon_counter:8d}')

    # close files
    alignment_file_id.close()
    exon_data_file_id.close()
    chimera_fasta_file_id.close()
    assembly_ids_chimeras_file_id.close()
    assembly_ids_0paths_file_id.close()
    assembly_ids_1path_file_id.close()
    assembly_ids_npaths_file_id.close()

    # print OK message 
    xlib.Message.print('verbose', f'\nThe file {os.path.basename(exon_data_file)} containing the extacted sequences is created.')

#-------------------------------------------------------------------------------
    
def get_verbose_code_list():
    '''
    Get the code list of "verbose".
    '''

    return ['Y', 'N']

#-------------------------------------------------------------------------------
    
def get_verbose_code_list_text():
    '''
    Get the code list of "verbose" as text.
    '''

    return 'Y (yes) or N (no)'

#-------------------------------------------------------------------------------
    
def get_trace_code_list():
    '''
    Get the code list of "trace".
    '''

    return ['Y', 'N']

#-------------------------------------------------------------------------------
    
def get_trace_code_list_text():
    '''
    Get the code list of "trace" as text.
    '''

    return 'Y (yes) or N (no)'

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
