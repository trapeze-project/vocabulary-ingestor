# Data Adapter Service

The data adapter service's responsibilities are to present data from different sources in a uniform way. Whether you are connecting to a database, structured or unstructured, or to a file containing text or csv or ... this service will present the data with similar meta-data, formatting and access points.

## Adding the data adapter service to a docker-compose
The default docker-compose entry looks like this:
```
  data:
    image: data-adapter-service:0.01
    links:
      - db:db
    volumes:
      - ./config/adapters:/app/lib/connector

```

### Options
There are some options settable in the environment variables:

#### DEFAULT_GRAPH
the default value for this variable is:
```
"http://xdc.tenforce.com/application"
```

#### SPARQL_ENDPOINT
the default value for this variable is:
```
"http://db:8890/sparql"
```

## Adapters
The service requires adapters to be added.

TODO: fill this with adapter specs and information.

## Calls

### POST /connections
Returns a connectionConfiguration object with the configured options as validated by the connector. In case of a successful connection it returns 200 OK, otherwise a 404 if the connection could not be made.
Body:
```
{"port": "8888", "url": "http://example-database.com/connectionl", "username": "admin", "password": "sadmin", "database": "backer", "script": "ExampleConnector"}
```
#### Expected response code
200
#### response
```
{\n  "database": "backer", \n  "password": "sadmin", \n  "port": "8888", \n  "script": "ExampleConnector", \n  "url": "http://example-database.com/connectionl", \n  "username": "admin"\n}\n
```

### GET /connections/:connection-id
Returns a connectionConfiguration object for the connection with :connection-id or a 404 if the connection could not be found.
#### Parameters
```
 - connection-id
```
#### Expected response code
200
#### response
```
{\n  "database": "test", \n  "password": "password", \n  "port": "3306", \n  "script": "ExampleConnector", \n  "url": "http://localhost/exampleURL", \n  "user": "admin"\n}\n
```

### GET /schema/:connection-id
Returns the schema for the datasource with connection (:connection-id). This schema contains the hashes that will be used to verify that the schema has not changed.
#### Parameters
```
 - connection-id
```
#### Expected response code
200
#### response
```
{\n  "classes": {\n    "users": {\n      "class_hash": "5", \n      "properties": {\n        "email": "String", \n        "id": "Integer", \n        "name": "String", \n        "note": "String", \n        "tel": "String"\n      }\n    }\n  }, \n  "schema_hash": "6"\n}\n
```
### GET /count/:connection-id/:class-id
Returns the count of the data points in the class with id :class-id.
#### Parameters
```
 -  connection-id
 - class-id
```
#### Expected response code
200
#### response
```
2\n
```
### GET /sample/:connection-id/:class-id/:class-hash
Returns a stream of sample data points for the connection with id :connection-id and class with class :class-id. If the currently calculated hash does not match the one passed in :hash then the response code is 503 (SERVICE TEMPORARILY UNAVAILABLE) and this service sends a message on KAFKA stating that the datasource is in need of rescheduling.
#### Parameters
```
 - connection-id
 - class-id
 - class-hash this hash is checked against a freshly generated hash for that class, if it is different the this call returns a 503 to the caller and puts a 'schema expired'- message on KAFKA
```
#### Expected response code
200
### response
```
{"record": {"id": "1", "name": "jonathan", "email": "", "tel": "016 31 48 60", "note": ""}, "hashes": {"id": "1", "record": "2"}}\n{"record": {"id": "2", "name": "vincent", "email": "vincent.goossens@tenforce.com", "tel": "", "note": "in case of emergency call +32 16 31 48 60 thank you"}, "hashes": {"id": "3", "record": "4"}}
```

# Future releases
For now we only have the concept of an adapter. This will be split into an adapter and a reader. For databases this will make almost no difference, for folder/file based data sources such as FTP, file-share, sharepoint, google drive, ... it will allow us to decouple the accessing from the actual reading of contents.
