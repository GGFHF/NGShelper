#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This program fixes sequence identifiers of a read file generated by simNGS to compatible format with CASAVA.

    Each read entry in a FASTQ file consists of four records:
        - Sequence identifier
        - Sequence
        - Quality score identifier line (consisting of a +)
        - Quality score

    In CASAVA, each sequence identifier, the line that precedes the sequence and describes it, needs to be
    in the following format:
        @<instrument>:<run>:<flowcell>:<lane>:<tile>:<x_pos>:<y_pos> <read>:<is_filtered>:<control>:<index>

    Where:

        instrument = Instrument ID (Characters allowed: a-z, A-Z, 0-9 and underscore)
        run = Run number on instrument (Numerical)
        flowcell = Flowcell ID (Characters allowed: a-z, A-Z, 0-9)
        lane = Lane number (Numerical)
        tile = Tile number (Numerical)
        x_pos = X coordinate of cluster (Numerical)
        y_pos = Y coordinate of cluster (Numerical)

        read = Read number. 1 can be single read or read 2 of paired-end  (Numerical)
        is_filtered = Y if the read is filtered, N otherwise (Y or N)
        control = 0 when none of the control bits are on, otherwise it is an even number (Numerical)
        index = Index sequence (ACTG)

    Sequence identifier example:
        @EAS139:136:FC706VJ:2:5:1000:12850 1:Y:18:ATCACG
        @MG00HS20:721:C7JR3ANXX:1:1101:18066:6008 1:N:0:CGATGT

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

    # fix sequence identifiers
    fix_seq_ids(args.filenum, args.readfile)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program fixes sequence identifiers of a read file generated by simNGS to compatible format with CASAVA.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--filenum', dest='filenum', help='1: in SE file or the first file in PE files; 2: the second file in PE files')
    parser.add_argument('--readfile', dest='readfile', help='Path of a read file generated by simNGS in FASTQ format')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def check_args(args):
    '''
    Verity the input arguments data.
    '''

    # initialize the control variable
    OK = True

    # check filenum
    if args.filenum is None:
        xlib.Message.print('error', '*** The file number must be indicated  in the input arguments.')
        OK = False
    else:
        try:
            args.filenum = int(args.filenum)
        except Exception:
            xlib.Message.print('error', f'*** The value {args.filenum} of file number is not 1 or 2.')
            OK = False
        if args.filenum not in [1, 2]:
            xlib.Message.print('error', f'*** The value {args.filenum} of file number is not 1 or 2.')
            OK = False

    # check readfile
    if args.readfile is None:
        xlib.Message.print('error', '*** A read file generated by simNGS in FASTQ format is not indicated in the input arguments.')
        OK = False
    else:
        if not os.path.isfile(args.readfile):
            xlib.Message.print('error', f'*** The file {args.readfile} does not exist.')
            OK = False
        if not args.readfile.endswith('.fastq') and not args.readfile.endswith('.fq') and not args.readfile.endswith('.fastq.gz') and not args.readfile.endswith('.fq.gz'):
            xlib.Message.print('error', f'*** The file {args.readfile} does not end in ".fastq", ".fq", ".fastq.gz or ".fq.gz".')
            OK = False

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def fix_seq_ids(filenum, readfile):
    '''
    Fix sequence identifiers.
    '''

    # set default values in sequence identifier data
    instrument = 'MG00HS20'
    run = 1
    flowcell = 'XXX'
    lane = 1
    tile = 1
    is_filtered = 'N'
    control = 0
    index = 'ACTG' if filenum == 1 else 'GTCA'

    # check if read file is a GZ file
    if readfile.endswith('.gz'):
        is_gz = True
    else:
        is_gz = False

    # set the read file and the fixed read file path
    fixed_readfile = os.path.dirname(readfile) + 'fixed_' + os.path.basename(readfile)

    # open the read file
    try:
        if is_gz:
            readfile_id = gzip.open(readfile, mode='rt', encoding='iso-8859-1')
        else:
            readfile_id = open(readfile, mode='r', encoding='iso-8859-1')
    except Exception as e:
        raise xlib.ProgramException(e, 'F001', readfile)

    # open the fixed read file
    try:
        if is_gz:
            fixed_readfile_id = gzip.open(fixed_readfile, mode='wt', encoding='iso-8859-1')
        else:
            fixed_readfile_id = open(fixed_readfile, mode='w', encoding='iso-8859-1')
    except Exception as e:
        raise xlib.ProgramException(e, 'F001', fixed_readfile)

    # set the pattern of the sequence identifier record
    pattern = r'^@Frag_([0-9]+) (\S+) .* Strand ([\+\-]) Offset ([0-9]+--[0-9]+) .*$'

    # read the first record of readfile
    record = readfile_id.readline()

    # while there are records in readfile
    while record != '':

        # process the sequence identifier record
        if record.startswith('@'):

            # extract the data
            record = record.replace('(','')
            record = record.replace(')','')
            mo = re.search(pattern, record)
            fragment = mo.group(1)
            # -- transcript = mo.group(2)
            # -- strand = mo.group(3)
            # -- offset = mo.group(4)

            # set the remaining data
            # -- instrument = f'___{fragment}___{transcript}___{strand}___{offset}___'
            flowcell = f'{fragment}'
            x_pos = y_pos = fragment

            # write the fixed sequence identifier record
            fixed_readfile_id.write(f'@{instrument}:{run}:{flowcell}:{lane}:{tile}:{x_pos}:{y_pos} {filenum}:{is_filtered}:{control}:{index}\n')

        else:
            # control the FASTQ format
            raise xlib.ProgramException('', 'F006', fixed_readfile, 'FASTQ')

        # read next record and process the sequence record
        record = readfile_id.readline()
        if record != '':
            fixed_readfile_id.write(record)
        else:
            # control the FASTQ format
            raise xlib.ProgramException('', 'F006', readfile, 'FASTQ')

        # read next record and process quality score identifier record
        record = readfile_id.readline()
        if record.startswith('+'):
            fixed_readfile_id.write(record)
        else:
            # control the FASTQ format
            raise xlib.ProgramException('', 'F006', readfile, 'FASTQ')

        # read next record and process quality score record
        record = readfile_id.readline()
        if record != '':
            fixed_readfile_id.write(record)
        else:
            # control the FASTQ format
            raise xlib.ProgramException('', 'F006', readfile, 'FASTQ')

        # read the next record
        record = readfile_id.readline()

    # close files
    readfile_id.close()
    fixed_readfile_id.close()

    # show OK message
    xlib.Message.print('info', f'The file {fixed_readfile} with cut reads is created.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
