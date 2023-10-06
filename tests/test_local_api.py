import os
import time
import subprocess
import requests

subprocess.Popen(['sh', "./boot.sh"])

time.sleep(10)

port = os.getenv("PORT", "5050")


def test_api():
    page_size = 12
    response = requests.get(
        f"http://0.0.0.0:{port}/api/v1/movies/?page_size={page_size}").json()
    assert len(response['results']) == page_size

# sudo lsof -t -i tcp:5050 | sudo xargs kill
