__author__ = 'mnowotka'

from chembl_webresource_client.settings import Settings

import re
import os
import logging
import requests
import requests_cache
import mimetypes
from chembl_webresource_client.http_errors import handle_http_error
from requests.packages.urllib3.util import Retry

inchi_key_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

#-----------------------------------------------------------------------------------------------------------------------

mimetypes.init()

#-----------------------------------------------------------------------------------------------------------------------

class UniChemClient(object):

#-----------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        self.session = None
        self._get_session()
        self.base_url = Settings.Instance().UNICHEM_URL
        self.timeout = Settings.Instance().NEW_CLIENT_TIMEOUT
        self.logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------------------------------------------------

    def _get_session(self):
        s = Settings.Instance()
        if not self.session:
            retry = Retry(total=s.TOTAL_RETRIES, backoff_factor=s.BACKOFF_FACTOR,
                    status_forcelist=(list(range(400, 421)) + list(range(500, 505))))
            size = s.CONCURRENT_SIZE
            adapter = requests.adapters.HTTPAdapter(pool_connections=size, pool_maxsize=size, pool_block=True,
                max_retries=retry)
            home_directory = os.path.expanduser('~')
            self.session = requests_cache.CachedSession(os.path.join(home_directory, s.CACHE_NAME), backend='sqlite',
                expire_after=s.CACHE_EXPIRE, fast_save=s.FAST_SAVE,
                allowable_methods=('GET', 'POST'),
                include_get_headers=True) if s.CACHING else requests.Session()
            if s.PROXIES:
                self.session.proxies = s.PROXIES
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
        return self.session

#-----------------------------------------------------------------------------------------------------------------------

    def _get_results(self, url):
        with self._get_session() as session:
                res = session.get(url, timeout=self.timeout)
                self.logger.info(res.url)
                self.logger.info('From cache: {0}'.format(res.from_cache if hasattr(res, 'from_cache') else False))
                if not res.ok:
                    handle_http_error(res)
                return res.json()

#-----------------------------------------------------------------------------------------------------------------------

    def get(self, pk, src_id=None, to_src_id=None, all=False, url=False, verbose=False):
        if pk.upper().startswith('CHEMBL'):
            if to_src_id:
                if url:
                    url = '{0}/src_compound_id_url/{1}/{2}/{3}'.format(self.base_url, pk, src_id, to_src_id)
                elif all:
                    url = '{0}/src_compound_id_all/{1}/{2}/{3}'.format(self.base_url, pk, src_id, to_src_id)
                elif src_id:
                    url = '{0}/src_compound_id/{1}/{2}/{3}'.format(self.base_url, pk, src_id, to_src_id)
                else:
                    url = '{0}/src_compound_id/{1}/{2}/{3}'.format(self.base_url, pk, 1, to_src_id)
            else:
                if all:
                    url = '{0}/src_compound_id_all/{1}/{2}'.format(self.base_url, pk, src_id)
                elif src_id:
                    url = '{0}/src_compound_id/{1}/{2}'.format(self.base_url, pk, src_id)
                else:
                    url = '{0}/src_compound_id/{1}/{2}'.format(self.base_url, pk, 1)
        elif inchi_key_regex.match(pk):
            if all:
                url = '{0}/inchikey_all/{1}'.format(self.base_url, pk)
            elif verbose:
                url = '{0}/verbose_inchikey/{1}'.format(self.base_url, pk)
            else:
                url = '{0}/inchikey/{1}'.format(self.base_url, pk)
        else:
            if to_src_id:
                url = '{0}/src_compound_id_all_obsolete/{1}/{2}/{3}'.format(self.base_url, pk, src_id, to_src_id)
            elif src_id:
                url = '{0}/src_compound_id_all_obsolete/{1}/{2}'.format(self.base_url, pk, src_id)
            else:
                url = '{0}/orphanIdMap/{1}'.format(self.base_url, pk)
        return self._get_results(url)

#-----------------------------------------------------------------------------------------------------------------------

    def map(self, src, dst=None):
        if dst:
            url = '{0}/mapping/{1}/{2}'.format(self.base_url, src, dst)
        else:
            url = '{0}/mappingaux/{1}'.format(self.base_url, src)
        return self._get_results(url)

#-----------------------------------------------------------------------------------------------------------------------

    def src(self, pk=None):
        if not pk:
            url = '{0}/src_ids/'.format(self.base_url)
        else:
            url = '{0}/sources/{1}'.format(self.base_url, pk)
        return self._get_results(url)

#-----------------------------------------------------------------------------------------------------------------------

    def structure(self,pk,src, all=False):
        if all:
            url = '{0}/structure_all/{1}/{2}'.format(self.base_url,pk,src)
        else:
            url = '{0}/structure/{1}/{2}'.format(self.base_url,pk,src)
        return self._get_results(url)

#-----------------------------------------------------------------------------------------------------------------------

    def inchiFromKey(self, inchi_key):
        url = '{0}/inchi/{1}'.format(self.base_url, inchi_key)
        return self._get_results(url)

#-----------------------------------------------------------------------------------------------------------------------

    def connectivity(self, pk, src_id=None, **kwargs):
        if pk.upper().startswith('CHEMBL'):
            search_type = 'cpd_search'
        else:
            search_type = 'key_search'

        A = kwargs.get('a') or kwargs.get('A') or kwargs.get('sources') or 0
        B = kwargs.get('b') or kwargs.get('B') or kwargs.get('pattern') or 0
        C = kwargs.get('c') or kwargs.get('C') or kwargs.get('component_mapping') or 0
        D = kwargs.get('d') or kwargs.get('D') or kwargs.get('frequency') or 0
        E = kwargs.get('e') or kwargs.get('E') or kwargs.get('inchi_length') or 0
        F = kwargs.get('f') or kwargs.get('F') or kwargs.get('unichem_labels') or 0
        G = kwargs.get('g') or kwargs.get('G') or kwargs.get('assignment_status') or 0
        H = kwargs.get('h') or kwargs.get('H') or kwargs.get('data_structure') or 0

        if B not in (0,1):
            assert False, "Pattern (B) can only be 0 or 1"
        if C not in range(5):
            assert False, "Component mapping (C) can only be in (0,1,2,3,4)"
        if D not in range(501):
            assert False, "Frequency (D) can only be in range 0-500"
        if G not in (0,1):
            assert False, "Assignment status (G) can only be 0 or 1"

        if search_type == 'cpd_search' and src_id:
            url = '{0}/{1}/{2}/{3}/{4}/{5}/{6}/{7}/{8}/{9}/{10}/{11}'.format(
                                                    self.base_url, search_type, pk, src_id, A, B, C, D, E, F, G, H)
        else:
            url = '{0}/{1}/{2}/{3}/{4}/{5}/{6}/{7}/{8}/{9}/{10}'.format(
                                                    self.base_url, search_type, pk, A, B, C, D, E, F, G, H)
        return self._get_results(url)

#-----------------------------------------------------------------------------------------------------------------------

unichem_client = UniChemClient()