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

    try:
        conn = sqlite3.connect(database_path, check_same_thread=check_same_thread)
    except Exception as e:
        raise xlib.ProgramException(e, 'B001', database_path)

    # return connection
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
# (see ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/)
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
                    VALUES ('{row_dict["gene_id"]}', '{row_dict["tax_id"]}', '{row_dict["symbol"]}', '{row_dict["description"]}')
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

def get_genomic_features_dict(conn, transcript_seq_id, transcript_start, transcript_end):
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
                    VALUES ('{row_dict["sample_id"]}', '{row_dict["species_id"]}', '{row_dict["mother_id"]}', '{row_dict["type"]}', {row_dict["colnum"]})
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
                    WHERE sample_id = '{sample_id}'
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
                            '{row_dict["alternative_alleles"]}', '{row_dict["variant_type"]}')
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
                    VALUES ('{row_dict["variant_id"]}', '{row_dict["allele_id"]}', '{row_dict["bases"]}', '{row_dict["structure_allele_id"]}')
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

def get_vcf_alleles_dict(conn):
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
                    VALUES ('{row_dict["variant_id"]}', '{row_dict["sample_id"]}', '{row_dict["allele_id"]}', {row_dict["frecuency"]})
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
                    VALUES ('{row_dict["variant_id"]}', '{row_dict["sample_id"]}', '{row_dict["gt_left"]}', '{row_dict["gt_right"]}')
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
                    VALUES ('{row_dict["variant_id"]}', '{row_dict["ref"]}', '{row_dict["alt"]}', '{row_dict["sample_gt_list"]}', '{row_dict["sample_withmd_list"]}')
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
# table "vcf_linkage_desequilibrium"
#-------------------------------------------------------------------------------

def drop_vcf_linkage_desequilibrium(conn):
    '''
    Drop the table "vcf_linkage_desequilibrium" (if it exists)
    '''

    sentence = '''
               DROP TABLE IF EXISTS vcf_linkage_desequilibrium;
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def create_vcf_linkage_desequilibrium(conn):
    '''
    Create the table "vcf_linkage_desequilibrium".
    '''

    sentence = '''
               CREATE TABLE vcf_linkage_desequilibrium (
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

def create_vcf_linkage_desequilibrium_index(conn):
    '''
    Create the unique index "vcf_linkage_desequilibrium_index" with the columns "snp_id_1" and "snp_id_2" on the table "vcf_linkage_desequilibrium"
    '''

    sentence = '''
               CREATE UNIQUE INDEX vcf_linkage_desequilibrium_index
                   ON vcf_linkage_desequilibrium (snp_id_1, snp_id_2);
               '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def insert_vcf_linkage_desequilibrium_row(conn, row_dict):
    '''
    Insert a row into table "vcf_linkage_desequilibrium"
    '''

    sentence = f'''
                INSERT INTO vcf_linkage_desequilibrium
                    (snp_id_1, snp_id_2, dhat, r2, sample_withmd_list_2)
                    VALUES ('{row_dict["snp_id_1"]}', '{row_dict["snp_id_2"]}', {row_dict["dhat"]}, {row_dict["r2"]}, '{row_dict["sample_withmd_list_2"]}')
                '''
    try:
        conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)

#-------------------------------------------------------------------------------

def check_vcf_linkage_desequilibrium(conn):
    '''
    Check if table "vcf_linkage_desequilibrium" exists and if there are rows.
    '''

    # check if table "vcf_linkage_desequilibrium" exists
    sentence = '''
               SELECT EXISTS
                   (SELECT 1
                       FROM sqlite_master
                       WHERE type = 'table'
                         AND tbl_name = 'vcf_linkage_desequilibrium'
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

    # check if there are rows when the table "vcf_linkage_desequilibrium" exists
    if control == 1:

        # select the row number
        sentence = '''
                   SELECT EXISTS
                       (SELECT 1
                           FROM vcf_linkage_desequilibrium
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

def get_vcf_linkage_desequilibrium_snp_id_1_list(conn):
    '''
    Get a list of variant identifications with linkage desequilibrium data.
    '''

    # initialize the list
    snp_id_1_list = []

    # query
    sentence = '''
               SELECT DISTINCT snp_id_1
                   FROM vcf_linkage_desequilibrium;
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

def get_vcf_linkage_desequilibrium_list(conn, snp_id_1):
    '''
    Get a list of linkage desequilibrium data corresponding to a variant.
    '''

    # initialize the list
    linkage_desequilibrium_list = []

    # query
    sentence = f'''
                SELECT snp_id_2, dhat, r2, sample_withmd_list_2
                    FROM vcf_linkage_desequilibrium
                    WHERE snp_id_1 = '{snp_id_1}';
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise xlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        linkage_desequilibrium_list.append([row[0], row[1], row[2], row[3]])

    # return the list
    return linkage_desequilibrium_list

#-------------------------------------------------------------------------------

def get_vcf_linkage_desequilibrium_r2_measures(conn):
    '''
    Get global measures of r2 from linkage desequilibrium data.
    '''

    conn.create_aggregate("STDEV", 1, Stdev)

    # initialize data
    avg = 0
    stdev = 0

    # query
    sentence = '''
               SELECT AVG(r2), STDEV(r2)
                   FROM vcf_linkage_desequilibrium
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
                    VALUES ({row_dict["individual_i"]}, {row_dict["individual_j"]}, {row_dict["rbeta"]}, {row_dict["rw"]}, {row_dict["ru"]})
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
# General classes
#-------------------------------------------------------------------------------

class Stdev:
    '''
    This class defines the calculation of standard deviation
    (SQLite does not have a function for standard deviation).
    '''

    #---------------

    def __init__(self):

        self.M = 0.0
        self.S = 0.0
        self.k = 1
 
    #---------------

    def step(self, value):

        if value is None:
            return

        tM = self.M
        self.M += (value - tM) / self.k
        self.S += (value - tM) * (value - self.M)
        self.k += 1
 
    #---------------

    def finalize(self):

        if self.k < 3:
            return None

        return math.sqrt(self.S / (self.k-2))

    #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print('This source contains general functions for the maintenance of the NGShelper SQLite databases in both console mode and gui mode.')
    sys.exit(0)

#-------------------------------------------------------------------------------
