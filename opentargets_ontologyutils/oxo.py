'''
Copyright 2014-2018 Biogen, Celgene Corporation, EMBL - European Bioinformatics Institute, GlaxoSmithKline, Takeda Pharmaceutical Company and Wellcome Sanger Institute

This software was developed as part of the Open Targets project. For more information please see: http://www.opentargets.org

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from __future__ import print_function
from builtins import object
import requests
import re
import copy
import logging
from pprint import pprint

SOURCES = dict(
    efo='EFO',
    go='GO',
    umls='UMLS',
    mp='MP',
    hp='HP',
    mondo='MONDO',
    doid='DOID',
    bao='BAO',
    orphanet='Orphanet',
    omim='OMIM',
    icd10='ICD10CM',
    mesh='MeSH'
)

STREAM_THRESHOLD = 20

__author__ = 'gautierk'

BASE_URL = 'https://www.ebi.ac.uk/spot/oxo/api'


class OXO(object):

    def __init__(self):
        self.oxo_source_to_dest = dict()
        self.oxo_nodes = set()
        self.oxo_labels = dict()
        self.oxo_sources = set()
        self.oxo_stop_node = None
        # for shortest paths
        self.path_nodes = set()
        self.path_sources = set()
        self.logger = logging.getLogger(__name__)

    def get_self_oxo_term(self, obo_id):

        url = BASE_URL + '/terms/' + obo_id
        r = requests.get(url, timeout=30)
        self.logger.debug(r.url)
        if r.status_code == 404:
            return None
        rsp = r.json()
        if 'error' in rsp:
            return None
        return rsp

    def query_by_obo_id(self, obo_id, stop_dests=[SOURCES['efo']]):

        results = []
        url = BASE_URL + '/mappings'
        nbPages = 0

        params = dict(fromId=obo_id, size=20)
        r = requests.get(url, params=params, timeout=30)
        self.logger.debug(r.url)
        if r.status_code == 404:
            return None
        rsp = r.json()
        if 'error' in rsp:
            return None

        # totalElements will give the number of elements per page
        if rsp['page']['totalElements'] == 0:
            return results

        if nbPages == 0:
            nbPages = rsp['page']['totalPages']

        for mapping in rsp['_embedded']['mappings']:
            self.logger.debug(mapping['sourcePrefix'])
            if mapping['datasource']['prefix'] in stop_dests:
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

    def oxo_mapping_from(self, curie, stop_dests=None, dead_ends=None):
        # https://www.ebi.ac.uk/spot/oxo/api/mappings?fromId=UMLS:C0002191
        # https://www.ebi.ac.uk/spot/oxo/api/mappings?fromId=ICD9CM:519.1
        #
        endpoints = set()
        i = 0
        nb_results = 0
        while True:

            url = BASE_URL + '/mappings'
            nbPages = 0

            params = dict(fromId=curie, page=i)
            r = requests.get(url, params=params, timeout=30)
            self.logger.debug(r.url)
            results = r.json()
            i += 1

            if results["page"]["totalElements"] > 0:
                # self.logger.debug(json.dumps(results, indent=2))
                for mapping in results["_embedded"]["mappings"]:
                    # "DATABASE"
                    source_type = mapping['sourceType']
                    # "sourcePrefix" "UMLS"

                    # fromTerm
                    source_curie = mapping["fromTerm"]["curie"]
                    source_label = mapping["fromTerm"]["label"]
                    self.oxo_labels[source_curie] = source_label
                    source_prefix = mapping["sourcePrefix"]
                    self.oxo_sources.add(source_prefix)

                    # toTerm
                    end_curie = mapping["toTerm"]["curie"]
                    end_label = mapping["fromTerm"]["label"]
                    self.oxo_labels[end_curie] = end_label
                    ecm = re.match("^([^:]+):.*", end_curie)
                    end_prefix = ecm.groups()[0]
                    self.oxo_sources.add(end_prefix)

                    # end_prefix = mapping["toTerm"]["datasource"]["prefix"]
                    #

                    # if we have never seen this end prefix before
                    if end_prefix not in self.oxo_source_to_dest:
                        self.oxo_source_to_dest[end_prefix] = dict()
                    if source_prefix not in self.oxo_source_to_dest[end_prefix]:
                        self.oxo_source_to_dest[end_prefix][source_prefix] = dict()

                    # and conversely
                    if source_prefix not in self.oxo_source_to_dest:
                        self.oxo_source_to_dest[source_prefix] = dict()
                    if end_prefix not in self.oxo_source_to_dest[source_prefix]:
                        self.oxo_source_to_dest[source_prefix][end_prefix] = dict()

                    # add the source node
                    if source_curie not in self.oxo_source_to_dest[source_prefix][end_prefix]:
                        self.oxo_source_to_dest[source_prefix][end_prefix][source_curie] = set()

                    # add the end node
                    if end_curie not in self.oxo_source_to_dest[end_prefix][source_prefix]:
                        self.oxo_source_to_dest[end_prefix][source_prefix][end_curie] = set()

                    # debug
                    # if end_curie not in self.oxo_source_to_dest[source_prefix][end_prefix][source_curie] or source_curie not in self.oxo_source_to_dest[end_prefix][source_prefix][end_curie]:
                    #    print ("from %s '%s' (%s) to %s '%s' (%s)" % (source_curie, source_label, source_prefix, end_curie, end_label, end_prefix))

                    #  add the edge between source and end nodes
                    if end_curie not in self.oxo_source_to_dest[source_prefix][end_prefix][source_curie]:
                        self.oxo_source_to_dest[source_prefix][end_prefix][source_curie].add(end_curie)

                    #  add the edge between end and source nodes
                    if source_curie not in self.oxo_source_to_dest[end_prefix][source_prefix][end_curie]:
                        self.oxo_source_to_dest[end_prefix][source_prefix][end_curie].add(source_curie)

                    # dead_end: we don't want to go further after having added the node in the graph
                    if (source_curie != curie and source_prefix in dead_ends and source_prefix not in stop_dests) or \
                            (end_curie != curie and end_prefix in dead_ends and end_prefix not in stop_dests):
                        continue

                    # however if the node is one of the type we expect
                    if source_curie != curie and source_prefix in stop_dests:
                        self.logger.debug("%s in STOP DEST" % source_curie)
                        self.oxo_stop_node = source_curie
                        return []

                    if end_curie != curie and end_prefix in stop_dests:
                        self.logger.debug("%s in STOP DEST" % end_curie)
                        self.oxo_stop_node = end_curie
                        return []

                    # We cut the graph is there are too many paths
                    if (source_curie != curie and source_curie not in self.oxo_nodes) and (
                            source_prefix not in stop_dests or len(
                            self.oxo_source_to_dest[end_prefix][source_prefix]) < STREAM_THRESHOLD):
                        endpoints.add(source_curie)
                    if end_curie != curie and end_curie not in self.oxo_nodes and (end_prefix not in stop_dests or len(
                            self.oxo_source_to_dest[source_prefix][end_prefix]) < STREAM_THRESHOLD):
                        endpoints.add(end_curie)
                if results["page"]["totalElements"] < 20:
                    # no need to query more
                    break
            else:
                break

        return endpoints

    def oxo_scan(self, curies=["ICD10CM:I11"], stop_dests=[SOURCES['efo'], SOURCES['mp'], SOURCES['hp'], SOURCES['mondo']], dead_ends=[SOURCES['orphanet'], SOURCES['omim']]):

        if self.oxo_stop_node is None:
            for curie in curies:
                # check we have not been there before
                if self.oxo_stop_node is None and curie not in self.oxo_nodes:
                    '''
                    Add the nodes to the graph if not seen before
                    '''
                    self.oxo_nodes.add(curie)
                    '''
                    get all direct neighbours
                    '''
                    new_curies = self.oxo_mapping_from(curie=curie, stop_dests=stop_dests, dead_ends=dead_ends)
                    '''
                    and iterate for the neighbours until you are in a dead end or to the destination
                    '''
                    self.oxo_scan(curies=new_curies, stop_dests=stop_dests, dead_ends=dead_ends)

    def oxo_paths(self, source=None, stop_dests=None, curie=None, paths=[], reset=True, tabs=""):

        '''
        How this works:
            algorithm adds current curie to all the paths
            []
            [[a]]
            [[a,b],[a,c]]
            [[a,b,d],[a,b,e],[a,c,f][a,c,g],[a,c,h]]

        :param source:
        :param stop_dest:
        :param curie:
        :param sources:
        :param nodes:
        :param paths:
        :param tabs:
        :return:
        '''

        if reset == True:
            self.path_nodes = set()
            self.path_sources = set()

        # don't want to loop over the same source again
        self.path_sources.add(source)

        # these are the resulting paths for this call
        inter_paths = []

        # check that we don't get there again, only add nodes that we have not seen before
        if curie not in self.path_nodes:
            self.path_nodes.add(curie)
            # print tabs + curie
            # if there is nothing in the path create a new path
            if len(paths) == 0:
                paths = [[]]
            # and add the current node to all existing paths
            for idx, val in enumerate(paths):
                paths[idx].append(curie)
                # print tabs + "Adding " + " -> ".join(paths[idx])
            # ok, if there is no stop destination or the source is not the stop destination, carry on
            if stop_dests is not None and source in stop_dests:
                # print tabs + "I'm done and I'll return all the paths %i" % len(paths)
                return list(paths)
            elif source in self.oxo_source_to_dest:
                # for every destination possible
                b_new_nodes = 0
                for dest, records in list(self.oxo_source_to_dest[source].items()):

                    # looking from source to dest
                    # any dest for which we have a link to
                    if dest not in self.path_sources and curie in records:
                        b_new_nodes += 1
                        for end_curie in records[curie]:
                            # print tabs + "Found new edge from %s to %s (%s)" % (source, dest, end_curie)
                            # deep copy
                            new_paths = self.oxo_paths(source=dest, stop_dests=stop_dests, curie=end_curie,
                                                       paths=copy.deepcopy(paths), reset=False, tabs=tabs + "\t")
                            # print tabs + "Return %i path(s)" %len(new_paths)
                            if len(new_paths) > 0:
                                for idx, p in enumerate(new_paths):
                                    inter_paths.append(p)
                # if we couldn't find any new nodes scanning all relationships
                # then we return a copy of the current paths
                if b_new_nodes == 0:
                    # print tabs + "Reaching the end %i" % len(paths)
                    return list(paths)

        # finally
        else:
            return paths
        return inter_paths
