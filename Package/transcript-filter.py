#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

'''
This source ... .
'''
#-------------------------------------------------------------------------------

import argparse
import os
import re
import subprocess
import sys

#-------------------------------------------------------------------------------

def main():
    '''
    Main line of the program.
    '''

    # verify the operating system
    verify_os()

    # get and verify the arguments
    parser = build_parser()
    args = parser.parse_args()
    verify_args(args)

    # initialize the transcripts dictionary
    transcripts_dict = {}

    # open the score file
    if args.score_file.endswith('.gz'):
        try:
            score_file_id = gzip.open(args.score_file_file, mode='rt', encoding='iso-8859-1')
        except:
            raise ProgramException('F002', args.score_file)
    else:
        try:
            score_file_id = open(args.score_file, mode='r', encoding='iso-8859-1')
        except:
            raise ProgramException('F001', args.score_file)

    # read the first record of score file and find out lenght, and FPKM and TMP positions
    score_record = score_file_id.readline()
    data_list = score_record.split('\t')
    transcript_id_position = -1
    length_position = -1
    FPKM_position = -1
    TPM_position = -1
    i = 0
    for datum in data_list:
        if datum.strip().upper().startswith('TRANSCRIPT_ID'):
            transcript_id_position = i
        if datum.strip().upper() == 'LENGTH':
            length_position = i
        elif datum.strip().upper() == 'FPKM':
            FPKM_position = i
        elif datum.strip().upper() == 'TPM':
            TPM_position = i
        i += 1
    if transcript_id_position == -1 or length_position == -1 or FPKM_position == -1 or TPM_position == -1:
        raise ProgramException('L001')

    # while there are records in score file, save theirs transcript id, lenght, FPKM and TPM
    score_record = score_file_id.readline()
    while score_record != '':
        data_list = score_record.split('\t')
        transcript_id = data_list[transcript_id_position].upper()
        try:
            length = float(data_list[length_position])
            (integer_part, decimal_part) = divmod(length, 1)
            if decimal_part > 0:
                raise ProgramException('D001', data_list[length_position], 'length')
            else:
                length = int(integer_part)
        except:
            raise ProgramException('D001', data_list[length_position], 'length')
        try:
            FPKM = float(data_list[FPKM_position])
        except:
            raise ProgramException('D002', data_list[FPKM_position], 'FPKM')
        try:
            TPM = float(data_list[TPM_position])
        except:
            raise ProgramException('D002', data_list[TPM_position], 'TPM')
        transcripts_dict[transcript_id] = {'length': length, 'FPKM': FPKM, 'TPM': TPM}
        score_record = score_file_id.readline()

    # close score file
    score_file_id.close()

    # open the transcriptome file
    if args.transcriptome_file.endswith('.gz'):
        try:
            tanscriptome_file_id = gzip.open(args.transcriptome_file, mode='rt', encoding='iso-8859-1')
        except:
            raise ProgramException('F002', args.transcriptome_file)
    else:
        try:
            tanscriptome_file_id = open(args.transcriptome_file, mode='r', encoding='iso-8859-1')
        except:
            raise ProgramException('F001', args.transcriptome_file)

    # open the ouput file
    if args.output_file.endswith('.gz'):
        try:
            output_file_id = gzip.open(args.output_file, mode='wt', encoding='iso-8859-1')
        except:
            raise ProgramException('F002', args.output_file)
    else:
        try:
            output_file_id = open(args.output_file, mode='w', encoding='iso-8859-1')
        except:
            raise ProgramException('F001', args.output_file)

    ## initialize the count of transcripts and saved transcripts
    transcripts_count = 0
    saved_transcripts_count = 0

    # set the pattern of the head records (>transcriptome_info)
    pattern = r'^>(.*)$'
 
    # read the first record of transcriptome file
    tanscriptome_record = tanscriptome_file_id.readline()

    # while there are records in transcriptome file
    while tanscriptome_record != '':

        # process the head record 
        if tanscriptome_record.startswith('>'):

            # extract the data 
            mo = re.search(pattern, tanscriptome_record)
            transcript_info = mo.group(1)

            # verify the origin
            if args.assembly_software_code == Const.AS_TRINITY_CODE and transcript_info[:7].upper() != 'TRINITY':
                raise ProgramException('F004', tanscriptome_record)

            # get the transcript id
            transcript_id = transcript_info.split(' ')[0].upper()

            # initialize the transcript sequence
            transcript_seq = ''

            # read the next record
            tanscriptome_record = tanscriptome_file_id.readline()

        else:

            # control the FASTA format
            raise ProgramException('F003', args.transcriptome_file, 'FASTA')

        # while there are records and they are sequence
        while tanscriptome_record != '' and not tanscriptome_record.startswith('>'):

            # concatenate the record to the transcript sequence
            transcript_seq += tanscriptome_record.strip()

            # read the next record of transcriptome file
            tanscriptome_record = tanscriptome_file_id.readline()

        # add 1 to trascriptomes count
        transcripts_count += 1

        # write the transcriptome_record in the output built if its length is between the minimum and maximum length, and FPKM and TPM are greater or equal to arguments values
        length = transcripts_dict.get(transcript_id, {}).get('length', 0)
        FPKM = transcripts_dict.get(transcript_id, {}).get('FPKM', 0)
        TPM = transcripts_dict.get(transcript_id, {}).get('TPM', 0)
        if length >= args.minlen and  length <= args.maxlen and FPKM >= args.FPKM and TPM >= args.TPM:
            try:
                output_file_id.write('>{0}\n'.format(transcript_info))
                output_file_id.write('{0}\n'.format(transcript_seq))
            except:
                raise ProgramException('F001', args.output_file)
            # add 1 to save trascripts count
            saved_transcripts_count += 1

        # print the counts
        if args.verbose == 'y':
            sys.stdout.write('\rTranscripts processed ... {0:9d} - Transcripts saved ... {1:9d}'.format(transcripts_count, saved_transcripts_count))

    # close transcriptome and output files
    tanscriptome_file_id.close()
    output_file_id.close()

    # print OK message 
    print('\nThe file {0} containing the transcripts selected has been created.'.format(os.path.basename(args.output_file)))

