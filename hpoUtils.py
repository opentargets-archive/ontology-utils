import os
import httplib
import time
import json
import re
import sys
import datetime
import optparse
import logging
import hashlib
import ontologyutils as onto
import numpy
import math
from settings import Config

hpo = None
hpo_alt_ids = {}
nb_diseases = 0
rare_diseases = {}
common_diseases = {}
diseaseLookup = {}
phenotypeLookup = {}
doidLookup = {}
ICs = {}
ancestors = {}
micas = {}
def main():

    parser = optparse.OptionParser()
    parser.add_option('-p', '--hpo', type='string', default=Config.HPO_FILES['obo'], dest='hpoFilename')
    parser.add_option('-r', '--rd', type='string', default=Config.HPO_FILES['rare_phenotype_annotation'], dest='rdFilename')
    parser.add_option('-c', '--cd', type='string', default=Config.HPO_FILES['common_phenotype_annotation'], dest='cdFilename')
    parser.add_option('-b', '--backup', type='string', default=Config.HPO_FILES['ic_backup'], dest='backupFilename')
    options, args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    loadHPO(options.hpoFilename);
    #loadRareDiseases(options.rdFilename)
    #loadCommonDiseases(options.cdFilename)
    #computeICs()
    #writeBackup(options.backupFilename)
    #sys.exit(1);

    readBackup(options.backupFilename);
    #extractDiseasePhenotype('OMIM:154700')
    
    getAllAncestors();
    #computeAllMICA();
    
    extractDiseasePhenotype('D001159')

    #sys.exit(0)
    
    #print "Similarity %f"%(sim('OMIM:154700', 'OMIM:154700'))
    #print "Similarity Noonan Opitz %f"%(sim('OMIM:163950', 'OMIM:300000'))
    print "Similarity %f"%(sim('D001159', 'D046788'))
    # D002446 Celiac Disease 
    
    print "Similarity COPD %f"%(sim('D029424', 'OMIM:244400'))
    
    # D001172 OMIM    610163  
    print "Similarity Arthritis, Rheumatoid / immunodeficiency due to defect in CD3 %f"%(sim('D001172', 'OMIM:610163'))
    
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
    
def getCD2RDs(cd, rdSet, cutoff=2, limit=20):
    diseasePairs = {}
    topScore = []
    #for n in range(0,20):
    global rare_diseases;
    global common_diseases; 
    n =0;
    for rd in rare_diseases[rdSet]:
        score = sim(cd, rd)
        if score >= cutoff:
            print "%s %s %s %s"%(cd, common_diseases['MeSH'][cd]['label'], rd, rare_diseases[rdSet][rd]['label']);
            print "Similarity %f"%(sim(cd, rd))
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
            print "%s %s %f"%(cd2, common_diseases['MeSH'][cd2]['label'], score)
            n+=1
        if n > limit:
            return;

def getRD2CDs(rd, rdSet, cutoff=2, limit=20):
    diseasePairs = {}
    topScore = []
    #for n in range(0,20):
    global rare_diseases;
    global common_diseases; 
    n =0;
    print rare_diseases[rdSet][rd]['label']
    for cd in common_diseases['MeSH']:
        score = sim(cd, rd)
        if score >= cutoff:
            print "%s %s %f"%(cd, common_diseases['MeSH'][cd]['label'], score);
            n+=1
        if n > limit:
            return;            
            
def getTop20SimilarDiseases():
    diseasePairs = {}
    topScore = []
    #for n in range(0,20):
    global rare_diseases;
    global common_diseases; 
    n = 0
    cutoff = 1.1
    for db1 in common_diseases:
        print db1;
        for db2 in rare_diseases:
            print db2;
            for cd in common_diseases[db1]:
                #print "%s %s"%();
                n =0;
                for rd in rare_diseases[db2]:
                    score = sim(cd, rd)
                    if score >= cutoff:
                        print "%s %s %s %s"%(cd, common_diseases[db1][cd]['label'], rd, rare_diseases[db2][rd]['label']);
                        print "Similarity %f"%(sim(cd, rd))
                        n+=1
                    if n > 20:
                        return;
        
def getAllAncestors():
    global phenotypeLookup;
    global ancestors;
    for hpo_id in phenotypeLookup:
        ancestors[hpo_id] = hpo.getAncestors(hpo_id);

#def computeAllMICA():
    
    
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
    
def computeICs():
    for phenotype in phenotypeLookup:
        ICs[phenotype] = ic(phenotype)
        
def extractDiseasePhenotype(disease_id):
    record = diseaseLookup[disease_id]
    print record['label']
    for termId in record['phenotypes']:
        print "%s" %(hpo.terms[termId]['tags']['name'][0])
    print len(record['phenotypes'])
    
def ic(hpo_id):
    return -math.log(len(phenotypeLookup[hpo_id])/float(nb_diseases));

def findMICA(s, t):
    mica = None
    if s == t or s in hpo.getAncestors(t):
        return ic(s);
    elif t in hpo.getAncestors(s):
        return ICs[t]; #ic(t);
    else:
        # find the most informative common ancestor
        l = [s, t]
        l.sort()
        key = "".join(l)
        if key in micas:
            return micas[key];
        else:
            #print "%s %s"%(t,s)
            common_ancestors = set(ancestors[t].intersection(ancestors[s]))
            #print "%s % s %s"%(s, t, ",".join(common_ancestors))
            mica = max(map(lambda x: ICs[x], common_ancestors))
            micas[key] = mica
            return mica;
    #return mica; 
    
