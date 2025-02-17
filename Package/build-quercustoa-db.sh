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

# AWS machine type: r5.4xlarge (vCPUs: 16 - Memory: 128 GiB).

#-------------------------------------------------------------------------------

# Software installation.

# Miniforge3
# ==========

#    $ cd /ngscloud2/apps
#    $ wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
#    $ [rm -fr Miniforge3]
#    $ chmod u+x Miniforge3-Linux-x86_64.sh
#    $ ./Miniforge3-Linux-x86_64.sh -b -p Miniforge3
#    $ rm Miniforge3-Linux-x86_64.sh

#    $ Miniforge3/condabin/conda init bash   (reinicializar la consola)

#    $ export MAMBA_ROOT_PREFIX=/ngscloud2/apps/Miniforge3

#    $ conda config --add channels bioconda
#    $ conda config --add channels conda-forge
#    $ conda config --set channel_priority strict

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
#    $ mamba install --yes --name base plotyy
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
#    $ [OLD_VERSION=5.71-102.0]
#    $ NEW_VERSION=5.72-103.0
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
#        (58): -XX:ParallelGCThreads=8   --->   -XX:ParallelGCThreads=16
#        (59): -Xms2028M -Xmx9216M       --->   -Xms64G -Xmx64G

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

if [ "$ENVIRONMENT" = "$ENV_AWS" ]; then

    source /ngscloud2/apps/Miniconda3/envs/mmseqs2/util/bash-completion.sh

    NGSHELPER_DIR=/ngscloud2/apps/NGShelper
    MMSEQS2_DIR=/ngscloud2/apps/Miniconda3/envs/mmseqs2/bin
    INTERPROSCAN_DIR=/ngscloud2/apps/InterProScan
    OUTPUT_DIR=/ngscloud2/quercustoa

    PROTEIN_FASTA_FILE=$CLADE-protein-sequences.fasta

    THREADS=16

elif [ "$ENVIRONMENT" = "$ENV_LOCAL" ]; then

    source $BIOCONDA/mmseqs2/util/bash-completion.sh

    NGSHELPER_DIR=$NGSHELPER
    MMSEQS2_DIR=$BIOCONDA/mmseqs2/bin
    INTERPROSCAN_DIR=$APPS/InterProScan
    OUTPUT_DIR=$QUERCUSTOA/output

    PROTEIN_FASTA_FILE=$CLADE-protein-sequences-seq1000.fasta

    THREADS=4

else
    echo 'Environment error'; exit 3
fi

DB_NAME=quercusTOA-db
DB_DIR=$OUTPUT_DIR/$DB_NAME
TEMP_DIR=$OUTPUT_DIR/$DB_NAME/temp
QUERCUSTOA_DB_ZIP=$DB_NAME.zip
OUTPUT_PREFIX=$TEMP_DIR/$CLADE-mmseqs2
CLUSTER_DIR=$TEMP_DIR/clusters
DB_FILE=$DB_NAME.db
DB_PATH=$DB_DIR/$DB_FILE
PROTEIN_FASTA_PATH=$TEMP_DIR/$PROTEIN_FASTA_FILE
ALLSEQS_FILE=$CLADE-mmseqs2_all_seqs.fasta
ALLSEQS_PATH=$TEMP_DIR/$ALLSEQS_FILE
RELATIONSHIP_FILE=$CLADE-relationships.csv
RELATIONSHIP_PATH=$TEMP_DIR/$RELATIONSHIP_FILE
IDENTITIES_FILE=$CLADE-identities.csv
IDENTITIES_PATH=$TEMP_DIR/$IDENTITIES_FILE
CONSEQS_PREFIX=$CLADE-consensus
CONSEQS_FILE=$CONSEQS_PREFIX-seqs.fasta
CONSEQS_PATH=$TEMP_DIR/$CONSEQS_FILE
CONSEQS_BLAST_DB_NAME=$CONSEQS_PREFIX-blastplus-db
CONSEQS_BLAST_DB_DIR=$DB_DIR/$CONSEQS_PREFIX-blastplus-db
CONSEQS_BLAST_DB_PATH=$CONSEQS_BLAST_DB_DIR/$CONSEQS_BLAST_DB_NAME
CONSEQS_DIAMOND_DB_NAME=$CONSEQS_PREFIX-diamond-db
CONSEQS_DIAMOND_DB_DIR=$DB_DIR/$CONSEQS_PREFIX-diamond-db
CONSEQS_DIAMOND_DB_PATH=$CONSEQS_DIAMOND_DB_DIR/$CONSEQS_DIAMOND_DB_NAME
INTERPRO_OUPUT=$TEMP_DIR/$CONSEQS_PREFIX-seqs.fasta.tsv
INTERPRO_ANNOTATIONS_PATH=$TEMP_DIR/$CONSEQS_PREFIX-annotations-interpro.tsv
EMAPPER_OUPUT=$TEMP_DIR/$CONSEQS_PREFIX.emapper.annotations
EMAPPER_ANNOTATIONS_PATH=$TEMP_DIR/$CONSEQS_PREFIX-annotations-emapper.tsv
ANNOTATIONS_FILE=$CONSEQS_PREFIX-seqs-annotations.csv
STATS_FILE=$DB_NAME-stats.ini
STATS_PATH=$DB_DIR/$STATS_FILE
NOANNOT_FILE=$DB_NAME-noannot.csv
# -- NOANNOT_PATH=$TEMP_DIR/$NOANNOT_FILE
NOANNOT_PATH=NONE

