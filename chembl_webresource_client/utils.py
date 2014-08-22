__author__ = 'mnowotka'

import requests
from chembl_webresource_client.spore_client import client_from_url
from chembl_webresource_client.settings import Settings

session = requests.Session()
utils = client_from_url(Settings.Instance().utils_spore_url)