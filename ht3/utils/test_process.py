import subprocess
import pytest
import sys
import os
from .process import execute, shellescape


def helper(*args,**kwargs):
    p = execute(
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        env=dict([('TEST','hans')] + list(os.environ.items())),
        **kwargs
    )
    return p

def test_excecute():
    p = helper(sys.executable, "-c", "print('$TEST')")
    t, e = p.communicate()
    assert t.strip() == '$TEST'

def test_excecute_split():
    p = helper(sys.executable, "-c", "print('$TEST')",is_split=True)
    t, e = p.communicate()
    assert t.strip() == '$TEST'

def test_excecute_shell():
    if sys.platform=='win32':
        pytest.skip("Meh") # TODO: make this test windows safe
    p = helper(shellescape(sys.executable) + " -c \"print('$TEST')\"", shell=True)
    t, e = p.communicate()
    assert t.strip() == '123'

def test_excecute_nosplit_err():
    with pytest.raises(TypeError):
        helper("a","b", is_split=False)

def test_excecute_shell_split():
    with pytest.raises(TypeError):
        helper("a","b", is_split=True, shell=True)

def test_excecute_shell_split2():
    with pytest.raises(TypeError):
        helper("a","b", shell=True)