# NCBI Genome
# Quercus agrifolia
GENOME_QUERCUS_ALBA_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/029/955/455/GCA_029955455.1_dhQueAgri1.0.hap1/GCA_029955455.1_dhQueAgri1.0.hap1_genomic.fna.gz
GENOME_QUERCUS_ALBA_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_ALBA_GENOME_URL")
GENOME_QUERCUS_ALBA_GFF_URL=
GENOME_QUERCUS_ALBA_GFF_PATH=
GENOME_QUERCUS_ALBA_PROTEIN_URL=
GENOME_QUERCUS_ALBA_PROTEIN_PATH=
# Quercus alba
GENOME_QUERCUS_ALBA_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/036/321/655/GCA_036321655.1_ASM3632165v1/GCA_036321655.1_ASM3632165v1_genomic.fna.gz
GENOME_QUERCUS_ALBA_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_ALBA_GENOME_URL")
GENOME_QUERCUS_ALBA_GFF_URL=
GENOME_QUERCUS_ALBA_GFF_PATH=
GENOME_QUERCUS_ALBA_PROTEIN_URL=
GENOME_QUERCUS_ALBA_PROTEIN_PATH=
# Quercus dentata
GENOME_QUERCUS_DENTATA_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/028/216/015/GCA_028216015.1_ASM2821601v1/GCA_028216015.1_ASM2821601v1_genomic.fna.gz
GENOME_QUERCUS_DENTATA_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_DENTATA_GENOME_URL")
GENOME_QUERCUS_DENTATA_GFF_URL=
GENOME_QUERCUS_DENTATA_GFF_PATH=
GENOME_QUERCUS_DENTATA_PROTEIN_URL=
GENOME_QUERCUS_DENTATA_PROTEIN_PATH=
# Quercus gilva
GENOME_QUERCUS_GILVA_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/023/621/385/GCA_023621385.1_ASM2362138v1/GCA_023621385.1_ASM2362138v1_genomic.fna.gz
GENOME_QUERCUS_GILVA_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_GILVA_GENOME_URL")
GENOME_QUERCUS_GILVA_GFF_URL=
GENOME_QUERCUS_GILVA_GFF_PATH=
GENOME_QUERCUS_GILVA_PROTEIN_URL=
GENOME_QUERCUS_GILVA_PROTEIN_PATH=
# Quercus glauca
GENOME_QUERCUS_GLAUCA_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/023/736/055/GCA_023736055.1_g3h1/GCA_023736055.1_g3h1_genomic.fna.gz
GENOME_QUERCUS_GLAUCA_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_GLAUCA_GENOME_URL")
GENOME_QUERCUS_GLAUCA_GFF_URL=
GENOME_QUERCUS_GLAUCA_GFF_PATH=
GENOME_QUERCUS_GLAUCA_PROTEIN_URL=
GENOME_QUERCUS_GLAUCA_PROTEIN_PATH=
# Quercus ilex
GENOME_QUERCUS_ILEX_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/964/341/355/GCA_964341355.1_dhQueIlex1.hap2.1/GCA_964341355.1_dhQueIlex1.hap2.1_genomic.fna.gz
GENOME_QUERCUS_ILEX_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_ILEX_GENOME_URL")
GENOME_QUERCUS_ILEX_GFF_URL=
GENOME_QUERCUS_ILEX_GFF_PATH=
GENOME_QUERCUS_ILEX_PROTEIN_URL=
GENOME_QUERCUS_ILEX_PROTEIN_PATH=
# Quercus lobata
GENOME_QUERCUS_LOBATA_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/001/633/185/GCF_001633185.2_ValleyOak3.2/GCF_001633185.2_ValleyOak3.2_genomic.fna.gz
GENOME_QUERCUS_LOBATA_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_LOBATA_GENOME_URL")
GENOME_QUERCUS_LOBATA_GFF_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/001/633/185/GCF_001633185.2_ValleyOak3.2/GCF_001633185.2_ValleyOak3.2_genomic.gff.gz
GENOME_QUERCUS_LOBATA_GFF_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_LOBATA_GFF_URL")
GENOME_QUERCUS_LOBATA_PROTEIN_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/001/633/185/GCF_001633185.2_ValleyOak3.2/GCF_001633185.2_ValleyOak3.2_protein.faa.gz
GENOME_QUERCUS_LOBATA_PROTEIN_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_LOBATA_PROTEIN_URL")
# Quercus mongolica
GENOME_QUERCUS_MONGOLICA_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/011/696/235/GCA_011696235.1_ASM1169623v1/GCA_011696235.1_ASM1169623v1_genomic.fna.gz
GENOME_QUERCUS_MONGOLICA_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_MONGOLICA_GENOME_URL")
GENOME_QUERCUS_MONGOLICA_GFF_URL=
GENOME_QUERCUS_MONGOLICA_GFF_PATH=
GENOME_QUERCUS_MONGOLICA_PROTEIN_URL=
GENOME_QUERCUS_MONGOLICA_PROTEIN_PATH=
# Quercus petraea
GENOME_QUERCUS_PETRAEA_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/964/102/825/GCA_964102825.1_dhQuePetr1.hap1.1/GCA_964102825.1_dhQuePetr1.hap1.1_genomic.fna.gz
GENOME_QUERCUS_PETRAEA_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_PETRAEA_GENOME_URL")
GENOME_QUERCUS_PETRAEA_GFF_URL=
GENOME_QUERCUS_PETRAEA_GFF_PATH=
GENOME_QUERCUS_PETRAEA_PROTEIN_URL=
GENOME_QUERCUS_PETRAEA_PROTEIN_PATH=
# Quercus robur
GENOME_QUERCUS_ROBUR_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/932/294/415/GCF_932294415.1_dhQueRobu3.1/GCF_932294415.1_dhQueRobu3.1_genomic.fna.gz
GENOME_QUERCUS_ROBUR_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_ROBUR_GENOME_URL")
GENOME_QUERCUS_ROBUR_GFF_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/932/294/415/GCF_932294415.1_dhQueRobu3.1/GCF_932294415.1_dhQueRobu3.1_genomic.gff.gz
GENOME_QUERCUS_ROBUR_GFF_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_ROBUR_GFF_URL")
GENOME_QUERCUS_ROBUR_PROTEIN_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/932/294/415/GCF_932294415.1_dhQueRobu3.1/GCF_932294415.1_dhQueRobu3.1_protein.faa.gz
GENOME_QUERCUS_ROBUR_PROTEIN_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_ROBUR_PROTEIN_URL")
# Quercus rubra
GENOME_QUERCUS_RUBRA_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/035/136/125/GCA_035136125.1_Qrubra_687_v2.0/GCA_035136125.1_Qrubra_687_v2.0_genomic.fna.gz
GENOME_QUERCUS_RUBRA_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_RUBRA_GENOME_URL")
GENOME_QUERCUS_RUBRA_GFF_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/035/136/125/GCA_035136125.1_Qrubra_687_v2.0/GCA_035136125.1_Qrubra_687_v2.0_genomic.gff.gz
GENOME_QUERCUS_RUBRA_GFF_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_RUBRA_GFF_URL")
GENOME_QUERCUS_RUBRA_PROTEIN_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/035/136/125/GCA_035136125.1_Qrubra_687_v2.0/GCA_035136125.1_Qrubra_687_v2.0_protein.faa.gz
GENOME_QUERCUS_RUBRA_PROTEIN_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_RUBRA_PROTEIN_URL")
# Quercus suber
GENOME_QUERCUS_SUBER_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/906/115/GCF_002906115.3_Cork_oak_2.0/GCF_002906115.3_Cork_oak_2.0_genomic.fna.gz
GENOME_QUERCUS_SUBER_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_SUBER_GENOME_URL")
GENOME_QUERCUS_SUBER_GFF_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/906/115/GCF_002906115.3_Cork_oak_2.0/GCF_002906115.3_Cork_oak_2.0_genomic.gff.gz
GENOME_QUERCUS_SUBER_GFF_PATH=$TEMP_DIR/$(basename "$rGENOME_QUERCUS_SUBER_GFF_URL")
GENOME_QUERCUS_SUBER_PROTEIN_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/906/115/GCF_002906115.3_Cork_oak_2.0/GCF_002906115.3_Cork_oak_2.0_protein.faa.gz
GENOME_QUERCUS_SUBER_PROTEIN_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_SUBER_PROTEIN_URL")
# Quercus variabilis
GENOME_QUERCUS_VARIABILIS_GENOME_URL=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/030/445/155/GCA_030445155.1_ASM3044515v1/GCA_030445155.1_ASM3044515v1_genomic.fna.gz
GENOME_QUERCUS_VARIABILIS_GENOME_PATH=$TEMP_DIR/$(basename "$GENOME_QUERCUS_VARIABILIS_GENOME_URL")
GENOME_QUERCUS_VARIABILIS_GFF_URL=
GENOME_QUERCUS_VARIABILIS_GFF_PATH=
GENOME_QUERCUS_VARIABILIS_PROTEIN_URL=
GENOME_QUERCUS_VARIABILIS_PROTEIN_PATH=

