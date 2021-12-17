from pathlib import Path

import ht3.history


def test_append_with_limit(monkeypatch, tmpdir):
    """History should enforce the limit when loading."""
    f = str(tmpdir.join("history"))
    p = Path(f)

    monkeypatch.setattr(ht3.history, "HISTORY", None)
    monkeypatch.setattr(ht3.history, "get_history_file", lambda: p)
    monkeypatch.setattr(ht3.history, "Env", {"HISTORY_LIMIT": 2})

    h = ht3.history.get_history()
    assert len(h) == 0

    ht3.history.append_history("cmd1", "Cmd2", "Cmd3")
    h = ht3.history.get_history()
    assert len(h) == 3

    ht3.history.append_history("cmdA", "CmdB")
    h = ht3.history.get_history()
    assert len(h) == 5
    assert h[-1] == "CmdB"

    ht3.history.load_history()

    h = ht3.history.get_history()
    assert len(h) == 2
    assert h[-1] == "CmdB"
