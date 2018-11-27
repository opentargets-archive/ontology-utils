from builtins import object
import re
import logging
import json
import copy
import io

class Ontology(object):
    def __init__(self):

        #keys are the term ids
        self.terms = dict()
        self.dbxrefs = dict()
        self.altids = dict()
        self.oboNamespace = 'http://purl.obolibrary.org/obo/'
        self.ordoNamespace = 'http://www.orpha.net/ORDO/'
        self.logger = logging.getLogger(__name__)

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
            if re.match('^.+!{1}.+$', value):
                value = value.split("!")[0].strip()
            #print tag + " => " + value + "\n"
            # property_value: http://www.ebi.ac.uk/efo/OMIM_definition_citation OMIM:600807 xsd:string
            if tag == 'xref':
                tag = 'hasDbXref'
                m = re.match("([^\"]+)\".*", value)
                if m:
                    v = m.groups()[0]
                    #print "{0}\n".format(v.rstrip())
                    value = v.rstrip()

            if tag not in list(data.keys()):
                data[tag] = []

            data[tag].append(value)

        return data

    def loadOBOOntology(self, filename, all_relationships=False):

        with io.open(filename, mode='rt', encoding="UTF-8") as oboFile:
            #skip the file header lines
            self.getTerm(oboFile)

            #infinite loop to go through the obo file.
            #Breaks when the term returned is empty, indicating end of file
            while 1:
                #get the term using the two parsing functions
                term = self.parseTagValue(self.getTerm(oboFile))
                if len(term) != 0:
                    termID = term['id'][0];

                    if termID not in list(self.terms.keys()):

                        self.terms[termID] = dict(tags=term)

                        if 'hasDbXref' in term:
                            for xref in term['hasDbXref']:
                                # print " add xref [{0}] ==> {1}\n".format(xref, termID)
                                if not xref in self.dbxrefs:
                                    self.dbxrefs[xref] = []
                                self.dbxrefs[xref].append(termID)
                        if 'alt_id' in term:
                            for alt_id in term['alt_id']:
                                self.altids[alt_id] = termID
                    elif not 'tags' in self.terms[termID]:
                        self.terms[termID]['tags'] = term

                    # Direct acyclic graph to retrieve all the connected nodes
                    if 'dag' not in self.terms[termID]:
                        self.terms[termID]['dag'] = dict()

                    filtered_keys = [elem for elem in list(term.keys()) if elem in ['is_a', 'intersection_of']]

                    for property_key in filtered_keys:

                        reverse_key = 'r_' + property_key
                        #print('Current term:', termID, property_key)

                        if property_key == 'is_a':
                            termParents = [p.split()[0] for p in term[property_key]]
                            if property_key not in self.terms[termID]['dag']:
                                self.terms[termID]['dag'][property_key] = []
                                self.terms[termID]['dag'][reverse_key] = []
                            #append parents of the current term
                            # for every parent term, add this current term as children
                            for termParent in termParents:
                                if termParent not in list(self.terms.keys()):
                                    self.terms[termParent] = dict()
                                    self.terms[termParent]['dag'] = dict()
                                    self.terms[termParent]['dag'][property_key] = []
                                    self.terms[termParent]['dag'][reverse_key] = []
                                    self.terms[termParent]['dag'][reverse_key].append(termID)
                            self.terms[termID]['dag'][property_key] = termParents
                        elif property_key == 'intersection_of':
                            # intersection_of: part_of GO:0006955 ! immune response
                            for p in term[property_key]:
                                if re.match("part_of|regulates|negatively_regulates|positively_regulates|happens_during|starts_during|occurs_in", p):
                                #if any(map(lambda x: p.startswith(x), ['part_of', 'regulates', 'negatively_regulates', 'positively_regulates', 'happens_during', 'starts_during', 'occurs_in'])):
                                    #print('=========='.join(p.split()))
                                    (property_key, object_id) = p.split()
                                    reverse_key = 'r_' + property_key
                                    if 'dag' not in self.terms[termID]:
                                        self.terms[termID]['dag'] = dict()
                                    if property_key not in self.terms[termID]['dag'].keys():
                                        self.terms[termID]['dag'][property_key] = []
                                        self.terms[termID]['dag'][property_key].append(object_id)
                                    if object_id not in list(self.terms.keys()):
                                        self.terms[object_id] = dict()
                                        self.terms[object_id]['dag'] = dict()
                                        self.terms[object_id]['dag'][reverse_key] = []
                                    elif reverse_key not in self.terms[object_id]['dag'].keys():
                                        self.terms[object_id]['dag'][reverse_key] = []
                                    self.terms[object_id]['dag'][reverse_key].append(termID)
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

    def get_all_paths(self, id):
        traversed = set()
        paths = [[id]]
        found_new_node = 1
        while found_new_node > 0:
            found_new_node = 0
            new_paths = []
            self.logger.debug('#paths', len(paths))
            for path in paths:
                self.logger.debug(json.dumps(path, indent=2))
                new_node = path[-1]
                if new_node not in traversed:
                    found_new_node +=1
                    traversed.add(new_node)
                    self.logger.debug('-> ', new_node)
                    for r_key, r_nodes in self.terms[new_node]['dag'].items():
                        if not r_key.startswith('r_'):
                            for r_node_id in r_nodes:
                                new_path = copy.copy(path)
                                new_path.extend([r_key, r_node_id])
                                self.logger.debug('Add ', r_key, r_node_id)
                                self.logger.debug(json.dumps(new_path, indent=2))
                                new_paths.append(new_path)
                else:
                    new_paths.append(path)
            paths = copy.copy(new_paths)
        return paths

    def getDescendents(self, id):
        recursiveArray = [id]
        if id in self.terms:
            children = self.terms[id]['dag']['r_is_a']
            if len(children) > 0:
                for child in children:
                    recursiveArray.extend(self.getDescendents(child))

        return set(recursiveArray)

    def getAncestors(self, id):
        recursiveArray = [id]
        if id in self.terms and 'is_a' in self.terms[id]['dag']:
            parents = self.terms[id]['dag']['is_a']
            if parents and len(parents) > 0:
                for parent in parents:
                    recursiveArray.extend(self.getAncestors(parent))

        return set(recursiveArray)

    def getParents(self, id):
        array = []
        if id in self.terms and 'is_a' in self.terms[id]:
            array = self.terms[id]['is_a']
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
