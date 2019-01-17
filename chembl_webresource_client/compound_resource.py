__author__ = 'mnowotka'

#-----------------------------------------------------------------------------------------------------------------------
try:
    import grequests
except:
    grequests = None

import requests
import requests_cache

from chembl_webresource_client.web_resource import WebResource
from chembl_webresource_client.settings import Settings

#-----------------------------------------------------------------------------------------------------------------------


class CompoundResource(WebResource):
    name = 'compounds'

#-----------------------------------------------------------------------------------------------------------------------

    def get(self, chembl_id=None, **kwargs):
        frmt = kwargs.get('frmt', 'json')
        if chembl_id:
            return super(CompoundResource, self).get(chembl_id, frmt=frmt)
        if 'stdinchikey' in kwargs:
            kname = 'stdinchikey'
        elif 'smiles' in kwargs:
            kname = 'smiles'
        else:
            return None
        return self._get(kname, kwargs[kname], frmt)

#-----------------------------------------------------------------------------------------------------------------------

    def get_one(self, chembl_id=None, **kwargs):
        frmt = kwargs.get('frmt', 'json')
        async_query = kwargs.get('async_query', False)
        prop = kwargs.get('prop', None)
        method = 'get'
        data = None
        if chembl_id:
            return super(CompoundResource, self).get_one(chembl_id=chembl_id, frmt=frmt, async_query=async_query, prop=prop)
        if 'stdinchikey' in kwargs:
            key = 'stdinchikey'
        elif 'smiles' in kwargs:
            key = 'smiles'
        else:
            self.logger.warning('No identifier given.')
            return None
        if any(x in kwargs[key] for x in self.url_unsafe_characters):
            url = '{0}/{1}/{2}'.format(Settings.Instance().webservice_root_url, self.name, key)
            method = 'post'
            data = {key : kwargs[key]}
        else:
            url = '{0}/{1}/{2}/{3}.{4}'.format(Settings.Instance().webservice_root_url, self.name, key, kwargs[key], frmt)
        return self._get_one(url, async_query, frmt, method, data)

#-----------------------------------------------------------------------------------------------------------------------

    def forms(self, chembl_id, frmt='json'):
        return super(CompoundResource, self).get(chembl_id, frmt=frmt, prop='form')

#-----------------------------------------------------------------------------------------------------------------------

    def drug_mechanisms(self, chembl_id, frmt='json'):
        return super(CompoundResource, self).get(chembl_id, frmt=frmt, prop='drugMechanism')

#-----------------------------------------------------------------------------------------------------------------------

    def _get_method(self, struct, **kwargs):
        frmt = kwargs.get('frmt', 'json')
        with self._get_session() as session:
            if any(x in struct for x in self.url_unsafe_characters):
                data = {'smiles':struct}
                if 'simscore' in kwargs:
                    data['simscore'] = kwargs['simscore']
                    url = '{0}/{1}/similarity'.format(Settings.Instance().webservice_root_url, self.name)
                else:
                    url = '{0}/{1}/substructure'.format(Settings.Instance().webservice_root_url, self.name)
                return self._process_request(url, session, frmt, timeout=Settings.Instance().TIMEOUT, method='post',
                    data=data)
            if 'simscore' in kwargs:
                simscore = kwargs['simscore']
                url = '{0}/{1}/similarity/{2}/{3}.{4}'.format(Settings.Instance().webservice_root_url, self.name, struct,
                                                     simscore, frmt)
            else:
                url = '{0}/{1}/substructure/{2}.{3}'.format(Settings.Instance().webservice_root_url, self.name, struct, frmt)
            return self._process_request(url, session, frmt, timeout=Settings.Instance().TIMEOUT)

#-----------------------------------------------------------------------------------------------------------------------

    def substructure(self, struct, frmt='json'):
        return self._get_method(struct, frmt=frmt)

#-----------------------------------------------------------------------------------------------------------------------

    def similar_to(self, struct, simscore, frmt='json'):
        return self._get_method(struct, simscore=simscore, frmt=frmt)

#-----------------------------------------------------------------------------------------------------------------------

    def image(self, chembl_id=None, **kwargs):
        if chembl_id:
            ids = chembl_id
            if isinstance(ids, list):
                if grequests and len(ids) > 10:
                    rs = (self.get_single_image(sid, True, **kwargs) for sid in ids)
                    ret = grequests.map(rs, size=50)
                    return self._apply(ret, self.get_val, None)
                ret = []
                for sid in ids:
                    ret.append(self.get_single_image(sid, False, **kwargs))
                return ret
            return self.get_single_image(ids, False, **kwargs)

#-----------------------------------------------------------------------------------------------------------------------

    def get_single_image(self, chembl_id, async_query, **kwargs):
        try:
            size = kwargs.get('size', 500)
            engine = kwargs.get('engine', 'rdkit')
            ignore_coords = kwargs.get('ignoreCoords', False)

            query = '?engine={0}&dimensions={1}'.format(engine, size)
            if ignore_coords:
                query += '&ignoreCoords=1'

            if chembl_id:
                url = '{0}/{1}/{2}/image{3}'.format(Settings.Instance().webservice_root_url, self.name, chembl_id, query)
                with self._get_session() as session:
                    if async_query and grequests:
                        return grequests.get(url, session=session)
                    res = session.get(url, timeout=Settings.Instance().TIMEOUT)
                if not res.ok:
                    self.logger.warning('Error when retrieving url: {0}, status code: {1}, msg: {2}'.format(
                        res.url, res.status_code, res.text))
                    return res.status_code
                self.logger.info(res.url)
                return res.content
            return None
        except Exception:
            return None

#-----------------------------------------------------------------------------------------------------------------------
