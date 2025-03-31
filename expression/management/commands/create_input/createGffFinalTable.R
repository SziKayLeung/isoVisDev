#!/usr/bin/env Rscript
## ----------Script-----------------
##
## Author: Szi Kay Leung (S.K.Leung@exeter.ac.uk)
## create a gene-specific txt file of ggtranscript output to plot in python 
## input:
## - gencode gff from MANE select transcripts
## - gff from gene of interest
## --------------------------------

## ---------- packages -----------------

suppressMessages(library("ggtranscript"))
suppressMessages(library("dplyr"))


## ---------- set up arguments -----------------

args = commandArgs(trailingOnly = T)
# gencode gff of MANE select
#gencode_gff <- "C:/Users/sl693/OneDrive - University of Exeter/ExeterPostDoc/2_Scripts/isoVisDev/expression/static/A1BG_mane_gencode.gff3"
gencode_gff <- args[1]
# gff of gene of interest
#gff <- "C:/Users/sl693/OneDrive - University of Exeter/ExeterPostDoc/2_Scripts/isoVisDev/expression/static/A1BG.gff3"
gff <- args[2]
# output dir 
output_dir <- args[3]
# gene
gene <- args[4]

message("Processing:", gene)

if(file.info(gencode_gff)$size ==0){
  quit("Gencode gff is empty; quitting Rscript")
}else{
  message("Pass check on gencode_gff")
}

if(file.info(gff)$size ==0){
  quit("gff is empty; quitting Rscript")
}else{
  message("Pass check on gff")
}


## ---------- read arguments -----------------

z <- as.data.frame(rtracklayer::import(gencode_gff))
x <- as.data.frame(rtracklayer::import(gff))
x <- x[x$gene_id == gene,]

## ---------- create table of rescaled utr and cds sequences -----------------

common_cols <- intersect(colnames(z), colnames(x))
x <- x %>% select(all_of(common_cols))
z <- z %>% select(all_of(common_cols))

# bind
x<-rbind(x[,names(z)], z)

# extract exons
x_exons <- x %>% dplyr::filter(type == "exon")

# extract cds
x_cds <- x %>% dplyr::filter(type == "CDS")

# remove transripts that have only CDS but no exons
# i.e. transcript present in x_cds but not x_exons (otherwise throws error in add_utr)
x_cds <- x_cds %>% filter(transcript_id %in% x_exons$transcript_id)

x_cds_w_stop <- x_cds %>%
  dplyr::group_by(transcript_id) %>%
  dplyr::mutate(
    end = ifelse(end == max(end), end + 3, end)
  ) %>%
  dplyr::ungroup()

# add_utr() adds ranges that represent the UTRs
x_cds_utr <- add_utr(
  x_exons,
  x_cds_w_stop,
  group_var = "transcript_id"
)

# rescale to shorten gaps
x_cds_utr_rescaled <-
  shorten_gaps(
    exons = x_cds_utr,
    introns = to_intron(x_cds_utr, "transcript_id"),
    group_var = "transcript_id"
  )


noncoding <- shorten_gaps(
    exons = x_exons,
    introns = to_intron(x_cds_utr, "transcript_id"),
    group_var = "transcript_id"
  )

x_cds_utr_rescaled <- x_cds_utr_rescaled %>% select(seqnames, start, end, strand, transcript_id, type, gene_id)
noncoding <- noncoding %>% select(seqnames, start, end, strand, transcript_id, type, gene_id)
final <- as.data.frame(rbind(x_cds_utr_rescaled, noncoding))

## ---------- create table of rescaled utr and cds sequences -----------------

message("Output:", output_dir, "/", gene, ".txt")
write.table(final, paste0(output_dir,"/",gene,".txt"), quote = F, sep = "\t", row.names = F)
