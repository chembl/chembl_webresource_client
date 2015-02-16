__author__ = 'mnowotka'

from chembl_webresource_client.singleton import Singleton


@Singleton
class Settings:
    WEBSERVICE_PROTOCOL = 'https'
    WEBSERVICE_DOMAIN = 'www.ebi.ac.uk'
    WEBSERVICE_PREFIX = '/chemblws'
    CACHING = True
    FAST_SAVE = True
    CONCURRENT_SIZE = 50
    ASYNC_TRESHOLD = 10
    CACHE_NAME = 'chembl_webresource_client'
    RESPECT_RATE_LIMIT = True
    TIMEOUT = 3.0
    UTILS_SPORE_URL = 'https://www.ebi.ac.uk/chembl/api/utils/spore'
    NEW_CLIENT_URL = 'https://www.ebi.ac.uk/chembl/api/data'
    TEST_CASE_TIMEOUT = 10
    MAX_LIMIT = 10
    REPR_OUTPUT_SIZE = 5
    MAX_URL_SIZE = 4000
    PROXIES = None
    CLIENT_VERSION_PICKLE_KEY = 'chembl_webresource_client_version'

    @property
    def webservice_root_url(self):
        return '%s://%s%s' % (self.WEBSERVICE_PROTOCOL, self.WEBSERVICE_DOMAIN, self.WEBSERVICE_PREFIX)

    def clear_cache(self):
        from requests_cache import clear
        clear()
