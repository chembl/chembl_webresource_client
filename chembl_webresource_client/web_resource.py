__author__ = 'mnowotka'

#-----------------------------------------------------------------------------------------------------------------------

import requests
from requests.models import Response
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

    def _process_request(self, url, session, frmt, **kwargs):
        try:
            res = session.get(url, **kwargs)
            if not res.ok:
                return res.status_code
            return res.json().values()[0] if frmt == 'json' else res.content
        except Exception:
            return None

#-----------------------------------------------------------------------------------------------------------------------

    def bioactivities(self, chembl_id, frmt='json'):
        session = self._get_session()
        url = '%s/%s/%s/bioactivities.%s' % (Settings.Instance().webservice_root_url, self.name, chembl_id, frmt)
        return self._process_request(url, session, frmt, timeout=Settings.Instance().TIMEOUT)

#-----------------------------------------------------------------------------------------------------------------------

    def get_val(self, x, frmt):
        if type(x) is not Response:
            return x
        if frmt == 'json':
            return x.json().values()[0] if x.ok else x.status_code
        else:
            return x.content if x.ok else x.status_code

#-----------------------------------------------------------------------------------------------------------------------

    def _apply(self, iterable, fn, *args, **kwargs):
        return [fn(x, *args, **kwargs) for x in iterable if x is not None]

#-----------------------------------------------------------------------------------------------------------------------

    def _get_async(self, kname, keys, frmt='json', prop=None):
        try:
	    rs = (self.get_one(**{'frmt': frmt, kname:key, 'async': True, 'prop': prop})
	      for key in keys)
	    return grequests.map(rs, size=min(Settings.Instance().CONCURRENT_SIZE, len(keys)))
        except Exception:
	    return None

#-----------------------------------------------------------------------------------------------------------------------

    def get_async(self, kname, keys, frmt='json', prop=None):
        ret = []
        if sys.platform == 'darwin': # thank you, Steve
		count = len(keys)
		for i in range(0, count, Settings.Instance().CONCURRENT_SIZE):
                    chunk = keys[i:i+Settings.Instance().CONCURRENT_SIZE]
                    ret.update(self._get_async(kname, chunk, frmt, prop))
        else:
            ret = self._get_async(kname, keys, frmt, prop)
        return self._apply(ret, self.get_val, frmt)

#-----------------------------------------------------------------------------------------------------------------------

    def get_sync(self, kname, keys, frmt='json', prop=None):
        return [self.get_one(**{'frmt': frmt, kname: key, 'prop': prop}) for key in keys]

#-----------------------------------------------------------------------------------------------------------------------

    def _get(self, kname, keys, frmt='json', prop=None):
        if isinstance(keys, list):
            if len(keys) > Settings.Instance().ASYNC_TRESHOLD:
                return self.get_async(kname, keys, frmt, prop)
            else:
                return self.get_sync(kname, keys, frmt, prop)
        return self.get_one(**{'frmt': frmt, kname: keys, 'prop': prop})

#-----------------------------------------------------------------------------------------------------------------------

    def get(self, chembl_id, frmt='json', prop=None):
        if chembl_id:
            return self._get('chembl_id', chembl_id, frmt, prop)
        return None

#-----------------------------------------------------------------------------------------------------------------------

    def _get_one(self, url, async, frmt):
        session = self._get_session()
        if async:
            return grequests.get(url, session=session)
        return self._process_request(url, session, frmt, timeout=Settings.Instance().TIMEOUT)

#-----------------------------------------------------------------------------------------------------------------------

    def get_one(self, chembl_id, frmt='json', async=False, prop=None):
        if chembl_id:
            if not prop:
                url = '%s/%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name, chembl_id, frmt)
            else:
                url = '%s/%s/%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name,
                                          chembl_id, prop, frmt)
            return self._get_one(url, async, frmt)

#-----------------------------------------------------------------------------------------------------------------------
