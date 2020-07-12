import subprocess

from pip_deepfreeze.list_depends import list_depends


def test_list_depends(virtualenv_python, testpkgs):
    # this is a basic test for the list_depends() function,
    # advanced dependencies tests are in test_list_depends_script.py
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            testpkgs,
            "pkgb",
        ]
    )
    assert list_depends(virtualenv_python, "pkgb") == {"pkga"}
