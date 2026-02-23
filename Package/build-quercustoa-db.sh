#!/bin/bash

#-------------------------------------------------------------------------------

# This script build the quercusTOA database.
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

# WARNINGS:
#
# AWS machine type requerided: r5.8xlarge (vCPUs: 32 - Memory: 256 GiB).
#
# This script requires the software detailed below to be previously installed.
#
# Before running this Bash script:
#
#    * Check that the file "/ngscloud2/apps/InterProScan/interproscan.sh" has
#      the CPUs number and the initial and maximum sizes of the Java heap indicated
#      in the InterProScan installation.
#
#    * Activate the Miniforge3 environment typing:
#
#      $ /ngscloud2/apps/Miniforge3/condabin/conda init    (reset the console)

#-------------------------------------------------------------------------------

# SOFTWARE INSTALLATION:

# Miniforge3
# ==========

#    $ cd /ngscloud2/apps
#    $ wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
#    $ [rm -fr Miniforge3]
#    $ chmod u+x Miniforge3-Linux-x86_64.sh
#    $ ./Miniforge3-Linux-x86_64.sh -b -p Miniforge3
#    $ rm Miniforge3-Linux-x86_64.sh

#    $ Miniforge3/condabin/conda init bash    (reset the console)

#    $ conda config --add channels bioconda
#    $ conda config --add channels conda-forge
#    $ conda config --set channel_priority strict

#    $ export MAMBA_ROOT_PREFIX=/ngscloud2/apps/Miniforge3

#    $ mamba update --yes --name base --all

#    $ mamba install --yes --name base biopython
#    $ mamba install --yes --name base boto3
#    $ mamba install --yes --name base gffutils
#    $ mamba install --yes --name base joblib
#    $ mamba install --yes --name base matplotlib
#    $ mamba install --yes --name base minisom
#    $ mamba install --yes --name base numpy
#    $ mamba install --yes --name base openjdk
#    $ mamba install --yes --name base pandas
#    $ mamba install --yes --name base pandasql
#    $ mamba install --yes --name base paramiko
#    $ mamba install --yes --name base plotly
#    $ mamba install --yes --name base plotnine
#    $ mamba install --yes --name base psutil
#    $ mamba install --yes --name base requests
#    $ mamba install --yes --name base scikit-learn
#    $ mamba install --yes --name base scipy
#    $ mamba install --yes --name base sqlite
#    $ mamba install --yes --name base seaborn
#    $ mamba install --yes --name base sympy

# NGShelper
# =========

# Decompress the NGShelper package in the directory "/ngscloud2/apps/NGShelper".

#    $ cd /ngscloud2/apps/NGShelper
#    $ chmod u+x *.py *.sh

# BLAST+
# ======

#    $ [conda env remove --yes --name blast]
#    $ mamba create --yes --name blast blast

# BUSCO
# =====

#    $ [conda env remove --yes --name busco]
#    $ mamba create --yes --name busco busco

# DIAMOND
# =======

#    $ [conda env remove --yes --name diamond]
#    $ mamba create --yes --name diamond diamond

# eggNOG-mapper
# =============

#    $ [conda env remove --yes --name eggnog-mapper]
#    $ mamba create --yes --name eggnog-mapper eggnog-mapper

#    Check URLs in the file /ngscloud2/apps/Miniforge3/envs/eggnog-mapper/bin/download_eggnog_data.py: http://eggnog5.embl.de is OK

#    $ mkdir /ngscloud2/apps/Miniforge3/envs/eggnog-mapper/lib/python3.11/site-packages/data/ (depending on eggnog-mapper Python version)
#    $ conda activate eggnog-mapper
#    $ mamba install --yes setuptools
#    $ download_eggnog_data.py -f -y -P -M
#    $ conda deactivate

# EMBOSS
# ======

#    $ [conda env remove --yes --name emboss]
#    $ mamba create --yes --name emboss emboss

# Entrez Direct
# =============

#    $ [conda env remove --yes --name entrez-direct]
#    $ mamba create --yes --name entrez-direct entrez-direct

# Liftoff
# =======

#    $ [conda env remove --yes --name liftoff]
#    $ mamba create --yes --name liftoff liftoff

# MAFFT
# =======

#    $ [conda env remove --yes --name mafft]
#    $ mamba create --yes --name mafft mafft

# MMseqs2
# =======

#    $ [conda env remove --yes --name mmseqs2]
#    $ mamba create --yes --name mmseqs2 mmseqs2

# MUSCLE
# ======

#    $ [conda env remove --yes --name muscle]
#    $ mamba create --yes --name muscle muscle

# InterProScan
# ============
#
#    $ [OLD_VERSION=5.75-106.0]
#    $ NEW_VERSION=5.76-107.0
#    $ sudo apt install libgomp1 (if Ubuntu 20.04) 
#    $ cd /ngscloud2/apps
#    $ wget http://ftp.ebi.ac.uk/pub/software/unix/iprscan/5/$NEW_VERSION/interproscan-$NEW_VERSION-64-bit.tar.gz
#    $ [unlink InterProScan]
#    $ [rm -fr InterProScan-$OLD_VERSION]
#    $ tar -xzvf interproscan-$NEW_VERSION-64-bit.tar.gz
#    $ mv interproscan-$NEW_VERSION InterProScan-$NEW_VERSION
#    $ ln -s InterProScan-$NEW_VERSION InterProScan
#    $ cd InterProScan
#    $ ./setup.py -f interproscan.properties

#    Modify lines 58 and 59 of the file "interproscan.sh" in InterProScan directory:
#        (58): -XX:ParallelGCThreads=8   --->   -XX:ParallelGCThreads=32
#        (59): -Xms2028M -Xmx9216M       --->   -Xms64G -Xmx160G

#-------------------------------------------------------------------------------

SEP="#########################################"

CLADE=Quercus

MAFFT=mafft
MUSCLE=muscle
ALIGNER=$MAFFT

DIAMOND=diamond
MMSEQS=mmseqs
EMAPPER_SEARCH_OPTION=$DIAMOND

ENV_AWS='aws'
ENV_LOCAL='local'
ENVIRONMENT=$ENV_AWS

# NCBI genomic data source
NCBI_GENOMIC_FILES_SOURCE_1='NCBI-DATABASES'
NCBI_GENOMIC_FILES_SOURCE_2='REPOSITORY-FILES'
NCBI_GENOMIC_FILES_SOURCE=$NCBI_GENOMIC_FILES_SOURCE_2

# CNCB-NGDC genomic data source
NGDC_GENOMIC_FILES_SOURCE_1='NGDC-DATABASES'
NGDC_GENOMIC_FILES_SOURCE_2='REPOSITORY-FILES'
NGDC_GENOMIC_FILES_SOURCE=$NGDC_GENOMIC_FILES_SOURCE_2

if [ "$ENVIRONMENT" = "$ENV_AWS" ]; then

    source /ngscloud2/apps/Miniforge3/envs/mmseqs2/util/bash-completion.sh

    NGSHELPER_DIR=/ngscloud2/apps/NGShelper
    MMSEQS2_DIR=/ngscloud2/apps/Miniforge3/envs/mmseqs2/bin
    INTERPROSCAN_DIR=/ngscloud2/apps/InterProScan
    QUERCUS_REPOSITORY_DIR=/ngscloud2/Quercus-genomic-data
    OUTPUT_DIR=/ngscloud2/quercustoa

    PROTEIN_FASTA_FILE=$CLADE-proteins-sequences.fasta

    THREADS=32

elif [ "$ENVIRONMENT" = "$ENV_LOCAL" ]; then

    source $BIOCONDA/mmseqs2/util/bash-completion.sh

    NGSHELPER_DIR=$NGSHELPER
    MMSEQS2_DIR=$BIOCONDA/mmseqs2/bin
    INTERPROSCAN_DIR=$APPS/InterProScan
    QUERCUS_REPOSITORY_DIR=$QUERCUSTOA/data
    OUTPUT_DIR=$QUERCUSTOA/output

    PROTEIN_FASTA_FILE=$CLADE-proteins-sequences-1000seqs.fasta

    THREADS=4

else
    echo 'Environment error'; exit 3
fi

DB_NAME=quercusTOA-db
DB_DIR=$OUTPUT_DIR/$DB_NAME
SEQUENCES_DB_FILE=sequences.db
SEQUENCES_DB_PATH=$DB_DIR/$SEQUENCES_DB_FILE


# Functional annotations - Paths and files
FUNCTIONAL_ANNOTATIONS_TEMP_DIR=$OUTPUT_DIR/$DB_NAME/functional-annotations-temp
FUNCTIONAL_ANNOTATIONS_DB_FILE=functional-annotations.db
FUNCTIONAL_ANNOTATIONS_DB_PATH=$DB_DIR/$FUNCTIONAL_ANNOTATIONS_DB_FILE
PROTEIN_CLUSTER_DIR=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/protein-clusters
PROTEIN_FASTA_PATH=$DB_DIR/$PROTEIN_FASTA_FILE
ALLSEQS_FILE=$CLADE-mmseqs2_all_seqs.fasta
ALLSEQS_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$ALLSEQS_FILE
CLUSTER_FILE=$CLADE-clusters.csv
CLUSTER_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$CLUSTER_FILE
IDENTITIES_FILE=$CLADE-identities.csv
IDENTITIES_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$IDENTITIES_FILE
CONSEQS_PREFIX=$CLADE-consensus
CONSEQS_FILE=$CONSEQS_PREFIX-seqs.fasta
CONSEQS_PATH=$DB_DIR/$CONSEQS_FILE
CONSEQS_BLAST_DB_NAME=$CONSEQS_PREFIX-blastplus-db
CONSEQS_BLAST_DB_DIR=$DB_DIR/$CONSEQS_PREFIX-blastplus-db
CONSEQS_BLAST_DB_PATH=$CONSEQS_BLAST_DB_DIR/$CONSEQS_BLAST_DB_NAME
CONSEQS_DIAMOND_DB_NAME=$CONSEQS_PREFIX-diamond-db
CONSEQS_DIAMOND_DB_DIR=$DB_DIR/$CONSEQS_PREFIX-diamond-db
CONSEQS_DIAMOND_DB_PATH=$CONSEQS_DIAMOND_DB_DIR/$CONSEQS_DIAMOND_DB_NAME
INTERPRO_OUPUT=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$CONSEQS_PREFIX-seqs.fasta.tsv
INTERPRO_ANNOTATIONS_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$CONSEQS_PREFIX-annotations-interpro.tsv
EMAPPER_OUPUT=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$CONSEQS_PREFIX.emapper.annotations
EMAPPER_ANNOTATIONS_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$CONSEQS_PREFIX-annotations-emapper.tsv
ANNOTATIONS_FILE=$CONSEQS_PREFIX-seqs-annotations.csv
STATS_FILE=$DB_NAME-stats.ini
STATS_PATH=$DB_DIR/$STATS_FILE
NOANNOT_FILE=seqs-without-annotations.csv
# -- NOANNOT_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$NOANNOT_FILE
NOANNOT_PATH=NONE

# Comparative genomics - Paths and files
COMPARATIVE_GENOMICS_TEMP_DIR=$OUTPUT_DIR/$DB_NAME/comparative-genomics-temp
COMPARATIVE_GENOMICS_DB_FILE=comparative-genomics.db
COMPARATIVE_GENOMICS_DB_PATH=$DB_DIR/$COMPARATIVE_GENOMICS_DB_FILE
CLUSTERED_GENOME_FEATURES_DIR=$COMPARATIVE_GENOMICS_TEMP_DIR/clustered-genome-features
CLEANED_GENOME_RELATIONSHIPS_DIR=$COMPARATIVE_GENOMICS_TEMP_DIR/cleaned-genome-relationships
MAP_GENE_PATH=$CLEANED_GENOME_RELATIONSHIPS/Quercus-common-mapped-genes.csv
MAP_CODGENE_PATH=$CLEANED_GENOME_RELATIONSHIPS_DIR/Quercus-common-mapped-protein-coding-genes.csv
MAP_PROT_PATH=$CLEANED_GENOME_RELATIONSHIPS_DIR/Quercus-common-mapped-proteins.csv
HOMOLOGY_RELATIONSHIPS_DIR=$COMPARATIVE_GENOMICS_TEMP_DIR/homology-relationships

# Species identifications
QACUTISSIMA=Qacutissima
QDENTATA=Qdentata
QGILVA=Qgilva
QLOBATA=Qlobata
QLONGISPICA=Qlongispica
QROBUR=Qrobur
QRUBRA=Qrubra
QSUBER=Qsuber
QVARIABILIS=Qvariabilis
REFERENCE_SPECIES_LIST=($QACUTISSIMA $QDENTATA $QGILVA $QLOBATA $QLONGISPICA $QROBUR $QRUBRA $QSUBER $QVARIABILIS)
REFERENCE_SPECIES_LIST_TXT=Qacutissima,Qdentata,Qgilva,Qlobata,Qlongispica,Qrobur,Qrubra,Qsuber,Qvariabilis
TARGET_SPECIES_LIST=($QACUTISSIMA $QDENTATA $QGILVA $QLOBATA $QLONGISPICA $QROBUR $QRUBRA $QSUBER $QVARIABILIS)
TARGET_SPECIES_LIST_TXT=Qacutissima,Qdentata,Qgilva,Qlobata,Qlongispica,Qrobur,Qrubra,Qsuber,Qvariabilis

