#!/bin/bash

#-------------------------------------------------------------------------------

# This script build the gymnoTOA database.
#
# This software has been developed by:
#
#    GI en Especies Leñosas (WooSp)
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

# Miniconda3
# ==========

#    $ cd /ngscloud2/apps
#    $ wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
#    $ [rm -fr Miniconda3]
#    $ chmod u+x Miniconda3-latest-Linux-x86_64.sh
#    $ ./Miniconda3-latest-Linux-x86_64.sh -b -p Miniconda3
#    $ rm Miniconda3-latest-Linux-x86_64.sh

#    $ Miniconda3/condabin/conda init bash   (reinicializar la consola)

#    $ conda config --add channels defaults
#    $ conda config --add channels bioconda
#    $ conda config --add channels conda-forge
#    $ conda config --set channel_priority strict

#    $ conda update --yes --name base --all

#    $ conda install --yes --name base mamba

#    $ mamba install --yes --name base openjdk=11
#    $ mamba install --yes --name base numpy
#    $ mamba install --yes --name base scipy
#    $ mamba install --yes --name base sympy
#    $ mamba install --yes --name base pandas
#    $ mamba install --yes --name base pandasql
#    $ mamba install --yes --name base matplotlib
#    $ mamba install --yes --name base seaborn
#    $ mamba install --yes --name base plotnine
#    $ mamba install --yes --name base biopython
#    $ mamba install --yes --name base minisom
#    $ mamba install --yes --name base scikit-learn
#    $ mamba install --yes --name base requests
#    $ mamba install --yes --name base paramiko
#    $ mamba install --yes --name base boto3
#    $ mamba install --yes --name base gffutils
#    $ mamba install --yes --name base psutil
#    $ mamba install --yes --name base joblib

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
#    $ mkdir /ngscloud2/apps/Miniconda3/envs/eggnog-mapper/lib/python3.12/site-packages/data/
#    $ conda activate eggnog-mapper
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
#    $ [OLD_VERSION=5.70-102.0]
#    $ NEW_VERSION=5.71-102.0
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

CLADE=Acrogymnospermae

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
    OUTPUT_DIR=/ngscloud2/gymnotoa

    FASTA_FILE=$CLADE-protein-sequences.fasta

    THREADS=16

elif [ "$ENVIRONMENT" = "$ENV_LOCAL" ]; then

    source $BIOCONDA/mmseqs2/util/bash-completion.sh

    NGSHELPER_DIR=$NGSHELPER
    MMSEQS2_DIR=$BIOCONDA/mmseqs2/bin
    INTERPROSCAN_DIR=$APPS/InterProScan
    OUTPUT_DIR=$GYMNOTOA/output

    FASTA_FILE=$CLADE-protein-sequences-seq1000.fasta

    THREADS=4

else
    echo 'Environment error'; exit 3
fi

DB_NAME=gymnoTOA-db
DB_DIR=$OUTPUT_DIR/$DB_NAME
TEMP_DIR=$OUTPUT_DIR/$DB_NAME/temp
GYMNOTOA_DB_ZIP=$DB_NAME.zip
OUTPUT_PREFIX=$TEMP_DIR/$CLADE-mmseqs2
CLUSTER_DIR=$TEMP_DIR/clusters
DB_FILE=$DB_NAME.db
DB_PATH=$DB_DIR/$DB_FILE
FASTA_PATH=$TEMP_DIR/$FASTA_FILE
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

# NCBI Taxonomy
TAXONOMY_TAXDMP_FTP=ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip
TAXONOMY_TAXDMP_PATH=$TEMP_DIR/taxdmp.zip
TAXONOMY_TAXONNAMES_PATH=$TEMP_DIR/names.dmp

# BUSCO gymnosperm dataset
BUSCO_DATASET=Gymnosperm_odb10
BUSCO_DATASET_FTP=https://github.com/jjwujay/Gymnosperm_odb10/raw/main/Gymnosperm_odb10.tar.gz
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
GO_ONTOLOGY_FTP=http://purl.obolibrary.org/obo/go.obo
GO_ONTOLOGY_FILE=$TEMP_DIR/go.obo

# CANTATA data
CANTATA_ARABIDOPSIS_THALIANA_FASTA_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Arabidopsis_thaliana_lncRNAs.fasta
CANTATA_ARABIDOPSIS_THALIANA_FASTA_FILE=$TEMP_DIR/Arabidopsis-thaliana-lncrnas.fasta
CANTATA_ARABIDOPSIS_THALIANA_GTF_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Arabidopsis_thaliana_lncRNAs.gtf
CANTATA_ARABIDOPSIS_THALIANA_GTF_FILE=$TEMP_DIR/Arabidopsis-thaliana-lncrnas.gtf
CANTATA_POPULUS_TRICHOCARPA_FASTA_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Populus_trichocarpa_lncRNAs.fasta
CANTATA_POPULUS_TRICHOCARPA_FASTA_FILE=$TEMP_DIR/Populus-trichocarpa-lncrnas.fasta
CANTATA_POPULUS_TRICHOCARPA_GTF_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Populus_trichocarpa_lncRNAs.gtf
CANTATA_POPULUS_TRICHOCARPA_GTF_FILE=$TEMP_DIR/Populus-trichocarpa-lncrnas.gtf
CANTATA_SELAGINELLA_MOELLENDORFFII_FASTA_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Selaginella_moellendorffii_lncRNAs.fasta
CANTATA_SELAGINELLA_MOELLENDORFFII_FASTA_FILE=$TEMP_DIR/Selaginella-moellendorffii-lncrnas.fasta
CANTATA_SELAGINELLA_MOELLENDORFFII_GTF_URL=http://yeti.amu.edu.pl/CANTATA/DOWNLOADS/Selaginella_moellendorffii_lncRNAs.gtf
CANTATA_SELAGINELLA_MOELLENDORFFII_GTF_FILE=$TEMP_DIR/Selaginella-moellendorffii-lncrnas.gtf
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
EMAPPER_EVALUE=0.001

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
    echo 'Creating the gymnoTOA database ...'
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

