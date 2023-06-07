#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program characterize-population.py 
# in a Linux environment.
#
# This software has been developed by:
#
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

SEP="#########################################"

NGSHELPER_DIR=$TRABAJO/ProyectosVScode/NGShelper
OUTPUT_DIR=$TRABAJO/ProyectosVScode/NGShelper/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Run the program characterize-population.py

DATA_DIR=$TRABAJO/SUBERINTRO-data
echo "$SEP"
echo "VCF: $DATA_DIR/test-SUBERINTRO-AL-samples-filtered2.vcf"
/usr/bin/time \
    ./characterize-population.py \
        --threads=1 \
        --db=$DATA_DIR/test-SUBERINTRO-AL-samples-filtered2.db \
        --vcf=$DATA_DIR/test-SUBERINTRO-AL-samples-filtered2.vcf \
        --verbose=N \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

DATA_DIR=$TRABAJO/SUBERINTRO-data
echo "$SEP"
echo "VCF: $DATA_DIR/test-SUBERINTRO-EN-samples-filtered2.vcf"
/usr/bin/time \
    ./characterize-population.py \
        --threads=1 \
        --db=$DATA_DIR/test-SUBERINTRO-EN-samples-filtered2.db \
        --vcf=$DATA_DIR/test-SUBERINTRO-EN-samples-filtered2.vcf \
        --verbose=N \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

DATA_DIR=$TRABAJO/SUBERINTRO-data
echo "$SEP"
echo "VCF: $DATA_DIR/test-SUBERINTRO-EFS-samples-filtered2.vcf"
/usr/bin/time \
    ./characterize-population.py \
        --threads=1 \
        --db=$DATA_DIR/test-SUBERINTRO-EFS-samples-filtered2.db \
        --vcf=$DATA_DIR/test-SUBERINTRO-EFS-samples-filtered2.vcf \
        --verbose=N \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

DATA_DIR=$TRABAJO/SUBERINTRO-data
echo "$SEP"
echo "VCF: $DATA_DIR/test-SUBERINTRO-A07-samples-filtered.vcf"
/usr/bin/time \
    ./characterize-population.py \
        --threads=1 \
        --db=$DATA_DIR/test-SUBERINTRO-A07-samples-filtered.db \
        --vcf=$DATA_DIR/test-SUBERINTRO-A07-samples-filtered.vcf \
        --verbose=N \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

DATA_DIR=$TRABAJO/SUBERINTRO-data
echo "$SEP"
echo "VCF: $DATA_DIR/test-SUBERINTRO-E96-samples-filtered.vcf"
/usr/bin/time \
    ./characterize-population.py \
        --threads=1 \
        --db=$DATA_DIR/test-SUBERINTRO-E96-samples-filtered.db \
        --vcf=$DATA_DIR/test-SUBERINTRO-E96-samples-filtered.vcf \
        --verbose=N \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

DATA_DIR=$TRABAJO/SUBERINTRO-data
echo "$SEP"
echo "VCF: $DATA_DIR/test-SUBERINTRO-FS20-samples-filtered.vcf"
/usr/bin/time \
    ./characterize-population.py \
        --threads=1 \
        --db=$DATA_DIR/test-SUBERINTRO-FS20-samples-filtered.db \
        --vcf=$DATA_DIR/test-SUBERINTRO-FS20-samples-filtered.vcf \
        --verbose=N \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

DATA_DIR=$TRABAJO/MOUSE-data
echo "$SEP"
echo "VCF: $DATA_DIR/reference.vcf"
/usr/bin/time \
    ./characterize-population.py \
        --threads=1 \
        --db=$DATA_DIR/reference.db \
        --vcf=$DATA_DIR/reference.vcf \
        --verbose=N \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

DATA_DIR=$TRABAJO/MOUSE-data
echo "$SEP"
echo "VCF: $DATA_DIR/reference-98inds.vcf"
/usr/bin/time \
    ./characterize-population.py \
        --threads=1 \
        --db=$DATA_DIR/reference-98inds.db \
        --vcf=$DATA_DIR/reference-98inds.vcf \
        --verbose=N \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

DATA_DIR=$TRABAJO/SUBERINTRO-data
echo "$SEP"
echo "VCF: $DATA_DIR/test-SUBERINTRO-AL-samples-filtered2-reducted.vcf"
/usr/bin/time \
    ./characterize-population.py \
        --threads=1 \
        --db=$DATA_DIR/test-SUBERINTRO-AL-samples-filtered2-reducted.db \
        --vcf=$DATA_DIR/test-SUBERINTRO-AL-samples-filtered2-reducted.vcf \
        --verbose=N \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

DATA_DIR=$TRABAJO/SUBERINTRO-data
echo "$SEP"
echo "VCF: $DATA_DIR/test-SUBERINTRO-ALandEN-samples-filtered2.vcf"
/usr/bin/time \
    ./characterize-population.py \
        --threads=1 \
        --db=$DATA_DIR/test-SUBERINTRO-ALandEN-2-filtered.db \
        --vcf=$DATA_DIR/test-SUBERINTRO-ALandEN-2-filtered.vcf \
        --verbose=N \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
