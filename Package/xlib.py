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
This source contains general functions and classes used in NGShelper
software package used in both console mode and gui mode.
'''

#-------------------------------------------------------------------------------

import collections
import gzip
import os
import re
import sys

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

    return '0.48'

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
    list = []

    # if the codification is not case sensitive, convert the code and code list to uppercase
    if not case_sensitive:
        try:
            literal = literal.upper()
        except:
            pass
        try:
            list = [x.upper() for x in text_list]
        except:
            pass
    else:
        list = text_list

    # check if the literal starts with a text in the list
    for text in list:
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
    list = []

    # if the codification is not case sensitive, convert the code and code list to uppercase
    if not case_sensitive:
        try:
            literal = literal.upper()
        except:
            pass
        try:
            list = [x.upper() for x in code_list]
        except:
            pass
    else:
        list = code_list

    # check if the code is in the code list
    OK = literal in list

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
        for i in range(sample_number):
            sample_list.append(record_data_list[i + 9])

        # set the key
        key = f'{chrom}'

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
    if sp1_id not in species_id_list or \
       sp2_id not in species_id_list or \
       hybrid_id == 'NONE' and len(species_id_list) != 2 or \
       hybrid_id != 'NONE' and (hybrid_id not in species_id_list or len(species_id_list) != 3):
        raise ProgramException(e, 'L001')

    # check the mother identification exists when it is not equal to NONE
    for key, value in sample_dict.items():
        if value['mother_id'] != 'NONE':
            if sample_dict.get(value['mother_id'], {}) == {}:
                raise ProgramException('L002', value['mother_id'])

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

def read_annotation_record(file_name, file_id, type, record_counter):
    '''
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
            # PLAZA record format:  "seq_id";"iteration_iter_num";"hit_num";"hit_accession";"hsp_num";"hsp_evalue";"hsp_identity";"hsp_positive";"hsp_gaps";"hsp_align_len";"hsp_qseq";"species";"family";"phylum";"kingdom";"superkingdom";"desc";"databases";"go_id";"go_desc";"interpro_id";"interpro_desc";"mapman_id";"mapman_desc";"ec_id";"kegg_id";"metacyc_id"
            data_list = []
            start = 0
            for end in [i for i, chr in enumerate(record) if chr == ';']:
                data_list.append(record[start:end].strip('"'))
                start = end + 1
            data_list.append(record[start:].strip('\n').strip('"'))
            try:
                seq_id = data_list[0]
                iteration_iter_num = data_list[1]
                hit_num = data_list[2]
                hit_accession = data_list[3]
                hsp_num = data_list[4]
                hsp_evalue = data_list[5]
                hsp_identity = data_list[6]
                hsp_positive = data_list[7]
                hsp_gaps = data_list[8]
                hsp_align_len = data_list[9]
                hsp_qseq = data_list[10]
                species = data_list[11]
                family = data_list[12]
                phylum = data_list[13]
                kingdom = data_list[14]
                superkingdom = data_list[15]
                desc = data_list[16]
                databases = data_list[17]
                go_id = data_list[18]
                go_desc = data_list[19]
                interpro_id = data_list[20]
                interpro_desc = data_list[21]
                mapman_id = data_list[22]
                mapman_desc = data_list[23]
                ec_id = data_list[24]
                kegg_id = data_list[25]
                metacyc_id = data_list[26]
            except Exception as e:
                raise ProgramException(e, 'F009', os.path.basename(file_name), record_counter)

            # set the key
            key = f'{seq_id}'

            # get the record data dictionary
            data_dict = {'seq_id': seq_id, 'iteration_iter_num': iteration_iter_num, 'hit_num': hit_num, 'hit_accession': hit_accession, 'hsp_num': hsp_num, 'hsp_evalue': hsp_evalue, 'hsp_identity': hsp_identity, 'hsp_positive': hsp_positive, 'hsp_gaps': hsp_gaps, 'hsp_align_len': hsp_align_len, 'hsp_qseq': hsp_qseq, 'species': species, 'family': family, 'phylum': phylum, 'kingdom': kingdom, 'superkingdom': superkingdom, 'desc': desc, 'databases': databases, 'go_id': go_id, 'go_desc': go_desc, 'interpro_id': interpro_id, 'interpro_desc': interpro_desc, 'mapman_id': mapman_id, 'mapman_desc': mapman_desc, 'ec_id': ec_id, 'kegg_id': kegg_id, 'metacyc_id': metacyc_id}

        # if type is REFSEQ
        elif type.upper() == 'REFSEQ':

            # extract data 
            # REFSEQ record format:  "seq_id";"iteration_iter_num";"hit_num";"hit_id";"hsp_num";"hsp_evalue";"hsp_identity";"hsp_positive";"hsp_gaps";"hsp_align_len";"hsp_qseq";"species";"family";"phylum";"kingdom";"superkingdom";"desc";"databases";"gene_id";"status";"rna_nucleotide_accession";"protein_accession";"genomic_nucleotide_accession";"gene_symbol";"go_id";"evidence";"go_term";"category";"interpro_id";"interpro_desc";"ec_id";"kegg_id";"metacyc_id"
            data_list = []
            start = 0
            for end in [i for i, chr in enumerate(record) if chr == ';']:
                data_list.append(record[start:end].strip('"'))
                start = end + 1
            data_list.append(record[start:].strip('"').strip('\n'))
            try:
                seq_id = data_list[0]
                iteration_iter_num = data_list[1]
                hit_num = data_list[2]
                hit_id = data_list[3]
                hsp_num = data_list[4]
                hsp_evalue = data_list[5]
                hsp_identity = data_list[6]
                hsp_positive = data_list[7]
                hsp_gaps = data_list[8]
                hsp_align_len = data_list[9]
                hsp_qseq = data_list[10]
                species = data_list[11]
                family = data_list[12]
                phylum = data_list[13]
                kingdom = data_list[14]
                superkingdom = data_list[15]
                desc = data_list[16]
                databases = data_list[17]
                gene_id = data_list[18]
                status = data_list[19]
                rna_nucleotide_accession = data_list[20]
                protein_accession = data_list[21]
                genomic_nucleotide_accession = data_list[22]
                gene_symbol = data_list[23]
                go_id = data_list[24]
                evidence = data_list[25]
                go_term = data_list[26]
                category = data_list[27]
                interpro_id = data_list[28]
                interpro_desc = data_list[29]
                ec_id = data_list[30]
                kegg_id = data_list[31]
                metacyc_id = data_list[32]
            except Exception as e:
                raise ProgramException(e, 'F009', os.path.basename(file_name), record_counter)

            # set the key
            key = f'{seq_id}'

            # get the record data dictionary
            data_dict = {'seq_id': seq_id, 'iteration_iter_num': iteration_iter_num, 'hit_num': hit_num, 'hit_id': hit_id, 'hsp_num': hsp_num,  'hsp_evalue': hsp_evalue,  'hsp_identity': hsp_identity, 'hsp_positive': hsp_positive, 'hsp_gaps': hsp_gaps, 'hsp_align_len': hsp_align_len, 'hsp_qseq': hsp_qseq, 'species': species, 'family': family, 'phylum': phylum, 'kingdom': kingdom, 'superkingdom': superkingdom, 'desc': desc, 'databases': databases, 'gene_id': gene_id, 'status': status, 'rna_nucleotide_accession': rna_nucleotide_accession, 'protein_accession': protein_accession, 'genomic_nucleotide_accession': genomic_nucleotide_accession, 'gene_symbol': gene_symbol, 'go_id': go_id, 'evidence': evidence, 'go_term': go_term, 'category':category, 'interpro_id': interpro_id, 'interpro_desc': interpro_desc, 'ec_id': ec_id, 'kegg_id': kegg_id, 'metacyc_id': metacyc_id}

        # if type is NT o NR
        if type.upper() in ['NT', 'NR']:

            # extract data 
            # PLAZA record format:  "seq_id";"iteration_iter_num";"hit_num";"hit_id";"hsp_num";"hsp_evalue";"hsp_identity";"hsp_positive";"hsp_gaps";"hsp_align_len";"hsp_qseq";"species";"family";"phylum";"kingdom";"superkingdom";"desc";"databases"
            data_list = []
            start = 0
            for end in [i for i, chr in enumerate(record) if chr == ';']:
                data_list.append(record[start:end].strip('"'))
                start = end + 1
            data_list.append(record[start:].strip('"'))
            try:
                seq_id = data_list[0]
                iteration_iter_num = data_list[12]
                hit_num = data_list[2]
                hit_id = data_list[3]
                hsp_num = data_list[4]
                hsp_evalue = data_list[5]
                hsp_identity = data_list[6]
                hsp_positive = data_list[7]
                hsp_gaps = data_list[8]
                hsp_align_len = data_list[9]
                hsp_qseq = data_list[10]
                species = data_list[11]
                family = data_list[12]
                phylum = data_list[13]
                kingdom = data_list[14]
                superkingdom = data_list[15]
                desc = data_list[16]
                databases = data_list[17]
            except Exception as e:
                raise ProgramException(e, 'F009', os.path.basename(file_name), record_counter)

            # set the key
            key = 'f{seq_id}'

            # get the record data dictionary
            data_dict = {'seq_id': seq_id, 'iteration_iter_num': iteration_iter_num, 'hit_num': hit_num, 'hit_id': hit_id, 'hsp_num': hsp_num, 'hsp_evalue': hsp_evalue, 'hsp_identity': hsp_identity, 'hsp_positive': hsp_positive, 'hsp_gaps': hsp_gaps, 'hsp_align_len': hsp_align_len, 'hsp_qseq': hsp_qseq, 'species': species, 'family': family, 'phylum': phylum, 'kingdom': kingdom, 'superkingdom': superkingdom, 'desc': desc, 'databases': databases}

        # if type is MERGER
        # MERGER record format:  "seq_id";"hit_num";"hit_id";"hsp_num";"hsp_evalue";"hsp_identity";"hsp_positive";"hsp_gaps";"hsp_align_len";"hsp_qseq";"species";"family";"phylum";"kingdom";"superkingdom";"desc";"databases";"go_id";"go_desc";"interpro_id";"interpro_desc";"mapman_id";"mapman_desc";"refseq_gene_id";"refseq_desc";"refseq_status";"refseq_protein_accession";"refseq_genomic_nucleotide_accession";"refseq_gene_symbol"
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
                hit_num = data_list[1]
                hit_id = data_list[2]
                hsp_num = data_list[3]
                hsp_evalue = data_list[4]
                hsp_identity = data_list[5]
                hsp_positive = data_list[6]
                hsp_gaps = data_list[7]
                hsp_align_len = data_list[8]
                hsp_qseq = data_list[9]
                species = data_list[10]
                family = data_list[11]
                phylum = data_list[12]
                kingdom = data_list[13]
                superkingdom = data_list[14]
                desc = data_list[15]
                databases = data_list[16]
                go_id = data_list[17]
                go_desc = data_list[18]
                interpro_id = data_list[19]
                interpro_desc = data_list[20]
                mapman_id = data_list[21]
                mapman_desc = data_list[22]
                ec_id = data_list[23]
                kegg_id = data_list[24]
                metacyc_id = data_list[25]
                refseq_gene_id = data_list[26]
                refseq_desc = data_list[27]
                refseq_status = data_list[28]
                refseq_rna_nucleotide_accession = data_list[29]
                refseq_protein_accession = data_list[30]
                refseq_genomic_nucleotide_accession = data_list[31]
                refseq_gene_symbol = data_list[32]
            except Exception as e:
                raise ProgramException(e, 'F009', os.path.basename(file_name), record_counter)

            # set the key
            key = f'{seq_id}'
    
            # get the record data dictionary
            data_dict = {'seq_id': seq_id, 'hit_num': hit_num, 'hsp_num': hsp_num, 'hit_id': hit_id, 'hsp_evalue': hsp_evalue,  'hsp_identity': hsp_identity, 'hsp_positive': hsp_positive, 'hsp_gaps': hsp_gaps, 'hsp_align_len': hsp_align_len, 'hsp_qseq': hsp_qseq, 'species': species, 'family': family, 'phylum': phylum, 'kingdom': kingdom, 'superkingdom': superkingdom, 'desc': desc, 'databases': databases, 'go_id': go_id, 'go_desc': go_desc, 'interpro_id': interpro_id, 'interpro_desc': interpro_desc, 'mapman_id': mapman_id, 'mapman_desc': mapman_desc, 'ec_id': ec_id, 'kegg_id': kegg_id, 'metacyc_id': metacyc_id, 'refseq_gene_id': refseq_gene_id, 'refseq_desc': refseq_desc, 'refseq_status': refseq_status, 'refseq_rna_nucleotide_accession': refseq_rna_nucleotide_accession, 'refseq_protein_accession': refseq_protein_accession, 'refseq_genomic_nucleotide_accession': refseq_genomic_nucleotide_accession, 'refseq_gene_symbol': refseq_gene_symbol}

    # if there is not record 
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

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

