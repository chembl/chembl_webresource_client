__author__ = 'mnowotka'

import requests
import requests_cache
from chembl_webresource_client.spore_client import client_from_url
from chembl_webresource_client.settings import Settings

def get_session():
    s = Settings.Instance()
    if s.CACHING:
        session = requests_cache.CachedSession(s.CACHE_NAME, backend='sqlite',
                                               fast_save=s.FAST_SAVE, allowable_methods=('GET', 'POST'))
    else:
        session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=s.CONCURRENT_SIZE,
                                            pool_maxsize=s.CONCURRENT_SIZE, max_retries=3, pool_block=True)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

utils = client_from_url(Settings.Instance().UTILS_SPORE_URL, session=get_session())