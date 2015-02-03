__author__ = 'mnowotka'

#-----------------------------------------------------------------------------------------------------------------------

import requests
import requests_cache
import grequests
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
        async = kwargs.get('async', False)
        prop = kwargs.get('prop', None)
        method = 'get'
        data = None
        if chembl_id:
            return super(CompoundResource, self).get_one(chembl_id=chembl_id, frmt=frmt, async=async, prop=prop)
        if 'stdinchikey' in kwargs:
            key = 'stdinchikey'
        elif 'smiles' in kwargs:
            key = 'smiles'
        else:
            self.logger.warning('No identifier given.')
            return None
        if any(x in kwargs[key] for x in self.url_unsafe_characters):
            url = '%s/%s/%s' % (Settings.Instance().webservice_root_url, self.name, key)
            method = 'post'
            data = {key : kwargs[key]}
        else:
            url = '%s/%s/%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name, key, kwargs[key], frmt)
        return self._get_one(url, async, frmt, method, data)

#-----------------------------------------------------------------------------------------------------------------------

    def forms(self, chembl_id, frmt='json'):
        return super(CompoundResource, self).get(chembl_id, frmt=frmt, prop='form')

#-----------------------------------------------------------------------------------------------------------------------

    def drug_mechanisms(self, chembl_id, frmt='json'):
        return super(CompoundResource, self).get(chembl_id, frmt=frmt, prop='drugMechanism')

#-----------------------------------------------------------------------------------------------------------------------

    def _get_method(self, struct, **kwargs):
        frmt = kwargs.get('frmt', 'json')
        session = self._get_session()
        if any(x in struct for x in self.url_unsafe_characters):
            data = {'smiles':struct}
            if 'simscore' in kwargs:
                data['simscore'] = kwargs['simscore']
                url = '%s/%s/similarity' % (Settings.Instance().webservice_root_url, self.name)
            else:
                url = '%s/%s/substructure' % (Settings.Instance().webservice_root_url, self.name)
            return self._process_request(url, session, frmt, timeout=Settings.Instance().TIMEOUT, method='post',
                data=data)
        if 'simscore' in kwargs:
            simscore = kwargs['simscore']
            url = '%s/%s/similarity/%s/%s.%s' % (Settings.Instance().webservice_root_url, self.name, struct,
                                                 simscore, frmt)
        else:
            url = '%s/%s/substructure/%s.%s' % (Settings.Instance().webservice_root_url, self.name, struct, frmt)
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
                if len(ids) > 10:
                    rs = (self.get_single_image(sid, True, **kwargs) for sid in ids)
                    ret = grequests.map(rs, size=50)
                    return self._apply(ret, self.get_val, None)
                ret = []
                for sid in ids:
                    ret.append(self.get_single_image(sid, False, **kwargs))
                return ret
            return self.get_single_image(ids, False, **kwargs)

#-----------------------------------------------------------------------------------------------------------------------

    def get_single_image(self, chembl_id, async, **kwargs):
        session = self._get_session()
        try:
            size = kwargs.get('size', 500)
            engine = kwargs.get('engine', 'rdkit')
            ignore_coords = kwargs.get('ignoreCoords', False)

            query = '?engine=%s&dimensions=%s' % (engine, size)
            if ignore_coords:
                query += '&ignoreCoords=1'

            if chembl_id:
                url = '%s/%s/%s/image%s' % (Settings.Instance().webservice_root_url, self.name, chembl_id, query)
                if async:
                    return grequests.get(url, session=session)
                res = session.get(url, timeout=Settings.Instance().TIMEOUT)
                if not res.ok:
                    self.logger.warning('Error when retrieving url: %s, status code: %s, msg: %s' %
                              (res.url, res.status_code, res.text))
                    return res.status_code
                self.logger.info(res.url)
                return res.content
            return None
        except Exception:
            return None

#-----------------------------------------------------------------------------------------------------------------------