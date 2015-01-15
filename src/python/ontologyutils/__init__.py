import re
class Ontology(object):
  def __init__(self):
  
    #keys are the term ids
    self.terms = {}
    self.dbxrefs = {}
    self.oboNamespace = 'http://purl.obolibrary.org/obo/'
    self.ordoNamespace = 'http://www.orpha.net/ORDO/'
    
  @classmethod
  def fromOBOFile(cls, filename):
    obj = cls()
    obj.loadOBOOntology(filename)
    return obj
    
  def parseTagValue(self, term):
    data = {}
    for line in term:
        tag = line.split(': ',1)[0]
        value = line.split(': ',1)[1]
        #print tag + " => " + value + "\n"
        if tag == 'xref':
            tag = 'hasDbXref'
            m = re.match("([^\"]+)\".*", value)
            if m:
                v = m.groups()[0]
                print "{0}\n".format(v.rstrip())
                value = v.rstrip()
            
        if not data.has_key(tag):
            data[tag] = []


        data[tag].append(value)

    return data      
     
  def loadOBOOntology(self, filename):
    #oboFile = open('C:\Users\gk680303\Documents\ontologies\hp.obo','r')
    oboFile = open(filename,'r')
    #skip the file header lines
    self.getTerm(oboFile)

    #infinite loop to go through the obo file.
    #Breaks when the term returned is empty, indicating end of file
    while 1:
      #get the term using the two parsing functions
      term = self.parseTagValue(self.getTerm(oboFile))
      if len(term) != 0:
        termID = term['id'][0]

        #only add to the structure if the term has a is_a tag
        #the is_a value contain GOID and term definition
        #we only want the GOID
        if term.has_key('is_a'):
          termParents = [p.split()[0] for p in term['is_a']]

          if not self.terms.has_key(termID):
            #each goid will have two arrays of parents and children
            self.terms[termID] = {'p':[],'c':[], 'tags':term}
            # reverse dictionnary from xref to term
            if 'hasDbXref' in term:
                for xref in term['hasDbXref']:
                    print " add xref [{0}] ==> {1}\n".format(xref, termID)
                    if not xref in self.dbxrefs:
                        self.dbxrefs[xref] = []
                    self.dbxrefs[xref].append(termID)

          #append parents of the current term
          self.terms[termID]['p'] = termParents

          #for every parent term, add this current term as children
          for termParent in termParents:
            if not self.terms.has_key(termParent):
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
    
  def getDescendents(self, goid):
    recursiveArray = [goid]
    if self.terms.has_key(goid):
        children = self.terms[goid]['c']
        if len(children) > 0:
          for child in children:
            recursiveArray.extend(self.getDescendents(child))

    return set(recursiveArray)

  def getAncestors(self, goid):
    recursiveArray = [goid]
    if self.terms.has_key(goid):
      parents = self.terms[goid]['p']
    if len(parents) > 0:
        for parent in parents:
          recursiveArray.extend(self.getAncestors(parent))

    return set(recursiveArray)
  
  def getTerm(self, stream):
    block = []
    for line in stream:
        if line.strip() == "[Term]" or line.strip() == "[Typedef]":
          break
        else:
          if line.strip() != "":
            block.append(line.strip())

    return block
 