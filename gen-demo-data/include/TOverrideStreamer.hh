#pragma once

#include <TBuffer.h>
#include <TObject.h>

class TOverrideStreamer : public TObject {
private:
  int m_int{0};
  double m_double{0.0};

public:
  TOverrideStreamer(int val = 0)
      : TObject(), m_int(val), m_double((double)val * 3.14) {}

  ClassDef(TOverrideStreamer, 1);
};

/* ---------------------------------------------------------------------------
 */

class TObjToSave : public TObject {
private:
  TOverrideStreamer m_obj;
  std::vector<TOverrideStreamer> m_objVec;
  std::map<int, TOverrideStreamer> m_objMap;

public:
  TObjToSave(int val = 0) : TObject() {
    m_obj = TOverrideStreamer(val);

    // Fill the STL containers with some data
    for (int i = 0; i < 5; ++i) {
      m_objVec.emplace_back(val + i);
      m_objMap.emplace(i, TOverrideStreamer(val + i * 10));
    }
  }

  ClassDef(TObjToSave, 1);
};
