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
    f = str(tmpdir.join('history'))
    monkeypatch.setattr(ht3.history,'get_history_file',lambda:pathlib.Path(f))
    monkeypatch.setattr(ht3.history,'Env',{'HISTORY_LIMIT':12})

    ht3.history.append_history("cmdA","CmdB")
    h = ht3.history.get_history()
    h = list(h)
    assert h[-1] == 'CmdB'
    ht3.history.append_history(*["cmd %d"%x for x in range(15)])
    h = ht3.history.get_history()
    h = list(h)
    assert len(h) == 12
    assert h[0] == 'cmd 3'
    assert h[-1] == 'cmd 14'