# NCBI Genome
# Quercus lobata
GENOME_QUERCUS_LOBATA_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/001/633/185/GCF_001633185.2_ValleyOak3.2/GCF_001633185.2_ValleyOak3.2_genomic.fna.gz
GENOME_QUERCUS_LOBATA_GENOME_FILE_GZ=$(basename "$GENOME_QUERCUS_LOBATA_GENOME_URL")
GENOME_QUERCUS_LOBATA_GFF_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/001/633/185/GCF_001633185.2_ValleyOak3.2/GCF_001633185.2_ValleyOak3.2_genomic.gff.gz
GENOME_QUERCUS_LOBATA_GFF_FILE_GZ=$(basename "$GENOME_QUERCUS_LOBATA_GFF_URL")
GENOME_QUERCUS_LOBATA_PROTEIN_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/001/633/185/GCF_001633185.2_ValleyOak3.2/GCF_001633185.2_ValleyOak3.2_protein.faa.gz
GENOME_QUERCUS_LOBATA_PROTEIN_FILE_GZ=$(basename "$GENOME_QUERCUS_LOBATA_PROTEIN_URL")
# Quercus robur
GENOME_QUERCUS_ROBUR_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/932/294/415/GCF_932294415.1_dhQueRobu3.1/GCF_932294415.1_dhQueRobu3.1_genomic.fna.gz
GENOME_QUERCUS_ROBUR_GENOME_FILE_GZ=$(basename "$GENOME_QUERCUS_ROBUR_GENOME_URL")
GENOME_QUERCUS_ROBUR_GFF_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/932/294/415/GCF_932294415.1_dhQueRobu3.1/GCF_932294415.1_dhQueRobu3.1_genomic.gff.gz
GENOME_QUERCUS_ROBUR_GFF_FILE_GZ=$(basename "$GENOME_QUERCUS_ROBUR_GFF_URL")
GENOME_QUERCUS_ROBUR_PROTEIN_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/932/294/415/GCF_932294415.1_dhQueRobu3.1/GCF_932294415.1_dhQueRobu3.1_protein.faa.gz
GENOME_QUERCUS_ROBUR_PROTEIN_FILE_GZ=$(basename "$GENOME_QUERCUS_ROBUR_PROTEIN_URL")
# Quercus rubra
GENOME_QUERCUS_RUBRA_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/035/136/125/GCA_035136125.1_Qrubra_687_v2.0/GCA_035136125.1_Qrubra_687_v2.0_genomic.fna.gz
GENOME_QUERCUS_RUBRA_GENOME_FILE_GZ=$(basename "$GENOME_QUERCUS_RUBRA_GENOME_URL")
GENOME_QUERCUS_RUBRA_GFF_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/035/136/125/GCA_035136125.1_Qrubra_687_v2.0/GCA_035136125.1_Qrubra_687_v2.0_genomic.gff.gz
GENOME_QUERCUS_RUBRA_GFF_FILE_GZ=$(basename "$GENOME_QUERCUS_RUBRA_GFF_URL")
GENOME_QUERCUS_RUBRA_PROTEIN_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/035/136/125/GCA_035136125.1_Qrubra_687_v2.0/GCA_035136125.1_Qrubra_687_v2.0_protein.faa.gz
GENOME_QUERCUS_RUBRA_PROTEIN_FILE_GZ=$(basename "$GENOME_QUERCUS_RUBRA_PROTEIN_URL")
# Quercus suber
GENOME_QUERCUS_SUBER_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/906/115/GCF_002906115.3_Cork_oak_2.0/GCF_002906115.3_Cork_oak_2.0_genomic.fna.gz
GENOME_QUERCUS_SUBER_GENOME_FILE_GZ=$(basename "$GENOME_QUERCUS_SUBER_GENOME_URL")
GENOME_QUERCUS_SUBER_GFF_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/906/115/GCF_002906115.3_Cork_oak_2.0/GCF_002906115.3_Cork_oak_2.0_genomic.gff.gz
GENOME_QUERCUS_SUBER_GFF_FILE_GZ=$(basename "$GENOME_QUERCUS_SUBER_GFF_URL")
GENOME_QUERCUS_SUBER_PROTEIN_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/906/115/GCF_002906115.3_Cork_oak_2.0/GCF_002906115.3_Cork_oak_2.0_protein.faa.gz
GENOME_QUERCUS_SUBER_PROTEIN_FILE_GZ=$(basename "$GENOME_QUERCUS_SUBER_PROTEIN_URL")

# CNCB - NGDC
# Quercus acutissima
NGDC_QUERCUS_ACUTISSIMA_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_acutissima_Quercus_a_v1.0_GWHBGBO00000000/GWHBGBO00000000.genome.fasta.gz
NGDC_QUERCUS_ACUTISSIMA_GENOME_FILE_GZ=$(basename "$NGDC_QUERCUS_ACUTISSIMA_GENOME_URL")
NGDC_QUERCUS_ACUTISSIMA_GFF_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_acutissima_Quercus_a_v1.0_GWHBGBO00000000/GWHBGBO00000000.gff.gz
NGDC_QUERCUS_ACUTISSIMA_GFF_FILE_GZ=$(basename "$NGDC_QUERCUS_ACUTISSIMA_GFF_URL")
NGDC_QUERCUS_ACUTISSIMA_PROTEIN_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_acutissima_Quercus_a_v1.0_GWHBGBO00000000/GWHBGBO00000000.Protein.faa.gz
NGDC_QUERCUS_ACUTISSIMA_PROTEIN_FILE_GZ=$(basename "$NGDC_QUERCUS_ACUTISSIMA_PROTEIN_URL")
# Quercus dentata
NGDC_QUERCUS_DENTATA_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_dentata_NA_GWHBRAD00000000/GWHBRAD00000000.genome.fasta.gz
NGDC_QUERCUS_DENTATA_GENOME_FILE_GZ=$(basename "$NGDC_QUERCUS_DENTATA_GENOME_URL")
NGDC_QUERCUS_DENTATA_GFF_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_dentata_NA_GWHBRAD00000000/GWHBRAD00000000.gff.gz
NGDC_QUERCUS_DENTATA_GFF_FILE_GZ=$(basename "$NGDC_QUERCUS_DENTATA_GFF_URL")
NGDC_QUERCUS_DENTATA_PROTEIN_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_dentata_NA_GWHBRAD00000000/GWHBRAD00000000.Protein.faa.gz
NGDC_QUERCUS_DENTATA_PROTEIN_FILE_GZ=$(basename "$NGDC_QUERCUS_DENTATA_PROTEIN_URL")
# Quercus gilva
NGDC_QUERCUS_GILVA_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_gilva_Quercus_gilva_V1_GWHDOCW00000000/GWHDOCW00000000.genome.fasta.gz
NGDC_QUERCUS_GILVA_GENOME_FILE_GZ=$(basename "$NGDC_QUERCUS_GILVA_GENOME_URL")
NGDC_QUERCUS_GILVA_GFF_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_gilva_Quercus_gilva_V1_GWHDOCW00000000/GWHDOCW00000000.gff.gz
NGDC_QUERCUS_GILVA_GFF_FILE_GZ=$(basename "$NGDC_QUERCUS_GILVA_GFF_URL")
NGDC_QUERCUS_GILVA_PROTEIN_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_gilva_Quercus_gilva_V1_GWHDOCW00000000/GWHDOCW00000000.Protein.faa.gz
NGDC_QUERCUS_GILVA_PROTEIN_FILE_GZ=$(basename "$NGDC_QUERCUS_GILVA_PROTEIN_URL")
# Quercus longispica
NGDC_QUERCUS_LONGISPICA_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_longispica_LKM1_GWHESEV00000000/GWHESEV00000000.genome.fasta.gz
NGDC_QUERCUS_LONGISPICA_GENOME_FILE_GZ=$(basename "$NGDC_QUERCUS_LONGISPICA_GENOME_URL")
NGDC_QUERCUS_LONGISPICA_GFF_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_longispica_LKM1_GWHESEV00000000/GWHESEV00000000.gff.gz
NGDC_QUERCUS_LONGISPICA_GFF_FILE_GZ=$(basename "$NGDC_QUERCUS_LONGISPICA_GFF_URL")
NGDC_QUERCUS_LONGISPICA_PROTEIN_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_longispica_LKM1_GWHESEV00000000/GWHESEV00000000.Protein.faa.gz
NGDC_QUERCUS_LONGISPICA_PROTEIN_FILE_GZ=$(basename "$NGDC_QUERCUS_LONGISPICA_PROTEIN_URL")
# Quercus variabilis
NGDC_QUERCUS_VARIABILIS_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_variabilis_Qv_SD_1.0_GWHEQCV00000000/GWHEQCV00000000.genome.fasta.gz
NGDC_QUERCUS_VARIABILIS_GENOME_FILE_GZ=$(basename "$NGDC_QUERCUS_VARIABILIS_GENOME_URL")
NGDC_QUERCUS_VARIABILIS_GFF_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_variabilis_Qv_SD_1.0_GWHEQCV00000000/GWHEQCV00000000.gff.gz
NGDC_QUERCUS_VARIABILIS_GFF_FILE_GZ=$(basename "$NGDC_QUERCUS_VARIABILIS_GFF_URL")
NGDC_QUERCUS_VARIABILIS_PROTEIN_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_variabilis_Qv_SD_1.0_GWHEQCV00000000/GWHEQCV00000000.Protein.faa.gz
NGDC_QUERCUS_VARIABILIS_PROTEIN_FILE_GZ=$(basename "$NGDC_QUERCUS_VARIABILIS_PROTEIN_URL")

# Reference genome, GFF and proteins files in the AWS/local repository of Quercus genomica data
# Quercus acutissima
REPOSITORY_QUERCUS_ACUTISSIMA_GENOME_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_ACUTISSIMA_GENOME_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_ACUTISSIMA_GFF_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_ACUTISSIMA_GFF_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_ACUTISSIMA_PROTEIN_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_ACUTISSIMA_PROTEIN_FILE_GZ%.gz}"
# Quercus dentata
REPOSITORY_QUERCUS_DENTATA_GENOME_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_DENTATA_GENOME_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_DENTATA_GFF_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_DENTATA_GFF_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_DENTATA_PROTEIN_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_DENTATA_PROTEIN_FILE_GZ%.gz}"
# Quercus gilva
REPOSITORY_QUERCUS_GILVA_GENOME_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_GILVA_GENOME_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_GILVA_GFF_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_GILVA_GFF_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_GILVA_PROTEIN_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_GILVA_PROTEIN_FILE_GZ%.gz}"
# Quercus lobata
REPOSITORY_QUERCUS_LOBATA_GENOME_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_LOBATA_GENOME_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_LOBATA_GFF_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_LOBATA_GFF_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_LOBATA_PROTEIN_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_LOBATA_PROTEIN_FILE_GZ%.gz}"
# Quercus longispica
REPOSITORY_QUERCUS_LONGISPICA_GENOME_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_LONGISPICA_GENOME_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_LONGISPICA_GFF_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_LONGISPICA_GFF_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_LONGISPICA_PROTEIN_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_LONGISPICA_PROTEIN_FILE_GZ%.gz}"
# Quercus robur
REPOSITORY_QUERCUS_ROBUR_GENOME_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_ROBUR_GENOME_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_ROBUR_GFF_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_ROBUR_GFF_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_ROBUR_PROTEIN_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_ROBUR_PROTEIN_FILE_GZ%.gz}"
# Quercus rubra
REPOSITORY_QUERCUS_RUBRA_GENOME_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_RUBRA_GENOME_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_RUBRA_GFF_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_RUBRA_GFF_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_RUBRA_PROTEIN_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_RUBRA_PROTEIN_FILE_GZ%.gz}"
# Quercus suber
REPOSITORY_QUERCUS_SUBER_GENOME_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_SUBER_GENOME_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_SUBER_GFF_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_SUBER_GFF_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_SUBER_PROTEIN_PATH=$QUERCUS_REPOSITORY_DIR/"${GENOME_QUERCUS_SUBER_PROTEIN_FILE_GZ%.gz}"
# Quercus variabilis
REPOSITORY_QUERCUS_VARIABILIS_GENOME_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_VARIABILIS_GENOME_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_VARIABILIS_GFF_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_VARIABILIS_GFF_FILE_GZ%.gz}"
REPOSITORY_QUERCUS_VARIABILIS_PROTEIN_PATH=$QUERCUS_REPOSITORY_DIR/"${NGDC_QUERCUS_VARIABILIS_PROTEIN_FILE_GZ%.gz}"

