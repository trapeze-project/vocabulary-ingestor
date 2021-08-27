import os
import importlib
from PetanQ.petanq_resource import PetanqResource
from PetanQ.petanq import Petanq
from SPARQLWrapper import SPARQLWrapper, JSON, POST

# set up the SPARQL client
sparql = SPARQLWrapper(os.getenv("SPARQL_ENDPOINT"), defaultGraph=os.getenv('DEFAULT_GRAPH'))
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)

# returns the connector for a certain connector
def make_connector(connection_configuration):
  class_name = connection_configuration['script'] #[:-3]
  package_name = "lib.connector.%s" % (class_name)
  plugin_module = importlib.import_module(package_name, ".")
  plugin = getattr(plugin_module, class_name)
  connector = plugin(connection_configuration)
  return connector

# returns the same connection but with the properties
# that are described by the connector attached to it
# if they are present in the database
def get_properties_for_connection(connection, connector):
  query = """PREFIX dct: <http://purl.org/dc/terms/> 
PREFIX tf: <http://xdc.tenforce.com/elements/> 

SELECT ?property ?value
WHERE {
GRAPH <%s> {
  <%s> tf:connectorProperty ?cp .
  ?cp dct:title ?property .
  <%s> ?cp ?value .
  }
}""" % (os.environ['DEFAULT_GRAPH'], connector.getUri(), connection.getUri())
  sparql.setQuery(query)
  readResult = sparql.queryAndConvert()
  bindings = readResult['results']['bindings']

  connection_configuration = {
    'script': connector.attributes['script']
  }

  # already fill in the default values, if there are values set for them we will override them below anyway
  for connector_property in connector.relationships['properties']:
    if "defaultValue" in connector_property.attributes:
      connection_configuration[connector_property.attributes["title"]] = connector_property.attributes["defaultValue"]

  for binding in bindings:
    connection_configuration[binding['property']['value']] = binding['value']['value']

  return connection_configuration

def get_connection_configuration_for_connection(id):
  petanq = Petanq()
  # first we load the connection with id:
  connection = petanq.find(id , "connection")

  # then we materialise its connector
  petanq.load_relation(connection, "connector")
  connector = connection.relationships["connector"]

  # then we get the properties for that connector
  petanq.load_relation(connector, "properties")

  # we load the script relation
  petanq.load_relation(connector, "script")

  # we set the script location on the main connector model
  connector.addAttribute('script',connector.relationships['script'].attributes['fileLocation'])

  # now we load the connection configuration from the properties in the DB
  connection_configuration = get_properties_for_connection(connection, connector)

  return connection_configuration

def get_class_name_for_class_id(class_id):
  query = """PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX tf: <http://xdc.tenforce.com/elements/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>

SELECT ?title
WHERE {
GRAPH <%s> {
  ?s a <http://xdc.tenforce.com/elements/Class> ;
  mu:uuid "%s" ;
  dct:title ?title
  }
}""" % (os.environ['DEFAULT_GRAPH'], class_id)
  sparql.setQuery(query)
  readResult = sparql.queryAndConvert()
  bindings = readResult['results']['bindings']

  if len(bindings) > 0:
    title = bindings[0]['title']['value']
    return title

  return class_id

def raise_schema_expired_on_kafka(connection_id):
  pass

# get uuids for classes and properties in a connection
# return format:
# {
#   'className': {
#     'id': 'classId',
#     'properties': {
#       "prop1": "propid",
#       'fkProp': "ID of the PK it is pointing to"
#     }
#   }
# }
def get_class_and_property_uuids(connection_id):
  query = f"""
  PREFIX dct: <http://purl.org/dc/terms/>
  PREFIX tf: <http://xdc.tenforce.com/elements/>
  PREFIX dcat: <http://www.w3.org/ns/dcat#>
  PREFIX mu: <http://mu.semte.ch/vocabularies/core/>

  select ?classTitle ?classUuid ?propertyTitle ?propertyUuid ?fkUuid
  where {{
    ?dataset dcat:distribution / tf:connection / mu:uuid '{connection_id}'.
    ?dataset tf:datasetProfile / tf:schema / tf:class ?class.

    ?class dct:title ?classTitle;
           mu:uuid ?classUuid;
           tf:property ?property.
    ?property dct:title ?propertyTitle;
              mu:uuid ?propertyUuid.

    optional {{
     ?property tf:foreignKeyProperty / mu:uuid ?fkUuid.
    }}
  }}
  """
  sparql.setQuery(query)
  readResult = sparql.queryAndConvert()
  bindings = readResult['results']['bindings']

  ret = {}
  for row in bindings:
    classTitle = row['classTitle']['value']
    classUuid = row['classUuid']['value']
    propertyTitle = row['propertyTitle']['value']
    propertyUuid = row['propertyUuid']['value']
    # if there is a FK uuid, use that as uuid for the property
    # as it is a foreign key
    if 'fkUuid' in row.keys():
      propertyUuid = row['fkUuid']['value']

    # if the class is not in the dict yet, create it
    if classTitle not in ret.keys():
      ret[classTitle] = {
        'id': classUuid,
        'properties': {}
      }
    # save this property and it's uuid
    ret[classTitle]['properties'][propertyTitle] = propertyUuid

  return ret

def get_connection_id_for_class(class_id):
  q = f"""SELECT DISTINCT ?conn_uuid
  WHERE {{
    GRAPH <http://xdc.tenforce.com/application> {{
      ?class a <http://xdc.tenforce.com/elements/Class> ; ?uuid "{class_id}" .
      ?dataset <http://xdc.tenforce.com/elements/contains-class> ?class ; <http://www.w3.org/ns/dcat#distribution> ?dist.
      ?dist <http://xdc.tenforce.com/elements/connection> ?conn .
      ?conn <http://mu.semte.ch/vocabularies/core/uuid> ?conn_uuid .
  }}
}}"""
  sparql.setQuery(q)
  readResult = sparql.queryAndConvert()
  bindings = readResult['results']['bindings']
  if len(bindings) > 0:
    return bindings[0]["conn_uuid"]["value"]
