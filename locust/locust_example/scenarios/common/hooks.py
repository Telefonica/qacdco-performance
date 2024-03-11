"""
a listener to provide results from locust tests in a JMeter compatible format
and thereby allow JMeter users with existing reporting solutions to transition more easily
"""

from datetime import datetime
from pathlib import Path
from time import time
from locust.runners import WorkerRunner
import os
import random
import requests
from flask import Blueprint, request, jsonify, make_response, Flask, render_template

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
    sampling = os.getenv("SAMPLING")

    def __init__(
        self,
        env,
        testplan="testplanname",
        field_delimiter=",",
        row_delimiter="\n",
        timestamp_format="%Y-%m-%d %H:%M:%S",
        flush_size=400,
        results_filename=None,
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
        # how many records should be held before flushing to disk
        self.flush_size = flush_size
        if not results_filename:
            # results filename format
            self.results_filename = f"results_{datetime.fromtimestamp(time()).strftime('%Y_%m_%d_%H_%M_%S')}.csv"
        else:
            self.results_filename = results_filename

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
            self.results_file = self._create_results_log()
            events.quitting.add_listener(self._write_final_log)
            events.worker_report.add_listener(self._worker_report)

        events.request.add_listener(self._request)

        if self.env.web_ui:

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

    def _create_results_log(self):
        filename = Path(self.results_filename)
        filename.parent.mkdir(exist_ok=True, parents=True)
        filename.touch(exist_ok=True)
        results_file = open(filename, "w")
        results_file.write(self.field_delimiter.join(self.csv_headers) + self.row_delimiter)
        results_file.flush()
        return results_file

    def _flush_to_log(self):
        self.results_file.write(self.row_delimiter.join(self.csv_results) + self.row_delimiter)
        self.results_file.flush()
        self.csv_results = []

    def _write_final_log(self, **kwargs):
        self.results_file.write(self.row_delimiter.join(self.csv_results) + self.row_delimiter)
        self.results_file.close()

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
        if self.sampling and int(self.sampling) >  0 and random.uniform(0, 1) > 1/int(self.sampling):
          return
        self.csv_results.append(self.field_delimiter.join(row))
        if len(self.csv_results) >= self.flush_size and not self.is_worker_runner:
            self._flush_to_log()

    def _request(self, request_type, name, response_time, response_length, exception, **kw):
        self.add_result(
            "false" if exception else "true", request_type, name, response_time, response_length, str(exception), **kw
        )

    def _report_to_master(self, data, **kwargs):
        data["csv_results"] = self.csv_results
        self.csv_results = []

    def _worker_report(self, data, **kwargs):
        self.csv_results += data["csv_results"]
        if len(self.csv_results) >= self.flush_size:
            self._flush_to_log()
    def _clear_results(self):
        self.csv_results = []

def upload_to_reporter(app: Flask, jmeter_listener: JmeterListener):
    upload_blueprint = Blueprint('upload', __name__, template_folder='../templates')

    @upload_blueprint.route('/upload', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST':
            try:
                form_data = {
                    'project_name': request.form['PERFORMANCE_PROJECT_NAME'],
                    'module': request.form['MODULE'],
                    'execution_name': request.form['PERFORMANCE_EXECUTION_NAME'],
                    'release_version': request.form['RELEASE_VERSION'],
                    'reporter_url': request.form['QA_REPORTER_URL'],
                    'sampling': request.form.get('SAMPLING')
                }
                if not form_data['sampling']:
                    form_data['sampling'] = 1
                print(form_data['sampling'])
                results_csv = requests.get('http://localhost:8089/csv_results.csv')
                if results_csv.status_code == 200:
                    with open('results.csv', 'w') as file:
                        file.write(results_csv.text)
                else:
                    raise Exception("Failed to download results.csv")

                # Create a new execution
                project_response = requests.get(f'{form_data["reporter_url"]}/api/1.0/projects/?name={form_data["project_name"]}')
                project_response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
                project = project_response.json()
                project_id = project[0]['project_id']

                execution_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                execution_data = {
                    'project-id': project_id,
                    'module': form_data['module'],
                    'name': form_data['execution_name'],
                    'type': 'load',
                    'version': form_data['release_version'],
                    'date': execution_date
                }
                execution_response = requests.post(f'{form_data["reporter_url"]}/api/1.0/executions/', data=execution_data)
                execution_response.raise_for_status()
                execution = execution_response.json()
                execution_id = execution['execution']['execution_id']

                with open('results.csv', 'rb') as file:
                    files = {'data': file}
                    upload_response = requests.post(f'{form_data["reporter_url"]}/api/1.0/executions/{execution_id}/csv_loader/', data={'execution-id': execution_id, 'input-type': 'jmeter-csv', 'sampling': form_data['sampling']}, files=files)
                    upload_response.raise_for_status()

                os.remove('results.csv')
                jmeter_listener._clear_results()
                return "Execution submitted successfully."
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            return render_template('upload_form.html')

    app.register_blueprint(upload_blueprint)