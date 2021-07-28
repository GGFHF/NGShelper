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
Description: This program launches several PHASE processes with a input file list.
'''

#-------------------------------------------------------------------------------

import argparse
import gzip
import pathlib
import os
from re import X
import sys

import xlib

#-------------------------------------------------------------------------------

def main(argv):
    '''
    Main line of the program.
    '''

    # check the operating system
    xlib.check_os()

    # check the WSL installation
    if sys.platform.startswith('win32'):
        command = 'whoami'
        rc = xlib.run_command(command, xlib.DevNull(), is_script=False)
        if rc == 0:
            pass
        else:
            print('*** ERROR: The WSL 2 is not installed.')
            sys.exit(1)

    # get and check the arguments
    parser = build_parser()
    args = parser.parse_args()
    check_args(args)

    # launch PHASE processes with a input file list
    launch_phase_processes(args.phase_dir, args.processes_number, args.input_dir, args.output_dir, args.iterations_number, args.thinning_interval, args.burn_in, args.other_parameters)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program launches several PHASE processes with a input file list.'
    text = f'{xlib.get_project_name()} v{xlib.get_project_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'
    parser.add_argument('--phasedir', dest='phase_dir', help='Path of the directoty of the PHASE application installation (mandatory).')
    parser.add_argument('--processes', dest='processes_number', help=f'Number of process to be launched; default: {xlib.Const.DEFAULT_PROCESSES_NUMBER}.')
    parser.add_argument('--indir', dest='input_dir', help='Path of the directoty where the PHASE application input files are located (mandatory).')
    parser.add_argument('--outdir', dest='output_dir', help='Path of the directoty where the PHASE application output files are generated (mandatory).')
    parser.add_argument('--iterations', dest='iterations_number', help=f'Number of iterations; default: {xlib.Const.DEFAULT_ITERATIONS_NUMBER}.')
    parser.add_argument('--thinning', dest='thinning_interval', help=f'Thinning interval; default: {xlib.Const.DEFAULT_THINNING_INTERVAL}.')
    parser.add_argument('--burnin', dest='burn_in', help=f'Burn-in; default: {xlib.Const.DEFAULT_BURN_IN}.')
    parser.add_argument('--otherparams', dest='other_parameters', help='Other parameters (between quotation marks) to be included in the PHASE run or NONE; default: NONE.')
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
        xlib.Message.print('error', '*** The directoty of the PHASE application installation is not indicated in the input arguments.')
        OK = False
    elif not os.path.isdir(args.phase_dir):
        xlib.Message.print('error', f'*** The directory {args.phase_dir} does not exist.')
        OK = False

    # check "processes_number"
    if args.processes_number is None:
        args.processes_number = xlib.Const.DEFAULT_PROCESSES_NUMBER
    elif not xlib.check_int(args.processes_number, minimum=1):
        xlib.Message.print('error', 'The processes number has to be a integer number greater than or equal to 1.')
        OK = False
    else: 
        args.processes_number = int(args.processes_number)

    # check "input_dir"
    if args.input_dir is None:
        xlib.Message.print('error', '*** The directoty where the PHASE application input files are located is not indicated in the input arguments.')
        OK = False
    elif not os.path.isdir(args.input_dir):
        xlib.Message.print('error', f'*** The directory {args.input_dir} does not exist.')
        OK = False

    # check "output_dir"
    if args.output_dir is None:
        xlib.Message.print('error', '*** The directoty where the PHASE application output files are generated is not indicated in the input arguments.')
        OK = False
    elif not os.path.isdir(args.output_dir):
        xlib.Message.print('error', f'*** The directory {args.output_dir} does not exist.')
        OK = False

    # check "iterations_number"
    if args.iterations_number is None:
        args.iterations_number = xlib.Const.DEFAULT_ITERATIONS_NUMBER
    elif not xlib.check_int(args.iterations_number, minimum=1):
        xlib.Message.print('error', 'The processes number has to be a integer number greater than or equal to 1.')
        OK = False
    else: 
        args.iterations_number = int(args.iterations_number)

    # check "thinning_interval"
    if args.thinning_interval is None:
        args.thinning_interval = xlib.Const.DEFAULT_THINNING_INTERVAL
    elif not xlib.check_int(args.thinning_interval, minimum=1):
        xlib.Message.print('error', 'The processes number has to be a integer number greater than or equal to 1.')
        OK = False
    else: 
        args.thinning_interval = int(args.thinning_interval)

    # check "burn_in"
    if args.burn_in is None:
        args.burn_in = xlib.Const.DEFAULT_BURN_IN
    elif not xlib.check_int(args.burn_in, minimum=1):
        xlib.Message.print('error', 'The processes number has to be a integer number greater than or equal to 1.')
        OK = False
    else: 
        args.burn_in = int(args.burn_in)

    # check "other_parameters"
    if args.other_parameters is None or args.other_parameters.upper() == 'NONE':
        args.other_parameters = 'NONE'

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

def launch_phase_processes(phase_dir, processes_number, input_dir, output_dir, iterations_number,thinning_interval, burn_in, other_parameters):
    '''
    '''

    # initialize the counter of rename files
    input_file_counter = 0

    # build the input file list
    input_file_list = []
    for path in pathlib.Path(input_dir).iterdir():
        if path.is_file():

            # add 1 to the counter of rename files
            input_file_counter += 1

            # add file name to the input file list
            input_file_list.append(os.path.basename(path))

            # print the counter of renamed files
            xlib.Message.print('verbose', f'\rInput files: {input_file_counter}')
    xlib.Message.print('verbose', '\n')

    # set the files number list
    files_number_list = []
    file_number = input_file_counter // processes_number
    remainder = input_file_counter % processes_number
    for i in range(processes_number):
        if i < remainder:
            files_number_list.append(file_number + 1)
        else:
            files_number_list.append(file_number)
    xlib.Message.print('info', f'files_number_list: {files_number_list}')

    # build the path file with input files of each process
    input_files_list_file_list = []
    for process_number in range(processes_number):
        input_files_list_file_list.append(f'{output_dir}{os.sep}phase-process-{process_number}-file-list.txt')

    # write input files corrrespondig to each process
    start = 0
    for process_number in range(processes_number):
        try:
            input_files_list_file_id = open(input_files_list_file_list[process_number], mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise xlib.ProgramException(e, 'F003', input_files_list_file_list[process_number])
        end = start + files_number_list[process_number]
        for i in range(start, end):
            input_files_list_file_id.write(f'{input_file_list[i]}\n')
        input_files_list_file_id.close()
        start = end 

    # create scripts of PHASE processes
    xlib.Message.print('info', f'{xlib.get_separator()}\n')
    for process_number in range(processes_number):
        xlib.Message.print('info', f'Creating the process script {get_phase_process_script(process_number, output_dir)} ...\n')
        build_phase_process_script(process_number, phase_dir, input_dir, input_files_list_file_list[process_number], output_dir, iterations_number, thinning_interval, burn_in, other_parameters)
        xlib.Message.print('info', 'The script is created.\n')

    # set run permision to the scripts of PHASE processes
    xlib.Message.print('info', f'{xlib.get_separator()}\n')
    for process_number in range(processes_number):
        script = get_phase_process_script(process_number, output_dir)
        xlib.Message.print('info', f'Setting on the run permision of {script} ...\n')
        if sys.platform.startswith('win32'):
            script = xlib.windows_path_2_wsl_path(script)
        command = f'chmod u+x {script}'
        rc = xlib.run_command(command, sys.stdout, is_script=False)
        if rc == 0:
            xlib.Message.print('info', 'The run permision is set.\n')
        else:
            raise xlib.ProgramException('', 'S002', command, rc)

    # create starters of PHASE processes
    xlib.Message.print('info', f'{xlib.get_separator()}\n')
    for process_number in range(processes_number):
        xlib.Message.print('info', f'Creating the process starter {get_phase_process_starter(process_number, output_dir)} ...\n')
        build_phase_process_starter(process_number, output_dir)
        xlib.Message.print('info', 'The script is created.\n')

    # set run permision to the starters of PHASE processes
    xlib.Message.print('info', f'{xlib.get_separator()}\n')
    for process_number in range(processes_number):
        starter = get_phase_process_starter(process_number, output_dir)
        xlib.Message.print('info', f'Setting on the run permision of {starter} ...\n')
        if sys.platform.startswith('win32'):
            starter = xlib.windows_path_2_wsl_path(starter)
        command = f'chmod u+x {starter}'
        rc = xlib.run_command(command, sys.stdout, is_script=False)
        if rc == 0:
            xlib.Message.print('info', 'The run permision is set.\n')
        else:
            raise xlib.ProgramException('', 'S002', command, rc)

    # launch PHASE processes
    xlib.Message.print('info', f'{xlib.get_separator()}\n')
    for process_number in range(processes_number):
        starter = get_phase_process_starter(process_number, output_dir)
        xlib.Message.print('info', f'Launching the process {starter} ...\n')
        if sys.platform.startswith('win32'):
            starter = xlib.windows_path_2_wsl_path(starter)
        command = f'{starter} &'
        rc = xlib.run_command(command, sys.stdout, is_script=True)
        if rc == 0:
            xlib.Message.print('info', 'The script is submitted.\n')
        else:
            raise xlib.ProgramException('', 'S002', command, rc)

#-------------------------------------------------------------------------------

def build_phase_process_script(process_number, phase_dir, input_dir, input_files_list_file, output_dir, iterations_number, thinning_interval, burn_in, other_parameters):
    '''
    Build the PHASE process script corresponding to the process number
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the PHASE process script
    try:
        if not os.path.exists(os.path.dirname(get_phase_process_script(process_number, output_dir))):
            os.makedirs(os.path.dirname(get_phase_process_script(process_number, output_dir)))
        with open(get_phase_process_script(process_number, output_dir), mode='w', encoding='iso-8859-1', newline='\n') as script_file_id:
            script_file_id.write( '#!/bin/bash\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'SEP="#########################################"\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write(f'export PATH={phase_dir}:$PATH\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function init\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    INIT_DATETIME=`date --utc +%s`\n')
            script_file_id.write( '    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    echo "Script started at $FORMATTED_INIT_DATETIME+00:00."\n')
            script_file_id.write( '}\n')
            if sys.platform.startswith('win32'):
                input_dir = xlib.windows_path_2_wsl_path(input_dir)
                output_dir = xlib.windows_path_2_wsl_path(output_dir)
                input_files_list_file = xlib.windows_path_2_wsl_path(input_files_list_file)
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function run_phase_process\n')
            script_file_id.write( '{\n')
            script_file_id.write(f'    cd {output_dir}\n')
            script_file_id.write( '    while read FILE_NAME; do\n')
            script_file_id.write( '        echo "$SEP"\n')
            script_file_id.write(f'        IN_FILE={input_dir}/$FILE_NAME\n')
            script_file_id.write(f'        OUT_FILE={output_dir}/$FILE_NAME\n')
            script_file_id.write( '        echo "Processing file $IN_FILE ..."\n')
            script_file_id.write( '        BASENAME=`basename $IN_FILE`\n')
            script_file_id.write( '        /usr/bin/time \\\n')
            script_file_id.write(f'            PHASE \\\n')
            script_file_id.write(f'                -d1 \\\n')
            if other_parameters != 'NONE':
                script_file_id.write(f'                {other_parameters} \\\n')
            script_file_id.write( '                $IN_FILE \\\n')
            script_file_id.write( '                $OUT_FILE \\\n')
            script_file_id.write(f'                {iterations_number} \\\n')
            script_file_id.write(f'                {thinning_interval} \\\n')
            script_file_id.write(f'                {burn_in}\n')
            script_file_id.write( '            RC=$?\n')
            script_file_id.write( '            # -- if [ $RC -ne 0 ]; then manage_error PHASE $RC; fi\n')
            script_file_id.write( '        echo "The file is processed."\n')
            script_file_id.write(f'    done < {input_files_list_file}\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function end\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    END_DATETIME=`date --utc +%s`\n')
            script_file_id.write( '    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            script_file_id.write( '    calculate_duration\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    echo "Script ended OK at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    exit 0\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function manage_error\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    END_DATETIME=`date --utc +%s`\n')
            script_file_id.write( '    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            script_file_id.write( '    calculate_duration\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    echo "ERROR: $1 returned error $2"\n')
            script_file_id.write( '    echo "Script ended WRONG at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    exit 3\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function calculate_duration\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    DURATION=`expr $END_DATETIME - $INIT_DATETIME`\n')
            script_file_id.write( '    HH=`expr $DURATION / 3600`\n')
            script_file_id.write( '    MM=`expr $DURATION % 3600 / 60`\n')
            script_file_id.write( '    SS=`expr $DURATION % 60`\n')
            script_file_id.write( '    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'init\n')
            script_file_id.write( 'run_phase_process\n')
            script_file_id.write( 'end\n')
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append(f'*** ERROR: The file {get_phase_process_script(process_number, output_dir)} can not be created.')
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_phase_process_starter(process_number, output_dir):
    '''
    Build the starter of the PHASE process script corresponding to the process number.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the ddRADseq simulation process starter
    try:
        if not os.path.exists(os.path.dirname(get_phase_process_starter(process_number, output_dir))):
            os.makedirs(os.path.dirname(get_phase_process_starter(process_number, output_dir)))
        with open(get_phase_process_starter(process_number, output_dir), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '#!/bin/bash\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            phase_process_script = get_phase_process_script(process_number, output_dir)
            log_file = get_log_file(process_number, output_dir)
            if sys.platform.startswith('win32'):
                phase_process_script = xlib.windows_path_2_wsl_path(phase_process_script)
                log_file = xlib.windows_path_2_wsl_path(log_file)
            file_id.write(f'{phase_process_script} &>{log_file} &\n')
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append(f'*** ERROR: The file {get_phase_process_starter(process_number, output_dir)} can not be created')
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_phase_process_script(process_number, output_dir):
    '''
    Get the PHASE process script path corresponding to the process number.
    '''

    # assign the PHASE script path
    phase_process_script = f'{output_dir}{os.sep}phase-process-{process_number}.sh'

    # return the PHASE script path
    return phase_process_script

#-------------------------------------------------------------------------------

def get_phase_process_starter(process_number, output_dir):
    '''
    Get the PHASE process starter path corresponding to the process number.
    '''

    # assign the PHASE process starter path
    phase_process_starter = f'{output_dir}{os.sep}phase-process-{process_number}-starter.sh'

    # return the PHASE starter path
    return phase_process_starter

#-------------------------------------------------------------------------------

def get_log_file(process_number, output_dir):
    '''
    Get the log file path corresponding to the process number.
    '''

    # assign the log file path
    log_file = f'{output_dir}{os.sep}phase-process-{process_number}-log.txt'

    # return the log file path
    return log_file

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
