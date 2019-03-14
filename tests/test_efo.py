import logging
import os
import opentargets_ontologyutils.efo as efo
import opentargets_ontologyutils.rdf_utils as rdf_utils

# Change logging level here.
logging.basicConfig(level=os.environ.get('LOG_LEVEL', logging.DEBUG))

def test_efo():
    ocr = rdf_utils.OntologyClassReader()
    efo.load_open_targets_disease_ontology(ocr, "https://github.com/EBISPOT/efo/releases/download/v3.3.1/efo.owl")
    #efo.load_open_targets_disease_ontology(ocr, "https://storage.googleapis.com/open-targets-efo-3/efo.owl")
    #efo.load_open_targets_disease_ontology(ocr, "file:///home/faulcon/Desktop/efo_3.3.1.owl")

    assert len(ocr.current_classes.keys()) > 10
    assert "http://www.ebi.ac.uk/efo/EFO_0000408" in ocr.current_classes
    assert ocr.current_classes["http://www.ebi.ac.uk/efo/EFO_0000408"] == "disease", ocr.current_classes["http://www.ebi.ac.uk/efo/EFO_0000408"]

    assert len(ocr.therapeutic_labels) > 0
    assert "http://www.ebi.ac.uk/efo/EFO_0000408" in ocr.therapeutic_labels

    assert "http://www.ebi.ac.uk/efo/EFO_0000319" in ocr.therapeutic_labels #heart disease
    assert len(ocr.therapeutic_labels["http://www.ebi.ac.uk/efo/EFO_0000319"]) == 2
    assert len(ocr.therapeutic_uris["http://www.ebi.ac.uk/efo/EFO_0000319"]) == 2
    heart_disease_labels = set(ocr.therapeutic_labels["http://www.ebi.ac.uk/efo/EFO_0000319"])
    assert heart_disease_labels == set(("disease", "cardiovascular disease")), heart_disease_labels
    heart_disease_uris = set(ocr.therapeutic_uris["http://www.ebi.ac.uk/efo/EFO_0000319"])
    assert heart_disease_uris == set(("http://www.ebi.ac.uk/efo/EFO_0000408","http://www.ebi.ac.uk/efo/EFO_0000319")), heart_disease_labels
    pericardium_disease_labels = set(ocr.therapeutic_labels["http://purl.obolibrary.org/obo/MONDO_0000474"])
    assert pericardium_disease_labels == set(("disease", "cardiovascular disease")), pericardium_disease_labels
    

    assert len(ocr.classes_paths) > 0
    assert "http://www.ebi.ac.uk/efo/EFO_0000408" in ocr.classes_paths
    assert ocr.classes_paths['http://www.ebi.ac.uk/efo/EFO_0000319']['ids'][0][-1] == 'EFO_0000319',ocr.classes_paths['http://www.ebi.ac.uk/efo/EFO_0000319']['ids'][0][-1]


if __name__ == "__main__":
    test_efo()