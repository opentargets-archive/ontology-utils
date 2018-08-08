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

    def getOboIdMappings(self, obo_id, targets=[oxo.SOURCES['efo']]):
        return self.oxo_mapper.queryByOboId(obo_id=obo_id, targets=targets)

    def getLabelMappings(self, label, targets=[ols.SOURCES['efo']]):
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