# Reference genome, GFF and proteins files in quercusTOA-db directory
# Quercus acutissima
DBDIR_QUERCUS_ACUTISSIMA_GENOME_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_ACUTISSIMA_GENOME_FILE_GZ
DBDIR_QUERCUS_ACUTISSIMA_GENOME_PATH=$DB_DIR/"${NGDC_QUERCUS_ACUTISSIMA_GENOME_FILE_GZ%.gz}"
DBDIR_QUERCUS_ACUTISSIMA_GFF_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_ACUTISSIMA_GFF_FILE_GZ
DBDIR_QUERCUS_ACUTISSIMA_GFF_PATH=$DB_DIR/"${NGDC_QUERCUS_ACUTISSIMA_GFF_FILE_GZ%.gz}"
DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_ACUTISSIMA_PROTEIN_FILE_GZ
DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH=$DB_DIR/"${NGDC_QUERCUS_ACUTISSIMA_PROTEIN_FILE_GZ%.gz}"
DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH_WSPECIES="${DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH%.*}".wspecies."${DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH##*.}"
# Quercus dentata
DBDIR_QUERCUS_DENTATA_GENOME_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_DENTATA_GENOME_FILE_GZ
DBDIR_QUERCUS_DENTATA_GENOME_PATH=$DB_DIR/"${NGDC_QUERCUS_DENTATA_GENOME_FILE_GZ%.gz}"
DBDIR_QUERCUS_DENTATA_GFF_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_DENTATA_GFF_FILE_GZ
DBDIR_QUERCUS_DENTATA_GFF_PATH=$DB_DIR/"${NGDC_QUERCUS_DENTATA_GFF_FILE_GZ%.gz}"
DBDIR_QUERCUS_DENTATA_PROTEIN_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_DENTATA_PROTEIN_FILE_GZ
DBDIR_QUERCUS_DENTATA_PROTEIN_PATH=$DB_DIR/"${NGDC_QUERCUS_DENTATA_PROTEIN_FILE_GZ%.gz}"
DBDIR_QUERCUS_DENTATA_PROTEIN_PATH_WSPECIES="${DBDIR_QUERCUS_DENTATA_PROTEIN_PATH%.*}".wspecies."${DBDIR_QUERCUS_DENTATA_PROTEIN_PATH##*.}"
# Quercus gilva
DBDIR_QUERCUS_GILVA_GENOME_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_GILVA_GENOME_FILE_GZ
DBDIR_QUERCUS_GILVA_GENOME_PATH=$DB_DIR/"${NGDC_QUERCUS_GILVA_GENOME_FILE_GZ%.gz}"
DBDIR_QUERCUS_GILVA_GFF_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_GILVA_GFF_FILE_GZ
DBDIR_QUERCUS_GILVA_GFF_PATH=$DB_DIR/"${NGDC_QUERCUS_GILVA_GFF_FILE_GZ%.gz}"
DBDIR_QUERCUS_GILVA_PROTEIN_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_GILVA_PROTEIN_FILE_GZ
DBDIR_QUERCUS_GILVA_PROTEIN_PATH=$DB_DIR/"${NGDC_QUERCUS_GILVA_PROTEIN_FILE_GZ%.gz}"
DBDIR_QUERCUS_GILVA_PROTEIN_PATH_WSPECIES="${DBDIR_QUERCUS_GILVA_PROTEIN_PATH%.*}".wspecies."${DBDIR_QUERCUS_GILVA_PROTEIN_PATH##*.}"
# Quercus lobata
DBDIR_QUERCUS_LOBATA_GENOME_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_LOBATA_GENOME_FILE_GZ
DBDIR_QUERCUS_LOBATA_GENOME_PATH=$DB_DIR/"${GENOME_QUERCUS_LOBATA_GENOME_FILE_GZ%.gz}"
DBDIR_QUERCUS_LOBATA_GFF_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_LOBATA_GFF_FILE_GZ
DBDIR_QUERCUS_LOBATA_GFF_PATH=$DB_DIR/"${GENOME_QUERCUS_LOBATA_GFF_FILE_GZ%.gz}"
DBDIR_QUERCUS_LOBATA_PROTEIN_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_LOBATA_PROTEIN_FILE_GZ
DBDIR_QUERCUS_LOBATA_PROTEIN_PATH=$DB_DIR/"${GENOME_QUERCUS_LOBATA_PROTEIN_FILE_GZ%.gz}"
# Quercus longispica
DBDIR_QUERCUS_LONGISPICA_GENOME_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_LONGISPICA_GENOME_FILE_GZ
DBDIR_QUERCUS_LONGISPICA_GENOME_PATH=$DB_DIR/"${NGDC_QUERCUS_LONGISPICA_GENOME_FILE_GZ%.gz}"
DBDIR_QUERCUS_LONGISPICA_GFF_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_LONGISPICA_GFF_FILE_GZ
DBDIR_QUERCUS_LONGISPICA_GFF_PATH=$DB_DIR/"${NGDC_QUERCUS_LONGISPICA_GFF_FILE_GZ%.gz}"
DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_LONGISPICA_PROTEIN_FILE_GZ
DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH=$DB_DIR/"${NGDC_QUERCUS_LONGISPICA_PROTEIN_FILE_GZ%.gz}"
DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH_WSPECIES="${DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH%.*}".wspecies."${DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH##*.}"
# Quercus robur
DBDIR_QUERCUS_ROBUR_GENOME_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_ROBUR_GENOME_FILE_GZ
DBDIR_QUERCUS_ROBUR_GENOME_PATH=$DB_DIR/"${GENOME_QUERCUS_ROBUR_GENOME_FILE_GZ%.gz}"
DBDIR_QUERCUS_ROBUR_GFF_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_ROBUR_GFF_FILE_GZ
DBDIR_QUERCUS_ROBUR_GFF_PATH=$DB_DIR/"${GENOME_QUERCUS_ROBUR_GFF_FILE_GZ%.gz}"
DBDIR_QUERCUS_ROBUR_PROTEIN_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_ROBUR_PROTEIN_FILE_GZ
DBDIR_QUERCUS_ROBUR_PROTEIN_PATH=$DB_DIR/"${GENOME_QUERCUS_ROBUR_PROTEIN_FILE_GZ%.gz}"
# Quercus rubra
DBDIR_QUERCUS_RUBRA_GENOME_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_RUBRA_GENOME_FILE_GZ
DBDIR_QUERCUS_RUBRA_GENOME_PATH=$DB_DIR/"${GENOME_QUERCUS_RUBRA_GENOME_FILE_GZ%.gz}"
DBDIR_QUERCUS_RUBRA_GFF_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_RUBRA_GFF_FILE_GZ
DBDIR_QUERCUS_RUBRA_GFF_PATH=$DB_DIR/"${GENOME_QUERCUS_RUBRA_GFF_FILE_GZ%.gz}"
DBDIR_QUERCUS_RUBRA_PROTEIN_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_RUBRA_PROTEIN_FILE_GZ
DBDIR_QUERCUS_RUBRA_PROTEIN_PATH=$DB_DIR/"${GENOME_QUERCUS_RUBRA_PROTEIN_FILE_GZ%.gz}"
# Quercus suber
DBDIR_QUERCUS_SUBER_GENOME_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_SUBER_GENOME_FILE_GZ
DBDIR_QUERCUS_SUBER_GENOME_PATH=$DB_DIR/"${GENOME_QUERCUS_SUBER_GENOME_FILE_GZ%.gz}"
DBDIR_QUERCUS_SUBER_GFF_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_SUBER_GFF_FILE_GZ
DBDIR_QUERCUS_SUBER_GFF_PATH=$DB_DIR/"${GENOME_QUERCUS_SUBER_GFF_FILE_GZ%.gz}"
DBDIR_QUERCUS_SUBER_PROTEIN_PATH_GZ=$DB_DIR/$GENOME_QUERCUS_SUBER_PROTEIN_FILE_GZ
DBDIR_QUERCUS_SUBER_PROTEIN_PATH=$DB_DIR/"${GENOME_QUERCUS_SUBER_PROTEIN_FILE_GZ%.gz}"
# Quercus variabilis
DBDIR_QUERCUS_VARIABILIS_GENOME_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_VARIABILIS_GENOME_FILE_GZ
DBDIR_QUERCUS_VARIABILIS_GENOME_PATH=$DB_DIR/"${NGDC_QUERCUS_VARIABILIS_GENOME_FILE_GZ%.gz}"
DBDIR_QUERCUS_VARIABILIS_GFF_PATH_GZ=$DB_DIR/$NGDC_QUERCUS_VARIABILIS_GFF_FILE_GZ
DBDIR_QUERCUS_VARIABILIS_GFF_PATH=$DB_DIR/"${NGDC_QUERCUS_VARIABILIS_GFF_FILE_GZ%.gz}"
DBDIR_QUERCUS_VARIABILIS_PROTEIN_GZ_PATH=$DB_DIR/$NGDC_QUERCUS_VARIABILIS_PROTEIN_FILE_GZ
DBDIR_QUERCUS_VARIABILIS_PROTEIN_PATH=$DB_DIR/"${NGDC_QUERCUS_VARIABILIS_PROTEIN_FILE_GZ%.gz}"
DBDIR_QUERCUS_VARIABILIS_PROTEIN_PATH_WSPECIES="${DBDIR_QUERCUS_VARIABILIS_PROTEIN_PATH%.*}".wspecies."${DBDIR_QUERCUS_VARIABILIS_PROTEIN_PATH##*.}"

# Reference genome
REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_LOBATA_GENOME_PATH
REFERENCE_GFF_URL=$DBDIR_QUERCUS_LOBATA_GFF_URL
REFERENCE_GFF_PATH=$DBDIR_QUERCUS_LOBATA_GFF_PATH

# NCBI Taxonomy
TAXONOMY_TAXDMP_URL=ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip
TAXONOMY_TAXDMP_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/taxdmp.zip
TAXONOMY_TAXONNAMES_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/names.dmp

# BUSCO Embryophyta dataset
BUSCO_DATASET=embryophyta_odb10
BUSCO_DATASET_URL=https://busco-data.ezlab.org/v5/data/lineages/embryophyta_odb10.2024-01-08.tar.gz
BUSCO_DATASET_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$BUSCO_DATASET.tar.gz
BUSCO_DATASET_DIR=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$BUSCO_DATASET
BUSCO_ASSESSMENT_PATTERN=busco-assessment
BUSCO_ASSESSMENT_FILE=short_summary.specific.$BUSCO_DATASET.$BUSCO_ASSESSMENT_PATTERN.txt
BUSCO_ASSESSMENT_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$BUSCO_ASSESSMENT_PATTERN/$BUSCO_ASSESSMENT_FILE
BUSCO_ASSESSMENT_DATA_PATH=$DB_DIR/$BUSCO_ASSESSMENT_PATTERN.txt

# TAIR10
TAIR10_PREFIX=tair10
# -- TAIR10_PEP_URL=https://www.arabidopsis.org/download_files/Proteins/TAIR10_protein_lists/TAIR10_pep_20101214
TAIR10_PEP_URL=https://www.arabidopsis.org/api/download-files/download?filePath=Proteins/TAIR10_protein_lists/TAIR10_pep_20101214
TAIR10_PEP_FILE=$TAIR10_PREFIX-peptides.fasta
TAIR10_PEP_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$TAIR10_PEP_FILE
TAIR10_BLAST_DB_NAME=$TAIR10_PREFIX-blastplus-db
TAIR10_BLAST_DB_DIR=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$TAIR10_PREFIX-blastplus-db
TAIR10_BLAST_DB_PATH=$TAIR10_BLAST_DB_DIR/$TAIR10_BLAST_DB_NAME
TAIR10_CONSEQS_ALIGNMENT_FILE=$CONSEQS_PREFIX-tair10-alignments.csv
TAIR10_CONSEQS_ALIGNMENT_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$TAIR10_CONSEQS_ALIGNMENT_FILE

# Gene Ontology
GO_ONTOLOGY_URL=http://purl.obolibrary.org/obo/go.obo
GO_ONTOLOGY_FILE=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/go.obo

# CANTATA data
CANTATA_ARABIDOPSIS_THALIANA_FASTA_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Arabidopsis_thaliana_lncRNAs.fasta
CANTATA_ARABIDOPSIS_THALIANA_FASTA_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/Arabidopsis-thaliana-lncrnas.fasta
CANTATA_ARABIDOPSIS_THALIANA_GTF_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Arabidopsis_thaliana_lncRNAs.gtf
CANTATA_ARABIDOPSIS_THALIANA_GTF_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/Arabidopsis-thaliana-lncrnas.gtf
CANTATA_QUERCUS_LOBATA_FASTA_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Quercus_lobata_lncRNAs.fasta
CANTATA_QUERCUS_LOBATA_FASTA_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/Quercus-lobata-lncrnas.fasta
CANTATA_QUERCUS_LOBATA_GTF_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Quercus_lobata_lncRNAs.gtf
CANTATA_QUERCUS_LOBATA_GTF_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/Quercus-lobata-lncrnas.gtf
CANTATA_QUERCUS_SUBER_FASTA_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Quercus_suber_lncRNAs.fasta
CANTATA_QUERCUS_SUBER_FASTA_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/Quercus-suber-lncrnas.fasta
CANTATA_QUERCUS_SUBER_GTF_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Quercus_suber_lncRNAs.gtf
CANTATA_QUERCUS_SUBER_GTF_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/Quercus-suber-lncrnas.gtf
LNCRNAS_PREFIX=lncRNA
LNCRNAS_FILE=$LNCRNAS_PREFIX-seqs.fasta
LNCRNAS_PATH=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$LNCRNAS_FILE
LNCRNAS_BLAST_DB_NAME=$LNCRNAS_PREFIX-blastplus-db
LNCRNAS_BLAST_DB_DIR=$DB_DIR/$LNCRNAS_PREFIX-blastplus-db
LNCRNAS_BLAST_DB_PATH=$LNCRNAS_BLAST_DB_DIR/$LNCRNAS_BLAST_DB_NAME

# MMseqs2 params
S=4.0        # s (sensitivity): 1.0 (faster), 4.0 (fast), 7.5 (sensitive) [5.700]
MASK=1       # mask (mask sequences in prefilter stage with tantan): 0 (w/o low complexity masking), 1 (with low complexity masking) [1]
# -- MSI=1.000    # min-seq-id (sequence identity threshold for clustering) [0.000]
MSI=0.900    # min-seq-id (sequence identity threshold for clustering) [0.000]
# -- C=1.0        # c (list matches above this fraction of aligned -covered- residue) [0.000]
C=0.9        # c (list matches above this fraction of aligned -covered- residue) [0.000]
CM=0         # cov-mode (coverage mode): 0 (coverage of query and target), 1 (coverage of target), 2 (coverage of query), ... [0]
ST=2         # similarity-type (score used for clustering): 1 (alignment score), 2 (sequence identity) [2]
TYPE=0       # dbtype: 0 (auto), 1 (amino acids), 2 (nucleotides) [0]

# InterProScan params
FASTA_TYPE=p
# -- INTERPROSCAN_ANALYSIS=AntiFam,CDD,Coils,Gene3D,Hamap,MobiDBLite,NCBIfam,PANTHER,Pfam,PIRSF,PIRSR,PRINTS,ProSitePatterns,ProSiteProfiles,SFLD,SMART,SUPERFAMILY,TIGRFAM,Phobius,TMHMM
INTERPROSCAN_ANALYSIS=AntiFam,CDD,Coils,Gene3D,Hamap,MobiDBLite,NCBIfam,PANTHER,Pfam,PIRSF,PIRSR,PRINTS,ProSitePatterns,ProSiteProfiles,SFLD,SMART,SUPERFAMILY,TIGRFAM
# -- INTERPROSCAN_FORMATS=TSV,XML,JSON,GFF3
INTERPROSCAN_FORMATS=TSV

# eggNOG-mapper params
EMAPPER_ITYPE=proteins
EMAPPER_DMND_ALGO=auto
EMAPPER_SENSMODE=sensitive
EMAPPER_DMND_ITERATE=yes
EMAPPER_START_SENS=3
EMAPPER_SENS_STEPS=3
EMAPPER_FINAL_SENS=7
# -- EMAPPER_PIDENT=30.0
EMAPPER_EVALUE=0.00001
# -- EMAPPER_QUERY_COVER=30.0

PATH=$NGSHELPER_DIR:$MMSEQS2_DIR:$INTERPROSCAN_DIR:$PATH

#-------------------------------------------------------------------------------

if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

#-------------------------------------------------------------------------------

function init
{

    INIT_DATETIME=`date +%s`
    FORMATTED_INIT_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    echo "$SEP"
    echo "Script started at $FORMATTED_INIT_DATETIME."

}

#-------------------------------------------------------------------------------

