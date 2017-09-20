#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

'''
This source ... .
'''
#-------------------------------------------------------------------------------

import contextlib
import itertools
import optparse
import os
import re
import subprocess
import sys
import threading
import time

#-------------------------------------------------------------------------------

def main(argv):
    '''
    Main line of the program.
    '''

    # verify the operating system
    verify_os()

    # verify the setting up of the intrastructure software
    verify_infrastructure_software()

    # get and verify the options
    parser = build_parser()
    (options, args) = parser.parse_args()
    verify_options(options)
 
    # set environment
    os.environ['BLASTDB'] = options.blast_db

    # if machine type is local:
    if options.machine_type == 'local':

        # set the annotation file
        annotation_file = '{0}/annotation.xml'.format(options.output_directory)
        Message.print('info', 'Annotation file: {0} '.format(annotation_file))

        # execute blastn with the transcriptome sequence
        command = 'blastx -num_threads {0} -db {1} -query {2} -evalue {3} -max_target_seqs {4} -outfmt 5 -out {5}'.format(options.blastx_thread_number, options.protein_database_name, options.transcriptome_file, options.e_value, options.max_target_seqs, annotation_file)
        Message.print('info', 'Run command: {0}'.format(command))
        rc = subprocess.call(command, shell=True)
        if rc != 0:
            raise ProgramException('S002', command, rc)

    # if machine type is ngscloud:
    elif options.machine_type == 'ngscloud':

        # initialize the transcript file list of each node
        node_transcript_file_list = []

        # if there is only one node
        if options.node_number == 1:
            node_transcript_file_list.append(options.transcriptome_file)

        # if there are two  or more nodes
        else:

            Message.print('info', 'Creating the node transcript files ...')

            # open the transcriptome file
            if options.transcriptome_file.endswith('.gz'):
                try:
                    transcriptome_file_id = gzip.open(options.transcriptome_file, mode='rt', encoding='iso-8859-1')
                except:
                    raise ProgramException('F002', options.transcriptome_file)
            else:
                try:
                    transcriptome_file_id = open(options.transcriptome_file, mode='r', encoding='iso-8859-1')
                except:
                    raise ProgramException('F001', options.transcriptome_file)

            # initialize the transcript file identification list of each node
            node_transcript_file_id_list = []

            # open a transcript file per node to write
            for i in range(options.node_number):
                node_transcript_file = '{0}/node-{1}-transcripts.fasta'.format(options.output_directory, i)
                node_transcript_file_list.append(node_transcript_file)
                try:
                    node_transcript_file_id = open(node_transcript_file, mode='w', encoding='iso-8859-1')
                except:
                    raise ProgramException('F004', node_transcript_file)
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
                    raise ProgramException('F005', genfile, 'FASTA')

                # while there are records and they are sequence
                while record != '' and not record.startswith('>'):

                    # concatenate the record to the transcript sequence
                    transcript_seq += record.strip()

                    # read the next record
                    record = transcriptome_file_id.readline()

                # write the transcript sequence in the corresponding node
                j = transcript_count % options.node_number
                node_transcript_file_id_list[j].write('>{0}\n'.format(transcript_info))
                k = 0
                while k < len(transcript_seq) - Const.FASTA_RECORD_LEN:
                    node_transcript_file_id_list[j].write('{0}\n'.format(transcript_seq[k:k+Const.FASTA_RECORD_LEN]))
                    k += Const.FASTA_RECORD_LEN
                node_transcript_file_id_list[j].write('{0}\n'.format(transcript_seq[k:]))

                # add 1 to trascript count and print it
                transcript_count += 1
                Message.print('verbose', '\rProcessed transcripts ... {0:9d}'.format(transcript_count))

            Message.print('verbose', '\n')
            Message.print('info', 'There are {0} transcripts in the transcriptome file.'.format(transcript_count))

            # close files
            transcriptome_file_id.close()
            for i in range(options.node_number):
                node_transcript_file_id_list[i].close()

            Message.print('info', 'The transcripts files are created.')

        # set lists to blastx process scripts, blastx process starters, annotation files, control files and log files
        blastx_process_script_list = []
        annotation_file_list = []
        control_file_list = []
        log_file_list = []
        for i in range(options.node_number):
            blastx_process_script_list.append('{0}/node-{1}-blastx-process.sh'.format(options.output_directory, i))
            annotation_file_list.append('{0}/node-{1}-annotation.xml'.format(options.output_directory, i))
            control_file_list.append('{0}/node-{1}-control.txt'.format(options.output_directory, i))
            log_file_list.append('{0}/node-{1}-log.txt'.format(options.output_directory, i))

        Message.print('info', 'Creating the control files ...')

        # create the control files
        for i in range(options.node_number):
            try:
                with open(control_file_list[i], mode='w', encoding='utf8', newline='\n') as control_file_id:
                    control_file_id.write('STARTING')
            except:
                raise ProgramException('F004', control_file_list[i])

        Message.print('info', 'The control files are created.')

        Message.print('info', 'Building the blastx process scripts ...')

        # build the blastx process scripts and process starters
        for i in range(options.node_number):

            # build the blastx process script
            build_blastx_process_script(blastx_process_script_list[i], options.blastx_thread_number, options.blast_db, options.protein_database_name, node_transcript_file_list[i], options.e_value, options.max_target_seqs, annotation_file_list[i], control_file_list[i])

            # set run permision to the the blastx process script
            command = 'chmod u+x {0}'.format(blastx_process_script_list[i])
            rc = subprocess.call(command, shell=True)
            if rc != 0:
                raise ProgramException('S002', command, rc)

        Message.print('info', 'The blastx process scripts are built.')

        Message.print('info', 'Submiting the blastx process scripts ...')

        # submit the blastx processes
        for i in range(options.node_number):
            command = 'qsub -V -b n -cwd {0}'.format(blastx_process_script_list[i])
            rc = subprocess.call(command, shell=True)
            if rc != 0:
                raise ProgramException('S002', command, rc)

        Message.print('info', 'The blastx process scripts are submitted.')

        # wait for all blastx processes are completed
        while True:

            Message.print('info', 'Verifing all blastx processes are completed at {0} UTC ...'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())))

            # initialize status counts
            starting_count = 0
            running_count = 0
            ok_count = 0
            wrong_count = 0
            other_count = 0

            # verify the status of each process node
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
                except:
                    raise ProgramException('F001', control_file_list[i])

            Message.print('info', 'STARTING: {0} - RUNNING: {1} - OK: {2} - WRONG: {3} - OTHERS: {4}'.format(starting_count, running_count, ok_count, wrong_count, other_count))

            # verify all blastx processes are completed
            if starting_count + running_count == 0:
                break

            # wait a delay time
            time.sleep(Const.DELAY_TIME) 

        # verify all blastx processes are ended OK
        if ok_count < options.node_number:
            raise ProgramException('P002')

        # set concatenation file
        concatenation_file = '{0}/annotation.xml'.format(options.output_directory)

        # when there is only one annotation file, rename it
        if range(options.node_number) == 1:
            command = 'mv {0} {1}'.format(annotation_file_list[0], concatenation_file)
            rc = subprocess.call(command, shell=True)
            if rc != 0:
                raise ProgramException('S002', command, rc)

        # when there are more than one annotation files, concatenate them in the concatenation file
        else:

            Message.print('info', 'Concatenating the annotation files ...')

            try:

                # open the concatenation file
                concatenation_file_id = open(concatenation_file, mode='w', encoding='utf8', newline='\n')
                
                # process every annotation file
                for i in range(options.node_number):

                    # set the query number
                    query_number = (i + 1) * Const.MAX_QUERY_NUMBER_PER_FILE

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
                            concatenation_file_id.write('  <Iteration_iter-num>{0}</Iteration_iter-num>\n'.format(query_number))
                            concatenation_file_id.write('  <Iteration_query-ID>Query_{0}</Iteration_query-ID>>\n'.format(query_number))
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

            except:
                raise ProgramException('F006')

            Message.print('info', 'The annotation files are concatenated.')

