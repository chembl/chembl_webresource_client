__author__ = 'mnowotka'

from chembl_webresource_client.settings import Settings
from xml.dom.minidom import parseString

try:
    from urllib import urlencode
    from urllib import quote
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import quote
import os, os.path
import requests
import requests_cache
import six
from six import string_types
import logging
import mimetypes
from chembl_webresource_client.cache import monkeypatch_requests_cache
from chembl_webresource_client.http_errors import handle_http_error
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter

mimetypes.init()
monkeypatch_requests_cache()


#-----------------------------------------------------------------------------------------------------------------------

class UrlQuery(object):

    def __init__(self, model):
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.base_url = Settings.Instance().NEW_CLIENT_URL + '/' +  model.name.lower()
        self.start = 0
        self.stop = None
        self.count = None
        self.searchable = model.searchable
        self.limit = Settings.Instance().MAX_LIMIT
        self.max_url_size = Settings.Instance().MAX_URL_SIZE
        self.timeout = Settings.Instance().NEW_CLIENT_TIMEOUT
        self.current_offset = 0
        self.current_index = 0
        self.current_chunk = None
        self.current_page = 0
        self.allows_list = True
        self.allows_multiple = True
        if model.collection_name:
            self.collection_name = model.collection_name.lower()
        else:
            self.allows_list = False
            self.allows_multiple = False
        self.api_total_count = None
        self.filters = []
        self.frmt = 'json'
        self.ordering = []
        self.session = None
        self._get_session()

#-----------------------------------------------------------------------------------------------------------------------

    def rewind(self):
        if self.stop and self.stop - self.start == 1:
            self.start = 0
            self.stop = None
        self.current_chunk = None
        self.current_offset = self.start
        self.current_index = 0
        self.current_page = 0

#-----------------------------------------------------------------------------------------------------------------------

    def set_limits(self, start, stop):
        if not self.allows_list:
            return
        if start is not None and stop is not None:
            if self.current_chunk and start >= self.start and self.current_page == int((start - self.start ) / self.limit) and \
               self.current_page == int((stop - self.start - 1) / self.limit):
                self.logger.info('reusing chunk')
                new_start = int((start-self.start) - self.current_page * self.limit)
                self.current_chunk = self.current_chunk[new_start:]
            else:
                self.logger.info('resetting chunk')
                self.current_chunk = None
        elif self.current_index >= self.limit:
            self.current_chunk = None
        self.start = start if start is not None else 0
        self.stop = stop
        if start is not None and stop is not None:
            self.count = stop - start
        else:
            self.count = None
            self.api_total_count = None
        if start is not None:
            self.current_offset = start
        else:
            self.current_offset = 0
        self.current_index = 0
        self.current_page = 0

#-----------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return quote(self.base_url + '?' + urlencode(self._prepare_url_params()))

#-----------------------------------------------------------------------------------------------------------------------

    def __deepcopy__(self, memo):
        result = self.clone(memo=memo)
        memo[id(self)] = result
        return result

#-----------------------------------------------------------------------------------------------------------------------

    def clone(self, memo=None):
        result = self.__class__(self.model)
        result.start = self.start
        result.stop = self.stop
        result.count = self.count
        result.limit = self.limit
        result.searchable = self.searchable
        result.base_url = self.base_url
        result.allows_list = self.allows_list
        result.allows_multiple = self.allows_multiple
        result.max_url_size = self.max_url_size
        result.current_offset = self.current_offset
        result.current_index = self.current_index
        result.current_chunk = self.current_chunk
        result.current_page = self.current_page
        result.api_total_count = self.api_total_count
        result.filters = self.filters[:]
        result.frmt = self.frmt
        result.ordering = self.ordering[:]
        return result

#-----------------------------------------------------------------------------------------------------------------------

    def __iter__(self):
        if not self.allows_list:
            return
        self.rewind()
        return self

#-----------------------------------------------------------------------------------------------------------------------

    def __len__(self):
        if not self.allows_list:
            return
        if not self.api_total_count:
            self.get_page()
        return self.api_total_count

