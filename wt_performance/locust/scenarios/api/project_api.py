
import json

class RequestXxx:
    def __init__(self, environment):
        self.name = "XXX"
        self.url = "https://" + environment + "/endpoint"
        self.headers = {
                        "Authorization": "token_id",
                        #"Content-Type": "application/x-www-form-urlencoded"
                }

class RequestYyy:
    def __init__(self, token_id, directline):
        self.name = "YYY"
        self.url = "https://" + directline + "/endpoint"
        self.headers = {
                    "Authorization": "Bearer " + token_id + "",
                }