# CNCB - NGDC
# Quercus acutissima
NGDC_QUERCUS_ACUTISSIMA_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_acutissima_Quercus_a_v1.0_GWHBGBO00000000/GWHBGBO00000000.genome.fasta.gz
NGDC_QUERCUS_ACUTISSIMA_GENOME_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_ACUTISSIMA_GENOME_URL")
NGDC_QUERCUS_ACUTISSIMAA_GFF_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_acutissima_Quercus_a_v1.0_GWHBGBO00000000/GWHBGBO00000000.gff.gz
NGDC_QUERCUS_ACUTISSIMA_GFF_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_ACUTISSIMAA_GFF_URL")
NGDC_QUERCUS_ACUTISSIMA_PROTEIN_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_acutissima_Quercus_a_v1.0_GWHBGBO00000000/GWHBGBO00000000.Protein.faa.gz
NGDC_QUERCUS_ACUTISSIMA_PROTEIN_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_ACUTISSIMA_PROTEIN_URL")
# Quercus dentata
NGDC_QUERCUS_DENTATA_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_dentata_NA_GWHBRAD00000000/GWHBRAD00000000.genome.fasta.gz
NGDC_QUERCUS_DENTATA_GENOME_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_DENTATA_GENOME_URL")
NGDC_QUERCUS_DENTATA_GFF_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_dentata_NA_GWHBRAD00000000/GWHBRAD00000000.gff.gz
NGDC_QUERCUS_DENTATA_GFF_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_DENTATA_GFF_URL")
NGDC_QUERCUS_DENTATA_PROTEIN_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_dentata_NA_GWHBRAD00000000/GWHBRAD00000000.Protein.faa.gz
NGDC_QUERCUS_DENTATA_PROTEIN_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_DENTATA_PROTEIN_URL")
# Quercus glauca
NGDC_QUERCUS_GLAUCA_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_glauca_chr_GWHDTWU00000000/GWHDTWU00000000.genome.fasta.gz
NGDC_QUERCUS_GLAUCA_GENOME_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_GLAUCA_GENOME_URL")
NGDC_QUERCUS_GLAUCA_GFF_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_glauca_chr_GWHDTWU00000000/GWHDTWU00000000.gff.gz
NGDC_QUERCUS_GLAUCA_GFF_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_GLAUCA_GFF_URL")
NGDC_QUERCUS_GLAUCA_PROTEIN_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_glauca_chr_GWHDTWU00000000/GWHDTWU00000000.Protein.faa.gz
NGDC_QUERCUS_GLAUCA_PROTEIN_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_GLAUCA_PROTEIN_URL")
# Quercus longispica
NGDC_QUERCUS_LONGISPICA_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_longispica_LKM1_GWHESEV00000000/GWHESEV00000000.genome.fasta.gz
NGDC_QUERCUS_LONGISPICA_GENOME_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_LONGISPICA_GENOME_URL")
NGDC_QUERCUS_LONGISPICA_GFF_URL=
NGDC_QUERCUS_LONGISPICA_GFF_PATH=
NGDC_QUERCUS_LONGISPICA_PROTEIN_URL=
NGDC_QUERCUS_LONGISPICA_PROTEIN_PATH=
# Quercus rex
NGDC_QUERCUS_REX_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_rex_Quercus_rex_GWHCBIV00000000/GWHCBIV00000000.genome.fasta.gz
NGDC_QUERCUS_REX_GENOME_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_REX_GENOME_URL")
NGDC_QUERCUS_REX_GFF_URL=
NGDC_QUERCUS_REX_GFF_PATH=
NGDC_QUERCUS_REX_PROTEIN_URL=
NGDC_QUERCUS_REX_PROTEIN_PATH=
# Quercus sichourensis
NGDC_QUERCUS_SICHOURENSIS_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_sichourensis_Quercus_sichourensis_GWHCBIW00000000/GWHCBIW00000000.genome.fasta.gz
NGDC_QUERCUS_SICHOURENSIS_GENOME_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_SICHOURENSIS_GENOME_URL")
NGDC_QUERCUS_SICHOURENSIS_GFF_URL=
NGDC_QUERCUS_SICHOURENSIS_GFF_PATH=
NGDC_QUERCUS_SICHOURENSIS_PROTEIN_URL=
NGDC_QUERCUS_SICHOURENSIS_PROTEIN_PATH=
# Quercus variabilis
NGDC_QUERCUS_VARIABILIS_GENOME_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_variabilis_QuvarV2_GWHBQTN00000000/GWHBQTN00000000.genome.fasta.gz
NGDC_QUERCUS_VARIABILIS_GENOME_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_VARIABILIS_GENOME_URL")
NGDC_QUERCUS_VARIABILIS_GFF_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_variabilis_QuvarV2_GWHBQTN00000000/GWHBQTN00000000.gff.gz
NGDC_QUERCUS_VARIABILIS_GFF_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_VARIABILIS_GFF_URL")
NGDC_QUERCUS_VARIABILIS_PROTEIN_URL=https://download.cncb.ac.cn/gwh/Plants/Quercus_variabilis_QuvarV2_GWHBQTN00000000/GWHBQTN00000000.Protein.faa.gz
NGDC_QUERCUS_VARIABILIS_PROTEIN_PATH=$TEMP_DIR/$(basename "$NGDC_QUERCUS_VARIABILIS_PROTEIN_URL")

