from locust import HttpUser, task, between, events, tag
from common.hooks import JmeterListener
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.path.pardir, 'apis'))
from apis import *

class QuickstartUser(HttpUser):
    @tag('testRequest')
    @task
    def testRequest(self):
        request = testRequest()
        self.client.get(url = request.url, headers = request.headers, name = request.name)

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    JmeterListener(env=environment, testplan="testPlan")
