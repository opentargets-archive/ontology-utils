from __future__ import division
from __future__ import print_function
from builtins import filter
from past.utils import old_div
from builtins import object
import opentargets_ontologyutils as onto
import numpy
import math
import operator
import json
import numpy as np

__author__ = 'gautierk'

LIMIT = 1000

class OntologyLookup(object):
    def __init__(self, obo_file=None):
        self.ontology = None
        self.term_to_disease_lookup = dict()
        self.ancestors = dict()
        self.alt_ids = dict()
        self.load_classes(obo_file)
        #self.generate_ancestors()
        pass

    def generate_ancestors(self):
        for class_id in self.term_to_disease_lookup:
            self.ancestors[class_id] = self.ontology.getAncestors(class_id)

    def load_classes(self, obo_file):
        self.ontology = onto.Ontology.fromOBOFile(obo_file)
        for term_id in self.ontology.terms:
            # print term_id
            if 'tags' in self.ontology.terms[term_id] and 'alt_id' in self.ontology.terms[term_id]['tags']:
                for alt_id in self.ontology.terms[term_id]['tags']['alt_id']:
                    self.alt_ids[alt_id] = term_id

    def write_backup(self, backupFilename):
        with open(backupFilename, "w") as f_obj:
            f_obj.write(json.dumps({
                'classLookup': self.term_to_disease_lookup,
                'ancestors': self.ancestors}))
        f_obj.close()

    def read_backup(self, backupFilename):
        with open(backupFilename, "rb") as f_obj:
            buffer = json.loads(f_obj.read())
            self.term_to_disease_lookup = buffer['classLookup']
            self.ancestors = buffer['ancestors']
        f_obj.close()


class PhenotypeLookup(OntologyLookup):
    def __init__(self, obo_file):
        """
		Call super constructor
		BaseClassName.__init__(self, args)
		"""
        super(PhenotypeLookup, self).__init__(obo_file=obo_file)
        self.sorted_terms = []

    def add_disease_to_phenotype(self, disease_id, hpo_id):
        '''
		Add a disease_id to a phenotype term. This is used
		to compute the level of information content of a term
		:param disease_id:
		:param hpo_id:
		:return:
		'''

        ancestors = list(self.ontology.getAncestors(hpo_id))
        if hpo_id not in self.ancestors:
            for ancestor in ancestors:
                if ancestor not in self.term_to_disease_lookup:
                    self.term_to_disease_lookup[ancestor] = []
                    an = list(self.ontology.getAncestors(ancestor))[:]
                    an.remove(ancestor)
                    print("Adding ancestors %s => %s"%(ancestor, ",".join(an)))
                    self.ancestors[ancestor] = an

        for ancestor in ancestors:

            if disease_id not in self.term_to_disease_lookup[ancestor]:
                self.term_to_disease_lookup[ancestor].append(disease_id)