function create_directories
{

    echo "$SEP"
    echo 'Creating directories ...'
    if [ -d "$DB_DIR" ]; then rm -rf $DB_DIR; fi; mkdir --parents $DB_DIR 
    if [ -d "$FUNCTIONAL_ANNOTATIONS_TEMP_DIR" ]; then rm -rf $FUNCTIONAL_ANNOTATIONS_TEMP_DIR; fi; mkdir --parents $FUNCTIONAL_ANNOTATIONS_TEMP_DIR 
    if [ -d "$PROTEIN_CLUSTER_DIR" ]; then rm -rf $PROTEIN_CLUSTER_DIR; fi; mkdir --parents $PROTEIN_CLUSTER_DIR
    if [ -d "$CONSEQS_BLAST_DB_DIR" ]; then rm -rf $CONSEQS_BLAST_DB_DIR; fi; mkdir --parents $CONSEQS_BLAST_DB_DIR
    if [ -d "$CONSEQS_DIAMOND_DB_DIR" ]; then rm -rf $CONSEQS_DIAMOND_DB_DIR; fi; mkdir --parents $CONSEQS_DIAMOND_DB_DIR
    if [ -d "$LNCRNAS_BLAST_DB_DIR" ]; then rm -rf $LNCRNAS_BLAST_DB_DIR; fi; mkdir --parents $LNCRNAS_BLAST_DB_DIR
    if [ -d "$COMPARATIVE_GENOMICS_TEMP_DIR" ]; then rm -rf $COMPARATIVE_GENOMICS_TEMP_DIR; fi; mkdir --parents $COMPARATIVE_GENOMICS_TEMP_DIR
    if [ -d "$CLUSTERED_GENOME_FEATURES_DIR" ]; then rm -rf $CLUSTERED_GENOME_FEATURES_DIR; fi; mkdir --parents $CLUSTERED_GENOME_FEATURES_DIR
    if [ -d "$CLEANED_GENOME_RELATIONSHIPS_DIR" ]; then rm -rf $CLEANED_GENOME_RELATIONSHIPS_DIR; fi; mkdir --parents $CLEANED_GENOME_RELATIONSHIPS_DIR
    if [ -d "$HOMOLOGY_RELATIONSHIPS_DIR" ]; then rm -rf $HOMOLOGY_RELATIONSHIPS_DIR; fi; mkdir --parents $HOMOLOGY_RELATIONSHIPS_DIR
    echo 'Directories are created.'

}

#-------------------------------------------------------------------------------

function create_databases
{

    echo "$SEP"
    echo 'Creating the sequences database ...'
    /usr/bin/time \
        recreate-database.py \
            --db=$SEQUENCES_DB_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error recreate-database.py $RC; fi
    echo 'Database is created.'

    echo "$SEP"
    echo 'Creating the functional annotations database ...'
    /usr/bin/time \
        recreate-database.py \
            --db=$FUNCTIONAL_ANNOTATIONS_DB_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error recreate-database.py $RC; fi
    echo 'Database is created.'

    echo "$SEP"
    echo 'Creating the comparative genomics database ...'
    /usr/bin/time \
        recreate-database.py \
            --db=$COMPARATIVE_GENOMICS_DB_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error recreate-database.py $RC; fi
    echo 'Database is created.'

}

#-------------------------------------------------------------------------------

function download_genome_sequences
{

    if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus lobata genome FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_LOBATA_GENOME_PATH_GZ \
                $GENOME_QUERCUS_LOBATA_GENOME_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_LOBATA_GENOME_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus lobata genome FASTA to database dir ...'
        cp $REPOSITORY_QUERCUS_LOBATA_GENOME_PATH $DBDIR_QUERCUS_LOBATA_GENOME_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus lobata genome GFF3 ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_LOBATA_GFF_PATH_GZ \
                $GENOME_QUERCUS_LOBATA_GFF_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_LOBATA_GFF_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus lobata genome GFF3 to database dir ...'
        cp $REPOSITORY_QUERCUS_LOBATA_GFF_PATH $DBDIR_QUERCUS_LOBATA_GFF_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus robur genome FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_ROBUR_GENOME_PATH_GZ \
                $GENOME_QUERCUS_ROBUR_GENOME_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_ROBUR_GENOME_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus robur genome FASTA to database dir ...'
        cp $REPOSITORY_QUERCUS_ROBUR_GENOME_PATH $DBDIR_QUERCUS_ROBUR_GENOME_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus robur genome GFF3 ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_ROBUR_GFF_PATH_GZ \
                $GENOME_QUERCUS_ROBUR_GFF_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_ROBUR_GFF_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus robur genome GFF3 to database dir ...'
        cp $REPOSITORY_QUERCUS_ROBUR_GFF_PATH $DBDIR_QUERCUS_ROBUR_GFF_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus rubra genome FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_RUBRA_GENOME_PATH_GZ \
                $GENOME_QUERCUS_RUBRA_GENOME_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_RUBRA_GENOME_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus rubra genome FASTA to database dir ...'
        cp $REPOSITORY_QUERCUS_RUBRA_GENOME_PATH $DBDIR_QUERCUS_RUBRA_GENOME_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus rubra genome GFF3 ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_RUBRA_GFF_PATH_GZ \
                $GENOME_QUERCUS_RUBRA_GFF_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_RUBRA_GFF_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus rubra genome GFF3 to database dir ...'
        cp $REPOSITORY_QUERCUS_RUBRA_GFF_PATH $DBDIR_QUERCUS_RUBRA_GFF_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus suber genome FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_SUBER_GENOME_PATH_GZ \
                $GENOME_QUERCUS_SUBER_GENOME_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_SUBER_GENOME_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus suber genome FASTA to database dir ...'
        cp $REPOSITORY_QUERCUS_SUBER_GENOME_PATH $DBDIR_QUERCUS_SUBER_GENOME_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus suber genome GFF3 ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_SUBER_GFF_PATH_GZ \
                $GENOME_QUERCUS_SUBER_GFF_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_SUBER_GFF_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus suber genome GFF3 to database dir ...'
        cp $REPOSITORY_QUERCUS_SUBER_GFF_PATH $DBDIR_QUERCUS_SUBER_GFF_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus acutissima genome FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_ACUTISSIMA_GENOME_PATH_GZ \
                $NGDC_QUERCUS_ACUTISSIMA_GENOME_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_ACUTISSIMA_GENOME_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus acutissima genome FASTA to database dir ...'
        cp $REPOSITORY_QUERCUS_ACUTISSIMA_GENOME_PATH $DBDIR_QUERCUS_ACUTISSIMA_GENOME_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus acutissima genome GFF3 ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_ACUTISSIMA_GFF_PATH_GZ \
                $NGDC_QUERCUS_ACUTISSIMA_GFF_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_ACUTISSIMA_GFF_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus acutissima genome GFF3 to database dir ...'
        cp $REPOSITORY_QUERCUS_ACUTISSIMA_GFF_PATH $DBDIR_QUERCUS_ACUTISSIMA_GFF_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus dentata genome FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_DENTATA_GENOME_PATH_GZ \
                $NGDC_QUERCUS_DENTATA_GENOME_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_DENTATA_GENOME_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus dentata genome FASTA to database dir ...'
        cp $REPOSITORY_QUERCUS_DENTATA_GENOME_PATH $DBDIR_QUERCUS_DENTATA_GENOME_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus dentata genome GFF3 ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_DENTATA_GFF_PATH_GZ \
                $NGDC_QUERCUS_DENTATA_GFF_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_DENTATA_GFF_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus dentata genome GFF3 to database dir ...'
        cp $REPOSITORY_QUERCUS_DENTATA_GFF_PATH $DBDIR_QUERCUS_DENTATA_GFF_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus gilva genome FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_GILVA_GENOME_PATH_GZ \
                $NGDC_QUERCUS_GILVA_GENOME_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_GILVA_GENOME_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus gilva genome FASTA to database dir ...'
        cp $REPOSITORY_QUERCUS_GILVA_GENOME_PATH $DBDIR_QUERCUS_GILVA_GENOME_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus gilva genome GFF3 ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_GILVA_GFF_PATH_GZ \
                $NGDC_QUERCUS_GILVA_GFF_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_GILVA_GFF_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus gilva genome GFF3 to database dir ...'
        cp $REPOSITORY_QUERCUS_GILVA_GFF_PATH $DBDIR_QUERCUS_GILVA_GFF_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus longispica genome FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_LONGISPICA_GENOME_PATH_GZ \
                $NGDC_QUERCUS_LONGISPICA_GENOME_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_LONGISPICA_GENOME_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus longispica genome FASTA to database dir ...'
        cp $REPOSITORY_QUERCUS_LONGISPICA_GENOME_PATH $DBDIR_QUERCUS_LONGISPICA_GENOME_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus longispica genome GFF3 ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_LONGISPICA_GFF_PATH_GZ \
                $NGDC_QUERCUS_LONGISPICA_GFF_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_LONGISPICA_GFF_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus longispica genome GFF3 to database dir ...'
        cp $REPOSITORY_QUERCUS_LONGISPICA_GFF_PATH $DBDIR_QUERCUS_LONGISPICA_GFF_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus variabilis genome FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_VARIABILIS_GENOME_PATH_GZ \
                $NGDC_QUERCUS_VARIABILIS_GENOME_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_VARIABILIS_GENOME_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus variabilis genome FASTA to database dir ...'
        cp $REPOSITORY_QUERCUS_VARIABILIS_GENOME_PATH $DBDIR_QUERCUS_VARIABILIS_GENOME_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

    if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
        echo "$SEP"
        echo 'Downloading and decompressing Quercus variabilis genome GFF3 ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $DBDIR_QUERCUS_VARIABILIS_GFF_PATH_GZ \
                $NGDC_QUERCUS_VARIABILIS_GFF_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $DBDIR_QUERCUS_VARIABILIS_GFF_PATH_GZ
        RC=$?
        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
        echo 'File is downloaded and decompressed.'
    else
        echo "$SEP"
        echo 'Copying Quercus variabilis genome GFF3 to database dir ...'
        cp $REPOSITORY_QUERCUS_VARIABILIS_GFF_PATH $DBDIR_QUERCUS_VARIABILIS_GFF_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File id copied.'
    fi

}

#-------------------------------------------------------------------------------

