import Env
from Env import cmd, show


@cmd
def mpd():
    execute_disconnected("mpd")


try:
    import musicpd
except ImportError:
    pass
else:

    def client():
        return (
            musicpd.MPDClient()
        )  # (host=Env.get('MPD_HOST'), port=Env.get('MPD_PORT'));

    @cmd
    def current_song():
        with client() as c:
            s = c.currentsong()
            show(f'{s["artist"]} - {s["album"]} - {s["title"]}')

    @cmd
    def play(typ: ["title", "artitst", "album"], query, *more_query):
        query = query + " " + " ".join(more_query)
        with client() as c:
            songs = c.playlistsearch(typ, query)
            if len(songs) > 1:
                id = songs[0]["id"]
            else:
                songs = c.search(typ, query)
                if len(songs) > 1:
                    id = c.addid(songs[0]["file"])
                else:
                    show("No such song {typ} {query}")
                    return "No such song {typ} {query}"
            c.playid(id)
