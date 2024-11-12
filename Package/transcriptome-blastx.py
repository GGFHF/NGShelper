#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program annotates transcripts.

This software has been developed by:

    GI en Especies Leñosas (WooSp)
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

import gzip
import optparse
import os
import re
import subprocess
import sys
import time

import xlib

#-------------------------------------------------------------------------------

def main():
    '''
    Main line of the program.
    '''

    # check the operating system
    xlib.check_os()

    # check the setting up of the intrastructure software
    check_infrastructure_software()

    # get and check the options
    parser = build_parser()
    (options, args) = parser.parse_args()
    check_options(options)

    # set environment
    os.environ['BLASTDB'] = options.blast_db

    # if machine type is local:
    if options.machine_type == 'local':

        # set the annotation file
        annotation_file = f'{options.output_directory}/annotation.xml'
        xlib.Message.print('info', f'Annotation file: {annotation_file} ')

        # execute blastn with the transcriptome sequence
        command = f'blastx -num_threads {options.blastx_thread_number} -db {options.protein_database_name} -query {options.transcriptome_file} -evalue {options.e_value} -max_target_seqs {options.max_target_seqs} -outfmt 5 -out {annotation_file}'
        xlib.Message.print('info', f'Run command: {command}')
        rc = subprocess.call(command, shell=True)
        if rc != 0:
            raise xlib.ProgramException('', 'S002', command, rc)

    # if machine type is ngscloud:
    elif options.machine_type == 'ngscloud':

        # initialize the transcript file list of each node
        node_transcript_file_list = []

        # if there is only one node
        if options.node_number == 1:
            node_transcript_file_list.append(options.transcriptome_file)

        # if there are two  or more nodes
        else:

            xlib.Message.print('info', 'Creating the node transcript files ...')

            # open the transcriptome file
            if options.transcriptome_file.endswith('.gz'):
                try:
                    transcriptome_file_id = gzip.open(options.transcriptome_file, mode='rt', encoding='iso-8859-1')
                except Exception as e:
                    raise xlib.ProgramException(e, 'F002', options.transcriptome_file)
            else:
                try:
                    transcriptome_file_id = open(options.transcriptome_file, mode='r', encoding='iso-8859-1')
                except Exception as e:
                    raise xlib.ProgramException(e, 'F001', options.transcriptome_file)

            # initialize the transcript file identification list of each node
            node_transcript_file_id_list = []

            # open a transcript file per node to write
            for i in range(options.node_number):
                node_transcript_file = f'{options.output_directory}/blastx-{i:02d}-transcripts.fasta'
                node_transcript_file_list.append(node_transcript_file)
                try:
                    node_transcript_file_id = open(node_transcript_file, mode='w', encoding='iso-8859-1')
                except Exception as e:
                    raise xlib.ProgramException(e, 'F003', node_transcript_file)
                node_transcript_file_id_list.append(node_transcript_file_id)

            # initialize the count of transcripts
            transcript_count = 0

            # set the pattern of the head records (>transcriptome_info)
            pattern = r'^>(.*)$'

            # read the first record
            record = transcriptome_file_id.readline()

            # while there are records
            while record != '':

                # process the head record
                if record.startswith('>'):

                    # extract the data
                    mo = re.search(pattern, record)
                    transcript_info = mo.group(1)

                    # initialize the transcript sequence
                    transcript_seq = ''

                    # read the next record
                    record = transcriptome_file_id.readline()

                else:

                    # control the FASTA format
                    raise xlib.ProgramException('', 'F006', node_transcript_file, 'FASTA')

                # while there are records and they are sequence
                while record != '' and not record.startswith('>'):

                    # concatenate the record to the transcript sequence
                    transcript_seq += record.strip()

                    # read the next record
                    record = transcriptome_file_id.readline()

                # write the transcript sequence in the corresponding node
                j = transcript_count % options.node_number
                node_transcript_file_id_list[j].write(f'>{transcript_info}\n')
                k = 0
                while k < len(transcript_seq) - xlib.Const.FASTA_RECORD_LEN:
                    node_transcript_file_id_list[j].write(f'{transcript_seq[k:k+xlib.Const.FASTA_RECORD_LEN]}\n')
                    k += xlib.Const.FASTA_RECORD_LEN
                node_transcript_file_id_list[j].write(f'{transcript_seq[k:]}\n')

                # add 1 to trascript count and print it
                transcript_count += 1
                xlib.Message.print('verbose', f'\rProcessed transcripts ... {transcript_count:9d}')

            xlib.Message.print('verbose', '\n')
            xlib.Message.print('info', f'There are {transcript_count} transcripts in the transcriptome file.')

            # close files
            transcriptome_file_id.close()
            for i in range(options.node_number):
                node_transcript_file_id_list[i].close()

            xlib.Message.print('info', 'The transcripts files are created.')

        # set lists related to blastx process and watcher scripts
        blastx_process_script_list = []
        annotation_file_list = []
        control_file_list = []
        log_file_list = []
        watcher_script_list = []
        watcher_log_list = []
        watcher_out_list = []
        watcher_err_list = []
        for i in range(options.node_number):
            blastx_process_script_list.append(f'{options.output_directory}/blastx-{i:02d}-process.sh')
            annotation_file_list.append(f'{options.output_directory}/blastx-{i:02d}-annotation.xml')
            control_file_list.append(f'{options.output_directory}/blastx-{i:02d}-control.txt')
            log_file_list.append(f'{options.output_directory}/blastx-{i:02d}-log.txt')
            watcher_script_list.append(f'{options.output_directory}/blastx-{i:02d}-watcher.sh')
            watcher_log_list.append(f'~/{os.path.basename(options.output_directory)}-blastx-{i:02d}-watcher.log')
            watcher_out_list.append(f'~/{os.path.basename(options.output_directory)}-blastx-{i:02d}-watcher.out')
            watcher_err_list.append(f'~/{os.path.basename(options.output_directory)}-blastx-{i:02d}-watcher.err')

        xlib.Message.print('info', 'Creating the control files ...')

        # create the control files
        for i in range(options.node_number):
            try:
                with open(control_file_list[i], mode='w', encoding='utf8', newline='\n') as control_file_id:
                    control_file_id.write('STARTING')
            except Exception as e:
                raise xlib.ProgramException(e, 'F003', control_file_list[i])

        xlib.Message.print('info', 'The control files are created.')

        xlib.Message.print('info', 'Building the blastx process and watcher scripts ...')

        # build the watcher and blastx process scripts
        for i in range(options.node_number):

            # build the blastx process script
            build_blastx_process_script(blastx_process_script_list[i], options.blastx_thread_number, options.blast_db, options.protein_database_name, node_transcript_file_list[i], options.e_value, options.max_target_seqs, options.max_hsps, options.qcov_hsp_perc, annotation_file_list[i], control_file_list[i], watcher_script_list[i], watcher_out_list[i], watcher_err_list[i])

            # set run permision to the blastx process script
            command = f'chmod u+x {blastx_process_script_list[i]}'
            rc = subprocess.call(command, shell=True)
            if rc != 0:
                raise xlib.ProgramException('', 'S002', command, rc)

            # build the watcher script
            build_watcher_script(watcher_script_list[i], watcher_log_list[i], blastx_process_script_list[i], control_file_list[i], options.email)

            # set run permision to the watcher script
            command = f'chmod u+x {watcher_script_list[i]}'
            rc = subprocess.call(command, shell=True)
            if rc != 0:
                raise xlib.ProgramException('', 'S002', command, rc)

        xlib.Message.print('info', 'The blastx process and watcher scripts are built.')

        xlib.Message.print('info', 'Submiting the blastx process scripts ...')

        # submit the blastx processes
        for i in range(options.node_number):
            command = f'qsub -V -b n -cwd {blastx_process_script_list[i]}'
            rc = subprocess.call(command, shell=True)
            if rc != 0:
                raise xlib.ProgramException('', 'S002', command, rc)

        xlib.Message.print('info', 'The blastx process scripts are submitted.')

        xlib.Message.print('info', 'Verifing blastx processes ...')

        # wait for all blastx processes are completed
        while True:

            # initialize status counters
            starting_count = 0
            running_count = 0
            ok_count = 0
            wrong_count = 0
            other_count = 0

            # check the status of each process node
            for i in range(options.node_number):
                try:
                    with open(control_file_list[i], mode='r', encoding='utf8', newline='\n') as control_file_id:
                        record = control_file_id.read()
                        if record.strip() == 'STARTING':
                            starting_count += 1
                        elif record.strip() == 'RUNNING':
                            running_count += 1
                        elif record.strip() == 'OK':
                            ok_count += 1
                        elif record.strip() == 'WRONG':
                            wrong_count += 1
                        else:
                            other_count += 1
                except Exception as e:
                    raise xlib.ProgramException(e, 'F001', control_file_list[i])

            xlib.Message.print('info', f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())} UTC ... STARTING: {starting_count:02d} - RUNNING: {running_count:02d} - OK: {ok_count:02d} - WRONG: {wrong_count:02d} - OTHERS: {other_count:02d}')

            # check all blastx processes are completed
            if starting_count + running_count == 0:
                break

            # wait a delay time
            time.sleep(xlib.Const.DELAY_TIME)

        # check all blastx processes are ended OK
        if ok_count < options.node_number:
            raise xlib.ProgramException('', 'P002')

        # set concatenation file
        concatenation_file = f'{options.output_directory}/annotation.xml'

        # when there is only one annotation file, rename it
        if range(options.node_number) == 1:
            command = f'mv {annotation_file_list[0]} {concatenation_file}'
            rc = subprocess.call(command, shell=True)
            if rc != 0:
                raise xlib.ProgramException('', 'S002', command, rc)

        # when there are more than one annotation files, concatenate them in the concatenation file
        else:

            xlib.Message.print('info', 'Concatenating the annotation files ...')

            try:

                # open the concatenation file
                concatenation_file_id = open(concatenation_file, mode='w', encoding='utf8', newline='\n')

                # process every annotation file
                for i in range(options.node_number):

                    # set the query number
                    query_number = (i + 1) * xlib.Const.MAX_QUERY_NUMBER_PER_FILE

                    # open the annotation file
                    annotation_file_id = open(annotation_file_list[i], mode='r', encoding='utf8', newline='\n')

                    # read the first record
                    record = annotation_file_id.readline()

                    # while there are records
                    while record != '':

                        # write the record in the concatenation file
                        if record.strip().startswith('<?xml') or record.strip().startswith('<!DOCTYPE') or record.strip().startswith('<BlastOutput') or record.strip().startswith('</BlastOutput_param>') or record.strip().startswith('<Parameters') or record.strip().startswith('</Parameters>'):
                            if i == 0:
                                concatenation_file_id.write(record)
                            else:
                                pass
                        elif record.strip().startswith('</BlastOutput_iterations>') or record.strip().startswith('</BlastOutput>'):
                            if i == options.node_number -1 :
                                concatenation_file_id.write(record)
                            else:
                                pass
                        elif record.strip().startswith('<Iteration_iter-num>'):
                            concatenation_file_id.write(f'  <Iteration_iter-num>{query_number}</Iteration_iter-num>\n')
                            concatenation_file_id.write(f'  <Iteration_query-ID>Query_{query_number}</Iteration_query-ID>>\n')
                            query_number += 1
                        elif record.strip().startswith('<Iteration_query-ID>'):
                            pass
                        elif record.strip() != '':
                            concatenation_file_id.write(record)

                        # read the next record
                        record = annotation_file_id.readline()

                    # close the annotation file
                    annotation_file_id.close()

                # close the concatenation file
                concatenation_file_id.close()

            except Exception as e:
                raise xlib.ProgramException(e, 'F008')

            xlib.Message.print('info', 'The annotation files are concatenated.')

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    parser = optparse.OptionParser()
    parser.add_option('-m', '--machine_type', dest='machine_type', help=f'Machine type: local or ngscloud (default: {xlib.Const.DEFAULT_MACHINE_TYPE})')
    parser.add_option('-n', '--node_number', dest='node_number', help=f'Node number (default: {xlib.Const.DEFAULT_NODE_NUMBER}; it must be 1 if machine type is local)')
    parser.add_option('-t', '--blastx_thread_number', dest='blastx_thread_number', help=f'Threads number using by blastx in every node (default: {xlib.Const.DEFAULT_BLASTX_THREADS_NUMBER})')
    parser.add_option('-d', '--blast_db', dest='blast_db', help='Path of the protein data base directory')
    parser.add_option('-p', '--protein_database_name', dest='protein_database_name', help='Protein database name')
    parser.add_option('-i', '--transcriptome', dest='transcriptome_file', help='Path of a transcriptome file in FASTA format')
    parser.add_option('-e', '--e_value', dest='e_value', help=f'Expectation value (E-value) threshold for saving hits (default: {xlib.Const.DEFAULT_E_VALUE})')
    parser.add_option('-s', '--max_target_seqs', dest='max_target_seqs', help=f'Maximum number of aligned sequences to keep (default: {xlib.Const.DEFAULT_MAX_TARGET_SEQS})')
    parser.add_option('-x', '--max_hsps', dest='max_hsps', help=f'Maximum number of HSPs per subject sequence to save for each query (default: {xlib.Const.DEFAULT_MAX_HSPS})')
    parser.add_option('-c', '--qcov_hsp_perc', dest='qcov_hsp_perc', help=f'Aligments below the specified query coverage per HSPs are removed (default: {xlib.Const.DEFAULT_QCOV_HSP_PERC})')
    parser.add_option('-o', '--output', dest='output_directory', help='Path of a directory where the results will be saved')
    parser.add_option('-l', '--email', dest='email', help='Email direction to send warnings')
    parser.add_option('-v', '--verbose', dest='verbose', help=f'Additional job status info during the run (y: YES; n: NO, default: {xlib.Const.DEFAULT_VERBOSE}).')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def check_options(options):
    '''
    Verity the input option values.
    '''

    # initialize the control variable
    OK = True

    # check machine_type
    if options.machine_type is None:
        options.machine_type = xlib.Const.DEFAULT_MACHINE_TYPE
    else:
        if options.machine_type.lower() not in ['local', 'ngscloud']:
            xlib.Message.print('error', f'*** The machine type value {options.machine_type} is not local or ngscloud.')
            OK = False

    # check node_number
    if options.node_number is None:
        options.node_number = xlib.Const.DEFAULT_NODE_NUMBER
    else:
        try:
            options.node_number = int(options.node_number)
            if options.node_number < 1:
                xlib.Message.print('error', f'*** The node number value {options.node_number} is not an integer greater or equal to 1.')
                OK = False
            elif options.node_number > 1 and options.machine_type == 'local':
                xlib.Message.print('error', f'*** The node number is {options.node_number} but it must be 1 where the machine type is local.')
                OK = False
        except Exception as e:
            xlib.Message.print('error', f'*** The node number value {options.node_number} is not an integer greater or equal to 1.')
            OK = False

    # check blastx_thread_number
    if options.blastx_thread_number is None:
        options.blastx_thread_number = xlib.Const.DEFAULT_BLASTX_THREADS_NUMBER
    else:
        try:
            options.blastx_thread_number = int(options.blastx_thread_number)
            if options.blastx_thread_number < 1:
                xlib.Message.print('error', f'*** The threads number value {options.blastx_thread_number} is not an integer greater or equal to 1.')
                OK = False
        except Exception as e:
            xlib.Message.print('error', f'*** The threads number value {options.blastx_thread_number} is not an integer greater or equal to 1.')
            OK = False

    # check blast_db
    if options.blast_db is None:
        xlib.Message.print('error', '*** The path of the protein data base is not indicated in the options.')
        OK = False
    else:
        if not os.path.isdir(options.blast_db):
            xlib.Message.print('error', f'*** The directory {options.blast_db} does not exist.')
            OK = False

    # check protein_database_name
    if options.protein_database_name is None:
        xlib.Message.print('error', '*** The name of the protein database is not indicated in the options.')
        OK = False

    # check transcriptome_file
    if options.transcriptome_file is None:
        xlib.Message.print('error', '*** A transcritpme file in Fasta format is not indicated in the options.')
        OK = False
    else:
        if not os.path.isfile(options.transcriptome_file):
            xlib.Message.print('error', f'*** The file {options.transcriptome_file} does not exist.')
            OK = False

    # check e_value
    if options.e_value is None:
        options.e_value = xlib.Const.DEFAULT_E_VALUE
    else:
        try:
            options.e_value = float(options.e_value)
        except Exception as e:
            xlib.Message.print('error', f'*** {options.e_value} is not a float number. E-value must be a float number.')
            OK = False

    # check max_target_seqs
    if options.max_target_seqs is None:
        options.max_target_seqs = xlib.Const.DEFAULT_MAX_TARGET_SEQS
    else:
        try:
            options.max_target_seqs = int(options.max_target_seqs)
            if options.max_target_seqs < 1:
                xlib.Message.print('error', f'*** The maximum number of aligned sequences to keep {options.max_target_seqs} is not an integer greater or equal to 1.')
                OK = False
        except Exception as e:
            xlib.Message.print('error', f'*** The maximum number of aligned sequences to keep {options.max_target_seqs} is not an integer greater or equal to 1.')
            OK = False

    # check max_hsps
    if options.max_hsps is None:
        options.max_hsps = xlib.Const.DEFAULT_MAX_HSPS
    else:
        try:
            options.max_hsps = int(options.max_hsps)
            if options.max_hsps < 1:
                xlib.Message.print('error', f'*** The maximum number of HSPs per subject sequence to save for each query {options.max_hsps} is not an integer greater or equal to 1.')
                OK = False
        except Exception as e:
            xlib.Message.print('error', f'*** The maximum number of HSPs per subject sequence to save for each query {options.max_hsps} is not an integer greater or equal to 1.')
            OK = False

    # check qcov_hsp_perc
    if options.qcov_hsp_perc is None:
        options.qcov_hsp_perc = xlib.Const.DEFAULT_QCOV_HSP_PERC
    else:
        try:
            options.qcov_hsp_perc = float(options.qcov_hsp_perc)
            if options.qcov_hsp_perc < 0.0 or options.qcov_hsp_perc > 100.0:
                xlib.Message.print('error', f'*** The query coverage per HSPs {options.qcov_hsp_perc} is not a float between 0.0 and 100.0.')
                OK = False
        except Exception as e:
            xlib.Message.print('error', f'*** The query coverage per HSPs {options.qcov_hsp_perc} is not a float between 0.0 and 100.0.')
            OK = False

    # check output_directory
    if options.output_directory is None:
        xlib.Message.print('error', '*** A directory where the results will be saved base is not indicated in the options.')
        OK = False
    else:
        try:
            if not os.path.exists(options.output_directory):
                os.makedirs(options.output_directory)
        except Exception as e:
            xlib.Message.print('error', f'*** The directory {options.output_directory} is not valid.')
            OK = False

    # check email
    if options.email is None and options.machine_type == 'ngscloud':
        xlib.Message.print('error', '*** An e-mail is not indicated in the options.')
        OK = False

    # check the verbose value
    if options.verbose is None:
        options.verbose = xlib.Const.DEFAULT_VERBOSE
    else:
        if options.verbose.lower() not in ['y', 'n']:
            xlib.Message.print('error', f'The value {options.verbose} of verbose is not y (YES) or n (NO).')
            OK = False
    if options.verbose == 'y':
        xlib.Message.set_verbose_status(True)

    # if there are errors, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def build_blastx_process_script(blastx_process_script, blastx_thread_number, blast_db, protein_database_name, node_transcript_file, e_value, max_target_seqs, max_hsps, qcov_hsp_perc, output_file, control_file, watcher_script, watcher_out, watcher_err):
    '''
    Build the current blastx process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the blastx process script
    try:
        if not os.path.exists(os.path.dirname(blastx_process_script)):
            os.makedirs(os.path.dirname(blastx_process_script))
        with open(blastx_process_script, mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write( '#!/bin/bash\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'export BLASTPLUS_DIR=/apps/Miniconda3/envs/blast/bin\n')
            file_id.write( 'export PATH=$BLASTPLUS_DIR:$PATH\n')
            file_id.write(f'export BLASTDB={blast_db}\n')
            file_id.write( 'SEP="#########################################"\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'function init\n')
            file_id.write( '{\n')
            file_id.write( '    INIT_DATETIME=`date --utc +%s`\n')
            file_id.write( '    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            file_id.write( '    echo "$SEP"\n')
            file_id.write( '    echo "Script started in node $HOSTNAME at $FORMATTED_INIT_DATETIME UTC."\n')
            file_id.write( '    echo "$SEP"\n')
            file_id.write(f'    echo "Creating the control file {control_file} ..."\n')
            file_id.write(f'    echo "RUNNING" > {control_file}\n')
            file_id.write( '    echo "The control file is created."\n')
            file_id.write( '}\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'function submit_watcher\n')
            file_id.write( '{\n')
            file_id.write( '    echo "$SEP"\n')
            file_id.write( '    echo "Submitting watcher ..."\n')
            file_id.write(f'    ssh root@$HOSTNAME "nohup {watcher_script} >{watcher_out} 2>{watcher_err} </dev/null &"\n')
            file_id.write( '}\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'function run_blastx_process\n')
            file_id.write( '{\n')
            file_id.write( '    echo "$SEP"\n')
            file_id.write( '    echo "Running the blastx process  ..."\n')
            file_id.write( '    /usr/bin/time \\\n')
            file_id.write( '        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\\n')
            file_id.write( '        blastx \\\n')
            file_id.write(f'            -num_threads {blastx_thread_number} \\\n')
            file_id.write(f'            -db {protein_database_name} \\\n')
            file_id.write(f'            -query {node_transcript_file} \\\n')
            file_id.write(f'            -evalue {e_value} \\\n')
            file_id.write(f'            -max_target_seqs {max_target_seqs} \\\n')
            file_id.write(f'            -max_hsps {max_hsps} \\\n')
            file_id.write(f'            -qcov_hsp_perc {qcov_hsp_perc} \\\n')
            file_id.write( '            -outfmt 5 \\\n')
            file_id.write(f'            -out {output_file}\n')
            file_id.write( '    RC=$?\n')
            file_id.write( '    if [ $RC -ne 0 ]; then manage_error $RC; fi\n')
            file_id.write( '}\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'function end\n')
            file_id.write( '{\n')
            file_id.write( '    echo "$SEP"\n')
            file_id.write(f'    echo "Updating the control file {control_file} ..."\n')
            file_id.write(f'    echo "OK" > {control_file}\n')
            file_id.write( '    echo "The control file is updated."\n')
            file_id.write( '    END_DATETIME=`date --utc +%s`\n')
            file_id.write( '    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            file_id.write( '    calculate_duration\n')
            file_id.write( '    echo "$SEP"\n')
            file_id.write( '    echo "Script ended OK at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."\n')
            file_id.write( '    echo "$SEP"\n')
            file_id.write( '    exit 0\n')
            file_id.write( '}\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'function manage_error\n')
            file_id.write( '{\n')
            file_id.write( '    echo "$SEP"\n')
            file_id.write(f'    echo "Updating the control file {control_file} ..."\n')
            file_id.write(f'    echo "WRONG" > {control_file}\n')
            file_id.write( '    echo "The control file is updated."\n')
            file_id.write( '    END_DATETIME=`date --utc +%s`\n')
            file_id.write( '    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            file_id.write( '    calculate_duration\n')
            file_id.write( '    echo "$SEP"\n')
            file_id.write( '    echo "ERROR: quast.py returned error $1"\n')
            file_id.write( '    echo "Script ended WRONG at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."\n')
            file_id.write( '    echo "$SEP"\n')
            file_id.write( '    exit 3\n')
            file_id.write( '}\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'function calculate_duration\n')
            file_id.write( '{\n')
            file_id.write( '    DURATION=`expr $END_DATETIME - $INIT_DATETIME`\n')
            file_id.write( '    HH=`expr $DURATION / 3600`\n')
            file_id.write( '    MM=`expr $DURATION % 3600 / 60`\n')
            file_id.write( '    SS=`expr $DURATION % 60`\n')
            file_id.write( '    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`\n')
            file_id.write( '}\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'init\n')
            file_id.write( 'submit_watcher\n')
            file_id.write( 'run_blastx_process\n')
            file_id.write( 'end\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F005', blastx_process_script)

#-------------------------------------------------------------------------------

def build_watcher_script(watcher_script, watcher_log, blastx_process_script, control_file, email):
    '''
    Build the script to watch if the blastx process script is ruuning.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the watcher script
    try:
        if not os.path.exists(os.path.dirname(watcher_script)):
            os.makedirs(os.path.dirname(watcher_script))
        with open(watcher_script, mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write( '#!/bin/bash\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'PS_INFO=~/ps_info.txt\n')
            file_id.write( 'SEP="#########################################"\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'function init\n')
            file_id.write( '{\n')
            file_id.write( '    INIT_DATETIME=`date --utc +%s`\n')
            file_id.write( '    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            file_id.write(f'    echo "$SEP" > {watcher_log}\n')
            file_id.write(f'    echo "Script started in node $HOSTNAME at $FORMATTED_INIT_DATETIME UTC." >> {watcher_log}\n')
            file_id.write( '}\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'function run_watcher\n')
            file_id.write( '{\n')
            file_id.write(f'    echo "$SEP" >> {watcher_log}\n')
            file_id.write(f'    echo "Verifing {blastx_process_script} run ...." >> {watcher_log}\n')
            file_id.write( '    ERROR="NO"\n')
            file_id.write( '    while true; do\n')
            file_id.write(f'        sleep {xlib.Const.DELAY_TIME}\n')
            file_id.write( '        ps -ef | grep -v grep | grep -v /usr/bin/time | grep -v /bin/bash | grep -v /transcriptome-blastx.py | grep blastx | awk \'{print $8}\' > $PS_INFO\n')
            file_id.write( '        test -s $PS_INFO && PROCESS_STATUS="RUNNING" || PROCESS_STATUS="NOT-RUNNING"\n')
            file_id.write( '        rm $PS_INFO\n')
            file_id.write(f'        if [[ -e {control_file} ]]; then\n')
            file_id.write( '            while read LINE; do\n')
            file_id.write( '                CONTROL_FILE_STATUS=$LINE\n')
            file_id.write(f'            done < {control_file}\n')
            file_id.write( '            [[ $CONTROL_FILE_STATUS != "OK" && $PROCESS_STATUS == "NOT-RUNNING" ]] && ERROR="YES"\n')
            file_id.write( '        else\n')
            file_id.write( '            CONTROL_FILE_STATUS="NOT-FOUND"\n')
            file_id.write( '            ERROR="YES"\n')
            file_id.write( '        fi\n')
            file_id.write( '        DATETIME=`date --utc +%s`\n')
            file_id.write( '        FORMATTED_DATETIME=`date --date="@$DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            file_id.write(f'        echo "$FORMATTED_DATETIME UTC ... Process: $PROCESS_STATUS; Control file: $CONTROL_FILE_STATUS; Error: $ERROR" >> {watcher_log}\n')
            file_id.write( '        [[ $PROCESS_STATUS == "NOT-RUNNING" || $ERROR == "YES" ]] && break\n')
            file_id.write( '    done\n')
            file_id.write(f'    echo "Loop while ended." >> {watcher_log}\n')
            file_id.write( '    [[ $ERROR == "YES" ]] && manage_error\n')
            file_id.write(f'    echo "Function run_watcher ended." >> {watcher_log}\n')
            file_id.write( '}\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'function end\n')
            file_id.write( '{\n')
            file_id.write( '    END_DATETIME=`date --utc +%s`\n')
            file_id.write( '    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            file_id.write( '    calculate_duration\n')
            file_id.write(f'    echo "$SEP" >> {watcher_log}\n')
            file_id.write(f'    echo "Script ended OK at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)." >> {watcher_log}\n')
            file_id.write(f'    echo "$SEP" >> {watcher_log}\n')
            file_id.write( '    exit 0\n')
            file_id.write( '}\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'function manage_error\n')
            file_id.write( '{\n')
            file_id.write( '    END_DATETIME=`date --utc +%s`\n')
            file_id.write( '    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            file_id.write( '    calculate_duration\n')
            file_id.write(f'    echo "$SEP" >> {watcher_log}\n')
            file_id.write(f'    echo "Script ended WRONG at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)." >> {watcher_log}\n')
            file_id.write(f'    echo "$SEP" >> {watcher_log}\n')
            file_id.write(f'    RECIPIENT={email}\n')
            file_id.write( '    SUBJECT="NGShelper: $PROCESS"\n')
            file_id.write(f'    MESSAGE="The {os.path.basename(watcher_script)} in node $HOSTNAME ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"\n')
            file_id.write( '    mail --append "Content-type: text/html;"  --subject "$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"\n')
            file_id.write( '    exit 3\n')
            file_id.write( '}\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'function calculate_duration\n')
            file_id.write( '{\n')
            file_id.write( '    DURATION=`expr $END_DATETIME - $INIT_DATETIME`\n')
            file_id.write( '    HH=`expr $DURATION / 3600`\n')
            file_id.write( '    MM=`expr $DURATION % 3600 / 60`\n')
            file_id.write( '    SS=`expr $DURATION % 60`\n')
            file_id.write( '    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`\n')
            file_id.write( '}\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( 'init\n')
            file_id.write( 'run_watcher\n')
            file_id.write( 'end\n')
    except Exception as e:
        raise xlib.ProgramException(e, 'F005', watcher_script)

#-------------------------------------------------------------------------------

def check_infrastructure_software():
    '''
    Check if the infrastructure software is setup.
    '''

    # initialize the control variable
    OK = True

    #check blastx
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        command = 'blastx -h >/dev/null 2>&1'
    elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        command = 'blastx.exe -h 1>null 2>&1'
    rc = subprocess.call(command, shell=True)
    if rc != 0:
        OK = False
        xlib.Message.print('error', 'blastx is not found.')

    # if there is software not found, exit with exception
    if not OK:
        raise xlib.ProgramException('', 'I001')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
