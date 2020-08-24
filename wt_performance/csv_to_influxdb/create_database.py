# -*- coding: utf-8 -*-

# Copyright (c) Telefónica Digital.
# CDO QA Team <qacdo@telefonica.com>

from influxdb import InfluxDBClient
from variables import *
import requests
import argparse

influx_user = INFLUX_DB_USER
influx_pwd = INFLUX_DB_PSWD
port = "8086"

def parse_args():

    parser = argparse.ArgumentParser(description='Create database at influxdb.')
    parser.add_argument("-db", "--db_name", nargs='?', required= True, help="database name to create at influxdb."
                                                                            " No blank spaces are allowed")
    parser.add_argument('-D', '--delete', action= "store_true",
                        help='database name to delete')

    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = parse_args()

    resp = requests.get(
        url="https://qacdco.d-consumer.com/agora/guma2/api/servers/" + "qacdo-es-pro-influxdb" + "/")
    host_influx = resp.json()['ip']

    client = InfluxDBClient(host_influx, influx_port, influx_user, influx_pwd)
    dbs = client.get_list_database()

def exist_database(name_db):
    list_dbs = []
    for db in dbs:
        list_dbs.append(db.get('name'))
    return name_db in list_dbs


def create_database():
    if not exist_database(args.db_name):
        client.create_database(args.db_name)

    else:
        raise Exception("The database with name {db_name} already exist at qacdo-es-pro-influxdb, Please check"
                        .format(db_name=args.db_name))

if not args.delete:
    create_database()

elif args.delete:
    if exist_database(args.db_name):
        client.drop_database(args.db_name)
    else:
        raise Exception("The database with name {db_name} is not present at qacdo-es-pro-influxdb and can't be deleted,"
                        " Please check".format(db_name=args.db_name))
