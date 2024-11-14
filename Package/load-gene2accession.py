#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program loads the accessions that are related to a GeneID into a SQLite database.

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

    # load the accessions that are related to a GeneID into the database of gymnoTOA
    load_gene2accession(conn, args.relationship_file, args.top_node_taxid)

    # close connection to gymnoTOA database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program loads the accessions that are related to a GeneID\n' \
       'into a SQLite database.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--relfile', dest='relationship_file', help='Path of the relationship file (mandatory).')
    parser.add_argument('--topnode', dest='top_node_taxid', help='Taxid of the top node whose species are considered (mandatory).')
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

    # check "relationship_file"
    if args.relationship_file is None:
        xlib.Message.print('error', '*** The input relationship file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.relationship_file):
        xlib.Message.print('error', f'*** The file {args.relationship_file} does not exist.')
        OK = False

    # check "top_node_taxid"
    if args.top_node_taxid is None:
        xlib.Message.print('error', '*** The taxid of the top node is not indicated in the input arguments.')
        OK = False
    elif not xlib.check_int(args.top_node_taxid, minimum=1):
        xlib.Message.print('error', 'The taxid of the top node has to be an integer number greater than or equal to 1.')
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

def load_gene2accession(conn, relationship_file, top_node_taxid):
    '''
    Load the accessions that are related to a GeneID into the database of
    gymnoTOA (Gymnosperms Taxonomy-oriented Annotation).
    '''

    # get the taxid list of species depending on the top node
    species_taxid_list = []
    xsqlite.get_species_taxid_list(conn, [top_node_taxid], species_taxid_list)
    species_taxid_list.sort(key=int)
    xlib.Message.print('verbose', f'species_taxid_list: {species_taxid_list}\n')
    xlib.Message.print('verbose', f'len(species_taxid_list): {len(species_taxid_list)}\n')

    # drop the table "gene2accession" (if it exists)
    xlib.Message.print('verbose', 'Droping the table "gene2accession" ...\n')
    xsqlite.drop_gene2accession(conn)
    xlib.Message.print('verbose', 'The table is droped.\n')

    # create the table "gene2accession"
    xlib.Message.print('verbose', 'Creating the table "gene2accession" ...\n')
    xsqlite.create_gene2accession(conn)
    xlib.Message.print('verbose', 'The table is created.\n')

    # initialize the record counter
    record_counter = 0

    # initialize the inserted row counter
    inserted_row_counter = 0

    # open the relationship file
    if relationship_file.endswith('.gz'):
        try:
            relationship_file_id = gzip.open(relationship_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F002', relationship_file)
    else:
        try:
            relationship_file_id = open(relationship_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise xlib.ProgramException(e, 'F001', relationship_file)

    # read the first record
    record = relationship_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to record counter
        record_counter += 1

        # process data records
        if record_counter > 1:

            # initialize the row data dictionary
            row_dict = {}

            # extract data
            # record format: tax_id <field_sep> gene_id <field_sep> status <field_sep> rna_nucleotide_accession_version <field_sep> rna_nucleotide_gi <field_sep> protein_accession_version <field_sep> protein_gi <field_sep> genomic_nucleotide_accession_version <field_sep> genomic_nucleotide_gi <field_sep> start_position_on_the_genomic_accession <field_sep> end_position_on_the_genomic_accession <field_sep> orientation <field_sep> assembly <field_sep> mature_peptide_accession_version <field_sep> mature_peptide_gi <field_sep> symbol <record_sep>
            field_sep = '\t'
            record_sep = '\n'
            data_list = re.split(field_sep, record.replace(record_sep,''))
            try:
                row_dict['tax_id'] = data_list[0].strip()
                row_dict['gene_id'] = data_list[1].strip()
                row_dict['protein_accession_version'] = data_list[5].strip()
            except Exception as e:
                raise xlib.ProgramException(e, 'F009', os.path.basename(relationship_file), record_counter)

            # check "tax_id"
            try:
                int(row_dict['tax_id'])
            except Exception as e:
                raise xlib.ProgramException(e, 'D001', 'tax_id', os.path.basename(relationship_file), record_counter)

            # insert data into the table "gene2accession" if the taxid is in the taxid_list
            if row_dict['tax_id'] in species_taxid_list and row_dict['protein_accession_version'] != '-':
                xsqlite.insert_gene2accession_row(conn, row_dict)
                inserted_row_counter += 1

        # print counters
        xlib.Message.print('verbose', f'\rrelationship file: {record_counter} processed records - Inserted rows: {inserted_row_counter}')

        # read the next record
        record = relationship_file_id.readline()

    xlib.Message.print('verbose', '\n')

    # create the index "gene2accession_index_1" on the table "gene2accession"
    xlib.Message.print('verbose', 'Creating the index 1 on the table "gene2accession" ...\n')
    xsqlite.create_gene2accession_index_1(conn)
    xlib.Message.print('verbose', 'The index is created.\n')

    # save changes into SQLite database
    xlib.Message.print('verbose', 'Saving changes into the SQLite database ...\n')
    conn.commit()
    xlib.Message.print('verbose', 'Changes are saved.\n')

    # close relationship file
    relationship_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
