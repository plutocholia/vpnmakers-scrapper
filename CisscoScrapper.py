import requests
from lxml import html
import os
import re
import json


def get_server(payload):
    login_url = f"https://{payload['domain']}/login"
    servers_url = f"https://{payload['domain']}/servers?p=cisco"

    _session = requests.session()
    res = _session.get(login_url)

    tree = html.fromstring(res.text)
    _token = list(
        set(tree.xpath("//input[@name='_token']/@value")))[0]
    payload['_token'] = _token

    res = _session.post(
        login_url, data=payload, headers=dict(refer=login_url)
    )
    res = _session.get(servers_url)

    inplace = True
    tree = html.fromstring(res.text)
    _server = list(
        set(
            tree.xpath('//*[(@id = "server_us")]/text()')
        )
    )[0]

    print(f"new address : {_server}")
    return _server


def change_zshrc(_server):

    filedata = None
    with open(os.path.expanduser('~') + "/.zshrc", 'r') as file:
        filedata = file.read()

    new_file_data = []
    for line in filedata.split("\n"):
        res = re.findall(r'(export SERVER_PATH)="(.*)"', line)
        if len(res):
            print(
                f"found in rc with address of {res[0][1]}\nchanged to {_server}")
            line = line.replace(res[0][1], _server)
        new_file_data.append(line)

    data = "\n".join((item for item in new_file_data))

    with open(os.path.expanduser('~') + "/.zshrc", 'w') as file:
        file.write(data)


if __name__ == '__main__':
    with open("setting.json") as f:
        data = json.load(f)
    payload = {
        "username": data['username'],
        "password": data['password'],
        "domain": data['domain'],
        "_token": ""
    }
    server = get_server(payload)
    if data['zshrc']:
        change_zshrc(server)
