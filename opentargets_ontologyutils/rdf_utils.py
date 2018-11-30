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

logger = logging.getLogger(__name__)

EFO_TAS = [
    'http://www.ebi.ac.uk/efo/EFO_1000018', # bladder disease
    'http://www.ebi.ac.uk/efo/EFO_0000319', # cardiovascular disease
    'http://www.ebi.ac.uk/efo/EFO_0000405', # digestive system disease
    'http://www.ebi.ac.uk/efo/EFO_0001379', # endocrine
    'http://www.ebi.ac.uk/efo/EFO_0003966', # eye disease
    'http://www.ebi.ac.uk/efo/EFO_0000508', # genetic disorder
    'http://www.ebi.ac.uk/efo/EFO_0000524', # head disease
    'http://www.ebi.ac.uk/efo/EFO_0005803', # henmatological
    'http://www.ebi.ac.uk/efo/EFO_0000540', # immune system disease
    'http://www.ebi.ac.uk/efo/EFO_0003086', # kidney disease
    'http://www.ebi.ac.uk/efo/EFO_0005741', # infection disease
    'http://www.ebi.ac.uk/efo/EFO_0000589', # metabolic disease
    'http://www.ebi.ac.uk/efo/EFO_0000616', # neoplasm
    'http://www.ebi.ac.uk/efo/EFO_0000618', # nervous system
    'http://www.ebi.ac.uk/efo/EFO_0000512', # reproductive system
    'http://www.ebi.ac.uk/efo/EFO_0000684', # respiratory system
    'http://www.ebi.ac.uk/efo/EFO_0002461', # skeletal system
    'http://www.ebi.ac.uk/efo/EFO_0000701', # skin disease
    'http://www.ebi.ac.uk/efo/EFO_0001421', # liver disease
]

HPO_TAS = [
    "http://purl.obolibrary.org/obo/HP_0005386", #"behavior/neurological phenotype",
    "http://purl.obolibrary.org/obo/HP_0005375", #"adipose tissue phenotype",
    "http://purl.obolibrary.org/obo/HP_0005385", #"cardiovascular system phenotype",
    "http://purl.obolibrary.org/obo/HP_0005384", #"cellular phenotype",
    "http://purl.obolibrary.org/obo/HP_0005382", #"craniofacial phenotype",
    "http://purl.obolibrary.org/obo/HP_0005381", #"digestive/alimentary phenotype",
    "http://purl.obolibrary.org/obo/HP_0005380", #"embryo phenotype",
    "http://purl.obolibrary.org/obo/HP_0005379", #"endocrine/exocrine phenotype",
    "http://purl.obolibrary.org/obo/HP_0005378", #"growth/size/body region phenotype",
    "http://purl.obolibrary.org/obo/HP_0005377", #"hearing/vestibular/ear phenotype",
    "http://purl.obolibrary.org/obo/HP_0005397", #"hematopoietic system phenotype",
    "http://purl.obolibrary.org/obo/HP_0005376", #"homeostasis/metabolism phenotype",
    "http://purl.obolibrary.org/obo/HP_0005387", #"immune system phenotype",
    "http://purl.obolibrary.org/obo/HP_0010771", #"integument phenotype",
    "http://purl.obolibrary.org/obo/HP_0005371", #"limbs/digits/tail phenotype",
    "http://purl.obolibrary.org/obo/HP_0005370", #"liver/biliary system phenotype",
    "http://purl.obolibrary.org/obo/HP_0010768", #"mortality/aging",
    "http://purl.obolibrary.org/obo/HP_0005369", #"muscle phenotype",
    "http://purl.obolibrary.org/obo/HP_0002006", #"neoplasm",
    "http://purl.obolibrary.org/obo/HP_0003631", #"nervous system phenotype",
    "http://purl.obolibrary.org/obo/HP_0002873", #"normal phenotype",
    "http://purl.obolibrary.org/obo/HP_0001186", #"pigmentation phenotype",
    "http://purl.obolibrary.org/obo/HP_0005367", #"renal/urinary system phenotype",
    "http://purl.obolibrary.org/obo/HP_0005389", #"reproductive system phenotype",
    "http://purl.obolibrary.org/obo/HP_0005388", #"respiratory system phenotype",
    "http://purl.obolibrary.org/obo/HP_0005390", #"skeleton phenotype",
    "http://purl.obolibrary.org/obo/HP_0005394", #"taste/olfaction phenotype",
    "http://purl.obolibrary.org/obo/HP_0005391", #"vision/eye phenotype"
]

