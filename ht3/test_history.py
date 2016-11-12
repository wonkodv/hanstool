from ht3.env import Env
import ht3.history
import pathlib
import os.path

def test_lazy_file_path(monkeypatch, tmpdir):
    f = str(ht3.history.get_history_file())
    p = str(os.path.expanduser(Env.get('HISTORY', ht3.history.HISTORY_FILE_DEFAULT)))

    assert f == p

    f2 = str(tmpdir.join('history2'))
    monkeypatch.setattr(ht3.history,'Env',{'HISTORY':f2})

    hf = str(ht3.history.get_history_file())
    assert hf == f
    assert hf != f2


def test_append_with_limit(monkeypatch, tmpdir):
    """History should enforce the limit when loading."""
    f = str(tmpdir.join('history'))
    p = pathlib.Path(f)

    monkeypatch.setattr(ht3.history,'get_history_file',lambda:p)
    monkeypatch.setattr(ht3.history,'Env',{'HISTORY_LIMIT':2})

    h = ht3.history.get_history()
    assert len(h) == 0

    ht3.history.append_history("cmd1","Cmd2","Cmd3")
    h = ht3.history.get_history()
    assert len(h) == 3

    ht3.history.append_history("cmdA","CmdB")
    h = ht3.history.get_history()
    assert len(h) == 5
    assert h[-1] == 'CmdB'

    ht3.history.load_history()

    h = ht3.history.get_history()
    assert len(h) == 2
    assert h[-1] == 'CmdB'