# Reference genome
REFERENCE_GENOME_URL=$GENOME_QUERCUS_LOBATA_GENOME_URL
REFERENCE_GENOME_PATH=$GENOME_QUERCUS_LOBATA_GENOME_PATH
REFERENCE_GFF_URL=$GENOME_QUERCUS_LOBATA_GFF_URL
REFERENCE_GFF_PATH=$GENOME_QUERCUS_LOBATA_GFF_PATH

# Protein source
PROTEIN_SOURCE_1='NCBI-PROTEINS-DATABASE'
PROTEIN_SOURCE_2='GENOMIC-PROTEINS'
PROTEIN_SOURCE=$PROTEIN_SOURCE_2

# NCBI Taxonomy
TAXONOMY_TAXDMP_URL=ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip
TAXONOMY_TAXDMP_PATH=$TEMP_DIR/taxdmp.zip
TAXONOMY_TAXONNAMES_PATH=$TEMP_DIR/names.dmp

# BUSCO Embryophyta dataset
BUSCO_DATASET=embryophyta_odb10
BUSCO_DATASET_URL=https://busco-data.ezlab.org/v5/data/lineages/embryophyta_odb10.2024-01-08.tar.gz
BUSCO_DATASET_PATH=$TEMP_DIR/$BUSCO_DATASET.tar.gz
BUSCO_DATASET_DIR=$TEMP_DIR/$BUSCO_DATASET
BUSCO_ASSESSMENT_PATTERN=busco-assessment
BUSCO_ASSESSMENT_FILE=short_summary.specific.$BUSCO_DATASET.$BUSCO_ASSESSMENT_PATTERN.txt
BUSCO_ASSESSMENT_PATH=$TEMP_DIR/$BUSCO_ASSESSMENT_PATTERN/$BUSCO_ASSESSMENT_FILE
BUSCO_ASSESSMENT_DATA_PATH=$DB_DIR/$BUSCO_ASSESSMENT_PATTERN.txt

