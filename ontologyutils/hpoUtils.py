from __future__ import print_function
import json
import sys
import optparse
import logging
from ontologyutils.similarity import PhenotypeLookup, Diseases
from ontologyutils.ou_settings import OUConfig

hpo = None
ICs = dict()
ancestors = dict()
micas = dict()
def main():

    parser = optparse.OptionParser()
    parser.add_option('-p', '--hpo', type='string', default=OUConfig.HPO_FILES['obo'], dest='hpoFilename')
    parser.add_option('-r', '--rd', type='string', default=OUConfig.HPO_FILES['rare_phenotype_annotation'], dest='rdFilename')
    parser.add_option('-c', '--cd', type='string', default=OUConfig.HPO_FILES['common_phenotype_annotation'], dest='cdFilename')
    #parser.add_option('-b', '--backup', type='string', default=Config.HPO_FILES['ic_backup'], dest='backupFilename')
    parser.add_option('-s', '--rdset', type='string', default='OMIM', dest='rdset')

    options, args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    logging.info("Load HP")
    phenotypeLookup = PhenotypeLookup(options.hpoFilename)
    diseases = Diseases(phenotypeLookup)

    bRecompute = False

    if (bRecompute):
        logging.info("Load Rare disease annotations")
        diseases.load_rare_diseases(options.rdFilename)
        logging.info("Load MeSH disease annotations")
        diseases.load_mesh_diseases(options.cdFilename)
        diseases.compute_ICs()
        diseases.compute_MICAs()
        diseases.write_backup(OUConfig.SIM_DISEASES_BACKUP, OUConfig.SIM_MICAS_BACKUP)
        #sys.exit(1)
    else:
        diseases.read_backup(OUConfig.SIM_DISEASES_BACKUP, OUConfig.SIM_MICAS_BACKUP)

        logging.info(diseases.MICAs[0,0])
        logging.info(diseases.MICAs[500, 600])
        logging.info(diseases.MICAs)

        indexA = 0
        for diseaseA in diseases.disease_lookup:
            #print diseaseA
            indexB = 0
            for diseaseB in diseases.disease_lookup:
                if indexB > indexA:
                    sim = diseases.compute_disease_similarity(diseaseA, diseaseB)
                    if sim >= 1.5:
                        logging.info("%s\t%s\t%.4f"%(diseaseA, diseaseB, diseases.compute_disease_similarity(diseaseA, diseaseB)))
                indexB+=1
            indexA +=1

    #diseases.list_disease_phenotype('D010392')

    # Now compute efficiency all the common ancestors level by level.
    # Each level in the ontology is the common ancestor of all its children
    # So we could build a data structure of common ancestors
    #diseases.write_backup(options.backupFilename)

    sys.exit(1)

    #extractDiseasePhenotype('OMIM:154700')

    ''' get all HP term ancestors in one place '''
    getAllAncestors()
    #computeAllMICA();

    #printAllDiseaseNames('MeSH')
    #sys.exit(0)

    #extractDiseasePhenotype('D010392')

    #sys.exit(0)

    #getCD2RDSimilarity('D010392', "ORPHANET:2732", 'ORPHANET')
    #"ORPHANET:2732" "ORPHANET:98849"
    getCDs2RDs(options.rdset);

    sys.exit(0)


    #print "Similarity %f"%(sim('OMIM:154700', 'OMIM:154700'))
    #print "Similarity Noonan Opitz %f"%(sim('OMIM:163950', 'OMIM:300000'))
    print("Similarity %f"%(sim('D001159', 'D046788')))

    # D002446 Celiac Disease 
    
    logging.info("Similarity COPD %f"%(sim('D029424', 'OMIM:244400')))
    
    # D001172 OMIM    610163  
    logging.info("Similarity Arthritis, Rheumatoid / immunodeficiency due to defect in CD3 %f"%(sim('D001172', 'OMIM:610163')))
    
    #getCD2RDs('D029424', 'OMIM', 2, limit =10)
    #getCD2RDs('D011565', 'ORPHANET')
    #getCD2RDs('D011565', 'OMIM')
    #getRD2CDs('OMIM:612567', 'OMIM', cutoff=2.8, limit=40)
    
    #print sim('OMIM:270200', 'D008180')
    
    # Vasculitis
    #getCD2CDs('D014657', cutoff=3.0, limit =300)
    # Psoriasis
    #getCD2CDs('D011565', cutoff=3.0, limit =300)
    # IBD D043183
    #getCD2CDs('D043183', cutoff=2.5, limit =300)
    # Asthma
    #getCD2CDs('D001249', cutoff=2.5, limit =300)
    #getCD2RDs('D001249', 'OMIM', cutoff=2.5, limit =100)
    #getCD2RDs('D001249', 'ORPHANET', cutoff=2.5, limit =100)
    #getTop20SimilarDiseases()
    # D050197 Atherosclerosis
    #getCD2CDs('D050197', cutoff=2.5, limit =300)
    #getCD2RDs('D050197', 'OMIM', cutoff=2.5, limit =100)
    #getCD2RDs('D050197', 'ORPHANET', cutoff=2.5, limit =100)
    # OMIM:176670 progeria
    getRD2CDs('OMIM:176670', 'OMIM', cutoff=2, limit=50)

