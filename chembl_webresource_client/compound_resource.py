__author__ = 'mnowotka'

#-----------------------------------------------------------------------------------------------------------------------

import requests
import requests_cache
import grequests
from chembl_webresource_client.web_resource import WebResource
from chembl_webresource_client.settings import Settings

#-----------------------------------------------------------------------------------------------------------------------

class CompoundResource(WebResource):
    name = 'compounds'

#-----------------------------------------------------------------------------------------------------------------------

    def get(self, chembl_id=None, **kwargs):
        format = kwargs.get('format', 'json')
        if chembl_id:
            return super(CompoundResource, self).get(chembl_id, format=format)
        if 'stdinchikey' in kwargs:
            kname = 'stdinchikey'
        elif 'smiles' in kwargs:
            kname = 'smiles'
        else:
            return None
        return self._get(kname, kwargs[kname], format)

#-----------------------------------------------------------------------------------------------------------------------

    def get_one(self, chembl_id=None, **kwargs):
        format = kwargs.get('format', 'json')
        async = kwargs.get('async', False)
        property = kwargs.get('property', None)
        if chembl_id:
            return super(CompoundResource, self).get_one(chembl_id=chembl_id, format=format, async=async, property=property)
        if 'stdinchikey' in kwargs:
            key = 'stdinchikey'
        elif 'smiles' in kwargs:
            key = 'smiles'
        else:
            return None
        url = '%s/%s/%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name, key, kwargs[key], format)
        return self._get_one(url, async, format)

#-----------------------------------------------------------------------------------------------------------------------

    def forms(self, chembl_id, format='json'):
        return super(CompoundResource, self).get(chembl_id, format=format, property='form')

#-----------------------------------------------------------------------------------------------------------------------

    def drug_mechnisms(self, chembl_id, format='json'):
        return super(CompoundResource, self).get(chembl_id, format=format, property='drugMechanism')

#-----------------------------------------------------------------------------------------------------------------------

    def _get_method(self, struct, **kwargs):
        format = kwargs.get('format', 'json')
        session = self._get_session()
        if 'simscore' in kwargs:
            simscore = kwargs['simscore']
            url = '%s/%s/similarity/%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name, struct,
                                                                                                simscore, format)
        else:
            url = '%s/%s/substructure/%s.%s' % (Settings.Instance().webservice_root_url, self.name, struct, format)
        return self._process_request(url, session, format, timeout=Settings.Instance().TIMEOUT)

#-----------------------------------------------------------------------------------------------------------------------

    def substructure(self, struct, format='json'):
        return self._get_method(struct, format=format)

#-----------------------------------------------------------------------------------------------------------------------

    def similar_to(self, struct, simscore, format='json'):
        return self._get_method(struct, simscore=simscore, format=format)

#-----------------------------------------------------------------------------------------------------------------------

    def image(self, chembl_id=None, **kwargs):
        if chembl_id:
            ids = chembl_id
            if isinstance(ids, list):
                if len(ids) > 10:
                    rs = (self.get_single_image(id, True, **kwargs) for id in ids)
                    ret = grequests.map(rs)
                    return self._apply(ret, self.get_val, format)
                ret = []
                for id in ids:
                    ret.append(self.get_single_image(id, False, **kwargs))
                return ret
            return self.get_single_image(ids, False, **kwargs)

#-----------------------------------------------------------------------------------------------------------------------

    def get_single_image(self, chembl_id, async, **kwargs):
        session = self._get_session()
        try:
            size = kwargs.get('size', 500)
            engine = kwargs.get('engine', 'rdkit')
            ignoreCoords = kwargs.get('ignoreCoords', False)

            query = '?engine=%s&dimensions=%s' % (engine, size)
            if ignoreCoords:
                query += '&ignoreCoords=1'

            if chembl_id:
                url = '%s/%s/%s/image%s' % (Settings.Instance().webservice_root_url, self.name, chembl_id, query)
                if async:
                    return grequests.get(url, session=session)
                res = session.get(url, timeout=Settings.Instance().TIMEOUT)
                if not res.ok:
                    return res.status_code
                return res.content
            return None
        except Exception:
            return None

#-----------------------------------------------------------------------------------------------------------------------