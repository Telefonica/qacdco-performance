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


def read_queries_file(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise argparse.ArgumentTypeError(f'Failed to open file: {filename}')

    queries = [item['query'] for item in data]
    titles = [item['title'] for item in data]
    y_axis = [item['y_axis'] for item in data]

    if len(queries) != len(titles) or len(queries) != len(y_axis):
        raise argparse.ArgumentTypeError(f'Error: The number of queries, \
                                         titles and y_axis must be equal.')

    return queries, titles, y_axis



def url_type(arg_value, pat=re.compile(r"^https?://.+$")):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError(f"invalid url value: {arg_value}")
    return arg_value


def user_pass_type(value):
    if len(value.split(':')) != 2:
        raise argparse.ArgumentTypeError("user_pass must be in the format 'user:password'")
    return value


def argument_parser() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=version)
    parser.add_argument("-u", "--prometheus_url", required=True, type=url_type, help="prometheus base url")
    parser.add_argument("-a", "--auth", required=False, help="prometheus basic auth in base64")
    parser.add_argument("-f", "--queries_file", type=read_queries_file, required=True, help="queries file")
    parser.add_argument("-x", "--user_pass", type=user_pass_type, required=False, help="prometheus user:password")
    parser.add_argument("-s", "--start_date", required=True, help="Metrics start date in epoch format")
    parser.add_argument("-e", "--end_date", required=True, help="Metrics end date in epoch format")
    parser.add_argument("-t", "--step", required=True, help="Metrics step in seconds")
    parser.add_argument("-g", "--generate_graphs", required=False, 
                        help="If set on True, generate the graphs. Otherwise, only the JSON is generated.")
    args = parser.parse_args()
    return args


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
    #return response.json()
    #def get_pods_list(response):
    print(len(response))
    pod_list = []
    print (type(response))
    for dataframe in response.json:
        pod_match = re.search('pod="([a-zA-Z0-9-]+)"', dataframe)
        if pod_match:
            pod_value = pod_match.group(1)
            if pod_value not in pod_list:
                pod_list.append(pod_value)
    print (pod_list)
    return pod_list


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
    queries, titles, y_axis = args.queries_file
    out_buff = io.StringIO()
    for query, title, y_units in zip(queries, titles, y_axis):
        values = get_metric(http_session, args.prometheus_url,
                            args.start_date, args.end_date, args.step, query)["data"]
        dataframe = to_pandas(values)
        if args.generate_graphs == "True":
            create_chart(title, dataframe, out_buff, y_units)
        metrics_values.append({"expr": query, "title": title,
                                "y_units": y_units, "result": values})

    with open("output.json", "w", newline="") as file:
        file.write(json.dumps(metrics_values))

    if args.generate_graphs == "True":
        with open("output.html", "w", newline="") as file:
            out_buff.seek(0)
            shutil.copyfileobj(out_buff, file)

    out_buff.close()


if __name__ == "__main__":
    main()