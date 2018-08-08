
import sys
import requests
import urllib
import ontologyutils.efo as efo
import ontologyutils.ols as ols
import logging
import json
from pprint import pprint

__author__ = 'gautierk'

BASE_URL = 'https://www.ebi.ac.uk/spot/zooma/v2/api/services'
#https://www.ebi.ac.uk/spot/zooma/v2/api/services/annotate?propertyValue=mus+musculus&propertyType=organism&filter=required:[none],ontologies:[efo,mirnao]

class Zooma():

    def __init__(self):
        self.ols_mapper = ols.OLS()
        pass

    def queryByLabelOrSynonym(self, label, ontology_name):

        url = BASE_URL + '/annotate'
        params = dict(propertyValue=label, propertyType='disease', filter='required:[cttv]', ontologies='[%s]'%ontology_name)
        r = requests.get(url, params=params, timeout=30)
        print(r.url)
        if r.status_code == 404:
            return None
        rsp = r.json()
        if 'error' in rsp:
            pprint(rsp)
            return None

        #pprint(rsp)
        return rsp

    def getHighMediumConfidenceMapping(self, label, ontology_name, confidence_levels=["HIGH"]):

        data = []
        rsp = self.queryByLabelOrSynonym(label, ontology_name)
        for map in rsp:
            if map['confidence'] in confidence_levels:
                for semanticTag in map['semanticTags']:
                    print(semanticTag)
                    # query OLS to retrieve the original name
                    return self.ols_mapper.queryByIRI(id_uri=semanticTag, ontology_name=ontology_name)
        return data