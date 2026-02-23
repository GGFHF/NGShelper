select variant_id, count(*)
    from vcf_samples_alleles
    where allele_id = '99'
    group by variant_id;

select *
    from genomic_features
    where seq_id = 'NW_019805565.1'
      and start <= 5831
      and end >= 5831
      and type in ('region', 'gene', 'pseudogene', 'exon');

select a.variant_id, a.seq_id, a.position, b.start, b.end, b.type, b.gene, c.description
    from vcf_variants a, genomic_features b, gene_info c
    where a.seq_id = b.seq_id
      and a.position >= b.start
      and a.position <= b.end
      and b.type in ('region', 'gene', 'pseudogene', 'exon')
      and b.gene = c.symbol
    order by a.variant_id;

select a.variant_id, a.seq_id, a.position, b.start, b.end, b.type, b.gene, c.description
    from vcf_variants a, genomic_features b
    left join gene_info c on b.gene = c.symbol
    where a.seq_id = b.seq_id
      and a.position >= b.start
      and a.position <= b.end
      and b.type in ('region', 'gene', 'pseudogene', 'exon')
    order by a.variant_id;

select a.variant_id, b.species_id, a.sample_id, a.allele_id, a.frecuency
    from vcf_samples_alleles a, vcf_samples b
    where a.sample_id = b.sample_id
      and a.variant_id = 'NW_019828847.1-129195'
      and b.mother_id = 'NONE'
    order by a.variant_id, b.species_id, a.sample_id, a.allele_id;

select a.variant_id, b.species_id, sample_id, a.allele_id, frecuency
    from vcf_samples_alleles a, vcf_samples b
    where a.sample_id = b.sample_id
      and b.mother_id = 'NONE'
    order by a.variant_id, b.species_id, a.sample_id, a.allele_id;

select a.variant_id, b.species_id, a.allele_id, sum(a.frecuency) "frecuency_sum"
    from vcf_samples_alleles a, vcf_samples b
    where a.sample_id = b.sample_id
      and a.allele_id <> '.'
      and b.mother_id = 'NONE'
    group by a.variant_id, b.species_id, a.allele_id
    order by a.variant_id, b.species_id, a.allele_id;

SELECT a.sample_id, 'PROGENY' "type"
   FROM vcf_samples a
   WHERE a.mother_id != 'NONE'
UNION
SELECT b.sample_id, 'MOTHER' "type"
   FROM vcf_samples b
   WHERE b.sample_id IN (SELECT DISTINCT c.mother_id FROM  vcf_samples c)
UNION
SELECT d.sample_id, 'ADULT' "type"
   FROM vcf_samples d
   WHERE d.mother_id == 'NONE'
     AND d.sample_id NOT IN (SELECT DISTINCT e.mother_id FROM  vcf_samples e)
ORDER BY 1;

SELECT a.variant_id, b.type, a.allele_id, SUM(a.frecuency)
    FROM vcf_samples_alleles a, vcf_samples b
    WHERE a.sample_id = b.sample_id
      AND a.allele_id <> '.'
      AND b.species_id = 'HY'
      AND b.mother_id = 'NONE'
    GROUP BY a.variant_id, b.type, a.allele_id
    ORDER BY a.variant_id, b.type, a.allele_id;
