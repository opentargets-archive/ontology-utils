from __future__ import print_function
import sys
import os
import pytest
#import everything to just give a *very* basic tests
import ontologyutils
import ontologyutils.efo
import ontologyutils.hpo
import ontologyutils.mapper
import ontologyutils.ols
import ontologyutils.ou_settings
import ontologyutils.oxo
import ontologyutils.rdf_utils
import ontologyutils.similarity
import ontologyutils.zooma
import ontologyutils.hpoUtils


def test_hpo():
    #load hpo
    filename = 'tests_resources/hp.obo'
    hpo = ontologyutils.Ontology.fromOBOFile(filename)

    #check if term exists as expected
    # "http://purl.obolibrary.org/obo/HP_0001387"
    # comment;synonym;name;hasDbXref;id;is_a;alt_id;def
    assert "name" in list(hpo.terms['HP:0001387']['tags'].keys())
    assert hpo.terms['HP:0001387']['tags']['name'][0] == "Joint stiffness"
    ancestors = hpo.getAncestors('HP:0001387')
    # HP:0011842,HP:0000001,HP:0000118,HP:0000924,HP:0001367,HP:0001376,HP:0011729,HP:0001387
    assert not ancestors == None
    assert "HP:0011842" in ancestors
    assert "HP:0000001" in ancestors
    
    #check cross references
    for xref in ["SNOMEDCT:299032009", 'MeSH:D014552']:
        terms = hpo.getTermsByDbXref(xref)
        assert not terms == None
        for termId in terms:
            print("{0}: {1}\n".format(xref, ';'.join(hpo.terms[termId]['tags']['name'])))