# TAIR10
TAIR10_PREFIX=TAIR10
# -- TAIR10_PEP_URL=https://www.arabidopsis.org/download_files/Proteins/TAIR10_protein_lists/TAIR10_pep_20101214
TAIR10_PEP_URL=https://www.arabidopsis.org/api/download-files/download?filePath=Proteins/TAIR10_protein_lists/TAIR10_pep_20101214
TAIR10_PEP_FILE=$TAIR10_PREFIX-protein-sequences.fasta
TAIR10_PEP_PATH=$TEMP_DIR/$TAIR10_PEP_FILE
TAIR10_BLAST_DB_NAME=$TAIR10_PREFIX-blastplus-db
TAIR10_BLAST_DB_DIR=$TEMP_DIR/$TAIR10_PREFIX-blastplus-db
TAIR10_BLAST_DB_PATH=$TAIR10_BLAST_DB_DIR/$TAIR10_BLAST_DB_NAME
TAIR10_CONSEQS_ALIGNMENT_FILE=$CONSEQS_PREFIX-tair10-alignments.csv
TAIR10_CONSEQS_ALIGNMENT_PATH=$TEMP_DIR/$TAIR10_CONSEQS_ALIGNMENT_FILE

# Gene Ontology
GO_ONTOLOGY_URL=http://purl.obolibrary.org/obo/go.obo
GO_ONTOLOGY_FILE=$TEMP_DIR/go.obo

# CANTATA data
CANTATA_ARABIDOPSIS_THALIANA_FASTA_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Arabidopsis_thaliana_lncRNAs.fasta
CANTATA_ARABIDOPSIS_THALIANA_FASTA_PATH=$TEMP_DIR/Arabidopsis-thaliana-lncrnas.fasta
CANTATA_ARABIDOPSIS_THALIANA_GTF_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Arabidopsis_thaliana_lncRNAs.gtf
CANTATA_ARABIDOPSIS_THALIANA_GTF_PATH=$TEMP_DIR/Arabidopsis-thaliana-lncrnas.gtf
CANTATA_QUERCUS_LOBATA_FASTA_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Quercus_lobata_lncRNAs.fasta
CANTATA_QUERCUS_LOBATA_FASTA_PATH=$TEMP_DIR/Quercus-lobata-lncrnas.fasta
CANTATA_QUERCUS_LOBATA_GTF_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Quercus_lobata_lncRNAs.gtf
CANTATA_QUERCUS_LOBATA_GTF_PATH=$TEMP_DIR/Quercus-lobata-lncrnas.gtf
CANTATA_QUERCUS_SUBER_FASTA_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Quercus_suber_lncRNAs.fasta
CANTATA_QUERCUS_SUBER_FASTA_PATH=$TEMP_DIR/Quercus-suber-lncrnas.fasta
CANTATA_QUERCUS_SUBER_GTF_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Quercus_suber_lncRNAs.gtf
CANTATA_QUERCUS_SUBER_GTF_PATH=$TEMP_DIR/Quercus-suber-lncrnas.gtf
LNCRNAS_PREFIX=lncRNA
LNCRNAS_FILE=$LNCRNAS_PREFIX-seqs.fasta
LNCRNAS_PATH=$TEMP_DIR/$LNCRNAS_FILE
LNCRNAS_BLAST_DB_NAME=$LNCRNAS_PREFIX-blastplus-db
LNCRNAS_BLAST_DB_DIR=$DB_DIR/$LNCRNAS_PREFIX-blastplus-db
LNCRNAS_BLAST_DB_PATH=$LNCRNAS_BLAST_DB_DIR/$LNCRNAS_BLAST_DB_NAME

# MMseqs2 params
S=4.0        # s (sensitivity)
C=1.0        # c (list matches above this fraction of aligned -covered- residue)
CM=0         # cov-mode: 0 (coverage of query and target)
MSI=1.000    # min-seq-id
ST=2         # similarity-type: 2 (sequence identity)
TYPE=1       # dbtype: 1 (amino acid)

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
    if [ -d "$TEMP_DIR" ]; then rm -rf $TEMP_DIR; fi; mkdir --parents $TEMP_DIR 
    if [ -d "$CLUSTER_DIR" ]; then rm -rf $CLUSTER_DIR; fi; mkdir --parents $CLUSTER_DIR
    if [ -d "$CONSEQS_BLAST_DB_DIR" ]; then rm -rf $CONSEQS_BLAST_DB_DIR; fi; mkdir --parents $CONSEQS_BLAST_DB_DIR
    if [ -d "$CONSEQS_DIAMOND_DB_DIR" ]; then rm -rf $CONSEQS_DIAMOND_DB_DIR; fi; mkdir --parents $CONSEQS_DIAMOND_DB_DIR
    if [ -d "$LNCRNAS_BLAST_DB_DIR" ]; then rm -rf $LNCRNAS_BLAST_DB_DIR; fi; mkdir --parents $LNCRNAS_BLAST_DB_DIR
    echo 'Directories are created.'

}