class Diseases(object):
    def __init__(self, phenotype_lookup):
        # store the keys of disease datasets
        self.datasets = dict()
        self.nb_diseases = 0
        self.disease_lookup = dict()
        self.do_lookup = dict()
        self.phenotype_lookup = phenotype_lookup
        self.ICs = dict()
        self.MICAs = np.empty([1, 1], dtype=float)

    def load_rare_diseases(self, rdFilename):

        nb_lines = 0
        with open(rdFilename, "rb") as f_obj:
            for line in f_obj:
                A = line.rstrip("\n").split("\t")
                # print A[2]
                if A[0] not in self.datasets:
                    self.datasets[A[0]] = dict()
                db = self.datasets[A[0]]
                disease_name = A[2]
                disease_id = A[0] + ":" + A[1]
                hpo_id = A[4]
                if hpo_id in self.phenotype_lookup.alt_ids:
                    hpo_id = self.phenotype_lookup.alt_ids[hpo_id]
                if hpo_id in self.phenotype_lookup.ontology.terms:
                    if ('is_obsolete' in self.phenotype_lookup.ontology.terms[hpo_id]['tags'] and
                                self.phenotype_lookup.ontology.terms[hpo_id]['tags']['is_obsolete'][0] == 'true'):
                        if 'replaced_by' in self.phenotype_lookup.ontology.terms[hpo_id]['tags']:
                            hpo_id = self.phenotype_lookup.ontology.terms[hpo_id]['tags']['replaced_by'][0]
                        else:
                            hpo_id = 'HP:0000001'  # So it's general term with a very low IC
                else:
                    hpo_id = 'HP:0000001'  # So it's general term with a very low IC
                # if A[4] == 'HP:0007852':
                #    print hpo_id
                #    sys.exit(1)
                key = disease_id;
                if key not in db:
                    self.nb_diseases += 1
                    db[key] = {'phenotypes': [], 'id': disease_id, 'label': disease_name}
                db[key]['phenotypes'].append(hpo_id)
                self.phenotype_lookup.add_disease_to_phenotype(disease_id, hpo_id)
                # pointer
                self.disease_lookup[key] = db[key]

                # print hpo_id
                nb_lines+=1
                #if nb_lines > LIMIT:
                #    break

        f_obj.close()

    def load_mesh_diseases(self, cdFilename):

        nb_lines = 0
        with open(cdFilename, "rb") as f_obj:
            for line in f_obj:
                A = line.rstrip("\n").split("\t")
                if 'MeSH' not in self.datasets:
                    self.datasets['MeSH'] = dict()
                db = self.datasets['MeSH']
                disease_name = A[1]
                disease_id = A[0]
                doid = A[2]
                # disease_id = doid
                hpo_id = A[3]
                if hpo_id in self.phenotype_lookup.alt_ids:
                    hpo_id = self.phenotype_lookup.alt_ids[hpo_id]
                if hpo_id in self.phenotype_lookup.ontology.terms:
                    if ('is_obsolete' in self.phenotype_lookup.ontology.terms[hpo_id]['tags'] and
                                self.phenotype_lookup.ontology.terms[hpo_id]['tags']['is_obsolete'][0] == 'true'):
                        if 'replaced_by' in self.phenotype_lookup.ontology.terms[hpo_id]['tags']:
                            hpo_id = self.phenotype_lookup.ontology.terms[hpo_id]['tags']['replaced_by'][0]
                        else:
                            hpo_id = 'HP:0000001'  # So it's general term with a very low IC
                else:
                    print("%s is not an HPO term" % (A[3]))
                    hpo_id = 'HP:0000001'  # So it's general term with a very low IC
                # if A[3] == 'HP:0007852':
                #    print hpo_id
                #    sys.exit(1)
                # print hpo_id
                if disease_id not in db:
                    self.nb_diseases += 1
                    db[disease_id] = {'phenotypes': [], 'id': disease_id, 'label': disease_name, 'doid': doid,
                                      'MeSH': disease_id}
                db[disease_id]['phenotypes'].append(hpo_id)
                self.phenotype_lookup.add_disease_to_phenotype(disease_id, hpo_id)
                # disease pointer
                self.disease_lookup[disease_id] = db[disease_id]
                # doid pointer
                if not doid in self.do_lookup:
                    self.do_lookup[doid] = []
                self.do_lookup[doid].append(disease_id)

                nb_lines+=1
                #if nb_lines > LIMIT:
                #    break

            f_obj.close()


    def write_backup(self, diseases_backup_filename, micas_backup_filename):

        with open(micas_backup_filename, "w") as f_micas:
        #memfile = StringIO.StringIO()
            numpy.save(f_micas, self.MICAs)
        ##memfile.seek(0)
        #serialized = json.dumps(memfile.read().decode('latin-1'))
        f_micas.close()

        with open(diseases_backup_filename, "w") as f_obj:
            f_obj.write(json.dumps({
                'nb_diseases': self.nb_diseases,
                'datasets': self.datasets,
                'do_lookup': self.do_lookup,
                'disease_lookup': self.disease_lookup,
                'phenotype_lookup' : {
                    'term_to_disease_lookup': self.phenotype_lookup.term_to_disease_lookup,
                    'ancestors': self.phenotype_lookup.ancestors,
                    'sorted_terms': self.phenotype_lookup.sorted_terms
                },
                'ICs': self.ICs } ))
        f_obj.close()

    def read_backup(self, diseases_backup_filename, micas_backup_filename):

        with open(micas_backup_filename) as f_micas:
        #memfile = StringIO.StringIO()
            self.MICAs = numpy.load(f_micas)
        ##memfile.seek(0)
        #serialized = json.dumps(memfile.read().decode('latin-1'))
        f_micas.close()

        with open(diseases_backup_filename, "rb") as f_obj:
            buffer = json.loads(f_obj.read())
            self.nb_diseases = buffer['nb_diseases']
            self.datasets = buffer['datasets']
            self.do_lookup = buffer['do_lookup']
            self.disease_lookup = buffer['disease_lookup']
            for item in buffer['phenotype_lookup']['term_to_disease_lookup']:
                self.phenotype_lookup.term_to_disease_lookup[item] = buffer['phenotype_lookup']['term_to_disease_lookup'][item]
            self.phenotype_lookup.ancestors = buffer['phenotype_lookup']['ancestors']
            self.phenotype_lookup.sorted_terms = buffer['phenotype_lookup']['sorted_terms']
            self.ICs = buffer['ICs']

        f_obj.close()

    def list_disease_phenotype(self, disease_id):
        record = self.disease_lookup[disease_id]
        print(record['label'])
        for termId in record['phenotypes']:
            print("%s" %(self.phenotype_lookup.ontology.terms[termId]['tags']['name'][0]))
        print(len(record['phenotypes']))


    def compute_ICs(self):
        for phenotype in self.phenotype_lookup.term_to_disease_lookup:
            self.ICs[phenotype] = self.ic(phenotype)

    def ic(self, hpo_id):
        return -math.log(old_div(len(self.phenotype_lookup.term_to_disease_lookup[hpo_id]), float(self.nb_diseases)))

    def compute_MICAs(self):

        self.phenotype_lookup.sorted_terms = list(self.phenotype_lookup.term_to_disease_lookup.keys())
        self.phenotype_lookup.sorted_terms.sort()

        n = len(self.phenotype_lookup.sorted_terms)
        self.MICAs = np.empty(shape=(n,n))

        indexA = 0

        for termA in self.phenotype_lookup.sorted_terms:
            #l = [0] * n
            print("A: %s %i %i"%(termA, indexA, n))
            indexB = 0
            for termB in self.phenotype_lookup.sorted_terms:
                #print "A: %s B: %s"%(termA, termB)
                # 0.A 1.B 2.C
                #         0.A 1.B 2.C
                if indexB < indexA:
                    #print "%i %i %s"%(indexA, indexB, termB)
                    self.MICAs[indexA, indexB] = self.MICAs[indexB, indexA]
                elif termA == termB or termA in self.phenotype_lookup.ancestors[termB]:
                    self.MICAs[indexA, indexB] =  self.ICs[termA] #dict(mica=self.ICs[termA], term=termA, type='same')
                elif termB in self.phenotype_lookup.ancestors[termA]:
                    self.MICAs[indexA, indexB] =  self.ICs[termB] # dict(mica=self.ICs[termB], term=termB, type='ancestor')
                else:
                    #print len(self.phenotype_lookup.ancestors[termA])
                    #print ",".join(self.phenotype_lookup.ancestors[termA])
                    common_ancestors = list(set(self.phenotype_lookup.ancestors[termA]).intersection(set(self.phenotype_lookup.ancestors[termB])))
                    values = list([self.ICs[x] for x in common_ancestors])
                    max_index, max_value = max(enumerate(values), key=operator.itemgetter(1))
                    term = common_ancestors[max_index]
                    ''' we don't want to have phenotypic abnormality
					    to be contributing since all terms are phenotypic abnormality
				    '''
                    if term == 'HP:0000118':
                        max_value = 0
                    self.MICAs[indexA, indexB] =  max_value # dict(mica=max_value, term=term, type='max')
                indexB+=1
            indexA+=1

    def sim_dir(self, diseaseA, diseaseB):

        phenotypesA = self.disease_lookup[diseaseA]['phenotypes']
        phenotypesB = self.disease_lookup[diseaseB]['phenotypes']
        set = []
        for termA in phenotypesA:
            indexA = self.phenotype_lookup.sorted_terms.index(termA)
            buffer = []
            for termB in phenotypesB:
                indexB = self.phenotype_lookup.sorted_terms.index(termB)
                mica = self.MICAs[indexA, indexB]
                buffer.append(self.MICAs[indexA, indexB])
            set.append(max(buffer))
        return np.mean(set)

    def compute_disease_similarity(self, diseaseA, diseaseB):
        return float(0.5) * self.sim_dir(diseaseA, diseaseB) + float(0.5) * self.sim_dir(diseaseB, diseaseA)

    def findMICA(self, s, t):
        mica = None
        if s == t or s in hpo.getAncestors(t):
            return dict(mica=ic(s), term=s, type='same')
        elif t in hpo.getAncestors(s):
            return dict(mica=ICs[t], term=t, type='ancestor');  # ic(t);
        else:
            # find the most informative common ancestor
            l = [s, t]
            l.sort()
            key = "".join(l)
            if key in micas:
                return micas[key];
            else:
                # print "%s %s"%(t,s)
                common_ancestors = list(set(ancestors[t].intersection(ancestors[s])))
                # print "%s % s %s"%(s, t, ",".join(common_ancestors))
                values = list([ICs[x] for x in common_ancestors])
                # mica = max(ca_ics)

                max_index, max_value = max(enumerate(values), key=operator.itemgetter(1))
                term = common_ancestors[max_index]
                ''' we don't want to have phenotypic abnormality
					to be contributing since all terms are phenotypic abnormality
				'''
                if term == 'HP:0000118':
                    max_value = 0
                micas[key] = dict(mica=max_value, term=term, type='max')
                return micas[key];
            # return mica;

    def mica2String(mica):
        '''
			This method will convert a set of most informative common ancestors into a string
		:param mica:
		:return:
		'''
        '''
		:param mica:
		:return:
		'''
        # print mica['term']
        # print json.dumps(hpo.getTermById(mica['term']), indent=4)
        if mica['term'] in ['HP:0000118', 'HP:0000001']:
            return None

        hp_class = hpo.getTermById(mica['term'])
        if 'tags' in hp_class and 'name' in hp_class['tags']:
            return "[%s,%s,%s,%f]" % (mica['term'], hp_class['tags']['name'][0], mica['type'], mica['mica'])
        else:
            return "[%s,%s,%s,%f]" % (mica['term'], mica['term'], mica['type'], mica['mica'])

    def micas2String(micas):
        '''
		This method will convert a set of most informative common ancestor to a string
		:param micas:
		:return:
		'''
        return ",".join(filter(partial(operator.is_not, None), [mica2String(x) for x in micas]))



    def simPhenotypes(D1, D2):
        d1d2 = simDir(D1, D2)
        d2d1 = simDir(D2, D1)
        return dict(sim=float(0.5) * d1d2['sim'] + float(0.5) * d2d1['sim'], d1d2=d1d2['phenotypes'],
                    d2d1=d2d1['phenotypes'])
