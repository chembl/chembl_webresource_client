__author__ = 'mnowotka'

from chembl_webresource_client.singleton import Singleton
from chembl_webresource_client import __version__

default_cache_name = '.chembl_ws_client__' + str(__version__)


@Singleton
class Settings:
    WEBSERVICE_PROTOCOL = 'https'
    WEBSERVICE_DOMAIN = 'www.ebi.ac.uk'
    WEBSERVICE_PREFIX = '/chemblws'
    CACHING = True
    FAST_SAVE = True
    TOTAL_RETRIES = 3
    BACKOFF_FACTOR = 2
    CONCURRENT_SIZE = 50
    ASYNC_TRESHOLD = 10
    CACHE_EXPIRE = 60 * 60 * 24
    CACHE_NAME = default_cache_name
    RESPECT_RATE_LIMIT = True
    TIMEOUT = 3.0
    UTILS_SPORE_URL = 'https://www.ebi.ac.uk/chembl/api/utils/spore'
    NEW_CLIENT_URL = 'https://www.ebi.ac.uk/chembl/api/data'
    UNICHEM_URL = 'https://www.ebi.ac.uk/unichem/rest'
    NEW_CLIENT_TIMEOUT = None
    TEST_CASE_TIMEOUT = 10
    MAX_LIMIT = 20
    REPR_OUTPUT_SIZE = 5
    MAX_URL_SIZE = 4000
    PROXIES = None
    CLIENT_VERSION_PICKLE_KEY = 'chembl_webresource_client_version'

    @property
    def webservice_root_url(self):
        return '{0}://{1}{2}'.format(self.WEBSERVICE_PROTOCOL, self.WEBSERVICE_DOMAIN, self.WEBSERVICE_PREFIX)

    def clear_cache(self):
        from requests_cache import clear
        clear()
