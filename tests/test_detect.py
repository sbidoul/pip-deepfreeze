from pip_deepfreeze.detect import supports_editable


def test_supports_editable(tmp_path):
    assert not supports_editable(tmp_path)
    (tmp_path / "setup.py").touch()
    assert supports_editable(tmp_path)