def get_structure_file_type_code_list():
    '''
    Get the code list of "structure_file_type".
    '''

    return ['0']

#-------------------------------------------------------------------------------

def get_structure_file_type_code_list_text():
    '''
    Get the code list of "structure_file_type" as text.
    '''

    return '0 (Structure format in two lines)'

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

    return ['ADD100', 'NONE']

#-------------------------------------------------------------------------------

def get_allele_transformation_code_list_text():
    '''
    Get the code list of "allele_transformation" as text.
    '''

    return 'ADD100 (add 100 to allele symbol when it is numeric) or NONE'

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

class Const():
    '''
    This class has attributes with values will be used as constants.
    '''

    #---------------

    DEFAULT_BLASTX_THREADS_NUMBER = 1
    DEFAULT_E_VALUE = 1E-6
    DEFAULT_ID_TYPE = 'LITERAL'
    DEFAULT_IMPUTED_MD_ID = '99'
    DEFAULT_MACHINE_TYPE = 'local'
    DEFAULT_MAX_HSPS = 999999
    DEFAULT_MAX_TARGET_SEQS = 10
    DEFAULT_MAXLEN = 10000
    DEFAULT_MIN_DEPTH = 1
    DEFAULT_MINFPKM = 1.0
    DEFAULT_MINLEN = 200
    DEFAULT_MINTPM = 1.0
    DEFAULT_NEW_MD_ID = 'U'
    DEFAULT_NODE_NUMBER = 1
    DEFAULT_NUCLEOTIDE_NUMBER = 25
    DEFAULT_QCOV_HSP_PERC = 0.0
    DEFAULT_TRACE = 'N'
    DEFAULT_VARIANT_NUMBER_PER_FILE = 1000
    DEFAULT_VERBOSE = 'N'

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

    def set_verbose_status(status):

        Message.verbose_status = status

    #---------------

    def set_trace_status(status):

        Message.trace_status = status

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

class ProgramException(Exception):
    '''
    This class controls various exceptions that can occur in the execution of the application.
    '''

   #---------------

    def __init__(self, e, code_exception, param1='', param2='', param3='', param4='', param5='', param6=''):
        '''Initialize the object to manage a passed exception.''' 

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
            Message.print('error', f'*** ERROR {code_exception}: The record format in record {param2} of the file {param1} is wrong.')
        elif code_exception == 'F010':
            Message.print('error', f'*** ERROR {code_exception}: The {param1} data is wrong in the assembly identification {param2}.')
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

        # exit with RC 1
        sys.exit(1)

   #---------------

#-------------------------------------------------------------------------------

class NestedDefaultDict(collections.defaultdict):
    '''
    This class is used to create nested dictionaries.
    '''

    def __init__(self, *args, **kwargs):
        super(NestedDefaultDict, self).__init__(NestedDefaultDict, *args, **kwargs)

    def __repr__(self):
        return repr(dict(self))

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
