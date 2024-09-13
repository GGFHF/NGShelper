#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint: disable=too-many-lines
#pylint: disable=line-too-long
#pylint: disable=invalid-name
#pylint: disable=multiple-statements
#pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This source contains general functions and classes used in NGShelper
software package used in both console mode and gui mode.

This software has been developed by:

    GI en especies leñosas (WooSp)
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

import collections
import gzip
import os
import re
import subprocess
import sys
import requests

#-------------------------------------------------------------------------------

def get_project_code():
    '''
    Get the project code.
    '''

    return 'ngshelper'

#-------------------------------------------------------------------------------

def get_project_name():
    '''
    Get the project name.
    '''

    return 'NGShelper'

#-------------------------------------------------------------------------------

def get_project_version():
    '''
    Get the project version.
    '''

    return '0.81'

#-------------------------------------------------------------------------------

def check_os():
    '''
    Check the operating system.
    '''

    # if the operating system is unsupported, exit with exception
    if not sys.platform.startswith('linux') and not sys.platform.startswith('darwin') and not sys.platform.startswith('win32') and not sys.platform.startswith('cygwin'):
        raise ProgramException('S001', sys.platform)

#-------------------------------------------------------------------------------

def check_startswith(literal, text_list, case_sensitive=False):
    '''
    Check if a literal starts with a text in a list.
    '''

    # initialize the control variable
    OK = False

    # initialize the working list
    w_list = []

    # if the codification is not case sensitive, convert the code and code list to uppercase
    if not case_sensitive:
        try:
            literal = literal.upper()
        except:
            pass
        try:
            w_list = [x.upper() for x in text_list]
        except:
            pass
    else:
        w_list = text_list

    # check if the literal starts with a text in the list
    for text in w_list:
        if literal.startswith(text):
            OK = True
            break

    # return control variable
    return OK

#-------------------------------------------------------------------------------

def check_code(literal, code_list, case_sensitive=False):
    '''
    Check if a literal is in a code list.
    '''

    # initialize the working list
    w_list = []

    # if the codification is not case sensitive, convert the code and code list to uppercase
    if not case_sensitive:
        try:
            literal = literal.upper()
        except:
            pass
        try:
            w_list = [x.upper() for x in code_list]
        except:
            pass
    else:
        w_list = code_list

    # check if the code is in the code list
    OK = literal in w_list

    # return control variable
    return OK

#-------------------------------------------------------------------------------

def check_int(literal, minimum=(-sys.maxsize - 1), maximum=sys.maxsize):
    '''
    Check if a numeric or string literal is an integer number.
    '''

    # initialize the control variable
    OK = True

    # check the number
    try:
        int(literal)
        int(minimum)
        int(maximum)
    except:
        OK = False
    else:
        if int(literal) < int(minimum) or int(literal) > int(maximum):
            OK = False

    # return control variable
    return OK

#-------------------------------------------------------------------------------

def check_float(literal, minimum=float(-sys.maxsize - 1), maximum=float(sys.maxsize), mne=0.0, mxe=0.0):
    '''
    Check if a numeric or string literal is a float number.
    '''

    # initialize the control variable
    OK = True

    # check the number
    try:
        float(literal)
        float(minimum)
        float(maximum)
        float(mne)
        float(mxe)
    except:
        OK = False
    else:
        if float(literal) < (float(minimum) + float(mne)) or float(literal) > (float(maximum) - float(mxe)):
            OK = False

    # return control variable
    return OK

#-------------------------------------------------------------------------------

def split_literal_to_integer_list(literal):
    '''
    Split a string literal in a integer value list which are separated by comma.
    '''

    # initialize the string values list and the interger values list
    strings_list = []
    integers_list = []

    # split the string literal in a string values list
    strings_list = split_literal_to_string_list(literal)

    # convert each value from string to integer
    for i in range(len(strings_list)):
        try:
            integers_list.append(int(strings_list[i]))
        except:
            integers_list = []
            break

    # return the integer values list
    return integers_list

#-------------------------------------------------------------------------------

def split_literal_to_float_list(literal):
    '''
    Split a string literal in a float value list which are separated by comma.
    '''

    # initialize the string values list and the float values list
    strings_list = []
    float_list = []

    # split the string literal in a string values list
    strings_list = split_literal_to_string_list(literal)

    # convert each value from string to float
    for i in range(len(strings_list)):
        try:
            float_list.append(float(strings_list[i]))
        except:
            float_list = []
            break

    # return the float values list
    return float_list

#-------------------------------------------------------------------------------

def split_literal_to_string_list(literal):
    '''
    Split a string literal in a string value list which are separated by comma.
    '''

    # initialize the string values list
    string_list = []

    # split the string literal in a string values list
    string_list = literal.split(',')

    # remove the leading and trailing whitespaces in each value
    for i in range(len(string_list)):
        string_list[i] = string_list[i].strip()

    # return the string values list
    return string_list

#-------------------------------------------------------------------------------

def join_string_list_to_string(string_list):
    '''
    Join a string value list in a literal (strings with simple quote and separated by comma).
    '''

    # initialize the literal
    literal = ''

    # concat the string items of string_list
    for string in string_list:
        literal = f"'{string}'" if literal == '' else f"{literal},'{string}'"

    # return the literal
    return literal

#-------------------------------------------------------------------------------

def get_nucleotide_dict():
    '''
    Get a dictionary with nucleotide data.
    '''

    # +----+------------------+------------------+-------------+
    # |Code|   Description    |   Translation    |Complementary|
    # +----+------------------+------------------+-------------+
    # | A  |Adenine           |A                 |     T/U     |
    # +----+------------------+------------------+-------------+
    # | C  |Cytosine          |C                 |      G      |
    # +----+------------------+------------------+-------------+
    # | G  |Guanine           |G                 |      C      |
    # +----+------------------+------------------+-------------+
    # | T  |Thymine           |T                 |      A      |
    # +----+------------------+------------------+-------------+
    # | U  |Uracil            |U                 |      A      |
    # +----+------------------+------------------+-------------+
    # | R  |puRine            |A or G            |      Y      |
    # +----+------------------+------------------+-------------+
    # | Y  |pYrimidine        |C or T/U          |      R      |
    # +----+------------------+------------------+-------------+
    # | S  |Strong interaction|C or G            |      S      |
    # +----+------------------+------------------+-------------+
    # | W  |Weak interaction  |A or T/U          |      W      |
    # +----+------------------+------------------+-------------+
    # | K  |Keto group        |G or T/U          |      M      |
    # +----+------------------+------------------+-------------+
    # | M  |aMino group       |A or C            |      K      |
    # +----+------------------+------------------+-------------+
    # | B  |not A             |C or G or T/U     |      V      |
    # +----+------------------+------------------+-------------+
    # | V  |not T             |A or C or G       |      B      |
    # +----+------------------+------------------+-------------+
    # | D  |not C             |A or G or T/U     |      H      |
    # +----+------------------+------------------+-------------+
    # | H  |not G             |A or C or T/U     |      D      |
    # +----+------------------+------------------+-------------+
    # | N  |aNy               |A or C or G or T/U|      N      |
    # +----+------------------+------------------+-------------+

    # build the nucleotide dictonary
    nucleotide_dict = {
        'A':{'code': 'A', 'nuclotide_list':['A'], 'complementary_code':'T', 'complementary_nuclotide_list':['T']},
        'a':{'code': 'a', 'nuclotide_list':['a'], 'complementary_code':'t', 'complementary_nuclotide_list':['t']},
        'C':{'code': 'C', 'nuclotide_list':['C'], 'complementary_code':'G', 'complementary_nuclotide_list':['G']},
        'c':{'code': 'c', 'nuclotide_list':['c'], 'complementary_code':'g', 'complementary_nuclotide_list':['g']},
        'G':{'code': 'G', 'nuclotide_list':['G'], 'complementary_code':'C', 'complementary_nuclotide_list':['C']},
        'g':{'code': 'g', 'nuclotide_list':['g'], 'complementary_code':'c', 'complementary_nuclotide_list':['c']},
        'T':{'code': 'T', 'nuclotide_list':['T'], 'complementary_code':'A', 'complementary_nuclotide_list':['A']},
        't':{'code': 't', 'nuclotide_list':['t'], 'complementary_code':'a', 'complementary_nuclotide_list':['a']},
        'R':{'code': 'R', 'nuclotide_list':['A','G'], 'complementary_code':'Y', 'complementary_nuclotide_list':['C','T']},
        'r':{'code': 'r', 'nuclotide_list':['a','g'], 'complementary_code':'y', 'complementary_nuclotide_list':['c','t']},
        'Y':{'code': 'Y', 'nuclotide_list':['C','T'], 'complementary_code':'R', 'complementary_nuclotide_list':['A','G']},
        'y':{'code': 'y', 'nuclotide_list':['c','t'], 'complementary_code':'r', 'complementary_nuclotide_list':['a','g']},
        'S':{'code': 'S', 'nuclotide_list':['C','G'], 'complementary_code':'S', 'complementary_nuclotide_list':['C','G']},
        's':{'code': 's', 'nuclotide_list':['c','G'], 'complementary_code':'s', 'complementary_nuclotide_list':['c','g']},
        'W':{'code': 'W', 'nuclotide_list':['A','T'], 'complementary_code':'W', 'complementary_nuclotide_list':['A','T']},
        'w':{'code': 'w', 'nuclotide_list':['a','t'], 'complementary_code':'w', 'complementary_nuclotide_list':['a','t']},
        'K':{'code': 'K', 'nuclotide_list':['G','T'], 'complementary_code':'M', 'complementary_nuclotide_list':['A','C']},
        'k':{'code': 'k', 'nuclotide_list':['g','t'], 'complementary_code':'m', 'complementary_nuclotide_list':['a','c']},
        'M':{'code': 'M', 'nuclotide_list':['A','C'], 'complementary_code':'K', 'complementary_nuclotide_list':['G','T']},
        'm':{'code': 'm', 'nuclotide_list':['a','c'], 'complementary_code':'k', 'complementary_nuclotide_list':['g','t']},
        'B':{'code': 'B', 'nuclotide_list':['C','G','T'], 'complementary_code':'V', 'complementary_nuclotide_list':['A','C','G']},
        'b':{'code': 'b', 'nuclotide_list':['c','G','T'], 'complementary_code':'v', 'complementary_nuclotide_list':['a','c','g']},
        'V':{'code': 'V', 'nuclotide_list':['A','C','G'], 'complementary_code':'B', 'complementary_nuclotide_list':['C','G','T']},
        'v':{'code': 'v', 'nuclotide_list':['a','c','g'], 'complementary_code':'b', 'complementary_nuclotide_list':['c','g','t']},
        'D':{'code': 'D', 'nuclotide_list':['A','G','T'], 'complementary_code':'H', 'complementary_nuclotide_list':['A','C','T']},
        'd':{'code': 'd', 'nuclotide_list':['a','g','t'], 'complementary_code':'h', 'complementary_nuclotide_list':['a','c','t']},
        'H':{'code': 'H', 'nuclotide_list':['A','C','T'], 'complementary_code':'D', 'complementary_nuclotide_list':['A','G','T']},
        'h':{'code': 'h', 'nuclotide_list':['a','C','t'], 'complementary_code':'d', 'complementary_nuclotide_list':['a','g','t']},
        'N':{'code': 'N', 'nuclotide_list':['A','C','G','T'], 'complementary_code':'N', 'complementary_nuclotide_list':['A','C','G','T']},
        'n':{'code': 'n', 'nuclotide_list':['a','c','g','t'], 'complementary_code':'n', 'complementary_nuclotide_list':['a','c','g','t']}
        }

    # return the nucleotide dictionary
    return nucleotide_dict

