#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This source contains functions for the maintenance of the NGShelper SQLite databases
used in both console mode and gui mode.

This software has been developed by:

    GI en Especies Leñosas (WooSp)
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

import math
import sqlite3
import sys

import xlib

#-------------------------------------------------------------------------------

def connect_database(database_path, check_same_thread=True):
    '''
    Connect to the database.
    '''

    # connet to the database
    try:
        conn = sqlite3.connect(database_path, check_same_thread=check_same_thread)
    except Exception as e:
        raise xlib.ProgramException(e, 'B001', database_path)

    # return the connection
    return conn

#-------------------------------------------------------------------------------

def rebuild_database(conn):
    '''
    Rebuild the database file.
    '''

    # initialize the control variable
    OK = True

    # rebuild
    sentence = 'VACUUM'
    try:
        conn.execute(sentence)
    except Exception as e:
        xlib.Message.print('error', f'*** WARNING: {e}')
        OK = False

    # return the control variable
    return OK

#-------------------------------------------------------------------------------
# table "gene_info"
# (see https://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/*)
#-------------------------------------------------------------------------------

def drop_gene_info(conn):
    '''
    Drop the table "gene_info" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS gene_info;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_gene_info(conn):
    '''
    Create the table "gene_info".
    '''

    sentence = '''
               CREATE TABLE gene_info (
                   gene_id     TEXT NOT NULL,
                   tax_id      TEXT NOT NULL,
                   symbol      TEXT NOT NULL,
                   description TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_gene_info_index_1(conn):
    '''
    Create the unique index "gene_info_index_1" with the column "gene_id" on the table "gene_info"
    '''

    sentence = '''
               CREATE UNIQUE INDEX gene_info_index_1
                   ON gene_info (gene_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_gene_info_index_2(conn):
    '''
    Create the index "gene_info_index_2" with the column "symbol" on the table "gene_info"
    '''

    sentence = '''
               CREATE INDEX gene_info_index_2
                   ON gene_info (symbol);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_gene_info_row(conn, row_dict):
    '''
    Insert a row into table "gene_info"
    '''

    sentence = f'''
                INSERT INTO gene_info
                    (gene_id, tax_id, symbol, description)
                    VALUES ('{row_dict["gene_id"]}', '{row_dict["tax_id"]}', '{row_dict["symbol"]}', '{row_dict["description"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_gene_info(conn):
    '''
    Check if table "gene_info exists and if there are rows.
    '''

    # check if table "gene_info" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'gene_info'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "gene_info" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM gene_info
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------
# table "gene2accession"
# (see https://ftp.ncbi.nih.gov/gene/DATA/gene2accession.gz)
#-------------------------------------------------------------------------------

def drop_gene2accession(conn):
    '''
    Drop the table "gene2accession" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS gene2accession;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_gene2accession(conn):
    '''
    Create the table "gene2accession".
    '''

    sentence = '''
               CREATE TABLE gene2accession (
                   tax_id                    TEXT NOT NULL,
                   gene_id                   TEXT NOT NULL,
                   protein_accession_version TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_gene2accession_index_1(conn):
    '''
    Create the index "gene2accession_index_1" with the column "protein_accession_version" on the table "gene2accession"
    '''

    sentence = '''
               CREATE INDEX gene2accession_index_1
                   ON gene2accession (protein_accession_version);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_gene2accession_row(conn, row_dict):
    '''
    Insert a row into table "gene2accession"
    '''

    sentence = f'''
                INSERT INTO gene2accession
                    (tax_id, gene_id, protein_accession_version)
                    VALUES ('{row_dict["tax_id"]}', '{row_dict["gene_id"]}', '{row_dict["protein_accession_version"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_gene2accession(conn):
    '''
    Check if table "gene2accession" exists and if there are rows.
    '''

    # check if table "gene2accession" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'gene2accession'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "gene2accession" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM gene2accession
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------
# table "gene2go"
# (see https://ftp.ncbi.nih.gov/gene/DATA/gene2accession.gz)
#-------------------------------------------------------------------------------

def drop_gene2go(conn):
    '''
    Drop the table "gene2go" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS gene2go;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_gene2go(conn):
    '''
    Create the table "gene2go".
    '''

    sentence = '''
               CREATE TABLE gene2go (
                   tax_id  TEXT NOT NULL,
                   gene_id TEXT NOT NULL,
                   go_id   TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_gene2go_index_1(conn):
    '''
    Create the index "gene2go_index_1" with the columns "tax_id" and "gene_id" on the table "gene2go"
    '''

    sentence = '''
               CREATE INDEX gene2go_index_1
                   ON gene2go (tax_id, gene_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_gene2go_row(conn, row_dict):
    '''
    Insert a row into table "gene2go"
    '''

    sentence = f'''
                INSERT INTO gene2go
                    (tax_id, gene_id, go_id)
                    VALUES ('{row_dict["tax_id"]}', '{row_dict["gene_id"]}', '{row_dict["go_id"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_gene2go(conn):
    '''
    Check if table "gene2go" exists and if there are rows.
    '''

    # check if table "gene2go" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'gene2go'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "gene2go" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM gene2go
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------
# table "gene_orthologs"
# (https://ftp.ncbi.nih.gov/gene/DATA/gene_orthologs.gz)
#-------------------------------------------------------------------------------

def drop_gene_orthologs(conn):
    '''
    Drop the table "gene_orthologs" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS gene_orthologs;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_gene_orthologs(conn):
    '''
    Create the table "gene_orthologs".
    '''

    sentence = '''
               CREATE TABLE gene_orthologs (
                   tax_id        TEXT NOT NULL,
                   gene_id       TEXT NOT NULL,
                   other_tax_id  TEXT NOT NULL,
                   other_gene_id TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_gene_orthologs_index_1(conn):
    '''
    Create the index "gene_orthologs_index_1" with the columns "tax_id" and "gene_id" on the table "gene_orthologs"
    '''

    sentence = '''
               CREATE INDEX gene_orthologs_index_1
                   ON gene_orthologs (tax_id, gene_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_gene_orthologs_index_2(conn):
    '''
    Create the index "gene_orthologs_index_2" with the columns "other_tax_id" and "other_gene_id" on the table "gene_orthologs"
    '''

    sentence = '''
               CREATE INDEX gene_orthologs_index_2
                   ON gene_orthologs (other_tax_id, other_gene_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_gene_orthologs_row(conn, row_dict):
    '''
    Insert a row into table "gene_orthologs"
    '''

    sentence = f'''
                INSERT INTO gene_orthologs
                    (tax_id, gene_id, other_tax_id, other_gene_id)
                    VALUES ('{row_dict["tax_id"]}', '{row_dict["gene_id"]}', '{row_dict["other_tax_id"]}', '{row_dict["other_gene_id"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_gene_orthologs(conn):
    '''
    Check if table "gene_orthologs" exists and if there are rows.
    '''

    # check if table "gene_orthologs" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'gene_orthologs'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "gene_orthologs" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM gene_orthologs
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------
# table "taxonomy_nodes"
# (https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip, nodes.dmp)
#-------------------------------------------------------------------------------

def drop_taxonomy_nodes(conn):
    '''
    Drop the table "taxonomy_nodes" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS taxonomy_nodes;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_taxonomy_nodes(conn):
    '''
    Create the table "taxonomy_nodes".
    '''

    sentence = '''
               CREATE TABLE taxonomy_nodes (
                   tax_id        TEXT NOT NULL,
                   parent_tax_id TEXT NOT NULL,
                   rank          TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_taxonomy_nodes_index_1(conn):
    '''
    Create the unique index "taxonomy_nodes_index_1" with the column "tax_id" on the table "taxonomy_nodes"
    '''

    sentence = '''
               CREATE UNIQUE INDEX taxonomy_nodes_index_1
                   ON taxonomy_nodes (tax_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_taxonomy_nodes_index_2(conn):
    '''
    Create the index "taxonomy_nodes_index_2" with the column "parent tax_id" on the table "taxonomy_nodes"
    '''

    sentence = '''
               CREATE INDEX taxonomy_nodes_index_2
                   ON taxonomy_nodes (parent_tax_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_taxonomy_nodes_row(conn, row_dict):
    '''
    Insert a row into table "taxonomy_nodes"
    '''

    sentence = f'''
                INSERT INTO taxonomy_nodes
                    (tax_id, parent_tax_id, rank)
                    VALUES ('{row_dict["tax_id"]}', '{row_dict["parent_tax_id"]}', '{row_dict["rank"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_taxonomy_nodes(conn):
    '''
    Check if table "taxonomy_nodes" exists and if there are rows.
    '''

    # check if table "taxonomy_nodes" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'taxonomy_nodes'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "taxonomy_nodes" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM taxonomy_nodes
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_taxid_data(conn, tax_id):
    '''
    Get row data from the table "taxonomy_nodes" for a tax_id.
    '''

    # initialize the sequence feature dictionary
    node_data_dict = {}

    # select rows from the table "taxonomy_nodes"
    sentence = f'''
                SELECT tax_id, parent_tax_id, rank
                    FROM taxonomy_nodes
                    WHERE tax_id = '{tax_id}';
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException('B002', e, sentence, conn)

    # add row data to the dictionary
    for row in rows:
        node_data_dict = {'tax_id': row[0], 'parent_tax_id': row[1], 'rank': row[2]}
        break

    # return the sequence feature dictionary
    return node_data_dict

#-------------------------------------------------------------------------------

def get_node_data_dict(conn, parent_tax_id):
    '''
    Get row data from the table "taxonomy_nodes" for a parent taxid.
    '''

    # initialize the sequence feature dictionary
    node_data_dict = {}

    # initialize the dictionary key
    key = 0

    # select rows from the table "taxonomy_nodes"
    sentence = f'''
                SELECT tax_id, parent_tax_id, rank
                    FROM taxonomy_nodes
                    WHERE parent_tax_id = '{parent_tax_id}';
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException('B002', e, sentence, conn)

    # add row data to the dictionary
    for row in rows:
        node_data_dict[key] = {'tax_id': row[0], 'parent_tax_id': row[1], 'rank': row[2]}
        key += 1

    # return the sequence feature dictionary
    return node_data_dict

#-------------------------------------------------------------------------------

def get_species_taxid_list(conn, old_parent_taxid_list, species_taxid_list):
    '''
    Get the taxid list of species depending on the parent taxid list using a
    recusive process.
    '''

    # initialize the new parent taxid list
    new_parent_taxid_list = []

    # for each taxid in the old parent taxid list
    for old_parent_taxid in old_parent_taxid_list:

        # get the data for the nodes with the parent taxid that is being processed
        node_data_dict = get_node_data_dict(conn, old_parent_taxid)
        for _, value in node_data_dict.items():
            if value['rank'] == 'species':
                species_taxid_list.append(value['tax_id'])
            else:
                new_parent_taxid_list.append(value['tax_id'])

    # process the next nodes if necessary
    if  len(new_parent_taxid_list) > 0:
        # the next node sequence data
        get_species_taxid_list(conn, new_parent_taxid_list, species_taxid_list)

    # return to end the resusive process of the node
    return

#-------------------------------------------------------------------------------

def get_taxonomy_dict(conn, species_name):
    '''
    Get the taxonomy dictionary of a species tax_id corresponding to a species name.
    '''

    # initialize the taxonomy dictionary
    taxonomy_dict = {}

    # get the species tax_id
    tax_id = get_species_taxid(conn, species_name)

    # initialize name of nodes
    family_name = xlib.get_na()
    phylum_name = xlib.get_na()
    kingdom_name = xlib.get_na()
    superkingdom_name = xlib.get_na()
    tax_id_list = []

    # get data of tax_id
    node_data_dict = get_taxid_data(conn, tax_id)

    # check the tax_id corresponding to a species
    if node_data_dict and node_data_dict['rank'] == 'species':

        # traverse the nodes
        while node_data_dict['tax_id'] != '1':

            # add tax_id to tax_id list
            tax_id_list.append(node_data_dict['tax_id'])

            # set the node data to the maily, phylum, kingdom and suyperkingdom
            if node_data_dict['rank'] == 'family':
                species_data_dict = get_species_data_dict(conn, node_data_dict['tax_id'])
                family_name = species_data_dict['name_txt']
            elif node_data_dict['rank'] == 'phylum':
                species_data_dict = get_species_data_dict(conn, node_data_dict['tax_id'])
                phylum_name = species_data_dict['name_txt']
            elif node_data_dict['rank'] == 'kingdom':
                species_data_dict = get_species_data_dict(conn, node_data_dict['tax_id'])
                kingdom_name = species_data_dict['name_txt']
            elif node_data_dict['rank'] == 'superkingdom':
                species_data_dict = get_species_data_dict(conn, node_data_dict['tax_id'])
                superkingdom_name = species_data_dict['name_txt']

            # get data of tax_id of the next parent node
            node_data_dict = get_taxid_data(conn, node_data_dict['parent_tax_id'])

        # build the taxonomy dictionary
        taxonomy_dict = {'tax_id': tax_id, 'tax_id_list': tax_id_list, 'family_name': family_name, 'phylum_name': phylum_name, 'kingdom_name': kingdom_name, 'superkingdom_name': superkingdom_name}

    # return the taxonomy dictionary
    return taxonomy_dict

#-------------------------------------------------------------------------------
# table "species_names"
# (https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip, names.dmp)
#-------------------------------------------------------------------------------

def drop_species_names(conn):
    '''
    Drop the table "species_names" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS species_names;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_species_names(conn):
    '''
    Create the table "species_names".
    '''

    sentence = '''
               CREATE TABLE species_names (
                   tax_id      TEXT NOT NULL,
                   name_class  TEXT NOT NULL,
                   name_txt    TEXT NOT NULL,
                   unique_name TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_species_names_index_1(conn):
    '''
    Create the index "species_names_index_1" with the column "tax_id" on the table "species_names"
    '''

    sentence = '''
               CREATE INDEX species_names_index_1
                   ON species_names (tax_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_species_names_index_2(conn):
    '''
    Create the index "species_names_index_2" with the column "name_class" on the table "species_names"
    '''

    sentence = '''
               CREATE INDEX species_names_index_2
                   ON species_names (name_class);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_species_names_row(conn, row_dict):
    '''
    Insert a row into table "species_names"
    '''

    sentence = f'''
                INSERT INTO species_names
                    (tax_id, name_class, name_txt, unique_name)
                    VALUES ('{row_dict["tax_id"]}', '{row_dict["name_class"]}', '{row_dict["name_txt"]}', '{row_dict["unique_name"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_species_names(conn):
    '''
    Check if table "species_names" exists and if there are rows.
    '''

    # check if table "species_names" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'species_names'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "species_names" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM species_names
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_species_data_dict(conn, tax_id):
    '''
    Get the species data dictionary corresponding to a tax_id.
    '''

    # initialize the species data dictionary
    species_data_dict = {}

    # select rows from the table "species_name"
    sentence = f'''
                SELECT tax_id, name_class, name_txt, unique_name
                    FROM species_names
                    WHERE tax_id = '{tax_id}'
                      AND name_class = 'scientific name';
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException('B002', e, sentence, conn)

    # add row data to the dictionary
    for row in rows:
        species_data_dict = {'tax_id': row[0], 'name_class': row[1], 'name_txt': row[2], 'unique_name': row[3]}
        break

    # return the species data dictionary
    return species_data_dict

#-------------------------------------------------------------------------------

def get_species_taxid(conn, species_name):
    '''
    Get the species tax_id corresponding to a species name.
    '''

    # initialize the tax_id
    tax_id = ''

    # select rows from the table "species_name"
    sentence = f'''
                SELECT tax_id
                    FROM species_names
                    WHERE name_class = 'scientific name'
                      AND name_txt = '{species_name}';
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException('B002', e, sentence, conn)

    # add row data to the dictionary
    for row in rows:
        tax_id = row[0]
        break

    # return the sequence feature dictionary
    return tax_id

#-------------------------------------------------------------------------------
# table "protaccession2taxid"
# (https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/prot.accession2taxid.gz)
#-------------------------------------------------------------------------------

def drop_protaccession2taxid(conn):
    '''
    Drop the table "protaccession2taxid" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS protaccession2taxid;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_protaccession2taxid(conn):
    '''
    Create the table "protaccession2taxid".
    '''

    sentence = '''
               CREATE TABLE protaccession2taxid (
                   protein_accession_version TEXT NOT NULL,
                   tax_id                    TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_protaccession2taxid_index_1(conn):
    '''
    Create the unique index "protaccession2taxid_index_1" with the column "protein_accession_version" on the table "protaccession2taxid"
    '''

    sentence = '''
               CREATE UNIQUE INDEX protaccession2taxid_index_1
                   ON protaccession2taxid (protein_accession_version);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_protaccession2taxid_index_2(conn):
    '''
    Create the index "protaccession2taxid_index_2" with the column "tax_id" on the table "protaccession2taxid"
    '''

    sentence = '''
               CREATE INDEX protaccession2taxid_index_2
                   ON protaccession2taxid (tax_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_protaccession2taxid_row(conn, row_dict):
    '''
    Insert a row into table "protaccession2taxid"
    '''

    sentence = f'''
                INSERT INTO protaccession2taxid
                    (protein_accession_version, tax_id)
                    VALUES ('{row_dict["protein_accession_version"]}', '{row_dict["tax_id"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_protaccession2taxid(conn):
    '''
    Check if table "protaccession2taxid" exists and if there are rows.
    '''

    # check if table "protaccession2taxid" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'protaccession2taxid'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "protaccession2taxid" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM protaccession2taxid
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------
# table "go_ontology"
# (see https://purl.obolibrary.org/obo/go.obo)
#-------------------------------------------------------------------------------

def drop_go_ontology(conn):
    '''
    Drop the table "go_ontology" (if it exists).
    '''

    sentence = '''
               DROP TABLE IF EXISTS go_ontology;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException('B002', e, sentence, conn)

#-------------------------------------------------------------------------------

def create_go_ontology(conn):
    '''
    Create the table "go_ontology".
    '''

    sentence = '''
               CREATE TABLE go_ontology (
                   go_id         TEXT NOT NULL,
                   go_name       TEXT NOT NULL,
                   namespace     TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException('B002', e, sentence, conn)

#-------------------------------------------------------------------------------

def create_go_ontology_index(conn):
    '''
    Create the index "go_ontology_index" with the column "go_id" on the table "go_ontology".
    '''

    sentence = '''
               CREATE INDEX go_ontology_index
                   ON go_ontology (go_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException('B002', e, sentence, conn)

#-------------------------------------------------------------------------------

def insert_go_ontology_row(conn, row_dict):
    '''
    Insert a row into table "go_ontology".
    '''

    sentence = f'''
                INSERT INTO go_ontology
                    (go_id, go_name, namespace)
                    VALUES ('{row_dict["go_id"]}', '{row_dict["go_name"]}', '{row_dict["namespace"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException('B002', e, sentence, conn)

#-------------------------------------------------------------------------------

def check_go_ontology(conn):
    '''
    Check if table "go_ontology" exists and if there are rows.
    '''

    # check if table "go_ontology" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'go_ontology'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException('B002', e, sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "go_ontology" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM go_ontology
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException('B002', e, sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_go_ontology_dict(conn, go_id_list):
    '''
    Get a dictionary of ontology from the table "go_ontology".
    '''

    # initialize the ontology dictionary
    go_onlology_dict = {}

    # select rows from the table "go_ontology"
    if go_id_list == []:
        sentence = '''
                   SELECT DISTINCT go_id, go_name, namespace
                       FROM go_ontology;
                   '''
    else:
        sentence = f'''
                    SELECT DISTINCT go_id, go_name, namespace
                        FROM go_ontology
                        WHERE go_id in ({xlib.join_string_list_to_string(go_id_list)});
                    '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException('B002', e, sentence, conn)

    # add ontology data to the dictionary
    for row in rows:
        go_onlology_dict[row[0]] = {'go_id':row[0], 'go_name':row[1], 'namespace':row[2]}

    # return the ontology dictionary
    return go_onlology_dict

#-------------------------------------------------------------------------------
# table "genomic_features"
#-------------------------------------------------------------------------------

def drop_genomic_features(conn):
    '''
    Drop the table "genomic_features" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS genomic_features;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------
def create_genomic_features(conn):
    '''
    Create table "genomic_features".
    '''

    sentence = '''
               CREATE TABLE genomic_features (
                   seq_id TEXT NOT NULL,
                   start  INTEGER NOT NULL,
                   end    INTEGER NOT NULL,
                   type   TEXT NOT NULL,
                   gene   TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_genomic_features_index(conn):
    '''
    Create the index "genomic_features_index" (if it does not exist) with the column "seq_id" on the table "genomic_features".
    '''

    sentence = '''
               CREATE INDEX genomic_features_index
                   ON genomic_features (seq_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_genomic_features_row(conn, row_dict):
    '''
    Insert a row into table "genomic_features".
    '''

    sentence = f'''
                INSERT INTO genomic_features
                    (seq_id, start, end, type, gene)
                    VALUES ('{row_dict["seq_id"]}', {row_dict["start"]}, {row_dict["end"]}, '{row_dict["type"]}', '{row_dict["gene"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_genomic_features(conn):
    '''
    Check if table "genomic_features" exists and if there are rows.
    '''

    # check if table "genomic_features" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'genomic_features'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "genomic_features" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM genomic_features
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_genomic_feature_dict(conn, transcript_seq_id, transcript_start, transcript_end):
    '''
    Get a sequence feature dictionary from the table "genomic_features" corresponding to a sequence identification and its start less than or equal to the transcript start.
    '''

    # initialize the sequence feature dictionary
    genomic_feature_dict = {}

    # initialize the dictionary key
    key = 0

    # select rows from the table "genomic_features"
    sentence = f'''
                SELECT seq_id, start, end, type, gene
                    FROM genomic_features
                    WHERE seq_id = "{transcript_seq_id}"
                      AND start <= {transcript_start}
                      AND end >= {transcript_end};
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        genomic_feature_dict[key] = {'seq_id': row[0], 'start': row[1], 'end': row[2], 'type': row[3], 'gene': row[4]}
        key += 1

    # return the sequence feature dictionary
    return genomic_feature_dict

#-------------------------------------------------------------------------------
# table "annotations"
#-------------------------------------------------------------------------------

def drop_annotations(conn):
    '''
    Drop the table "annotations" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS annotations;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_annotations(conn):
    '''
    Create table "annotations".
    '''

    sentence = '''
               CREATE TABLE annotations (
                   seq_id      TEXT NOT NULL,
                   description TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_annotations_index(conn):
    '''
    Create the index "annotations_index" (if it does not exist) with the column "seq_id" on the table "annotations".
    '''

    sentence = '''
               CREATE INDEX annotations_index
                   ON annotations (seq_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_annotations_row(conn, row_dict):
    '''
    Insert a row into table "annotations".
    '''

    sentence = f'''
                INSERT INTO annotations
                    (seq_id, description)
                    VALUES ('{row_dict["seq_id"]}', '{row_dict["description"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_annotations(conn):
    '''
    Check if table "annotations" exists and if there are rows.
    '''

    # check if table "annotations" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'annotations'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "annotations" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM annotations
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------
# table "alignments"
#-------------------------------------------------------------------------------

def drop_alignments(conn):
    '''
    Drop the table "alignments" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS alignments;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------
def create_alignments(conn):
    '''
    Create table "alignments".
    '''

    sentence = '''
               CREATE TABLE alignments (
                   variant_id    TEXT NOT NULL,
                   chromosome_id TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_alignments_index(conn):
    '''
    Create the index "alignments_index" (if it does not exist) with the column "variant_id" on the table "alignments".
    '''

    sentence = '''
               CREATE INDEX alignments_index
                   ON alignments (variant_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_alignments_row(conn, row_dict):
    '''
    Insert a row into table "alignments".
    '''

    sentence = f'''
                INSERT INTO alignments
                    (variant_id, chromosome_id)
                    VALUES ('{row_dict["variant_id"]}', '{row_dict["chromosome_id"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_alignments(conn):
    '''
    Check if table "alignments" exists and if there are rows.
    '''

    # check if table "alignments" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'alignments'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "alignments" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM alignments
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------
# table "vcf_samples"
#-------------------------------------------------------------------------------

def drop_vcf_samples(conn):
    '''
    Drop the table "vcf_samples" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS vcf_samples;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_samples(conn):
    '''
    Create the table "vcf_samples".
    '''

    sentence = '''
               CREATE TABLE vcf_samples (
                   sample_id  TEXT NOT NULL,
                   species_id TEXT NOT NULL,
                   mother_id  TEXT NOT NULL,
                   type       TEXT NOT NULL,
                   colnum     INTEGER NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_samples_index(conn):
    '''
    Create the unique index "vcf_samples_index" with the column "sample_id" on the table "vcf_samples"
    '''

    sentence = '''
               CREATE UNIQUE INDEX vcf_samples_index
                   ON vcf_samples (sample_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_vcf_samples_row(conn, row_dict):
    '''
    Insert a row into table "vcf_samples"
    '''

    sentence = f'''
                INSERT INTO vcf_samples
                    (sample_id, species_id, mother_id, type, colnum)
                    VALUES ('{row_dict["sample_id"]}', '{row_dict["species_id"]}', '{row_dict["mother_id"]}', '{row_dict["type"]}', {row_dict["colnum"]});
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def update_vcf_samples_row(conn, sample_id, type):
    '''
    Insert a row into table "vcf_samples"
    '''

    sentence = f'''
                UPDATE vcf_samples
                    SET type = '{type}'
                    WHERE sample_id = '{sample_id}';
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_vcf_samples(conn):
    '''
    Check if table "vcf_samples" exists and if there are rows.
    '''

    # check if table "vcf_samples" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'vcf_samples'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "vcf_samples" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM vcf_samples
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_sample_type_dict(conn):
    '''
    Get a dictionary with the type corresponding to samples.
    '''

    # initialize the dictionary
    sample_type_dict = xlib.NestedDefaultDict()

    # query
    sentence = '''
               SELECT a.sample_id, 'PROGENY' "type"
                  FROM vcf_samples a
                  WHERE a.mother_id != 'NONE'
               UNION
               SELECT b.sample_id, 'MOTHER' "type"
                  FROM vcf_samples b
                  WHERE b.sample_id IN (SELECT DISTINCT c.mother_id FROM  vcf_samples c)
               UNION
               SELECT d.sample_id, 'ADULT' "type"
                  FROM vcf_samples d
                  WHERE d.mother_id == 'NONE'
                    AND d.sample_id NOT IN (SELECT DISTINCT e.mother_id FROM  vcf_samples e)
               ORDER BY 1;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        sample_type_dict[row[0]] = {'sample_id': row[0], 'type': row[1]}

    # return the dictionary
    return sample_type_dict

#-------------------------------------------------------------------------------
# table "vcf_variants"
#-------------------------------------------------------------------------------

def drop_vcf_variants(conn):
    '''
    Drop the table "vcf_variants" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS vcf_variants;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_variants(conn):
    '''
    Create the table "vcf_variants".
    '''

    sentence = '''
               CREATE TABLE vcf_variants (
                   variant_id          TEXT NOT NULL,
                   seq_id              TEXT NOT NULL,
                   position            INTEGER NOT NULL,
                   reference_bases     TEXT NOT NULL,
                   alternative_alleles TEXT NOT NULL,
                   variant_type        TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_variants_index(conn):
    '''
    Create the unique index "vcf_variants_index" with the column "variant_id" on the table "vcf_variants"
    '''

    sentence = '''
               CREATE UNIQUE INDEX vcf_variants_index
                   ON vcf_variants (variant_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_vcf_variants_row(conn, row_dict):
    '''
    Insert a row into table "vcf_variants"
    '''

    sentence = f'''
                INSERT INTO vcf_variants
                    (variant_id, seq_id, position, reference_bases, alternative_alleles, variant_type)
                    VALUES ('{row_dict["variant_id"]}', '{row_dict["seq_id"]}', {row_dict["position"]}, '{row_dict["reference_bases"]}',
                            '{row_dict["alternative_alleles"]}', '{row_dict["variant_type"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_vcf_variants(conn):
    '''
    Check if table "vcf_variants exists and if there are rows.
    '''

    # check if table "vcf_variants" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'vcf_variants'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "vcf_variants" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM vcf_variants
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------
# table "vcf_alleles"
#-------------------------------------------------------------------------------

def drop_vcf_alleles(conn):
    '''
    Drop the table "vcf_alleles" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS vcf_alleles;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_alleles(conn):
    '''
    Create the table "vcf_alleles".
    '''

    sentence = '''
               CREATE TABLE vcf_alleles (
                   variant_id          TEXT  NOT NULL,
                   allele_id           TEXT NOT NULL,
                   bases               TEXT NOT NULL,
                   structure_allele_id TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_alleles_index(conn):
    '''
    Create the unique index "vcf_alleles_index" with thes column "variant_id", "allele_id" on the table "vcf_alleles"
    '''

    sentence = '''
               CREATE UNIQUE INDEX vcf_alleles_index
                   ON vcf_alleles (variant_id, allele_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_vcf_alleles_row(conn, row_dict):
    '''
    Insert a row into table "vcf_alleles"
    '''

    sentence = f'''
                INSERT INTO vcf_alleles
                    (variant_id, allele_id, bases, structure_allele_id)
                    VALUES ('{row_dict["variant_id"]}', '{row_dict["allele_id"]}', '{row_dict["bases"]}', '{row_dict["structure_allele_id"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_vcf_alleles(conn):
    '''
    Check if table "vcf_alleles" exists and if there are rows.
    '''

    # check if table "vcf_alleles" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'vcf_alleles'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "vcf_alleles" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM vcf_alleles
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_vcf_allele_dict(conn):
    '''
    Get a dictionary corresponding to allele data.
    '''

    # initialize the dictionary
    allele_dict = xlib.NestedDefaultDict()

    # query
    sentence = '''
               SELECT variant_id, allele_id, bases, structure_allele_id
                   FROM vcf_alleles;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        allele_dict[row[0]][row[1]] = {'bases': row[2], 'structure_allele_id': row[3]}

    # return the dictionary
    return allele_dict

#-------------------------------------------------------------------------------
# table "vcf_samples_alleles"
#-------------------------------------------------------------------------------

def drop_vcf_samples_alleles(conn):
    '''
    Drop the table "vcf_samples_alleles" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS vcf_samples_alleles;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_samples_alleles(conn):
    '''
    Create the table "vcf_samples_alleles".
    '''

    sentence = '''
               CREATE TABLE vcf_samples_alleles (
                   variant_id TEXT  NOT NULL,
                   sample_id  TEXT NOT NULL,
                   allele_id  TEXT NOT NULL,
                   frecuency  REAL NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_samples_alleles_index(conn):
    '''
    Create the unique index "vcf_samples_alleles_index" with the column "variant_id", "sample_id" and "allele_id" on the table "vcf_samples_alleles"
    '''

    sentence = '''
               CREATE UNIQUE INDEX vcf_samples_alleles_index
                   ON vcf_samples_alleles (variant_id, sample_id, allele_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_vcf_samples_alleles_row(conn, row_dict):
    '''
    Insert a row into table "vcf_samples_alleles"
    '''

    sentence = f'''
                INSERT INTO vcf_samples_alleles
                    (variant_id, sample_id, allele_id, frecuency)
                    VALUES ('{row_dict["variant_id"]}', '{row_dict["sample_id"]}', '{row_dict["allele_id"]}', {row_dict["frecuency"]});
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_vcf_samples_alleles(conn):
    '''
    Check if table "vcf_samples_alleles" exists and if there are rows.
    '''

    # check if table "vcf_samples_alleles" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'vcf_samples_alleles'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "vcf_samples_alleles" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM vcf_samples_alleles
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------
# table "vcf_samples_genotypes"
#-------------------------------------------------------------------------------

def drop_vcf_samples_genotypes(conn):
    '''
    Drop the table "vcf_samples_genotypes" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS vcf_samples_genotypes;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_samples_genotypes(conn):
    '''
    Create the table "vcf_samples_genotypes".
    '''

    sentence = '''
               CREATE TABLE vcf_samples_genotypes (
                   variant_id TEXT NOT NULL,
                   sample_id  TEXT NOT NULL,
                   gt_left    TEXT NOT NULL,
                   gt_right   TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_samples_genotypes_index(conn):
    '''
    Create the unique index "vcf_samples_genotypes_index" with the column "variant_id" and "sample_id" on the table "vcf_samples_genotypes"
    '''

    sentence = '''
               CREATE UNIQUE INDEX vcf_samples_genotypes_index
                   ON vcf_samples_genotypes (variant_id, sample_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_vcf_samples_genotypes_row(conn, row_dict):
    '''
    Insert a row into table "vcf_samples_genotypes"
    '''

    sentence = f'''
                INSERT INTO vcf_samples_genotypes
                    (variant_id, sample_id, gt_left, gt_right)
                    VALUES ('{row_dict["variant_id"]}', '{row_dict["sample_id"]}', '{row_dict["gt_left"]}', '{row_dict["gt_right"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_vcf_samples_genotypes(conn):
    '''
    Check if table "vcf_samples_genotypes" exists and if there are rows.
    '''

    # check if table "vcf_samples_genotypes" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'vcf_samples_genotypes'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "vcf_samples_genotypes" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM vcf_samples_genotypes
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_vcf_individual_genotype(conn, variant_id, sample_id):
    '''
    Get the genotype of an individual in a variant.
    '''

    if variant_id[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        variant_id = variant_id.lower()

    # query
    sentence = f'''
                SELECT gt_left, gt_right
                    FROM vcf_samples_genotypes
                    WHERE variant_id = '{variant_id}'
                      AND sample_id = '{sample_id}';
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the genotype
    gt_left = ''
    gt_right = ''
    for row in rows:
        gt_left = row[0]
        gt_right = row[1]

    # return the dictionary
    return gt_left, gt_right

#-------------------------------------------------------------------------------
# query "query_variants"
#-------------------------------------------------------------------------------

def query_variants(conn):
    '''
    Get a dictionary corresponding to rows variant data (genes, pseudogenes and exones).
    '''

    # initialize the dictionary
    variant_dict = {}

    # initialize the dictionary key
    key = 0

    # query
    sentence = '''
               SELECT a.variant_id, a.seq_id, a.position, b.start, b.end, b.type, b.gene, c.description, d.chromosome_id
                   FROM vcf_variants a, genomic_features b
                   LEFT JOIN gene_info c ON b.gene = c.symbol
                   LEFT JOIN alignments d ON a.variant_id = d.variant_id
                   WHERE a.seq_id = b.seq_id
                     AND a.position >= b.start
                     AND a.position <= b.end
                     AND b.type in ('region', 'gene', 'pseudogene', 'exon')
                UNION
                SELECT e.variant_id, e.seq_id, e.position, 0, 0, 'N/A', 'N/A', f.description, g.chromosome_id
                   FROM vcf_variants e
                   LEFT JOIN annotations f ON e.seq_id = f.seq_id
                   LEFT JOIN alignments g ON e.variant_id = g.variant_id
                   WHERE e.seq_id NOT IN (SELECT seq_id FROM genomic_features)
                ORDER BY 1;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        variant_dict[key] = {'variant_id': row[0], 'seq_id': row[1], 'position': row[2], 'start': row[3], 'end': row[4], 'type': row[5], 'gene': row[6], 'description': row[7], 'chromosome_id': row[8]}
        key += 1

    # return the dictionary
    return variant_dict

#-------------------------------------------------------------------------------
# query "query_imputed_alleles"
#-------------------------------------------------------------------------------

def query_imputed_alleles(conn, imputed_md_id):
    '''
    Get a dictionary corresponding to data of alleles with imputations.
    '''

    # initialize the dictionary
    imputed_allele_dict = {}

    # query
    sentence = f'''
                SELECT variant_id, COUNT(*)
                    FROM vcf_samples_alleles
                    WHERE allele_id = '{imputed_md_id}'
                    GROUP BY variant_id;
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        imputed_allele_dict[row[0]] = {'variant_id': row[0], 'counter': row[1]}

    # return the dictionary
    return imputed_allele_dict

#-------------------------------------------------------------------------------
# query "query_species_allele_frequencies"
#-------------------------------------------------------------------------------

def query_species_allele_frequencies(conn, md_symbol):
    '''
    Get a dictionary corresponding to individual allele frequencies per species of variant (alleles with missing data are not considered).
    '''

    # initialize the dictionary
    species_allele_frequency_dict = xlib.NestedDefaultDict()

    # query
    sentence = f'''
                SELECT a.variant_id, b.species_id, a.allele_id, SUM(a.frecuency)
                    FROM vcf_samples_alleles a, vcf_samples b
                    WHERE a.sample_id = b.sample_id
                      AND a.allele_id <> '{md_symbol}'
                      AND b.mother_id = 'NONE'
                    GROUP BY a.variant_id, b.species_id, a.allele_id
                    ORDER BY a.variant_id, b.species_id, a.allele_id;
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        species_allele_frequency_dict[row[0]][row[1]][row[2]] = {'frecuency_sum': row[3]}

    # return the dictionary
    return species_allele_frequency_dict

#-------------------------------------------------------------------------------
# query "query_species_and_type_allele_frequencies"
#-------------------------------------------------------------------------------

def query_species_and_type_allele_frequencies(conn, md_symbol):
    '''
    Get a dictionary corresponding to individual allele frequencies per species and type of variant per species (alleles with missing data and adult individuals are not considered).
    '''

    # initialize the dictionary
    species_and_type_allele_frequency_dict = xlib.NestedDefaultDict()

    # query
    sentence = f'''
                SELECT a.variant_id, b.species_id, b.type, a.allele_id, SUM(a.frecuency)
                    FROM vcf_samples_alleles a, vcf_samples b
                    WHERE a.sample_id = b.sample_id
                      AND a.allele_id <> '{md_symbol}'
                      AND b.type <> 'ADULT'
                    GROUP BY a.variant_id, b.species_id, b.type, a.allele_id
                    ORDER BY a.variant_id, b.species_id, b.type, a.allele_id;
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        species_and_type_allele_frequency_dict[row[0]][row[1]][row[2]][row[3]] = {'frecuency_sum': row[4]}

    # return the dictionary
    return species_and_type_allele_frequency_dict

#-------------------------------------------------------------------------------
# table "vcf_snps"
#-------------------------------------------------------------------------------

def drop_vcf_snps(conn):
    '''
    Drop the table "vcf_snps" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS vcf_snps;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_snps(conn):
    '''
    Create the table "vcf_snps".
    '''

    sentence = '''
               CREATE TABLE vcf_snps (
                   variant_id         TEXT NOT NULL,
                   ref                TEXT NOT NULL,
                   alt                TEXT NOT NULL,
                   sample_gt_list     TEXT NOT NULL,
                   sample_withmd_list TEXT);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_snps_index(conn):
    '''
    Create the unique index "vcf_snps_index" with the column "variant_id" on the table "vcf_snps"
    '''

    sentence = '''
               CREATE UNIQUE INDEX vcf_snps_index
                   ON vcf_snps (variant_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_vcf_snps_row(conn, row_dict):
    '''
    Insert a row into table "vcf_snps"
    '''

    sentence = f'''
                INSERT INTO vcf_snps
                    (variant_id, ref, alt, sample_gt_list, sample_withmd_list)
                    VALUES ('{row_dict["variant_id"]}', '{row_dict["ref"]}', '{row_dict["alt"]}', '{row_dict["sample_gt_list"]}', '{row_dict["sample_withmd_list"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_vcf_snps(conn):
    '''
    Check if table "vcf_snps" exists and if there are rows.
    '''

    # check if table "vcf_snps" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'vcf_snps'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "vcf_snps" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM vcf_snps
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_snp_data_dict(conn, snp_id):
    '''
    Get a dictionary of SNP data corresponding to the SNP identification.
    '''

    # initialize the dictionary
    snps_data_dict = {}

    # query
    sentence = f'''
                SELECT variant_id, ref, alt, sample_gt_list, sample_withmd_list
                    FROM vcf_snps
                    WHERE variant_id = '{snp_id}';
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        snps_data_dict = {'variant_id': row[0], 'ref': row[1], 'alt': row[2], 'sample_gt_list': row[3], 'sample_withmd_list': row[4]}

    # return the dictionary
    return snps_data_dict

#-------------------------------------------------------------------------------
# query "get_snp_ids_list"
#-------------------------------------------------------------------------------

def get_snp_ids_list(conn):
    '''
    Get a list corresponding to all variant identifications.
    '''

    # initialize the list
    variant_id_list = []

    # query
    sentence = '''
               SELECT variant_id
                   FROM vcf_snps;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # add the variant identification to the list
    for row in rows:
        variant_id_list.append(row[0])

    # return the list
    return variant_id_list

#-------------------------------------------------------------------------------
# query "get_snp_ids_wmd_list"
#-------------------------------------------------------------------------------

def get_snp_ids_wmd_list(conn):
    '''
    Get a list corresponding to the variant identifications with missing data.
    '''

    # initialize the list
    variant_id_list = []

    # query
    sentence = '''
               SELECT variant_id
                   FROM vcf_snps
                   WHERE length(sample_withmd_list) > 0;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # add the variant identification to the list
    for row in rows:
        variant_id_list.append(row[0])

    # return the list
    return variant_id_list

#-------------------------------------------------------------------------------
# table "vcf_linkage_disequilibrium"
#-------------------------------------------------------------------------------

def drop_vcf_linkage_disequilibrium(conn):
    '''
    Drop the table "vcf_linkage_disequilibrium" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS vcf_linkage_disequilibrium;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_linkage_disequilibrium(conn):
    '''
    Create the table "vcf_linkage_disequilibrium".
    '''

    sentence = '''
               CREATE TABLE vcf_linkage_disequilibrium (
                   snp_id_1             TEXT NOT NULL,
                   snp_id_2             TEXT NOT NULL,
                   dhat                 REAL NOT NULL,
                   r2                   REAL NOT NULL,
                   sample_withmd_list_2 TEXT);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_linkage_disequilibrium_index(conn):
    '''
    Create the unique index "vcf_linkage_disequilibrium_index" with the columns "snp_id_1" and "snp_id_2" on the table "vcf_linkage_disequilibrium"
    '''

    sentence = '''
               CREATE UNIQUE INDEX vcf_linkage_disequilibrium_index
                   ON vcf_linkage_disequilibrium (snp_id_1, snp_id_2);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_vcf_linkage_disequilibrium_row(conn, row_dict):
    '''
    Insert a row into table "vcf_linkage_disequilibrium"
    '''

    sentence = f'''
                INSERT INTO vcf_linkage_disequilibrium
                    (snp_id_1, snp_id_2, dhat, r2, sample_withmd_list_2)
                    VALUES ('{row_dict["snp_id_1"]}', '{row_dict["snp_id_2"]}', {row_dict["dhat"]}, {row_dict["r2"]}, '{row_dict["sample_withmd_list_2"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_vcf_linkage_disequilibrium(conn):
    '''
    Check if table "vcf_linkage_disequilibrium" exists and if there are rows.
    '''

    # check if table "vcf_linkage_disequilibrium" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'vcf_linkage_disequilibrium'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "vcf_linkage_disequilibrium" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM vcf_linkage_disequilibrium
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_vcf_linkage_disequilibrium_snp_id_1_list(conn):
    '''
    Get a list of variant identifications with linkage disequilibrium data.
    '''

    # initialize the list
    snp_id_1_list = []

    # query
    sentence = '''
               SELECT DISTINCT snp_id_1
                   FROM vcf_linkage_disequilibrium;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        snp_id_1_list.append(row[0])

    # return the list
    return snp_id_1_list

#-------------------------------------------------------------------------------

def get_vcf_linkage_disequilibrium_list(conn, snp_id_1):
    '''
    Get a list of linkage disequilibrium data corresponding to a variant.
    '''

    # initialize the list
    linkage_disequilibrium_list = []

    # query
    sentence = f'''
                SELECT snp_id_2, dhat, r2, sample_withmd_list_2
                    FROM vcf_linkage_disequilibrium
                    WHERE snp_id_1 = '{snp_id_1}';
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        linkage_disequilibrium_list.append([row[0], row[1], row[2], row[3]])

    # return the list
    return linkage_disequilibrium_list

#-------------------------------------------------------------------------------

def get_vcf_linkage_disequilibrium_r2_measures(conn):
    '''
    Get global measures of r2 from linkage disequilibrium data.
    '''

    conn.create_aggregate("STDEV", 1, Stdev)

    # initialize data
    avg = 0
    stdev = 0

    # query
    sentence = '''
               SELECT AVG(r2), STDEV(r2)
                   FROM vcf_linkage_disequilibrium
                   where r2 >= 0;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        avg = float(row[0])
        stdev = float(row[1])
        break

    # return the list
    return avg, stdev

#-------------------------------------------------------------------------------
# table "vcf_kinship"
#-------------------------------------------------------------------------------

def drop_vcf_kinship(conn):
    '''
    Drop the table "vcf_kinship" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS vcf_kinship;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_kinship(conn):
    '''
    Create the table "vcf_kinship".
    '''

    sentence = '''
               CREATE TABLE vcf_kinship (
                   individual_i INTEGER NOT NULL,
                   individual_j INTEGER NOT NULL,
                   rbeta        REAL    NOT NULL,
                   rw           REAL    NOT NULL,
                   ru           REAL    NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_kinship_index(conn):
    '''
    Create the unique index "vcf_kinship_index" with the columns "individual_i" and "individual_j" on the table "vcf_kinship"
    '''

    sentence = '''
               CREATE UNIQUE INDEX vcf_kinship_index
                   ON vcf_kinship (individual_i, individual_j);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_vcf_kinship_row(conn, row_dict):
    '''
    Insert a row into table "vcf_kinship"
    '''

    sentence = f'''
                INSERT INTO vcf_kinship
                    (individual_i, individual_j, rbeta, rw, ru)
                    VALUES ({row_dict["individual_i"]}, {row_dict["individual_j"]}, {row_dict["rbeta"]}, {row_dict["rw"]}, {row_dict["ru"]});
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_vcf_kinship(conn):
    '''
    Check if table "vcf_kinship" exists and if there are rows.
    '''

    # check if table "vcf_kinship" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'vcf_kinship'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "vcf_kinship" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM vcf_kinship
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_vcf_kinship_dict(conn):
    '''
    Get a dictionary corresponding to kinship data.
    '''

    # initialize the dictionary
    kinship_dict = xlib.NestedDefaultDict()

    # query
    sentence = '''
               SELECT individual_i, individual_j, rbeta, rw, ru
                   FROM vcf_kinship;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        kinship_dict[row[0]][row[1]] = {'rbeta': row[2], 'rw': row[3], 'ru': row[4]}

    # return the dictionary
    return kinship_dict

#-------------------------------------------------------------------------------
# table "interproscan_annotations"
#-------------------------------------------------------------------------------

def drop_interproscan_annotations(conn):
    '''
    Drop the table "interproscan_annotations" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS interproscan_annotations;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_interproscan_annotations(conn):
    '''
    Create table "interproscan_annotations".
    '''

    sentence = '''
               CREATE TABLE interproscan_annotations (
                   cluster_id        TEXT NOT NULL,
                   interpro_goterms  TEXT NOT NULL,
                   panther_goterms   TEXT NOT NULL,
                   x_goterms         TEXT NOT NULL,
                   metacyc_pathways  TEXT NOT NULL,
                   reactome_pathways TEXT NOT NULL,
                   x_pathways        TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_interproscan_annotations_index(conn):
    '''
    Create the index "interproscan_annotations_index" (if it does not exist) with the column "cluster_id" on the table "interproscan_annotations".
    '''

    sentence = '''
               CREATE INDEX interproscan_annotations_index
                   ON interproscan_annotations (cluster_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_interproscan_annotations_row(conn, row_dict):
    '''
    Insert a row into table "interproscan_annotations".
    '''

    sentence = f'''
                INSERT INTO interproscan_annotations
                    (cluster_id, interpro_goterms, panther_goterms, x_goterms, metacyc_pathways, reactome_pathways, x_pathways)
                    VALUES ('{row_dict["cluster_id"]}', '{row_dict["interpro_goterms"]}', '{row_dict["panther_goterms"]}', '{row_dict["x_goterms"]}', '{row_dict["metacyc_pathways"]}', '{row_dict["reactome_pathways"]}', '{row_dict["x_pathways"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_interproscan_annotations(conn):
    '''
    Check if table "interproscan_annotations" exists and if there are rows.
    '''

    # check if table "interproscan_annotations" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'interproscan_annotations'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "interproscan_annotations" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM interproscan_annotations
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_interproscan_annotation_dict(conn, cluster_id):
    '''
    Get the row data from the table "interproscan_annotations" corresponding to
    a cluster identification.
    '''

    # initialize the dictionary
    annotations_dict = {}

    # select rows from the table "interproscan_annotations"
    sentence = f'''
                SELECT cluster_id, interpro_goterms, panther_goterms, x_goterms, metacyc_pathways, reactome_pathways, x_pathways
                    FROM interproscan_annotations
                    WHERE cluster_id = "{cluster_id}";
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        annotations_dict = {'cluster_id': row[0], 'interpro_goterms': row[1], 'panther_goterms': row[2], 'x_goterms': row[3], 'metacyc_pathways': row[4], 'reactome_pathways': row[5], 'x_pathways': row[6]}

    # return the dictionary
    return annotations_dict

#-------------------------------------------------------------------------------

def get_metacyc_pathways_per_cluster_dict(conn, species_name):
    '''
    Get the dictionary of the MetaCyc pathways of each cluster corresponding to the species.
    '''

    # initialize the dictionary
    pathways_per_cluster_dict = {}

    # select rows from the table "interproscan_annotations"
    if species_name == xlib.get_all_species_code():
        sentence = '''
                   SELECT cluster_id, metacyc_pathways
                       FROM interproscan_annotations;
                   '''
    else:
        sentence = f'''
                    SELECT cluster_id, metacyc_pathways
                        FROM interproscan_annotations
                        WHERE cluster_id in (SELECT DISTINCT cluster_id
                                                FROM mmseqs2_relationships
                                                where species like "%{species_name}%");
                    '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        pathways_per_cluster_dict[row[0]] = {'metacyc_pathways': row[1]}

    # return the dictionary
    return pathways_per_cluster_dict

#-------------------------------------------------------------------------------
# table "emapper_annotations"
#-------------------------------------------------------------------------------

def drop_emapper_annotations(conn):
    '''
    Drop the table "emapper_annotations" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS emapper_annotations;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_emapper_annotations(conn):
    '''
    Create table "emapper_annotations".
    '''

    sentence = '''
               CREATE TABLE emapper_annotations (
                   cluster_id       TEXT NOT NULL,
                   ortholog_seq_id  TEXT NOT NULL,
                   ortholog_species TEXT NOT NULL,
                   eggnog_ogs       TEXT NOT NULL,
                   cog_category     TEXT NOT NULL,
                   description      TEXT NOT NULL,
                   goterms          TEXT NOT NULL,
                   ec               TEXT NOT NULL,
                   kegg_kos         TEXT NOT NULL,
                   kegg_pathways    TEXT NOT NULL,
                   kegg_modules     TEXT NOT NULL,
                   kegg_reactions   TEXT NOT NULL,
                   kegg_rclasses    TEXT NOT NULL,
                   brite            TEXT NOT NULL,
                   kegg_tc          TEXT NOT NULL,
                   cazy             TEXT NOT NULL,
                   pfams            TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_emapper_annotations_index(conn):
    '''
    Create the index "emapper_annotations_index" (if it does not exist) with the column "cluster_id" on the table "emapper_annotations".
    '''

    sentence = '''
               CREATE INDEX emapper_annotations_index
                   ON emapper_annotations (cluster_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_emapper_annotations_row(conn, row_dict):
    '''
    Insert a row into table "emapper_annotations".
    '''

    sentence = f'''
                INSERT INTO emapper_annotations
                    (cluster_id, ortholog_seq_id, ortholog_species, eggnog_ogs, cog_category, description, goterms, ec, kegg_kos, kegg_pathways, kegg_modules, kegg_reactions, kegg_rclasses, brite, kegg_tc, cazy, pfams)
                    VALUES ('{row_dict["cluster_id"]}', '{row_dict["ortholog_seq_id"]}', '{row_dict["ortholog_species"]}', '{row_dict["eggnog_ogs"]}', '{row_dict["cog_category"]}', '{row_dict["description"]}', '{row_dict["goterms"]}', '{row_dict["ec"]}', '{row_dict["kegg_kos"]}', '{row_dict["kegg_pathways"]}', '{row_dict["kegg_modules"]}', '{row_dict["kegg_reactions"]}', '{row_dict["kegg_rclasses"]}', '{row_dict["brite"]}', '{row_dict["kegg_tc"]}', '{row_dict["cazy"]}', '{row_dict["pfams"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_emapper_annotations(conn):
    '''
    Check if table "emapper_annotations" exists and if there are rows.
    '''

    # check if table "emapper_annotations" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'emapper_annotations'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "emapper_annotations" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM emapper_annotations
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_emapper_annotation_dict(conn, cluster_id):
    '''
    Get the row data from the table "emapper_annotations" corresponding to
    a cluster identification.
    '''

    # initialize the dictionary
    annotations_dict = {}

    # select rows from the table "emapper_annotations"
    sentence = f'''
                SELECT cluster_id, ortholog_seq_id, ortholog_species, eggnog_ogs, cog_category, description, goterms, ec, kegg_kos, kegg_pathways, kegg_modules, kegg_reactions, kegg_rclasses, brite, kegg_tc, cazy, pfams
                    FROM emapper_annotations
                    WHERE cluster_id = "{cluster_id}";
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        annotations_dict = {'cluster_id': row[0], 'ortholog_seq_id': row[1], 'ortholog_species': row[2], 'eggnog_ogs': row[3], 'cog_category': row[4], 'description': row[5], 'goterms': row[6], 'ec': row[7], 'kegg_kos': row[8], 'kegg_pathways': row[9], 'kegg_modules': row[10], 'kegg_reactions': row[11], 'kegg_rclasses': row[12], 'brite': row[13], 'kegg_tc': row[14], 'cazy': row[15], 'pfams': row[16]}

    # return the dictionary
    return annotations_dict

#-------------------------------------------------------------------------------

def get_kegg_kos_per_cluster_dict(conn, species_name):
    '''
    Get the dictionary of the KEGG KOs of each cluster corresponding to the species.
    '''

    # initialize the dictionary
    kos_per_cluster_dict = {}

    # select rows from the table "emapper_annotations"
    if species_name == xlib.get_all_species_code():
        sentence = '''
                   SELECT cluster_id, kegg_kos
                       FROM emapper_annotations;
                   '''
    else:
        sentence = f'''
                    SELECT cluster_id, kegg_kos
                        FROM emapper_annotations
                        WHERE cluster_id in (SELECT DISTINCT cluster_id
                                                FROM mmseqs2_relationships
                                                where species like "%{species_name}%");
                    '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        kos_per_cluster_dict[row[0]] = {'kegg_kos': row[1]}

    # return the dictionary
    return kos_per_cluster_dict

#-------------------------------------------------------------------------------

def get_kegg_pathways_per_cluster_dict(conn, species_name):
    '''
    Get the dictionary of the KEGG pathways of each cluster corresponding to the species.
    '''

    # initialize the dictionary
    pathways_per_cluster_dict = {}

    # select rows from the table "emapper_annotations"
    if species_name == xlib.get_all_species_code():
        sentence = '''
                   SELECT cluster_id, kegg_pathways
                       FROM emapper_annotations;
                   '''
    else:
        sentence = f'''
                    SELECT cluster_id, kegg_pathways
                        FROM emapper_annotations
                        WHERE cluster_id in (SELECT DISTINCT cluster_id
                                                FROM mmseqs2_relationships
                                                where species like "%{species_name}%");
                    '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        pathways_per_cluster_dict[row[0]] = {'kegg_pathways': row[1]}

    # return the dictionary
    return pathways_per_cluster_dict

#-------------------------------------------------------------------------------
# table "mmseqs2_relationships"
#-------------------------------------------------------------------------------

def drop_mmseqs2_relationships(conn):
    '''
    Drop the table "mmseqs2_relationships" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS mmseqs2_relationships;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_mmseqs2_relationships(conn):
    '''
    Create table "mmseqs2_relationships".
    '''

    sentence = '''
               CREATE TABLE mmseqs2_relationships (
                   cluster_id  TEXT NOT NULL,
                   seq_id      TEXT NOT NULL,
                   description TEXT NOT NULL,
                   species     TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_mmseqs2_relationships_index_1(conn):
    '''
    Create the index "mmseqs2_relationships_index_1" (if it does not exist) with the column "cluster_id" on the table "mmseqs2_relationships".
    '''

    sentence = '''
               CREATE INDEX mmseqs2_relationships_index_1
                   ON mmseqs2_relationships (cluster_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_mmseqs2_relationships_index_2(conn):
    '''
    Create the index "mmseqs2_relationships_index_2" (if it does not exist) with the column "seq_id" on the table "mmseqs2_relationships".
    '''

    sentence = '''
               CREATE UNIQUE INDEX mmseqs2_relationships_index_2
                   ON mmseqs2_relationships (seq_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_mmseqs2_relationships_row(conn, row_dict):
    '''
    Insert a row into table "mmseqs2_relationships".
    '''

    sentence = f'''
                INSERT INTO mmseqs2_relationships
                    (cluster_id, seq_id, description, species)
                    VALUES ('{row_dict["cluster_id"]}', '{row_dict["seq_id"]}', '{row_dict["description"]}', '{row_dict["species"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_mmseqs2_relationships(conn):
    '''
    Check if table "mmseqs2_relationships" exists and if there are rows.
    '''

    # check if table "mmseqs2_relationships" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'mmseqs2_relationships'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "mmseqs2_relationships" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM mmseqs2_relationships
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_mmseqs2_relationship_dict(conn, cluster_id):
    '''
    Get rows data from the table "mmseqs2_relationships" corresponding to
    a cluster identification.
    '''

    # initialize the dictionary
    relationships_dict = {}

    # select rows from the table "mmseqs2_relationships"
    sentence = f'''
                SELECT cluster_id, seq_id, description, species
                    FROM mmseqs2_relationships
                    WHERE cluster_id = "{cluster_id}";
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        key = f'{row[0]}-{row[1]}'
        relationships_dict[key] = {'cluster_id': row[0], 'seq_id': row[1], 'description': row[2], 'species': row[3]}

    # return the dictionary
    return relationships_dict

#-------------------------------------------------------------------------------

def get_mmseqs2_seq_mf_data(conn, cluster_id):
    '''
    Get the most frequent description and species from the table "mmseqs2_relationships"
    corresponding to a cluster identification.
    '''

    # initialize the description, dictionary
    description_dict = {}

    # initialize the dictionary
    species_dict = {}

    # select rows from the table "mmseqs2_relationships"
    sentence = f'''
                SELECT description, species
                    FROM mmseqs2_relationships
                    WHERE cluster_id = "{cluster_id}";
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # count descriptions and species
    for row in rows:
        # descriptions
        description_counter = description_dict.get(row[0], 0)
        description_dict[row[0]] = description_counter + 1
        # species
        species_counter = species_dict.get(row[1], 0)
        species_dict[row[1]] = species_counter + 1

    # calculate the most frecuent description and species
    higher_counter = -1
    mf_description = ''
    for description, description_counter in description_dict.items():
        if description_counter > higher_counter:
            mf_description = description
            higher_counter = description_counter

    # calculate the most frecuent species
    higher_counter = -1
    mf_species = ''
    for species, species_counter in species_dict.items():
        if species_counter > higher_counter:
            mf_species = species
            higher_counter = species_counter

    # return the most frecuent species
    return mf_description, mf_species

#-------------------------------------------------------------------------------

def get_mmseqs2_species_list(conn):
    '''
    Get the distinct species names in the table "mmseqs2_relationships".
    '''

    # initialize the species names list
    species_names_list = []

    # select rows from the table "mmseqs2_relationships"
    sentence = '''
               SELECT DISTINCT species
                   FROM mmseqs2_relationships
                   ORDER by 1;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add species name to the species names list
    for row in rows:
        if len(row[0].split()) == 2 and row[0][0].isalpha() and row[0][0].isupper() and not row[0].endswith('sp.') and row[0].find('AltName') == -1:
            species_names_list.append(row[0])

    # return the species names list
    return species_names_list

#-------------------------------------------------------------------------------

def get_goterms_per_cluster_dict(conn, species_name):
    '''
    Get the dictionary of the GO terms of each cluster corresponding to the species.
    '''

    # initialize the dictionary
    goterms_per_cluster_dict = {}

    # select rows from the table "interproscan_annotations"
    if species_name == xlib.get_all_species_code():
        sentence = '''
                   WITH cluster_identifications AS (
                       SELECT DISTINCT cluster_id
                       FROM mmseqs2_relationships
                   )
                   SELECT a.cluster_id, COALESCE(b.interpro_goterms, '-'), COALESCE(b.panther_goterms, '-'), COALESCE(c.goterms, '-')
                   FROM cluster_identifications a
                   LEFT JOIN interproscan_annotations b USING (cluster_id)
                   LEFT JOIN emapper_annotations c USING (cluster_id)
                   WHERE COALESCE(b.interpro_goterms, '-') != '-' OR COALESCE(b.panther_goterms, '-') != '-' OR COALESCE(c.goterms, '-') != '-'; 
                   '''
    else:
        sentence = f'''
                    WITH cluster_identifications AS (
                        SELECT DISTINCT cluster_id
                        FROM mmseqs2_relationships
                        WHERE species LIKE "%{species_name}%"
                    )
                    SELECT a.cluster_id, COALESCE(b.interpro_goterms, '-'), COALESCE(b.panther_goterms, '-'), COALESCE(c.goterms, '-')
                    FROM cluster_identifications a
                    LEFT JOIN interproscan_annotations b USING (cluster_id)
                    LEFT JOIN emapper_annotations c USING (cluster_id)
                    WHERE COALESCE(b.interpro_goterms, '-') != '-' OR COALESCE(b.panther_goterms, '-') != '-' OR COALESCE(c.goterms, '-') != '-';
                    '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        goterms_per_cluster_dict[row[0]] = {'interpro_goterms': row[1], 'panther_goterms': row[2], 'eggnog_goterms': row[3]}

    # return the dictionary
    return goterms_per_cluster_dict

#-------------------------------------------------------------------------------
# table "tair10_orthologs"
#-------------------------------------------------------------------------------

def drop_tair10_orthologs(conn):
    '''
    Drop the table "tair10_orthologs" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS tair10_orthologs;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_tair10_orthologs(conn):
    '''
    Create table "tair10_orthologs".
    '''

    sentence = '''
               CREATE TABLE tair10_orthologs (
                   cluster_id      TEXT NOT NULL,
                   ortholog_seq_id TEXT NOT NULL);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_tair10_orthologs_index(conn):
    '''
    Create the index "tair10_orthologs_index" (if it does not exist) with the column "cluster_id" on the table "tair10_orthologs".
    '''

    sentence = '''
               CREATE UNIQUE INDEX tair10_orthologs_index
                   ON tair10_orthologs (cluster_id);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_tair10_orthologs_row(conn, row_dict):
    '''
    Insert a row into table "tair10_orthologs".
    '''

    sentence = f'''
                INSERT INTO tair10_orthologs
                    (cluster_id, ortholog_seq_id)
                    VALUES ('{row_dict["cluster_id"]}', '{row_dict["ortholog_seq_id"]}');
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_tair10_orthologs(conn):
    '''
    Check if table "tair10_orthologs" exists and if there are rows.
    '''

    # check if table "tair10_orthologs" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'tair10_orthologs'
                       LIMIT 1);
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        control = int(row[0])
        break

    # check if there are rows when the table "tair10_orthologs" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM tair10_orthologs
                           LIMIT 1);
                   '''
        try:
            rows = conn.execute(sentence)
        except Exception as e:
            raise xlib.ProgramException(e, 'B002', sentence, conn)

        # get the row number
        for row in rows:
            control = int(row[0])
            break

    # return the row number
    return control

#-------------------------------------------------------------------------------

def get_tair10_ortholog_seq_id(conn, cluster_id):
    '''
    Get the TAIR 10 ortholog sequence identification of a cluster identification.
    '''

    # initialize ortholog sequence identification
    ortholog_seq_id = '-'

    # query
    sentence = f'''
                SELECT ortholog_seq_id
                    FROM tair10_orthologs
                    where cluster_id = '{cluster_id}';
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        ortholog_seq_id = row[0]
        break

    # return the ortholog sequence identification
    return ortholog_seq_id

#-------------------------------------------------------------------------------
# Statistics of gymnoTOA database
#-------------------------------------------------------------------------------

def get_quercustoa_db_stats(conn):
    '''
    Get the statistics of gymnoTOA database.
    '''

    # count the sequences number of Acrogymnospermae
    sentence = '''
               SELECT COUNT(*)
                   FROM mmseqs2_relationships;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # set the sequences number of Acrogymnospermae
    seqnum_acrogymnospermae = 0
    for row in rows:
        seqnum_acrogymnospermae = int(row[0])
        break

    # count the total of clusters
    sentence = '''
               SELECT COUNT(DISTINCT cluster_id)
                   FROM mmseqs2_relationships;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # set the total of clusters
    clusternum_total = 0
    for row in rows:
        clusternum_total = int(row[0])
        break

    # count the clusters number with InterProScan annotations
    sentence = '''
               SELECT COUNT(*)
                   FROM interproscan_annotations;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # set the clusters number with InterProScan annotations
    clusternum_interproscan_annotations = 0
    for row in rows:
        clusternum_interproscan_annotations = int(row[0])
        break

    # count the clusters number with eggNOG-mapper annotations
    sentence = '''
               SELECT COUNT(*)
                   FROM emapper_annotations;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # set the clusters number with eggNOG-mapper annotations
    clusternum_emapper_annotations = 0
    for row in rows:
        clusternum_emapper_annotations = int(row[0])
        break

    # count the clusters number with TAIR10 orthologs
    sentence = '''
               SELECT COUNT(*)
                   FROM tair10_orthologs;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # set the clusters number with TAIR10 orthologs
    clusternum_tair10_ortologs = 0
    for row in rows:
        clusternum_tair10_ortologs = int(row[0])
        break

    # get the cluster identifications with InterProScan annotations
    sentence = '''
               SELECT cluster_id
                   FROM interproscan_annotations;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # build the set of clusters identifications with InterProScan annotations
    interproscan_cluster_id_set = set()
    for row in rows:
        interproscan_cluster_id_set.add(row[0])

    # get the cluster identifications with eggNOG-mapper annotations
    sentence = '''
               SELECT cluster_id
                   FROM emapper_annotations;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # build the set of clusters identifications with eggNOG-mapper annotations
    emapper_cluster_id_set = set()
    for row in rows:
        emapper_cluster_id_set.add(row[0])

    # get the cluster identifications with TAIR10 orthologs
    sentence = '''
               SELECT cluster_id
                   FROM tair10_orthologs;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # build the set of clusters identifications with TAIR10 orthologs
    tair10_cluster_id_set = set()
    for row in rows:
        tair10_cluster_id_set.add(row[0])

    # calculate the
    union_cluster_id_set = interproscan_cluster_id_set | emapper_cluster_id_set | tair10_cluster_id_set
    clusternum_with_annotations = len(union_cluster_id_set)
    clusternum_without_annotations = clusternum_total - clusternum_with_annotations


    # return the ortholog sequence identification
    return seqnum_acrogymnospermae, clusternum_total, clusternum_interproscan_annotations, clusternum_emapper_annotations, clusternum_tair10_ortologs, clusternum_without_annotations

#-------------------------------------------------------------------------------
# Statistics of quercusTOA database
#-------------------------------------------------------------------------------

def get_quercustoa_db_stats(conn):
    '''
    Get the statistics of quercusTOA database.
    '''

    # count the sequences number of Quercus
    sentence = '''
               SELECT COUNT(*)
                   FROM mmseqs2_relationships;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # set the sequences number of Quercus
    seqnum_quercus = 0
    for row in rows:
        seqnum_quercus = int(row[0])
        break

    # count the total of clusters
    sentence = '''
               SELECT COUNT(DISTINCT cluster_id)
                   FROM mmseqs2_relationships;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # set the total of clusters
    clusternum_total = 0
    for row in rows:
        clusternum_total = int(row[0])
        break

    # count the clusters number with InterProScan annotations
    sentence = '''
               SELECT COUNT(*)
                   FROM interproscan_annotations;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # set the clusters number with InterProScan annotations
    clusternum_interproscan_annotations = 0
    for row in rows:
        clusternum_interproscan_annotations = int(row[0])
        break

    # count the clusters number with eggNOG-mapper annotations
    sentence = '''
               SELECT COUNT(*)
                   FROM emapper_annotations;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # set the clusters number with eggNOG-mapper annotations
    clusternum_emapper_annotations = 0
    for row in rows:
        clusternum_emapper_annotations = int(row[0])
        break

    # count the clusters number with TAIR10 orthologs
    sentence = '''
               SELECT COUNT(*)
                   FROM tair10_orthologs;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # set the clusters number with TAIR10 orthologs
    clusternum_tair10_ortologs = 0
    for row in rows:
        clusternum_tair10_ortologs = int(row[0])
        break

    # get the cluster identifications with InterProScan annotations
    sentence = '''
               SELECT cluster_id
                   FROM interproscan_annotations;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # build the set of clusters identifications with InterProScan annotations
    interproscan_cluster_id_set = set()
    for row in rows:
        interproscan_cluster_id_set.add(row[0])

    # get the cluster identifications with eggNOG-mapper annotations
    sentence = '''
               SELECT cluster_id
                   FROM emapper_annotations;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # build the set of clusters identifications with eggNOG-mapper annotations
    emapper_cluster_id_set = set()
    for row in rows:
        emapper_cluster_id_set.add(row[0])

    # get the cluster identifications with TAIR10 orthologs
    sentence = '''
               SELECT cluster_id
                   FROM tair10_orthologs;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

    # build the set of clusters identifications with TAIR10 orthologs
    tair10_cluster_id_set = set()
    for row in rows:
        tair10_cluster_id_set.add(row[0])

    # calculate the
    union_cluster_id_set = interproscan_cluster_id_set | emapper_cluster_id_set | tair10_cluster_id_set
    clusternum_with_annotations = len(union_cluster_id_set)
    clusternum_without_annotations = clusternum_total - clusternum_with_annotations


    # return the ortholog sequence identification
    return seqnum_quercus, clusternum_total, clusternum_interproscan_annotations, clusternum_emapper_annotations, clusternum_tair10_ortologs, clusternum_without_annotations

#-------------------------------------------------------------------------------
# General classes
#-------------------------------------------------------------------------------

class Stdev:
    '''
    This class defines the calculation of standard deviation
    (SQLite does not have a function for standard deviation).
    '''

    #---------------

    def __init__(self):
        '''
        Initialize the class
        '''

        self.M = 0.0
        self.S = 0.0
        self.k = 1

    #---------------

    def step(self, value):
        '''
        ...
        '''

        if value is None:
            return

        tM = self.M
        self.M += (value - tM) / self.k
        self.S += (value - tM) * (value - self.M)
        self.k += 1

    #---------------

    def finalize(self):
        '''
        Finalize the class
        '''

        if self.k < 3:
            return None

        return math.sqrt(self.S / (self.k-2))

    #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print('This source contains general functions for the maintenance of the NGShelper SQLite databases in both console mode and gui mode.')
    sys.exit(0)

#-------------------------------------------------------------------------------
