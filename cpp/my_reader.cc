#include <cstdint>
#include <memory>
#include <vector>

#include "uproot-custom/uproot-custom.hh"

using namespace uproot;

class OverrideStreamerReader : public IReader {
private:
  const std::string m_name;
  std::shared_ptr<std::vector<int>> m_data_ints;
  std::shared_ptr<std::vector<double>> m_data_doubles;

public:
  OverrideStreamerReader(std::string name)
      : IReader(name), m_data_ints(std::make_shared<std::vector<int>>()),
        m_data_doubles(std::make_shared<std::vector<double>>()) {}

  void read(BinaryStream &stream) override {
    // Skip TObject header
    stream.skip_TObject();

    // Read integer value
    m_data_ints->push_back(stream.read<int>());

    // Read a customly added tag
    auto tag = stream.read<uint32_t>();
    if (tag != 0x12345678) {
      throw std::runtime_error("Unexpected tag value: " +
                               std::to_string(tag));
    }

    // Read double value
    m_data_doubles->push_back(stream.read<double>());
  }

  py::object data() const override {
    // `uproot::make_array` converts `std::shared_ptr<std::vector<T>>`
    // to `pybind11::array_t<T>`.
    auto int_array = make_array(m_data_ints);
    auto double_array = make_array(m_data_doubles);

    // Return a tuple of these two arrays. This tuple will be used
    // in `OverrideStreamerFactory.make_awkward_content` method.
    return py::make_tuple(int_array, double_array);
  }
};

class TObjArrayReader : public IReader {
private:
  SharedReader m_element_reader;
  std::shared_ptr<std::vector<int64_t>> m_offsets;

public:
  TObjArrayReader(std::string name, SharedReader element_reader)
      : IReader(name), m_element_reader(element_reader),
        m_offsets(std::make_shared<std::vector<int64_t>>(1, 0)) {}

  void read(BinaryStream &stream) override {
    // Read TObjArray header
    stream.skip_fNBytes();
    stream.skip_fVersion();
    stream.skip_TObject();
    stream.read_TString(); // fName
    auto fSize = stream.read<uint32_t>();
    stream.skip(4); // fLowerBound

    // Record the new offset
    m_offsets->push_back(m_offsets->back() + fSize);

    // Read the elements using the element reader
    m_element_reader->read_many(stream, fSize);
  }

  py::object data() const override {
    auto offsets_array = make_array(m_offsets);
    py::object element_data = m_element_reader->data();
    return py::make_tuple(offsets_array, element_data);
  }
};

/*
 * Declare your C++ module here. The name "cpp" should match
 * the name in `CMakeLists.txt`: `pybind11_add_module(cpp ...)`.
 */
PYBIND11_MODULE(cpp, m) {

  // This macro imports `uproot::IReader` in runtime. It is required
  // for all custom readers.
  IMPORT_UPROOT_CUSTOM_CPP;

  // Declare your custom readers with type information of their constructors.
  declare_reader<OverrideStreamerReader, std::string>(m,
                                                      "OverrideStreamerReader");
  declare_reader<TObjArrayReader, std::string, SharedReader>(m,
                                                             "TObjArrayReader");
}