#-------------------------------------------------------------------------------

def get_nucleotide_list_symbol(nucleotide_list):
    '''
    Get the nucleotide code or ambiguous nucleotide symbol corresponding to a nucleotide list.
    '''

    # initialize the symbol
    symbol = ''

    # get a dictionary with nucleotide data
    nucleotide_dict = get_nucleotide_dict()

    # set element list in uppercase
    for i in range(len(nucleotide_list)):
        nucleotide_list[i] = nucleotide_list[i].upper()

    # find the nucleotide code
    for code in nucleotide_dict.keys():
        if set(nucleotide_dict[code]['nuclotide_list']) == set(nucleotide_list):
            symbol = code
            break

    # return the symbol
    return symbol

#-------------------------------------------------------------------------------

def windows_path_2_wsl_path(path):
    '''
    Change a Windows format path to a WSL format path.
    '''

    # change the format path
    new_path = path.replace('\\', '/')
    new_path = f'/mnt/{new_path[0:1].lower()}{new_path[2:]}'

    # return the path
    return new_path

#-------------------------------------------------------------------------------

def wsl_path_2_windows_path(path):
    '''
    Change a WSL format path to a Windows format path.
    '''

    # change the format path
    new_path = f'{path[5:6].upper()}:{path[6:]}'
    new_path = new_path.replace('/', '\\')

    # return the path
    return new_path

#-------------------------------------------------------------------------------

def run_command(command, log, is_script):
    '''
    Run a Bash shell command and redirect stdout and stderr to log.
    '''

    # prepare the command to be execuete in WSL
    if sys.platform.startswith('win32'):
        if is_script:
            command = command.replace('&','')
            command = f'wsl bash -c "nohup {command} &>/dev/null"'
        else:
            command = command.replace(':$PATH','')
            command = f'wsl bash -c "{command}"'

    # run the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in iter(process.stdout.readline, b''):
        # replace non-ASCII caracters by one blank space
        line = re.sub(b'[^\x00-\x7F]+', b' ', line)
        # create a string from the bytes literal
        line = line.decode('utf-8')
        # write the line in log
        log.write(line)
    rc = process.wait()

    # return the return code of the command run
    return rc

#-------------------------------------------------------------------------------

def get_wsl_envvar(envvar):
    '''
    Get the value of a varible environment from WSL.
    '''

    # initialice the environment variable value
    envvar_value = get_na()

    # build the command
    command = f'wsl bash -c "echo ${envvar}"'

    # run the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in iter(process.stdout.readline, b''):
        envvar_value = line.decode('utf-8').replace('\n','')
        break
    rc = process.wait()

    # return the environment variable value
    return envvar_value

#-------------------------------------------------------------------------------

def read_vcf_file(vcf_file_id, sample_number, check_sample_number=True):
    '''
    Read a VCF file record.
    '''

    # initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read record
    record = vcf_file_id.readline()

    # if there is a metadata records
    if record != '' and record.startswith('##'):

        pass

    # if there is a column description record
    if record != '' and record.startswith('#CHROM'):

        # split the record data
        record_data_list = []
        start = 0
        for end in [i for i, chr in enumerate(record) if chr == '\t']:
            record_data_list.append(record[start:end].strip())
            start = end + 1
        record_data_list.append(record[start:].strip('\n').strip())

        # get the record data dictionary
        data_dict = {'record_data_list': record_data_list}

    # if there is a variant record
    if record != '' and not record.startswith('##') and not record.startswith('#CHROM'):

        # split the record data
        record_data_list = []
        start = 0
        for end in [i for i, chr in enumerate(record) if chr == '\t']:
            record_data_list.append(record[start:end].strip())
            start = end + 1
        record_data_list.append(record[start:].strip('\n').strip())

        # check if the number of sample data
        if check_sample_number and len(record_data_list) - 9 != sample_number:
            print('sample_number: {}'.format(sample_number))
            print('len(record_data_list) - 9: {}'.format(len(record_data_list) - 9))
            raise ProgramException('L006', record_data_list[0], record_data_list[1])

        # extract data from the record
        chrom = record_data_list[0]
        pos = record_data_list[1]
        id = record_data_list[2]
        ref = record_data_list[3]
        alt = record_data_list[4]
        qual = record_data_list[5]
        filter = record_data_list[6]
        info = record_data_list[7]
        format = record_data_list[8]
        sample_list = []
        for i in range(len(record_data_list) - 9):
            sample_list.append(record_data_list[i + 9])

        # set the key
        key = f'{chrom}-{int(pos):09d}'

        # get the record data dictionary
        data_dict = {'chrom': chrom, 'pos': pos, 'id': id, 'ref': ref, 'alt': alt, 'qual': qual, 'filter': filter, 'info': info, 'format': format, 'sample_list': sample_list}

    # if there is not any record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

