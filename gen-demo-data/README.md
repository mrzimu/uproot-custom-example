# gen-demo-data

This program generates demo data for this repository.

## Usage

```bash
cd /path/to/gen-demo-data
mkdir build
cd build
cmake ..
make -j
./gen-demo-data
```

This will create a `demo-data.root` file in the `build` directory.

Copy it over `../tests/demo-data.root`; the tests read that copy. The file holds one `TOverrideStreamer` and one `TObjWithObjArray` per entry of the tree `my_tree`, written by [`src/main.cc`](./src/main.cc) from the classes in [`include/`](./include/).
