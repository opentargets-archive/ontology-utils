from __future__ import print_function
from builtins import str
from builtins import object
import copy
import re
import sys
import os
import gzip
import pickle
import logging
import rdflib
import requests
from rdflib import URIRef
from rdflib.namespace import Namespace
from rdflib.namespace import RDF, RDFS
from datetime import date
from opentargets_urlzsource import URLZSource

logger = logging.getLogger(__name__)


'''
subclass generators: yield a series of values
'''
def _get_subclass_of(arg, graph):
    
    node = arg[0]
    depth = arg[1]
    path = arg[2]
    level = arg[3]
    #logger.debug("Superclass: %s; label: %s; depth: %i"%(str(node.identifier), node.value(RDFS.label), depth))

    if level > 0 and depth == level:
        return
    for c in graph.subjects(predicate=RDFS.subClassOf, object=node.identifier):

        cr = rdflib.resource.Resource(graph, c)
        if cr.identifier == node.identifier:
            logger.warning("self reference on {} skipping".format(node.identifier))
            continue

        yield (cr, depth+1, path + (node,), level)

class OntologyClassReader(object):

    def __init__(self):
        """Initialises the class

        Declares an RDF graph that will contain an ontology representation.
        Current classes are extracted in the current_classes dictionary
        Obsolete classes are extracted in the obsolete_classes dictionary
        """
        self.rdf_graph = rdflib.Graph()
        self.current_classes = dict()
        self.obsolete_classes = dict()
        self.top_level_classes = dict()
        self.disease_locations = dict()
        self.classes_paths = dict()
        self.obsoletes = dict()
        self.children = dict()

    def load_ontology_graph(self, uri):
        """Loads the ontology from a URI in a RDFLib graph.

        Given a uri pointing to a OWL file, load the ontology representation in a graph.

        Args:
            uri (str): the URI for the ontology representation in OWL.

        Returns:
            None

        Raises:
            None

        """
        with URLZSource(uri).open() as source:
            self.rdf_graph.parse(file = source, format='xml')

    def get_deprecated_classes(self, obsoleted_in_version=False):

        count = 0

        # do this once
        if len(self.obsoletes) == 0:

            sparql_query = '''
                SELECT DISTINCT ?ont_node ?label ?label ?ont_new
                {
                    ?ont_node owl:deprecated true .
                    ?ont_node obo:IAO_0100001 ?ont_new_id .
                    ?ont_new oboInOwl:id ?ont_new_id .
                    ?ont_node rdfs:label ?label
                }
                '''

            if obsoleted_in_version:

                sparql_query = '''
                    SELECT DISTINCT ?ont_node ?label ?reason ?ont_new_id
                    {
                    ?ont_node rdfs:subClassOf oboInOwl:ObsoleteClass . 
                    ?ont_node obo:IAO_0100001 ?ont_new_id .
                    ?ont_node rdfs:label ?label . 
                    ?ont_node efo:reason_for_obsolescence ?reason
                    }
                    '''

                '''
                <rdfs:subClassOf rdf:resource="http://www.geneontology.org/formats/oboInOwl#ObsoleteClass"/>
                <obo:IAO_0100001 rdf:datatype="http://www.w3.org/2001/XMLSchema#string">http://www.ebi.ac.uk/efo/EFO_0002067</obo:IAO_0100001>
                <efo:obsoleted_in_version>2.44</efo:obsoleted_in_version>
                <efo:reason_for_obsolescence>Duplicate with class K562 http://www.ebi.ac.uk/efo/EFO_0002067</efo:reason_for_obsolescence>
                '''

            qres = self.rdf_graph.query(sparql_query)

            for (ont_node, ont_label, ont_reason, ont_new_id) in qres:
                uri = str(ont_node)
                label = str(ont_label)
                reason_for_obsolescence = str(ont_reason)
                # unfortunately there may be some trailing spaces!
                new_uri = str(ont_new_id).strip()
                # point to the new URI
                self.obsoletes[uri] = {'label': label,
                                       'new_uri': new_uri,
                                       'reason_for_obsolescence': reason_for_obsolescence,
                                       'processed': False}
                count +=1
                logger.debug("Obsoleted %s %s '%s' use %s" % (uri, label, reason_for_obsolescence, new_uri))

        """
        Still need to loop over to find the next new class to replace the
        old URI with the latest URI (some intermediate classes can be obsolete too)
        """

        for old_uri, record in list(self.obsoletes.items()):
            if not record['processed']:
                next_uri = self.obsoletes[old_uri]['new_uri']
                next_reason = self.obsoletes[old_uri]['reason_for_obsolescence']
                while next_uri in list(self.obsoletes.keys()):
                    prev_uri = next_uri
                    next_uri = self.obsoletes[prev_uri]['new_uri']
                    if next_uri == prev_uri:
                        break
                    next_reason = self.obsoletes[prev_uri]['reason_for_obsolescence']
                if next_uri in self.current_classes:
                    new_label = self.current_classes[next_uri]
                    self.obsolete_classes[old_uri] = "Use %s label:%s (reason: %s)" % (next_uri, new_label, next_reason)
                else:
                    # load the class
                    self.obsolete_classes[old_uri] = next_reason
                # mark the record as processed
                record['processed'] = True

        return count

    def load_ontology_classes(self, base_class=None):
        """Loads all current and obsolete classes from an ontology stored in RDFLib

        Given a base class in the ontology, extracts the classes and stores the sets of
        current and obsolete classes in dictionaries. This avoids traversing all the graph
        if only a few branches are required.

        Args:
            base_classes (list of str): the root(s) of the ontology to start from.

        Returns:
            None

        Raises:
            None

        """
        sparql_query = '''
        SELECT DISTINCT ?ont_node ?label
        {
        ?ont_node rdfs:subClassOf* <%s> .
        ?ont_node rdfs:label ?label
        }
        '''

        count = 0
        qres = self.rdf_graph.query(sparql_query % base_class)

        for (ont_node, ont_label) in qres:
            uri = str(ont_node)
            label = str(ont_label)
            self.current_classes[uri] = label
            count +=1

            '''
             Add the children too
            '''
            self.get_children(uri=uri)

        logger.debug("parsed %i classes"%count)

    def get_children(self, uri):

        disease_uri = URIRef(uri)
        if uri not in self.children:
            self.children[uri] = []
        for c in self.rdf_graph.subjects(predicate=RDFS.subClassOf, object=disease_uri):
            cr = rdflib.resource.Resource(self.rdf_graph, c)
            label = str(cr.value(RDFS.label))
            (prefix, namespace, id) = self.rdf_graph.namespace_manager.compute_qname(cr.identifier)
            self.children[uri].append({'code': id, 'label': label})

    def get_new_from_obsolete_uri(self, old_uri):

        next_uri = self.obsoletes[old_uri]['new_uri']
        while next_uri in list(self.obsoletes.keys()):
            next_uri = self.obsoletes[next_uri]['new_uri']
        if next_uri in self.current_classes:
            return next_uri
        else:
            return None

    """
    retuns a dictionary where keys are iris that are subclasses of the root uri
    and the value is a dictionary 
    """
    def get_classes_paths(self, root_uri, level=0):

        root_node = rdflib.resource.Resource(self.rdf_graph,
                                             rdflib.term.URIRef(root_uri))

        # create an entry for the root:
        root_node_uri = str(root_node.identifier)

        classes_paths = {}
        classes_paths[root_node_uri] = {'all': [], 'labels': [], 'ids': []}
        classes_paths[root_node_uri]['all'].append([{'uri': str(root_node_uri), 'label': root_node.value(RDFS.label)}])
        classes_paths[root_node_uri]['labels'].append([root_node.value(RDFS.label)])
        (prefix, namespace, id) = self.rdf_graph.namespace_manager.compute_qname(root_node.identifier)
        classes_paths[root_node_uri]['ids'].append([id])

        for entity in self.rdf_graph.transitiveClosure(_get_subclass_of, (root_node, 0, (), level)):

            node = entity[0]
            depth = entity[1]
            path = entity[2]

            node_uri = str(node.identifier)

            if node_uri not in classes_paths:
                classes_paths[node_uri] = { 'all': [], 'labels': [], 'ids': [] }

            all_struct = []
            labels_struct = []
            ids_struct = []

            for n in path:
                all_struct.append({'uri': str(n.identifier), 'label': n.value(RDFS.label)})
                labels_struct.append( n.value(RDFS.label) )
                (prefix, namespace, id) = self.rdf_graph.namespace_manager.compute_qname(n.identifier)
                ids_struct.append( id )

            all_struct.append( {'uri': str(node_uri), 'label': node.value(RDFS.label)} )
            labels_struct.append( node.value(RDFS.label) )
            (prefix, namespace, id) = self.rdf_graph.namespace_manager.compute_qname(node.identifier)
            ids_struct.append( id )

            classes_paths[node_uri]['all'].append(all_struct)
            classes_paths[node_uri]['labels'].append(labels_struct)
            classes_paths[node_uri]['ids'].append(ids_struct)

        return classes_paths

    def parse_properties(self, rdf_node):
        #logger.debug("parse_properties for rdf_node: {}".format(rdf_node))
        raw_properties = list(self.rdf_graph.predicate_objects(subject=rdf_node))
        rdf_properties = dict()
        #logger.debug("raw_properties for rdf_node: {}".format(rdf_node))
        for index, property in enumerate(raw_properties):
            #logger.debug("{}. {}".format(index, property))
            property_name = str(property[0])
            property_value = str(property[1])
            if property_name in rdf_properties:
                rdf_properties[property_name].append(property_value)
            else:
                rdf_properties[property_name] = [property_value]
        return rdf_properties




