from urllib.parse import urljoin
import json

from chembl_webresource_client.settings import Settings
import time
import re
import requests
from easydict import EasyDict

OFFICIAL_ENDPOINT = re.compile('^http(s)?://www(dev)?.ebi.ac.uk/chembl/api/utils/spore')

def client_from_url(url, session=requests, base_url=None):
    """Builds a client from an url

    :param url: the url you want to get the SPORE schema from
    :param session: the :class:`request.Session` instance to use. Defaults to
                    the requests module itself.

    """
    schema = requests.get(url).json()
    if 'base_url' not in schema:
        if base_url:
            schema['base_url'] = base_url
        else:
            schema['base_url'] = '/'.join(url.split('/')[:-1])
    if not schema['base_url'].endswith('/'):
        schema['base_url'] += '/'

    official = True if OFFICIAL_ENDPOINT.match(url) else False

    return Client(description=schema, session=session, official=official)


def make_spore_function(client, method_definition):
    """Returns the actual function being exposed to the end user.

    :param client:
        the :class:`Client` instance to which the function will be bounded.

    :param method_definition:
        Definition of the method we are defining the function.
    """
    def spore_function(*method_args, **method_kw):
        return client.call_spore_function(
            method_definition, *method_args, **method_kw
        )

    spore_function.__doc__ = get_method_documentation(method_definition)
    return spore_function


def decode_response(resp, definition):
    """Decode the response if we know how to handle it"""
    try:
        return resp.content.decode()
    except:
        return resp.content


def define_format(kw, definition):
    """Set the correct Content-Type headers and encode the data to the right
    format, if we know how to handle it.
    """
    if 'json' in definition.formats:
        if 'headers' not in kw or 'Content-Type' not in kw['headers']:
            kw['headers'] = {'Content-Type': 'application/json'}

        if 'data' in kw:
            kw['data'] = json.dumps(kw['data'])
    # XXX deal with other formats


def get_method_documentation(definition):
    """Get the documentation from the SPORE format and attach it to the method
    that will be exposed to the user.

    :param definition: the definition of the method, from the SPORE file.
    """
    if 'description' not in definition:
        definition['description'] = ''

    documentation = """
{description}

This binds to the {path} method.
Output format is in {formats}.
""".format(**definition)
    return documentation


class Client(object):
    """The way to interact with the API.

    :param description:
        a python object containing the definition of the SPORE service

    :param session:
        a :class:`requests.Session` instance that will be used to perform the
        http requests.

    This client provides two main things: the description, available as
    a dotted dict, and a number of methods to interact with the service.
    """

    def __init__(self, description, session=None, official = False):
        self.description = EasyDict(description)
        if session is None:
            session = requests
        self.session = session
        self.official = official

        # for each method defined in the spore file, create a method on this
        # object.
        for method, definition in [(m,d) for (m,d) in self.description.methods.items() if
                                   m.startswith('POST_') or m == 'GET_status']:
            spore_function = make_spore_function(self, definition)
            name = ''.join(method.split('_')[1:])
            spore_function.__name__ = name
            setattr(self, name, spore_function)

    def call_spore_function(self, definition,
                            *method_args, **method_kw):
        """
        Handles the actual call to the resource and define for you some
        additional headers and behaviour depending on the spore definition
        that was given.

        :param method_definition:
            Definition of the method we are defining the function.

        :param service_description:
            SPORE description of the service. Could be useful to get top-level
            information, such as the base url of the service.
        """
        # for each param passed to the method,
        # match if it's needed in the path, and replace it there if
        # needed
        path = definition.path
        for kw in method_kw.keys():
            key = ':{0}'.format(kw)
            if key in path and kw != 'data':
                path = path.replace(key, method_kw.pop(kw))

        if path.startswith('/'):
            path = path[1:]
        url = urljoin(self.description.base_url, path)
        if len(method_args) == 1:
            method_kw['data'] = method_args[0]
        elif 'data' not in method_kw:
            resp = self.session.request(definition.method, url, data=json.dumps(method_kw))
            return decode_response(resp, definition)

        # make the actual query to the resource
        resp = self.session.request(definition.method, url, **method_kw)
        if (not hasattr(resp, 'from_cache') or not resp.from_cache) and (self.official or
                                                                         Settings.Instance().RESPECT_RATE_LIMIT):
            hourly_rate = int(resp.headers.get('x-hourlyratelimit-limit', 3600))
            freq_s = 3600 / float(hourly_rate)
            time.sleep(freq_s)

        return decode_response(resp, definition)
