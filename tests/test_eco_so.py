
import opentargets_ontologyutils.eco_so
import opentargets_ontologyutils.rdf_utils


def test_eco_so():
    ocr = opentargets_ontologyutils.rdf_utils.OntologyClassReader()
    uri_so = "https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/v3.1/releases/so-xp.owl/so-xp.owl"
    uri_eco = "https://raw.githubusercontent.com/evidenceontology/evidenceontology/v2018-11-10/eco.owl"
    #actually load it
    opentargets_ontologyutils.eco_so.load_evidence_classes(ocr, uri_so, uri_eco)


    assert len(ocr.current_classes) > 0
    assert len(ocr.classes_paths) > 0
    assert len(ocr.children) > 0