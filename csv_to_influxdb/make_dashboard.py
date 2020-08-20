# -*- coding: utf-8 -*-

# Copyright (c) Telefónica Digital.
# CDO QA Team <qacdo@telefonica.com>

from jinja2 import Environment, FileSystemLoader
from variables import *
import os
import argparse
import requests
import json

def parse_args():
    parser = argparse.ArgumentParser(description='datasource influxdb & grafana.')
    parser.add_argument('-n', '--name', nargs='?', default='Performance',
                        help='Datasource name. Must be the same in Grafana & Influx')
    parser.add_argument('-i', '--output_dir', nargs='?', required=True,
                        help='Output dir')

    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = parse_args()

    url = "https://qacdco.d-consumer.com/grafana/api/datasources/name/performance_" + args.name.replace(" ", "%20")
    headers = {
        'Authorization': GRAFANA_AUTH_BEARER
    }
    resp = requests.get(url, headers=headers)

    if resp.status_code != 200: # The datasource is not created in Grafana platform, We create a new datasource
        payload = {
            "name": "performance_" + args.name,
            "type": "influxdb",
            "typeLogoUrl": "public/app/plugins/datasource/influxdb/img/influxdb_logo.svg",
            "url": INFLUX_DB_URL,
            "access":"proxy",
            "password": INFLUX_DB_PSWD,
            "user": INFLUX_DB_USER,
            "database": "performance_" + args.name,
            "basicAuth": False
        }
        url = "https://qacdco.d-consumer.com/grafana/api/datasources/"
        pythonToJson = json.dumps(payload, sort_keys=True, indent=4, separators=(',', ':'))
        resp = requests.post(url, data=payload, headers=headers)
        assert resp.status_code == 200, "Please check, the connection between Grafana datasource and InfluxDB can't be " \
                                        "created"

    path_origin = os.path.abspath(os.path.join('/opt', 'csv_to_influxdb'))
    env = Environment(loader=FileSystemLoader(path_origin))

    json_to_send = env.get_template('dashboard_template.json').render(data_source="performance_" + args.name)
    custom_path = os.path.join(args.output_dir, "dashboard.json")

    #Generate .json
    # We open the file, if the file exists before it is deleted. w-> only writing
    with open(custom_path, "w") as txt:
        txt.write(json_to_send.encode('utf-8'))
