__author__ = 'mnowotka'

#-----------------------------------------------------------------------------------------------------------------------

import requests
import requests_cache
import grequests
from chembl_webresource_client.web_resource import WebResource
from chembl_webresource_client.settings import Settings

#-----------------------------------------------------------------------------------------------------------------------

class TargetResource(WebResource):
    name = 'targets'

#-----------------------------------------------------------------------------------------------------------------------

    def get_all(self, format='json'):
        session = self._get_session()
        url = '%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name, format)
        return self._process_request(url, session, format, timeout=Settings.Instance().TIMEOUT)

#-----------------------------------------------------------------------------------------------------------------------

    def get(self, chembl_id=None, **kwargs):
        format = kwargs.get('format', 'json')
        if chembl_id:
            return super(TargetResource, self).get(chembl_id, format=format)
        if not 'uniprot' in kwargs:
            return None
        kname = 'uniprot'
        return self._get(kname, kwargs[kname], format)

#-----------------------------------------------------------------------------------------------------------------------

    def approved_drugs(self, chembl_id=None, format='json'):
        return super(TargetResource, self).get(chembl_id, format=format, property='approvedDrug')

#-----------------------------------------------------------------------------------------------------------------------

    def get_one(self, chembl_id=None, **kwargs):
        format = kwargs.get('format', 'json')
        async = kwargs.get('acync', False)
        property = kwargs.get('property', None)
        if chembl_id:
            return super(TargetResource, self).get_one(chembl_id=chembl_id, format=format, async=async, property=property)
        if not 'uniprot' in kwargs:
            return None
        key = 'uniprot'
        url = '%s/%s/%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name, key, kwargs[key],format)
        return self._get_one(url, async, format)

#-----------------------------------------------------------------------------------------------------------------------
