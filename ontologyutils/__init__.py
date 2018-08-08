import re
import sys
#reload(sys);
#sys.setdefaultencoding("utf8");

class Ontology(object):
    def __init__(self):

        #keys are the term ids
        self.terms = dict()
        self.dbxrefs = dict()
        self.altids = dict()
        self.oboNamespace = 'http://purl.obolibrary.org/obo/'
        self.ordoNamespace = 'http://www.orpha.net/ORDO/'

    @classmethod
    def fromOBOFile(cls, filename):
        obj = cls()
        obj.loadOBOOntology(filename)
        return obj

    def parseTagValue(self, term):
        data = dict()
        for line in term:
            tag = line.split(': ',1)[0]
            # calculate the length of the first split
            #value = line[len(tag)+2:]
            value = line.split(': ',1)[1]
            if re.match("!", value):
                value = value.split("!")[0]
            #print tag + " => " + value + "\n"
            # property_value: http://www.ebi.ac.uk/efo/OMIM_definition_citation OMIM:600807 xsd:string
            if tag == 'xref':
                tag = 'hasDbXref'
                m = re.match("([^\"]+)\".*", value)
                if m:
                    v = m.groups()[0]
                    #print "{0}\n".format(v.rstrip())
                    value = v.rstrip()
                
            if tag not in data.keys():
                data[tag] = []

            data[tag].append(value)

        return data      
     
    def loadOBOOntology(self, filename):
        #oboFile = open('C:\Users\gk680303\Documents\ontologies\hp.obo','r')
        oboFile = open(filename, mode='rt', encoding='utf-8')
        #skip the file header lines
        self.getTerm(oboFile)

        #infinite loop to go through the obo file.
        #Breaks when the term returned is empty, indicating end of file
        while 1:
          #get the term using the two parsing functions
          term = self.parseTagValue(self.getTerm(oboFile))
          if len(term) != 0:
            termID = term['id'][0];

            #only add to the structure if the term has a is_a tag
            #the is_a value contain GOID and term definition
            #we only want the GOID
            if 'is_a' in term.keys():
              termParents = [p.split()[0] for p in term['is_a']]

              if termID not in self.terms.keys():
                #each goid will have two arrays of parents and children
                self.terms[termID] = {'p':[],'c':[], 'tags':term}
                # reverse dictionnary from xref to term
                if 'hasDbXref' in term:
                    for xref in term['hasDbXref']:
                        #print " add xref [{0}] ==> {1}\n".format(xref, termID)
                        if not xref in self.dbxrefs:
                            self.dbxrefs[xref] = []
                        self.dbxrefs[xref].append(termID)
                if 'alt_id' in term:
                  for alt_id in term['alt_id']:
                    self.altids[alt_id] = termID
              elif not 'tags' in self.terms[termID]:
                self.terms[termID]['tags'] = term
              #append parents of the current term
              self.terms[termID]['p'] = termParents

              #for every parent term, add this current term as children
              for termParent in termParents:
                if termParent not in self.terms.keys():
                  self.terms[termParent] = {'p':[],'c':[]}
                self.terms[termParent]['c'].append(termID)
          else:
            break    

    def getTermsByDbXref(self, xref):
        result = None
        #print "{0}\n".format()
        if (xref in self.dbxrefs):
            result = self.dbxrefs[xref]
        return result

    def getTermById(self, id):
        result = None
        #print "{0}\n".format()
        if (id in self.terms):
            result = self.terms[id]
        elif (id in self.altids):
            result = self.terms[self.altids[id]]
        return result

    def getDescendents(self, goid):
        recursiveArray = [goid]
        if self.terms.has_key(goid):
            children = self.terms[goid]['c']
            if len(children) > 0:
              for child in children:
                recursiveArray.extend(self.getDescendents(child))

        return set(recursiveArray)

    def getAncestors(self, id):
        recursiveArray = [id]
        if id in self.terms and 'p' in self.terms[id]:
            parents = self.terms[id]['p']
            if parents and len(parents) > 0:
                for parent in parents:
                    recursiveArray.extend(self.getAncestors(parent))

        return set(recursiveArray)

    def getParents(self, id):
        array = []
        if id in self.terms and 'p' in self.terms[id]:
            array = self.terms[id]['p']
        return array
        
    def getTerm(self, stream):
        block = []
        for line in stream:
            if line.strip() == "[Term]" or line.strip() == "[Typedef]":
              break
            else:
              if line.strip() != "":
                block.append(line.strip())

        return block
