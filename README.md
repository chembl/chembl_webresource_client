[![Latest Version](https://img.shields.io/pypi/v/chembl_webresource_client.svg)](https://pypi.python.org/pypi/chembl_webresource_client/)
[![License](https://img.shields.io/pypi/l/chembl_webresource_client.svg)](https://pypi.python.org/pypi/chembl_webresource_client/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/chembl_webresource_client.svg)](https://pypi.python.org/pypi/chembl_webresource_client/)
[![Binder](http://mybinder.org/badge.svg)](http://beta.mybinder.org/v2/gh/chembl/chembl_webresource_client/master?filepath=demo_wrc.ipynb)


# ChEMBL webresource client

This is the only official Python client library developed and supported by ChEMBL group.

## Key Features

* Easy access to ChEMBL data and tools from Python
* You do not need to know interations for SQL or REST APIs
* No need for compling or installing cheminformatics frameworks
* Automatic caching of results
* Abstraction of all network-related tasks
* Lazy evaluation of results to improve performance and reduce network requests

## Installation
Requires Python version >= 3.7. It can be installed using pip:
```bash
pip install chembl_webresource_client
```

## Live Jupyter notebook with examples

Explore live Jupyter notebooks [here](http://beta.mybinder.org/v2/gh/chembl/chembl_webresource_client/master?filepath=demo_wrc.ipynb)

## Available filters

The design of the client is based on Django QuerySet (https://docs.djangoproject.com/en/1.11/ref/models/querysets) and most important lookup types are supported. These are:
```bash
_exact
_iexact
_contains
_icontains
_in
_gt
_gte
_lt
_lte
_startswith
_istartswith
_endswith
_iendswith
_range
_isnull
_regex
_iregex
_search
```
## Example 

``` python
from chembl_webresource_client.new_client import new_client

molecule = new_client.molecule
mols = molecule.filter(pref_name__iexact='aspirin')
mols
```

## 'only' operator

The`only` method allows you to limit the results to a selected set of fields. It should take a **single argument**: a list of fields that should be included in result. Specified fields have to exists in the endpoint against which only is executed. Using `only` will usually make an API call faster because less information returned will save bandwidth. The API logic will also check if any SQL joins are necessary to return the specified field and exclude unnecessary joins with critically improves performance.

### Limitations

* A list of fields will ignore nested fields i.e. calling `only(['molecule_properties__alogp'])` is equivalent to `only(['molecule_properties'])`.

* For many-to-many relationships `only` will not make any SQL join optimisation.


## Settings

To configure the client, import the settings object:
```python
from chembl_webresource_client.settings import Settings
```

Settings object is a singleton that exposes Instance method, for example:

```python
Settings.Instance().TIMEOUT = 10
```

Key options inclde:

    CACHING: should results be cached locally (default is True)
    CACHE_EXPIRE: cache expiry time in seconds (default 24 hours)
    CACHE_NAME: name of the .sqlite file with cache
    TOTAL_RETRIES: number of total retires per HTTP request (default is 3)
    CONCURRENT_SIZE: total number of concurrent requests (default is 50)
    FAST_SAVE: Speedup cache saving up to 50 times but with possibility of data loss (default is True)

## Contributions

If you would like to contribue to this project, please follow these steps:

1. Fork this repository
2. Clone the forked respoitory to your local device
3. Make you changes, commit, and push to your fork.
4. Resolve, if any, merge conflicts 
5. Create a Pull request to the main repository

## Citing

For citations refer to: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4489243/

## License

The content of this respository is licensed under the Apache Software License.
