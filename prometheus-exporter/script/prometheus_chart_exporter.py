import argparse
import io
import json
import re
import requests
import sys
import shlex

import shutil

import plotly.express as px

from argparse import Namespace
from pandas import DataFrame
from prometheus_pandas.query import to_pandas

version = "1.0.0"


def url_type(arg_value, pat=re.compile(r"^https?://.+$")):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError(f"invalid url value: {arg_value}")
    return arg_value


def split_queries(pp):
    return shlex.split(pp)

def user_pass_type(value):
    if len(value.split(':')) != 2:
        raise argparse.ArgumentTypeError("user_pass must be in the format 'user:password'")
    return value

def argument_parser() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=version)

    parser.add_argument("-u", "--prometheus_url", required=True, type=url_type, help="prometheus base url")
    parser.add_argument("-a", "--auth", required=False, help="prometheus basic auth in base64")
    parser.add_argument("-x", "--user_pass", type=user_pass_type, required=False, help="prometheus user:password")
    parser.add_argument("-s", "--start_date", required=True, help="Metrics start date in epoch format")
    parser.add_argument("-e", "--end_date", required=True, help="Metrics end date in epoch format")
    parser.add_argument("-t", "--step", required=True, help="Metrics step in seconds")
    parser.add_argument("-q", "--queries", type=split_queries, required=True, help="Metric queries, space separated values")

    return parser.parse_args()


def create_http_session(basic_auth: str, type) -> requests.Session:
    http = requests.Session()
    if (type == 0):
        http.headers["Authorization"] = f"Basic {basic_auth}"
    elif (type == 1):
        credentials = basic_auth.split(':')
        http.auth = (credentials[0], credentials[1])
    http.verify = False
    return http


def get_metric(http_session: requests.Session, base_url: str, start_date: int, end_date: int, step: int,
               prometheus_query: str):
    url = f"{base_url.strip('/')}/api/v1/query_range"
    params = {"query": prometheus_query, "start": start_date, "end": end_date, "step": step}
    response = http_session.get(url, params=params)
    response.raise_for_status()
    return response.json()


def create_chart(title: str, table: DataFrame, buffer: io.StringIO):
    fig = px.line(table, title=title)
    fig.write_html(buffer)


def main():
    args = argument_parser()
    print("Executing Script Prometheus chart exporter version", version)
    metrics_values = []
    if (args.auth is not None) :
        http_session = create_http_session(args.auth, 0)
    elif (args.user_pass is not None):
        http_session = create_http_session(args.user_pass, 1)
    else :
        http_session = create_http_session(args.auth, 2)
    out_buff = io.StringIO()
    for query in args.queries:
        values = get_metric(http_session, args.prometheus_url, args.start_date, args.end_date, args.step, query)["data"]
        dataframe = to_pandas(values)
        create_chart(query, dataframe, out_buff)
        metrics_values.append({"expr": query, "result": values})

    with open("output.json", "w", newline="") as file:
        file.write(json.dumps(metrics_values))

    with open("output.html", "w", newline="") as file:
        out_buff.seek(0)
        shutil.copyfileobj(out_buff, file)

    out_buff.close()


if __name__ == "__main__":
    main()