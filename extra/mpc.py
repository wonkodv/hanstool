from Env import cmd, show, execute_disconnected


def client():
    import musicpd

    return musicpd.MPDClient()
    # (host=Env.get('MPD_HOST'), port=Env.get('MPD_PORT'));


@cmd
def current_song():
    with client() as c:
        s = c.currentsong()
        show(f'{s["artist"]} - {s["album"]} - {s["title"]}')


@cmd
def play(query):
    c = client()
    c.connect()
    try:
        for typ in ["title", "artist", "album"]:
            songs = c.playlistsearch(typ, query)
            if len(songs) > 1:
                id = songs[0]["id"]
                break
        else:
            for typ in ["title", "artist", "album"]:
                songs = c.search(typ, query)
                if len(songs) > 1:
                    id = c.addid(songs[0]["file"])
                    break
            else:
                show(f"No such title, artist or album {query!r}")
                return f"No such title, artist or album {query!r}"
        c.playid(id)
    finally:
        c.disconnect()
