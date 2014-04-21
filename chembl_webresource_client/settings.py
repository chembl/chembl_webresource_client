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
    TIMEOUT = 3.0

    @property
    def webservice_root_url(self):
        return '%s://%s%s' % (self.WEBSERVICE_PROTOCOL, self.WEBSERVICE_DOMAIN, self.WEBSERVICE_PREFIX)

    def clear_cache(self):
        from requests_cache import clear
        clear()
