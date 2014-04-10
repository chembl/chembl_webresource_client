__author__ = 'mnowotka'

#-----------------------------------------------------------------------------------------------------------------------

import requests
import requests_cache
import grequests
import sys
import time
from chembl_webresource_client.settings import Settings
from chembl_webresource_client import __version__ as version

#-----------------------------------------------------------------------------------------------------------------------

class WebResource(object):

#-----------------------------------------------------------------------------------------------------------------------

    def _get_session(self):
        s = Settings.Instance()
        if s.CACHING:
            return requests_cache.CachedSession(s.CACHE_NAME, backend='sqlite', fast_save=s.FAST_SAVE)
        return requests.Session()

#-----------------------------------------------------------------------------------------------------------------------

    def get_service(self):
        try:
            res = requests.get('%s/status/' % Settings.Instance().webservice_root_url,
                                                                                timeout=Settings.Instance().TIMEOUT)
            if not res.ok:
                return None
            js = res.json()
            if not 'service' in js:
                return False
            return js['service']
        except Exception:
            return None

#-----------------------------------------------------------------------------------------------------------------------

    def server_version(self):
        service = self.get_service()
        if not 'version' in service:
            return None
        return service['version']

#-----------------------------------------------------------------------------------------------------------------------

    def client_version(self):
        return version

#-----------------------------------------------------------------------------------------------------------------------

    def status(self):
        service = self.get_service()
        if not 'status' in service:
            return False
        return service['status'] == 'UP'

#-----------------------------------------------------------------------------------------------------------------------

    def _process_request(self, url, session, format, **kwargs):
        try:
            res = session.get(url, **kwargs)
            if not res.ok:
                return res.status_code
            return res.json().values()[0] if format == 'json' else res.content
        except Exception:
            return None


#-----------------------------------------------------------------------------------------------------------------------

    def bioactivities(self, chembl_id, format='json'):
        session = self._get_session()
        url = '%s/%s/%s/bioactivities.%s' % (Settings.Instance().webservice_root_url, self.name, chembl_id, format)
        return self._process_request(url, session, format, timeout=Settings.Instance().TIMEOUT)

#-----------------------------------------------------------------------------------------------------------------------

    def get_val(self,x,format):
        if format == 'json':
            return x.json().values()[0] if (x and x.ok) else (x.status_code if x else None)
        else:
            return x.content if (x and x.ok) else (x.status_code if x else None)

#-----------------------------------------------------------------------------------------------------------------------

    def _apply(self, iterable, fn, *args, **kwargs):
        return [fn(x, *args, **kwargs) for x in iterable if x ]

#-----------------------------------------------------------------------------------------------------------------------

    def _get(self, kname, keys, format='json', property=None):
        if isinstance(keys, list):
            if len(keys) > 10:
                try:
                    rs = (self.get_one(**{'format':format, kname:key, 'async':True, 'property': property}) for key in keys)
                    ret = grequests.map(rs)
                    return self._apply(ret, self.get_val, format)
                except Exception:
                    return None
            else:
                ret = []
                for key in keys:
                    ret.append(self.get_one(**{'format':format, kname:key, 'property': property}))
                return ret
        return self.get_one(**{'format':format, kname:keys, 'property': property})

#-----------------------------------------------------------------------------------------------------------------------

    def get(self, chembl_id, format='json', property=None):
        if chembl_id:
            return self._get('chembl_id', chembl_id, format, property)
        return None

#-----------------------------------------------------------------------------------------------------------------------

    def _get_one(self, url, async, format):
        session = self._get_session()
        if async:
            return grequests.get(url, session=session)
        return self._process_request(url, session, format, timeout=Settings.Instance().TIMEOUT)

#-----------------------------------------------------------------------------------------------------------------------

    def get_one(self, chembl_id, format='json', async=False, property=None):
        if chembl_id:
            if not property:
                url = '%s/%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name, chembl_id, format)
            else:
                url = '%s/%s/%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name, chembl_id, property, format)
            return self._get_one(url, async, format)

#-----------------------------------------------------------------------------------------------------------------------

