# -*- coding: utf-8 -*-

# Copyright (c) Telefónica Digital.
# CDO QA Team <qacdo@telefonica.com>

import argparse
import configparser
import requests
import json
import gzip
import argparse
import csv
import datetime
from pytz import timezone
from influxdb import InfluxDBClient

epoch_naive = datetime.datetime.utcfromtimestamp(0)
epoch = timezone('UTC').localize(epoch_naive)

def unix_time_millis(dt):
    return int((dt - epoch).total_seconds() * 1000)

##
## Check if data type of field is float
##
def isfloat(value):
        try:
            float(value)
            return True
        except:
            return False

##
## Check if data type of field is int
##
def isinteger(value):
        try:
            if(float(value).is_integer()):
                return True
            else:
                return False
        except:
            return False


# main
def loadCsv(inputfilename, servername, user, password, dbname, metric,
            timecolumn, timeformat, tagcolumns, fieldcolumns, usegzip,
            delimiter, batchsize, create, datatimezone, version, module, is_jmeter=False):
    host = servername[0:servername.rfind(':')]
    port = int(servername[servername.rfind(':') + 1:])
    client = InfluxDBClient(host, port, user, password, dbname)

    if (create == True):
        print('Deleting database %s' % dbname)
        client.drop_database(dbname)
        print('Creating database %s' % dbname)
        client.create_database(dbname)

    client.switch_user(user, password)

    # format tags and fields
    if tagcolumns:
        tagcolumns = tagcolumns.split(',')
    if fieldcolumns:
        fieldcolumns = fieldcolumns.split(',')

    # open csv
    datapoints = []
    count = 0
    with open(inputfilename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:

            # Change only in JMeter test files since it's a timestamp in ms and not on host resources files (i.e. memory)
            if is_jmeter:
                # JMeter
                # timecolumn = timeStamp
                seconds = int(row[timecolumn]) / 1000
                row[timecolumn] = datetime.datetime.utcfromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')

            # ISO Format (%Y-%m-%d %H:%M:%S)
            datetime_naive = datetime.datetime.strptime(row[timecolumn], timeformat)
            datetime_local = timezone(datatimezone).localize(datetime_naive)

            timestamp = unix_time_millis(datetime_local) * 1000000  # in nanoseconds

            tags = {}
            for t in tagcolumns:
                v = 0
                if t in row:
                    v = row[t]
                tags[t] = v
                tags["version"] = version
                tags["module"] = module

            fields = {}
            for f in fieldcolumns:
                v = 0
                if f in row:
                    if isfloat(row[f]): #the data is float?
                        v = float(row[f])
                    elif isinteger(row[f]): # the data is int?
                        v = int(row[f])
                    else: # the data is string
                        v = row[f]
                fields[f] = v

            point = {"measurement": metric, "time": timestamp, "fields": fields, "tags": tags}

            datapoints.append(point)
            count += 1

            if len(datapoints) % batchsize == 0:
                print('Read %d lines' % count)
                print('Inserting %d datapoints...' % (len(datapoints)))
                response = client.write_points(datapoints)

                if response == False:
                    print('Problem inserting points, exiting...')
                    exit(1)

                print("Wrote %d, response: %s" % (len(datapoints), response))

                datapoints = []

    # write rest
    if len(datapoints) > 0:
        print('Read %d lines' % count)
        print('Inserting %d datapoints...' % (len(datapoints)))
        response = client.write_points(datapoints)

        if response == False:
            print('Problem inserting points, exiting...')
            exit(1)

        print("Wrote %d, response: %s" % (len(datapoints), response))

    print('Done')


def parse_args():
    parser = argparse.ArgumentParser(description='Csv to influxdb.')

    parser.add_argument("-path", "--path_execution", nargs='?', default= 'wt_performance/project-example/config',
                        help="Path to properties.ini")

    parser.add_argument('-i', '--input', nargs='?', required=True,
                        help='Input csv file.')

    parser.add_argument('-v', '--version', nargs='?', required=True,
                        help='Version_Number')

    parser.add_argument('-mo', '--module', nargs='?', required=True,
                        help='Module_Number')

    parser.add_argument('-d', '--delimiter', nargs='?', required=False, default=',',
                        help='Csv delimiter. Default: \',\'.')

    parser.add_argument('-s', '--server', nargs='?', default='localhost:8086',
                        help='Server address. Default: localhost:8086')

    parser.add_argument('-u', '--user', nargs='?', default='root',
                        help='User name.')

    parser.add_argument('-p', '--password', nargs='?', default='root',
                        help='Password.')

    parser.add_argument('--dbname', nargs='?', required=True,
                        help='Database name.')

    parser.add_argument('--create', action='store_true', default=False,
                        help='Drop database and create a new one.')

    parser.add_argument('-m', '--metricname', nargs='?', default='value',
                        help='Metric column name. Default: value')

    parser.add_argument('-ma', '--machine', nargs='?', default='qacdo-es-pro-influxdb',
                        help='Machine name with the influx db database. Default: qacdo-es-pro-influxdb')

    parser.add_argument('-tc', '--timecolumn', nargs='?', default='timestamp',
                        help='Timestamp column name. Default: timestamp.')

    parser.add_argument('-tf', '--timeformat', nargs='?', default='%Y-%m-%d %H:%M:%S',
                        help='Timestamp format. Default: \'%%Y-%%m-%%d %%H:%%M:%%S\' e.g.: 1970-01-01 00:00:00')

    parser.add_argument('-tz', '--timezone', default='UTC',
                        help='Timezone of supplied data. Default: UTC')

    parser.add_argument('--fieldcolumns', nargs='?', default='value',
                        help='List of csv columns to use as fields, separated by comma, e.g.: value1,value2. Default: value')

    parser.add_argument('--tagcolumns', nargs='?', default='host',
                        help='List of csv columns to use as tags, separated by comma, e.g.: host,data_center. Default: host')

    parser.add_argument('-g', '--gzip', action='store_true', default=False,
                        help='Compress before sending to influxdb.')

    parser.add_argument('-b', '--batchsize', type=int, default=5000,
                        help='Batch size. Default: 5000.')

    parser.add_argument('-ij', '--is_jmeter', action= "store_true",
                        help='Indicates if it is a JMeter file')

    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = parse_args()

    config = configparser.ConfigParser()
    config.read(['properties.ini',
                 '{user_config_path}/properties.ini'.format(user_config_path=args.path_execution)])

    hosts = config['RemoteSUT']['host_name']
    address_machines = hosts.split(',')

    resp = requests.get(
        url="https://qacdco.d-consumer.com/agora/guma2/api/servers/" + args.machine + "/")
    host_influx = resp.json()['ip'] + ':8086'

    try:
        if args.is_jmeter:

            fieldcolumns = 'elapsed,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,sentBytes,grpThreads,allThreads,Latency,IdleTime,Connect'
            tagcolums = 'label,sentBytes'
            timecolum = 'timeStamp'
            metric_name = 'tmp_samples_jmeter'
            loadCsv(args.input, host_influx, influx_user, influx_pwd, args.dbname, metric_name,
                    timecolum, args.timeformat, tagcolums, fieldcolumns, args.gzip,
                    args.delimiter, args.batchsize, args.create, args.timezone, args.version, args.module, args.is_jmeter)

        else:

            for host in address_machines:

                name_file = 'tmp_collectd_cpu_measures_{}.csv'.format(host)
                metric_name = 'tmp_cpu_sar'
                fieldcolumns = '%system,%idle,%steal,%iowait,%nice,%user'
                tagcolums = 'host'
                timecolum= 'timestamp'
                loadCsv(args.input + name_file, host_influx, influx_user, influx_pwd, args.dbname, metric_name,
                                        timecolum, args.timeformat, tagcolums, fieldcolumns, args.gzip,
                                        args.delimiter, args.batchsize, args.create, args.timezone, args.version, args.module)

                name_file = 'tmp_collectd_network_measures_{}.csv'.format(host)
                metric_name = 'tmp_network_sar'
                fieldcolumns = 'txkB/s,IFACE,%ifutil,rxmcst/s,rxkB/s,rxpck/s,txcmp/s,txpck/s,rxcmp/s'
                tagcolums = 'host,IFACE'
                timecolum= 'timestamp'
                loadCsv(args.input + name_file, host_influx, influx_user, influx_pwd, args.dbname, metric_name,
                                        timecolum, args.timeformat, tagcolums, fieldcolumns, args.gzip,
                                        args.delimiter, args.batchsize, args.create, args.timezone, args.version, args.module)

                name_file = 'tmp_collectd_memory_measures_{}.csv'.format(host)
                metric_name = 'tmp_memory_sar'
                fieldcolumns = '%memused,kbactive,kbcached,kbdirty,kbinact,kbmemfree,kbbuffers'
                tagcolums = 'host'
                timecolum= 'timestamp'
                loadCsv(args.input + name_file, host_influx, influx_user, influx_pwd, args.dbname, metric_name,
                                        timecolum, args.timeformat, tagcolums, fieldcolumns, args.gzip,
                                        args.delimiter, args.batchsize, args.create, args.timezone, args.version, args.module)

                name_file = 'tmp_collectd_disk_measures_{}.csv'.format(host)
                metric_name = 'tmp_disk_sar'
                fieldcolumns = 'interval,bwrtn/s,tps,rtps,bread/s,wtps'
                tagcolums = 'host'
                timecolum= 'timestamp'
                loadCsv(args.input + name_file, host_influx, influx_user, influx_pwd, args.dbname, metric_name,
                                        timecolum, args.timeformat, tagcolums, fieldcolumns, args.gzip,
                                        args.delimiter, args.batchsize, args.create, args.timezone, args.version, args.module)

    except IOError, e:
        print (u"Probably there is a problem to locate .csv file. Don't worry if you ran the tests with the option"
               u" to retrieve the metrics off : %s" % e)

