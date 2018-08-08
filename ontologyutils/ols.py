import sys
import requests
import urllib
import ontologyutils.efo as efo
import logging
import json
from pprint import pprint

SOURCES = dict(
    efo = 'efo',
    umls = 'umls',
    hp = 'hp',
    mondo = 'mondo',
    doid = 'doid',
    bao = 'bao',
    orphanet = 'orphanet'
)

__author__ = 'gautierk'

BASE_URL = 'https://www.ebi.ac.uk/ols/api'

class OLS():

    def __init__(self):
        pass

    def queryByIRI(self, id_uri, ontology_name):

        url = BASE_URL + '/ontologies/' + ontology_name + '/terms/' + urllib.parse.quote_plus(id_uri).replace('%2F', '%252F')
        r = requests.get(url, timeout=30)
        print(r.url)
        if r.status_code == 404:
            return None
        rsp = r.json()
        if 'error' in rsp:
            pprint(rsp)
            return None
        return rsp

    def queryByOboId(self, obo_id, ontology_name):

        id_uri = None
        if ontology_name == 'efo':
            id_uri = efo.EFOUtils.get_url_from_ontology_id(obo_id)
        else:
            # should raise an exception!
            print("No support yet for other ontologies")
            sys.exit(1)

        return self.queryByIRI(id_uri, ontology_name)

    def queryByLabelOrSynonym(self, label, ontology_name):

        # https://www.ebi.ac.uk/ols/api/search/?q=neoplasm&ontology=efo&queryFields=label,synonym&exact=true
        url = BASE_URL + '/search/'
        params = dict(q=label, ontology=ontology_name, queryFields="label,synonym", exact='true')
        r = requests.get(url, params=params, timeout=30)
        rsp = r.json()
        print(r.url)
        # count number of results
        if rsp['response']['numFound'] > 0:
            for doc in rsp['response']['docs']:
                return doc
        return None