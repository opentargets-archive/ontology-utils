from __future__ import print_function

import logging

import rdflib

from opentargets_ontologyutils.rdf_utils import OntologyClassReader

logger = logging.getLogger(__name__)

#thereaputic areas used by opentargets
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

def get_efo(uri):
    '''
    Load EFO current and obsolete classes to report them to data providers
    :return:
    '''
    obj = OntologyClassReader()

    obj.load_ontology_graph(uri)

    # load disease, phenotype, measurement, biological process, function and injury and mental health
    for base_class in [ 'http://www.ebi.ac.uk/efo/EFO_0000408',
                        'http://www.ebi.ac.uk/efo/EFO_0000651',
                        'http://www.ebi.ac.uk/efo/EFO_0001444',
                        'http://purl.obolibrary.org/obo/GO_0008150',
                        'http://www.ifomis.org/bfo/1.1/snap#Function',
                        'http://www.ebi.ac.uk/efo/EFO_0000546',
                        'http://www.ebi.ac.uk/efo/EFO_0003935' ]:
        obj.load_ontology_classes(base_class=base_class)
        obj.get_top_levels(base_class=base_class)
    obj.get_deprecated_classes()

    obj.rdf_graph = None
    return obj


def load_open_targets_disease_ontology(ocr, efo_uri):
    """Loads the EFO graph and extracts the current and obsolete classes.
        Generates the therapeutic areas
        Creates the other disease class
        Move injury under other disease
        Status: production
    """
    logger.debug("load_open_targets_disease_ontology...")
    ocr.load_ontology_graph(efo_uri)

    ocr.get_deprecated_classes(obsoleted_in_version=True)

    '''
    get the original top_levels from EFO
    '''
    ocr.get_top_levels(base_class='http://www.ebi.ac.uk/efo/EFO_0000408')

    '''
    Detach the TAs from the disease node
    and load all the classes
    '''
    disease_uri = rdflib.URIRef('http://www.ebi.ac.uk/efo/EFO_0000408')
    for base_class in EFO_TAS:
        uri = rdflib.URIRef(base_class)
        ocr.rdf_graph.remove((uri, None, disease_uri))
        ocr.load_ontology_classes(base_class=base_class)
        ocr.get_classes_paths(root_uri=base_class, level=0)

    '''
    Create an other disease node
    '''
    cttv = rdflib.Namespace(str("http://www.targetvalidation.org/disease"))

    # namespace_manager = NamespaceManager(self.rdf_graph)
    ocr.rdf_graph.namespace_manager.bind('cttv', cttv)

    '''
    Some diseases have no categories, let's create a category for them
    '''
    other_disease_uri = rdflib.URIRef('http://www.targetvalidation.org/disease/other')
    ocr.rdf_graph.add((other_disease_uri, rdflib.RDF.type, rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#Class')))
    ocr.rdf_graph.add([other_disease_uri, rdflib.RDFS.label, rdflib.Literal('other disease')])

    '''
    Get all children of 'disease' and assign them to 'other disease'
    '''
    for c in ocr.rdf_graph.subjects(predicate=rdflib.RDFS.subClassOf, object=disease_uri):
        ocr.rdf_graph.add([c, rdflib.RDFS.subClassOf, other_disease_uri])

    '''
    Move 'injury' under 'other disease'
    injuries are treated with medication recorded in ChEMBL
    Move 'mental health' under 'other disease'
    '''
    ocr.rdf_graph.add([rdflib.URIRef('http://www.ebi.ac.uk/efo/EFO_0000546'), rdflib.RDFS.subClassOf, other_disease_uri])
    ocr.rdf_graph.add([rdflib.URIRef('http://www.ebi.ac.uk/efo/EFO_0003935'), rdflib.RDFS.subClassOf, other_disease_uri])


    # other disease, phenotype, measurement, biological process, function
    for base_class in [ 'http://www.targetvalidation.org/disease/other',
                        'http://www.ebi.ac.uk/efo/EFO_0000651',
                        'http://www.ebi.ac.uk/efo/EFO_0001444',
                        'http://purl.obolibrary.org/obo/GO_0008150',
                        'http://www.ifomis.org/bfo/1.1/snap#Function']:

        ocr.load_ontology_classes(base_class=base_class)
        ocr.get_classes_paths(root_uri=base_class, level=0)
