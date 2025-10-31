#include <TFile.h>
#include <TTree.h>

#include "TObjInObjArray.hh"
#include "TOverrideStreamer.hh"

int main() {
  TFile f("demo-data.root", "RECREATE");
  TTree t("my_tree", "tree");

  TObjToSave override_streamer;
  t.Branch("override_streamer", &override_streamer);

  TObjWithObjArray obj_with_obj_array;
  t.Branch("obj_with_obj_array", &obj_with_obj_array);

  for (int i = 0; i < 10; i++) {
    override_streamer = TObjToSave(i);
    obj_with_obj_array = TObjWithObjArray(i);
    t.Fill();
  }

  t.Write();
  f.Close();
}