from locust import HttpUser, task
import re
from api.project_api import *
from common.utils import *
from common.hooks import *

environment="xxx.com"

class ProjectFeature (HttpUser):
    @task(1)
    def test_case_1 (self):
        request = RequestXxx(environment)
        logger.debug(f"Url to XXX: {request.url} and headers {request.headers}")
        response = self.client.get(name = request.name,
                                    url = request.url,
                                    headers = request.headers)
        logger.debug(f"Response content for XXX: {response.content}")


        token_id = re.findall("token\":\"([^\"]+)",response.text)[0]
        

        request = RequestYyy(token_id, environment)
        logger.debug(f"Url to YYY: {request.url} and headers {request.headers}")
        response = self.client.post(name = request.name,    
                                     url = request.url,
                                     headers = request.headers)
        logger.debug(f"Response content for YYY: {response.content}")
        
    
#        conversation_id = re.findall("conversationId\": \"([^\"]+)",response.text)[0] ## regular expression to get conversationId