import argparse
import io
import json
import requests
import sys
import shlex
import shutil
import plotly.express as px
import os
from argparse import Namespace
from pandas import DataFrame
from prometheus_pandas.query import to_pandas
from ConfigArgs import ConfigArgs
import yaml


version = "2.0.0"

def get_config_file_argument() -> str:
    parser = argparse.ArgumentParser(description="Prometheus Exporter Tool")
    parser.add_argument("config_file", type=str, help="Path to the YAML configuration file")
    args = parser.parse_args()
    return args.config_file


def read_yaml_configuration(file_name: str) -> dict:
    with open(file_name, 'r') as file:
        configuration = yaml.safe_load(file)
    return configuration

def yaml_parser(yaml_config: dict) -> Namespace:
    try:
        conf_yaml = ConfigArgs(yaml_config)
    except yaml.YAMLError as e:
        print("config_file:", e)
        print("Please read the usage section of the readme for this tool.")
        sys.exit(1)
    return conf_yaml


def create_http_session(authentication: list) -> requests.Session:
    http = requests.Session()
    
    auth_type = authentication[0]["type"]
    credentials = authentication[0]["credentials"]

    if (auth_type == "None"):
        pass
    elif (auth_type == "basic_auth"):
        http.headers["Authorization"] = f"Basic {credentials}"
    elif (auth_type == "user_password"):
        user, password = credentials.split(':')
        http.auth = (user, password)
    
    http.verify = False
    return http


def get_metric(http_session: requests.Session, base_url: str, start_date: int, end_date: int, step: int,
               prometheus_query: str):
    url = f"{base_url.strip('/')}/api/v1/query_range"
    params = {"query": prometheus_query, "start": start_date, "end": end_date, "step": step}
    response = http_session.get(url, params=params)
    response.raise_for_status()
    return response.json()


def create_chart(title: str, table: DataFrame, buffer: io.StringIO, y_axes: str):
    fig = px.line(table, title=title)
    fig.update_layout(title={
        'text': title,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
        })
    fig.update_yaxes(title_text=y_axes)
    fig.write_html(buffer)


def main(config_file_path):
    yaml_config = read_yaml_configuration(config_file_path)
    args = yaml_parser(yaml_config)
    print("Executing Script Prometheus chart exporter version", version)

    # Create session based on authentication
    http_session = create_http_session(args.authentication)

    metrics_values = []
    out_buff = io.StringIO()
    for metric in args.metrics:
        values = get_metric(http_session, args.prometheus_url,
                            args.start_date, args.end_date, args.step, metric["query"])["data"]
        dataframe = to_pandas(values)
        if args.generate_graphs:
            create_chart(metric["metric_name"], dataframe, out_buff, metric["y_axis_units"])
        metrics_values.append({"expr": metric["query"], "title": metric["metric_name"],
                               "y_units": metric["y_axis_units"], "result": values})
    
    with open("/app/output.json", "w", newline="") as file:
        file.write(json.dumps(metrics_values))

    if args.generate_graphs:
        with open("/app/output.html", "w", newline="") as file:
            out_buff.seek(0)
            shutil.copyfileobj(out_buff, file)

    out_buff.close()

if __name__ == "__main__":
    config_file_path = get_config_file_argument()
    if not os.path.exists(config_file_path):
        print(f"Error: The file {config_file_path} does not exist.")
        sys.exit(1)
    main(config_file_path)
