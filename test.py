import requests

url = "http://47.94.87.127/"
data = {
    "input": "七里香",
    "filter": "name",
    "type": "netease",
    "page": 1
}
response = requests.post(url, data=data)
print(response.text)
