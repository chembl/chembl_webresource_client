__author__ = 'mnowotka'

from urllib.parse import urlparse
import requests
from chembl_webresource_client.query_set import QuerySet
from chembl_webresource_client.query_set import Model
from chembl_webresource_client.settings import Settings
from easydict import EasyDict

#-----------------------------------------------------------------------------------------------------------------------

class NewClient(object):
    pass

#-----------------------------------------------------------------------------------------------------------------------

def client_from_url(url, base_url=None):
    """Builds a client from an url

    :param url: the url you want to get the SPORE schema from
    :param session: the :class:`request.Session` instance to use. Defaults to
                    the requests module itself.

    """
    res = requests.get(url)
    if not res.ok:
        raise Exception('Error getting schema from url {0} with status {1} and msg {2}'.format(url, res.status_code, res.text))
    schema = res.json()
    if 'base_url' not in schema:
        if base_url:
            schema['base_url'] = base_url
        else:
            parsed_url = urlparse(url)
            schema['base_url'] = parsed_url.scheme + '://' + parsed_url.netloc + '/'
    if not schema['base_url'].endswith('/'):
        schema['base_url'] += '/'

    client = NewClient()
    client.description = EasyDict(schema)
    client.official = False # TODO: change

    keys = client.description.methods.keys()
    for method, definition in [(m,d) for (m,d) in client.description.methods.items() if
                               (m.startswith('POST_') or m.startswith('GET_')) and m.endswith('_detail')]:
        searchable = False
        if method.replace('dispatch_detail', 'get_search') in keys:
            searchable = True
        name = definition['resource_name']
        collection_name = definition['collection_name']
        formats = [format for format in definition['formats'] if format not in ('jsonp', 'html')]
        default_format = definition['default_format'].split('/')[-1]
        if not name:
            continue
        model = Model(name, collection_name, formats, searchable)
        qs = QuerySet(model=model)
        if default_format not in ('xml', 'svg+xml'):
            qs.set_format(default_format)
        setattr(client, name, qs)

    return client


#-----------------------------------------------------------------------------------------------------------------------

new_client = client_from_url(Settings.Instance().NEW_CLIENT_URL + '/spore')

#-----------------------------------------------------------------------------------------------------------------------