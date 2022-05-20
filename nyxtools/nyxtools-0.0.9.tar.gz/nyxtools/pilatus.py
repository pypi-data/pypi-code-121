# import datetime

from ophyd import Component as Cpt
from ophyd import Device, EpicsPathSignal, EpicsSignal, ImagePlugin
from ophyd.areadetector.base import ADComponent
from ophyd.areadetector.detectors import PilatusDetector
from ophyd.areadetector.filestore_mixins import FileStoreBase


class PilatusSimulatedFilePlugin(Device, FileStoreBase):
    file_path = ADComponent(EpicsPathSignal, "FilePath", string=True, path_semantics="posix")
    file_name = ADComponent(EpicsPathSignal, "FileName", string=True, path_semantics="posix")
    file_number = ADComponent(EpicsSignal, "FileNumber")

    # external_name = Cpt(Signal, value="")

    def __init__(self, *args, **kwargs):
        self.filestore_spec = "AD_PILATUS_MX"
        self.frame_num = None
        super().__init__(*args, **kwargs)
        self._datum_kwargs_map = dict()

    def stage(self):  # getting values from resource document

        # print(f"{print_now()} staging detector {self.name}")
        # res_uid = self.external_name.get()
        # write_path = datetime.datetime.now().strftime(self.write_path_template)
        # set_and_wait(self.file_path, f"{write_path}/")
        # set_and_wait(self.file_write_name_pattern, "{}_$id".format(res_uid))
        # super().stage()
        # fn = PurePath(self.file_path.get()) / res_uid
        # ipf = int(self.file_write_images_per_file.get())  # noqa
        # # logger.debug("Inserting resource with filename %s", fn)
        # self._fn = fn
        # # res_kwargs = {"images_per_file": ipf}
        # seq_id = int(self.sequence_id.get())  # det writes to the NEXT one
        # res_kwargs = {"seq_id": seq_id}
        # self._generate_resource(res_kwargs)
        # print(f"{print_now()} done staging detector {self.name}")
        # # res_uid = self.external_name.get() #
        # # write_path = datetime.datetime.now().strftime(self.write_path_template)

        super().stage()

    def generate_datum(self, key, timestamp, datum_kwargs):
        if self.frame_num is not None:
            datum_kwargs.update({"frame_num": self.frame_num})
        return super().generate_datum(key, timestamp, datum_kwargs)


class PilatusBase(PilatusDetector):
    file = Cpt(PilatusSimulatedFilePlugin, suffix="cam1:", write_path_template="", root="")
    image = Cpt(ImagePlugin, "image1:")

    def stage(self, *args, **kwargs):
        ret = super().stage(*args, **kwargs)
        return ret

    def unstage(self):
        super().unstage()
