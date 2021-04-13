__author__ = 'mnowotka'

from requests_cache.backends.base import BaseCache
from requests_cache.cache_keys import _encode
import hashlib

def create_key(self, request, **kwargs):
    key = hashlib.sha256()
    key.update(_encode(request.method.upper()))
    key.update(_encode(request.url))
    if request.body:
        key.update(_encode(request.body))
    if request.headers and 'Accept' in request.headers:
        key.update(_encode(request.headers['Accept']))
    return key.hexdigest()

def monkeypatch_requests_cache():
    BaseCache.create_key = create_key
