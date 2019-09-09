__author__ = 'mnowotka'

try:
    __version__ = __import__('pkg_resources').get_distribution('chembl_webresource_client').version
except Exception as e:
    __version__ = 'development'

import requests
try:
    import grequests
except:
    grequests = None

from chembl_webresource_client.assay_resource import AssayResource
from chembl_webresource_client.target_resource import TargetResource
from chembl_webresource_client.compound_resource import CompoundResource

__all__ = [
    "AssayResource",
    "TargetResource",
    "CompoundResource",
]
