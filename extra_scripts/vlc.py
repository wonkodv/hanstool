"""Control VLC via its web interface"""


from Env import cmd, log, show, Path, execute_disconnected, PATH

import http.client
import pprint
import json
import fnmatch
import re
import random
import base64

PASSWORD = "Passwort123"
PASSWORD_b64=base64.b64encode((":"+PASSWORD).encode("ASCII")).decode("ASCII")


PATH.append(Path(r"C:\Program Files\VideoLAN\VLC"))

def request(s):
    c = http.client.HTTPConnection("localhost",63215)
    c.request("GET",s,headers={"Authorization":"Basic " + PASSWORD_b64})
    r = c.getresponse().read()
    c.close()
    return r

def playlist():
    result = []
    def walk(x):
        if 'name' in x:
            result.append((x['name'],x['id']))
        if 'children' in x:
            for c in x['children']:
                walk(c)

    b = request("/requests/playlist.json")
    s = b.decode("utf-8")
    l = json.loads(s)
    walk(l)
    return result

def find(search):
    l = playlist()
    r = "^.*"+".*".join(search.split())+".*$"
    r = re.compile(r, re.IGNORECASE)
    return [(name,id) for (name,id) in l if r.fullmatch(name)]

def play_id(id):
    request("/requests/status.json?command=pl_play&id="+id)

@cmd(name="play")
def play(search):

    ids = find(search)
    if(ids):
        for name, id in ids:
            log(name)
        play_id(id)

@cmd(name="status")
def status():
    b = request("/requests/status.json")
    s = b.decode("utf-8")
    o = json.loads(s)
    show(o['information']['category']['meta'])

def vlc(*args):
    return execute_disconnected("vlc","--http-host=localhost","--http-port=63215","--http-password=" + PASSWORD, *args)

@cmd
def music(s:Path=r"G:\list.m3u"):
    return vlc(s)