function download_protein_sequences
{

    if [ "$ENVIRONMENT" = "$ENV_AWS" ]; then

        if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
            echo "$SEP"
            echo 'Downloading and decompressing Quercus lobata protein FASTA ...'
            /usr/bin/time \
                wget \
                    --quiet \
                    --output-document $DBDIR_QUERCUS_LOBATA_PROTEIN_PATH_GZ \
                    $GENOME_QUERCUS_LOBATA_PROTEIN_URL
            RC=$?
            if [ $RC -ne 0 ]; then manage_error wget $RC; fi
            gzip -d $DBDIR_QUERCUS_LOBATA_PROTEIN_PATH_GZ
            RC=$?
            if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
            echo 'File is downloaded and decompressed.'
        else
            echo "$SEP"
            echo 'Copying Quercus lobata protein FASTA to database dir ...'
            cp $REPOSITORY_QUERCUS_LOBATA_PROTEIN_PATH $DBDIR_QUERCUS_LOBATA_PROTEIN_PATH
            RC=$?
            if [ $RC -ne 0 ]; then manage_error cp $RC; fi
            echo 'File id copied.'
        fi

        if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
            echo "$SEP"
            echo 'Downloading and decompressing Quercus robur protein FASTA ...'
            /usr/bin/time \
                wget \
                    --quiet \
                    --output-document $DBDIR_QUERCUS_ROBUR_PROTEIN_PATH_GZ \
                    $GENOME_QUERCUS_ROBUR_PROTEIN_URL
            RC=$?
            if [ $RC -ne 0 ]; then manage_error wget $RC; fi
            gzip -d $DBDIR_QUERCUS_ROBUR_PROTEIN_PATH_GZ
            RC=$?
            if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
            echo 'File is downloaded and decompressed.'
        else
            echo "$SEP"
            echo 'Copying Quercus robur protein FASTA to database dir ...'
            cp $REPOSITORY_QUERCUS_ROBUR_PROTEIN_PATH $DBDIR_QUERCUS_ROBUR_PROTEIN_PATH
            RC=$?
            if [ $RC -ne 0 ]; then manage_error cp $RC; fi
            echo 'File id copied.'
        fi

        if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
            echo "$SEP"
            echo 'Downloading and decompressing Quercus rubra protein FASTA ...'
            /usr/bin/time \
                wget \
                    --quiet \
                    --output-document $DBDIR_QUERCUS_RUBRA_PROTEIN_PATH_GZ \
                    $GENOME_QUERCUS_RUBRA_PROTEIN_URL
            RC=$?
            if [ $RC -ne 0 ]; then manage_error wget $RC; fi
            gzip -d $DBDIR_QUERCUS_RUBRA_PROTEIN_PATH_GZ
            RC=$?
            if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
            echo 'File is downloaded and decompressed.'
        else
            echo "$SEP"
            echo 'Copying Quercus rubra protein FASTA to database dir ...'
            cp $REPOSITORY_QUERCUS_RUBRA_PROTEIN_PATH $DBDIR_QUERCUS_RUBRA_PROTEIN_PATH
            RC=$?
            if [ $RC -ne 0 ]; then manage_error cp $RC; fi
            echo 'File id copied.'
        fi

        if [ "$NCBI_GENOMIC_FILES_SOURCE" = "$NCBI_GENOMIC_FILES_SOURCE_1" ]; then
            echo "$SEP"
            echo 'Downloading and decompressing Quercus suber protein FASTA ...'
            /usr/bin/time \
                wget \
                    --quiet \
                    --output-document $DBDIR_QUERCUS_SUBER_PROTEIN_PATH_GZ \
                    $GENOME_QUERCUS_SUBER_PROTEIN_URL
            RC=$?
            if [ $RC -ne 0 ]; then manage_error wget $RC; fi
            gzip -d $DBDIR_QUERCUS_SUBER_PROTEIN_PATH_GZ
            RC=$?
            if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
            echo 'File is downloaded and decompressed.'
        else
            echo "$SEP"
            echo 'Copying Quercus suber protein FASTA to database dir ...'
            cp $REPOSITORY_QUERCUS_SUBER_PROTEIN_PATH $DBDIR_QUERCUS_SUBER_PROTEIN_PATH
            RC=$?
            if [ $RC -ne 0 ]; then manage_error cp $RC; fi
            echo 'File id copied.'
        fi

        if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
            echo "$SEP"
            echo 'Downloading and decompressing Quercus acutissima protein FASTA ...'
            /usr/bin/time \
                wget \
                    --quiet \
                    --output-document $DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH_GZ \
                    $NGDC_QUERCUS_ACUTISSIMA_PROTEIN_URL
            RC=$?
            if [ $RC -ne 0 ]; then manage_error wget $RC; fi
            gzip -d $DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH_GZ
            RC=$?
            if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
            echo 'File is downloaded and decompressed.'
        else
            echo "$SEP"
            echo 'Copying Quercus acutissima protein FASTA to database dir ...'
            cp $REPOSITORY_QUERCUS_ACUTISSIMA_PROTEIN_PATH $DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH
            RC=$?
            if [ $RC -ne 0 ]; then manage_error cp $RC; fi
            echo 'File id copied.'
        fi

        echo "$SEP"
        echo 'Adding species name to headers of Quercus acutissima protein FASTA ...'
        /usr/bin/time \
            add-species-in-headers.py \
                --species="Quercus acutissima" \
                --fasta=$DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH \
                --output=$DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH_WSPECIES \
                --verbose=N \
                --trace=N
        RC=$?
        if [ $RC -ne 0 ]; then manage_error add-species-in-headers.py $RC; fi
        echo 'Species name added.'

        if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
            echo "$SEP"
            echo 'Downloading and decompressing Quercus dentata protein FASTA ...'
            /usr/bin/time \
                wget \
                    --quiet \
                    --output-document $DBDIR_QUERCUS_DENTATA_PROTEIN_PATH_GZ \
                    $NGDC_QUERCUS_DENTATA_PROTEIN_URL
            RC=$?
            if [ $RC -ne 0 ]; then manage_error wget $RC; fi
            gzip -d $DBDIR_QUERCUS_DENTATA_PROTEIN_PATH_GZ
            RC=$?
            if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
            echo 'File is downloaded and decompressed.'
        else
            echo "$SEP"
            echo 'Copying Quercus dentata protein FASTA to database dir ...'
            cp $REPOSITORY_QUERCUS_DENTATA_PROTEIN_PATH $DBDIR_QUERCUS_DENTATA_PROTEIN_PATH
            RC=$?
            if [ $RC -ne 0 ]; then manage_error cp $RC; fi
            echo 'File id copied.'
        fi

        echo "$SEP"
        echo 'Adding species name to headers of Quercus dentata protein FASTA ...'
        /usr/bin/time \
            add-species-in-headers.py \
                --species="Quercus dentata" \
                --fasta=$DBDIR_QUERCUS_DENTATA_PROTEIN_PATH \
                --output=$DBDIR_QUERCUS_DENTATA_PROTEIN_PATH_WSPECIES \
                --verbose=N \
                --trace=N
        RC=$?
        if [ $RC -ne 0 ]; then manage_error add-species-in-headers.py $RC; fi
        echo 'Species name added.'

        if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
            echo "$SEP"
            echo 'Downloading and decompressing Quercus gilva protein FASTA ...'
            /usr/bin/time \
                wget \
                    --quiet \
                    --output-document $DBDIR_QUERCUS_GILVA_PROTEIN_PATH_GZ \
                    $NGDC_QUERCUS_GILVA_PROTEIN_URL
            RC=$?
            if [ $RC -ne 0 ]; then manage_error wget $RC; fi
            gzip -d $DBDIR_QUERCUS_GILVA_PROTEIN_PATH_GZ
            RC=$?
            if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
            echo 'File is downloaded and decompressed.'
        else
            echo "$SEP"
            echo 'Copying Quercus gilva protein FASTA to database dir ...'
            cp $REPOSITORY_QUERCUS_GILVA_PROTEIN_PATH $DBDIR_QUERCUS_GILVA_PROTEIN_PATH
            RC=$?
            if [ $RC -ne 0 ]; then manage_error cp $RC; fi
            echo 'File id copied.'
        fi

        echo "$SEP"
        echo 'Adding species name to headers of Quercus gilva protein FASTA ...'
        /usr/bin/time \
            add-species-in-headers.py \
                --species="Quercus gilva" \
                --fasta=$DBDIR_QUERCUS_GILVA_PROTEIN_PATH \
                --output=$DBDIR_QUERCUS_GILVA_PROTEIN_PATH_WSPECIES \
                --verbose=N \
                --trace=N
        RC=$?
        if [ $RC -ne 0 ]; then manage_error add-species-in-headers.py $RC; fi
        echo 'Species name added.'

        if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
            echo "$SEP"
            echo 'Downloading and decompressing Quercus longispica protein FASTA ...'
            /usr/bin/time \
                wget \
                    --quiet \
                    --output-document $DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH_GZ \
                    $NGDC_QUERCUS_LONGISPICA_PROTEIN_URL
            RC=$?
            if [ $RC -ne 0 ]; then manage_error wget $RC; fi
            gzip -d $DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH_GZ
            RC=$?
            if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
            echo 'File is downloaded and decompressed.'
        else
            echo "$SEP"
            echo 'Copying Quercus longispica protein FASTA to database dir ...'
            cp $REPOSITORY_QUERCUS_LONGISPICA_PROTEIN_PATH $DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH
            RC=$?
            if [ $RC -ne 0 ]; then manage_error cp $RC; fi
            echo 'File id copied.'
        fi

        echo "$SEP"
        echo 'Adding species name to headers of Quercus longispica protein FASTA ...'
        /usr/bin/time \
            add-species-in-headers.py \
                --species="Quercus longispica" \
                --fasta=$DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH \
                --output=$DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH_WSPECIES \
                --verbose=N \
                --trace=N
        RC=$?
        if [ $RC -ne 0 ]; then manage_error add-species-in-headers.py $RC; fi
        echo 'Species name added.'

        if [ "$NGDC_GENOMIC_FILES_SOURCE" = "$NGDC_GENOMIC_FILES_SOURCE_1" ]; then
            echo "$SEP"
            echo 'Downloading and decompressing Quercus variabilis protein FASTA ...'
            /usr/bin/time \
                wget \
                    --quiet \
                    --output-document $DBDIR_QUERCUS_VARIABILIS_PROTEIN_PATH_GZ \
                    $NGDC_QUERCUS_VARIABILIS_PROTEIN_URL
            RC=$?
            if [ $RC -ne 0 ]; then manage_error wget $RC; fi
            gzip -d $DBDIR_QUERCUS_VARIABILIS_PROTEIN_PATH_GZ
            RC=$?
            if [ $RC -ne 0 ]; then manage_error gzip $RC; fi
            echo 'File is downloaded and decompressed.'
        else
            echo "$SEP"
            echo 'Copying Quercus variabilis protein FASTA to database dir ...'
            cp $REPOSITORY_QUERCUS_VARIABILIS_PROTEIN_PATH $DBDIR_QUERCUS_VARIABILIS_PROTEIN_PATH
            RC=$?
            if [ $RC -ne 0 ]; then manage_error cp $RC; fi
            echo 'File id copied.'
        fi

        echo "$SEP"
        echo 'Adding species name to headers of Quercus variabilis protein FASTA ...'
        /usr/bin/time \
            add-species-in-headers.py \
                --species="Quercus variabilis" \
                --fasta=$DBDIR_QUERCUS_VARIABILIS_PROTEIN_PATH \
                --output=$DBDIR_QUERCUS_VARIABILIS_PROTEIN_PATH_WSPECIES \
                --verbose=N \
                --trace=N
        RC=$?
        if [ $RC -ne 0 ]; then manage_error add-species-in-headers.py $RC; fi
        echo 'Species name added.'

        echo "$SEP"
        echo 'Concatenating the protein FASTAs ...'
        /usr/bin/time \
            cat \
                $DBDIR_QUERCUS_LOBATA_PROTEIN_PATH \
                $DBDIR_QUERCUS_ROBUR_PROTEIN_PATH \
                $DBDIR_QUERCUS_RUBRA_PROTEIN_PATH \
                $DBDIR_QUERCUS_SUBER_PROTEIN_PATH \
                $DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH_WSPECIES \
                $DBDIR_QUERCUS_DENTATA_PROTEIN_PATH_WSPECIES \
                $DBDIR_QUERCUS_GILVA_PROTEIN_PATH_WSPECIES \
                $DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH_WSPECIES \
                $DBDIR_QUERCUS_VARIABILIS_PROTEIN_PATH_WSPECIES \
                > $PROTEIN_FASTA_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cat $RC; fi
        echo 'Files are concatenated.'

    elif [ "$ENVIRONMENT" = "$ENV_LOCAL" ]; then

        echo "$SEP"
        echo 'Copying the file of protin FASTAs concatenated to database directory ...'
        cp $QUERCUSTOA/data/$PROTEIN_FASTA_FILE $PROTEIN_FASTA_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        echo 'File is copied.'

    else

        echo 'Environment error'; exit 3

    fi

}

#-------------------------------------------------------------------------------

function load_species_sequences
{

    echo "$SEP"
    echo 'Loading Quercus lobata sequences into the sequence database ...'
    /usr/bin/time \
        load-species-seqs.py \
            --db=$SEQUENCES_DB_PATH \
            --server=NCBI \
            --species=$QLOBATA\
            --genome=$DBDIR_QUERCUS_LOBATA_GENOME_PATH \
            --gff=$DBDIR_QUERCUS_LOBATA_GFF_PATH \
            --proteins=$DBDIR_QUERCUS_LOBATA_PROTEIN_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-species-seqs.py $RC; fi
    echo 'Sequences are loaded.'

    echo "$SEP"
    echo 'Loading Quercus robur sequences into the sequence database ...'
    /usr/bin/time \
        load-species-seqs.py \
            --db=$SEQUENCES_DB_PATH \
            --server=NCBI \
            --species=$QROBUR\
            --genome=$DBDIR_QUERCUS_ROBUR_GENOME_PATH \
            --gff=$DBDIR_QUERCUS_ROBUR_GFF_PATH \
            --proteins=$DBDIR_QUERCUS_ROBUR_PROTEIN_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-species-seqs.py $RC; fi
    echo 'Sequences are loaded.'

    echo "$SEP"
    echo 'Loading Quercus rubra sequences into the sequence database ...'
    /usr/bin/time \
        load-species-seqs.py \
            --db=$SEQUENCES_DB_PATH \
            --server=NCBI \
            --species=$QRUBRA\
            --genome=$DBDIR_QUERCUS_RUBRA_GENOME_PATH \
            --gff=$DBDIR_QUERCUS_RUBRA_GFF_PATH \
            --proteins=$DBDIR_QUERCUS_RUBRA_PROTEIN_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-species-seqs.py $RC; fi
    echo 'Sequences are loaded.'

    echo "$SEP"
    echo 'Loading Quercus suber sequences into the sequence database ...'
    /usr/bin/time \
        load-species-seqs.py \
            --db=$SEQUENCES_DB_PATH \
            --server=NCBI \
            --species=$QSUBER\
            --genome=$DBDIR_QUERCUS_SUBER_GENOME_PATH \
            --gff=$DBDIR_QUERCUS_SUBER_GFF_PATH \
            --proteins=$DBDIR_QUERCUS_SUBER_PROTEIN_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-species-seqs.py $RC; fi
    echo 'Sequences are loaded.'

    echo "$SEP"
    echo 'Loading Quercus acutissima sequences into the sequence database ...'
    /usr/bin/time \
        load-species-seqs.py \
            --db=$SEQUENCES_DB_PATH \
            --server=CNCB-NGDC \
            --species=$QACUTISSIMA\
            --genome=$DBDIR_QUERCUS_ACUTISSIMA_GENOME_PATH \
            --gff=$DBDIR_QUERCUS_ACUTISSIMA_GFF_PATH \
            --proteins=$DBDIR_QUERCUS_ACUTISSIMA_PROTEIN_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-species-seqs.py $RC; fi
    echo 'Sequences are loaded.'

    echo "$SEP"
    echo 'Loading Quercus dentata sequences into the sequence database ...'
    /usr/bin/time \
        load-species-seqs.py \
            --db=$SEQUENCES_DB_PATH \
            --server=CNCB-NGDC \
            --species=$QDENTATA\
            --genome=$DBDIR_QUERCUS_DENTATA_GENOME_PATH \
            --gff=$DBDIR_QUERCUS_DENTATA_GFF_PATH \
            --proteins=$DBDIR_QUERCUS_DENTATA_PROTEIN_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-species-seqs.py $RC; fi
    echo 'Sequences are loaded.'

    echo "$SEP"
    echo 'Loading Quercus gilva sequences into the sequence database ...'
    /usr/bin/time \
        load-species-seqs.py \
            --db=$SEQUENCES_DB_PATH \
            --server=CNCB-NGDC \
            --species=$QGILVA\
            --genome=$DBDIR_QUERCUS_GILVA_GENOME_PATH \
            --gff=$DBDIR_QUERCUS_GILVA_GFF_PATH \
            --proteins=$DBDIR_QUERCUS_GILVA_PROTEIN_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-species-seqs.py $RC; fi
    echo 'Sequences are loaded.'

    echo "$SEP"
    echo 'Loading Quercus longispica sequences into the sequence database ...'
    /usr/bin/time \
        load-species-seqs.py \
            --db=$SEQUENCES_DB_PATH \
            --server=CNCB-NGDC \
            --species=$QLONGISPICA\
            --genome=$DBDIR_QUERCUS_LONGISPICA_GENOME_PATH \
            --gff=$DBDIR_QUERCUS_LONGISPICA_GFF_PATH \
            --proteins=$DBDIR_QUERCUS_LONGISPICA_PROTEIN_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-species-seqs.py $RC; fi
    echo 'Sequences are loaded.'

    echo "$SEP"
    echo 'Loading Quercus variabilis sequences into the sequence database ...'
    /usr/bin/time \
        load-species-seqs.py \
            --db=$SEQUENCES_DB_PATH \
            --server=CNCB-NGDC \
            --species=$QVARIABILIS\
            --genome=$DBDIR_QUERCUS_VARIABILIS_GENOME_PATH \
            --gff=$DBDIR_QUERCUS_VARIABILIS_GFF_PATH \
            --proteins=$DBDIR_QUERCUS_VARIABILIS_PROTEIN_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-species-seqs.py $RC; fi
    echo 'Sequences are loaded.'

}

#-------------------------------------------------------------------------------

function download_tair10_sequences
{

    echo "$SEP"
    echo 'Downloading TAIR10 peptide sequences ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $TAIR10_PEP_PATH \
            $TAIR10_PEP_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

}

#-------------------------------------------------------------------------------

