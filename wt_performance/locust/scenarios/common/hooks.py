import csv
import logging
import os
import pathlib
import random

from datetime import datetime
from flask import send_file
from locust import events

logger = logging.getLogger(__name__)

path = pathlib.Path().absolute()
filename =  str(path) + "/" + "success_req_stats_" + ".csv"
HEADER_CSV = ["timeStamp","elapsed","label","responseCode","responseMessage","threadName","dataType","success",
              "failureMessage","bytes","sentBytes","grpThreads","allThreads","Latency","IdleTime","Connect"]
request_success_stats = [list()]
master_success_stats = [list()]
sampling  = os.environ["SAMPLING"]

@events.init.add_listener
def on_locust_init(web_ui, **kw):
    @web_ui.app.route("/qareporter_csv")
    def qa_reporter():
        return send_file(filename,
                         attachment_filename=filename,
                         mimetype='text/plain',
                         as_attachment=True)

@events.request_success.add_listener
def hook_request_success(request_type, name, response_time, response_length, **kw):
    if response_length == 0: # performance reporter do no support response_size to 0
        response_length = 1
    value = [int(datetime.now().timestamp() * 1000), int(response_time), request_type + " " + name,
        "200", "OK", "Threads", "text", "true", "", response_length, 0, 0, 0, 0, 0, 0]

    append_request_result(value)

@events.request_failure.add_listener
def hook_request_failure(request_type, name, response_time, response_length, **kw):
    if response_length == 0: # performance reporter do no support response_size to 0
        response_length = 1
    value = [int(datetime.now().timestamp() * 1000), int(response_time), request_type + " " + name,
        "600", "Generic error", "Threads", "text", "false", "", response_length, 0, 0, 0, 0, 0, 0]
    
    append_request_result(value)

def append_request_result(value):
    if sampling and int(sampling) > 0 and random.uniform(0, 1) > 1/int(sampling):
        value = None
    
    if value:
        request_success_stats.append(value)

@events.report_to_master.add_listener
def hook_report_to_master(client_id, data, **kw):
    global request_success_stats
    data["current_responses"] = request_success_stats
    request_success_stats = []

@events.worker_report.add_listener
def hook_slave_report(client_id, data, **kw):
    if "current_responses" in data:
        for value in data["current_responses"]:
            master_success_stats.append(value)
            with open(filename, 'a') as csv_file:
                writer = csv.writer(csv_file)
                for value in master_success_stats:
                    if value:
                        writer.writerow(value)
            csv_file.close()
            master_success_stats.clear()
            request_success_stats.clear()

@events.test_start.add_listener
def hook_start_hatching(**kw):
    if os.path.exists(filename):
        logger.debug("deleting file: %s", filename)
        os.remove(filename)
    with open(filename, 'w+') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(HEADER_CSV)

@events.test_stop.add_listener
def hook_stop_hatching(**kw):
    pass