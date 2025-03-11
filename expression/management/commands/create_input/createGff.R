library("ggtranscirpt")
library("data.table")
library("dplyr")

dir <- "/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/C_Whole_Targeted/10_cpat/"

gff <- as.data.frame(rtracklayer::import(paste0(dir,"APOE.gff3"))) 
#gff<-rbind(gff[,names(z)], z)

x_exons <- gff %>% dplyr::filter(type == "exon")
x_cds <- gff %>% dplyr::filter(type == "CDS")

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
x_cds_utr_rescaled <-
  shorten_gaps(
    exons = x_cds_utr,
    introns = to_intron(x_cds_utr, "transcript_id"),
    group_var = "transcript_id"
  )

x_cds_utr_rescaled <- x_cds_utr_rescaled["gene_id","transcript_id","type","start","end"]