#-------------------------------------------------------------------------------

function create_database
{

    echo "$SEP"
    echo 'Creating the quercusTOA database ...'
    /usr/bin/time \
        recreate-database.py \
            --db=$DB_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error recreate-database.py $RC; fi
    echo 'Database is created.'

}

#-------------------------------------------------------------------------------

function download_reference_genome
{

    echo "$SEP"
    echo 'Downloading and decompressing reference genome FASTA ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $REFERENCE_GENOME_PATH \
            $REFERENCE_GENOME_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    gzip -d $REFERENCE_GENOME_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error tar $RC; fi
    echo 'File is downloaded and decompressed.'

    echo "$SEP"
    echo 'Downloading and decompressing reference genome GFF3 ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $REFERENCE_GFF_PATH \
            $REFERENCE_GFF_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    gzip -d $REFERENCE_GFF_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error tar $RC; fi
    echo 'File is downloaded and decompressed.'

}

#-------------------------------------------------------------------------------

function download_protein_sequences
{

    if [ "$PROTEIN_SOURCE" = "$PROTEIN_SOURCE_1" ]; then

        echo "$SEP"
        echo "Downloading $CLADE protein sequences from NCBI protein database ..."
        if [ "$ENVIRONMENT" = "$ENV_AWS" ]; then
            source activate entrez-direct
            /usr/bin/time \
                esearch -db protein -query "$CLADE [Organism]" | efetch -format fasta >$PROTEIN_FASTA_PATH
            RC=$?
            if [ $RC -ne 0 ]; then manage_error esearch $RC; fi
            conda deactivate
        elif [ "$ENVIRONMENT" = "$ENV_LOCAL" ]; then
            cp /home/fmm/Documents/Trabajo/ProyectosVScode/quercusTOA/data/$PROTEIN_FASTA_FILE $TEMP_DIR
        else
            echo 'Environment error'; exit 3
        fi
        echo 'Sequences are downloaded.'

    elif [ "$PROTEIN_SOURCE" = "$PROTEIN_SOURCE_2" ]; then

        echo "$SEP"
        echo 'Downloading and decompressing Quercus lobata protein FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $GENOME_QUERCUS_LOBATA_PROTEIN_PATH \
                $GENOME_QUERCUS_LOBATA_PROTEIN_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $GENOME_QUERCUS_LOBATA_PROTEIN_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error tar $RC; fi
        echo 'File is downloaded and decompressed.'

        echo "$SEP"
        echo 'Downloading and decompressing Quercus robur protein FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $GENOME_QUERCUS_ROBUR_PROTEIN_PATH \
                $GENOME_QUERCUS_ROBUR_PROTEIN_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $GENOME_QUERCUS_ROBUR_PROTEIN_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error tar $RC; fi
        echo 'File is downloaded and decompressed.'

        echo "$SEP"
        echo 'Downloading and decompressing Quercus rubra protein FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $GENOME_QUERCUS_RUBRA_PROTEIN_PATH \
                $GENOME_QUERCUS_RUBRA_PROTEIN_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $GENOME_QUERCUS_RUBRA_PROTEIN_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error tar $RC; fi
        echo 'File is downloaded and decompressed.'

        echo "$SEP"
        echo 'Downloading and decompressing Quercus suber protein FASTA ...'
        /usr/bin/time \
            wget \
                --quiet \
                --output-document $GENOME_QUERCUS_SUBER_PROTEIN_PATH \
                $GENOME_QUERCUS_SUBER_PROTEIN_URL
        RC=$?
        if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        gzip -d $GENOME_QUERCUS_SUBER_PROTEIN_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error tar $RC; fi
        echo 'File is downloaded and decompressed.'

        # echo "$SEP"
        # echo 'Downloading and decompressing Quercus acutissima protein FASTA ...'
        # /usr/bin/time \
        #     wget \
        #         --quiet \
        #         --output-document $NGDC_QUERCUS_ACUTISSIMA_PROTEIN_PATH \
        #         $NGDC_QUERCUS_ACUTISSIMA_PROTEIN_URL
        # RC=$?
        # if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        # gzip -d $NGDC_QUERCUS_ACUTISSIMA_PROTEIN_PATH
        # RC=$?
        # if [ $RC -ne 0 ]; then manage_error tar $RC; fi
        # echo 'File is downloaded and decompressed.'

        # echo "$SEP"
        # echo 'Downloading and decompressing Quercus dentata protein FASTA ...'
        # /usr/bin/time \
        #     wget \
        #         --quiet \
        #         --output-document $NGDC_QUERCUS_DENTATA_PROTEIN_PATH \
        #         $NGDC_QUERCUS_DENTATA_PROTEIN_URL
        # RC=$?
        # if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        # gzip -d $NGDC_QUERCUS_DENTATA_PROTEIN_PATH
        # RC=$?
        # if [ $RC -ne 0 ]; then manage_error tar $RC; fi
        # echo 'File is downloaded and decompressed.'

        # echo "$SEP"
        # echo 'Downloading and decompressing Quercus glauca protein FASTA ...'
        # /usr/bin/time \
        #     wget \
        #         --quiet \
        #         --output-document $NGDC_QUERCUS_GLAUCA_PROTEIN_PATH \
        #         $NGDC_QUERCUS_GLAUCA_PROTEIN_URL
        # RC=$?
        # if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        # gzip -d $NGDC_QUERCUS_GLAUCA_PROTEIN_PATH
        # RC=$?
        # if [ $RC -ne 0 ]; then manage_error tar $RC; fi
        # echo 'File is downloaded and decompressed.'

        # echo "$SEP"
        # echo 'Downloading and decompressing Quercus variabilis protein FASTA ...'
        # /usr/bin/time \
        #     wget \
        #         --quiet \
        #         --output-document $NGDC_QUERCUS_VARIABILIS_PROTEIN_PATH \
        #         $NGDC_QUERCUS_VARIABILIS_PROTEIN_URL
        # RC=$?
        # if [ $RC -ne 0 ]; then manage_error wget $RC; fi
        # gzip -d $NGDC_QUERCUS_VARIABILIS_PROTEIN_PATH
        # RC=$?
        # if [ $RC -ne 0 ]; then manage_error tar $RC; fi
        # echo 'File is downloaded and decompressed.'

        # echo "$SEP"
        # echo 'Concating the protein FASTAs ...'
        # /usr/bin/time \
        #     cat \
        #         "${GENOME_QUERCUS_LOBATA_PROTEIN_PATH%.*}" \
        #         "${GENOME_QUERCUS_ROBUR_PROTEIN_PATH%.*}" \
        #         "${GENOME_QUERCUS_RUBRA_PROTEIN_PATH%.*}" \
        #         "${GENOME_QUERCUS_SUBER_PROTEIN_PATH%.*}" \
        #         "${NGDC_QUERCUS_ACUTISSIMA_PROTEIN_PATH%.*}" \
        #         "${NGDC_QUERCUS_DENTATA_PROTEIN_PATH%.*}" \
        #         "${NGDC_QUERCUS_GLAUCA_PROTEIN_PATH%.*}" \
        #         "${NGDC_QUERCUS_VARIABILIS_PROTEIN_PATH%.*}" \
        #         > $PROTEIN_FASTA_PATH
        # RC=$?
        # if [ $RC -ne 0 ]; then manage_error cat $RC; fi
        # echo 'Files are concated.'

        echo "$SEP"
        echo 'Concating the protein FASTAs ...'
        /usr/bin/time \
            cat \
                "${GENOME_QUERCUS_LOBATA_PROTEIN_PATH%.*}" \
                "${GENOME_QUERCUS_ROBUR_PROTEIN_PATH%.*}" \
                "${GENOME_QUERCUS_RUBRA_PROTEIN_PATH%.*}" \
                "${GENOME_QUERCUS_SUBER_PROTEIN_PATH%.*}" \
                > $PROTEIN_FASTA_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error cat $RC; fi
        echo 'Files are concated.'

    else
        echo 'Protein source error'; exit 3
    fi

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
    unzip -o -d $TEMP_DIR $TAXONOMY_TAXDMP_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error tar $RC; fi
    echo 'File is downloaded and decompressed.'

}