def get_sample_data(sample_file, sp1_id, sp2_id, hybrid_id):
    '''
    Get data of the samples included in a VCF file from a file with record format: format: sample_id;species_id
    '''

    # initialize the sample dictonary
    sample_dict = {}

    # initialize the species name list
    species_id_list = []

    # set the record pattern
    # format: sample_id;species_id;mother_id
    record_pattern = re.compile('^(.*);(.*);(.*)$')

    # open the sample file
    if sample_file.endswith('.gz'):
        try:
            sample_file_id = gzip.open(sample_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise ProgramException(e, 'F002', sample_file)
    else:
        try:
            sample_file_id = open(sample_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise ProgramException(e, 'F001', sample_file)

    # initialize counters
    record_counter = 0
    sample_counter = 0

    # read the first record
    record = sample_file_id.readline()

    # while there are records
    while record != '':

        # add 1 to the record counter
        record_counter += 1

        # if the record is not a comment
        if not record.startswith('#'):

            # add 1 to the sample counter
            sample_counter += 1

            # extract the data
            try:
                mo = record_pattern.match(record)
                sample_id = mo.group(1).strip()
                species_id = mo.group(2).strip()
                mother_id = mo.group(3).strip()
            except Exception as e:
                raise ProgramException(e, 'D001', record.strip('\n'), sample_file)

            # check "mother_id"
            if mother_id.upper() == 'NONE':
                mother_id = mother_id.upper()

            # add sample data to the dictionary
            sample_dict[sample_id] = {'sample_id':sample_id, 'species_id':species_id , 'mother_id':mother_id, 'colnum': sample_counter}

            # add species_id to species list
            if species_id not in species_id_list:
                species_id_list.append(species_id)

        Message.print('verbose', f'\rProcessed records ... {record_counter:4d} - Samples ... {sample_counter:4d}')

        # read the next record
        record = sample_file_id.readline()

    Message.print('verbose', '\n')

    # close file
    sample_file_id.close()

    # check the species identification
    if sp2_id.upper() == 'NONE' and hybrid_id.upper() == 'NONE':
        pass
    elif sp1_id not in species_id_list or \
       sp2_id not in species_id_list or \
       hybrid_id.upper() == 'NONE' and len(species_id_list) != 2 or \
       hybrid_id.upper() != 'NONE' and (hybrid_id not in species_id_list or len(species_id_list) != 3):
        raise ProgramException('','L001')

    # check the mother identification exists when it is not equal to NONE
    for _, value in sample_dict.items():
        if value['mother_id'].upper() != 'NONE':
            if sample_dict.get(value['mother_id'], {}) == {}:
                raise ProgramException('', 'L002', value['mother_id'])

    # return the sample dictonary and species name list
    return sample_dict

#-------------------------------------------------------------------------------

def get_id_data(id_file):
    '''
    Build a list and dictionary of identifications from a file.
    '''

    # initialize the list and dictonary of identifications
    id_list = []
    id_dict = {}

    # initialize the identification counter
    id_counter = 0

    # open the identification file
    if id_file.endswith('.gz'):
        try:
            id_file_id = gzip.open(id_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise ProgramException(e, 'F002', id_file)
    else:
        try:
            id_file_id = open(id_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise ProgramException(e, 'F001', id_file)

    # read the first record
    record = id_file_id.readline()

    # while there are records
    while record != '':

        # add identification to the list and dictionary
        id_list.append(record.strip())
        id_dict[record.strip()] = 0

        # add 1 to the identification counter
        id_counter += 1
        Message.print('verbose', f'\rIdentifications ... {id_counter}')

        # read the next record
        record = id_file_id.readline()

    Message.print('verbose', '\n')

    # close file
    id_file_id.close()

    # sort the identification list
    if id_list != []:
        id_list.sort()

    # return the list and dictonary of identifications
    return id_list, id_dict

#-------------------------------------------------------------------------------

def get_toa_file_type_code_list():
    '''
    Get the code list of "toa_file_type".
    '''

    return ['PLAZA', 'REFSEQ', 'NT', 'NR', 'MERGER']

#-------------------------------------------------------------------------------

def get_toa_file_type_code_list_text():
    '''
    Get the code list of "toa_file_type" as text.
    '''

    return str(get_toa_file_type_code_list()).strip('[]').replace('\'', '').replace(',', ' or')

#-------------------------------------------------------------------------------

def get_taxonomy_server():
    '''
    Get the taxonomy server URL.
    '''
    return 'https://taxonomy.jgi-psf.org/'

#-------------------------------------------------------------------------------

def get_taxonomy_dict(type, value):
    '''
    Get a taxonomy dictionary with the a species data downloaded from the taxonomy server.
    '''

    # initialize the taxonomy dictionary
    taxonomy_dict = {}

    # set the taxonomy server
    taxonomy_server = get_taxonomy_server()

    # replace spaces by underscores in value
    value = value.strip().replace(' ', '_')

    # inquire the taxonomy data to the server
    try:
        r = requests.get(f'{taxonomy_server}/{type}/{value}')
    except requests.exceptions.ConnectionError:
        raise ProgramException('', 'W002', taxonomy_server)
    except Exception as e:
        raise ProgramException(e, 'W001', taxonomy_server)

    # build the taxonomy dictionary
    if r.status_code == requests.codes.ok: #pylint: disable=no-member
        try:
            if r.json()[value].get('error','OK') == 'OK' :
                taxonomy_dict = r.json()[value]
        except Exception as e:
            pass
    else:
        raise ProgramException('', 'W003', taxonomy_server, r.status_code)

    # return taxonomy dictionary
    return taxonomy_dict

#-------------------------------------------------------------------------------

def read_toa_annotation_record(file_name, file_id, type, record_counter):
    '''
    Read the next record of the functional annotation file built by TOA application.
    '''

# initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read next record
    record = file_id.readline()

    # if there is record
    if record != '':

        # remove EOL
        record = record.strip('\n')

        # if type is PLAZA
        if type.upper() == 'PLAZA':

            # extract data
            # PLAZA record format: "seq_id";"nt_seq_id";"aa_seq_id";"hit_num";"hsp_num";"iteration_iter_num";"hit_accession";"hsp_evalue";"hsp_identity";"hsp_positive";"hsp_gaps";"hsp_align_len";"hsp_qseq";"species";"family";"phylum";"kingdom";"superkingdom";"desc";"databases";"go_id";"go_desc";"interpro_id";"interpro_desc";"mapman_id";"mapman_desc";"ec_id";"kegg_id";"metacyc_id"
            data_list = []
            start = 0
            for end in [i for i, chr in enumerate(record) if chr == ';']:
                data_list.append(record[start:end].strip('"'))
                start = end + 1
            data_list.append(record[start:].strip('\n').strip('"'))
            try:
                seq_id = data_list[0]
                nt_seq_id = data_list[1]
                aa_seq_id = data_list[2]
                hit_num = data_list[3]
                hsp_num = data_list[4]
                iteration_iter_num = data_list[5]
                hit_accession = data_list[6]
                hsp_evalue = data_list[7]
                hsp_identity = data_list[8]
                hsp_positive = data_list[9]
                hsp_gaps = data_list[10]
                hsp_align_len = data_list[11]
                hsp_qseq = data_list[12]
                species = data_list[13]
                family = data_list[14]
                phylum = data_list[15]
                kingdom = data_list[16]
                superkingdom = data_list[17]
                desc = data_list[18]
                databases = data_list[19]
                go_id = data_list[20]
                go_desc = data_list[21]
                interpro_id = data_list[22]
                interpro_desc = data_list[23]
                mapman_id = data_list[24]
                mapman_desc = data_list[25]
                ec_id = data_list[26]
                kegg_id = data_list[27]
                metacyc_id = data_list[28]
            except Exception as e:
                raise ProgramException(e, 'F006', os.path.basename(file_name), record_counter) from e

            # set the key
            key = f'{nt_seq_id}-{aa_seq_id}-{hit_num}-{hsp_num}'

            # get the record data dictionary
            data_dict = {'seq_id': seq_id, 'nt_seq_id': nt_seq_id, 'aa_seq_id': aa_seq_id, 'hit_num': hit_num, 'hsp_num': hsp_num, 'iteration_iter_num': iteration_iter_num, 'hit_accession': hit_accession, 'hsp_evalue': hsp_evalue, 'hsp_identity': hsp_identity, 'hsp_positive': hsp_positive, 'hsp_gaps': hsp_gaps, 'hsp_align_len': hsp_align_len, 'hsp_qseq': hsp_qseq, 'species': species, 'family': family, 'phylum': phylum, 'kingdom': kingdom, 'superkingdom': superkingdom, 'desc': desc, 'databases': databases, 'go_id': go_id, 'go_desc': go_desc, 'interpro_id': interpro_id, 'interpro_desc': interpro_desc, 'mapman_id': mapman_id, 'mapman_desc': mapman_desc, 'ec_id': ec_id, 'kegg_id': kegg_id, 'metacyc_id': metacyc_id}

        # if type is REFSEQ
        elif type.upper() == 'REFSEQ':

            # extract data
            # REFSEQ record format: "seq_id";"nt_seq_id";"aa_seq_id";"hit_num";"hsp_num";"iteration_iter_num";"hit_id";"hsp_evalue";"hsp_identity";"hsp_positive";"hsp_gaps";"hsp_align_len";"hsp_qseq";"species";"family";"phylum";"kingdom";"superkingdom";"desc";"databases";"gene_id";"status";"rna_nucleotide_accession";"protein_accession";"genomic_nucleotide_accession";"gene_symbol";"go_id";"evidence";"go_term";"category";"interpro_id";"interpro_desc";"ec_id";"kegg_id";"metacyc_id"
            data_list = []
            start = 0
            for end in [i for i, chr in enumerate(record) if chr == ';']:
                data_list.append(record[start:end].strip('"'))
                start = end + 1
            data_list.append(record[start:].strip('"').strip('\n'))
            try:
                seq_id = data_list[0]
                nt_seq_id = data_list[1]
                aa_seq_id = data_list[2]
                hit_num = data_list[3]
                hsp_num = data_list[4]
                iteration_iter_num = data_list[5]
                hit_id = data_list[6]
                hsp_evalue = data_list[7]
                hsp_identity = data_list[8]
                hsp_positive = data_list[9]
                hsp_gaps = data_list[10]
                hsp_align_len = data_list[11]
                hsp_qseq = data_list[12]
                species = data_list[13]
                family = data_list[14]
                phylum = data_list[15]
                kingdom = data_list[16]
                superkingdom = data_list[17]
                desc = data_list[18]
                databases = data_list[19]
                gene_id = data_list[20]
                status = data_list[21]
                rna_nucleotide_accession = data_list[22]
                protein_accession = data_list[23]
                genomic_nucleotide_accession = data_list[24]
                gene_symbol = data_list[25]
                go_id = data_list[26]
                evidence = data_list[27]
                go_term = data_list[28]
                category = data_list[29]
                interpro_id = data_list[30]
                interpro_desc = data_list[31]
                ec_id = data_list[32]
                kegg_id = data_list[33]
                metacyc_id = data_list[34]
            except Exception as e:
                raise ProgramException('F006', os.path.basename(file_name), record_counter) from e

            # set the key
            key = f'{nt_seq_id}-{aa_seq_id}-{hit_num}-{hsp_num}'

            # get the record data dictionary
            data_dict = {'seq_id': seq_id, 'nt_seq_id': nt_seq_id, 'aa_seq_id': aa_seq_id, 'hit_num': hit_num, 'hsp_num': hsp_num, 'iteration_iter_num': iteration_iter_num, 'hit_id': hit_id,  'hsp_evalue': hsp_evalue,  'hsp_identity': hsp_identity, 'hsp_positive': hsp_positive, 'hsp_gaps': hsp_gaps, 'hsp_align_len': hsp_align_len, 'hsp_qseq': hsp_qseq, 'species': species, 'family': family, 'phylum': phylum, 'kingdom': kingdom, 'superkingdom': superkingdom, 'desc': desc, 'databases': databases, 'gene_id': gene_id, 'status': status, 'rna_nucleotide_accession': rna_nucleotide_accession, 'protein_accession': protein_accession, 'genomic_nucleotide_accession': genomic_nucleotide_accession, 'gene_symbol': gene_symbol, 'go_id': go_id, 'evidence': evidence, 'go_term': go_term, 'category':category, 'interpro_id': interpro_id, 'interpro_desc': interpro_desc, 'ec_id': ec_id, 'kegg_id': kegg_id, 'metacyc_id': metacyc_id}

        # if type is NT o NR
        if type.upper() in ['NT', 'NR']:

            # extract data
            # PLAZA record format: "seq_id";"nt_seq_id";"aa_seq_id";"hit_num";"hsp_num";"iteration_iter_num";"hit_id";"hsp_evalue";"hsp_identity";"hsp_positive";"hsp_gaps";"hsp_align_len";"hsp_qseq";"species";"family";"phylum";"kingdom";"superkingdom";"desc";"databases"
            data_list = []
            start = 0
            for end in [i for i, chr in enumerate(record) if chr == ';']:
                data_list.append(record[start:end].strip('"'))
                start = end + 1
            data_list.append(record[start:].strip('"'))
            try:
                seq_id = data_list[0]
                nt_seq_id = data_list[1]
                aa_seq_id = data_list[2]
                hit_num = data_list[3]
                hsp_num = data_list[4]
                iteration_iter_num = data_list[5]
                hit_id = data_list[6]
                hsp_evalue = data_list[7]
                hsp_identity = data_list[8]
                hsp_positive = data_list[9]
                hsp_gaps = data_list[10]
                hsp_align_len = data_list[11]
                hsp_qseq = data_list[12]
                species = data_list[13]
                family = data_list[14]
                phylum = data_list[15]
                kingdom = data_list[16]
                superkingdom = data_list[17]
                desc = data_list[18]
                databases = data_list[19]
            except Exception as e:
                raise ProgramException('F006', os.path.basename(file_name), record_counter) from e

            # set the key
            key = f'{nt_seq_id}-{aa_seq_id}-{hit_num}-{hsp_num}'

            # get the record data dictionary
            data_dict = {'seq_id': seq_id, 'nt_seq_id': nt_seq_id, 'aa_seq_id': aa_seq_id, 'hit_num': hit_num, 'hsp_num': hsp_num, 'iteration_iter_num': iteration_iter_num, 'hit_id': hit_id, 'hsp_evalue': hsp_evalue, 'hsp_identity': hsp_identity, 'hsp_positive': hsp_positive, 'hsp_gaps': hsp_gaps, 'hsp_align_len': hsp_align_len, 'hsp_qseq': hsp_qseq, 'species': species, 'family': family, 'phylum': phylum, 'kingdom': kingdom, 'superkingdom': superkingdom, 'desc': desc, 'databases': databases}

        # if type is MERGER
        # MERGER record format: "seq_id";"nt_seq_id";"aa_seq_id";"hit_num";"hsp_num";"hit_id";"hsp_evalue";"hsp_identity";"hsp_positive";"hsp_gaps";"hsp_align_len";"hsp_qseq";"species";"family";"phylum";"kingdom";"superkingdom";"desc";"databases";"go_id";"go_desc";"interpro_id";"interpro_desc";"mapman_id";"mapman_desc";"refseq_gene_id";"refseq_desc";"refseq_status";"refseq_protein_accession";"refseq_genomic_nucleotide_accession";"refseq_gene_symbol"
        elif type.upper() == 'MERGER':

            # extract data
            data_list = []
            start = 0
            for end in [i for i, chr in enumerate(record) if chr == ';']:
                data_list.append(record[start:end].strip('"'))
                start = end + 1
            data_list.append(record[start:].strip('"').strip('\n'))
            try:
                seq_id = data_list[0]
                nt_seq_id = data_list[1]
                aa_seq_id = data_list[2]
                hit_num = data_list[3]
                hsp_num = data_list[4]
                hit_id = data_list[5]
                hsp_evalue = data_list[6]
                hsp_identity = data_list[7]
                hsp_positive = data_list[8]
                hsp_gaps = data_list[9]
                hsp_align_len = data_list[10]
                hsp_qseq = data_list[11]
                species = data_list[12]
                family = data_list[13]
                phylum = data_list[14]
                kingdom = data_list[15]
                superkingdom = data_list[16]
                desc = data_list[17]
                databases = data_list[18]
                go_id = data_list[19]
                go_desc = data_list[20]
                interpro_id = data_list[21]
                interpro_desc = data_list[22]
                mapman_id = data_list[23]
                mapman_desc = data_list[24]
                ec_id = data_list[25]
                kegg_id = data_list[26]
                metacyc_id = data_list[27]
                refseq_gene_id = data_list[28]
                refseq_desc = data_list[29]
                refseq_status = data_list[30]
                refseq_rna_nucleotide_accession = data_list[31]
                refseq_protein_accession = data_list[32]
                refseq_genomic_nucleotide_accession = data_list[33]
                refseq_gene_symbol = data_list[34]
            except Exception as e:
                raise ProgramException('F006', os.path.basename(file_name), record_counter) from e

            # set the key
            key = f'{nt_seq_id}-{aa_seq_id}-{hit_num}-{hsp_num}'

            # get the record data dictionary
            data_dict = {'seq_id': seq_id, 'nt_seq_id': nt_seq_id, 'aa_seq_id': aa_seq_id, 'hit_num': hit_num, 'hsp_num': hsp_num, 'hit_id': hit_id, 'hsp_evalue': hsp_evalue,  'hsp_identity': hsp_identity, 'hsp_positive': hsp_positive, 'hsp_gaps': hsp_gaps, 'hsp_align_len': hsp_align_len, 'hsp_qseq': hsp_qseq, 'species': species, 'family': family, 'phylum': phylum, 'kingdom': kingdom, 'superkingdom': superkingdom, 'desc': desc, 'databases': databases, 'go_id': go_id, 'go_desc': go_desc, 'interpro_id': interpro_id, 'interpro_desc': interpro_desc, 'mapman_id': mapman_id, 'mapman_desc': mapman_desc, 'ec_id': ec_id, 'kegg_id': kegg_id, 'metacyc_id': metacyc_id, 'refseq_gene_id': refseq_gene_id, 'refseq_desc': refseq_desc, 'refseq_status': refseq_status, 'refseq_rna_nucleotide_accession': refseq_rna_nucleotide_accession, 'refseq_protein_accession': refseq_protein_accession, 'refseq_genomic_nucleotide_accession': refseq_genomic_nucleotide_accession, 'refseq_gene_symbol': refseq_gene_symbol}

    # if there is not record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

def read_gymnotoa_annotation_record(file_name, file_id, record_counter):
    '''
    Read the next record of the functional annotation file built by gymnoTOA application.
    '''

    # initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read next record
    record = file_id.readline()

    # if there is record
    if record != '':

        # extract data
        # record format: qseqid <field_sep> sseqid <field_sep> pident <field_sep> length <field_sep> mismatch <field_sep> gapopen <field_sep> qstart <field_sep> qend <field_sep> sstart <field_sep> send <field_sep> evalue <field_sep> bitscore <record_sep>
        field_sep = ';'
        record_sep = '\n'
        data_list = re.split(field_sep, record.replace(record_sep,''))
        try:
            qseqid = data_list[0].strip()
            sseqid = data_list[1].strip()
            pident = data_list[2].strip()
            length = data_list[3].strip()
            mismatch = data_list[4].strip()
            gapopen = data_list[5].strip()
            qstart = data_list[6].strip()
            qend = data_list[7].strip()
            sstart = data_list[8].strip()
            send = data_list[9].strip()
            evalue = data_list[10].strip()
            bitscore = data_list[11].strip()
            aligner = data_list[12].strip()
            ncbi_description = data_list[13].strip()
            ncbi_species = data_list[14].strip()
            tair10_ortholog_seq_id = data_list[15].strip()
            interpro_goterms = data_list[16].strip()
            panther_goterms = data_list[17].strip()
            metacyc_pathways = data_list[18].strip()
            # -- reactome_pathways = data_list[x].strip()
            eggnog_ortholog_seq_id = data_list[19].strip()
            eggnog_ortholog_species = data_list[20].strip()
            eggnog_ogs = data_list[21].strip()
            cog_category = data_list[22].strip()
            eggnog_description = data_list[23].strip()
            eggnog_goterms = data_list[24].strip()
            ec = data_list[25].strip()
            kegg_kos = data_list[26].strip()
            kegg_pathways = data_list[27].strip()
            kegg_modules = data_list[28].strip()
            kegg_reactions = data_list[29].strip()
            kegg_rclasses = data_list[30].strip()
            brite = data_list[31].strip()
            kegg_tc = data_list[32].strip()
            cazy = data_list[33].strip()
            pfams = data_list[34].strip()
        except Exception as e:
            raise ProgramException(e, 'F006', os.path.basename(file_name), record_counter) from e

        # set the key
        key = f'{qseqid}-{sseqid}'

        # get the record data dictionary
        # -- data_dict = {'qseqid': qseqid, 'sseqid': sseqid, 'pident': pident, 'length': length, 'mismatch': mismatch, 'gapopen': gapopen, 'qstart': qstart, 'qend': qend, 'sstart': sstart, 'send': send, 'evalue': evalue, 'bitscore': bitscore, 'aligner': aligner, 'ncbi_description': ncbi_description, 'ncbi_species': ncbi_species, 'tair10_ortholog_seq_id': tair10_ortholog_seq_id, 'interpro_goterms': interpro_goterms, 'panther_goterms': panther_goterms, 'metacyc_pathways': metacyc_pathways, 'reactome_pathways': reactome_pathways, 'eggnog_ortholog_seq_id': eggnog_ortholog_seq_id, 'eggnog_ortholog_species': eggnog_ortholog_species, 'eggnog_ogs': eggnog_ogs, 'cog_category': cog_category, 'eggnog_description': eggnog_description, 'eggnog_goterms': eggnog_goterms, 'ec': ec, 'kegg_kos': kegg_kos, 'kegg_pathways': kegg_pathways, 'kegg_modules': kegg_modules, 'kegg_reactions': kegg_reactions, 'kegg_rclasses': kegg_rclasses, 'brite': brite, 'kegg_tc': kegg_tc, 'cazy': cazy, 'pfams': pfams}
        data_dict = {'qseqid': qseqid, 'sseqid': sseqid, 'pident': pident, 'length': length, 'mismatch': mismatch, 'gapopen': gapopen, 'qstart': qstart, 'qend': qend, 'sstart': sstart, 'send': send, 'evalue': evalue, 'bitscore': bitscore, 'aligner': aligner, 'ncbi_description': ncbi_description, 'ncbi_species': ncbi_species, 'tair10_ortholog_seq_id': tair10_ortholog_seq_id, 'interpro_goterms': interpro_goterms, 'panther_goterms': panther_goterms, 'metacyc_pathways': metacyc_pathways, 'eggnog_ortholog_seq_id': eggnog_ortholog_seq_id, 'eggnog_ortholog_species': eggnog_ortholog_species, 'eggnog_ogs': eggnog_ogs, 'cog_category': cog_category, 'eggnog_description': eggnog_description, 'eggnog_goterms': eggnog_goterms, 'ec': ec, 'kegg_kos': kegg_kos, 'kegg_pathways': kegg_pathways, 'kegg_modules': kegg_modules, 'kegg_reactions': kegg_reactions, 'kegg_rclasses': kegg_rclasses, 'brite': brite, 'kegg_tc': kegg_tc, 'cazy': cazy, 'pfams': pfams}

    # if there is not record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

def read_blast2go_annotation_record(file_name, file_id, record_counter):
    '''
    Read the next record of the functional annotation file built by Blast2GO application.
    '''

    # initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read next record
    record = file_id.readline()

    # if there is record
    if record != '':

        # remove EOL
        record = record.strip('\n')

        # extract data
        # Blast2GO record format: unknown	Tags	SeqName	Description	Length	#Hits	e-Value	sim mean	#GO	GO IDs	GO Names	Enzyme Codes	Enzyme Names	InterPro IDs	InterPro GO IDs	InterPro GO Names
        data_list = []
        start = 0
        for end in [i for i, chr in enumerate(record) if chr == '\t']:
            data_list.append(record[start:end])
            start = end + 1
        data_list.append(record[start:].strip('\n'))
        try:
            # -- selected_seq = data_list[0]
            tags = data_list[1]
            seq_name = data_list[2]
            description = data_list[3]
            length = data_list[4]
            hit_counter = data_list[5]
            e_value = data_list[6]
            sim_mean = data_list[7]
            go_counter = data_list[8]
            go_ids = data_list[9]
            go_names = data_list[10]
            enzyme_codes = data_list[11]
            enzyme_names = data_list[12]
            interpro_ids = data_list[13]
            interpro_go_ids = data_list[14]
            interpro_go_names = data_list[15]
        except Exception as e:
            raise ProgramException(e, 'F009', os.path.basename(file_name), record_counter) from e

        # get the record data dictionary
        data_dict = {'tags': tags, 'seq_name': seq_name, 'description': description, 'length': length, 'hit_counter': hit_counter, 'e_value': e_value, 'sim_mean': sim_mean, 'go_counter': go_counter, 'go_ids': go_ids, 'go_names': go_names, 'enzyme_codes': enzyme_codes, 'enzyme_names': enzyme_names, 'interpro_ids': interpro_ids, 'interpro_go_ids': interpro_go_ids, 'interpro_go_names': interpro_go_names}

    # if there is not record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

def read_entap_runn_annotation_record(file_name, file_id, record_counter):
    '''
    Read the next record of the functional annotation file built by EnTAP application using the runN option.
    '''

    # initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read next record
    record = file_id.readline()

    # if there is record
    if record != '':

        # remove EOL
        record = record.strip('\n')

        # extract data
        # -- EnTAP record format: Query Sequence	Subject Sequence	Percent Identical	Alignment Length	Mismatches	Gap Openings	Query Start	Query End	Subject Start	Subject End	E Value	Coverage	Description	Species	Taxonomic Lineage	Origin Database	Contaminant	Informative	Seed Ortholog	Seed E-Value	Seed Score	Predicted Gene	Tax Scope	Tax Scope Max	Member OGs	KEGG Terms	GO Biological	GO Cellular	GO Molecular
        # EnTAP record format: Query Sequence	Subject Sequence	Percent Identical	Alignment Length	Mismatches	Gap Openings	Query Start	Query End	Subject Start	Subject End	E Value	Coverage	Description	Species	Taxonomic Lineage	Origin Database	Contaminant	Informative	EggNOG Seed Ortholog	EggNOG Seed E-Value	EggNOG Seed Score	EggNOG Tax Scope Max	EggNOG Member OGs	EggNOG Description	EggNOG COG Abbreviation	EggNOG COG Description	EggNOG BIGG Reaction	EggNOG KEGG KO	EggNOG KEGG Pathway	EggNOG KEGG Module	EggNOG KEGG Reaction	EggNOG KEGG RClass	EggNOG BRITE	EggNOG GO Biological	EggNOG GO Cellular	EggNOG GO Molecular	EggNOG Protein Domains
        data_list = []
        start = 0
        for end in [i for i, chr in enumerate(record) if chr == '\t']:
            data_list.append(record[start:end])
            start = end + 1
        data_list.append(record[start:].strip('\n'))
        try:
            query_sequence = data_list[0]
            subject_sequence = data_list[1]
            percent_identical = data_list[2]
            alignment_length = data_list[3]
            mismatches = data_list[4]
            gap_openings = data_list[5]
            query_start = data_list[6]
            query_end = data_list[7]
            subject_start = data_list[8]
            subject_end = data_list[9]
            e_value = data_list[10]
            coverage = data_list[11]
            description = data_list[12]
            species = data_list[13]
            taxonomic_lineage = data_list[14]
            origin_database = data_list[15]
            contaminant = data_list[16]
            informative = data_list[17]
            # -- seed_ortholog = data_list[18]
            # -- seed_e_value = data_list[19]
            # -- seed_score = data_list[20]
            # -- predicted_gene = data_list[21]
            # -- tax_scope = data_list[22]
            # -- tax_scope_max = data_list[23]
            # -- member_ogs = data_list[24]
            # -- kegg_terms = data_list[25]
            # -- go_biological = data_list[26]
            # -- go_cellular = data_list[27]
            # -- go_molecular = data_list[28]
            eggnog_seed_ortholog = data_list[18]
            eggnog_seed_e_value = data_list[19]
            eggnog_seed_score = data_list[20]
            eggnog_tax_scope_max = data_list[21]
            eggnog_member_ogs = data_list[22]
            eggnog_description = data_list[23]
            eggnog_cog_abbreviation = data_list[24]
            eggnog_cog_description = data_list[25]
            eggnog_bigg_reaction = data_list[26]
            eggnog_kegg_ko = data_list[27]
            eggnog_kegg_pathway  = data_list[28]
            eggnog_kegg_module = data_list[29]
            eggnog_kegg_reaction = data_list[30]
            eggnog_kegg_rclass = data_list[31]
            eggnog_brite = data_list[32]
            eggnog_go_biological = data_list[33]
            eggnog_go_cellular = data_list[34]
            eggnog_go_molecular = data_list[35]
            eggnog_protein_domains = data_list[36]
        except Exception as e:
            raise ProgramException(e, 'F009', os.path.basename(file_name), record_counter) from e

        # get the record data dictionary
        # -- data_dict = {'query_sequence': query_sequence, 'subject_sequence': subject_sequence, 'percent_identical': percent_identical, 'alignment_length': alignment_length, 'mismatches': mismatches, 'gap_openings': gap_openings, 'query_start': query_start, 'query_end': query_end, 'subject_start': subject_start, 'subject_end': subject_end, 'e_value': e_value, 'coverage': coverage, 'description': description, 'species': species, 'taxonomic_lineage': taxonomic_lineage, 'origin_databasem': origin_database, 'contaminant': contaminant, 'informative': informative, 'seed_ortholog': seed_ortholog, 'seed_e_value': seed_e_value, 'seed_score': seed_score, 'predicted_gene': predicted_gene, 'tax_scope': tax_scope, 'tax_scope_max': tax_scope_max, 'member_ogs': member_ogs, 'kegg_terms': kegg_terms, 'go_biological': go_biological, 'go_cellular': go_cellular, 'go_molecular': go_molecular}
        data_dict = {'query_sequence': query_sequence, 'subject_sequence': subject_sequence, 'percent_identical': percent_identical, 'alignment_length': alignment_length, 'mismatches': mismatches, 'gap_openings': gap_openings, 'query_start': query_start, 'query_end': query_end, 'subject_start': subject_start, 'subject_end': subject_end, 'e_value': e_value, 'coverage': coverage, 'description': description, 'species': species, 'taxonomic_lineage': taxonomic_lineage, 'origin_databasem': origin_database, 'contaminant': contaminant, 'informative': informative, 'eggnog_seed_ortholog': eggnog_seed_ortholog, 'eggnog_seed_e_value': eggnog_seed_e_value, 'eggnog_seed_score': eggnog_seed_score, 'eggnog_tax_scope_max': eggnog_tax_scope_max, 'eggnog_member_ogs': eggnog_member_ogs, 'eggnog_description': eggnog_description, 'eggnog_cog_abbreviation': eggnog_cog_abbreviation, 'eggnog_cog_description': eggnog_cog_description, 'eggnog_bigg_reaction': eggnog_bigg_reaction, 'eggnog_kegg_ko': eggnog_kegg_ko, 'eggnog_kegg_pathway': eggnog_kegg_pathway, 'eggnog_kegg_module': eggnog_kegg_module, 'eggnog_kegg_reaction': eggnog_kegg_reaction, 'eggnog_kegg_rclass': eggnog_kegg_rclass, 'eggnog_brite': eggnog_brite, 'eggnog_go_biological': eggnog_go_biological, 'eggnog_go_cellular': eggnog_go_cellular, 'eggnog_go_molecular': eggnog_go_molecular, 'eggnog_protein_domains': eggnog_protein_domains}

    # if there is not record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

def read_entap_runp_annotation_record(file_name, file_id, record_counter):
    '''
    Read the next record of the functional annotation file built by EnTAP application using the runP option.
    '''

    # initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read next record
    record = file_id.readline()

    # if there is record
    if record != '':

        # remove EOL
        record = record.strip('\n')

        # extract data
        # -- EnTAP record format: Query Sequence	Frame	Subject Sequence	Percent Identical	Alignment Length	Mismatches	Gap Openings	Query Start	Query End	Subject Start	Subject End	E Value	Coverage	Description	Species	Taxonomic Lineage	Origin Database	Contaminant	Informative	Seed Ortholog	Seed E-Value	Seed Score	Predicted Gene	Tax Scope	Tax Scope Max	Member OGs	KEGG Terms	GO Biological	GO Cellular	GO Molecular
        # EnTAP record format: Query Sequence	Frame	Subject Sequence	Percent Identical	Alignment Length	Mismatches	Gap Openings	Query Start	Query End	Subject Start	Subject End	E Value	Coverage	Description	Species	Taxonomic Lineage	Origin Database	Contaminant	Informative	EggNOG Seed Ortholog	EggNOG Seed E-Value	EggNOG Seed Score	EggNOG Tax Scope Max	EggNOG Member OGs	EggNOG Description	EggNOG COG Abbreviation	EggNOG COG Description	EggNOG BIGG Reaction	EggNOG KEGG KO	EggNOG KEGG Pathway	EggNOG KEGG Module	EggNOG KEGG Reaction	EggNOG KEGG RClass	EggNOG BRITE	EggNOG GO Biological	EggNOG GO Cellular	EggNOG GO Molecular	EggNOG Protein Domains
        data_list = []
        start = 0
        for end in [i for i, chr in enumerate(record) if chr == '\t']:
            data_list.append(record[start:end])
            start = end + 1
        data_list.append(record[start:].strip('\n'))
        try:
            query_sequence = data_list[0]
            frame = data_list[1]
            subject_sequence = data_list[2]
            percent_identical = data_list[3]
            alignment_length = data_list[4]
            mismatches = data_list[5]
            gap_openings = data_list[6]
            query_start = data_list[7]
            query_end = data_list[8]
            subject_start = data_list[9]
            subject_end = data_list[10]
            e_value = data_list[11]
            coverage = data_list[12]
            description = data_list[13]
            species = data_list[14]
            taxonomic_lineage = data_list[15]
            origin_database = data_list[16]
            contaminant = data_list[17]
            informative = data_list[18]
            # -- seed_ortholog = data_list[19]
            # -- seed_e_value = data_list[20]
            # -- seed_score = data_list[21]
            # -- predicted_gene = data_list[22]
            # -- tax_scope = data_list[23]
            # -- tax_scope_max = data_list[24]
            # -- member_ogs = data_list[25]
            # -- kegg_terms = data_list[26]
            # -- go_biological = data_list[27]
            # -- go_cellular = data_list[28]
            # -- go_molecular = data_list[29]
            eggnog_seed_ortholog = data_list[19]
            eggnog_seed_e_value = data_list[20]
            eggnog_seed_score = data_list[21]
            eggnog_tax_scope_max = data_list[22]
            eggnog_member_ogs = data_list[23]
            eggnog_description = data_list[24]
            eggnog_cog_abbreviation = data_list[25]
            eggnog_cog_description = data_list[26]
            eggnog_bigg_reaction = data_list[27]
            eggnog_kegg_ko = data_list[28]
            eggnog_kegg_pathway  = data_list[29]
            eggnog_kegg_module = data_list[30]
            eggnog_kegg_reaction = data_list[31]
            eggnog_kegg_rclass = data_list[32]
            eggnog_brite = data_list[33]
            eggnog_go_biological = data_list[34]
            eggnog_go_cellular = data_list[35]
            eggnog_go_molecular = data_list[36]
            eggnog_protein_domains = data_list[37]
        except Exception as e:
            raise ProgramException(e, 'F009', os.path.basename(file_name), record_counter) from e

        # get the record data dictionary
        # -- data_dict = {'query_sequence': query_sequence, 'frame': frame, 'subject_sequence': subject_sequence, 'percent_identical': percent_identical, 'alignment_length': alignment_length, 'mismatches': mismatches, 'gap_openings': gap_openings, 'query_start': query_start, 'query_end': query_end, 'subject_start': subject_start, 'subject_end': subject_end, 'e_value': e_value, 'coverage': coverage, 'description': description, 'species': species, 'taxonomic_lineage': taxonomic_lineage, 'origin_databasem': origin_database, 'contaminant': contaminant, 'informative': informative, 'seed_ortholog': seed_ortholog, 'seed_e_value': seed_e_value, 'seed_score': seed_score, 'predicted_gene': predicted_gene, 'tax_scope': tax_scope, 'tax_scope_max': tax_scope_max, 'member_ogs': member_ogs, 'kegg_terms': kegg_terms, 'go_biological': go_biological, 'go_cellular': go_cellular, 'go_molecular': go_molecular}
        data_dict = {'query_sequence': query_sequence, 'frame': frame, 'subject_sequence': subject_sequence, 'percent_identical': percent_identical, 'alignment_length': alignment_length, 'mismatches': mismatches, 'gap_openings': gap_openings, 'query_start': query_start, 'query_end': query_end, 'subject_start': subject_start, 'subject_end': subject_end, 'e_value': e_value, 'coverage': coverage, 'description': description, 'species': species, 'taxonomic_lineage': taxonomic_lineage, 'origin_databasem': origin_database, 'contaminant': contaminant, 'informative': informative, 'eggnog_seed_ortholog': eggnog_seed_ortholog, 'eggnog_seed_e_value': eggnog_seed_e_value, 'eggnog_seed_score': eggnog_seed_score, 'eggnog_tax_scope_max': eggnog_tax_scope_max, 'eggnog_member_ogs': eggnog_member_ogs, 'eggnog_description': eggnog_description, 'eggnog_cog_abbreviation': eggnog_cog_abbreviation, 'eggnog_cog_description': eggnog_cog_description, 'eggnog_bigg_reaction': eggnog_bigg_reaction, 'eggnog_kegg_ko': eggnog_kegg_ko, 'eggnog_kegg_pathway': eggnog_kegg_pathway, 'eggnog_kegg_module': eggnog_kegg_module, 'eggnog_kegg_reaction': eggnog_kegg_reaction, 'eggnog_kegg_rclass': eggnog_kegg_rclass, 'eggnog_brite': eggnog_brite, 'eggnog_go_biological': eggnog_go_biological, 'eggnog_go_cellular': eggnog_go_cellular, 'eggnog_go_molecular': eggnog_go_molecular, 'eggnog_protein_domains': eggnog_protein_domains}

    # if there is not record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

def read_trapid_annotation_record(file_name, file_id, record_counter):
    '''
    Read the next record of the functional annotation file built by TRAPID application.
    '''

    # initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read next record
    record = file_id.readline()

    # if there is record
    if record != '':

        # remove EOL
        record = record.strip('\n')

        # extract data
        # TRAPID record format: counter	transcript_id	go	evidence_code	is_hidden	description
        data_list = []
        start = 0
        for end in [i for i, chr in enumerate(record) if chr == '\t']:
            data_list.append(record[start:end])
            start = end + 1
        data_list.append(record[start:].strip('\n'))
        try:
            counter = data_list[0]
            transcript_id = data_list[1]
            go = data_list[2]
            evidence_code = data_list[3]
            is_hidden = data_list[4]
            description = data_list[5]
        except Exception as e:
            raise ProgramException(e, 'F009', os.path.basename(file_name), record_counter) from e

        # get the record data dictionary
        data_dict = {'counter': counter, 'transcript_id': transcript_id, 'go': go, 'evidence_code': evidence_code, 'is_hidden': is_hidden, 'description': description}

    # if there is not record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

def read_trinotate_annotation_record(file_name, file_id, record_counter):
    '''
    Read the next record of the functional annotation file built by Trinotate application.
    '''

    # initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read next record
    record = file_id.readline()

    # if there is record
    if record != '':

        # remove EOL
        record = record.strip('\n')

        # extract data
        # Trinotate record format: True	Tags	SeqName	Description	Length	#Hits	e-Value	sim mean	#GO	GO IDs	GO Names	Enzyme Codes	Enzyme Names	InterPro IDs	InterPro GO IDs	InterPro GO Names
        data_list = []
        start = 0
        for end in [i for i, chr in enumerate(record) if chr == '\t']:
            data_list.append(record[start:end])
            start = end + 1
        data_list.append(record[start:].strip('\n'))
        try:
            gene_id = data_list[0]
            transcript_id = data_list[1]
            sprot_top_blastx_hit = data_list[2]
            rnammer = data_list[3]
            prot_id = data_list[4]
            prot_coords = data_list[5]
            sprot_top_blastp_hit = data_list[6]
            pfam = data_list[7]
            signalp = data_list[8]
            tmhmmx = data_list[9]
            eggnog = data_list[10]
            kegg = data_list[11]
            gene_ontology_blastx = data_list[12]
            gene_ontology_blastp = data_list[13]
            gene_ontology_pfam = data_list[14]
            transcript = data_list[15]
            peptide = data_list[16]
        except Exception as e:
            raise ProgramException(e, 'F009', os.path.basename(file_name), record_counter) from e

        # get the record data dictionary
        data_dict = {'gene_id': gene_id, 'transcript_id': transcript_id, 'sprot_top_blastx_hit': sprot_top_blastx_hit, 'rnammer': rnammer, 'prot_id': prot_id, 'prot_coords': prot_coords, 'sprot_top_blastp_hit': sprot_top_blastp_hit, 'pfam': pfam, 'signalp': signalp, 'tmhmmx': tmhmmx, 'eggnog': eggnog, 'kegg': kegg, 'gene_ontology_blastx': gene_ontology_blastx, 'gene_ontology_blastp': gene_ontology_blastp, 'gene_ontology_pfam': gene_ontology_pfam, 'transcript': transcript, 'peptide': peptide}

    # if there is not record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

def build_go_ontology_dict(ontology_file):
    '''
    Build the dictionary of GO ontology data from a GO ontology data.
    '''

    # initialize the dictionary of GO ontology data
    go_ontology_dict = NestedDefaultDict()

    # open the ontology file
    if ontology_file.endswith('.gz'):
        try:
            ontology_file_id = gzip.open(ontology_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise ProgramException(e, 'F002', ontology_file) from e
    else:
        try:
            ontology_file_id = open(ontology_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise ProgramException(e, 'F001', ontology_file) from e

    # initialize the GO term counter
    go_term_counter = 0

    # initialize the record counter
    record_counter = 0

    # read the first record
    record = ontology_file_id.readline()

    # while there are records and they are the header
    while record != '' and not record.startswith('[Term]'):

        # add 1 to record counter
        record_counter += 1

        # print record counter
        Message.print('verbose', f'\rOntology file: {record_counter} processed records - # GO terms: {go_term_counter}.')

        # read the next record
        record = ontology_file_id.readline()

    # if there is a first term block
    if record.startswith('[Term]'):

        # while there are records
        while record != '':

            # add 1 to record counter
            record_counter += 1

            # print record counter
            Message.print('verbose', f'\rOntology file: {record_counter} processed records - # GO terms: {go_term_counter}.')

            # read the next record
            record = ontology_file_id.readline()

            # initialize go term data
            go_id = ''
            go_name = ''
            namespace = ''
            alt_id_list = []

            # while there are records and they are term details
            while record != '' and not record.startswith('[Term]'):

                # add 1 to record counter
                record_counter += 1

                # get the GO identification
                if record.startswith('id:'):
                    go_id = record[len('id:'):].strip()

                # get the GO name
                if record.startswith('name:'):
                    go_name = record[len('name:'):].strip()

                    # change semicolons in go_name
                    go_name = go_name.replace(';', ',')

                # get the namespace
                if record.startswith('namespace:'):
                    namespace = record[len('namespace:'):].strip()

                # get the alternative identificationnamespace
                if record.startswith('alt_id:'):
                    alt_id_list.append(record[len('alt_id:'):].strip())

                # print record counter
                Message.print('verbose', f'\rOntology file: {record_counter} processed records - # GO terms: {go_term_counter}.')

                # read the next record
                record = ontology_file_id.readline()

                # break the loop when typedef sections start
                if record.startswith('[Typedef]'):
                    break

            # insert data into the dictionary of GO ontology data
            go_ontology_dict[go_id] = {'go_id': go_id, 'go_name': go_name, 'namespace': namespace}
            go_term_counter += 1
            for alt_id in alt_id_list:
                go_ontology_dict[alt_id] = {'go_id': alt_id, 'go_name': go_name, 'namespace': namespace}
                go_term_counter += 1

            # print record counter
            Message.print('verbose', f'\rOntology file: {record_counter} processed records - # GO terms: {go_term_counter}.')

            # break the loop when typedef sections start
            if record.startswith('[Typedef]'):
                break

    Message.print('verbose', '\n')

    # close ontology file
    ontology_file_id.close()

    # return the dictionary of GO ontology data
    return go_ontology_dict

#-------------------------------------------------------------------------------

def get_all_species_code():
    '''
    Get the code used to identify the selection by all species.
    '''

    return 'all_species'

#-------------------------------------------------------------------------------

def get_all_species_name():
    '''
    Get the text used to identify the selection by all species.
    '''

    return 'all species'

#-------------------------------------------------------------------------------

def get_fix_code_list():
    '''
    Get the code list of "fix".
    '''

    return ['Y', 'N']

#-------------------------------------------------------------------------------

def get_fix_code_list_text():
    '''
    Get the code list of "fix" as text.
    '''

    return 'Y (yes) or N (no)'

#-------------------------------------------------------------------------------

def get_scenario_code_list():
    '''
    Get the code list of "scenario".
    '''

    return ['0', '1', '2', '3']

#-------------------------------------------------------------------------------

def get_scenario_code_list_text():
    '''
    Get the code list of "scenario" as text.
    '''

    return '0 (no imputation) or 1 (standard) or 2 (maximum possible imputation) or 3 (maximum possible missing data)'

#-------------------------------------------------------------------------------

def get_md_symbol():
    '''
    Get the "missing_data" symbol.
    '''

    return '.'

#-------------------------------------------------------------------------------

def get_md_code_list():
    '''
    Get the code list of "missing_data".
    '''

    return ['./.', '.|.']

#-------------------------------------------------------------------------------

def get_md_code_list_text():
    '''
    Get the code list of "missing_data" as text.
    '''

    return str(get_md_code_list()).strip('[]').replace('\'','').replace(',', ' or')

#-------------------------------------------------------------------------------

def get_allele_transformation_code_list():
    '''
    Get the code list of "allele_transformation".
    '''

    return ['ADD100', 'ATCG', 'NONE']

#-------------------------------------------------------------------------------

def get_allele_transformation_code_list_text():
    '''
    Get the code list of "allele_transformation" as text.
    '''

    return 'ADD100 (add 100 to allele symbol when it is numeric) OR ATCG (A->1;T->2;C->3;G->4) or NONE'

#-------------------------------------------------------------------------------

def get_converted_file_type_code_list():
    '''
    Get the code list of "converted_file_type".
    '''

    return ['0', '1', '2']

#-------------------------------------------------------------------------------

def get_converted_file_type_code_list_text():
    '''
    Get the code list of "converted_file_type" as text.
    '''

    return '0 (Structure input format in two lines, all variants) or 1 (Structure input format in two lines, only variants without any imputed missing data) or 2 (PHASE input format)'

#-------------------------------------------------------------------------------

def get_go_app_code_list():
    '''
    Get the code list of applications applications that calculate the statistics of GO terms.
    '''

    return ['Blast2GO', 'EnTAP', 'TOA', 'TRAPID', 'Trinotate']

#-------------------------------------------------------------------------------

def get_go_app_code_list_text():
    '''
    Get the code list of applications applications that calculate the statistics of GO terms as text.
    '''

    return str(get_go_app_code_list()).strip('[]').replace('\'', '').replace(',', ' or')

#-------------------------------------------------------------------------------

def get_go_app_code_list_2():
    '''
    Get the code list of applications applications that calculate the enrichment analysis of GO terms.
    '''

    return ['EnTAP-runN', 'EnTAP-runP', 'gymnoTOA', 'TOA', 'TRAPID']

#-------------------------------------------------------------------------------

def get_go_app_code_list_2_text():
    '''
    Get the code list of applications applications that calculate the enrichment analysis of GO terms as text.
    '''

    return str(get_go_app_code_list_2()).strip('[]').replace('\'', '').replace(',', ' or')

#-------------------------------------------------------------------------------

def get_toa_go_seleccion_code_list():
    '''
    Get the code list of selection code for GO term data in TOA results.
    '''

    return ['LEV', 'LEVWD']

#-------------------------------------------------------------------------------

def get_toa_go_seleccion_code_list_text():
    '''
    Get the code list of selection code for GO term data in TOA results as text.
    '''

    return 'LEV (the lowest e-value -GO data can be empty- is considered) or LEVWD (the lowest e-value with GO data not empty is considered)'

#-------------------------------------------------------------------------------

def get_structure_input_format_code_list():
    '''
    Get the code list of "structure_input_format".
    '''

    # -- return ['1', '2']
    return ['2']

#-------------------------------------------------------------------------------

def get_structure_input_format_code_list_text():
    '''
    Get the code list of "structure_input_format" as text.
    '''

    # -- return '1 (one line: one allele in different columns) or 2 (two lines:  one allele in different rows)'
    return '2 (two lines:  one allele in different rows)'

#-------------------------------------------------------------------------------

def get_structure_swap_type_code_list():
    '''
    Get the code list of "structure_input_format".
    '''

    # -- return ['1TO2', '2TO1']
    return ['2TO1']

#-------------------------------------------------------------------------------

def get_structure_swap_type_code_list_text():
    '''
    Get the code list of "structure_swap_type" as text.
    '''

    # -- return '1TO2 (one line to two lines) or 2TO1 (two lines to one line)'
    return '2TO1 (two lines to one line)'

#-------------------------------------------------------------------------------

def get_strcuture_purge_code_list():
    '''
    Get the code list of "structure_purge_code".
    '''

    return ['CHAVAL', 'DELCOL']

#-------------------------------------------------------------------------------

def get_structure_purge_code_list_text():
    '''
    Get the code list of "structure_purge_code" as text.
    '''

    return 'CHAVAL (change a value by a new value) or DELCOL (delete columns containing a determined value)'

#-------------------------------------------------------------------------------

def get_vcf_purge_code_list():
    '''
    Get the code list of "vcf_purge_variant".
    '''

    return ['CHAVAL', 'FILVAR']

#-------------------------------------------------------------------------------

def get_vcf_purge_code_list_text():
    '''
    Get the code list of "vcf_purge_variant" as text.
    '''

    return 'CHAVAL (change a value by a new value) or FILVAR (filter variants containing a determined value)'

#-------------------------------------------------------------------------------

def get_vcf_reduction_code_list():
    '''
    Get the code list of "vcf_reduction_variant".
    '''

    return ['RANDOM']

#-------------------------------------------------------------------------------

def get_vcf_reduction_code_list_text():
    '''
    Get the code list of "vcf_reduction_variant" as text.
    '''

    return 'RANDOM (Reduce randomly variants)'

#-------------------------------------------------------------------------------

def get_simulation_method_code_list():
    '''
    Get the code list of "simulation_method".
    '''

    return ['RANDOM']

#-------------------------------------------------------------------------------

def get_simulation_method_code_list_text():
    '''
    Get the code list of "simulation_method" as text.
    '''

    return 'RANDOM'

#-------------------------------------------------------------------------------

def get_r_estimator_code_list():
    '''
    Get the code list of "r_estimator".
    '''

    return ['ru', 'rw']

#-------------------------------------------------------------------------------

def get_r_estimator_code_list_text():
    '''
    Get the code list of "r_estimator" as text.
    '''

    return 'ru (the unweighted average estimator) or rw (the weighted estimator)'

#-------------------------------------------------------------------------------

def get_genotype_imputation_method_code_list():
    '''
    Get the code list of "genotype_imputation_method".
    '''

    return ['MF', 'CK']

#-------------------------------------------------------------------------------

def get_genotype_imputation_method_code_list_text():
    '''
    Get the code list of "genotype_ imputation_method" as text.
    '''

    return 'MF (the most frequent genotype) or CK (the genotype of the closest kinship individual)'

#-------------------------------------------------------------------------------

def get_vcf_filtering_action_code_list():
    '''
    Get the code list of "genotype_imputation_method".
    '''

    return ['MM']

#-------------------------------------------------------------------------------

def get_vcf_filtering_action_code_list_text():
    '''
    Get the code list of "genotype_ imputation_method" as text.
    '''

    return 'MM (variants with all monomorphic individuals)'

#-------------------------------------------------------------------------------

def get_fdr_method_code_list():
    '''
    Get the code list of "fdr_method".
    '''

    return ['bh', 'by']

#-------------------------------------------------------------------------------

def get_fdr_method_code_list_text():
    '''
    Get the code list of "fdr_method" as text.
    '''

    return 'bh (Benjamini-Hochberg) or by (Benjamini-Yekutieli)'

#-------------------------------------------------------------------------------

def get_fdr_method_text_list():
    '''
    Get the list of "fdr_method" as text.
    '''

    return ['Benjamini-Hochberg', 'Benjamini-Yekutieli']

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

def get_na():
    '''
    Get the characters to represent not available.
    '''

    return 'N/A'

#-------------------------------------------------------------------------------

def get_separator():
    '''
    Get the separation line between process steps.
    '''

    return '**************************************************'

#-------------------------------------------------------------------------------

class DevNull(object):
    '''
    This class is used when it is necessary do not write a output
    '''

    #---------------

    def write(self, *_):
        '''
        Do not write anything.
        '''

        pass

    #---------------

#-------------------------------------------------------------------------------

class Const():
    '''
    This class has attributes with values will be used as constants.
    '''

    #---------------

    DEFAULT_BLASTX_THREADS_NUMBER = 1
    DEFAULT_BURN_IN = 100
    DEFAULT_E_VALUE = 1E-6
    DEFAULT_FDR_METHOD = 'by'
    DEFAULT_GENOTYPE_IMPUTATION_METHOD = 'MF'
    DEFAULT_ID_TYPE = 'LITERAL'
    DEFAULT_IMPUTED_MD_ID = '99'
    DEFAULT_ITERATIONS_NUMBER = 100
    DEFAULT_MACHINE_TYPE = 'local'
    DEFAULT_MAX_HSPS = 999999
    DEFAULT_MAXPERC_IND_WMD = 10
    DEFAULT_MAX_TARGET_SEQS = 10
    DEFAULT_MAXLEN = 10000
    DEFAULT_MIN_DEPTH = 1
    DEFAULT_MIN_SEQNUM_ANNOTATIONS = 5
    DEFAULT_MIN_SEQNUM_SPECIES = 10
    DEFAULT_MINFPKM = 1.0
    DEFAULT_MINLEN = 200
    DEFAULT_MINTPM = 1.0
    DEFAULT_NEW_MD_ID = 'U'
    DEFAULT_NODE_NUMBER = 1
    DEFAULT_NUCLEOTIDE_NUMBER = 25
    DEFAULT_QCOV_HSP_PERC = 0.0
    DEFAULT_PROCESSES_NUMBER = 4
    DEFAULT_THINNING_INTERVAL = 1
    DEFAULT_TOA_GO_SELECCTION = 'LEVWD'
    DEFAULT_R_ESTIMATOR = 'ru'
    DEFAULT_STRUCTURE_INFO_COL_NUMBER = 2
    DEFAULT_TRACE = 'N'
    DEFAULT_VARIANT_NUMBER_PER_FILE = 1000
    DEFAULT_VCF_FILTERING_ACTION = 'MM'
    DEFAULT_VERBOSE = 'N'

    #---------------

    FRAGPROB_LOWEST = 0.0
    FRAGPROB_UPPEST = 1.0
    INDELPROB_LOWEST = 0.0
    INDELPROB_UPPEST = 1.0
    MAXFRAGNUM_LOWEST = 2
    MAXFRAGNUM_UPPEST = 5
    MAXMUTNUM_LOWEST = 1
    MAXMUTNUM_UPPEST = 10
    MAXMUTSIZE_LOWEST = 1
    MAXMUTSIZE_UPPEST = 30
    MAXSHORTENING_LOWEST = 0
    MAXSHORTENING_UPPEST = 10
    MUTPROB_LOWEST = 0.0
    MUTPROB_UPPEST = 1.0

    #---------------

    AS_GENERATED_BY_NGSCLOUD = 'ngscloud'
    AS_SOAPDENOVOTRANS_CODE = 'sdnt'
    AS_TRINITY_CODE = 'trinity'

   #---------------

    DELAY_TIME = 60
    FASTA_RECORD_LEN = 70
    MAX_QUERY_NUMBER_PER_FILE = 1000000

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

    @staticmethod
    def set_verbose_status(status):

        Message.verbose_status = status

    #---------------

    @staticmethod
    def set_trace_status(status):

        Message.trace_status = status

    #---------------

    @staticmethod
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

class ProgramException(Exception):
    '''
    This class controls various exceptions that can occur in the execution of the application.
    '''

   #---------------

    def __init__(self, e, code_exception, param1='', param2='', param3='', param4='', param5='', param6=''):
        '''Initialize the object to manage a passed exception.'''

        # call the init method of the parent class
        super().__init__()

        # print the message of the exception
        if e != '':
            Message.print('error', f'*** EXCEPTION: "{e}"')

        # manage the code of exception
        if code_exception == 'B001':
            Message.print('error', f'*** ERROR {code_exception}: The database {param1} can not be connected.')
        elif code_exception == 'B002':
            Message.print('error', f'*** ERROR {code_exception} in sentence:')
            Message.print('error', f'{param1}')
        elif code_exception == 'B003':
            Message.print('error', f'*** ERROR {code_exception}: The table {param1} is not loaded.')
        elif code_exception == 'D001':
            Message.print('error', f'*** ERROR {code_exception}: Invalid pattern of record --->{param1}<--- in file {param2}.')
        elif code_exception == 'D002':
            Message.print('error', f'*** ERROR {code_exception}: {param1} is not an integer number and therefore it is a invalid value to {param2}.')
        elif code_exception == 'D003':
            Message.print('error', f'*** ERROR {code_exception}: {param1} is not a float number and therefore it is a invalid value to {param2}.')
        elif code_exception == 'D004':
            Message.print('error', f'*** ERROR {code_exception}: There are wrong nucleotide code in the variant with identification {param1} and position {param2}.')
        elif code_exception == 'F001':
            Message.print('error', f'*** ERROR {code_exception}: The file {param1} can not be opened.')
        elif code_exception == 'F002':
            Message.print('error', f'*** ERROR {code_exception}: The GZ compressed file {param1} can not be opened.')
        elif code_exception == 'F003':
            Message.print('error', f'*** ERROR {code_exception}: The file {param1} can not be written.')
        elif code_exception == 'F004':
            Message.print('error', f'*** ERROR {code_exception}: The GZ compressed file {param1} can not be written.')
        elif code_exception == 'F005':
            Message.print('error', f'*** ERROR {code_exception}: The file {param1} can not be built.')
        elif code_exception == 'F006':
            Message.print('error', f'*** ERROR {code_exception}: The format of file {param1} is not {param2}.')
        elif code_exception == 'F007':
            Message.print('error', f'*** ERROR {code_exception}: Header record {param1} is wrong.')
        elif code_exception == 'F008':
            Message.print('error', f'*** ERROR {code_exception:} The output xml files can not be concatenated.')
        elif code_exception == 'F009':
            Message.print('error', f'*** ERROR {code_exception}: The record # {param1} of file {param1} has a wrong format.')
        elif code_exception == 'F010':
            Message.print('error', f'*** ERROR {code_exception}: The {param1} data is wrong in the transcript {param2}.')
        elif code_exception == 'F011':
            Message.print('error', f'*** ERROR {code_exception}: The chimeric data format is wrong in the transcript {param1}.')
        elif code_exception == 'I001':
            Message.print('error', f'*** ERROR {code_exception}: The infrastructure software is not setup.')
        elif code_exception == 'L001':
            Message.print('error', f'*** ERROR {code_exception}: There are wrong species identifications.')
        elif code_exception == 'L002':
            Message.print('error', f'*** ERROR {code_exception}: The identification {param1} is not in the sample file.')
        elif code_exception == 'L003':
            Message.print('error', f'*** ERROR {code_exception}: The record started by "#CHROM" is not found before variant records in the VCF file.')
        elif code_exception == 'L004':
            Message.print('error', f'*** ERROR {code_exception}: The sequence identification {param1} is not found in the VCF file.')
        elif code_exception == 'L005':
            Message.print('error', f'*** ERROR {code_exception}: The position is not a integer number in the variant with identification {param1} and position {param2}.')
        elif code_exception == 'L006':
            Message.print('error', f'*** ERROR {code_exception}: The sample data number is wrong in the variant with identification {param1} and position {param2}.')
        elif code_exception == 'L007':
            Message.print('error', f'*** ERROR {code_exception}: The field {param1} is not found in the variant with identification {param2} and position {param3}.')
        elif code_exception == 'L008':
            Message.print('error', f'*** ERROR {code_exception}: The field {param1} has an invalid value in the variant with identification {param2} and position {param3}.')
        elif code_exception == 'L009':
            Message.print('error', f'*** ERROR {code_exception}: Mother alleles are not OK in\nCHROM: {param1} - POS: {param2} - SAMPLE: {param3} - IMPUTATION: {param4} - DISTINCT MOTHER ALLELES: {param5} - SAMPLE GT: {param6}.')
        elif code_exception == 'L010':
            Message.print('error', f'*** ERROR {code_exception}: Sample alleles are not OK in\nCHROM: {param1} - POS: {param2} - SAMPLE: {param3} - IMPUTATION: {param4} - DISTINCT MOTHER ALLELES: {param5} - SAMPLE GT: {param6}.')
        elif code_exception == 'L011':
            Message.print('error', f'*** ERROR {code_exception}: Ther loci number is not even.')
        elif code_exception == 'L012':
            Message.print('error', f'*** ERROR {code_exception}: There are records with different loci number.')
        elif code_exception == 'L013':
            Message.print('error', f'*** ERROR {code_exception}: There are samples with different sequence number.')
        elif code_exception == 'L014':
            Message.print('error', f'*** ERROR {code_exception}: There are samples with different variant number.')
        elif code_exception == 'L015':
            Message.print('error', f'*** ERROR {code_exception}: Transcript id or lenght or FPKM data have not been found out in score file.')
        elif code_exception == 'L016':
            Message.print('error', f'*** ERROR {code_exception}: An allele is not A, T, C or G in variant {param1}.')
        elif code_exception == 'L017':
            Message.print('error', f'*** ERROR {code_exception}: The number of samples in the two VCF files are different ({param1}: {param2} - {param3}: {param4}).')
        elif code_exception == 'L018':
            Message.print('error', f'*** ERROR {code_exception}: The sample identifications lists has to be equal in the VCF files {param1} and {param2}.')
        elif code_exception == 'L019':
            Message.print('error', f'*** ERROR {code_exception}: The variant {param1} has different reference allele in the VCF files {param2} and {param3}.')
        elif code_exception == 'L020':
            Message.print('error', f'*** ERROR {code_exception}: The variant {param1} has different alternative alleles in the VCF files {param2} and {param3}.')
        elif code_exception == 'L021':
            Message.print('error', f'\n*** ERROR {code_exception}: The variant {param1} has more than one alternative allele.')
        elif code_exception == 'L022':
            Message.print('error', f'\n*** ERROR {code_exception}: The genotype number does not correspond to variant number in the sample {param1}.')
        elif code_exception == 'P001':
            Message.print('error', f'*** ERROR {code_exception}: The program has parameters with invalid values.')
        elif code_exception == 'P002':
            Message.print('error', f'*** ERROR {code_exception}: There are some node processes ended NOT OK.')
        elif code_exception == 'S001':
            Message.print('error', f'*** ERROR {code_exception}: The {param1} OS is not supported.')
        elif code_exception == 'S002':
            Message.print('error', f'*** ERROR {code_exception}: RC {param2} in command {param1}')
        else:
            Message.print('error', f'*** ERROR {code_exception}: The exception is not managed.')

        # exit with error RC
        sys.exit(1)

   #---------------

#-------------------------------------------------------------------------------

class NestedDefaultDict(collections.defaultdict):
    '''
    This class is used to create nested dictionaries.
    '''

    #---------------

    def __init__(self, *args, **kwargs):

        super(NestedDefaultDict, self).__init__(NestedDefaultDict, *args, **kwargs)

    #---------------

    def __repr__(self):

        return repr(dict(self))

    #---------------

#-------------------------------------------------------------------------------

class BreakAllLoops(Exception):
    '''
    This class is used to break out of nested loops.
    '''

    pass

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print(f'This source contains general functions and classes used in {get_project_name()} software package used in both console mode and gui mode.')
    sys.exit(0)

#-------------------------------------------------------------------------------
