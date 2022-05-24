import os

from pykotor.extract.installation import Installation
from pykotor.resource.formats.tlk import read_tlk
from pykotor.resource.generics.dlg import read_dlg
from pykotor.resource.type import ResourceType

k1_path = "C:/Program Files (x86)/Steam/steamapps/common/swkotor/"
k2_path = "C:/Users/hugin/Documents/Apps/TSLVanilla/"
k1_inst = Installation(k1_path)
k2_inst = Installation(k2_path)
k1_tlk = read_tlk(k1_path + "dialog.tlk")
k2_tlk = read_tlk(k2_path + "dialog.tlk")

k1_voice = "C:/Users/hugin/Documents/tts/hk/k1"
k2_voice = "C:/Users/hugin/Documents/tts/hk/k2"

vo = {}

k1_resources = k1_inst.chitin_resources()
for module in k1_inst.modules_list():
    k1_resources.extend(k1_inst.module_resources(module))

k2_resources = k2_inst.chitin_resources()
for module in k2_inst.modules_list():
    k2_resources.extend(k2_inst.module_resources(module))

for file in os.listdir(k1_voice) + os.listdir(k2_voice):
    file = file.lower().replace(".wav", "")
    vo[file] = ""

for res in k1_resources:
    if res.restype() == ResourceType.DLG:
        dlg = read_dlg(res.data())

        for entry in dlg.all_entries():
            file = entry.vo_resref.get().lower()
            if file in vo:
                english = k1_tlk.get(entry.text.stringref)
                if english is not None and not english.text.isspace():
                    vo[file] = english.text
            elif entry.speaker.lower() == "hk47":
                print("add", file)
                vo[file] = None
