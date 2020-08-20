# -*- coding: utf-8 -*-

# Copyright Telefonica Digital
# CDO QA Team <qacdo@telefonica.com>

import logging.config
import subprocess
from logging import getLogger
from fabric_utils import FabricUtils
from fabric.api import get
from optparse import OptionParser
from io import BytesIO
from StringIO import StringIO
import configparser
import argparse
import time
from datetime import datetime

FILE_RAW = 'raw'
FILE_COLLECTD = 'collectd'
FILE_PROCESSED = FILE_COLLECTD

#######################
# Transformation rules
#######################
MEASURE_CPU_ORDER = ['timestamp', '%steal', '%user', '%idle', 'interval', '%iowait', '%system', '%nice', '# hostname',
                     'CPU']
MEASURE_MEMORY_ORDER = ['kbactive', '%memused', '%commit', 'kbmemfree', 'timestamp', 'kbdirty', 'interval', 'kbinact',
                        'kbmemused', 'kbcommit', 'kbbuffers', '# hostname', 'kbcached']
MEASURE_DISK_ORDER = ['timestamp', 'interval', 'bwrtn/s', 'tps', 'rtps', 'bread/s', '# hostname', 'wtps']
MEASURE_NETWORK_ORDER = ['txkB/s', 'IFACE', '%ifutil', 'timestamp', 'interval', 'rxmcst/s', 'rxkB/s', 'rxpck/s',
                         'txcmp/s', '# hostname', 'txpck/s', 'rxcmp/s']

###########################
# Headers transformation
# FORMAT_TIMESTAMP = u'%Y-%m-%d %H:%M:%S UTC'   # First version. Currently UTC is removed from SUT scripts
FORMAT_TIMESTAMP = u'%Y-%m-%d %H:%M:%S'
NEW_HEADERS = {"# hostname": "host"}


#  NEW_HEADERS = {"# hostname ": "host", "CPU": "Microprocessor"}


def __usage():
    """
    usage message
    """
    msg_lines = [
        " *****************************************************************************************************",
        " * This script execute all .feature files in a given directory and its subdirectories.               *",
        " *  usage:                                                                                           *",
        " *    python MachineMeasuresRetrieval.py [-s start_time] [-e end_time] -path [dest_path]             *",
        " *                                       [-a hosts_addrs] [-u usernames]                             *",
        " *                                                                                                   *",
        " *  parameters:                                                                                      *",
        " *     -s: start_time                  [optional].                                                   *",
        " *     -e: end_time                    [optional].                                                   *",
        " *     -path: dest_path                [mandatory].                                                  *",
        " *     -a: address for remote hosts    [optional].                                                   *",
        " *     -u: usernames for remote hosts  [optional].                                                   *",
        " *                                                                                                   *",
        " *  example:                                                                                         *",
        " *    python MachineMeasuresRetrieval.py -s 10:00:00 -e 12:00:00                                     *",
        " *                                                                                                   *",
        " * Note:                                                                                             *",
        " *       SUT time can be different to local machine                                                  *",
        " *                                                                                                   *",
        " *****************************************************************************************************"
    ]

    for n in msg_lines:
        print n
    exit(0)


str_range_time = "-s {start_time} -e {end_time}"

str_command_cpu = "sadf {range_time} -d -P ALL > {output_file}"
str_command_disk = "sadf {range_time} -d -- -b > {output_file}"
str_command_memory = "sadf {range_time} -d -- -r > {output_file}"
str_command_network = "sadf {range_time} -d -- -n DEV > {output_file}"
str_command_comma = "sed -i 's/\;/\,/g' {output_file}"
str_command_no_utc = "sed -i 's/ UTC//g' {output_file}"

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# deprecated
def command_measure_sh(type_measure):
    """
    Build remote command: e.g. [remote_path][remote_script] [parameter]
    :param type_measure:
    :return: command string
    """
    # ".//metricas_perf//gen_cpu_measures.sh /tmp/cpu_measures.csv"
    str_command = "{script_path} {remote_path} {start_time} {end_time}".format(
        script_path=config['MeasurePaths']['measure_command'],
        remote_path=config['MeasurePaths']['remote_path'],
        start_time=args.start_time,
        end_time=args.end_time)

    return str_command.format(type_measure=type_measure)


def command_csv_with_comma(type_measure):
    str_command = str_command_comma.format(output_file=config['MeasurePaths']['remote_path'])
    return str_command.format(type_measure=type_measure)


def command_csv_no_utc(type_measure):
    str_command = str_command_no_utc.format(output_file=config['MeasurePaths']['remote_path'])
    return str_command.format(type_measure=type_measure)