class DiseaseUtils(object):

    def __init__(self):
        pass

    def get_disease_phenotypes(self, ontologyclassreader, uri_hpo, uri_mp, uri_disease_phenotypes):

        disease_phenotypes_map = dict()


        # load HPO:
        logger.debug("Merge HPO graph")
        ontologyclassreader.load_ontology_graph(uri_hpo)
        logger.debug("Merge MP graph")
        ontologyclassreader.load_ontology_graph(uri_mp)

        for key, uri in uri_disease_phenotypes:
            logger.debug("merge phenotypes from %s" % uri)
            ontologyclassreader.rdf_graph.parse(uri, format='xml')

        qres = ontologyclassreader.rdf_graph.query(
            """
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            PREFIX oban: <http://purl.org/oban/>
            select DISTINCT ?disease_id ?disease_label ?phenotype_id ?phenotype_label
            where {
              ?code oban:association_has_subject ?disease_id .
              ?disease_id rdfs:label ?disease_label .
              ?code oban:association_has_object ?phenotype_id .
              ?phenotype_id rdfs:label ?phenotype_label
            }
            """
        )

        '''
        Results are tuple of values
        '''
        for rdisease_uri, rdisease_label, rphenotype_uri, rphenotype_label in qres:
            (disease_uri, disease_label, phenotype_uri, phenotype_label) = (str(rdisease_uri), str(rdisease_label), str(rphenotype_uri), str(rphenotype_label))
            #logger.debug("%s (%s) hasPhenotype %s (%s)" % (disease_uri, disease_label, phenotype_uri, phenotype_label))
            if disease_uri not in disease_phenotypes_map:
                disease_phenotypes_map[disease_uri] = { 'label': disease_label, 'phenotypes': [] }
            if phenotype_uri not in [x['uri'] for x in disease_phenotypes_map[disease_uri]['phenotypes']]:
                disease_phenotypes_map[disease_uri]['phenotypes'].append({'label': phenotype_label, 'uri': phenotype_uri})

        return disease_phenotypes_map


def merge_classes_paths(a,b):
    result = {}
    for src in a,b:
        for uri in src:
            if uri not in result:
                result[uri] = {'all': [], 'labels': [], 'ids': []}
            result[uri]['all'].extend(src[uri]['all'])
            result[uri]['labels'].extend(src[uri]['labels'])
            result[uri]['ids'].extend(src[uri]['ids'])
    return result