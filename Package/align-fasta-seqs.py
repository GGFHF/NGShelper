#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=unnecessary-pass

#-------------------------------------------------------------------------------

'''
This program aligns a FASTA sequence file using the MAFFT aligner and plots the
alignment using pyMSAviz. Besides, it generates and plots the phylogenetic tree.

WARNING: The MAFFT software must be installed and accessible.

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
import os
import shutil
import subprocess
import sys

from Bio import Phylo

import matplotlib
import matplotlib.pyplot as plt
from pymsaviz import MsaViz

import xlib

matplotlib.use('Agg')

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

    # align the FASTA sequence file and plot the alignment
    align_fasta_seqs(args.fasta_seq_file, args.tree_generation)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program aligns a FASTA sequence file using the MAFFT aligner and\n' \
       'plots the alignment using pyMSAviz. Besides, it generates and plots the phylogenetic tree.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    # pylint: disable=protected-access
    parser.add_argument('--seqs', dest='fasta_seq_file', help='Path of the FASTA sequence file (mandatory).')
    parser.add_argument('--tree', dest='tree_generation', help=f'Generation and plot of the the guide tree: {xlib.get_yn_code_list_text()}; default: {xlib.Const.DEFAULT_TREE_GENERATION}.')
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

    # check "fasta_seq_file"
    if args.fasta_seq_file is None:
        xlib.Message.print('error', '*** The FASTA sequence file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.fasta_seq_file):
        xlib.Message.print('error', f'*** The file {args.fasta_seq_file} does not exist.')
        OK = False

    # check "tree_generation"
    if args.tree_generation is None:
        args.tree_generation = xlib.Const.DEFAULT_TREE_GENERATION
    elif not xlib.check_code(args.tree_generation, xlib.get_yn_code_list(), case_sensitive=False):
        xlib.Message.print('error', f'*** tree has to be {xlib.get_yn_code_list_text()}.')
        OK = False
    if args.tree_generation.upper() == 'Y':
        xlib.Message.set_verbose_status(True)

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

def align_fasta_seqs(fasta_seq_file, tree_generation):
    '''
    Align a FASTA sequence file using the MAFFT aligner and plot the alignment using pyMSAviz.
    Besides, generate and plot the phylogenetic tree.
    '''

    # get the sequence number in the FASTA sequence file
    with open(fasta_seq_file, 'r', encoding='iso-8859-1') as fasta_seq_file_id:
        record_count = sum(1 for _ in fasta_seq_file_id)
    seq_number = record_count / 2

    # run sequence alignment
    alignment_file = f'{fasta_seq_file}.aln'
    if seq_number > 1:
        xlib.Message.print('info', f'Aligning sequences in {alignment_file} ...')
        with open(alignment_file, mode='w', encoding='iso-8859-1') as alignment_file_id:
            result = subprocess.run(['mafft', '--auto', '--anysymbol', fasta_seq_file], stdout=alignment_file_id, stderr=subprocess.PIPE, text=True, check=True)
        if result.returncode == 0:
            xlib.Message.print('info', 'The alignment is done.')
        else:
            raise xlib.ProgramException('', 'M001', 'mafft', result.stderr)
    else:
        xlib.Message.print('info', f'The file {fasta_seq_file} has only one record. Copying this file in {alignment_file} ...')
        shutil.copy(fasta_seq_file, alignment_file)
        xlib.Message.print('info', 'The copy is done.')

    # plot the sequence alignment using pyMSAviz
    alignment_plot_file = f'{fasta_seq_file}.aln.pdf'
    try:
        xlib.Message.print('info', 'Plotting the alignment ...')
        alignment_plot = MsaViz(alignment_file, format='fasta', wrap_length=80, sort=False, color_scheme='Flower', show_count=True, show_consensus=False)
        alignment_plot.savefig(alignment_plot_file)
        xlib.Message.print('info', 'Plot is done.')
    except Exception as e:
        raise xlib.ProgramException(e, 'M001', 'pymsaviz', e)

    # when the guide tree must be generated
    if tree_generation  == 'Y':

        # when there is more than one FASTA sequence
        if seq_number > 1:

            # generate the guide tree represents the clustering of sequences in Newick format
            xlib.Message.print('info', 'Generating the guide tree ...')
            result = subprocess.run(['mafft', '--treeout', fasta_seq_file], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=True)
            if result.returncode == 0:
                xlib.Message.print('info', 'The generation is done.')
            else:
                raise xlib.ProgramException('', 'M001', 'mafft', result.stderr)

            # plot the guide tree
            tree = Phylo.read(f'{fasta_seq_file}.tree', 'newick')
            Phylo.draw(tree, do_show=False)
            tree_plot_file = f'{fasta_seq_file}.tree.pdf'
            plt.savefig(tree_plot_file)
            plt.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
