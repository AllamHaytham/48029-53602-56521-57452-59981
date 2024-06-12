import os
import datetime
import csv

class User:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.registration_date = datetime.datetime.now()
        self.tasks = []
