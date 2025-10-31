from pathlib import Path

import uproot

import my_reader

tree = uproot.open(Path(__file__).parent / "test-data.root")["my_tree"]


def test_override_streamer():
    tree["override_streamer"].array()


def test_tobjarray():
    tree["obj_with_obj_array"].arrays()
