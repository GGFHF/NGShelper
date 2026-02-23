#!/bin/bash

#-------------------------------------------------------------------------------

# This script build the sequence database a Linux environment.
#
# This software has been developed by:
#
#    GI en Desarrollo de Especies y Comunidades Leñosas (WooSp)
#    Dpto. Sistemas y Recursos Naturales
#    ETSI Montes, Forestal y del Medio Natural
#    Universidad Politecnica de Madrid
#    https://github.com/ggfhf/
#
# Licence: GNU General Public Licence Version 3.

#-------------------------------------------------------------------------------

# Control parameters

if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

#-------------------------------------------------------------------------------

# Set environment

PYTHON=python3
PYTHON_OPTIONS=
PYTHONPATH=.

NGSHELPER_DIR=$NGSHELPER
DATA_DIR=/home/fmm/quercusTOA-app-databases/quercusTOA-db
OUTPUT_DIR=$NGSHELPER/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

INITIAL_DIR=$(pwd)
cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Run the program load-species-seqs.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS load-species-seqs.py \
        --db=$DATA_DIR/sequences.db \
        --server=NCBI \
        --species=Qlobata \
        --genome=$DATA_DIR/GCF_001633185.2_ValleyOak3.2_genomic.fna \
        --gff=$DATA_DIR/GCF_001633185.2_ValleyOak3.2_genomic.gff \
        --proteins=$DATA_DIR/GCF_001633185.2_ValleyOak3.2_protein.faa \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS load-species-seqs.py \
        --db=$DATA_DIR/sequences.db \
        --server=NCBI \
        --species=Qrobur \
        --genome=$DATA_DIR/GCF_932294415.1_dhQueRobu3.1_genomic.fna \
        --gff=$DATA_DIR/GCF_932294415.1_dhQueRobu3.1_genomic.gff \
        --proteins=$DATA_DIR/GCF_932294415.1_dhQueRobu3.1_protein.faa \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS load-species-seqs.py \
        --db=$DATA_DIR/sequences.db \
        --server=NCBI \
        --species=Qrubra \
        --genome=$DATA_DIR/GCA_035136125.1_Qrubra_687_v2.0_genomic.fna \
        --gff=$DATA_DIR/GCA_035136125.1_Qrubra_687_v2.0_genomic.gff \
        --proteins=$DATA_DIR/GCA_035136125.1_Qrubra_687_v2.0_protein.faa \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS load-species-seqs.py \
        --db=$DATA_DIR/sequences.db \
        --server=NCBI \
        --species=Qsuber \
        --genome=$DATA_DIR/GCF_002906115.3_Cork_oak_2.0_genomic.fna \
        --gff=$DATA_DIR/GCF_002906115.3_Cork_oak_2.0_genomic.gff \
        --proteins=$DATA_DIR/GCF_002906115.3_Cork_oak_2.0_protein.faa \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS load-species-seqs.py \
        --db=$DATA_DIR/sequences.db \
        --server=CNCB-NGDC \
        --species=Qacutissima \
        --genome=$DATA_DIR/GWHBGBO00000000.genome.fasta \
        --gff=$DATA_DIR/GWHBGBO00000000.gff \
        --proteins=$DATA_DIR/GWHBGBO00000000.Protein.faa \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS load-species-seqs.py \
        --db=$DATA_DIR/sequences.db \
        --server=CNCB-NGDC \
        --species=Qdentata \
        --genome=$DATA_DIR/GWHBRAD00000000.genome.fasta \
        --gff=$DATA_DIR/GWHBRAD00000000.gff \
        --proteins=$DATA_DIR/GWHBRAD00000000.Protein.faa \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS load-species-seqs.py \
        --db=$DATA_DIR/sequences.db \
        --server=CNCB-NGDC \
        --species=Qglauca \
        --genome=$DATA_DIR/GWHDTWU00000000.genome.fasta \
        --gff=$DATA_DIR/GWHDTWU00000000.gff \
        --proteins=$DATA_DIR/GWHDTWU00000000.Protein.faa \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS load-species-seqs.py \
        --db=$DATA_DIR/sequences.db \
        --server=CNCB-NGDC \
        --species=Qvariabilis \
        --genome=$DATA_DIR/GWHBQTN00000000.genome.fasta \
        --gff=$DATA_DIR/GWHBQTN00000000.gff \
        --proteins=$DATA_DIR/GWHBQTN00000000.Protein.faa \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
