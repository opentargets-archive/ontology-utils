from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import object
import sys
import requests
import urllib.request, urllib.parse, urllib.error
import opentargets_ontologyutils.efo as efo
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

class OLS(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def queryByIRI(self, id_uri, ontology_name):

        url = BASE_URL + '/ontologies/' + ontology_name + '/terms/' + urllib.parse.quote_plus(id_uri).replace('%2F', '%252F')
        r = requests.get(url, timeout=30)
        self.logger.debug(r.url)
        if r.status_code == 404:
            return None
        rsp = r.json()
        if 'error' in rsp:
            self.logger.debug(json.dumps(rsp, indent=2))
            return None
        return rsp

    def queryByOboId(self, obo_id, ontology_name):

        id_uri = None
        if ontology_name == 'efo':
            id_uri = efo.EFOUtils.get_url_from_ontology_id(obo_id)
        else:
            # should raise an exception!
            self.logger.debug("No support yet for other ontologies")
            sys.exit(1)

        return self.queryByIRI(id_uri, ontology_name)

    def queryByLabelOrSynonym(self, label, ontology_name):

        # https://www.ebi.ac.uk/ols/api/search/?q=neoplasm&ontology=efo&queryFields=label,synonym&exact=true
        url = BASE_URL + '/search/'
        params = dict(q=label, ontology=ontology_name, queryFields="label,synonym", exact='true')
        r = requests.get(url, params=params, timeout=30)
        rsp = r.json()
        self.logger.debug(r.url)
        # count number of results
        if rsp['response']['numFound'] > 0:
            for doc in rsp['response']['docs']:
                return doc
        return None