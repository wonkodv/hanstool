"""Control VLC via its http json interface

Documented in http://localhost:63215/requests/README.txt"""


import base64
import fnmatch
import http.client
import json
import pprint
import random
import re

from Env import PATH, Path, cmd, execute_disconnected, log, set_clipboard, show

PASSWORD = "Passwort123"
PASSWORD_b64 = base64.b64encode((":" + PASSWORD).encode("ASCII")).decode("ASCII")


def request(s):
    c = http.client.HTTPConnection("localhost", 63215)
    c.request("GET", s, headers={"Authorization": "Basic " + PASSWORD_b64})
    r = c.getresponse().read()
    c.close()
    return r


def playlist():
    result = []

    def walk(x):
        if "name" in x:
            result.append((x["name"], x["id"]))
        if "children" in x:
            for c in x["children"]:
                walk(c)

    b = request("/requests/playlist.json")
    s = b.decode("utf-8")
    l = json.loads(s)
    walk(l)
    return result


def find(search):
    l = playlist()
    r = "^.*" + ".*".join(search.split()) + ".*$"
    r = re.compile(r, re.IGNORECASE)
    return [(name, id) for (name, id) in l if r.fullmatch(name)]


def play_id(id):
    request("/requests/status.json?command=pl_play&id=" + id)


@cmd
def play(search):

    ids = find(search)
    if ids:
        for name, id in ids:
            log(name)
        play_id(id)


@cmd
def current_song():
    b = request("/requests/status.json")
    s = b.decode("utf-8")
    o = json.loads(s)
    s = "{artist} - {album}.{track_number} - {title}".format(
        **o["information"]["category"]["meta"]
    )
    set_clipboard(s)
    show(s)


@cmd
def status():
    b = request("/requests/status.json")
    s = b.decode("utf-8")
    o = json.loads(s)
    m = o["information"]["category"]["meta"]
    show(m)
    set_clipboard("{artist} - {title}".format(**m))


def vlc(*args):
    return execute_disconnected(
        "vlc",
        "--http-host=localhost",
        "--http-port=63215",
        "--http-password=" + PASSWORD,
        *args
    )


@cmd
def music(s: Path = None):
    if not s:
        for c in "GHIJKL":
            try:
                p = Path(c + ":/list.m3u")
                if p.is_file():
                    s = p
                    break
            except OSError:
                pass
        else:
            raise FileNotFoundError("*:/list.m3u nicht gefunden")
    return vlc(str(s))