def command_measure(type_measure):
    """
    Build remote command: e.g. [remote_path][remote_script] [parameter]
    :param type_measure:
    :return: command string
    """
    range_time = ""
    output_file = ""
    if args.start_time is not None:
        range_time = str_range_time.format(start_time=args.start_time, end_time=args.end_time)
    if type_measure == MEASURE_CPU:
        str_command = str_command_cpu.format(range_time=range_time, output_file=config['MeasurePaths']['remote_path'])
    elif type_measure == MEASURE_DISK:
        str_command = str_command_disk.format(range_time=range_time, output_file=config['MeasurePaths']['remote_path'])
    elif type_measure == MEASURE_MEMORY:
        str_command = str_command_memory.format(range_time=range_time,
                                                output_file=config['MeasurePaths']['remote_path'])
    elif type_measure == MEASURE_NETWORK:
        str_command = str_command_network.format(range_time=range_time,
                                                 output_file=config['MeasurePaths']['remote_path'])

    return str_command.format(type_measure=type_measure)


# Compatibility python 3 (in backup, by the fly :-))
def _read_file(file_path, encoding='utf-8'):
    io_obj = BytesIO()
    get(file_path, io_obj)
    return io_obj.getvalue().decode(encoding)


def read_remote_file(remote_path):
    """
    Read one file from remote machine
    :param remote_path: file remote path
    :return: file content
    """
    fd = StringIO()
    get(remote_path, fd)
    content = fd.getvalue()
    fd.close()
    return content

def get_local_file(type_measure):
    """
    Get CSV local file
    :param type_measure: measure type recovered
    :return: file content
    """
    local_path = "{remote_path}".format(remote_path=config['MeasurePaths']['remote_path'])
    with open(local_path.format(type_measure=type_measure), 'r') as file:
        file_content = file.read()
    return file_content

def write_file_in_local(content_file, path):
    file = open(path, 'w')
    file.write(content_file)
    file.close()

def get_remote_file(type_measure):
    """
    Get CSV remote file
    :param type_measure: measure type recovered
    :return: file content
    """
    remote_path = "{remote_path}".format(remote_path=config['MeasurePaths']['remote_path'])
    file_content = read_remote_file(remote_path.format(type_measure=type_measure))
    return file_content


def write_local_type_file(type_measure, content_file, dir_machine, type_file=FILE_RAW):
    """
    Write CSV file in local machine depending of the type of measure and the file
    :param type_measure: measure type MEASURE_CPU_ORDER, MEASURE_DISK_ORDER, MEASURE_MEMORY_ORDER, MEASURE_NETWORK_ORDER
    :param content_file: file content
    :param dir_machine: IP of the host
    :param type_file: FILE_RAW directly from SADF or FILE_COLLECTD processed file
    """

    if type_file == FILE_COLLECTD:
        local_path = config['MeasurePaths']['local_collectd_path']
        name_file = local_path.format(path_of_execution=args.path_of_execution + "/machine_measures",
                                      type_measure=type_measure, dir_machine=dir_machine)
    else:
        raise Exception("Writing type file: {} unknown".format(type_file))

    write_local_file(name_file, content_file)


def write_local_file(name_file, content_file):
    """ Write file in local machine """
    __logger__.debug("Writting measures in local file {}".format(name_file))
    fd = open(name_file, 'w')
    fd.write(content_file)
    fd.close()


# Index of columns-csv files
# cpu_columns = {'%steal': 8, '%user': 4, 'timestamp': 2, '%idle': 9, 'interval': 1, '%iowait': 7, '%system': 6,
#                '%nice': 5, '# hostname': 0, 'CPU': 3}
# disk_columns = {'timestamp': 2, 'interval': 1, 'bwrtn/s': 7, 'tps': 3, 'rtps': 4, 'bread/s': 6, '# hostname': 0,
#                 'wtps': 5}
# memory_colummns = {'kbactive': 10, '%memused': 5, '%commit': 9, 'kbmemfree': 3, 'timestamp': 2, 'kbdirty': 12,
#                    'interval': 1, 'kbinact': 11, 'kbmemused': 4, 'kbcommit': 8, 'kbbuffers': 6, '# hostname': 0,
#                    'kbcached': 7}
# network_colummns = {'txkB/s': 7, 'IFACE': 3, '%ifutil': 11, 'timestamp': 2, 'interval': 1, 'rxmcst/s': 10,
#                     'rxkB/s': 6, 'rxpck/s': 4, 'txcmp/s': 9, '# hostname': 0, 'txpck/s': 5, 'rxcmp/s': 8}


def default_sorted_file(measure_matrix, type_measure):
    file_sort = ""
    len_row = len(measure_matrix[0])
    for row in measure_matrix:
        n = 0
        for i in row:
            file_sort += i
            if n != len_row - 1:
                file_sort += ","
            n += 1
        file_sort += "\n"
    return file_sort


