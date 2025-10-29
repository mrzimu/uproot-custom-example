# Example of `uproot-custom` usage

This project demonstrates how to use the `uproot-custom` package to customize branch data reading.

## Introduction

It implements 2 factory-reader pairs to read [`TOverrideStreamer`](https://github.com/mrzimu/uproot-custom/blob/main/example/gen-demo-data/include/TOverrideStreamer.hh) and [`TObjWithObjArray`](https://github.com/mrzimu/uproot-custom/blob/main/example/gen-demo-data/include/TObjInObjArray.hh) objects from [demo ROOT files](https://github.com/mrzimu/uproot-custom/blob/main/tests/test-data.root). The program generating demo file is located at [`uproot-custom/example/gen-demo-data`](https://github.com/mrzimu/uproot-custom/tree/main/example/gen-demo-data).

## Project structure

A typical downstream project using `uproot-custom` will have the following structure:

```
my_project/
    ├── pyproject.toml
    ├── my_module/
    │   └── Python source files...
    └── cpp/
        └── C++ source files...

```

- `pyproject.toml` file is required to specify the project metadata and build system requirements.
- `my_module` directory contains the Python source files, which is the entry point for users to do `import my_module`. 
- `cpp` directory contains the C++ source files that implement custom data reading logic.

> [!TIP]
> The name of this project is `my-reader`, and the Python module name is `my_reader`. See [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) to learn more about `pyproject.toml`.

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
