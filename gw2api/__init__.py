import requests
import copy

class GW2Client:
    '''Parent to store api objects'''

    LANG = 'en'
    VERS = 'v2'
    BASEURL = 'https://api.guildwars.com'

    def __init__(self, base_url=BASEURL, version=VERS, language=LANG, api_key=None, proxy=None, verify_ssl=True):

        assert version in ('v1', 'v2')
        assert language in ('en','es','de','fr','ko','zh')

        self.base_url=base_url
        self.version=version
        self.lang=language
        self.api_key=api_key
        self.proxy=proxy
        self.verify_ssl=verify_ssl

        if not self.verify_ssl:
                #Suppress warnings for verbosity
                requests.packages.urllib3.disable_warnings()

        GW2Client.LANG=language
        GW2Client.VERSION=version
        GW2Client.BASE_URL=base_url

        #Iniitializing session to assign api objects
        self.session = self.__build_requests_session()

        #constructs a list of API objects to assign to the instance
        self.__build_object_clients()

    def __build_requests_session(self):
        '''Build session to handle HTTP requests'''

        session = requests.Session()

        #Useful for proxy handling
        session.verify = self.verify_ssl

        session.headers.update({
            'User-Agent':'gw2-api-python-wrapper',
            'Accept':'application/json',
            'Accept-Language': GW2Client.LANG
        })

        if self.api_key:
            assert isinstance(self.api_key,str)
            session.headers.update({'Authorization':'Bearer' + self.api_key})

        return session

    def __build_object_clients(self):
        '''Generates and assigns API objects to instance'''

        if GW2Client.VERSION == 'v1':
            from gw2api.objects.api_version_1 import API_OBJECTS
        elif GW2Client.VERSION == 'v2':
            from gw2api.objects.api_version_2 import API_OBJECTS
        else:
            raise ValueError('Unable to import API Objects, make sure the version is correct - '+GW2Client.VERSION)

        objects=API_OBJECTS

        for object_ in objects:
            object_ = copy.copy(object_)
            object_.session=self.session
            setattr(self, object_.__class__.__name__.lower(), object_)

    def __repr__(self):
        return '<GW2 Client %s\nVersion: %s\nAPI_Key: %s\nLanguage: %s\nProxy: %s\nVerify SSL?: %s>'\
            % (self.base_url, self.version, self.api_key, self.language, self.proxy, self.verify_ssl)