function download_lncrna_sequences
{

    echo "$SEP"
    echo 'Downloading Arabidopsis thaliana lncRNA FASTA ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $CANTATA_ARABIDOPSIS_THALIANA_FASTA_PATH \
            $CANTATA_ARABIDOPSIS_THALIANA_FASTA_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

    echo "$SEP"
    echo 'Downloading Arabidopsis thaliana lncRNA GTF ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $CANTATA_ARABIDOPSIS_THALIANA_GTF_PATH \
            $CANTATA_ARABIDOPSIS_THALIANA_GTF_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

    echo "$SEP"
    echo 'Downloading Quercus lobata lncRNA FASTA ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $CANTATA_QUERCUS_LOBATA_FASTA_PATH \
            $CANTATA_QUERCUS_LOBATA_FASTA_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

    echo "$SEP"
    echo 'Downloading Quercus lobata lncRNA GTF ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $CANTATA_QUERCUS_LOBATA_GTF_PATH \
            $CANTATA_QUERCUS_LOBATA_GTF_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

    echo "$SEP"
    echo 'Downloading Quercus suber lncRNA FASTA ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $CANTATA_QUERCUS_SUBER_FASTA_PATH \
            $CANTATA_QUERCUS_SUBER_FASTA_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

    echo "$SEP"
    echo 'Downloading Quercus suber lncRNA GTF ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $CANTATA_QUERCUS_SUBER_GTF_PATH \
            $CANTATA_QUERCUS_SUBER_GTF_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

    echo "$SEP"
    echo 'Concatenating the lncRNA FASTAs ...'
    /usr/bin/time \
        cat \
            $CANTATA_ARABIDOPSIS_THALIANA_FASTA_PATH \
            $CANTATA_QUERCUS_LOBATA_FASTA_PATH \
            $CANTATA_QUERCUS_SUBER_FASTA_PATH \
            > $LNCRNAS_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error cat $RC; fi
    echo 'Files are concatenated.'

}

#-------------------------------------------------------------------------------

function download_taxonomy_data
{

    echo "$SEP"
    echo 'Downloading and decompressing NCBI Taxonomy database dump file ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $TAXONOMY_TAXDMP_PATH \
            $TAXONOMY_TAXDMP_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    unzip -o -d $FUNCTIONAL_ANNOTATIONS_TEMP_DIR $TAXONOMY_TAXDMP_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error unzip $RC; fi
    echo 'File is downloaded and decompressed.'

}

#-------------------------------------------------------------------------------

function cluster_protein_sequences
{

    source activate mmseqs2

    OUTPUT_PREFIX=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$CLADE-mmseqs2
    if [ ! -d "$OUTPUT_PREFIX" ]; then mkdir --parents $OUTPUT_PREFIX; fi
    MMSEQ2_TEMP_DIR=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR/$CLADE-mmseqs2-temp
    if [ ! -d "$MMSEQ2_TEMP_DIR" ]; then mkdir --parents $MMSEQ2_TEMP_DIR; fi

    echo "$SEP"
    echo 'Clustering protein sequences ...'
    /usr/bin/time \
        mmseqs \
            easy-cluster \
            $PROTEIN_FASTA_PATH \
            $OUTPUT_PREFIX \
            $MMSEQ2_TEMP_DIR \
            -v 0 \
            --threads $THREADS \
            -s $S \
            --mask 0 \
            --min-seq-id $MSI \
            -c $C \
            --cov-mode $CM \
            --similarity-type $ST
    RC=$?
    if [ $RC -ne 0 ]; then manage_error mmseqs $RC; fi
    echo 'Sequences are clustered.'

    conda deactivate

}

#-------------------------------------------------------------------------------

function split_protein_clusters
{

    echo "$SEP"
    echo 'Splitting protein clusters ...'
    /usr/bin/time \
        split-mmseqs2-protein-clusters.py \
            --allseqs=$ALLSEQS_PATH \
            --clusters=$CLUSTER_PATH \
            --outdir=$PROTEIN_CLUSTER_DIR \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error split-mmseqs2-protein-clusters.py $RC; fi
    echo 'Clusters are splitted.'

}

#-------------------------------------------------------------------------------

function load_protein_clusters
{

    echo "$SEP"
    echo 'Loading protein clusters into the quercusTOA database ...'
    /usr/bin/time \
        load-mmseqs2-protein-clusters.py \
            --db=$FUNCTIONAL_ANNOTATIONS_DB_PATH \
            --clusters=$CLUSTER_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-mmseqs2-protein-clusters.py $RC; fi
    echo 'Clusters are loaded.'

}

#-------------------------------------------------------------------------------

function align_protein_clusters
{

    source activate $ALIGNER

    echo "$SEP"
    CLUSTERS_FILE_LIST=$PROTEIN_CLUSTER_DIR/clusters-files.txt
    find $PROTEIN_CLUSTER_DIR -type f -name cluster*.fasta > $CLUSTERS_FILE_LIST
    sort --output=$CLUSTERS_FILE_LIST $CLUSTERS_FILE_LIST
    while read FILE_1; do
        echo "Aligning sequences in cluster file `basename $FILE_1` ..."
        FILE_2=`echo $FILE_1 | sed "s/.fasta/-$ALIGNER.fasta/g"`
        if [ "$ALIGNER" = "$MAFFT" ]; then
            /usr/bin/time \
                mafft \
                    --thread $THREADS \
                    --amino \
                    $FILE_1 \
                    > $FILE_2
            RC=$?
            if [ $RC -ne 0 ]; then manage_error mafft $RC; fi
        elif [ "$ALIGNER" = "$MUSCLE" ]; then
            NLIN=`grep -o '>' $FILE_1 | wc -l`
            if [ $NLIN -gt 1 ]; then
                /usr/bin/time \
                    muscle \
                        -quiet \
                        -align $FILE_1 \
                        -output $FILE_2
                RC=$?
                if [ $RC -ne 0 ]; then manage_error muscle $RC; fi
            else
                cp $FILE_1 $FILE_2
                RC=$?
                if [ $RC -ne 0 ]; then manage_error cp $RC; fi
            fi
        else
            echo 'Aligner error'; exit 3
        fi
        echo 'Sequences are aligned.'
    done < $CLUSTERS_FILE_LIST

    conda deactivate

}

#-------------------------------------------------------------------------------

function calculate_protein_clusters_identity
{

    echo "$SEP"
    echo 'Calculating identity percentage of protein clusters ...'
    /usr/bin/time \
        calculate-alignment-identity.py \
            --indir=$PROTEIN_CLUSTER_DIR \
            --pattern=cluster.*-$ALIGNER.fasta \
            --out=$IDENTITIES_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error calculate-alignment-identity.py $RC; fi
    echo 'Identity percentage is calculated.'

}

#-------------------------------------------------------------------------------

function calculate_consensus_seqs
{

    source activate emboss

    echo "$SEP"
    ALIGNED_CLUSTERS_FILE_LIST=$PROTEIN_CLUSTER_DIR/aligned-clusters-files.txt
    find $PROTEIN_CLUSTER_DIR -type f -name cluster*-$ALIGNER.fasta > $ALIGNED_CLUSTERS_FILE_LIST
    sort --output=$ALIGNED_CLUSTERS_FILE_LIST $ALIGNED_CLUSTERS_FILE_LIST
    while read FILE_1; do
        echo "Calculting consensus sequence in cluster file `basename $FILE_1` ..."
        FILE_2=`echo $FILE_1 | sed "s/-$ALIGNER.fasta/-$ALIGNER-cons.fasta/g"`
        NLIN=`grep -o '>' $FILE_1 | wc -l`
        if [ $NLIN -gt 1 ]; then
            /usr/bin/time \
                cons \
                    -sequence $FILE_1 \
                    -outseq $FILE_2
            RC=$?
            if [ $RC -ne 0 ]; then manage_error mafft $RC; fi
        else
            cp $FILE_1 $FILE_2
            RC=$?
            if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        fi
    done < $ALIGNED_CLUSTERS_FILE_LIST

    conda deactivate

}

#-------------------------------------------------------------------------------

function unify_consensus_seqs
{

    echo "$SEP"
    echo 'Unifying consensus sequences ...'
    /usr/bin/time \
        unify-consensus-seqs.py \
            --indir=$PROTEIN_CLUSTER_DIR \
            --pattern=cluster.*-$ALIGNER-cons.fasta \
            --out=$CONSEQS_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error calculate-alignment-identity.py $RC; fi
    echo 'Sequences are unified.'

}

#-------------------------------------------------------------------------------

function download_busco_dataset
{

    echo "$SEP"
    echo 'Downloading and decompressing BUSCO gymnosperm dataset ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $BUSCO_DATASET_PATH \
            $BUSCO_DATASET_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    tar -xzvf $BUSCO_DATASET_PATH --directory=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR
    RC=$?
    if [ $RC -ne 0 ]; then manage_error tar $RC; fi
    echo 'File is downloaded and decompressed.'

}

#-------------------------------------------------------------------------------

function assess_consensus_seqs
{

    source activate busco

    echo "$SEP"
    echo 'Assessing consensus sequences ...'
    /usr/bin/time \
        busco \
            --cpu=$THREADS \
            --force \
            --lineage_dataset=$BUSCO_DATASET_DIR \
            --mode=proteins \
            --evalue=1E-03 \
            --limit=3 \
            --in=$CONSEQS_PATH \
            --out_path=$FUNCTIONAL_ANNOTATIONS_TEMP_DIR \
            --out=$BUSCO_ASSESSMENT_PATTERN
    RC=$?
    if [ $RC -ne 0 ]; then manage_error busco $RC; fi
    tail -n +7 $BUSCO_ASSESSMENT_PATH | head -n -4 > $BUSCO_ASSESSMENT_DATA_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error tail-head $RC; fi
    echo 'Sequences are assessed.'

    conda deactivate

}

#-------------------------------------------------------------------------------

function build_consensus_blast_db
{

    source activate blast

    echo "$SEP"
    echo "Generating BLAST+ database with the $CLADE consensus sequences ..."
    /usr/bin/time \
        makeblastdb \
            -title $CONSEQS_BLAST_DB_NAME \
            -dbtype prot \
            -input_type fasta \
            -in $CONSEQS_PATH \
            -out $CONSEQS_BLAST_DB_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error makeblastdb $RC; fi
    echo 'BLAST+ database is generated.'

    conda deactivate

}

#-------------------------------------------------------------------------------

function build_consensus_diamond_db
{

    source activate diamond

    echo "$SEP"
    echo "Generating DIAMOND database with the $CLADE consensus sequences ..."
    /usr/bin/time \
        diamond makedb \
            --threads $THREADS \
            --in $CONSEQS_PATH \
            --db $CONSEQS_DIAMOND_DB_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error diamond-makedb $RC; fi
    echo 'DIAMOND database is generated.'

    conda deactivate

}

#-------------------------------------------------------------------------------

function run_interscanpro_analysis
{

    echo "$SEP"
    echo 'Running InterScanPro analysis ...'
    /usr/bin/time \
        $INTERPROSCAN_DIR/interproscan.sh \
            --cpu $THREADS \
            --input $CONSEQS_PATH \
            --seqtype $FASTA_TYPE \
            --applications $INTERPROSCAN_ANALYSIS \
            --iprlookup \
            --goterms \
            --pathways \
            --formats $INTERPROSCAN_FORMATS \
            --output-dir $FUNCTIONAL_ANNOTATIONS_TEMP_DIR
    RC=$?
    if [ $RC -ne 0 ]; then manage_error interproscan.sh $RC; fi
    mv $INTERPRO_OUPUT $INTERPRO_ANNOTATIONS_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error mv $RC; fi
    echo 'InterScanPro analysis is ended.'

}

#-------------------------------------------------------------------------------

function load_interproscan_annotations
{

    echo "$SEP"
    echo 'Loading InterScanPro annotations into quercusTOA database ...'
    /usr/bin/time \
        load-interproscan-annotations.py \
            --db=$FUNCTIONAL_ANNOTATIONS_DB_PATH \
            --annotations=$INTERPRO_ANNOTATIONS_PATH \
            --stats=NONE \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-interproscan-annotations.py $RC; fi
    echo 'Annotations are loaded.'

}

#-------------------------------------------------------------------------------

function run_eggnog_mapper_analysis
{

    source activate eggnog-mapper

    echo "$SEP"
    echo 'Running eggNOG-mapper analysis ...'
    if [ "$EMAPPER_SEARCH_OPTION" = "$DIAMOND" ]; then
        # -- /usr/bin/time \
        # --     emapper.py \
        # --         --cpu $THREADS \
        # --         -i $CONSEQS_PATH \
        # --         --itype $EMAPPER_ITYPE \
        # --         -m $DIAMOND \
        # --         --dmnd_algo $EMAPPER_DMND_ALGO \
        # --         --sensmode $EMAPPER_SENSMODE \
        # --         --dmnd_iterate $EMAPPER_DMND_ITERATE \
        # --         --pident $EMAPPER_PIDENT \
        # --         --evalue $EMAPPER_EVALUE \
        # --         --query_cover $EMAPPER_QUERY_COVER \
        # --         --output_dir $FUNCTIONAL_ANNOTATIONS_TEMP_DIR \
        # --         --output $CONSEQS_PREFIX
        /usr/bin/time \
            emapper.py \
                --cpu $THREADS \
                -i $CONSEQS_PATH \
                --itype $EMAPPER_ITYPE \
                -m $DIAMOND \
                --dmnd_algo $EMAPPER_DMND_ALGO \
                --sensmode $EMAPPER_SENSMODE \
                --dmnd_iterate $EMAPPER_DMND_ITERATE \
                --evalue $EMAPPER_EVALUE \
                --output_dir $FUNCTIONAL_ANNOTATIONS_TEMP_DIR \
                --output $CONSEQS_PREFIX
        RC=$?
        if [ $RC -ne 0 ]; then manage_error emapper.py $RC; fi
    elif [ "$EMAPPER_SEARCH_OPTION" = "$MMSEQS" ]; then
        # -- /usr/bin/time \
        # --     emapper.py \
        # --         --cpu $THREADS \
        # --         -i $CONSEQS_PATH \
        # --         --itype $EMAPPER_ITYPE \
        # --         -m $MMSEQS \
        # --         --start_sens $EMAPPER_START_SENS \
        # --         --sens_steps $EMAPPER_SENS_STEPS \
        # --         --final_sens $EMAPPER_FINAL_SENS \
        # --         --pident $EMAPPER_PIDENT \
        # --         --evalue $EMAPPER_EVALUE \
        # --         --query_cover $EMAPPER_QUERY_COVER \
        # --         --output_dir $FUNCTIONAL_ANNOTATIONS_TEMP_DIR \
        # --         --output $CONSEQS_PREFIX
        /usr/bin/time \
            emapper.py \
                --cpu $THREADS \
                -i $CONSEQS_PATH \
                --itype $EMAPPER_ITYPE \
                -m $MMSEQS \
                --start_sens $EMAPPER_START_SENS \
                --sens_steps $EMAPPER_SENS_STEPS \
                --final_sens $EMAPPER_FINAL_SENS \
                --evalue $EMAPPER_EVALUE \
                --output_dir $FUNCTIONAL_ANNOTATIONS_TEMP_DIR \
                --output $CONSEQS_PREFIX
        RC=$?
        if [ $RC -ne 0 ]; then manage_error emapper.py $RC; fi
    else
        echo 'Search option error'; exit 3
    fi
    mv $EMAPPER_OUPUT $EMAPPER_ANNOTATIONS_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error mv $RC; fi
    echo 'eggNOG-mapper analysis is ended.'

    conda deactivate

}