def getCDs2RDs(rdSet, cutoff=2):
    global common_diseases
    cdSet = 'MeSH'
    for cd in common_diseases[cdSet]:
        for rd in rare_diseases[rdSet]:
                s = simPhenotypes(cd, rd)
                score = s['sim']
                d1d2 = s['d1d2']
                d2d1 = s['d2d1']
                #score = sim(cd, rd)
                if score >= cutoff:
                    logging.info("\"%s\"\t\"%s\"\t\"%s\"\t\"%s\"\t\"%s\"\t\"%s\"\t\"%s\""%(cd, common_diseases['MeSH'][cd]['label'], rd, rare_diseases[rdSet][rd]['label'], score, micas2String(d1d2),micas2String(d2d1) ));

def getCD2RDSimilarity(cd, rd, rdSet):
    global common_diseases
    cdSet = 'MeSH'
    s = simPhenotypes(cd, rd)
    score = s['sim']
    d1d2 = s['d1d2']
    d2d1 = s['d2d1']
    logging.info("\"%s\"\t\"%s\"\t\"%s\"\t\"%s\"\t\"%s\"\t\"%s\"\t\"%s\""%(cd, common_diseases['MeSH'][cd]['label'], rd, rare_diseases[rdSet][rd]['label'], score, micas2String(d1d2),micas2String(d2d1) ));


def getCD2RDs(cd, rdSet, cutoff=2, limit=20):
    diseasePairs = dict()
    topScore = []
    #for n in range(0,20):
    global rare_diseases;
    global common_diseases; 
    n =0;
    for rd in rare_diseases[rdSet]:
        score = sim(cd, rd)
        if score >= cutoff:
            logging.info("%s %s %s %s"%(cd, common_diseases['MeSH'][cd]['label'], rd, rare_diseases[rdSet][rd]['label']));
            logging.info("Similarity %f"%(sim(cd, rd)))
            n+=1
        if n > limit:
            return;

def getCD2CDs(cd1, cutoff=2, limit=20):
    global common_diseases; 
    cdSet = 'MeSH';
    n =0;
    for cd2 in common_diseases[cdSet]:
        score = sim(cd1, cd2)
        if score >= cutoff:
            logging.info("%s %s %f"%(cd2, common_diseases['MeSH'][cd2]['label'], score))
            n+=1
        if n > limit:
            return;

def getRD2CDs(rd, rdSet, cutoff=2, limit=20):
    diseasePairs = dict()
    topScore = []
    #for n in range(0,20):
    global rare_diseases;
    global common_diseases; 
    n =0;
    print(rare_diseases[rdSet][rd]['label'])
    for cd in common_diseases['MeSH']:
        score = sim(cd, rd)
        if score >= cutoff:
            logging.info("%s %s %f"%(cd, common_diseases['MeSH'][cd]['label'], score));
            n+=1
        if n > limit:
            return;            
            
def getTop20SimilarDiseases():
    diseasePairs = dict()
    topScore = []
    #for n in range(0,20):
    global rare_diseases;
    global common_diseases; 
    n = 0
    cutoff = 1.1
    for db1 in common_diseases:
        logging.info(db1);
        for db2 in rare_diseases:
            logging.info(db2);
            for cd in common_diseases[db1]:
                #print "%s %s"%();
                n =0;
                for rd in rare_diseases[db2]:
                    score = sim(cd, rd)
                    if score >= cutoff:
                        logging.info("%s %s %s %s"%(cd, common_diseases[db1][cd]['label'], rd, rare_diseases[db2][rd]['label']));
                        logging.info("Similarity %f"%(sim(cd, rd)))
                        n+=1
                    if n > 20:
                        return;

#def computeAllMICA():
    

def printAllDiseaseNames(diseaseSet):
    if diseaseSet == 'OMIM' or diseaseSet == 'ORPHANET':
        for disease_id in rare_diseases[diseaseSet]:
            logging.info(rare_diseases[diseaseSet][disease_id]['label'])
    elif diseaseSet == 'MeSH':
        for disease_id in common_diseases[diseaseSet]:
            logging.info(common_diseases[diseaseSet][disease_id]['label'])

def writeBackup(backupFilename):
    global nb_diseases;
    global rare_diseases;
    global common_diseases;
    global diseaseLookup;
    global phenotypeLookup;
    global doidLookup;
    global ICs;
    with open(backupFilename, "w") as f_obj:
        f_obj.write(json.dumps({ 
            'nb_diseases': nb_diseases, 
            'rare_diseases': rare_diseases, 
            'common_diseases': common_diseases, 
            'doidLookup': doidLookup, 
            'diseaseLookup': diseaseLookup, 
            'phenotypeLookup': phenotypeLookup, 
            'ICs': ICs } ))
    f_obj.close()

def readBackup(backupFilename):
    global nb_diseases;
    global rare_diseases;
    global common_diseases;
    global doidLookup;
    global diseaseLookup;
    global phenotypeLookup;
    global ICs;
    with open(backupFilename, "rb") as f_obj:
        buffer = json.loads(f_obj.read())
        nb_diseases = buffer['nb_diseases']
        rare_diseases = buffer['rare_diseases']
        common_diseases = buffer['common_diseases']
        doidLookup = buffer['doidLookup']
        diseaseLookup = buffer['diseaseLookup']
        phenotypeLookup = buffer['phenotypeLookup']
        ICs = buffer['ICs']
    f_obj.close()
    

def extractDiseasePhenotype(disease_id):
    record = diseaseLookup[disease_id]
    logging.info(record['label'])
    for termId in record['phenotypes']:
        logging.info("%s" %(hpo.terms[termId]['tags']['name'][0]))
    logging.info(len(record['phenotypes']))
    




    f_obj.close()
    logging.info(",".join(list(common_diseases.keys())))
    
    

    
if __name__ == "__main__":
    main()

    