FROM python:3.6-stretch

RUN apt-get update
# for cx_oracle
RUN apt-get install -y unixodbc unixodbc-dev freetds-dev freetds-bin freetds-common tdsodbc

WORKDIR /app

RUN pip install requests
RUN pip install Flask
RUN pip install SPARQLWrapper
RUN pip install pyyaml
RUN pip install filepath

WORKDIR /app
COPY ./app /app/

ENV PYTHONUNBUFFERED=1
ENV DEFAULT_GRAPH="http://mu.semte.ch/application"
ENV SPARQL_ENDPOINT="http://db:8890/sparql"
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=true

CMD flask run --host=0.0.0.0 --with-threads
