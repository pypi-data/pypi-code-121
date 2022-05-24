import os
import shutil

from pykotor.common.stream import BinaryReader
from pykotor.tools import sound

from pykotor.extract.installation import Installation
from pykotor.resource.formats.ssf import read_ssf, SSFSound
from pykotor.resource.formats.tlk import read_tlk
from pykotor.resource.generics.dlg import read_dlg
from pykotor.resource.type import ResourceType

k1_path = "C:/Program Files (x86)/Steam/steamapps/common/swkotor/"
k2_path = "C:/Users/hugin/Documents/Apps/TSLVanilla/"
k1_inst = Installation(k1_path)
k2_inst = Installation(k2_path)
k1_tlk = read_tlk(k1_path + "dialog.tlk")
k2_tlk = read_tlk(k2_path + "dialog.tlk")

voice_folder = "C:/Users/hugin/Documents/tts/hk/merge"
voices = {}

files = {}
for path in [os.path.join(path, name) for path, subdirs, files in os.walk(k1_inst.streamvoice_path()) for name in files] \
        + [os.path.join(path, name) for path, subdirs, files in os.walk(k1_inst.streamsounds_path()) for name in files]:
    file = os.path.basename(path).replace(".wav", "").lower()
    files[file] = path


def search(inst, tlk, dlg_tags, ssf_files, dlg_files):
    resources = inst.chitin_resources()
    for module in inst.modules_list():
        resources.extend(inst.module_resources(module))

    # Soundset files
    for res in resources:
        if res.restype() != ResourceType.SSF:
            continue
        if res.resname().lower() not in ssf_files:
            continue

        ssf = read_ssf(res.data())
        for i in range(28):
            sound = ssf.get(SSFSound(i))
            if sound != -1 and tlk.get(sound).text != "" and tlk.get(sound).voiceover.get() != "":
                voices[tlk.get(sound).voiceover.get().lower()] = tlk.get(sound).text

    # Dialog files
    for res in resources:
        if res.restype() != ResourceType.DLG:
            continue

        dlg = read_dlg(res.data())

        for entry in dlg.all_entries():
            file = entry.vo_resref.get().lower()

            if entry.speaker.lower() in dlg_tags or res.resname().lower() in dlg_files:
                english = tlk.get(entry.text.stringref)
                if english is not None and not english.text.isspace():
                    voices[file] = english.text


search(k1_inst, k1_tlk, ["hk47"], ["p_hk47"], ["k_hhkd_dialog"])
for vo, text in voices.items():
    if vo in files:
        if "[Unintelligible]" in text:
            continue

        with open("{}/{}.txt".format(voice_folder, vo), "w") as f:
            f.write(text)

        audio = sound.fix_audio(BinaryReader.load_file(files[vo]))
        # audio = BinaryReader.load_file(files[vo])
        with open("{}/{}.wav".format(voice_folder, vo), "wb") as f:
            f.write(audio)
