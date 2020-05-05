#!/bin/bash

#-------------------------------------------------------------------------------

# This software has been developed by:
#
#    GI Sistemas Naturales e Historia Forestal (formerly known as GI Genetica, Fisiologia e Historia Forestal)
#    Dpto. Sistemas y Recursos Naturales
#    ETSI Montes, Forestal y del Medio Natural
#    Universidad Politecnica de Madrid
#    https://github.com/ggfhf/
#
# Licence: GNU General Public Licence Version 3.

#-------------------------------------------------------------------------------

# This script executes a test of the program transcriptome-blastx.py in a Linux
# environment.

#-------------------------------------------------------------------------------

# Control parameters

if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

#-------------------------------------------------------------------------------

# Set run environment

BLASTPLUS_DIR=$APPS/Miniconda3/envs/blast/bin
NGSHELPER_DIR=$TRABAJO/ProyectosVScode/NGShelper

export PATH=$BLASTPLUS_DIR:$NGSHELPER_DIR:$PATH

# -- PROYECT_DIR=$TRABAJO/Pcan/results-02
PROYECT_DIR=$TRABAJO/Athaliana/results-01.0x-v01-00-test
# -- TRANSCRIPTOME_DIR=$PROYECT_DIR/trinity-170407-120957
TRANSCRIPTOME_DIR=$PROYECT_DIR/trinity-170101-235959
# -- TRANSCRIPTOME_FILE=Trinity.fasta
TRANSCRIPTOME_FILE=Trinity.fasta
BLASTDB=$TRABAJO/NCBI/RefSeq_Plant_Protein
PROTEIN_DATABASE_NAME=RefSeq_Plant_Protein
E_VALUE=1E-6
MAX_TARGET_SEQS=10
OUTPUT_DIR=$PROYECT_DIR/transcriptome-blastx-test

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Execute the program transcriptome-blastx.py

/usr/bin/time \
    ./transcriptome-blastx.py \
        --machine_type='local' \
        --node_number=1 \
        --blastx_thread_number=1 \
        --blast_db=$BLASTDB \
        --protein_database_name=$PROTEIN_DATABASE_NAME \
        --transcriptome=$TRANSCRIPTOME_DIR/$TRANSCRIPTOME_FILE \
        --e_value=$E_VALUE \
        --max_target_seqs=$MAX_TARGET_SEQS \
        --output=$OUTPUT_DIR \
        --verbose='y'
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
