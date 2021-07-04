from requests.auth import HTTPBasicAuth

from datenadler_rdf4j import __version__

from unittest import TestCase

from datenadler_rdf4j.api import tripel_store
from datenadler_rdf4j.constants import RDF4J_BASE, ADMIN_USER, ADMIN_PASS, VIEWER_PASS, VIEWER_USER, EDITOR_USER, \
    EDITOR_PASS


def test_version():
    assert __version__ == '0.1.0'

class TestRepositoryAPI(TestCase):

    def test_create_repository(self):
        sparql_endpoint = tripel_store.create_repository('test')

    def test_drop_repository(self):
        sparql_endpoint = tripel_store.drop_repository('test')


class TestRepositoryAuth(TestCase):

    ACTORS = {
        'viewer' : HTTPBasicAuth(VIEWER_USER, VIEWER_PASS),
        'editor' : HTTPBasicAuth(EDITOR_USER, EDITOR_PASS),
        'admin' : HTTPBasicAuth(ADMIN_USER, ADMIN_PASS)
    }
    actors = ['viewer', 'editor', 'admin']

    repos_dir = RDF4J_BASE + 'repositories'
    system_dir = RDF4J_BASE + 'repositories/SYSTEM'
    repo = RDF4J_BASE + 'repositories/test'

    QUERIES = {
        repo : {
            'params' :"""select {?s ?p ?o}""",
        }
    }

    PUT = tripel_store.put
    GET = tripel_store.get
    DELETE = tripel_store.delete
    POST = tripel_store.post

    METHODS = {
        'put' : PUT,
        'get' : GET,
        'delete' : DELETE,
        'post' :POST
    }

    methods = METHODS.keys()


    MATRIX = {
        repos_dir : {
            'admin' : {'get': 200,
                       'post': 500,
                       },
        },
        system_dir: {
            'admin' : {'get': 400,
                       'post': 415,
                       },
        },
        repo: {
            'admin' : {'get': 404,
                       'post': 404,
                       'put': 500,
                       'delete': 404,
                       },
            'editor' : {'get': 404,
                       'post': 404,
                       'put': 500,
                       },
            'viewer' : {'get': 400,
                       'post': 404,
                       }
        },
    }

    def testGet(self):
        sparql_endpoint = tripel_store.create_repository('test')


        def make_request(method, uri, actor):
            headers = {'content-type': 'application/x-turtle'}
            data = None
            if uri in self.QUERIES:
                data = self.QUERIES[uri]['params']

            if actor is not None:
                response = method(uri, headers=headers, data=data, auth=actor)
            else:
                response = method(uri, headers=headers, data=data)
            return response

        for uri in self.MATRIX:
            for actor in self.actors:
                for method in self.methods:
                    response = make_request(self.METHODS[method], uri, self.ACTORS[actor])
                    if actor in self.MATRIX[uri] and method in self.MATRIX[uri][actor]:
                        if response.status_code != self.MATRIX[uri][actor][method] :
                            a=5
                        assert response.status_code == self.MATRIX[uri][actor][method]
                    else:
                        if response.status_code == 200:
                            a=5
                        assert response.status_code != 200
