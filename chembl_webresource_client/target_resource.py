__author__ = 'mnowotka'

#-----------------------------------------------------------------------------------------------------------------------

import requests
import requests_cache
try:
    import grequests
except:
    grequests = None
from chembl_webresource_client.web_resource import WebResource
from chembl_webresource_client.settings import Settings

#-----------------------------------------------------------------------------------------------------------------------


class TargetResource(WebResource):
    name = 'targets'

#-----------------------------------------------------------------------------------------------------------------------

    def get_all(self, frmt='json'):
        url = '{0}/{1}.{2}'.format(Settings.Instance().webservice_root_url, self.name, frmt)
        with self._get_session() as session:
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
        asyn = kwargs.get('asyn', False)
        prop = kwargs.get('prop', None)
        if chembl_id:
            return super(TargetResource, self).get_one(chembl_id=chembl_id, frmt=frmt, asyn=asyn, prop=prop)
        if not 'uniprot' in kwargs:
            self.logger.warning('No identifier given')
            return None
        key = 'uniprot'
        url = '{0}/{1}/{2}/{3}.{4}'.format(Settings.Instance().webservice_root_url, self.name, key, kwargs[key], frmt)
        return self._get_one(url, asyn, frmt)

#-----------------------------------------------------------------------------------------------------------------------
