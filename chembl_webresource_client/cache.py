__author__ = 'mnowotka'

from requests_cache.backends.base import BaseCache, hashlib, _to_bytes

def create_key(self, request):
    key = hashlib.sha256()
    key.update(_to_bytes(request.method.upper()))
    key.update(_to_bytes(request.url))
    if request.body:
        key.update(_to_bytes(request.body))
    if request.headers and 'Accept' in request.headers:
        key.update(request.headers['Accept'])
    return key.hexdigest()

def monkeypatch_requests_cache():
    BaseCache.create_key = create_key
