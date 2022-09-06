import csv
import os
import random


class testRequest:
    def __init__(self):
        self.url= f'/vacation.html'
        self.name = 'testRequest'
        self.headers = { 'Content-Type':'application/json', 'Test-Header':'Test-Value'}
