__author__ = 'mnowotka'

#-----------------------------------------------------------------------------------------------------------------------

try:
    import grequests
except:
    grequests = None

import requests
from requests.models import Response
import requests_cache

import sys
import time
import logging
from chembl_webresource_client.settings import Settings
from chembl_webresource_client import __version__ as version

#-----------------------------------------------------------------------------------------------------------------------


class WebResource(object):

#-----------------------------------------------------------------------------------------------------------------------

    content_types = {
        'json': 'application/json',
        'xml': 'application/xml',
    }

    url_unsafe_characters = ['/', '#']

#-----------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        self.cached_session = None
        self.session = None
        self.logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------------------------------------------------

    def _get_session(self):
        s = Settings.Instance()
        if s.CACHING:
            if not self.cached_session:
                self.cached_session = requests_cache.CachedSession(s.CACHE_NAME, backend='sqlite',
                                                            fast_save=s.FAST_SAVE, allowable_methods=('GET', 'POST'))
                adapter = requests.adapters.HTTPAdapter(pool_connections=s.CONCURRENT_SIZE,
                                                        pool_maxsize=s.CONCURRENT_SIZE, max_retries=3, pool_block=True)
                self.cached_session.mount('http://', adapter)
                self.cached_session.mount('https://', adapter)
            if s.PROXIES:
                self.cached_session.proxies = s.PROXIES
            return self.cached_session
        if not self.session:
            self.session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(pool_connections=s.CONCURRENT_SIZE,
                                                        pool_maxsize=s.CONCURRENT_SIZE, max_retries=3, pool_block=True)
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
            if s.PROXIES:
                self.session.proxies = s.PROXIES
        return self.session

#-----------------------------------------------------------------------------------------------------------------------

    def get_service(self):
        try:
            res = requests.get('{0}/status/'.format(Settings.Instance().webservice_root_url,
                               timeout=Settings.Instance().TIMEOUT))
            if not res.ok:
                self.logger.warning('Error when retrieving url: {0}, status code: {1}, msg: {2}'.format(
                    res.url, res.status_code, res.text))
                return None
            self.logger.info(res.url)
            self.logger.info('From cache: {0}'.format(res.from_cache if hasattr(res, 'from_cache') else False))
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

    def _process_request(self, url, session, frmt, method='get', data=None, **kwargs):
        try:
            if method == 'get':
                res = session.get(url, **kwargs)
            else:
                res = session.post(url, data=data, headers={'Accept': self.content_types[frmt]}, **kwargs)
            if not res.ok:
                self.logger.warning('Error when retrieving url: {0}, status code: {1}, msg: {2}'.format(
                    res.url, res.status_code, res.text))
                return res.status_code
            self.logger.info(res.url)
            self.logger.info('From cache: {0}'.format(res.from_cache if hasattr(res, 'from_cache') else False))
            return list(res.json().values())[0] if frmt == 'json' else res.content
        except Exception:
            return None

#-----------------------------------------------------------------------------------------------------------------------

    def bioactivities(self, chembl_id, frmt='json'):
        url = '{0}/{1}/{2}/bioactivities.{3}'.format(Settings.Instance().webservice_root_url, self.name, chembl_id, frmt)
        with self._get_session() as session:
            return self._process_request(url, session, frmt, timeout=Settings.Instance().TIMEOUT)

#-----------------------------------------------------------------------------------------------------------------------

    def get_val(self, x, frmt):
        if type(x) is not Response:
            return x
        if frmt == 'json':
            return list(x.json().values())[0] if x.ok else x.status_code
        else:
            return x.content if x.ok else x.status_code

#-----------------------------------------------------------------------------------------------------------------------

    def _apply(self, iterable, fn, *args, **kwargs):
        return [fn(x, *args, **kwargs) for x in iterable if x is not None]

#-----------------------------------------------------------------------------------------------------------------------

    def _get_async(self, kname, keys, frmt='json', prop=None, retry=0):
        try:
          rs = (self.get_one(**{'frmt': frmt, kname:key, 'async_query': True, 'prop': prop})
	      for key in keys)
          return grequests.map(rs, size=min(Settings.Instance().CONCURRENT_SIZE, len(keys)))
        except Exception:
            return []

#-----------------------------------------------------------------------------------------------------------------------

    def get_async(self, kname, keys, frmt='json', prop=None):
        ret = self._get_async(kname, keys, frmt, prop)
        return self._apply(ret, self.get_val, frmt)

#-----------------------------------------------------------------------------------------------------------------------

    def get_sync(self, kname, keys, frmt='json', prop=None):
        return [self.get_one(**{'frmt': frmt, kname: key, 'prop': prop}) for key in keys]

#-----------------------------------------------------------------------------------------------------------------------

    def _get(self, kname, keys, frmt='json', prop=None):
        if isinstance(keys, list):
            if len(keys) > Settings.Instance().ASYNC_TRESHOLD and grequests:
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

    def _get_one(self, url, async_query, frmt, method='get', data=None):
        with self._get_session() as session:
            if async_query and grequests:
                if method == 'get':
                    return grequests.get(url, session=session)
                else:
                    return grequests.post(url, session=session, data=data, headers={'Accept': self.content_types[frmt]})
            return self._process_request(url, session, frmt, timeout=Settings.Instance().TIMEOUT, method=method, data=data)

#-----------------------------------------------------------------------------------------------------------------------

    def get_one(self, chembl_id, frmt='json', async_query=False, prop=None):
        if chembl_id:
            if not prop:
                url = '{0}/{1}/{2}.{3}'.format(Settings.Instance().webservice_root_url, self.name, chembl_id, frmt)
            else:
                url = '{0}/{1}/{2}/{3}.{4}'.format(Settings.Instance().webservice_root_url, self.name,
                                          chembl_id, prop, frmt)
            return self._get_one(url, async_query, frmt)

#-----------------------------------------------------------------------------------------------------------------------