#-------------------------------------------------------------------------------

def verify_os():
    '''
    Verify the operating system.
    '''    

    # if the operating system is unsupported, exit with exception
    if not sys.platform.startswith('linux') and not sys.platform.startswith('darwin') and not sys.platform.startswith('win32') and not sys.platform.startswith('cygwin'):
        raise ProgramException('S001', sys.platform)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available options.
    '''

    #create the parser and add options
    parser = argparse.ArgumentParser(description='This program filters Trinity transcripts depending on the score gotten by DETONATE.')
    parser.add_argument('-a', '--assembler', dest='assembly_software_code', help='{0} (Trinity) or {1} (SOAPdenovo-Trans).'.format(Const.AS_TRINITY_CODE, Const.AS_SOAPDENOVOTRANS_CODE))
    parser.add_argument('-t', '--transcriptome', dest='transcriptome_file', help='Path of a transcriptome file in FASTA format generated by Trinity.')
    parser.add_argument('-s', '--score', dest='score_file', help='Path of a score file where DETONATE saved the score of the transcriptome file.')
    parser.add_argument('-o', '--output', dest='output_file', help='Path of a output file where filtered transcripts will be saved.')
    parser.add_argument('-m', '--minlen', dest='minlen', help='Transcript with length values less than this value will be filtered (default: {0}).'.format(Const.DEFAULT_MINLEN))
    parser.add_argument('-n', '--maxlen', dest='maxlen', help='Transcript with length values greater than this value will be filtered (default: {0}).'.format(Const.DEFAULT_MAXLEN))
    parser.add_argument('-f', '--FPKM', dest='FPKM', help='Transcript with FPKM values less than this value will be filtered (default: {0}).'.format(Const.DEFAULT_FPKM))
    parser.add_argument('-p', '--TPM', dest='TPM', help='Transcript with TPM values less than this value will be filtered (default: {0}).'.format(Const.DEFAULT_TPM))
    parser.add_argument('-v', '--verbose', dest='verbose', help='Additional job status info during the run (y: YES; n: NO, default: {0}).'.format(Const.DEFAULT_VERBOSE))

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def verify_args(args):
    '''
    Verity the input arguments data.
    '''

    # initialize the control variable
    OK = True

    # verify the assembly_software_code value
    if args.assembly_software_code is None:
        print('The assembly software that generated the transcritpme file has not been indicated in the input arguments.')
        OK = False
    else:
        if args.assembly_software_code not in [Const.AS_TRINITY_CODE, Const.AS_SOAPDENOVOTRANS_CODE, Const.AS_GENERATED_BY_NGSCLOUD]:
            print('{0} is not a valid code of assembly software.'.format(args.assembly_software_code))
            OK = False

    # verify the transcriptome_file value
    if args.transcriptome_file is None:
        print('A transcritpme file in Fasta format has not been indicated in the input arguments.')
        OK = False
    else:
        if not os.path.isfile(args.transcriptome_file):
            print('The file {0} does not exist.'.format(args.transcriptome_file))
            OK = False

    # verify the score_file value
    if args.score_file is None:
        print('A score file where RSEM-EVAL (DETONATE package) saved the score of the transcriptome file has not been indicated in the input arguments.')
        OK = False
    else:
        if not os.path.isfile(args.score_file):
            print('The file {0} does not exist.'.format(args.tscore_file))
            OK = False

    # verify the output_file value
    if args.output_file is None:
        print('A output file where filtered transcripts will be saved has not been indicated in the options.')
        OK = False
    else:
        try:
            if not os.path.exists(os.path.dirname(args.output_file)):
                os.makedirs(os.path.dirname(args.output_file))
        except:
            print('The directory {0} of the file {1} is not valid.'.format(os.path.dirname(args.output_file), args.output_file))
            OK = False

    # verify the minlen value
    if args.minlen is None:
        args.minlen = Const.DEFAULT_MINLEN
    else:
        try:
            args.minlen = int(args.minlen)
            if args.minlen < 1:
                print('The minlen value {0} is not a integer number greater than 0.'.format(args.minlen))
                OK = False
        except:
            print('The minlen value {0} is not a integer number greater than 0.'.format(args.minlen))
            OK = False

    # verify the maxlen value
    if args.maxlen is None:
        args.maxlen = Const.DEFAULT_MAXLEN
    else:
        try:
            args.maxlen = int(args.maxlen)
            if args.maxlen < 1:
                print('The maxlen value {0} is not a integer number greater than 0.'.format(args.maxlen))
                OK = False
        except:
            print('The maxlen value {0} is not a integer number greater than 0.'.format(args.maxlen))
            OK = False

    # verify if maxlen value is greater or equal than minlen value
    if args.maxlen < args.minlen:
        print('The value maxlen value ({0}) is less than minlen value ({1}).'.format(args.maxlen, args.minlen))
        OK = False

    # verify the FPKM value
    if args.FPKM is None:
        args.FPKM = Const.DEFAULT_FPKM
    else:
        try:
            args.FPKM = float(args.FPKM)
            if args.FPKM < 0.:
                print('The FPKM value {0} is not a float number greater or equal to 0.0.'.format(args.FPKM))
                OK = False
        except:
            print('The FPKM value {0} is not a float number greater or equal to 0.0.'.format(args.FPKM))
            OK = False

    # verify the TPM value
    if args.TPM is None:
        args.TPM = Const.DEFAULT_TPM
    else:
        try:
            args.TPM = float(args.TPM)
            if args.TPM < 0.:
                print('The TPM value {0} is not a float number greater or equal to 0.0.'.format(args.TPM))
                OK = False
        except:
            print('The TPM value {0} is not a float number greater or equal to 0.0.'.format(args.TPM))
            OK = False

    # verify the verbose value
    if args.verbose is None:
        args.verbose = Const.DEFAULT_VERBOSE
    else:
        if args.verbose.lower() not in ['y', 'n']:
            print('The value {0} of verbose is not y (YES) or n (NO).'.format(args.verbose))
            OK = False

    # if there are errors, exit with exception
    if not OK:
        raise ProgramException('P001', sys.platform)

#-------------------------------------------------------------------------------
 
class Const():
    '''
    Define class attributes with values will be used as constants.
    '''

    #---------------

    DEFAULT_MINLEN = 200
    DEFAULT_MAXLEN = 10000
    DEFAULT_FPKM = 1.0
    DEFAULT_TPM = 1.0
    DEFAULT_VERBOSE = 'n'

    #---------------

    AS_TRINITY_CODE = 'trinity'
    AS_SOAPDENOVOTRANS_CODE = 'sdnt'
    AS_GENERATED_BY_NGSCLOUD = 'ngscloud'

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
        if code_exception == 'D001':
            print('*** ERROR {0}: {1} is not an integer number and therefore it is a invalid value to {2}.'.format(code_exception, param1, param2), file=sys.stderr)
        elif code_exception == 'D002':
            print('*** ERROR {0}: {1} is not a float number and therefore it is a invalid value to {2}.'.format(code_exception, param1, param2), file=sys.stderr)
        elif code_exception == 'F001':
            print('*** ERROR {0}: This file {1} can not be opened.'.format(code_exception, param1), file=sys.stderr)
        elif code_exception == 'F002':
            print('*** ERROR {0}: This GZ compressed file {1} can not be opened.'.format(code_exception, param1), file=sys.stderr)
        elif code_exception == 'F003':
            print('*** ERROR {0}: Format file {1} is not {2}.'.format(code_exception, param1, param2), file=sys.stderr)
        elif code_exception == 'F004':
            print('*** ERROR {0}: Head record {1} is wrong.'.format(code_exception, param1), file=sys.stderr)
        elif code_exception == 'L001':
            print('*** ERROR {0}: Transcript id or lenght or FPKM data have not been found out in score file.'.format(code_exception), file=sys.stderr)
        elif code_exception == 'P001':
            print('*** ERROR {0}: This program has wrong parameters.'.format(code_exception), file=sys.stderr)
        elif code_exception == 'S001':
            print('*** ERROR {0}: The {1} OS is not supported.'.format(code_exception, param1), file=sys.stderr)
        else:
            print('*** ERROR {0}: This exception is not managed.'.format(code_exception), file=sys.stderr)

        # exit with return code 1
        sys.exit(1)

   #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
