import requests

URL = "https://jh9d4gng3e.execute-api.ap-southeast-1.amazonaws.com/prod"


def test_api():
    page_size = 12
    response = requests.get(
        f"{URL}/api/v1/movies/?page_size={page_size}").json()
    assert len(response['results']) == page_size

# sudo lsof -t -i tcp:5050 | sudo xargs kill
