from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
from builtins import object
import sys
import requests
import urllib.request, urllib.parse, urllib.error
import opentargets_ontologyutils.efo as efo
import opentargets_ontologyutils.ols as ols
import logging
import json
from pprint import pprint

__author__ = 'gautierk'

BASE_URL = 'https://www.ebi.ac.uk/spot/zooma/v2/api/services'
#https://www.ebi.ac.uk/spot/zooma/v2/api/services/annotate?propertyValue=mus+musculus&propertyType=organism&filter=required:[none],ontologies:[efo,mirnao]

class Zooma(object):

    def __init__(self):
        self.ols_mapper = ols.OLS()
        self.logger = logging.getLogger(__name__)

    def queryByLabelOrSynonym(self, label, ontology_name):

        url = BASE_URL + '/annotate'
        params = dict(propertyValue=label, propertyType='disease', filter='required:[cttv]', ontologies='[%s]'%ontology_name)
        r = requests.get(url, params=params, timeout=30)
        self.logger.debug(r.url)
        if r.status_code == 404:
            return None
        rsp = r.json()
        if 'error' in rsp:
            self.logger.debug(json.dumps(rsp, indent=2))
            return None
        return rsp

    def getHighMediumConfidenceMapping(self, label, ontology_name, confidence_levels=["HIGH"]):

        data = []
        rsp = self.queryByLabelOrSynonym(label, ontology_name)
        for map in rsp:
            if map['confidence'] in confidence_levels:
                for semanticTag in map['semanticTags']:
                    self.logger.debug(semanticTag)
                    # query OLS to retrieve the original name
                    return self.ols_mapper.queryByIRI(id_uri=semanticTag, ontology_name=ontology_name)
        return data