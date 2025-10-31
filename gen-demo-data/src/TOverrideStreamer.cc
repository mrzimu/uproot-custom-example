#include "TOverrideStreamer.hh"
#include <TObject.h>

#include <iostream>

ClassImp(TOverrideStreamer);

void TOverrideStreamer::Streamer(TBuffer &b) {
  if (b.IsReading()) {
    TObject::Streamer(b); // Call base class Streamer

    b >> m_int;

    unsigned int tag;
    b >> tag; // We additionally read a mask
    if (tag != 0x12345678) {
      throw std::runtime_error(
          "TOverrideStreamer::Streamer: Data corruption detected (invalid "
          "tag)!");
    }

    b >> m_double;
  } else {
    TObject::Streamer(b); // Call base class Streamer
    b << m_int;
    unsigned int tag = 0x12345678; // Example mask
    b << tag;                      // Write the mask
    b << m_double;
  }
}
