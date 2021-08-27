import pytest
import yaml
import requests
import urllib3
from app import create_app
from os import environ as ENV

# Note: I normally use SPARQLWrapper when making SPARQL calls to the backend
#       because this failed I use the direct http call methods
# TODO: fix SPARQLWrapper in pytest use case

# Tests
def test_connections_post():
    app = create_app()
    clear_db()
    prepare_test_data()
    url = 'http://localhost:5000/connections/'
    expected_status_code = 200
    body = '{"port": "8888", "url": "http://example-database.com/connectionl", "username": "admin", "password": "sadmin", "database": "backer", "script": "ExampleConnector"}'
    response_text = b'{\n  "database": "backer", \n  "password": "sadmin", \n  "port": "8888", \n  "script": "ExampleConnector", \n  "url": "http://example-database.com/connectionl", \n  "username": "admin"\n}\n'
    response = app.test_client().post(url, data=body)
    assert response.status_code == expected_status_code
    assert response.data == response_text

def test_connections_get():
    app = create_app()
    clear_db()
    prepare_test_data()
    url = 'http://localhost:5000/connections/5B4620918D035A000900000A'
    expected_status_code = 200
    response_text = b'{\n  "database": "test", \n  "password": "password", \n  "port": "3306", \n  "script": "ExampleConnector", \n  "url": "http://localhost/exampleURL", \n  "user": "admin"\n}\n'

    response = app.test_client().get(url)
    assert response.status_code == expected_status_code
    assert response.data == response_text

def test_schema_get():
    app = create_app()
    clear_db()
    prepare_test_data()
    url = 'http://localhost:5000/schema/5B4620918D035A000900000A'
    expected_status_code = 200
    response_text = b'{\n  "classes": {\n    "users": {\n      "class_hash": "5", \n      "properties": {\n        "email": {\n          "type": "String"\n        }, \n        "id": {\n          "type": "Integer"\n        }, \n        "name": {\n          "type": "String"\n        }, \n        "note": {\n          "type": "String"\n        }, \n        "tel": {\n          "type": "String"\n        }\n      }\n    }\n  }, \n  "schema_hash": "6"\n}\n'
    response = app.test_client().get(url)
    assert response.status_code == expected_status_code
    assert response.data == response_text

def test_count_get():
    app = create_app()
    clear_db()
    prepare_test_data()
    url = 'http://localhost:5000/count/5B4620918D035A000900000A/5B46272D8D035A000900000F'
    expected_status_code = 200
    response_text = b'2\n'
    response = app.test_client().get(url)
    assert response.status_code == expected_status_code
    assert response.data == response_text

def test_sample_get():
    app = create_app()
    clear_db()
    prepare_test_data()
    url = 'http://localhost:5000/sample/5B4620918D035A000900000A/5B46272D8D035A000900000F/5'
    expected_status_code =  200
    response_text = b'{"record": {"id": "1", "name": "jonathan", "email": "", "tel": "016 31 48 60", "note": ""}, "hashes": {"id": "1", "record": "2"}}\n{"record": {"id": "2", "name": "vincent", "email": "vincent.goossens@tenforce.com", "tel": "", "note": "in case of emergency call +32 16 31 48 60 thank you"}, "hashes": {"id": "3", "record": "4"}}\n'
    response = app.test_client().get(url)
    assert response.status_code == expected_status_code
    assert response.data == response_text

def test_sample_get_wrong_hash():
    app = create_app()
    clear_db()
    prepare_test_data()
    url = 'http://localhost:5000/sample/5B4620918D035A000900000A/5B46272D8D035A000900000F/1'
    expected_status_code = 503
    response_text = b'[!] class has has expired, requested was: 1, found: 5'
    response = app.test_client().get(url)
    assert response.status_code == expected_status_code
    assert response.data == response_text

# Supporting methods
def default_graph():
    return ENV['DEFAULT_GRAPH']

def clear_db():
  query_dict = {
      "update": ("DELETE { GRAPH <%s> { ?s ?p ?o . } } WHERE { GRAPH <%s> {?s ?p ?o . } }" % (default_graph(), default_graph()))
      }
  query_url = 'http://db:8890/sparql?%s' % (urllib3.request.urlencode(query_dict))
  requests.get(query_url)

def prepare_test_data():
    with open("test_data/test_data.yaml", 'r') as stream:
        try:
            query_array = yaml.load(stream)
            for query in query_array:
                query_dict = {}
                query_dict["update"] = query.replace("DEFAULT_GRAPH", default_graph())
                query_url = 'http://db:8890/sparql?%s' % (urllib3.request.urlencode(query_dict))
                requests.get(query_url)
        except yaml.YAMLError as exc:
            print(exc)