def build_measure_row(row, dict_columns, expected_order):
    """
    Build the row of the measures (writepoints in influxdb argot). Read the original columns and change the order in
    function of expected order
    :param row: measure row from sadf command
    :param dict_columns: columns dictionary form original measure files
    :param expected_order: new order for output measures
    :return:
    """
    size_line = len(expected_order) - 1  # Special treatment for last element (skipped empty last line)
    build_line = ""
    for i in range(size_line):
        str_index = dict_columns[expected_order[i]]
        build_line = build_line + row[str_index] + ','
    str_index = dict_columns[expected_order[size_line]]
    build_line = build_line + row[dict_columns[expected_order[size_line]]] + "\n"
    return build_line


def normalize_headers(header_line, measure_dict):
    header_list = header_line.split(',')
    header_list[len(header_list) - 1] = header_list[len(header_list) - 1].rstrip('\n')
    new_headers = []

    i = 0
    for header in header_list:
        found = False
        for key, value in NEW_HEADERS.items():
            if key == header:
                new_headers.append(value)
                found = True
        if not found:
            new_headers.append(header)

    new_header_line = ""
    for i in range(len(new_headers) - 1):
        new_header_line = new_header_line + new_headers[i] + ','
    new_header_line = new_header_line + new_headers[len(new_headers) - 1] + '\n'
    return new_header_line


def sorted_file(measure_matrix, expected_order, dict_columns):
    """
    Build the new measure content sorted by the new expected order
    :param measure_matrix: original measures content
    :param expected_order: list with the new colmns expected order
    :param dict_columns: original columns dictionary from original file
    :return: measure content with the new order
    """
    file_sort = ""
    first_row = True
    for row in measure_matrix:
        file_sort = file_sort + build_measure_row(row, dict_columns, expected_order)
        if first_row:
            file_sort = normalize_headers(file_sort, dict_columns)
            first_row = False
    return file_sort


def adjust_measure_matrix(raw_file):
    """
    Transform the measure content to measure matrix and the headers as dictionary
    :param raw_file: Content from the remote measure file
    :return: measure matrix [][] and dictionary with the names of the columns
    """
    # Adjusting matrix of values
    measure_matrix = []
    splitted_line = raw_file.split('\n')
    n_lines = len(splitted_line)
    for n in range(n_lines - 1):
        measure_matrix.append([measure for measure in splitted_line[n].split(',')])

    measure_dict = {}
    i = 0
    for column_header in measure_matrix[0]:
        measure_dict[column_header] = i
        i += 1
    return measure_matrix, measure_dict


def convert_column_timestamp(measure_matrix, measure_dict):
    """
    Convert the timestamp format according
    :param measure_matrix:
    :param measure_dict:
    :return:
    """
    for line in measure_matrix:
        line[measure_dict["timestamp"]] = convert_timestamp(line[measure_dict["timestamp"]])
    return measure_matrix


def normalize_sadf_content(raw_file, type_measure):
    """
    Normalize raw content (from sadf command) and new format to write in influxdb db
    :param raw_file: content raw from sadf
    :param type_measure:
    :return: processed content
    """
    measure_matrix, measure_dict = adjust_measure_matrix(raw_file)

    for key, value in measure_dict.items():
        print key, ":", value
    ### Beacon
    # for line in measure_matrix:
    #    print line[dict_columns["timestamp"]]

    if type_measure == MEASURE_CPU:
        # Now, I don't want modify the timestamp format (csv2influx handle directly the current format)
        # measure_matrix = convert_column_timestamp(measure_matrix, measure_dict)
        content_sorted = sorted_file(measure_matrix, MEASURE_CPU_ORDER, measure_dict)
    elif type_measure == MEASURE_DISK:
        content_sorted = sorted_file(measure_matrix, MEASURE_DISK_ORDER, measure_dict)
    elif type_measure == MEASURE_MEMORY:
        content_sorted = sorted_file(measure_matrix, MEASURE_MEMORY_ORDER, measure_dict)
    elif type_measure == MEASURE_NETWORK:
        content_sorted = sorted_file(measure_matrix, MEASURE_NETWORK_ORDER, measure_dict)
    else:
        raise "Measure type file: {} unknown".format(type_measure)

    return content_sorted


# Example timestamp formats
# Input timestamp   : 2018-11-14 00:05:01 UTC
# Output timestamp  : 1542159901.0
# Collectd timestamp: 1540889097475700375
def convert_timestamp(str_timestamp):
    """
    Convert timestamp according to FORMAT_TIMESTAMP string format
    :param str_timestamp: Timestamp from sadf command
    :return: timestamp as integer format
    """
    if str_timestamp == "timestamp":
        return str_timestamp
    date_object = datetime.strptime(str_timestamp, FORMAT_TIMESTAMP)
    adapted_timestamp = time.mktime(date_object.timetuple())
    # print adapted_timestamp
    return str(adapted_timestamp)


