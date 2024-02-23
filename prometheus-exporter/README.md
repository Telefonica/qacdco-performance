# Prometheus Exporter Tool

The Prometheus Exporter utilizes Prometheus, Pandas, and Plotly libraries to craft an HTML dashboard, and a json with raw data showcasing Prometheus metrics, all conveniently packaged within a Docker container

## Usage
To use the Prometheus Exporter, you must have a configuration file in YAML format that contains all the necessary parameters. Below is an example of such a file ('config.yaml'):

```yaml
prometheus_url: https://prometheus.example.com/metrics
start_date: 1679359438
end_date: 1679445838
interval: 60
generate_graphs: true
authentication:
  - type: user_password
    credentials: pepe:pepepassword
metrics:
  - query: prometheus_query_1
    metric_name: "apigw replicas"
    y_axis_units: "n replicas"
  - query: prometheus_query_2
    metric_name: "apigw replicas"
    y_axis_units: "n replicas"
```
### What is each parameter?

**prometheus_url**: the URL of the Prometheus server to query

**start_date**: the start date of the query range in Unix timestamp format

**end_date**: the end date of the query range in Unix timestamp format

**interval**: the step size of the query in seconds

**generate_graphs**: flag to generate (true) or not (false) the graphs on html file.

**authentication**: Contains information for authenticating with the Prometheus server. It's an array, allowing for multiple authentication methods Each method has a `type` and associated `credentials`.
- **type**: This specifies the authentication method. For example, "user_password" implies using a username and password combination.
This tool support 3 ways/`type`s of authentication (user_password / basic_auth / None (this `type` means without authentication))
- **credentials**: The actual credentials needed for the chosen type. Format for every type:

```yaml
authentication:
  - type: user_password
    credentials: pepe:pepepassword

authentication:
  - type: basic_auth
    credentials: stringtoken

authentication:
  - type: None
    credentials: None
```

**metrics**: An array containing the details of the Prometheus queries to be run and how they should be displayed.
- query: The actual Prometheus query string.
- metric_name: The name/title of the metric as it should appear in the output.
- y_axis_units: The units for the y-axis, if different from the general units for the metric.

Command to build the image: 
```bash
docker build -t img_prometheus_exporter_dev . -f ./docker/Dockerfile   
```
Execute the Docker container in the following manner:
```bash
docker run -v /path/to/config/directory:/app img_prometheus_exporter_dev /app/config.yaml
```

Ensure to replace /path/to/config/directory with the absolute path on your host where the yaml config file is located

### Where can I collect the results?
This tool leaves the results files by default in the `/app` directory(`ouput.json` for data file and `ouput.html` for graphs file), so it is advisable to take this into account when you want to collect the results from a container execution.

## Directory Structure

The directory structure of the project is as follows:

* docker/Dockerfile: the Dockerfile used to create the Docker container
* docker/requirements.txt: the requirements file for the Docker container, including the Plotly and Pandas libraries
* script/prometheus_chart_exporter.py: a Python script that collects input parameters and creates an HTML and JSON dashboard of the Prometheus queries.
* script/ConfigArgs.py: a python class that collects all the yaml parameters to pass them to prometheus_chart_exporter.py

## Requirements

**To run this tool on a container** you only need to have docker installed and the yaml configuration file created.


**To run this tool on your localhost without a container**, you just need to run:
```bash
pip3 install -r docker/requirements.txt
```

And you can go to ./script directory and run:
```bash
prometheus_chart_export.py example_config.yaml
```