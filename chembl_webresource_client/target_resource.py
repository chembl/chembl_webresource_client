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

    def get_all(self, frmt='json'):
        session = self._get_session()
        url = '%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name, frmt)
        return self._process_request(url, session, frmt, timeout=Settings.Instance().TIMEOUT)

#-----------------------------------------------------------------------------------------------------------------------

    def get(self, chembl_id=None, **kwargs):
        frmt = kwargs.get('frmt', 'json')
        if chembl_id:
            return super(TargetResource, self).get(chembl_id, frmt=frmt)
        if not 'uniprot' in kwargs:
            self.logger.warning('No identifier given')
            return None
        kname = 'uniprot'
        return self._get(kname, kwargs[kname], frmt)

#-----------------------------------------------------------------------------------------------------------------------

    def approved_drugs(self, chembl_id=None, frmt='json'):
        return super(TargetResource, self).get(chembl_id, frmt=frmt, prop='approvedDrug')

#-----------------------------------------------------------------------------------------------------------------------

    def get_one(self, chembl_id=None, **kwargs):
        frmt = kwargs.get('frmt', 'json')
        async = kwargs.get('async', False)
        prop = kwargs.get('prop', None)
        if chembl_id:
            return super(TargetResource, self).get_one(chembl_id=chembl_id, frmt=frmt, async=async, prop=prop)
        if not 'uniprot' in kwargs:
            self.logger.warning('No identifier given')
            return None
        key = 'uniprot'
        url = '%s/%s/%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name, key, kwargs[key], frmt)
        return self._get_one(url, async, frmt)

#-----------------------------------------------------------------------------------------------------------------------
