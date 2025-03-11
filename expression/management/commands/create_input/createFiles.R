library("dplyr")
library("vroom")
library("data.table")
root_dir <- "C:/Users/sl693/OneDrive - University of Exeter/ExeterPostDoc/1_Projects/SFARI/PaperZenodo/"
output_dir <- "C:/Users/sl693/OneDrive - University of Exeter/ExeterPostDoc/2_Scripts/isoVisDev/expression/files/"
load(file = paste0(root_dir,"sqanti/sqantifiltered_monoexonicfiltered_2reads2samples.RData"))
normGenes <- vroom(paste0(root_dir,"DGE/DESeq2_whole_development_normAll.csv"),delim = ",", show_col_types = FALSE)
normGroupTranscript <- vroom(paste0(root_dir,"DTE/DESeq2_whole_development_normSig.csv"),delim = ",", show_col_types = FALSE)
normSexTranscript<- vroom(paste0(root_dir,"DTE/DESeq2_whole_sex_normSig.csv"),delim = ",", show_col_types = FALSE)
phenotype <- fread(paste0(root_dir, "metadata/WholeTargetedphenotype_fixedsex.csv"),data.table=F, stringsAsFactors=F) %>% mutate(time = age)
ProteinCodingGenes <- read.table(paste0(root_dir, "/utils/protein-coding-genes.txt"))[["V1"]]

# generate num_Genes.csv
totalN <- class.files$glob_targ_SQ %>% filter(!grepl("novel", associated_gene)) %>% group_by(associated_gene) %>% tally()
colnames(totalN) <- c("associated_gene","totalN")
novelN <- class.files$glob_targ_SQ %>% filter(!grepl("novel", associated_gene)) %>% filter(!structural_category %in% c("FSM","ISM")) %>% 
  group_by(associated_gene) %>% tally()
colnames(novelN) <- c("associated_gene","novelN")
numGenes <- merge(totalN, novelN, by = "associated_gene", all = T)
numGenes[is.na(numGenes)] <- 0
numGenes <- numGenes %>% filter(!grepl("_", associated_gene))
numGenes <- numGenes %>% filter(associated_gene %in% ProteinCodingGenes)
write.csv(numGenes, paste0(root_dir, "webResource/NumGenes.csv"), row.names = F, quote = F)
write.csv(numGenes, paste0(output_dir, "NumGenes.csv"), row.names = F, quote = F)

# generate normalised gene counts
normGenes <- merge(normGenes, phenotype, by = "sample")
normGenes <- normGenes[normGenes$associated_gene %in% numGenes$associated_gene, ]
normGenes <- normGenes %>% mutate(sampleID = as.numeric(factor(sample))) %>% select(sampleID, associated_gene, normalised_counts, group, sex) 
colnames(normGenes) <- c("sampleID","geneName","counts","group","sex")
write.csv(normGenes, paste0(root_dir, "webResource/NormalisedGeneCounts.csv"), row.names = F, quote = F)

# generate normalised trancript counts
normGroupTranscript <- normGroupTranscript[normGroupTranscript$associated_gene %in% numGenes$associated_gene, ]
normGroupTranscript <- merge(normGroupTranscript, phenotype, by = "sample")
normGroupTranscript <- normGroupTranscript %>% mutate(sampleID = as.numeric(factor(sample))) %>% select(sampleID, associated_gene, isoform, normalised_counts, group, sex) 
colnames(normGroupTranscript) <- c("sampleID","geneName","isoform","counts","group","sex")
write.csv(normGroupTranscript, paste0(root_dir, "webResource/NormalisedGroupTranscriptCounts.csv"), row.names = F, quote = F)

# generate normalised trancript counts
normSexTranscript <- normSexTranscript[normSexTranscript$associated_gene %in% numGenes$associated_gene, ]
normSexTranscript  <- merge(normSexTranscript, phenotype, by = "sample")
normSexTranscript  <- normSexTranscript %>% mutate(sampleID = as.numeric(factor(sample))) %>% select(sampleID, associated_gene, isoform, normalised_counts, group, sex) 
colnames(normSexTranscript) <- c("sampleID","geneName","isoform","counts","group","sex")
write.csv(normSexTranscript , paste0(root_dir, "webResource/NormalisedSexTranscriptCounts.csv"), row.names = F, quote = F)