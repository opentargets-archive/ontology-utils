import opentargets_ontologyutils.mp
import opentargets_ontologyutils.rdf_utils

def test_mp():
    ocr = opentargets_ontologyutils.rdf_utils.OntologyClassReader()
    uri_mp = "https://storage.googleapis.com/ot-releases/18.12/annotations/mp_2018-12-06.owl.gz"

    opentargets_ontologyutils.mp.load_mammalian_phenotype_ontology(ocr,uri_mp)

    assert len(ocr.current_classes) > 0
    assert len(ocr.classes_paths) > 0
    assert len(ocr.children) > 0


if __name__ == "__main__":
    test_mp()