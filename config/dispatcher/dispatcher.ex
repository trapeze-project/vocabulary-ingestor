defmodule Dispatcher do
  use Matcher
  define_accept_types []

  match "/classes/*path" do
    forward conn, path, "http://resource/classes/"
  end

  match "/properties/*path" do
    forward conn, path, "http://resource/properties/"
  end

  match "/data-sources/*path" do
    forward conn, path, "http://resource/data-sources/"
  end

  match "/data-source-service/*path" do
    forward conn, path, "http://data-source:5000/"
  end
end