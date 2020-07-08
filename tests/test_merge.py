import pytest

from pip_deepfreeze.merge import merge


@pytest.mark.parametrize(
    "in_reqs,frozen_reqs,update_all,to_update,expected",
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
    ],
)
def test_merge(in_reqs, frozen_reqs, update_all, to_update, expected, tmp_path):
    in_filename = tmp_path / "requirements.txt.in"
    in_filename.write_text("\n".join(in_reqs))
    frozen_filename = tmp_path / "requirements.txt"
    frozen_filename.write_text("\n".join(frozen_reqs))
    # TODO remove str() when parse accepts Paths
    assert (
        set(merge(str(in_filename), str(frozen_filename), update_all, to_update))
        == expected
    )


def test_merge_missing_in(tmp_path):
    in_filename = tmp_path / "requirements.txt.in"
    frozen_filename = tmp_path / "requirements.txt"
    frozen_filename.write_text("pkga==1.0.0")
    # TODO remove str() when parse accepts Paths
    assert set(merge(str(in_filename), str(frozen_filename))) == {"pkga==1.0.0"}


def test_merge_missing_frozen(tmp_path):
    in_filename = tmp_path / "requirements.txt.in"
    in_filename.write_text("pkga")
    frozen_filename = tmp_path / "requirements.txt"
    # TODO remove str() when parse accepts Paths
    assert set(merge(str(in_filename), str(frozen_filename))) == {"pkga"}
