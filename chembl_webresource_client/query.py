from chembl_webresource_client.settings import Settings
import os, os.path
import requests
import requests_cache
from requests.packages.urllib3.util import Retry


class Query(object):

    def __init__(self):
        self.session = None
        self._get_session()

    def _get_session(self):
        s = Settings.Instance()
        if not self.session:
            retry = Retry(total=s.TOTAL_RETRIES, backoff_factor=s.BACKOFF_FACTOR,
                          status_forcelist=(list(range(400, 421)) + list(range(500, 505))))
            size = s.CONCURRENT_SIZE
            adapter = requests.adapters.HTTPAdapter(pool_connections=size, pool_maxsize=size,
                                                    pool_block=True, max_retries=retry)
            home_directory = os.path.expanduser('~')
            self.session = requests_cache.CachedSession(
                os.path.join(home_directory, s.CACHE_NAME),
                backend='sqlite',
                expire_after=s.CACHE_EXPIRE,
                fast_save=s.FAST_SAVE,
                allowable_methods=('GET', 'POST'),
                include_get_headers=True) if s.CACHING else requests.Session()
            if s.PROXIES:
                self.session.proxies = s.PROXIES
            self.session.headers.update({"X-HTTP-Method-Override": "GET"})
            self.session.headers.update({'Content-type': 'application/json'})
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
        return self.session