#-------------------------------------------------------------------------------

function cluster_sequences
{

    source activate mmseqs2

    echo "$SEP"
    echo 'Clustering sequences ...'
    /usr/bin/time \
        mmseqs \
            easy-cluster \
            $PROTEIN_FASTA_PATH \
            $OUTPUT_PREFIX \
            tmp \
            --threads $THREADS \
            -s $S \
            -c $C \
            --cov-mode $CM \
            --min-seq-id $MSI \
            --similarity-type $ST
    RC=$?
    if [ $RC -ne 0 ]; then manage_error mmseqs $RC; fi
    echo 'Sequences are clustered.'

    conda deactivate

}

#-------------------------------------------------------------------------------

function split_clusters
{

    echo "$SEP"
    echo 'Splitting clusters ...'
    /usr/bin/time \
        split-mmseqs2-clusters.py \
            --allseqs=$ALLSEQS_PATH \
            --relationships=$RELATIONSHIP_PATH \
            --outdir=$CLUSTER_DIR \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error split-mmseqs2-clusters.py $RC; fi
    echo 'Clusters are splitted.'

}

#-------------------------------------------------------------------------------

function load_cluster_sequence_relationships
{

    echo "$SEP"
    echo 'Loading cluster-sequence relationships into quercusTOA database ...'
    /usr/bin/time \
        load-mmseqs2-relationships.py \
            --db=$DB_PATH \
            --relationships=$RELATIONSHIP_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-mmseqs2-relationships.py $RC; fi
    echo 'Relationships are loaded.'

}

#-------------------------------------------------------------------------------

