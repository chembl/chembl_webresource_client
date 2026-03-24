from importlib.metadata import version

__author__ = 'mnowotka'

try:
    __version__ = version('chembl_webresource_client')
except Exception as e:
    __version__ = 'development'

import requests
