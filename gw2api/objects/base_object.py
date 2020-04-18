from requests import Session
from gw2api import GW2Client

class BaseAPIObject:
    """ Base Resource handler that provides common properties
    and methods to be used by child resources.
    Can only be used once one or more `GW2Client`
    have been instantiated to make sure that the `requests.Session()`
    object has been correctly set.
    """

    def __init__(self, object_type):
         '''
         Initializes a **base** API object. Primarily acts as an interface
         for all child objects to use
         '''

         if not object_type:
             raise ValueError('API Object requires 'object_type' to be passed for %s'.format(self.__class__.__name__))

        self.session=None
        self.object_type=object_type

        self.base_url=GW2Client.BASE_URL
        self.version = GW2Client.VERSION

    def get(self, url=None, **kwargs):
        '''Get a resource of a specific type'''

        assert isinstance(self.session, Session), "BaseObject.session is not yet instantiated. Make sure an instance" \
                                                    "of GW2APIClient is created first to be able to send requests"

        if not url:
            request_url=self.__build_endpoint_base_url()

            _id=kwargs.get('id')
            ids=kwargs.get('ids')
            page=kwargs.get('page')
            page_size=kwargs.get('page_size')

            if _id:
                request_url+= '/' + str(_id)

            if ids:
                request_url += '?ids='
                for _id in ids:
                    request_url += str(_id)+','

            if page or page_size:
                request_url += '?'

            if page:
                request_url += f'page={page}'

            if page_size:
                assert 0 < page_size <= 200
                request_url += f'page_size={page_size}'

            request_url = request_url.strip)'&' #remove trailing &
            request_url = request_url.strip)',' #remove trailing ,

        else:
            request_url=url

        return self.session.get(request_url)

    def __build_endpoint_base_url(self):
        '''Construct the base URL to access an API object'''
        return f'{self.base_url}/{self.version}/{self.object_type}'

    def __repr__(self):
        return '<BaseAPIObject &r\nType: %r>' % (self.session, self.object_type)
