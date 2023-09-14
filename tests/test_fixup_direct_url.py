import subprocess

from pip_deepfreeze.pip import pip_fixup_vcs_direct_urls, pip_freeze


def test_fixup_vcs_direct_url_branch_fake_commit(virtualenv_python: str) -> None:
    """When installing from a git branch, the commit_id in direct_url.json is replaced
    with a fake one.
    """
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "git+https://github.com/PyPA/pip-test-package",
        ]
    )
    frozen = "\n".join(pip_freeze(virtualenv_python))
    assert "git+https://github.com/PyPA/pip-test-package" in frozen
    # fake commit NOT in direct_url.json
    assert f"git+https://github.com/PyPA/pip-test-package@{'f'*40}" not in frozen
    pip_fixup_vcs_direct_urls(virtualenv_python)
    frozen = "\n".join(pip_freeze(virtualenv_python))
    # fake commit in direct_url.json
    assert f"git+https://github.com/PyPA/pip-test-package@{'f'*40}" in frozen


def test_fixup_vcs_direct_url_commit(virtualenv_python: str) -> None:
    """When installing from a git commit, the commit_id in direct_url.json is left
    untouched.
    """
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "git+https://github.com/PyPA/pip-test-package"
            "@5547fa909e83df8bd743d3978d6667497983a4b7",
        ]
    )
    frozen = "\n".join(pip_freeze(virtualenv_python))
    assert (
        "git+https://github.com/PyPA/pip-test-package"
        "@5547fa909e83df8bd743d3978d6667497983a4b7" in frozen
    )
    pip_fixup_vcs_direct_urls(virtualenv_python)
    frozen = "\n".join(pip_freeze(virtualenv_python))
    assert (
        "git+https://github.com/PyPA/pip-test-package"
        "@5547fa909e83df8bd743d3978d6667497983a4b7" in frozen
    )
