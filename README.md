[![Latest Version](https://img.shields.io/pypi/v/chembl_webresource_client.svg)](https://pypi.python.org/pypi/chembl_webresource_client/)
[![License](https://img.shields.io/pypi/l/chembl_webresource_client.svg)](https://pypi.python.org/pypi/chembl_webresource_client/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/chembl_webresource_client.svg)](https://pypi.python.org/pypi/chembl_webresource_client/)
[![Binder](http://mybinder.org/badge.svg)](http://beta.mybinder.org/v2/gh/chembl/chembl_webresource_client/master?filepath=demo_wrc.ipynb)


# ChEMBL webresource client

This is the only official Python client library developed and supported by ChEMBL group.

The library helps accessing ChEMBL data and cheminformatics tools from Python. You don't need to know how to write SQL. You don't need to know how to interact with REST APIs. You don't need to compile or install any cheminformatics frameworks. Results are cached.

The client handles interaction with the HTTPS protocol and caches all results in the local file system for faster retrieval. Abstracting away all network-related tasks, the client provides the end user with a convenient interface, giving the impression of working with a local resource. Design is based on the Django QuerySet interface. The client also implements lazy evaluation of results, which means it will only evaluate a request for data when a value is required. This approach reduces number of network requests and increases performance.

## Installation

```bash
pip install chembl_webresource_client
```

## Live Jupyter notebook with examples

[Click here](http://beta.mybinder.org/v2/gh/chembl/chembl_webresource_client/master?filepath=demo_wrc.ipynb)

## Available filters

The design of the client is based on Django QuerySet (https://docs.djangoproject.com/en/1.11/ref/models/querysets) and most important lookup types are supported. These are:

- exact
- iexact
- contains
- icontains
- in
- gt
- gte
- lt
- lte
- startswith
- istartswith
- endswith
- iendswith
- range
- isnull
- regex
- iregex
- search


## Only operator

`only` is a special method allowing to limit the results to a selected set of fields. only should take a single argument: a list of fields that should be included in result. Specified fields have to exists in the endpoint against which only is executed. Using only will usually make an API call faster because less information returned will save bandwidth. The API logic will also check if any SQL joins are necessary to return the specified field and exclude unnecessary joins with critically improves performance.

Please note that only has one limitation: a list of fields will ignore nested fields i.e. calling only(['molecule_properties__alogp']) is equivalent to only(['molecule_properties']).

For many 2 many relationships only will not make any SQL join optimisation.


## Settings

In order to use settings you need to import them before using the client:

```python
from chembl_webresource_client.settings import Settings
```

Settings object is a singleton that exposes Instance method, for example:

```python
Settings.Instance().TIMEOUT = 10
```

Most important options:

    CACHING: should results be cached locally (default is True)
    CACHE_EXPIRE: cache expiry time in seconds (default 24 hours)
    CACHE_NAME: name of the .sqlite file with cache
    TOTAL_RETRIES: number of total retires per HTTP request (default is 3)
    CONCURRENT_SIZE: total number of concurrent requests (default is 50)
    FAST_SAVE: Speedup cache saving up to 50 times but with possibility of data loss (default is True)


## Citing

https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4489243/