#-------------------------------------------------------------------------------

function load_emapper_annotations
{

    echo "$SEP"
    echo 'Loading eggNOG-mapper annotations into quercusTOA database ...'
    /usr/bin/time \
        load-emapper-annotations.py \
            --db=$FUNCTIONAL_ANNOTATIONS_DB_PATH \
            --annotations=$EMAPPER_ANNOTATIONS_PATH \
            --taxnames=$TAXONOMY_TAXONNAMES_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-interproscan-annotations.py $RC; fi
    echo 'Annotations are loaded.'

}

#-------------------------------------------------------------------------------

function load_tair10_info
{

    echo "$SEP"
    echo 'Loading TAIR10 peptide information ...'
    /usr/bin/time \
        load-tair10-info.py \
            --db=$FUNCTIONAL_ANNOTATIONS_DB_PATH \
            --tair10=$TAIR10_PEP_PATH \
            --verbose=N  \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

}

#-------------------------------------------------------------------------------

function build_tair10_blast_db
{

    source activate blast

    echo "$SEP"
    echo 'Generating BLAST+ database with the TAIR10 sequences ...'
    /usr/bin/time \
        makeblastdb \
            -title $TAIR10_BLAST_DB_NAME \
            -dbtype prot \
            -input_type fasta \
            -in $TAIR10_PEP_PATH \
            -out $TAIR10_BLAST_DB_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error makeblastdb $RC; fi
    echo 'BLAST+ database is generated.'

    conda deactivate

}

#-------------------------------------------------------------------------------

function align_consensus_seqs_2_tair10_blast_db
{

    source activate blast

    echo "$SEP"
    echo 'Aligning consensus sequences to BLAST+ TAIR10 database ...'
    export BLASTDB=$TAIR10_BLAST_DB_DIR
    /usr/bin/time \
        blastp \
            -num_threads $THREADS \
            -db $TAIR10_BLAST_DB_NAME \
            -query $CONSEQS_PATH \
            -evalue 1E-3 \
            -max_target_seqs 1 \
            -max_hsps 1 \
            -qcov_hsp_perc 0.0 \
            -outfmt "6 delim=; qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore" \
            -out $TAIR10_CONSEQS_ALIGNMENT_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error blastp $RC; fi
    echo 'Alignment is done.'

    conda deactivate

}

#-------------------------------------------------------------------------------

function load_tair10_orthologs
{

    echo "$SEP"
    echo 'Loading TAIR10 orthologs into quercusTOA database ...'
    /usr/bin/time \
        load-tair10-orthologs.py \
            --db=$FUNCTIONAL_ANNOTATIONS_DB_PATH \
            --alignments=$TAIR10_CONSEQS_ALIGNMENT_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-tair10-orthologs.py $RC; fi
    echo 'Orthologs are loaded.'

}

#-------------------------------------------------------------------------------

function download_gene_ontology
{

    echo "$SEP"
    echo 'Downloading Gene Ontology ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $GO_ONTOLOGY_FILE \
            $GO_ONTOLOGY_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

}

#-------------------------------------------------------------------------------

function load_gene_ontology
{

    echo "$SEP"
    echo 'Loading Gene Onlotoly into quercusTOA database ...'
    /usr/bin/time \
        load-gene-ontology.py \
            --db=$FUNCTIONAL_ANNOTATIONS_DB_PATH \
            --ontology=$GO_ONTOLOGY_FILE \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-gene_ontology.py $RC; fi
    echo 'Gene Ontology are loaded.'

}

#-------------------------------------------------------------------------------

function build_lncrna_blast_db
{

    source activate blast

    echo "$SEP"
    echo 'Generating BLAST+ database with the lncRNA sequences ...'
    /usr/bin/time \
        makeblastdb \
            -title $LNCRNAS_BLAST_DB_NAME \
            -dbtype nucl \
            -input_type fasta \
            -in $LNCRNAS_PATH \
            -out $LNCRNAS_BLAST_DB_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error makeblastdb $RC; fi
    echo 'BLAST+ database is generated.'

    conda deactivate

}

#-------------------------------------------------------------------------------

