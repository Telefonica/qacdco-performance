# Prometheus Exporter Tool

This tool provides a new tool called Prometheus Exporter, which uses Prometheus, Pandas, and Plotly libraries to create an HTML dashboard of Prometheus metrics. It is packaged in a Docker container for easy deployment.

## Usage

To use the Prometheus Exporter, run the following command:
**with authorization-header authentication**

```bash
./initDocker.sh -u [prometheus-url] -a [authorization-header] -s [start-date] -e [end-date] -t [step] -q '[prometheus-query]' -i '[graphs_info]'
```

**with user:password authentication**

```bash
./initDocker.sh -u [prometheus-url] -x [user:password] -s [start-date] -e [end-date] -t [step] -q '[prometheus-query]' -i '[graphs_info]'
```

This will build and run a Docker container with the specified parameters. The parameters are:

    -u: the URL of the Prometheus server to query
    -a: the authorization header or
    -x: user and password to use when querying the Prometheus server 
    -s: the start date of the query range in Unix timestamp format
    -e: the end date of the query range in Unix timestamp format
    -t: the step size of the query in seconds
    -q: the Prometheus query to run. This can be a single query or multiple queries separated by semicolons.
    -i: the title of these metrics and their units, separated by commas.
        The number of metrics info elements must match the number of queries provided,
        titles and axis units for each graph, separated by semicolons.

## Directory Structure

The directory structure of the project is as follows:

* exporter.sh: a shell script that collects input parameters and passes them to script/prometheus_chart_exporter.py
* initDocker.sh: a shell script that builds and runs a Docker container with the specified parameters
* docker/Dockerfile: the Dockerfile used to create the Docker container
* docker/requirements.txt: the requirements file for the Docker container, including the Plotly and Pandas libraries
* script/prometheus_chart_exporter.py: a Python script that collects input parameters and creates an HTML and JSON dashboard of the Prometheus queries.

## Example

Here is an example of how to use the Prometheus Exporter tool:

```bash
    ./initDocker.sh -u https://prometheus.example.com/metrics -a "Basic [authorization]" -s 1679359438 -e 1679445838 -t 60 -q 'sum(rate(container_cpu_usage_seconds_total{container="my-container"}[1m])) by (pod); sum(rate(container_memory_usage_bytes{container="my-container"}[1m])) by (pod)' -i 'cpu usage, vCPUs; containers memory, bytes'
```
This will create a Docker container that queries the Prometheus server at `https://prometheus.example.com/metrics` with the provided authorization header, for the time range between `1679359438` and `1679445838`, with a step size of `60` seconds. The Prometheus queries used will be `sum(rate(container_cpu_usage_seconds_total{container="my-container"}[1m])) by (pod); sum(rate(container_memory_usage_bytes{container="my-container"}[1m])) by (pod).`The title of each metric will be "cpu usage" and "containers memory" respectively, with "vCPUs" and "bytes" as the units.