#-------------------------------------------------------------------------------

def build_blastx_process_script(blastx_process_script, blastx_thread_number, blast_db, protein_database_name, node_transcript_file, e_value, max_target_seqs, output_file, control_file):
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
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('export BLASTPLUS_DIR=/apps/Miniconda3/envs/blast/bin'))
            file_id.write('{0}\n'.format('export PATH=$BLASTPLUS_DIR:$PATH'))
            file_id.write('{0}\n'.format('export BLASTDB={0}'.format(blast_db)))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME at $FORMATTED_INIT_DATETIME UTC."'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Creating the control file {0} ..."'.format(control_file)))
            file_id.write('{0}\n'.format('    echo "RUNNING" > {0}'.format(control_file)))
            file_id.write('{0}\n'.format('    echo "The control file is created."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function run_blastx_process'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Running the blastx process ...."'))
            file_id.write('{0}\n'.format('    /usr/bin/time \\'))
            file_id.write('{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            file_id.write('{0}\n'.format('        blastx \\'))
            file_id.write('{0}\n'.format('            -num_threads {0} \\'.format(blastx_thread_number)))
            file_id.write('{0}\n'.format('            -db {0} \\'.format(protein_database_name)))
            file_id.write('{0}\n'.format('            -query {0} \\'.format(node_transcript_file)))
            file_id.write('{0}\n'.format('            -evalue {0} \\'.format(e_value)))
            file_id.write('{0}\n'.format('            -max_target_seqs {0} \\'.format(max_target_seqs)))
            file_id.write('{0}\n'.format('            -outfmt 5 \\'))
            file_id.write('{0}\n'.format('            -out {0}'.format(output_file)))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error $RC; fi'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function end'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Updating the control file {0} ..."'.format(control_file)))
            file_id.write('{0}\n'.format('    echo "OK" > {0}'.format(control_file)))
            file_id.write('{0}\n'.format('    echo "The control file is updated."'))
            file_id.write('{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    calculate_duration'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script ended OK at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    exit 0'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function manage_error'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Updating the control file {0} ..."'.format(control_file)))
            file_id.write('{0}\n'.format('    echo "WRONG" > {0}'.format(control_file)))
            file_id.write('{0}\n'.format('    echo "The control file is updated."'))
            file_id.write('{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    calculate_duration'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "ERROR: quast.py returned error $1"'))
            file_id.write('{0}\n'.format('    echo "Script ended WRONG at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    exit $1'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function calculate_duration'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    DURATION=`expr $END_DATETIME - $INIT_DATETIME`'))
            file_id.write('{0}\n'.format('    HH=`expr $DURATION / 3600`'))
            file_id.write('{0}\n'.format('    MM=`expr $DURATION % 3600 / 60`'))
            file_id.write('{0}\n'.format('    SS=`expr $DURATION % 60`'))
            file_id.write('{0}\n'.format('    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('init'))
            file_id.write('{0}\n'.format('run_blastx_process'))
            file_id.write('{0}\n'.format('end'))
    except:
        raise ProgramException('F003', blastx_process_script)

#-------------------------------------------------------------------------------

def verify_os():
    '''
    Verify the operating system.
    '''    

    # if the operating system is unsupported, exit with exception
    if not sys.platform.startswith('linux') and not sys.platform.startswith('darwin') and not sys.platform.startswith('win32') and not sys.platform.startswith('cygwin'):
        raise ProgramException('S001', sys.platform)

#-------------------------------------------------------------------------------

def verify_infrastructure_software():
    '''
    Verify if the infrastructure software is setup.
    '''    

    # initialize the control variable
    OK = True

    #verify blastx
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        command = 'blastx -h >/dev/null 2>&1'
    elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        command = 'blastx.exe -h 1>null 2>&1'
    rc = subprocess.call(command, shell=True)
    if rc != 0:
        OK = False
        Message.print('error', 'blastx has not been found.')

    # if there is software not found, exit with exception
    if not OK:
        raise ProgramException('I001')

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available options.
    '''

    #create the parser and add options
    parser = optparse.OptionParser()
    parser.add_option('-m', '--machine_type', dest='machine_type', help='Machine type: local or ngscloud (default: {0})'.format(Const.DEFAULT_MACHINE_TYPE))
    parser.add_option('-n', '--node_number', dest='node_number', help='Node number (default: {0}; it must be 1 if machine type is local)'.format(Const.DEFAULT_NODE_NUMBER))
    parser.add_option('-t', '--blastx_thread_number', dest='blastx_thread_number', help='Threads number using by blastx in every node (default: {0})'.format(Const.DEFAULT_BLASTX_THREADS_NUMBER))
    parser.add_option('-d', '--blast_db', dest='blast_db', help='Path of the protein data base directory')
    parser.add_option('-p', '--protein_database_name', dest='protein_database_name', help='Protein database name')
    parser.add_option('-i', '--transcriptome', dest='transcriptome_file', help='Path of a transcriptome file in FASTA format')
    parser.add_option('-e', '--e_value', dest='e_value', help='Expectation value (E-value) threshold for saving hits (default: {0})'.format(Const.DEFAULT_E_VALUE))
    parser.add_option('-s', '--max_target_seqs', dest='max_target_seqs', help='Maximum number of aligned sequences to keep (default: {0})'.format(Const.DEFAULT_MAX_TARGET_SEQS))
    parser.add_option('-o', '--output', dest='output_directory', help='Path of a directory where the results will be saved')
    parser.add_option('-v', '--verbose', dest='verbose', help='Additional job status info during the run (y: YES; n: NO, default: {0}).'.format(Const.DEFAULT_VERBOSE))

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def verify_options(options):
    '''
    Verity the input options data.abundancebin
    '''

    # initialize the control variable
    OK = True

    # verify machine_type
    if options.machine_type is None:
        options.machine_type = Const.DEFAULT_MACHINE_TYPE
    else:
        if options.machine_type.lower() not in ['local', 'ngscloud']:
            Message.print('error', '*** The machine type value {0} is not local or ngscloud.'.format(options.machine_type))
            OK = False

    # verify node_number
    if options.node_number is None:
        options.node_number = Const.DEFAULT_NODE_NUMBER
    else:
        try:
            options.node_number = int(options.node_number)
            if options.node_number < 1:
                Message.print('error', '*** The node number value {0} is not a integer greater or equal to 1.'.format(options.node_number))
                OK = False
            elif options.node_number > 1 and options.machine_type == 'local':
                Message.print('error', '*** The node number is {0} but it must be 1 where the machine type is local.'.format(options.node_number))
                OK = False
        except:
            Message.print('error', '*** The node number value {0} is not a integer greater or equal to 1.'.format(options.node_number))
            OK = False

    # verify blastx_thread_number
    if options.blastx_thread_number is None:
        options.blastx_thread_number = Const.DEFAULT_BLASTX_THREADS_NUMBER
    else:
        try:
            options.blastx_thread_number = int(options.blastx_thread_number)
            if options.blastx_thread_number < 1:
                Message.print('error', '*** The threads number value {0} is not a integer greater or equal to 1.'.format(options.blastx_thread_number))
                OK = False
        except:
            Message.print('error', '*** The threads number value {0} is not a integer greater or equal to 1.'.format(options.blastx_thread_number))
            OK = False

    # verify blast_db
    if options.blast_db is None:
        Message.print('error', '*** The path of the protein data base has not been indicated in the options.')
        OK = False
    else:
        if not os.path.isdir(options.blast_db):
            Message.print('error', '*** The directory {0} does not exist.'.format(options.blast_db))
            OK = False

    # verify protein_database_name
    if options.protein_database_name is None:
        Message.print('error', '*** The name of the protein database has not been indicated in the options.')
        OK = False

    # verify transcriptome_file
    if options.transcriptome_file is None:
        Message.print('error', '*** A transcritpme file in Fasta format has not been indicated in the options.')
        OK = False
    else:
        if not os.path.isfile(options.transcriptome_file):
            Message.print('error', '*** The file {0} does not exist.'.format(options.transcriptome_file))
            OK = False

    # verify e_value
    if options.e_value is None:
        options.e_value = Const.DEFAULT_E_VALUE
    else:
        try:
            options.e_value = float(options.e_value)
        except:
            Message.print('error', '*** {0} is not a float number. E-value must be a float number.'.format(options.e_value))
            OK = False

    # verify max_target_seqs
    if options.max_target_seqs is None:
        options.max_target_seqs = Const.DEFAULT_DEFAULT_MAX_TARGET_SEQS
    else:
        try:
            options.max_target_seqs = int(options.max_target_seqs)
            if options.max_target_seqs < 1:
                Message.print('error', '*** The maximum number of aligned sequences to keep {0} is not a integer greater or equal to 1.'.format(options.max_target_seqs))
                OK = False
        except:
            Message.print('error', '*** The maximum number of aligned sequences to keep {0} is not a integer greater or equal to 1.'.format(options.max_target_seqs))
            OK = False

    # verify output_directory
    if options.output_directory is None:
        Message.print('error', '*** A directory where the results will be saved base has not been indicated in the options.')
        OK = False
    else:
        try:
            if not os.path.exists(options.output_directory):
                os.makedirs(options.output_directory)
        except:
            Message.print('error', '*** The directory {0} is not valid.'.format(options.output_directory))
            OK = False

    # verify the verbose value
    if options.verbose is None:
        options.verbose = Const.DEFAULT_VERBOSE
    else:
        if options.verbose.lower() not in ['y', 'n']:
            Message.print('error', 'The value {0} of verbose is not y (YES) or n (NO).'.format(options.verbose))
            OK = False
    if options.verbose == 'y':
        Message.set_verbose_status(True)

    # if there are errors, exit with exception
    if not OK:
        raise ProgramException('P001', sys.platform)

#-------------------------------------------------------------------------------
 
class Const():
    '''
    This class has attributes with values will be used as constants.
    '''

    #---------------

    DEFAULT_MACHINE_TYPE = 'local'
    DEFAULT_NODE_NUMBER = 1
    DEFAULT_BLASTX_THREADS_NUMBER = 1
    DEFAULT_E_VALUE = 1E-6
    DEFAULT_MAX_TARGET_SEQS = 10
    DEFAULT_VERBOSE = 'n'

   #---------------

    FASTA_RECORD_LEN = 60
    MAX_QUERY_NUMBER_PER_FILE = 1000000
    DELAY_TIME = 60

   #---------------

#-------------------------------------------------------------------------------

class ProgramException(Exception):
    '''
    This class controls various exceptions that can occur in the execution of the application.
    '''

   #---------------

    def __init__(self, code_exception, param1='', param2='', param3=''):
        '''Initialize the object to manage a passed exception.''' 

        # manage the code of exception
        if code_exception == 'EXIT':
            sys.exit(0)
        elif code_exception == 'F001':
            Message.print('error', '*** ERROR {0}: This file {1} can not be opened.'.format(code_exception, param1))
            sys.exit(1)
        elif code_exception == 'F002':
            Message.print('error', '*** ERROR {0}: This GZ compressed file {1} can not be opened.'.format(code_exception, param1))
            sys.exit(1)
        elif code_exception == 'F003':
            Message.print('error', '*** ERROR {0}: This file {1} can not be built.'.format(code_exception, param1))
            sys.exit(1)
        elif code_exception == 'F004':
            Message.print('error', '*** ERROR {0}: This file {1} can not be written.'.format(code_exception, param1))
            sys.exit(1)
        elif code_exception == 'F005':
            Message.print('error', '*** ERROR {0}: Format file {1} is not {2}.'.format(code_exception, param1, param2))
        elif code_exception == 'F006':
            Message.print('error', '*** ERROR {0}: The output xml files can not be concatenated.'.format(code_exception))
        elif code_exception == 'I001':
            Message.print('error', '*** ERROR {0}: The infrastructure software is not setup.'.format(code_exception))
            sys.exit(1)
        elif code_exception == 'P001':
            Message.print('error', '*** ERROR {0}: This program has parameters with invalid values.'.format(code_exception))
            sys.exit(1)
        elif code_exception == 'P002':
            Message.print('error', '*** ERROR {0}: There are some node processes ended NOT OK.'.format(code_exception))
            sys.exit(1)
        elif code_exception == 'S001':
            Message.print('error', '*** ERROR {0}: The {1} OS is not supported.'.format(code_exception, param1))
            sys.exit(1)
        elif code_exception == 'S002':
            Message.print('error', '*** ERROR {0}: RC {1} in command {2}'.format(code_exception, param2, param1))
            sys.exit(1)
        else:
            Message.print('error', '*** ERROR {0}: This exception is not managed.'.format(code_exception), file=error_output)
            sys.exit(1)

   #---------------

#-------------------------------------------------------------------------------
 
class Message():
    '''
    This class controls the informative messages printed on the console.
    '''

    #---------------

    verbose_status = False
    trace_status = False

    #---------------

    def set_verbose_status(status):

        Message.verbose_status = status

    #---------------

    def print(message_type, message_text):

        if message_type == 'info':
            print(message_text, file=sys.stdout)
            sys.stdout.flush()
        elif message_type == 'verbose' and Message.verbose_status:
            sys.stdout.write(message_text)
            sys.stdout.flush()
        elif message_type == 'trace' and Message.trace_status:
            print(message_text, file=sys.stdout)
            sys.stdout.flush()
        elif message_type == 'error':
            print(message_text, file=sys.stderr)
            sys.stderr.flush()

    #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
