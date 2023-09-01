import json
import os
import subprocess

# /!\ this test file must be python 2 compatible /!\
ENV_INFO_JSON = os.path.join(
    os.path.dirname(__file__), "..", "src", "pip_deepfreeze", "env-info-json.py"
)


def test_env_info_json(virtualenv_python):
    """Basic check, more elaborate tests are in test_sanity.py."""
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "pytest-cov",  # pytest-cov needed for subprocess coverage to work
        ]
    )
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "uninstall",
            "-y",
            "wheel",
            "importlib_metadata",
        ]
    )
    env_info_json = subprocess.check_output(
        [virtualenv_python, ENV_INFO_JSON],
        universal_newlines=True,
    )
    env_info = json.loads(env_info_json)
    assert "in_virtualenv" in env_info