'''
subclass generators: yield a series of values
'''
def _get_subclass_of(arg, graph):
    
    node = arg[0]
    depth = arg[1]
    path = arg[2]
    level = arg[3]
    logger.debug("Superclass: %s; label: %s; depth: %i"%(str(node.identifier), node.value(RDFS.label), depth))

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
        self.rdf_graph.parse(uri, format='xml')

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
                logger.debug("WARNING: Obsolete %s %s '%s' %s" % (uri, label, reason_for_obsolescence, new_uri))

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
                    logger.warn("%s => %s" % (old_uri, self.obsoletes[old_uri]))
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

            # logger.debug("RDFLIB '%s' '%s'" % (uri, label))
        logger.debug("parsed %i classes"%count)

    def get_top_levels(self, base_class=None):

        sparql_query = '''
        select DISTINCT ?top_level ?top_level_label
        {
          ?top_level rdfs:subClassOf <%s> .
          ?top_level rdfs:label ?top_level_label
        }
        '''
        qres = self.rdf_graph.query(sparql_query % base_class)

        for row in qres:
            uri = str(row[0])
            label = str(row[1])
            self.top_level_classes[uri] = label

    def get_children(self, uri):

        disease_uri = URIRef(uri)
        if uri not in self.children:
            self.children[uri] = []
        for c in self.rdf_graph.subjects(predicate=RDFS.subClassOf, object=disease_uri):
            cr = rdflib.resource.Resource(self.rdf_graph, c)
            label = str(cr.value(RDFS.label))
            c_uri = str(cr.identifier)
            (prefix, namespace, id) = self.rdf_graph.namespace_manager.compute_qname(cr.identifier)
            self.children[uri].append({'code': id, 'label': label})

    def get_new_from_obsolete_uri(self, old_uri):

        next_uri = self.obsoletes[old_uri]['new_uri']
        while next_uri in list(self.obsoletes.keys()):
            next_uri = self.obsoletes[next_uri]['new_uri']
        if next_uri in self.current_classes:
            new_label = self.current_classes[next_uri]
            logger.warn("%s => %s" % (old_uri, self.obsoletes[old_uri]))
            return next_uri
        else:
            return None

    def get_classes_paths(self, root_uri, level=0):

        root_node = rdflib.resource.Resource(self.rdf_graph,
                                             rdflib.term.URIRef(root_uri))

        # create an entry for the root:
        root_node_uri = str(root_node.identifier)
        self.classes_paths[root_node_uri] = {'all': [], 'labels': [], 'ids': []}
        self.classes_paths[root_node_uri]['all'].append([{'uri': str(root_node_uri), 'label': root_node.value(RDFS.label)}])
        self.classes_paths[root_node_uri]['labels'].append([root_node.value(RDFS.label)])
        (prefix, namespace, id) = self.rdf_graph.namespace_manager.compute_qname(root_node.identifier)
        self.classes_paths[root_node_uri]['ids'].append([id])

        for entity in self.rdf_graph.transitiveClosure(_get_subclass_of, (root_node, 0, (), level)):

            node = entity[0]
            depth = entity[1]
            path = entity[2]

            node_uri = str(node.identifier)

            if node_uri not in self.classes_paths:
                self.classes_paths[node_uri] = { 'all': [], 'labels': [], 'ids': [] }

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

            self.classes_paths[node_uri]['all'].append(all_struct)
            self.classes_paths[node_uri]['labels'].append(labels_struct)
            self.classes_paths[node_uri]['ids'].append(ids_struct)

        return

    def parse_properties(self, rdf_node):
        logger.debug("parse_properties for rdf_node: {}".format(rdf_node))
        raw_properties = list(self.rdf_graph.predicate_objects(subject=rdf_node))
        rdf_properties = dict()
        logger.debug("raw_properties for rdf_node: {}".format(rdf_node))
        for index, property in enumerate(raw_properties):
            logger.debug("{}. {}".format(index, property))
            property_name = str(property[0])
            property_value = str(property[1])
            # rdf_properties[property_name].append(property_value)
            if property_name in rdf_properties:
                rdf_properties[property_name].append(property_value)
            else:
                rdf_properties[property_name] = [property_value]
        return rdf_properties

    def load_hpo_classes(self, uri):
        """Loads the HPO graph and extracts the current and obsolete classes.
           Status: production
        """
        logger.debug("load_hpo_classes...")

        self.load_ontology_graph(uri)

        base_class = 'http://purl.obolibrary.org/obo/HP_0000118'
        self.load_ontology_classes(base_class=base_class)
        self.get_deprecated_classes()
        self.get_top_levels(base_class= base_class)

    def load_mp_classes(self, uri):
        """Loads the HPO graph and extracts the current and obsolete classes.
           Status: production
        """
        logger.debug("load_mp_classes...")

        self.load_ontology_graph(uri)
        base_class = 'http://purl.obolibrary.org/obo/MP_0000001'
        self.load_ontology_classes(base_class= base_class)
        self.get_deprecated_classes()
        self.get_top_levels(base_class= base_class)

        #self.get_ontology_top_levels(base_class, top_level_map=self.phenotype_top_levels)

    def load_efo_classes(self, uri, lightweight=False, uberon_uri=None):
        """Loads the EFO graph and extracts the current and obsolete classes.
           Status: production
        """
        logger.debug("load_efo_classes...")

        print("load EFO classes...")

        self.load_ontology_graph(uri)

        if uberon_uri:
            logger.debug("load Uberon classes...")
            print("load Uberon classes...")
            self.load_ontology_graph(uberon_uri)

        print("Done")
        if lightweight == True:
            return

        # load disease, phenotype, measurement, biological process, function and injury and mental health
        for base_class in [ 'http://www.ebi.ac.uk/efo/EFO_0000408',
                            'http://www.ebi.ac.uk/efo/EFO_0000651',
                            'http://www.ebi.ac.uk/efo/EFO_0001444',
                            'http://purl.obolibrary.org/obo/GO_0008150',
                            'http://www.ifomis.org/bfo/1.1/snap#Function',
                            'http://www.ebi.ac.uk/efo/EFO_0000546',
                            'http://www.ebi.ac.uk/efo/EFO_0003935' ]:
            self.load_ontology_classes(base_class=base_class)
            self.get_top_levels(base_class=base_class)
        self.get_deprecated_classes()


    #TODO this should be a static method
    def get_hpo(self, uri):
        '''
        Load HPO to accept phenotype terms that are not in EFO
        :return:
        '''
        obj = OntologyClassReader()
        obj.load_hpo_classes(uri)
        obj.rdf_graph = None
        return obj

    #TODO this should be a static method
    def get_mp(self, uri):
        '''
        Load MP to accept phenotype terms that are not in EFO
        :return:
        '''
        obj = None
        obj = OntologyClassReader()
        obj.load_mp_classes(uri)
        obj.rdf_graph = None
        return obj

    #TODO this should be a static method
    def get_efo(self, uri):
        '''
        Load EFO current and obsolete classes to report them to data providers
        :return:
        '''
        obj = OntologyClassReader()
        obj.load_efo_classes(uri)
        obj.rdf_graph = None
        return obj

    def load_open_targets_disease_ontology(self, efo_uri):
        """Loads the EFO graph and extracts the current and obsolete classes.
           Generates the therapeutic areas
           Creates the other disease class
           Move injury under other disease
           Status: production
        """
        logger.debug("load_open_targets_disease_ontology...")
        self.load_ontology_graph(efo_uri)
        all_ns = [n for n in self.rdf_graph.namespace_manager.namespaces()]

        self.get_deprecated_classes(obsoleted_in_version=True)

        '''
        get the original top_levels from EFO
        '''
        self.get_top_levels(base_class='http://www.ebi.ac.uk/efo/EFO_0000408')

        '''
        Detach the TAs from the disease node
        and load all the classes
        '''
        disease_uri = URIRef('http://www.ebi.ac.uk/efo/EFO_0000408')
        for base_class in EFO_TAS:
            uri = URIRef(base_class)
            self.rdf_graph.remove((uri, None, disease_uri))
            self.load_ontology_classes(base_class=base_class)
            self.get_classes_paths(root_uri=base_class, level=0)

        '''
        Create an other disease node
        '''
        cttv = Namespace(str("http://www.targetvalidation.org/disease"))

        # namespace_manager = NamespaceManager(self.rdf_graph)
        self.rdf_graph.namespace_manager.bind('cttv', cttv)

        '''
        Some diseases have no categories, let's create a category for them
        '''
        other_disease_uri = URIRef('http://www.targetvalidation.org/disease/other')
        self.rdf_graph.add((other_disease_uri, RDF.type, rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#Class')))
        self.rdf_graph.add([other_disease_uri, RDFS.label, rdflib.Literal('other disease')])

        '''
        Get all children of 'disease' and assign them to 'other disease'
        '''
        for c in self.rdf_graph.subjects(predicate=RDFS.subClassOf, object=disease_uri):
            self.rdf_graph.add([c, RDFS.subClassOf, other_disease_uri])

        '''
        Move 'injury' under 'other disease'
        injuries are treated with medication recorded in ChEMBL
        Move 'mental health' under 'other disease'
        '''
        self.rdf_graph.add([URIRef('http://www.ebi.ac.uk/efo/EFO_0000546'), RDFS.subClassOf, other_disease_uri])
        self.rdf_graph.add([URIRef('http://www.ebi.ac.uk/efo/EFO_0003935'), RDFS.subClassOf, other_disease_uri])


        # other disease, phenotype, measurement, biological process, function
        for base_class in [ 'http://www.targetvalidation.org/disease/other',
                            'http://www.ebi.ac.uk/efo/EFO_0000651',
                            'http://www.ebi.ac.uk/efo/EFO_0001444',
                            'http://purl.obolibrary.org/obo/GO_0008150',
                            'http://www.ifomis.org/bfo/1.1/snap#Function']:

            self.load_ontology_classes(base_class=base_class)
            self.get_classes_paths(root_uri=base_class, level=0)

    def load_mammalian_phenotype_ontology(self, uri):
        """
            Loads the MP graph and extracts the current and obsolete classes.
            Status: production
        """
        logger.debug("load_mammalian_phenotype_ontology...")
        self.load_ontology_graph(uri)

        all_ns = [n for n in self.rdf_graph.namespace_manager.namespaces()]

        '''
        Detach the anatomical system from the mammalian phenotype node
        and load all the classes
        '''

        mp_root_uri = 'http://purl.obolibrary.org/obo/MP_0000001'
        mp_root_uriref = URIRef(mp_root_uri)
        self.get_children(mp_root_uri)

        for child in self.children[mp_root_uri]:
            print("%s %s..."%(child['code'], child['label']))
            uri = "http://purl.obolibrary.org/obo/" + child['code']
            uriref = URIRef(uri)
            self.rdf_graph.remove((uriref, None, mp_root_uriref))
            self.load_ontology_classes(base_class=uri)
            self.get_classes_paths(root_uri=uri, level=0)
            print(len(self.current_classes))

    def load_evidence_classes(self, uri_so, uri_eco):
        '''
        Loads evidence from ECO, SO and the Open Targets evidence classes
        :return:
        '''
        self.load_ontology_graph(uri_so)
        self.load_ontology_graph(uri_eco)

        evidence_uri = URIRef('http://purl.obolibrary.org/obo/ECO_0000000')

        # for triple in self.rdf_graph.triples((evidence_uri, None, None)):
        #      logger.debug(triple)

        '''
            Open Targets specific evidence:
            A) Create namespace for OT evidence
            B) Add Open Targets evidence terms to graph
            C) Traverse the graph breadth first
        '''

        cttv = Namespace(str("http://www.targetvalidation.org/disease"))
        ot = Namespace(str("http://identifiers.org/eco"))

        #namespace_manager = NamespaceManager(self.rdf_graph)
        self.rdf_graph.namespace_manager.bind('cttv', cttv)
        self.rdf_graph.namespace_manager.bind('ot',ot)

        open_targets_terms = {
            'http://www.targetvalidation.org/disease/cttv_evidence':'CTTV evidence',
            'http://identifiers.org/eco/drug_disease':'drug-disease evidence',
            'http://identifiers.org/eco/target_drug':'biological target to drug evidence',
            'http://identifiers.org/eco/clinvar_gene_assignments':'ClinVAR SNP-gene pipeline',
            'http://identifiers.org/eco/cttv_mapping_pipeline':'CTTV-custom annotation pipeline',
            'http://identifiers.org/eco/GWAS':'Genome-wide association study evidence',
            'http://identifiers.org/eco/GWAS_fine_mapping': 'Fine-mapping study evidence',
            'http://identifiers.org/eco/somatic_mutation_evidence':'Somatic mutation evidence',
            'http://www.targetvalidation.org/evidence/genomics_evidence':'genomics evidence',
            'http://targetvalidation.org/sequence/nearest_gene_five_prime_end':'Nearest gene counting from 5&apos; end',
            'http://targetvalidation.org/sequence/regulatory_nearest_gene_five_prime_end':'Nearest regulatory gene from 5&apos; end',
            'http://www.targetvalidation.org/evidence/literature_mining':'Literature mining',
            'http://www.targetvalidation.org/provenance/DatabaseProvenance':'database provenance',
            'http://www.targetvalidation.org/provenance/ExpertProvenance':'expert provenance',
            'http://www.targetvalidation.org/provenance/GWAS_SNP_to_trait_association':'GWAS SNP to trait association',
            'http://www.targetvalidation.org/provenance/LiteratureProvenance':'literature provenance',
            'http://www.targetvalidation.org/provenance/disease_to_phenotype_association':'disease to phenotype association',
            'http://www.targetvalidation.org/provenance/gene_to_disease_association':'gene to disease association'
        }

        for uri, label in open_targets_terms.items():
            u = URIRef(uri)
            self.rdf_graph.add((u, RDF.type, rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#Class')))
            self.rdf_graph.add([u, RDFS.label, rdflib.Literal(label)])
            self.rdf_graph.add([u, RDFS.subClassOf, evidence_uri])

        u = URIRef('http://identifiers.org/eco/target_drug')
        # for triple in self.rdf_graph.triples((u, None, None)):
        #      logger.debug(triple)

        #(a, b, c) = self.rdf_graph.namespace_manager.compute_qname(unicode('http://identifiers.org/eco/target_drug'))
        #logger.debug(c)
        #return
        # Add the bits specific to Open Targets
        # 'Open Targets evidence' ?
        # 'biological target-disease association via drug' ECO:0000360
        # 'drug-disease evidence' http://identifiers.org/eco/drug_disease SubclassOf 'biological target-disease association via drug'
        # 'biological target to drug evidence' http://identifiers.org/eco/target_drug SubclassOf 'biological target-disease association via drug'
        # ClinVAR SNP-gene pipeline http://identifiers.org/eco/clinvar_gene_assignments SubclassOf ECO:0000246
        # CTTV-custom annotation pipeline http://identifiers.org/eco/cttv_mapping_pipeline SubclassOf ECO:0000246

        for base_class in ['http://purl.obolibrary.org/obo/ECO_0000000', 'http://purl.obolibrary.org/obo/SO_0000400', 'http://purl.obolibrary.org/obo/SO_0001260', 'http://purl.obolibrary.org/obo/SO_0000110', 'http://purl.obolibrary.org/obo/SO_0001060' ]:
            self.load_ontology_classes(base_class=base_class)
            self.get_classes_paths(root_uri=base_class, level=0)

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
            logger.debug("%s (%s) hasPhenotype %s (%s)" % (disease_uri, disease_label, phenotype_uri, phenotype_label))
            if disease_uri not in disease_phenotypes_map:
                disease_phenotypes_map[disease_uri] = { 'label': disease_label, 'phenotypes': [] }
            if phenotype_uri not in [x['uri'] for x in disease_phenotypes_map[disease_uri]['phenotypes']]:
                disease_phenotypes_map[disease_uri]['phenotypes'].append({'label': phenotype_label, 'uri': phenotype_uri})

        return disease_phenotypes_map
