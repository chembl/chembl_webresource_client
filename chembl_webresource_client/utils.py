__author__ = 'mnowotka'

import requests
import requests_cache
from chembl_webresource_client.spore_client import client_from_url
from chembl_webresource_client.settings import Settings

def get_session():
    s = Settings.Instance()
    if s.CACHING:
        return requests_cache.CachedSession(s.CACHE_NAME, backend='sqlite',
                                                        fast_save=s.FAST_SAVE, allowable_methods=('GET', 'POST'))
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3, pool_block=True)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

utils = client_from_url(Settings.Instance().utils_spore_url, session=get_session())