function cluster_genome_features
{

    for REFERENCE_SPECIES in "${REFERENCE_SPECIES_LIST[@]}"; do

        if [[ "$REFERENCE_SPECIES" == "$QACUTISSIMA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_ACUTISSIMA_GENOME_PATH
            REFERENCE_GFF_PATH=$DBDIR_QUERCUS_ACUTISSIMA_GFF_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QDENTATA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_DENTATA_GENOME_PATH
            REFERENCE_GFF_PATH=$DBDIR_QUERCUS_DENTATA_GFF_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QGILVA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_GILVA_GENOME_PATH
            REFERENCE_GFF_PATH=$DBDIR_QUERCUS_GILVA_GFF_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QLOBATA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_LOBATA_GENOME_PATH
            REFERENCE_GFF_PATH=$DBDIR_QUERCUS_LOBATA_GFF_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QLONGISPICA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_LONGISPICA_GENOME_PATH
            REFERENCE_GFF_PATH=$DBDIR_QUERCUS_LONGISPICA_GFF_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QROBUR" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_ROBUR_GENOME_PATH
            REFERENCE_GFF_PATH=$DBDIR_QUERCUS_ROBUR_GFF_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QRUBRA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_RUBRA_GENOME_PATH
            REFERENCE_GFF_PATH=$DBDIR_QUERCUS_RUBRA_GFF_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QSUBER" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_SUBER_GENOME_PATH
            REFERENCE_GFF_PATH=$DBDIR_QUERCUS_SUBER_GFF_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QVARIABILIS" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_VARIABILIS_GENOME_PATH
            REFERENCE_GFF_PATH=$DBDIR_QUERCUS_VARIABILIS_GFF_PATH
        else
            echo 'The reference species does not exist'; exit 3
        fi

        GENE_FILE_PATH=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/gff-gene.fasta
        CDS_FILE_PATH=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/gff-cds.fasta
        CONCDS_FILE_PATH=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/gff-concated-cds.fasta

        if [ ! -d "$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES" ]; then mkdir --parents $CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES; fi

        echo "$SEP"
        echo "Reference species: $REFERENCE_SPECIES - Extracting sequences of GFF features ..."
        /usr/bin/time \
            extract-gff-feature-seqs.py \
                --genome=$REFERENCE_GENOME_PATH \
                --gff=$REFERENCE_GFF_PATH \
                --gene-file=$GENE_FILE_PATH \
                --cds-file=$CDS_FILE_PATH \
                --concds-file=$CONCDS_FILE_PATH \
                --verbose=N \
                --trace=N \
                --tvi=NONE
        RC=$?
        if [ $RC -ne 0 ]; then manage_error extract-gff-feature-seqs.py $RC; fi
        echo 'Sequences are extracted.'

        OUTPUT_PREFIX=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/gff-concated-cds/mmseqs2
        MMSEQ2_TEMP_DIR=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/gff-concated-cds/mmseqs2-temp
        if [ ! -d "$OUTPUT_PREFIX" ]; then mkdir --parents $OUTPUT_PREFIX; fi
        if [ ! -d "$MMSEQ2_TEMP_DIR" ]; then mkdir --parents $MMSEQ2_TEMP_DIR; fi

        echo "$SEP"
        echo "Reference species: $REFERENCE_SPECIES - Clustering concated CDS sequences ..."
        source activate mmseqs2
        /usr/bin/time \
            mmseqs \
                easy-cluster \
                $CONCDS_FILE_PATH \
                $OUTPUT_PREFIX \
                $MMSEQ2_TEMP_DIR \
                -v 0 \
                --threads $THREADS \
                -s $S \
                --mask 0 \
                --min-seq-id $MSI \
                -c $C \
                --cov-mode $CM \
                --similarity-type $ST
        RC=$?
        if [ $RC -ne 0 ]; then manage_error mmseqs $RC; fi
        conda deactivate
        echo 'Sequences are clustered.'

        ALLSEQS_PATH=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/gff-concated-cds/mmseqs2_all_seqs.fasta
        CLUSTER_FILE_PATH=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/gff-concated-cds/concated-cds-clusters.csv
        CLUSTER_DIR=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/gff-concated-cds/clusters

        if [ ! -d "$CLUSTER_DIR" ]; then mkdir --parents $CLUSTER_DIR; fi

        echo "$SEP"
        echo "Reference species: $REFERENCE_SPECIES - Splitting clusters ..."
        /usr/bin/time \
            split-mmseqs2-concds-clusters.py \
                --allseqs=$ALLSEQS_PATH \
                --clusters=$CLUSTER_FILE_PATH \
                --outdir=$CLUSTER_DIR \
                --verbose=N \
                --trace=N
        RC=$?
        if [ $RC -ne 0 ]; then manage_error split-mmseqs2-concds-clusters.py $RC; fi
        echo 'Clusters are splitted.'

        echo "$SEP"
        echo "Reference species: $REFERENCE_SPECIES - Loading clusters into SQLite database ..."
        /usr/bin/time \
            load-mmseqs2-concds-clusters.py \
                --db=$COMPARATIVE_GENOMICS_DB_PATH \
                --clusters=$CLUSTER_FILE_PATH \
                --species=$REFERENCE_SPECIES \
                --verbose=N \
                --trace=N
        RC=$?
        if [ $RC -ne 0 ]; then manage_error load-mmseqs2-concds-clusters.py $RC; fi
        echo 'Clusters are loaded.'

        CLEANED_GFF_PATH=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/$REFERENCE_SPECIES-without-redundancies.gff
        REDUNDANCIES_PATH=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/$REFERENCE_SPECIES-redundancies.txt

        echo "$SEP"
        echo "Reference species: $REFERENCE_SPECIES - Removing redundancies from the GFF file ..."
        /usr/bin/time \
            remove-gff-redundancies.py \
                --db=$COMPARATIVE_GENOMICS_DB_PATH \
                --input-gff=$REFERENCE_GFF_PATH \
                --output-gff=$CLEANED_GFF_PATH \
                --redundancies=$REDUNDANCIES_PATH \
                --verbose=N \
                --trace=N \
                --tgi=NONE
        RC=$?
        if [ $RC -ne 0 ]; then manage_error remove-gff-redundancies.py $RC; fi
        echo 'GFF file is cleaned.'

    done

}

#-------------------------------------------------------------------------------

function run_genome_comparative
{

    for REFERENCE_SPECIES in "${REFERENCE_SPECIES_LIST[@]}"; do

        if [[ "$REFERENCE_SPECIES" == "$QACUTISSIMA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_ACUTISSIMA_GENOME_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QDENTATA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_DENTATA_GENOME_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QGILVA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_GILVA_GENOME_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QLOBATA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_LOBATA_GENOME_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QLONGISPICA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_LONGISPICA_GENOME_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QROBUR" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_ROBUR_GENOME_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QRUBRA" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_RUBRA_GENOME_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QSUBER" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_SUBER_GENOME_PATH
        elif [[ "$REFERENCE_SPECIES" == "$QVARIABILIS" ]]; then
            REFERENCE_GENOME_PATH=$DBDIR_QUERCUS_VARIABILIS_GENOME_PATH
        else
            echo 'The reference species does not exist'; exit 3
        fi

        CLEANED_GFF_PATH=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/$REFERENCE_SPECIES-without-redundancies.gff

        for TARGET_SPECIES in "${TARGET_SPECIES_LIST[@]}"; do

            if [[ "$TARGET_SPECIES" == "$QACUTISSIMA" ]]; then
                TARGET_GENOME_PATH=$DBDIR_QUERCUS_ACUTISSIMA_GENOME_PATH
            elif [[ "$TARGET_SPECIES" == "$QDENTATA" ]]; then
                TARGET_GENOME_PATH=$DBDIR_QUERCUS_DENTATA_GENOME_PATH
            elif [[ "$TARGET_SPECIES" == "$QGILVA" ]]; then
                TARGET_GENOME_PATH=$DBDIR_QUERCUS_GILVA_GENOME_PATH
            elif [[ "$TARGET_SPECIES" == "$QLOBATA" ]]; then
                TARGET_GENOME_PATH=$DBDIR_QUERCUS_LOBATA_GENOME_PATH
            elif [[ "$TARGET_SPECIES" == "$QLONGISPICA" ]]; then
                TARGET_GENOME_PATH=$DBDIR_QUERCUS_LONGISPICA_GENOME_PATH
            elif [[ "$TARGET_SPECIES" == "$QROBUR" ]]; then
                TARGET_GENOME_PATH=$DBDIR_QUERCUS_ROBUR_GENOME_PATH
            elif [[ "$TARGET_SPECIES" == "$QRUBRA" ]]; then
                TARGET_GENOME_PATH=$DBDIR_QUERCUS_RUBRA_GENOME_PATH
            elif [[ "$TARGET_SPECIES" == "$QSUBER" ]]; then
                TARGET_GENOME_PATH=$DBDIR_QUERCUS_SUBER_GENOME_PATH
            elif [[ "$TARGET_SPECIES" == "$QVARIABILIS" ]]; then
                TARGET_GENOME_PATH=$DBDIR_QUERCUS_VARIABILIS_GENOME_PATH
            else
                echo 'The target species does not exist'; exit 3
            fi
            TARGET_GFF_PATH=$COMPARATIVE_GENOMICS_TEMP_DIR/$REFERENCE_SPECIES-$TARGET_SPECIES-liftoff-target.gff
            UNMAPPED_FEATURES_PATH=$COMPARATIVE_GENOMICS_TEMP_DIR/$REFERENCE_SPECIES-$TARGET_SPECIES-liftoff-unmapped.txt
            GFF_GENE_DATA_PATH=$COMPARATIVE_GENOMICS_TEMP_DIR/$REFERENCE_SPECIES-$TARGET_SPECIES-gff-gene-data.csv
            GFF_CDS_DATA_PATH=$COMPARATIVE_GENOMICS_TEMP_DIR/$REFERENCE_SPECIES-$TARGET_SPECIES-gff-cds-data.csv
            INTERMEDIATE_FILES_PATH=$COMPARATIVE_GENOMICS_TEMP_DIR/$REFERENCE_SPECIES-$TARGET_SPECIES-liftoff-temp

            echo "$SEP"
            echo "Reference species: $REFERENCE_SPECIES - Target species: $TARGET_SPECIES - Building the target GFF file ..."
            source activate liftoff
            /usr/bin/time \
                liftoff \
                    -p $THREADS \
                    -g $CLEANED_GFF_PATH \
                    -o $TARGET_GFF_PATH \
                    -copies \
                    -u $UNMAPPED_FEATURES_PATH \
                    -dir $INTERMEDIATE_FILES_PATH \
                    $TARGET_GENOME_PATH \
                    $REFERENCE_GENOME_PATH
            RC=$?
            if [ $RC -ne 0 ]; then manage_error liftoff $RC; fi
            conda deactivate

            echo "$SEP"
            echo "Reference species: $REFERENCE_SPECIES - Target species: $TARGET_SPECIES - Getting data of target GFF file ..."
            /usr/bin/time \
                get-liftoff-gff-data.py \
                    --rspecies=$REFERENCE_SPECIES \
                    --tspecies=$TARGET_SPECIES \
                    --gff=$TARGET_GFF_PATH \
                    --gene-file=$GFF_GENE_DATA_PATH \
                    --cds-file=$GFF_CDS_DATA_PATH \
                    --verbose=N \
                    --trace=N \
                    --tvi=NONE
            RC=$?
            if [ $RC -ne 0 ]; then manage_error get-liftoff-gff-data.py $RC; fi

            echo "$SEP"
            echo "Reference species: $REFERENCE_SPECIES - Target species: $TARGET_SPECIES - Loading data of target GFF file in the database ..."
            /usr/bin/time \
                load-liftoff-gff-data.py \
                    --db=$COMPARATIVE_GENOMICS_DB_PATH \
                    --rspecies=$REFERENCE_SPECIES \
                    --tspecies=$TARGET_SPECIES \
                    --gene-file=$GFF_GENE_DATA_PATH \
                    --cds-file=$GFF_CDS_DATA_PATH \
                    --unmapped_file=$UNMAPPED_FEATURES_PATH \
                    --verbose=N  \
                    --trace=N
            RC=$?
            if [ $RC -ne 0 ]; then manage_error load-liftoff-gff-data.py $RC; fi

        done

    done

}

#-------------------------------------------------------------------------------

function get_cleaned_gff_data
{

    for REFERENCE_SPECIES in "${REFERENCE_SPECIES_LIST[@]}"; do

        CLEANED_GFF_PATH=$CLUSTERED_GENOME_FEATURES_DIR/$REFERENCE_SPECIES/$REFERENCE_SPECIES-without-redundancies.gff
        UNMAPPED_FEATURES_PATH=$COMPARATIVE_GENOMICS_TEMP_DIR/$REFERENCE_SPECIES-unmapped.txt
        touch $UNMAPPED_FEATURES_PATH
        GFF_GENE_DATA_PATH=$COMPARATIVE_GENOMICS_TEMP_DIR/$REFERENCE_SPECIES-gff-gene-data.csv
        GFF_CDS_DATA_PATH=$COMPARATIVE_GENOMICS_TEMP_DIR/$REFERENCE_SPECIES-gff-cds-data.csv

        echo "$SEP"
        echo "Reference species: $REFERENCE_SPECIES - Getting data of target GFF file ..."
        /usr/bin/time \
            get-liftoff-gff-data.py \
                --rspecies=$REFERENCE_SPECIES \
                --tspecies=NA \
                --gff=$CLEANED_GFF_PATH \
                --gene-file=$GFF_GENE_DATA_PATH \
                --cds-file=$GFF_CDS_DATA_PATH \
                --verbose=N \
                --trace=N \
                --tvi=NONE
        RC=$?
        if [ $RC -ne 0 ]; then manage_error get-liftoff-gff-data.py $RC; fi

        echo "$SEP"
        echo "Reference species: $REFERENCE_SPECIES - Loading data of target GFF file in the database ..."
        /usr/bin/time \
            load-liftoff-gff-data.py \
                --db=$COMPARATIVE_GENOMICS_DB_PATH \
                --rspecies=$REFERENCE_SPECIES \
                --tspecies=NA \
                --gene-file=$GFF_GENE_DATA_PATH \
                --cds-file=$GFF_CDS_DATA_PATH \
                --unmapped_file=$UNMAPPED_FEATURES_PATH \
                --verbose=N  \
                --trace=N
        RC=$?
        if [ $RC -ne 0 ]; then manage_error load-liftoff-gff-data.py $RC; fi

    done

}

#-------------------------------------------------------------------------------

function get_cleaned_genome_relationships
{

    echo "$SEP"
    echo "Getting relationships of Quercus species genomes ..."
    /usr/bin/time \
        get-liftoff-genome-relationships.py \
            --db=$COMPARATIVE_GENOMICS_DB_PATH \
            --ref_sp_list=$REFERENCE_SPECIES_LIST_TXT \
            --tar_sp_list=NA \
            --map_gene_file=$MAP_GENE_PATH \
            --map_codgene_file=$MAP_CODGENE_PATH \
            --map_prot_file=$MAP_PROT_PATH \
            --verbose=N  \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error gffcompare $RC; fi

}

#-------------------------------------------------------------------------------

function get_liftoff_genome_relationships
{

    echo "$SEP"
    echo "Getting relationships between Quercus species genomes and genomes of related species..."
    /usr/bin/time \
        get-liftoff-genome-relationships.py \
            --db=$COMPARATIVE_GENOMICS_DB_PATH \
            --ref_sp_list=$REFERENCE_SPECIES_LIST_TXT \
            --tar_sp_list=$TARGET_SPECIES_LIST_TXT \
            --map_gene_file=$MAP_GENE_PATH \
            --map_codgene_file=$MAP_CODGENE_PATH \
            --map_prot_file=$MAP_PROT_PATH \
            --verbose=N  \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error gffcompare $RC; fi

}

#-------------------------------------------------------------------------------

function get_liftoff_homologous_proteins
{

    for REFERENCE_SPECIES in "${REFERENCE_SPECIES_LIST[@]}"; do

        for TARGET_SPECIES in "${TARGET_SPECIES_LIST[@]}"; do

            if [[ "$REFERENCE_SPECIES" != "$TARGET_SPECIES" ]]; then

                echo "$SEP"
                echo "Reference species: $REFERENCE_SPECIES - Target species: $TARGET_SPECIES - Getting homologous proteins ..."
                /usr/bin/time \
                    get-liftoff-homologous-proteins.py \
                        --db=$COMPARATIVE_GENOMICS_DB_PATH \
                        --ref_sp=$REFERENCE_SPECIES \
                        --tar_sp=$TARGET_SPECIES \
                        --map_prot_file=$MAP_PROT_PATH \
                        --threshold=0 \
                        --verbose=N \
                        --trace=N \
                        --tpi=NONE
                RC=$?
                if [ $RC -ne 0 ]; then manage_error get-liftoff-gff-data.py $RC; fi

            fi

        done

    done

}

#-------------------------------------------------------------------------------

function get_homology_relationships
{

    for REFERENCE_SPECIES in "${REFERENCE_SPECIES_LIST[@]}"; do

        REVIEWED_TARGET_SPECIES_LIST=()
        FOUND=0
        for ITEM in "${TARGET_SPECIES_LIST[@]}"; do
            if [[ "$ITEM" != "$REFERENCE_SPECIES" ]]; then
                REVIEWED_TARGET_SPECIES_LIST+=("$ITEM")
            fi
        done

        IFS=,
        REVIEWED_TARGET_SPECIES_LIST_TEXT="${REVIEWED_TARGET_SPECIES_LIST[*]}"
        unset IFS

        echo "$SEP"
        echo "Reference species: $REFERENCE_SPECIES - Getting homology relationships ..."
        /usr/bin/time \
            get-homology-relationships.py \
                --db=$COMPARATIVE_GENOMICS_DB_PATH \
                --ref_sp=$REFERENCE_SPECIES \
                --tar_sp_list=$REVIEWED_TARGET_SPECIES_LIST_TEXT \
                --homology_file=$HOMOLOGY_RELATIONSHIPS_DIR/$REFERENCE_SPECIES-homology-relationships.csv \
                --verbose=N \
                --trace=N \
                --tpi=NONE
        RC=$?
        if [ $RC -ne 0 ]; then manage_error get-homology-relationships.py $RC; fi
        echo 'The file with homology relationships is created.'

    done

    echo "$SEP"
    echo "Merging homology relationships files ..."
    /usr/bin/time \
        merge-homology-relationships.py \
            --indir=$HOMOLOGY_RELATIONSHIPS_DIR \
            --pattern=.*-homology-relationships.csv \
            --out=$HOMOLOGY_RELATIONSHIPS_DIR/Quercus-homology-relationships-merged.csv \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error merge-homology-relationships.py $RC; fi
    echo 'The file merged is created.'

}

#-------------------------------------------------------------------------------

function delete_genome_index_files
{

    echo "$SEP"
    echo 'Deleting genome index files ...'
    cd $OUTPUT_DIR
    /usr/bin/time \
        rm \
            -f \
            $DB_NAME/*.fai \
            $DB_NAME/*.mmi
    RC=$?
    if [ $RC -ne 0 ]; then manage_error zip $RC; fi
    echo 'Database is compressed.'

}

#-------------------------------------------------------------------------------

function calculate_quercustoa_db_stats
{

    echo "$SEP"
    echo 'Calculating statistics of quercusTOA database ...'
    /usr/bin/time \
        calculate-quercustoadb-stats.py \
            --db=$FUNCTIONAL_ANNOTATIONS_DB_PATH \
            --stats=$STATS_PATH \
            --noannot=$NOANNOT_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error calculate-quercustoadb-stats.py $RC; fi
    echo 'Stats are calculated.'

}

#-------------------------------------------------------------------------------

function delete_genome_index_files
{

    echo "$SEP"
    echo 'Deleting genome index files ...'
    cd $OUTPUT_DIR
    /usr/bin/time \
        rm \
            -f \
            $DB_NAME/*.fai \
            $DB_NAME/*.mmi
    RC=$?
    if [ $RC -ne 0 ]; then manage_error rm $RC; fi
    echo 'Database is compressed.'

}

#-------------------------------------------------------------------------------

function compress_quercustoa_db
{

    echo "$SEP"
    echo 'Compressing quercusTOA database ...'
    cd $OUTPUT_DIR
    zip -r quercusTOA-db.zip quercusTOA-db -x "quercusTOA-db/functional-annotations-temp/*" "quercusTOA-db/comparative-genomics-temp/*"
    # /usr/bin/time \
    #     zip \
    #         -r \
    #         $DB_NAME.zip \
    #         $DB_NAME \
    #         -x "$DB_NAME/$(basename "$FUNCTIONAL_ANNOTATIONS_TEMP_DIR")/*" \ 
    #         -x "$DB_NAME/$(basename "$FUNCTIONAL_ANNOTATIONS_TEMP_DIR")/**" \ 
    #         -x "$DB_NAME/$(basename "$COMPARATIVE_GENOMICS_TEMP_DIR")/*" \
    #         -x "$DB_NAME/$(basename "$COMPARATIVE_GENOMICS_TEMP_DIR")/**"
    RC=$?
    if [ $RC -ne 0 ]; then manage_error zip $RC; fi
    echo 'Database is compressed.'

}

#-------------------------------------------------------------------------------

function calculate_duration
{

    DURATION=`expr $END_DATETIME - $INIT_DATETIME`
    HH=`expr $DURATION / 3600`
    MM=`expr $DURATION % 3600 / 60`
    SS=`expr $DURATION % 60`
    FORMATTED_DURATION=`printf "%03d:%02d:%02d\n" $HH $MM $SS`

}

#-------------------------------------------------------------------------------

function end
{

    END_DATETIME=`date +%s`
    FORMATTED_END_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    calculate_duration
    echo "$SEP"
    echo "Script ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION)."
    echo "$SEP"
    exit 0

}

#-------------------------------------------------------------------------------

function manage_error
{

    END_DATETIME=`date +%s`
    FORMATTED_END_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    calculate_duration
    echo "$SEP"
    echo "ERROR: $1 returned error $2"
    echo "Script ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION)."
    echo "$SEP"
    exit 3

}

#-------------------------------------------------------------------------------

init
create_directories
create_databases
# *** sequences step ***
download_genome_sequences
download_protein_sequences
load_species_sequences
download_tair10_sequences
download_lncrna_sequences
# *** functional annotation step ***
download_taxonomy_data
cluster_protein_sequences
split_protein_clusters
load_protein_clusters
align_protein_clusters
calculate_protein_clusters_identity
calculate_consensus_seqs
unify_consensus_seqs
download_busco_dataset
assess_consensus_seqs
build_consensus_blast_db
build_consensus_diamond_db
run_interscanpro_analysis
load_interproscan_annotations
run_eggnog_mapper_analysis
load_emapper_annotations
build_tair10_blast_db
align_consensus_seqs_2_tair10_blast_db
load_tair10_info
load_tair10_orthologs
download_gene_ontology
load_gene_ontology
build_lncrna_blast_db
# *** comparative genomics step ***
cluster_genome_features
run_genome_comparative
get_cleaned_gff_data
get_cleaned_genome_relationships
get_liftoff_genome_relationships
get_liftoff_homologous_proteins
get_homology_relationships
# ***
calculate_quercustoa_db_stats
delete_genome_index_files
compress_quercustoa_db
end

#-------------------------------------------------------------------------------
