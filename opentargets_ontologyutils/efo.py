from __future__ import print_function

import logging
import collections

import rdflib

from opentargets_ontologyutils.rdf_utils import OntologyClassReader,merge_classes_paths

logger = logging.getLogger(__name__)


"""
Loads EFO from the URI provided into the ontology class reader object
returns nothing
"""
def load_open_targets_disease_ontology(ocr, efo_uri):

    logger.debug("load_open_targets_disease_ontology...")
    ocr.load_ontology_graph(efo_uri)

    ocr.get_deprecated_classes(obsoleted_in_version=True)

    # disease, phenotype, measurement, biological process, function
    #these are the parts of EFO that we want to slim to
    for root in [ 'http://www.ebi.ac.uk/efo/EFO_0000408',
            'http://www.ebi.ac.uk/efo/EFO_0000651',
            'http://www.ebi.ac.uk/efo/EFO_0001444',
            'http://purl.obolibrary.org/obo/GO_0008150',
            'http://www.ifomis.org/bfo/1.1/snap#Function']:

        ocr.load_ontology_classes(base_class=root)
    logger.debug("Found %d classes", len(ocr.current_classes.keys()))


    therapeutic_areas = tuple(find_therapeutic_areas(ocr.rdf_graph))
    logger.debug("Found %d therapeutic areas", len(therapeutic_areas))

    #for each therapeutic area, calculate the paths and parents
    ocr.classes_paths_bases = {}
    for therapeutic_area in therapeutic_areas:
        ocr.classes_paths_bases[therapeutic_area] = ocr.get_classes_paths(root_uri=therapeutic_area, level=0)

    #combine each therapeutic area in a combined collection
    ocr.classes_paths = {}
    for therapeutic_area in ocr.classes_paths_bases:
        ocr.classes_paths = merge_classes_paths(ocr.classes_paths, 
            ocr.classes_paths_bases[therapeutic_area])

    #combine a dictionary of which therapeutic areas each term is in
    ocr.therapeutic_labels = collections.defaultdict(list)
    for therapeutic_area in ocr.classes_paths_bases:
        label = ocr.classes_paths_bases[therapeutic_area][therapeutic_area]['labels'][-1]
        for uri in ocr.classes_paths_bases[therapeutic_area]:
            ocr.therapeutic_labels[uri].append(label)




"""
Generator of the therapeutic areas labelled in the rdf graph of efo
"""
def find_therapeutic_areas(rdf_graph):
    in_subset = rdflib.term.URIRef('http://www.geneontology.org/formats/oboInOwl#inSubset')
    therapeutic_area_label = rdflib.term.Literal('therapeutic_area')
    for s in rdf_graph.subjects(in_subset,therapeutic_area_label):
        therapeutic_area = str(s)
        logger.debug("found therapeutic area: %s", therapeutic_area)
        yield therapeutic_area
