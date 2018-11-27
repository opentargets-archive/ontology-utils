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
import opentargets_ontologyutils.ols as ols
import opentargets_ontologyutils.zooma as zooma
import opentargets_ontologyutils.oxo as oxo
import logging

__author__ = 'gautierk'

class OntologyMapper(object):

    def __init__(self):
        self.ols_mapper = ols.OLS()
        self.zooma_mapper = zooma.Zooma()
        self.oxo_mapper = oxo.OXO()
        self.logger = logging.getLogger(__name__)
        self.dead_ends = dict()
        self.dead_ends[oxo.SOURCES['efo']] = [oxo.SOURCES['omim'], oxo.SOURCES['orphanet']]
        self.dead_ends[oxo.SOURCES['mondo']] = [oxo.SOURCES['omim'], oxo.SOURCES['orphanet']]
        self.oxo_mapped_ontology_prefix = dict()
        self.oxo_mapped_ontology_prefix[oxo.SOURCES['efo']] = [oxo.SOURCES['efo'], oxo.SOURCES['hp'], oxo.SOURCES['mp'], oxo.SOURCES['go']]
        self.oxo_mapped_ontology_prefix[oxo.SOURCES['mondo']] = [oxo.SOURCES['mondo']]



    def get_obo_id_mappings(self, obo_id, targets=[oxo.SOURCES['efo']]):
        return self.oxo_mapper.query_by_obo_id(obo_id=obo_id, stop_dests=targets)

    def get_label_mappings(self, label, targets=[ols.SOURCES['efo']]):
        results = []
        for ontology_name in targets:
            result = self.ols_mapper.queryByLabelOrSynonym(label=label, ontology_name=ontology_name)
            if result:
                results.append(dict(scope='EXACT',
                                    source=ontology_name.upper(),
                                    id=result['obo_id'],
                                    label=result['label'],
                                    tool='OLS'))
                break
            else:
                result = self.zooma_mapper.getHighMediumConfidenceMapping(label=label, ontology_name=ontology_name)
                if result:
                    results.append(dict(scope='EXACT',
                                        source=ontology_name.upper(),
                                        id=result['obo_id'],
                                        label=result['label'],
                                        tool='ZOOMA'))
                    break
        return results

    def get_full_ontology_mappings(self, source, source_id, stop_dests=[oxo.SOURCES['efo']], dead_ends=[]):

        final_mappings = dict()
        final_ontology_prefix = set()
        for stop_dest in stop_dests:
            final_ontology_prefix |= set(self.oxo_mapped_ontology_prefix[stop_dest])

        self.oxo_mapper = oxo.OXO()
        
        curie = source + ':' + source_id
        '''
        This step essentially computes a graph of all relationships between the source uri and the destination uri
        and iterate until there is a stop dest
        '''
        self.oxo_mapper.oxo_scan(curies=[curie], stop_dests=stop_dests, dead_ends=dead_ends)
        '''
        once this is done, this algorithm starts from the source ontology and create all the paths to the destination 
        ontologies
        '''
        if source in self.oxo_mapper.oxo_source_to_dest:
            paths = self.oxo_mapper.oxo_paths(source=source, stop_dests=stop_dests, curie=curie)
            # create a list of all the end nodes
            for path in paths:
                result_paths = ["%s (%s)" % (x, self.oxo_mapper.oxo_labels[x]) for x in path]
                self.logger.debug(" -> ".join(result_paths))
                '''
                this part should be improved with a lambda expression but also stop at the stop_dests which is not in the path
                '''
                if any(path[-1].startswith(prefix) for prefix in final_ontology_prefix):
                        #path[-1].startswith(oxo.SOURCES['efo']) or path[-1].startswith(oxo.SOURCES['hp']) or path[-1].startswith(oxo.SOURCES['mp']):
                    (source, raw) = path[-1].split(":")
                    id = path[-1]
                    final_mappings[id] = dict(
                        id=id,
                        label=self.oxo_mapper.oxo_labels[id],
                        source=" -> ".join(result_paths),
                        process='oXo shortest path'
                    )

        else:
            final_mappings[source_id] = dict(
                id=source_id,
                label='N/A',
                source=source,
                process="Curation Required"
            )
        return final_mappings
        