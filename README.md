# Example of `uproot-custom` usage

This project demonstrates how to use the `uproot-custom` package to customize branch data reading. You can use this project as a template to create your own downstream projects that leverage `uproot-custom` for reading custom ROOT data structures.

## Introduction

It implements 2 factories to read [`TOverrideStreamer`](./gen-demo-data/include/TOverrideStreamer.hh) and [`TObjWithObjArray`](./gen-demo-data/include/TObjInObjArray.hh) objects from [demo ROOT files](./tests/demo-data.root). The class definitions and the program generating the demo file are located at [`./gen-demo-data`](./gen-demo-data/).

Each factory implements the reader for all three backends of `uproot-custom`, so the same branch can be read three ways:

| Backend | Reader | Runs the read path | In this project |
| ------- | ------ | ------------------ | --------------- |
| `detree` | a Detree reader: Python source compiled to a detree-vm module | the Detree machine | `DtOverrideStreamerReader`, `DtTObjArrayReader` |
| `python` | a Python `IReader` | the Python interpreter | `PyOverrideStreamerReader`, `PyTObjArrayReader` |
| `cpp` | a C++ `IReader` | native code in the `_kernel` extension | `kernel/my_reader.cc` |

`detree` is the recommended route for a new project: one implementation, no build step, and no version pinning. The `python` and `cpp` readers are kept here to show the Python + C++ route and to exercise the compiled extension. See [choosing a technical route](https://mrzimu.github.io/uproot-custom/concepts/choosing-a-route.html).

> [!IMPORTANT]
> `cpp` is the default backend of `uproot-custom`. A project that only writes Detree readers must select `detree` before the first read; a factory without `build_cpp_reader` raises `NotImplementedError` instead of falling back silently.

## Project structure

A typical downstream project using `uproot-custom` will have the following structure:

```
my-read-project/
    ├── pyproject.toml
    ├── my_read_project/        # the Python package, `import my_read_project`
    │   ├── __init__.py         # registers the factories and the target branches
    │   ├── OverrideStreamer.py # `TOverrideStreamer`: factory + detree/python readers
    │   ├── TObjArray.py        # `TObjArray`: factory + detree/python readers
    │   └── _kernel.pyi         # type stubs for the C++ extension
    ├── kernel/                 # C++ sources, built into `my_read_project/_kernel`
    │   ├── CMakeLists.txt
    │   └── my_reader.cc
    ├── gen-demo-data/          # the program that writes `tests/demo-data.root`
    └── tests/
        ├── demo-data.root
        ├── test_detree.py
        ├── test_python.py
        └── test_cpp.py
```

- `pyproject.toml` file is required to specify the project metadata and build system requirements.
- `my_read_project` directory contains the Python source files, which is the entry point for users to do `import my_read_project`.
- `kernel` directory contains the C++ source files that implement custom data reading logic. `cmake.source-dir` in `pyproject.toml` points at it, and the extension is installed into the package as `my_read_project/_kernel`.

> [!TIP]
> The name of this example project is `my-read-project`, and the Python module name is `my_read_project`. See [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) to learn more about `pyproject.toml`.

A project that takes only the Detree route needs none of the C++ half: drop `kernel/`, the `from . import _kernel` import, `build_cpp_reader`, and the `pybind11` and `uproot-custom` C++ build requirements in `pyproject.toml`. Everything else stays.

## Installation

To install this package, run:

```bash
cd /path/to/this/project
pip install .
```

You can also install it in editable mode for development:

```bash
cd /path/to/this/project
pip install -e .
```

## The Detree reader

A Detree reader declares its output buffers and sub-readers as class fields and implements `read` and `data`. `my_read_project/OverrideStreamer.py` is the smallest one:

```python
@detree.reader
class DtOverrideStreamerReader(detree.Reader):
    buf_ints: detree.BufferProxy = detree.Buffer("i")
    buf_doubles: detree.BufferProxy = detree.Buffer("d")

    def read(self, stream: detree.Stream):
        stream.skip_TObject()
        stream.read_into(self.buf_ints)
        mask = stream.read_uint32()
        assert mask == 0x12345678, "Expect mask 0x12345678"
        self.buf_doubles.append(stream.read_double())

    def data(self):
        return np.asarray(self.buf_ints), np.asarray(self.buf_doubles)
```

- `detree.Buffer("i")` is a typed output array; `type` is a `struct` typecode, a NumPy dtype or a dtype string. `detree.Buffer("q", init=(0,), kind="offsets")` in `TObjArray.py` is a cumulative-offset buffer that starts at `0`.
- `detree.Child()` is exactly one sub-reader. `TObjArrayFactory.build_detree_reader` builds the element reader from its element factory and passes it in, the same way the C++ and Python builders do.
- `read` is **compiled**, not interpreted, so it stays inside a small Python subset. There is no `raise`: report a bad record with `assert`. A counted ROOT frame is written as `with stream.check_nbytes():`, which reads the masked `fNBytes` and checks where the frame ends; the Python reader spells the same step `stream.skip_fNBytes()`.
- `data` runs as ordinary Python once the buffers are filled, so its return shape must stay in step with the factory's `make_awkward_content`, exactly as for a Python or C++ reader.
- The class must be defined in a `.py` file: the compiler re-reads its source, so a reader typed into a notebook or a REPL is refused when the class is defined.

The factory gains one builder beside the other two, and nothing else changes:

```python
def build_detree_reader(self):
    return DtOverrideStreamerReader(self.name)
```

`build_factory`, `make_awkward_content` and `make_awkward_form` are shared by every backend, so all three readers decode to the same awkward array. The full DSL (fields, the compilable subset, counted regions and the error types) is in the [Detree reader reference](https://mrzimu.github.io/uproot-custom/reference/detree-dsl.html), with a guided version in [Write a Detree reader](https://mrzimu.github.io/uproot-custom/tutorial/write-a-reader.html).

## Selecting a backend

```python
import uproot
import uproot_custom as uc

import my_read_project  # noqa: F401  (registers the factories)

tree = uproot.open("tests/demo-data.root")["my_tree"]

with uc.use_backend("detree"):
    arrays = tree["override_streamer"].arrays()
```

`uc.set_backend("detree")` sets the backend for the rest of the process, and `UPROOT_CUSTOM_READER_BACKEND=detree` sets it before the first read. Select it before reading a branch: the reader is built once per branch, and only the selected backend's builder runs.

## Tests

```bash
pytest -v tests/
```

There is one test module per backend (`test_detree.py`, `test_python.py` and `test_cpp.py`), and each reads both demo branches inside `uc.use_backend(...)`, so a backend that silently fell back would fail. `test_cpp.py` needs the compiled `_kernel` extension, which `pip install -e .` builds.

`tests/demo-data.root` is a copy of the file `gen-demo-data` writes; see [`gen-demo-data/README.md`](./gen-demo-data/README.md) to regenerate it.
