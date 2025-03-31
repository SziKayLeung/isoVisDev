MANE <- data.table::fread("C:/Users/sl693/OneDrive - University of Exeter/ExeterPostDoc/2_Scripts/isoVisDev/expression/static/MANE.GRCh38.v1.4.summary.txt")
protein_coding <-  data.table::fread("C:/Users/sl693/OneDrive - University of Exeter/ExeterPostDoc/2_Scripts/isoVisDev/expression/static/protein-coding-genes.txt", 
                                     header = F)

protein_coding <- protein_coding %>% filter(!grepl("MT",V1))
MANE_protein_coding <- MANE %>% filter(symbol %in% protein_coding$V1) %>% select(symbol, Ensembl_nuc)
write.table(MANE_protein_coding, "C:/Users/sl693/OneDrive - University of Exeter/ExeterPostDoc/2_Scripts/isoVisDev/expression/static/MANE_protein-coding-genes_nonMT.txt",
             col.names = F, row.names = F, sep = "\t", quote = F)
            
            