def simDir(D1, D2):
    P1 = diseaseLookup[D1]['phenotypes']
    P2 = diseaseLookup[D2]['phenotypes']
    set = []
    for s in P1:
        buffer = []
        for t in P2:
            buffer.append(findMICA(s, t))
        set.append(max(buffer))
    return numpy.mean(set)

def sim(D1, D2):
    return float(0.5)*simDir(D1, D2)+float(0.5)*simDir(D2, D1);

def addDiseaseToPhenotype(disease_id, hpo_id):
    global phenotypeLookup;
    ancestors = hpo.getAncestors(hpo_id)
    for ancestor in ancestors:
        if ancestor not in phenotypeLookup:
            phenotypeLookup[ancestor] = []
        if disease_id not in phenotypeLookup[ancestor]:
            phenotypeLookup[ancestor].append(disease_id)
    
def loadRareDiseases(rdFilename):
    global rare_diseases;
    global diseaseLookup;
    global nb_diseases;
    global hpo_alt_ids;
    with open(rdFilename, "rb") as f_obj:
        for line in f_obj:
            A = line.rstrip("\n").split("\t")
            #print A[0]
            if A[0] not in rare_diseases:
                rare_diseases[A[0]] = {}
            db = rare_diseases[A[0]]
            disease_name = A[2]
            disease_id = A[0] + ":" + A[1]
            hpo_id = A[4]
            if hpo_id in hpo_alt_ids:
                hpo_id = hpo_alt_ids[hpo_id]
            if hpo_id in hpo.terms:
                if 'is_obsolete' in hpo.terms[hpo_id]['tags'] and hpo.terms[hpo_id]['tags']['is_obsolete'][0] == 'true':
                    if 'replaced_by' in hpo.terms[hpo_id]['tags']:
                        hpo_id = hpo.terms[hpo_id]['tags']['replaced_by'][0]
                    else:
                        hpo_id = 'HP:0000001' # So it's general term with a very low IC
            else:
                hpo_id = 'HP:0000001' # So it's general term with a very low IC
            #if A[4] == 'HP:0007852':
            #    print hpo_id
            #    sys.exit(1)
            key = disease_id;
            if key not in db:
                nb_diseases +=1
                db[key] = { 'phenotypes': [], 'id' : disease_id, 'label': disease_name }
            db[key]['phenotypes'].append(hpo_id)
            addDiseaseToPhenotype(disease_id, hpo_id)
            #pointer
            diseaseLookup[key] = db[key]
            
            #print hpo_id
    f_obj.close()
    print ",".join(rare_diseases.keys())

def loadCommonDiseases(cdFilename):
    global common_diseases;
    global diseaseLookup;
    global nb_diseases;
    global hpo_alt_ids;
    with open(cdFilename, "rb") as f_obj:
        for line in f_obj:
            A = line.rstrip("\n").split("\t")
            if 'MeSH' not in common_diseases:
                common_diseases['MeSH'] = {}
            db = common_diseases['MeSH']
            disease_name = A[1]
            disease_id = A[0]
            doid = A[2]
            #disease_id = doid
            hpo_id = A[3]
            if hpo_id in hpo_alt_ids:
                hpo_id = hpo_alt_ids[hpo_id]
            if hpo_id in hpo.terms:
                if 'is_obsolete' in hpo.terms[hpo_id]['tags'] and hpo.terms[hpo_id]['tags']['is_obsolete'][0] == 'true':
                    if 'replaced_by' in hpo.terms[hpo_id]['tags']:
                        hpo_id = hpo.terms[hpo_id]['tags']['replaced_by'][0]
                    else:
                        hpo_id = 'HP:0000001' # So it's general term with a very low IC
            else:
                print "%s is not an HPO term"%(A[3])
                hpo_id = 'HP:0000001' # So it's general term with a very low IC
            #if A[3] == 'HP:0007852':
            #    print hpo_id
            #    sys.exit(1)            
            #print hpo_id
            if disease_id not in db:
                nb_diseases +=1
                db[disease_id] = { 'phenotypes': [], 'id' : disease_id, 'label': disease_name, 'doid': doid, 'MeSH': disease_id }
            db[disease_id]['phenotypes'].append(hpo_id)
            addDiseaseToPhenotype(disease_id, hpo_id)
            #disease pointer
            diseaseLookup[disease_id] = db[disease_id]
            # doid pointer
            if not doid in doidLookup:
                doidLookup[doid] = []
            doidLookup[doid].append(disease_id)

    f_obj.close()
    print ",".join(common_diseases.keys())
    
    
#parse OBO file
def loadHPO(hpoFilename):
    global hpo
    hpo = onto.Ontology.fromOBOFile(hpoFilename)
    logging.info(hpo.terms['HP:0100006']['tags'].keys())
    for term_id in hpo.terms:
        print term_id
        if 'tags' in hpo.terms[term_id] and 'alt_id' in hpo.terms[term_id]['tags']:
            for alt_id in hpo.terms[term_id]['tags']['alt_id']:
                hpo_alt_ids[alt_id] = term_id
    
if __name__ == "__main__":
    main()

    