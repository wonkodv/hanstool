"""Control VLC via its web interface"""


from Env import cmd, log, show

import http.client
import pprint
import json
import fnmatch
import re

def vlc(*args):
    execute_disconnected("vlc","--http","--http-password=HansHans",*args) #TODO

def request(s):
    c = http.client.HTTPConnection("localhost",8080)
    c.request("GET",s,headers={"Authorization":"Basic OlBXbmFSZFZJNDI2Nw=="})
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
    #return [id for (name, id) in l if name == search or fnmatch.fnmatch("*"+search+"*", name)]
    r = "^.*"+".*".join(search.split())+".*$"
    r = re.compile(r, re.IGNORECASE)
    return [(name,id) for (name,id) in l if r.fullmatch(name)]

def play_id(id):
    request("/requests/status.json?command=pl_play&id="+id)

@cmd(name="vlcplay")
def play(search):

    ids = find(search)
    if(ids):
        for name, id in ids:
            log(name)
        play_id(id)

@cmd(name="vlcstatus")
def status():
    b = request("/requests/status.json")
    s = b.decode("utf-8")
    o = json.loads(s)
    show(o['information']['category']['meta'])
