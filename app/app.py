import json
import flask
import importlib
import requests
import traceback

def create_app():
  app = flask.Flask(__name__)

  @app.route("/ingest-data-sources", methods=["GET", "POST"])
  def ingest_data_sources():
    print("Ingesting data sources")
    print("----------------------")
    result = { "successes": {}, "failures": {} }
    data_sources = get_all_data_sources()
    for data_source in data_sources:
      try:
        print("Ingesting: " + data_source["attributes"]["label"])
        package_name = "lib.data-sources.%s" % (data_source["attributes"]["package-name"])
        plugin_module = importlib.import_module(package_name, ".")
        plugin = getattr(plugin_module, data_source["attributes"]["package-name"])
        print(plugin)
        plugin(data_source)
        update_data_source(data_source)
        result["successes"][data_source["id"]] = data_source["attributes"]["version-identifier"]
      except Exception as e:
        traceback.print_exc()
        result["failures"][data_source["id"]] = str(e)
      finally:
        print("----------------------")
    return flask.jsonify(result)

  def get_all_data_sources():
    print("Getting all data sources")
    url = "http://resource/data-sources"
    data = requests.get(url).json()
    print("----------------------")
    return data["data"]

  def update_data_source(data_source):
    print("Updating data sources")
    url = "http://resource/data-sources/" + data_source["id"]
    print(url)
    json_ds = { "data": data_source }
    print(json.dumps(json_ds))
    data = requests.patch(url, json= json_ds, headers= {"Content-Type": "application/vnd.api+json"})
    print(data)
    print("----------------------")
    return data

  return app