function download_ncbi_taxonomy_data
{

    echo "$SEP"
    echo 'Downloading and decompressing NCBI Taxonomy database dump file ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $TAXONOMY_TAXDMP_PATH \
            $TAXONOMY_TAXDMP_FTP
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    unzip -o -d $TEMP_DIR $TAXONOMY_TAXDMP_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error tar $RC; fi
    echo 'File is downloaded and decompressed.'

}

#-------------------------------------------------------------------------------

function download_ncbi_protein_sequences
{

    echo "$SEP"
    echo "Downloading $CLADE protein sequences from NCBI taxonomy database ..."
    if [ "$ENVIRONMENT" = "$ENV_AWS" ]; then
        source activate entrez-direct
        /usr/bin/time \
            esearch -db protein -query "$CLADE [Organism]" | efetch -format fasta >$FASTA_PATH
        RC=$?
        if [ $RC -ne 0 ]; then manage_error esearch $RC; fi
        conda deactivate
    elif [ "$ENVIRONMENT" = "$ENV_LOCAL" ]; then
        cp /home/fmm/Documents/Trabajo/ProyectosVScode/gymnoTOA/data/$FASTA_FILE $TEMP_DIR
    else
        echo 'Environment error'; exit 3
    fi
    echo 'Sequences are downloaded.'

}

#-------------------------------------------------------------------------------

function cluster_sequences
{

    echo "$SEP"
    echo 'Clustering sequences ...'
    /usr/bin/time \
        mmseqs \
            easy-cluster \
            $FASTA_PATH \
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
    echo 'Loading cluster-sequence relationships into gymnoTOA database ...'
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
            $BUSCO_DATASET_FTP
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
    echo 'Loading InterScanPro annotations into gymnoTOA database ...'
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
    echo 'Loading eggNOG-mapper annotations into gymnoTOA database ...'
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
    echo 'Loading TAIR10 orthologs into gymnoTOA database ...'
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
            $GO_ONTOLOGY_FTP
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

}

#-------------------------------------------------------------------------------

function load_gene_ontology
{

    echo "$SEP"
    echo 'Loading Gene Onlotoly into gymnoTOA database ...'
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
            --output-document $CANTATA_ARABIDOPSIS_THALIANA_FASTA_FILE \
            $CANTATA_ARABIDOPSIS_THALIANA_FASTA_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

    echo "$SEP"
    echo 'Downloading Arabidopsis thaliana lncRNA GTF ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $CANTATA_ARABIDOPSIS_THALIANA_GTF_FILE \
            $CANTATA_ARABIDOPSIS_THALIANA_GTF_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

    echo "$SEP"
    echo 'Downloading Populus trichocarpa lncRNA FASTA ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $CANTATA_POPULUS_TRICHOCARPA_FASTA_FILE \
            $CANTATA_POPULUS_TRICHOCARPA_FASTA_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

    echo "$SEP"
    echo 'Downloading Populus trichocarpa lncRNA GTF ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $CANTATA_POPULUS_TRICHOCARPA_GTF_FILE \
            $CANTATA_POPULUS_TRICHOCARPA_GTF_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

    echo "$SEP"
    echo 'Downloading Selaginella moellendorffii lncRNA FASTA ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $CANTATA_SELAGINELLA_MOELLENDORFFII_FASTA_FILE \
            $CANTATA_SELAGINELLA_MOELLENDORFFII_FASTA_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

    echo "$SEP"
    echo 'Downloading Selaginella moellendorffii lncRNA GTF ...'
    /usr/bin/time \
        wget \
            --quiet \
            --output-document $CANTATA_SELAGINELLA_MOELLENDORFFII_GTF_FILE \
            $CANTATA_SELAGINELLA_MOELLENDORFFII_GTF_URL
    RC=$?
    if [ $RC -ne 0 ]; then manage_error wget $RC; fi
    echo 'File is downloaded.'

}

#-------------------------------------------------------------------------------

function concat_lncrna_sequences
{

    echo "$SEP"
    echo 'Concating the lncRNA FASTAS ...'
    /usr/bin/time \
        cat \
            $CANTATA_ARABIDOPSIS_THALIANA_FASTA_FILE \
            $CANTATA_POPULUS_TRICHOCARPA_FASTA_FILE \
            $CANTATA_SELAGINELLA_MOELLENDORFFII_FASTA_FILE \
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

function calculate_gymnotoa_db_stats
{

    echo "$SEP"
    echo 'Calculating stats of gymnoTOA database ...'
    /usr/bin/time \
        calculate-gymnotoadb-stats.py \
            --db=$DB_PATH \
            --stats=$STATS_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error calculate-gymnotoadb-stats.py $RC; fi
    echo 'Stats are calculated.'

}

#-------------------------------------------------------------------------------

function compress_gymnotoa_db
{

    echo "$SEP"
    echo 'Compressing gymnoTOA database ...'
    cd $OUTPUT_DIR
    # zip -r gymnoTOA-db.zip gymnoTOA-db -x "gymnoTOA-db/temp/*"
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
download_ncbi_taxonomy_data
download_ncbi_protein_sequences
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
concat_lncrna_sequences
build_lncrna_blast_db
calculate_gymnotoa_db_stats
compress_gymnotoa_db
end

#-------------------------------------------------------------------------------
