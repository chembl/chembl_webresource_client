__author__ = 'mnowotka'

import copy
import logging
from chembl_webresource_client import __version__
from chembl_webresource_client.settings import Settings
from chembl_webresource_client.url_query import UrlQuery

#-----------------------------------------------------------------------------------------------------------------------

class Model(object):
    def __init__(self, name, collection_name = None, formats=('json', 'xml'), searchable=False):
        self.name = name
        self.collection_name = collection_name
        self.formats = formats
        self.searchable=searchable

#This class is based on Django QuerySet (https://github.com/django/django/blob/master/django/db/models/query.py)

#-----------------------------------------------------------------------------------------------------------------------

class QuerySet(object):

#-----------------------------------------------------------------------------------------------------------------------

    def __init__(self, model=None, query=None):
        if model is not None:
            self.model = model
            self.query = UrlQuery(model)
        elif query is not None:
            self.model = query.model
            self.query = query
        self.logger = logging.getLogger(__name__)
        self.chunk = None
        self.current_index = 0
        self.can_filter = True
        self.limits = None
        self.searched = False

#-----------------------------------------------------------------------------------------------------------------------

    def __deepcopy__(self, memo):
        obj = self.__class__()
        for k, v in self.__dict__.items():
            if k != 'logger':
                obj.__dict__[k] = copy.deepcopy(v, memo)
        return obj

#-----------------------------------------------------------------------------------------------------------------------

    def __getstate__(self):
        obj_dict = self.__dict__.copy()
        obj_dict[Settings.Instance().CLIENT_VERSION_PICKLE_KEY] = __version__
        return obj_dict

#-----------------------------------------------------------------------------------------------------------------------

    def __setstate__(self, state):
        msg = None
        pickled_version = state.get(Settings.Instance().CLIENT_VERSION_PICKLE_KEY)
        if pickled_version:
            current_version = __version__
            if current_version != pickled_version:
                msg = ("Pickled queryset version {0} does not match the current version {1}" .format(
                    pickled_version, current_version))
        else:
            msg = "Pickled queryset version is not specified."

        if msg:
            self.logger.warning(msg)

#-----------------------------------------------------------------------------------------------------------------------

    def __repr__(self):
        if not self.query.allows_multiple:
            return '{0} resource'.format(self.model.name)
        clone = self._clone()
        data = list(clone[:Settings.Instance().REPR_OUTPUT_SIZE])
        length = len(self)
        if length > Settings.Instance().REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."
        else:
            data = data[:length]
        return repr(data)

#-----------------------------------------------------------------------------------------------------------------------

    def __len__(self):
        if not self.query.allows_multiple:
            return None
        if self.limits:
            if self.limits[1] is not None:
                return self.limits[1] - self.limits[0]
            return len(self.query) - self.limits[0]
        if not self.can_filter:
            return 1
        return len(self.query)

#-----------------------------------------------------------------------------------------------------------------------

    def __iter__(self):
        self.chunk = None
        self.current_index = 0
        self.query.__iter__()
        return self

#-----------------------------------------------------------------------------------------------------------------------

    def next(self):
        if not self.query.allows_multiple:
            return None
        if not self.chunk and not self.current_index:
            self.chunk = self.query.get_page()
        if not self.chunk or self.current_index >= len(self.chunk):
            self.chunk = self.query.next_page()
            if not self.chunk:
                raise StopIteration
            self.current_index = 0

        ret = self.chunk[self.current_index]
        self.current_index += 1
        return ret

#-----------------------------------------------------------------------------------------------------------------------

    def __next__(self):
        return self.next()

#-----------------------------------------------------------------------------------------------------------------------

    def __bool__(self):
        return bool(len(self))

#-----------------------------------------------------------------------------------------------------------------------

    def __nonzero__(self):
        return type(self).__bool__(self)

#-----------------------------------------------------------------------------------------------------------------------

    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results.
        """
        if not self.query.allows_multiple:
            return None
        if not isinstance(k, (slice,) + tuple([int])):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0)) or
                (isinstance(k, slice) and (k.start is None or k.start >= 0) and
                 (k.stop is None or k.stop >= 0))), \
            "Negative indexing is not supported."

        if isinstance(k, slice):
            clone = self._clone()
            clone.can_filter = False
            if k.start is not None:
                start = int(k.start)
            else:
                start = None
            if k.stop is not None:
                stop = int(k.stop)
            else:
                stop = None
            clone.limits = (start, stop) if start is not None else (0, stop)
            self.logger.info('__getitem__, self.limits = {0}, k = {1}'.format(clone.limits, k))
            clone.query.set_limits(clone.limits[0], clone.limits[1])
            return clone

        return self.query[k]

#-----------------------------------------------------------------------------------------------------------------------

    def get(self, *args, **kwargs):
        if args:
            return self.query.get(*args, **kwargs)
        if kwargs:
            clone = self._clone()
            clone.query.get(*args, **kwargs)
            return clone


#-----------------------------------------------------------------------------------------------------------------------

    def exists(self):
        return type(self).__bool__(self)

#-----------------------------------------------------------------------------------------------------------------------

    def all(self):
        if not self.query.allows_multiple:
            return None
        return self._clone()

#-----------------------------------------------------------------------------------------------------------------------

    def search(self, query):
        self.searched = True
        clone = self._clone()
        clone.query.search(query)
        return clone

#-----------------------------------------------------------------------------------------------------------------------

    def filter(self, **kwargs):
        if not self.query.allows_multiple:
            return None
        if kwargs:
            assert self.can_filter, "Cannot filter a query once a slice has been taken."
        clone = self._clone()
        clone.query.add_filters(**kwargs)
        return clone

#-----------------------------------------------------------------------------------------------------------------------

    def order_by(self, *field_names):
        assert not self.searched, "Cannot order search results"
        if not self.query.allows_multiple:
            return None
        if not self.query.allows_multiple:
            return None
        clone = self._clone()
        clone.query.set_ordering(*field_names)
        return clone

#-----------------------------------------------------------------------------------------------------------------------

    def only(self, *field_names):
        clone = self._clone()
        clone.query.set_only(*field_names)
        return clone

#-----------------------------------------------------------------------------------------------------------------------

    def ordered(self):
        if not self.query.allows_multiple:
            return None
        return self.query.ordering

    ordered = property(ordered)

#-----------------------------------------------------------------------------------------------------------------------

    def reverse(self):
        if not self.query.allows_multiple:
            return None
        assert self.ordered, "Cannot reverse unordered query set."
        self.query.reverse()

#-----------------------------------------------------------------------------------------------------------------------

    def set_format(self, frmt):
        self.query.set_format(frmt)

#-----------------------------------------------------------------------------------------------------------------------

    def url(self):
        return str(self.query)

#-----------------------------------------------------------------------------------------------------------------------

    def _clone(self):
        query = self.query.clone()
        clone = self.__class__(query=query)
        clone.limits = self.limits
        return clone

#-----------------------------------------------------------------------------------------------------------------------
