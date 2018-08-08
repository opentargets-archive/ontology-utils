
# https://www.ebi.ac.uk/spot/oxo/api/terms/CHEBI:16750

import sys
import requests
import urllib
import ontologyutils.efo as efo
import logging
import json
from pprint import pprint

SOURCES = dict(
    efo = 'EFO',
    umls = 'UMLS',
    hp = 'HP',
    mondo = 'MONDO',
    doid = 'DOID',
    bao = 'BAO',
    orphanet = 'Orphanet'
)

__author__ = 'gautierk'

BASE_URL = 'https://www.ebi.ac.uk/spot/oxo/api'

class OXO():

    def __init__(self):
        pass

    def getSelf(self, obo_id):

        url = BASE_URL + '/terms/' + obo_id
        r = requests.get(url, timeout=30)
        print(r.url)
        if r.status_code == 404:
            return None
        rsp = r.json()
        pprint(rsp)
        if 'error' in rsp:
            pprint(rsp)
            return None
        return rsp

    def queryByOboId(self, obo_id, targets=[SOURCES['efo']]):

        results = []
        url = BASE_URL + '/mappings'
        nbPages = 0


        params = dict(fromId=obo_id, size=20)
        r = requests.get(url, params=params, timeout=30)
        print(r.url)
        if r.status_code == 404:
            return None
        rsp = r.json()
        #pprint(rsp)
        if 'error' in rsp:
            pprint(rsp)
            return None

        if nbPages == 0:
            nbPages = rsp['page']['totalPages']

        for mapping in rsp['_embedded']['mappings']:
            print(mapping['sourcePrefix'])
            if mapping['datasource']['prefix'] in targets:
                mapped_id = mapping['fromTerm']['curie']
                mapped_label = mapping['fromTerm']['label']
                if mapping['fromTerm']['curie'] == obo_id:
                    mapped_id = mapping['toTerm']['curie']
                    mapped_label = mapping['toTerm']['label']

                results.append(dict(scope=mapping['scope'],
                                    source=mapping['sourcePrefix'],
                                    id=mapped_id,
                                    label=mapped_label,
                                    tool='OXO'))

        return results
