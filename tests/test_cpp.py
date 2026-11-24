from pathlib import Path

import uproot
import uproot_custom as uc

import my_read_project  # noqa: F401

tree = uproot.open(Path(__file__).parent / "demo-data.root")["my_tree"]


def test_override_streamer():
    with uc.use_backend("cpp"):
        tree["override_streamer"].arrays()


def test_tobjarray():
    with uc.use_backend("cpp"):
        tree["obj_with_obj_array"].arrays()