function align_clusters
{

    source activate $ALIGNER

    echo "$SEP"
    CLUSTERS_FILE_LIST=$CLUSTER_DIR/clusters-files.txt
    find $CLUSTER_DIR -type f -name cluster*.fasta > $CLUSTERS_FILE_LIST
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

function calculate_clusters_identity
{

    echo "$SEP"
    echo 'Calculating identity percentage of clusters ...'
    /usr/bin/time \
        calculate-alignment-identity.py \
            --indir=$CLUSTER_DIR \
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
    ALIGNED_CLUSTERS_FILE_LIST=$CLUSTER_DIR/aligned-clusters-files.txt
    find $CLUSTER_DIR -type f -name cluster*-$ALIGNER.fasta > $ALIGNED_CLUSTERS_FILE_LIST
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
            --indir=$CLUSTER_DIR \
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
    tar -xzvf $BUSCO_DATASET_PATH --directory=$TEMP_DIR
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
            --out_path=$TEMP_DIR \
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
            --output-dir $TEMP_DIR
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
            --db=$DB_PATH \
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
        /usr/bin/time \
        /usr/bin/time \
            # -- emapper.py \
            # --     --cpu $THREADS \
            # --     -i $CONSEQS_PATH \
            # --     --itype $EMAPPER_ITYPE \
            # --     -m $DIAMOND \
            # --     --dmnd_algo $EMAPPER_DMND_ALGO \
            # --     --sensmode $EMAPPER_SENSMODE \
            # --     --dmnd_iterate $EMAPPER_DMND_ITERATE \
            # --     --pident $EMAPPER_PIDENT \
            # --     --evalue $EMAPPER_EVALUE \
            # --     --query_cover $EMAPPER_QUERY_COVER \
            # --     --output_dir $TEMP_DIR \
            # --     --output $CONSEQS_PREFIX
            emapper.py \
                --cpu $THREADS \
                -i $CONSEQS_PATH \
                --itype $EMAPPER_ITYPE \
                -m $DIAMOND \
                --dmnd_algo $EMAPPER_DMND_ALGO \
                --sensmode $EMAPPER_SENSMODE \
                --dmnd_iterate $EMAPPER_DMND_ITERATE \
                --evalue $EMAPPER_EVALUE \
                --output_dir $TEMP_DIR \
                --output $CONSEQS_PREFIX
            RC=$?
        if [ $RC -ne 0 ]; then manage_error emapper.py $RC; fi
    elif [ "$EMAPPER_SEARCH_OPTION" = "$MMSEQS" ]; then
        /usr/bin/time \
        # -- emapper.py \
        # --     --cpu $THREADS \
        # --     -i $CONSEQS_PATH \
        # --     --itype $EMAPPER_ITYPE \
        # --     -m $MMSEQS \
        # --     --start_sens $EMAPPER_START_SENS \
        # --     --sens_steps $EMAPPER_SENS_STEPS \
        # --     --final_sens $EMAPPER_FINAL_SENS \
        # --     --pident $EMAPPER_PIDENT \
        # --     --evalue $EMAPPER_EVALUE \
        # --     --query_cover $EMAPPER_QUERY_COVER \
        # --     --output_dir $TEMP_DIR \
        # --     --output $CONSEQS_PREFIX
        emapper.py \
            --cpu $THREADS \
            -i $CONSEQS_PATH \
            --itype $EMAPPER_ITYPE \
            -m $MMSEQS \
            --start_sens $EMAPPER_START_SENS \
            --sens_steps $EMAPPER_SENS_STEPS \
            --final_sens $EMAPPER_FINAL_SENS \
            --evalue $EMAPPER_EVALUE \
            --output_dir $TEMP_DIR \
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
            --db=$DB_PATH \
            --annotations=$EMAPPER_ANNOTATIONS_PATH \
            --taxnames=$TAXONOMY_TAXONNAMES_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-interproscan-annotations.py $RC; fi
    echo 'Annotations are loaded.'

}

#-------------------------------------------------------------------------------

function download_tair10_sequences
{

    echo "$SEP"
    echo 'Downloading TAIR10 protein sequences ...'
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
            --db=$DB_PATH \
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
            --db=$DB_PATH \
            --ontology=$GO_ONTOLOGY_FILE \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-gene_ontology.py $RC; fi
    echo 'Gene Ontology are loaded.'

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
    echo 'Concating the lncRNA FASTAs ...'
    /usr/bin/time \
        cat \
            $CANTATA_ARABIDOPSIS_THALIANA_FASTA_PATH \
            $CANTATA_QUERCUS_LOBATA_FASTA_PATH \
            $CANTATA_QUERCUS_SUBER_FASTA_PATH \
            > $LNCRNAS_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error cat $RC; fi
    echo 'Files are concated.'

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

function calculate_quercustoa_db_stats
{

    echo "$SEP"
    echo 'Calculating stats of quercusTOA database ...'
    /usr/bin/time \
        calculate-quercustoadb-stats.py \
            --db=$DB_PATH \
            --stats=$STATS_PATH \
            --noannot=$NOANNOT_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error calculate-quercustoadb-stats.py $RC; fi
    echo 'Stats are calculated.'

}

#-------------------------------------------------------------------------------

function compress_quercustoa_db
{

    echo "$SEP"
    echo 'Compressing quercusTOA database ...'
    cd $OUTPUT_DIR
    # zip -r quercusTOA-db.zip quercusTOA-db -x "quercusTOA-db/temp/*"
    /usr/bin/time \
        zip \
            -r \
            $DB_NAME.zip \
            $DB_NAME \
            -x "$DB_NAME/temp/*"
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
create_database
download_reference_genome
download_protein_sequences
download_taxonomy_data
cluster_sequences
split_clusters
load_cluster_sequence_relationships
align_clusters
calculate_clusters_identity
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
download_tair10_sequences
build_tair10_blast_db
align_consensus_seqs_2_tair10_blast_db
load_tair10_orthologs
download_gene_ontology
load_gene_ontology
download_lncrna_sequences
build_lncrna_blast_db
calculate_quercustoa_db_stats
compress_quercustoa_db
end

#-------------------------------------------------------------------------------
