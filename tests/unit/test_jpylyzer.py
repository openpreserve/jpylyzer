# pylint: disable=missing-docstring
import pytest

from jpylyzer.jpylyzer import __version__, checkNullArgs, checkNoInput, \
                              printHelpAndExit, EXISTING_FILES, getFiles
import jpylyzer.config as config

def test_version():
    assert __version__

def test_check_empty_args():
    # https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
    with pytest.raises(SystemExit) as pytest_wrapped_excep:
        checkNullArgs([])
    assert pytest_wrapped_excep.type == SystemExit
    assert pytest_wrapped_excep.value.code == config.ERR_CODE_NO_IMAGES

def test_check_null_args():
    with pytest.raises(SystemExit) as pytest_wrapped_excep:
        checkNullArgs(None)
    assert pytest_wrapped_excep.type == SystemExit
    assert pytest_wrapped_excep.value.code == config.ERR_CODE_NO_IMAGES

def test_check_not_null_args():
    checkNullArgs(["arg"])

def test_empty_input_files():
    with pytest.raises(SystemExit) as pytest_wrapped_excep:
        checkNoInput([])
    assert pytest_wrapped_excep.type == SystemExit
    assert pytest_wrapped_excep.value.code == config.ERR_CODE_NO_IMAGES

def test_null_input_files():
    with pytest.raises(SystemExit) as pytest_wrapped_excep:
        checkNoInput(None)
    assert pytest_wrapped_excep.type == SystemExit
    assert pytest_wrapped_excep.value.code == config.ERR_CODE_NO_IMAGES

def test_input_files():
    checkNullArgs(["file"])

def test_print_help():
    with pytest.raises(SystemExit) as pytest_wrapped_excep:
        printHelpAndExit()
    assert pytest_wrapped_excep.type == SystemExit
    assert pytest_wrapped_excep.value.code is None

def test_get_files():
    assert not EXISTING_FILES
    getFiles('./*')
    assert EXISTING_FILES
    EXISTING_FILES.clear()
    assert not EXISTING_FILES
