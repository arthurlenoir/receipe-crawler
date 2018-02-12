import certifi
import json
import urllib
import urllib3

try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except Exception, e:
    pass

POOL_MANAGER = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs="/etc/ssl/certs/ca-certificates.crt")


class BabelNetClient:
    def __init__(self, api_key=None):
        self.scheme = 'https'
        self.host = 'babelnet.io'
        self.path = '/v4/'
        self.api_key = api_key

    def request(self, func, **kwargs):
        kwargs['key'] = self.api_key
        conn = POOL_MANAGER.connection_from_host(self.host, scheme=self.scheme)
        answer  = conn.urlopen('GET', self.path + func + '?' + urllib.urlencode(kwargs) + '&filterLangs=EN')
        try:
            data = answer.data.decode('utf-8')
            content = json.loads(data)
        except ValueError, e:
            print("%s %s" % (method, path))
            raise e
        return content

    def get_synset_ids(self, word, langs, filterLangs=None, pos=None, source=None, normalizer=True):
        return self.request('getSynsetIds', word=word, langs=langs, filterLangs=filterLangs, pos=pos, source=source, normalizer=normalizer)

    def get_synset(self, id, filterLangs=None):
        return self.request('getSynset', id=id, filterLangs=filterLangs)




#BABEL_APIKEY = '9ed6492f-0659-4d58-bd57-5ef4f7d16ce9'
