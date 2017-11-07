import json
from chembl_webresource_client.query import Query
from chembl_webresource_client.settings import Settings


class ElasticClient(Query):

    def __init__(self):
        super(ElasticClient, self).__init__()

    def _search(self, query, method_name):
        url = '{0}/{1}/_search'.format(Settings.Instance().ELASTIC_URL, method_name)
        res = self.session.post(url, data=
        json.dumps({"size": 0,
             "suggest": {
                 "autocomplete": {
                     "prefix": query,
                     "completion": {
                         "field": "_metadata.es_completion"
                     }
                 }
             }
             }
        ))
        if not res.ok:
            return
        try:
            return [x['_id'] for x in res.json()['suggest']['autocomplete'][0]['options']]
        except:
            pass

    def search_molecule(self, query):
        return self._search(query, 'chembl_molecule')

    def search_target(self, query):
        return self._search(query, 'chembl_target')

    def search_assay(self, query):
        return self._search(query, 'chembl_assay')

    def search_document(self, query):
        return self._search(query, 'chembl_document')

    def search_cell_line(self, query):
        return self._search(query, 'chembl_cell_line')

    def search_tissue(self, query):
        return self._search(query, 'chembl_tissue')

