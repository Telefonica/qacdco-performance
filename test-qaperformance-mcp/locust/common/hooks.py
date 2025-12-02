"""
a listener to provide results from locust tests in a JMeter compatible format
and thereby allow JMeter users with existing reporting solutions to transition more easily
"""

import os
import random
from datetime import datetime
from time import time

from locust.runners import WorkerRunner


class JmeterListener:
    """
    create an intance of the listener at the start of a test
    to create a JMeter style results file
    different formats can be chosen in initialisation
    (field_delimiter row_delimiter and timestamp_format)
    and the number of results to send to a log file at a time (flush_size)
    """

    # holds results until processed
    csv_results = []

    def __init__(
        self,
        env,
        testplan="testplanname",
        field_delimiter=",",
        row_delimiter="\n",
        timestamp_format="%Y-%m-%d %H:%M:%S",
    ):
        self.env = env
        self.runner = self.env.runner
        self.is_worker_runner = isinstance(self.env.runner, WorkerRunner)

        self.testplan = testplan
        # default JMeter field and row delimiters
        self.field_delimiter = field_delimiter
        self.row_delimiter = row_delimiter
        # a timestamp format, others could be added...
        self.timestamp_format = timestamp_format

        # fields set by default in jmeter
        self.csv_headers = [
            "timeStamp",
            "elapsed",
            "label",
            "responseCode",
            "responseMessage",
            "threadName",
            "dataType",
            "success",
            "failureMessage",
            "bytes",
            "sentBytes",
            "grpThreads",
            "allThreads",
            "Latency",
            "IdleTime",
            "Connect",
        ]

        self.user_count = 0
        self.testplan = ""
        events = self.env.events
        if self.is_worker_runner:
            events.report_to_master.add_listener(self._report_to_master)
        else:
            events.worker_report.add_listener(self._worker_report)

        events.request.add_listener(self._request)

        if self.env.web_ui:
            @self.env.web_ui.app.route("/worker_number")
            def worker_number():
                return str(self.runner.worker_index_max)

            @self.env.web_ui.app.route("/csv_results.csv")
            def csv_results_page():  # pylint: disable=unused-variable
                """
                a different way of obtaining results rather than writing to disk
                to use it getting all results back, set the flush_size to
                a high enough value that it will not flush during your test
                """
                response = self.env.web_ui.app.response_class(
                    response=self.field_delimiter.join(self.csv_headers)
                    + self.row_delimiter
                    + self.row_delimiter.join(self.csv_results),
                    status=200,
                    mimetype="text/csv",
                )
                return response
            @self.env.web_ui.app.route("/clear_results")
            def clear_results():
                self.csv_results = []
                return "csv results clean"

    def add_result(self, success, _request_type, name, response_time, response_length, exception, **kw):
        timestamp = str (round(datetime.now().timestamp() * 1000))
        response_message = "OK" if success == "true" else "KO"
        # check to see if the additional fields have been populated. If not, set to a default value
        status_code = kw["status_code"] if "status_code" in kw else "0"
        thread_name = self.testplan
        data_type = kw["data_type"] if "data_type" in kw else "unknown"
        bytes_sent = kw["bytes_sent"] if "bytes_sent" in kw else "0"
        group_threads = str(self.runner.user_count)
        all_threads = str(self.runner.user_count)
        latency = kw["latency"] if "latency" in kw else "0"
        idle_time = kw["idle_time"] if "idle_time" in kw else "0"
        connect = kw["connect"] if "connect" in kw else "0"
        exception = kw["exception"] if "exception" in kw else ""
        exception = exception.replace(",", "")

        row = [
            timestamp,
            str(round(response_time)),
            name,
            str(status_code),
            response_message,
            thread_name,
            data_type,
            success,
            exception,
            str(response_length),
            bytes_sent,
            str(group_threads),
            str(all_threads),
            latency,
            idle_time,
            connect,
        ]
        self.csv_results.append(self.field_delimiter.join(row))

    def _request(self, request_type, name, response_time, response_length, exception, **kw):
        self.add_result(
            "false" if exception else "true", request_type, name, response_time, response_length, str(exception), **kw
        )

    def _report_to_master(self, data, **kwargs): 
       data["csv_results"] = self.csv_results
       self.csv_results = []

    def _worker_report(self, data, **kwargs):
        self.csv_results += data["csv_results"]
