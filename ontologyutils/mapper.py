import ontologyutils.ols as ols
import ontologyutils.zooma as zooma
import ontologyutils.oxo as oxo
import logging

__author__ = 'gautierk'

class OntologyMapper():

    def __init__(self):
        self.ols_mapper = ols.OLS()
        self.zooma_mapper = zooma.Zooma()
        self.oxo_mapper = oxo.OXO()
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
                                    source=ontology_name,
                                    id=result['id'],
                                    label=result['label'],
                                    tool='OLS'))
                break
            else:
                result = self.zooma_mapper.getHighMediumConfidenceMapping(label=label, ontology_name=ontology_name)
                if result:
                    results.append(dict(scope='EXACT',
                                        source=ontology_name,
                                        id=result['obo_id'],
                                        label=result['label'],
                                        tool='ZOOMA'))
                    break
        return results

    def get_full_ontology_mappings(self, source, source_id, stop_dests=[oxo.SOURCES['efo']]):

        final_mappings = dict()
        final_ontology_prefix = set()
        for stop_dest in stop_dests:
            final_ontology_prefix |= set(self.oxo_mapped_ontology_prefix(stop_dest))

        self.oxo_mapper = oxo.OXO()
        
        curie = source + ':' + source_id
        '''
        This step essentially computes a graph of all relationships between the source uri and the destination uri
        and iterate until there is a stop dest
        '''
        self.oxo_mapper.oxo_scan(curies=[curie], stop_dests=stop_dests)
        '''
        once this is done, this algorithm starts from the source ontology and create all the paths to the destination 
        ontologies
        '''
        if source in self.oxo_mapper.oxo_source_to_dest:
            paths = self.oxo_mapper.oxo_paths(source=source, stop_dests=stop_dests, curie=curie)
            # create a list of all the end nodes
            for path in paths:
                result_paths = map(lambda x: "%s (%s)" % (x, self.oxo_mapper.oxo_labels[x]), path)
                print(" -> ".join(result_paths))
                '''
                this part should be improved with a lambda expression but also stop at the stop_dests which is not in the path
                '''
                if any(path[-1].startswith(prefix) for prefix in final_ontology_prefix)
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
        