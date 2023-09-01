import pytest

from pip_deepfreeze.req_merge import prepare_frozen_reqs_for_upgrade


@pytest.mark.parametrize(
    "in_reqs,frozen_reqs,upgrade_all,to_upgrade,expected",
    [
        ([], [], False, None, set()),
        (
            ["pkga"],
            ["pkga==1.0.0", "pkgb==1.0.0"],
            False,
            None,
            {"pkga==1.0.0", "pkgb==1.0.0"},
        ),
        # update all
        (["pkga"], ["pkga==1.0.0", "pkgb==1.0.0"], True, None, {"pkga"}),
        # empty frozen list, same as update all
        (["pkga"], [], False, None, {"pkga"}),
        # update pkga
        (
            ["pkga"],
            ["pkga==1.0.0", "pkgb==1.0.0"],
            False,
            ["pkga"],
            {"pkga", "pkgb==1.0.0"},
        ),
        # options and comments
        (
            ["# a comment", "-f './wheel house'", "pkga"],
            ["pkga==1.0.0", "pkgb==1.0.0"],
            False,
            None,
            {"-f './wheel house'", "pkga==1.0.0", "pkgb==1.0.0"},
        ),
        # repeated req in constraints, with different env marker
        (
            ['pkga>=3.0 ; python_version>="3"', 'pkga<3 ; python_version<"3"'],
            [],
            False,
            None,
            {'pkga>=3.0 ; python_version>="3"', 'pkga<3 ; python_version<"3"'},
        ),
    ],
)
def test_merge(in_reqs, frozen_reqs, upgrade_all, to_upgrade, expected, tmp_path):
    in_filename = tmp_path / "requirements.txt.in"
    in_filename.write_text("\n".join(in_reqs))
    frozen_filename = tmp_path / "requirements.txt"
    frozen_filename.write_text("\n".join(frozen_reqs))
    assert (
        set(
            prepare_frozen_reqs_for_upgrade(
                [frozen_filename], in_filename, upgrade_all, to_upgrade
            )
        )
        == expected
    )


def test_merge_missing_in(tmp_path):
    in_filename = tmp_path / "requirements.txt.in"
    frozen_filename = tmp_path / "requirements.txt"
    frozen_filename.write_text("pkga==1.0.0")
    assert set(prepare_frozen_reqs_for_upgrade([frozen_filename], in_filename)) == {
        "pkga==1.0.0"
    }


def test_merge_missing_frozen(tmp_path):
    in_filename = tmp_path / "requirements.txt.in"
    in_filename.write_text("pkga")
    frozen_filename = tmp_path / "requirements.txt"
    assert set(prepare_frozen_reqs_for_upgrade([frozen_filename], in_filename)) == {
        "pkga"
    }


def test_req_merge_unnamed_in(tmp_path, capsys):
    in_filename = tmp_path / "requirements.txt.in"
    in_filename.write_text("-e .")
    frozen_filename = tmp_path / "requirements.txt"
    assert set(prepare_frozen_reqs_for_upgrade([frozen_filename], in_filename)) == set()
    captured = capsys.readouterr()
    assert "Ignoring unnamed constraint '-e .'" in captured.err


def test_req_merge_unnamed_frozen(tmp_path, capsys):
    in_filename = tmp_path / "requirements.txt.in"
    frozen_filename = tmp_path / "requirements.txt"
    frozen_filename.write_text("-e .")
    assert set(prepare_frozen_reqs_for_upgrade([frozen_filename], in_filename)) == set()
    captured = capsys.readouterr()
    assert "Ignoring unnamed frozen requirement '-e .'" in captured.err


def test_req_merge_named_editable(tmp_path):
    in_filename = tmp_path / "requirements.txt.in"
    in_filename.write_text(
        "-e git+https://github.com/pypa/pip-test-package#egg=pip-test-package"
    )
    frozen_filename = tmp_path / "requirements.txt"
    assert set(prepare_frozen_reqs_for_upgrade([frozen_filename], in_filename)) == set(
        ["-e git+https://github.com/pypa/pip-test-package#egg=pip-test-package"]
    )
