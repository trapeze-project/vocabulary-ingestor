import os
from SPARQLWrapper import SPARQLWrapper, JSON, POST
from uuid import uuid4 as uuid
import datetime

# set up the SPARQL client
sparql = SPARQLWrapper(os.getenv("SPARQL_ENDPOINT"))
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)

# common interface for data-sources
class Dpv():
    data_source = None
    dpv_url = "https://raw.githubusercontent.com/dpvcg/dpv/master/dpv.rdf"
    new_version_identifier = None
    temporary_graph = None

    def __init__(self, data_source):
        self.data_source = data_source
        self.new_version_identifier = str(uuid())
        self.temporary_graph = "http://temporary-graph/" + self.new_version_identifier
        print("Import vocabulary")
        self.import_vocabulary()
        print("----------------------")
        print("Transform to base model")
        self.transform_to_base_model()
        print("----------------------")
        print("Generate ids")
        self.generate_ids()
        print("----------------------")
        print("Generate vocabulary version identifier")
        self.generate_vocabulary_version_identifier()
        print("----------------------")
        print("Delete old content")
        self.delete_old_content()
        print("----------------------")
        print("Insert new content")
        self.insert_new_content()
        print("----------------------")
        print("Delete temporary graph")
        self.delete_temporary_graph()
        print("----------------------")


    def close(self):
        pass

    def import_vocabulary(self):
        # Import rdf into a temporary graph
        query = """
            LOAD <%s>
            INTO GRAPH <%s>
        """ % (self.dpv_url, self.temporary_graph)
        print(query)
        sparql.setQuery(query)
        sparql.queryAndConvert()

    def transform_to_base_model(self):
        # Transform to classes and properties with the appropriate predicate
        pass

    def generate_ids(self):
        # Either generate brand new uuids or use the URIs to generate them
        query = """
        PREFIX mu:<http://mu.semte.ch/vocabularies/core/>

        INSERT {
        GRAPH <%s> {
                ?s mu:uuid ?uuid .
            }
        }
        WHERE
        {
            ?s a ?type .
            OPTIONAL { ?s mu:uuid ?id . }
            BIND(IF(BOUND(?id), ?id, STRUUID()) as ?uuid)
        }""" % self.temporary_graph
        print(query)
        sparql.setQuery(query)
        sparql.queryAndConvert()

    def generate_vocabulary_version_identifier(self):
        # Add on all resources a triple to identify what will need to be removed
        query = """
        INSERT {
        GRAPH <%s> {
                ?s <http://mu.semte.ch/vocabularies/ext/version-identifier> "%s" .
            }
        }
        WHERE
        {
            GRAPH <%s> {
                ?s a ?type .
            }
        }""" % (self.temporary_graph, self.new_version_identifier, self.temporary_graph)
        print(query)
        sparql.setQuery(query)
        sparql.queryAndConvert()

    def delete_old_content(self):
        # Remove the content from the previous iteration of this vocabulary
        if "version-identifier" in self.data_source["attributes"]:
            query = """
            DELETE { 
                GRAPH <%s> {
                    ?s <http://mu.semte.ch/vocabularies/ext/version-identifier> "%s" .
                    ?s ?p ?o . 
                }
            }
            WHERE {
            GRAPH <%s> {
                ?s <http://mu.semte.ch/vocabularies/ext/version-identifier> "%s" .
                OPTIONAL {
                    ?s ?p ?o .
                    FILTER NOT EXISTS {
                        ?s a <http://mu.semte.ch/vocabularies/ext/Data-Source> .
                    }
                    FILTER NOT EXISTS {
                        ?s <http://mu.semte.ch/vocabularies/ext/version-identifier> ?version .
                        FILTER(?version != "%s")
                    }
                }
            }
            }""" % (os.environ['DEFAULT_GRAPH'], self.data_source["attributes"]["version-identifier"],
                    os.environ['DEFAULT_GRAPH'], self.data_source["attributes"]["version-identifier"],
                    self.data_source["attributes"]["version-identifier"])
            print(query)
            sparql.setQuery(query)
            sparql.queryAndConvert()
        else:
            print("No old version")

    def insert_new_content(self):
        # Insert in the main graph
        query = """
        INSERT {
            GRAPH <%s> { 
                ?s ?p ?o . 
            }
        }
        WHERE {
            GRAPH <%s> {
                ?s ?p ?o .
            }
        }""" % (os.environ['DEFAULT_GRAPH'], self.temporary_graph)
        print(query)
        sparql.setQuery(query)
        sparql.queryAndConvert()
        self.data_source["attributes"]["version-identifier"] = self.new_version_identifier
        self.data_source["attributes"]["last-updated"] = str(datetime.datetime.now())

    def delete_temporary_graph(self):
        # Delete temporary graph
        query = """
        CLEAR GRAPH <%s>
        """ % self.temporary_graph
        print(query)
        sparql.setQuery(query)
        sparql.queryAndConvert()