def measures_complete_process(type_measure, dir_machine, is_SUT=True):
    """
    Process of the capture measures. Execute remote scripts (isolate sar-sadf), get the measure remote file and
    normalize the output format
    :param type_measure:
    :return:
    """
    # execute sadf if it's a remote SUT
    if is_SUT:
        o_code = fabric_connection.execute_command(command_measure(type_measure))
        o_code = fabric_connection.execute_command(command_csv_with_comma(type_measure))
        o_code = fabric_connection.execute_command(command_csv_no_utc(type_measure))

        # get remote file
        content_file = get_remote_file(type_measure)

        # filter file
        normalize_content = normalize_sadf_content(content_file, type_measure)
        # save file (raw and processed)
        # write_local_type_file(type_measure, content_file, dir_machine, FILE_RAW)
        write_local_type_file(type_measure, normalize_content, dir_machine, FILE_PROCESSED)

     # execute sadf if it's the local injector, and no remote connection is needed
    else:
        subprocess.call(command_measure(type_measure), shell=True, stderr=subprocess.STDOUT)
        subprocess.call(command_csv_with_comma(type_measure), shell=True, stderr=subprocess.STDOUT)
        subprocess.call(command_csv_no_utc(type_measure), shell=True, stderr=subprocess.STDOUT)

        # get local file
        content_file = get_local_file(type_measure)

        # filter file
        normalize_content = normalize_sadf_content(content_file, type_measure)
        local_path = config['MeasurePaths']['local_collectd_path']
        write_file_in_local(normalize_content, local_path.format(path_of_execution=args.path_of_execution + "/machine_measures",
                                      type_measure=type_measure, dir_machine=dir_machine))



def parser_args(parser):
    parser.add_argument("-i", "--is_SUT", type=str2bool, dest="is_SUT",  default=True,
                        help="False if we want to extract measures from the injector. "
                             "True if we want to extract measures from the SUTs under user config")
    parser.add_argument("-s", "--start_time", dest="start_time", help="Start time")
    parser.add_argument("-e", "--end_time", dest="end_time", help="End time")
    parser.add_argument("-path", "--path_execution", dest="path_of_execution", help="Path to the execution")
    parser.add_argument("-a", "--addrs", dest="addrs", help="Remote hosts (with , as separator)")
    parser.add_argument("-u", "--usernames", dest="usernames", help="Usernames for remote hosts (with , as separator)")

    return parser


def update_command_parameter(param_machines, param_username):
    if args.addrs is not None:
        param_machines = args.addrs
    if args.usernames is not None:
        param_username = args.usernames
    return param_machines, param_username


if __name__ == '__main__':
    # Waiting to implement the params by command line
    __logger__ = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser_args(parser)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(['properties.ini', '{user_config_path}/properties.ini'
                .format(user_config_path=args.path_of_execution)])

    logging.basicConfig(filename='{user_config_path}/machine_measures.log'
                        .format(user_config_path=args.path_of_execution))

    logging.config.fileConfig("logging.ini")

    # exit(0)

    MEASURE_CPU = config['MeasurePattern']['measure_cpu']
    MEASURE_DISK = config['MeasurePattern']['measure_disk']
    MEASURE_MEMORY = config['MeasurePattern']['measure_memory']
    MEASURE_NETWORK = config['MeasurePattern']['measure_network']

    if args.is_SUT:

        param_machines = config['RemoteSUT']['host_name']
        user_name = config['RemoteSUT']['host_username']
        user_pass = config['RemoteSUT']['host_password']
        user_key = config['Credentials']['host_ssh_key']

        param_username = config['RemoteSUT']['host_username']

        param_machines, param_username = update_command_parameter(param_machines, param_username)

        username_machines = param_username.split(',')
        address_machines = param_machines.split(',')

        n_address = len(address_machines)

        for dir_machine, username_machine in zip(address_machines, username_machines):
            fabric_connection = FabricUtils(dir_machine, username_machine, user_pass, user_key)
            measures_complete_process(MEASURE_CPU, dir_machine)
            measures_complete_process(MEASURE_DISK, dir_machine)
            measures_complete_process(MEASURE_MEMORY, dir_machine)
            measures_complete_process(MEASURE_NETWORK, dir_machine)

    else:
        measures_complete_process(MEASURE_CPU, "injector", is_SUT=False)
        measures_complete_process(MEASURE_DISK, "injector", is_SUT=False)
        measures_complete_process(MEASURE_MEMORY, "injector", is_SUT=False)
        measures_complete_process(MEASURE_NETWORK, "injector", is_SUT=False)
