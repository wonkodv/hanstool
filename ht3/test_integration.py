import pkg_resources
import ht3.history
import pathlib


def test_integration(monkeypatch, tmpdir):
    from ht3.scripts import load_scripts, add_scripts
    from ht3.command import run_command

    f = str(tmpdir.join("history"))
    monkeypatch.setattr(ht3.history, "get_history_file", lambda: pathlib.Path(f))

    add_scripts(pkg_resources.resource_filename(__name__, "test_scripts"))
    load_scripts()
    result = run_command("test Yes")
    assert result == "Integration Tests ran"