#-----------------------------------------------------------------------------------------------------------------------

    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results.
        """
        if not self.allows_list:
            return
        if not isinstance(k, (slice,) + six.integer_types):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0)) or
                (isinstance(k, slice) and (k.start is None or k.start >= 0) and
                 (k.stop is None or k.stop >= 0))), \
            "Negative indexing is not supported."

        if isinstance(k, slice):
            if k.start is not None:
                start = int(k.start)
            else:
                start = None
            if k.stop is not None:
                stop = int(k.stop)
            else:
                stop = None
            self.set_limits(start, stop)
            page = self.get_page()
            if page:
                if start is None:
                    start = 0
                return page[:stop-start] if stop is not None else page
            return None

        self.set_limits(k, k + 1)
        page = self.get_page()
        if page:
            return page[0]
        return None

#-----------------------------------------------------------------------------------------------------------------------

    def add_filters(self, **kwargs):
        if not self.allows_list:
            return
        self.filters.extend([(key, quote(value) if isinstance(value, string_types) else value)
                             for key, value in kwargs.items()])
        self.set_limits(None, None)

#-----------------------------------------------------------------------------------------------------------------------

    def search(self, query):
        assert self.searchable, "This resource is not searchable"
        assert not self.filters, "You can add filters to refine search but you can't search among prefiltered results"
        self.filters = [('q', quote(query))]
        self.ordering = []
        self.base_url += '/search'
        self.set_limits(None, None)

#-----------------------------------------------------------------------------------------------------------------------

    def set_ordering(self, *fields):
        if not self.allows_list:
            return
        self.ordering = fields
        self.set_limits(None, None)

#-----------------------------------------------------------------------------------------------------------------------

    def reverse(self):
        if not self.allows_list:
            return
        self.ordering = ['-' + order for order in self.ordering]

#-----------------------------------------------------------------------------------------------------------------------

    def set_format(self, frmt):
        if self.frmt == frmt:
            return
        available_formats = self.model.formats or ('json', 'xml')
        if frmt not in available_formats:
            raise Exception('{0} is not an available format ({1})'.format(frmt, available_formats))
        self.frmt = frmt
        self.rewind()

#-----------------------------------------------------------------------------------------------------------------------

    def next(self):
        if not self.allows_list:
            return
        if self.count and self.current_index > self.count:
            raise StopIteration
        if not self.current_chunk:
            self.current_page = int(self.current_index / self.limit)
            self.get_page()
        if not self.current_chunk:
            raise StopIteration
        try:
            ret = self.current_chunk[int(self.current_index - self.limit * self.current_page)]
        except IndexError:
            raise StopIteration
        self.current_index += 1
        if self.current_page != int(self.current_index / self.limit):
            self.next_page()
        return ret

#-----------------------------------------------------------------------------------------------------------------------

    def __next__(self):
        return self.next()

#-----------------------------------------------------------------------------------------------------------------------

    def get(self, *args, **kwargs):
        if args:
            return self._get_by_ids(args[0])
        if kwargs and self.allows_list:
            return self._get_by_names(*list(kwargs.items())[0])

#-----------------------------------------------------------------------------------------------------------------------

    def _get_by_names(self, name, ids):
        if not name.endswith("__in"):
            filter_name = name + "__in"
        else:
            filter_name = name
        if not isinstance(ids, (list, tuple)):
            filter_val = str(ids)
        else:
            filter_val = ','.join([str(i) for i in ids])
        filter = (filter_name, filter_val)
        self.add_filters(**dict([filter]))
        return self

#-----------------------------------------------------------------------------------------------------------------------

    def _get_by_ids(self, ids):
        if self.frmt in ('mol', 'sdf'):
            headers = {'Accept': 'chemical/x-mdl-molfile'}
        else:
            headers = {'Accept': mimetypes.types_map['.'+self.frmt]}
        self.logger.info('headers:')
        self.logger.info(headers)
        if not isinstance(ids, (list, tuple)):
            url = self.base_url + '/'  + quote(str(ids))
            if self.frmt in ('mol', 'sdf'):
                url += '.sdf'
            if len(url) > self.max_url_size:
                raise Exception('URL {0} is longer than allowed {1} characters'.format(url, self.max_url_size))
            with self._get_session() as session:
                res = session.get(url, headers=headers, timeout=self.timeout)
            self.logger.info(res.url)
            self.logger.info('From cache: {0}'.format(res.from_cache if hasattr(res, 'from_cache') else False))
            if not res.ok:
                handle_http_error(res)
            if self.frmt == 'json':
                return res.json()
            elif self.frmt in ('xml', 'html', 'svg', 'txt', 'mol', 'sdf'):
                return res.text
            return res.content
        if not self.allows_multiple:
            self.logger.error("This resource doesn't accept multiple ids.")
            return
        ret = []
        url = self.base_url + '/set/'
        if len(url) > self.max_url_size:
            raise Exception('URL {0} is longer than allowed {1} characters'.format(url, self.max_url_size))
        for id in ids:
            if url.endswith('/'):
                url += quote(str(id))
                if len(url) > self.max_url_size:
                    raise Exception('URL {0} is longer than allowed {1} characters'.format(url, self.max_url_size))
            else:
                old_url = url
                url += ';' + quote(str(id))
                if len(url) > self.max_url_size:
                    with self._get_session() as session:
                        res = session.get(old_url, headers=headers, timeout=self.timeout)
                    self.logger.info(res.url)
                    self.logger.info('From cache: {0}'.format(res.from_cache if hasattr(res, 'from_cache') else False))
                    if not res.ok:
                        handle_http_error(res)
                    self._gather_results(res, ret)
        with self._get_session() as session:
            res = session.get(url, headers=headers, timeout=self.timeout)
        self.logger.info(res.url)
        self.logger.info('From cache: {0}'.format(res.from_cache if hasattr(res, 'from_cache') else False))
        if res.ok:
            self._gather_results(res, ret)
        else:
            handle_http_error(res)
        return ret

#-----------------------------------------------------------------------------------------------------------------------

    def _gather_results(self, request, ret):
        if self.frmt == 'json':
            json_data = request.json()
            ret.extend(json_data[self.collection_name])
        elif self.frmt in ('mol', 'sdf'):
            sdf_data = request.text.encode('utf-8')
            ret.extend(sdf_data.split('$$$$\n'))
        else:
            xml = parseString(request.text)
            ret.extend([e.toxml() for e in xml.getElementsByTagName(self.collection_name)[0].childNodes])

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
                allowable_methods=('GET', 'POST')) if s.CACHING else requests.Session()
            if s.PROXIES:
                self.session.proxies = s.PROXIES
            self.session.headers.update({"X-HTTP-Method-Override": "GET"})
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
        return self.session

#-----------------------------------------------------------------------------------------------------------------------

    def _prepare_url_params(self):
        url_params = self.filters[:]
        url_params.extend(map(lambda x:('order_by', x), self.ordering ))
        start = self.start
        url_params.extend([('limit', self.limit), ('offset', int(start + self.limit * self.current_page))])
        return url_params

#-----------------------------------------------------------------------------------------------------------------------

    def get_page(self):
        if not self.allows_list:
            return
        if (self.stop is not None and self.current_index >= self.stop) or \
           (self.api_total_count and self.current_index >= self.api_total_count):
            return []
        if not self.current_chunk or self.current_page != int(self.current_index / self.limit):
            self.current_page = int(self.current_index / self.limit)
            data = self._prepare_url_params()
            with self._get_session() as session:
                res = session.post(self.base_url + '.' + self.frmt, data=data, timeout=self.timeout)
            self.logger.info(res.url)
            self.logger.info(data)
            self.logger.info('From cache: {0}'.format(res.from_cache if hasattr(res, 'from_cache') else False))
            if not res.ok:
                handle_http_error(res)
            if self.frmt == 'json':
                json_data = res.json()
                self.current_chunk = json_data[self.collection_name]
                self.api_total_count = json_data['page_meta']['total_count']
            elif self.frmt in ('mol', 'sdf'):
                sdf_data = res.text.encode('utf-8')
                self.current_chunk = sdf_data.split('$$$$\n')
                with self._get_session() as session:
                    res = session.post(self.base_url + '.json', data=data, timeout=self.timeout)
                self.logger.info(res.url)
                self.logger.info(data)
                self.logger.info('From cache: {0}'.format(res.from_cache if hasattr(res, 'from_cache') else False))
                if not res.ok:
                    handle_http_error(res)
                json_data = res.json()
                self.api_total_count = json_data['page_meta']['total_count']
                aux_data = json_data[self.collection_name]
                for idx, mol in enumerate(aux_data):
                    if not mol['molecule_structures']:
                        self.logger.info((idx, mol['molecule_chembl_id']))
                        self.current_chunk.insert(idx, None)
                self.logger.info(aux_data)
                self.logger.info(self.current_chunk)
            else:
                xml = parseString(res.text.encode('utf-8'))
                self.current_chunk = [e.toxml() for e in xml.getElementsByTagName(self.collection_name)[0].childNodes]
                page_meta = xml.getElementsByTagName('page_meta')[0]
                self.api_total_count = int(page_meta.getElementsByTagName('total_count')[0].childNodes[0].data)
        start = self.start
        return self.current_chunk[:(self.stop - start) - self.current_index] if self.stop is not None else self.current_chunk

#-----------------------------------------------------------------------------------------------------------------------

    def next_page(self):
        if not self.allows_list:
            return
        start = self.start
        self.current_index = int(start + self.limit * (self.current_page + 1))
        return self.get_page()

#-----------------------------------------------------------------------------------------------------------------------

    def prev_page(self):
        if not self.allows_list:
            return
        if not self.current_page:
            return []
        start = self.start
        self.current_index = int(start + self.limit * (self.current_page - 1))
        return self.get_page()

#-----------------------------------------------------------------------------------------------------------------------

