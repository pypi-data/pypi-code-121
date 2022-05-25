from Bio import SeqIO

AAlist = ['A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I', 'L',
          'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V']

def extractEC(FName:str) -> dict:
    '''
    Extraction of Gene IDs and EC numbers from input file.
    Parameters
    ----------
    FName : str, 
        e.g. 'EC_Annotation.txt'.

    Returns
    -------
    dict
        Dictionary.

    '''
    # loading reference Usti gene-EC mapping
    # FName = 'EC_Annotation.txt'
    ECList = list()
    GeneID = list()
    ECID = list()
    with open(FName) as file:
        for line in file:
            if '[EC:' in line:
                GeneID.append(line.split('\t')[0]) # the first 10 characters represent the gene ID
                ECID.append(line[line.find('[EC:'):line.rfind(']')+1])
    
    EC_dict = dict(zip(GeneID, ECID))
    return EC_dict
# =============================================================================
# 
# =============================================================================
def processFasta(fastafile:str, EC_dict:dict, TestList:str=['unknown', 'hypothetical']) -> dict:
    # protein descriptions that flag ignorable entries
    # TestList = ['unknown', 'hypothetical']
    # "pangenome_AA_Umay.faa"
    
    # Initializing list in order to use append in loop
    recids = list()
    records = list()
    doubles = list()
    with open(fastafile) as handle:
        for record in SeqIO.parse(handle, "fasta"):
            # ignoring duplicate id records
            if record.id not in recids:
                # ignoring hypothetical, unknown entries
                if not any([test in record.description for test in TestList]):
                    if '[EC:' in record.description:
                        record.annotation = record.description[record.description.find('[EC:'):record.description.rfind(']')+1]
                    elif record.id in EC_dict.keys():
                        record.annotation = EC_dict[record.id]
                    records.append(record)
                    recids.append(record.id)
            else:
                doubles.append(record.id)
    
    # storing the entries in the fasta with non-unique id
    DoubleFile = 'Pan_Double_IDs.txt'
    with open(DoubleFile, 'w') as outfile:
        outfile.write('\n'.join(doubles))
        
    rec_dict = SeqIO.to_dict(records)
    return rec_dict
# =============================================================================
# 
# =============================================================================
def RelAASeq(sequence:list):
    myRelAA = [sequence.count(AAid)/len(sequence) for AAid in AAlist]
#     pd.Series(sequence).value_counts()/len(sequence)   
    return myRelAA
# =============================================================================
# 
# =============================================================================
def RelAA4RecDict(rec_dict:dict):
    
    # import pandas as pd
    import numpy as np
    
    SumRelAA = np.zeros(len(AAlist))
    for record in rec_dict.items():
        myRelAA = RelAASeq(list(record[1].seq))
        SumRelAA += myRelAA
    return SumRelAA / len(rec_dict)