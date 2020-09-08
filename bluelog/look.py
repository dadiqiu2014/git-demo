import os
import requests
from werkzeug.serving import run_simple
from flask import Flask
import time

for i in range(100000):
    time.sleep(0.1)
    requests.get('http://0.0.0.0:9999/blog/')