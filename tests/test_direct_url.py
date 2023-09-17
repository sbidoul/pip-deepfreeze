from pip_deepfreeze.installed_dist import DirectUrl


def test_as_pip_requirement():
    data = {
        "url": "https://github.com/pypa/pip-test-package",
        "vcs_info": {"vcs": "git", "commit_id": "1234567890abcdef"},
    }
    direct_url = DirectUrl(data)
    expected_output = "git+https://github.com/pypa/pip-test-package@1234567890abcdef"
    assert direct_url.as_pip_requirement() == expected_output


def test_as_pip_requirement_with_name():
    data = {
        "url": "https://github.com/pypa/pip-test-package",
        "subdirectory": "src",
        "vcs_info": {"vcs": "git", "commit_id": "1234567890abcdef"},
    }
    direct_url = DirectUrl(data)
    expected_output = (
        "pip-test-package @ git+https://github.com/pypa/pip-test-package"
        "@1234567890abcdef"
        "#subdirectory=src"
    )
    assert direct_url.as_pip_requirement("pip-test-package") == expected_output


def test_is_editable():
    data = {
        "url": "file:///home/project/pip-test-package",
        "subdirectory": "src",
        "dir_info": {"editable": True},
    }
    direct_url = DirectUrl(data)
    assert direct_url.is_editable
