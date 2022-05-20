# import getpass
# import grp
import logging

# import os
import time as ttime
from collections import deque

import fabio
from event_model import compose_resource
from mxtools.flyer import MXFlyer
from ophyd.status import SubscriptionStatus

logger = logging.getLogger(__name__)
DEFAULT_DATUM_DICT = {"data": None, "omega": None}


class NYXFlyer(MXFlyer):
    def __init__(self, vector, zebra, detector=None) -> None:
        self.name = "NYXFlyer"
        self.vector = vector
        self.zebra = zebra
        self.detector = detector

        self.data_directory_name = None
        self.file_prefix = None
        self.num_images = None
        self.file_number_start = None

        self._asset_docs_cache = deque()
        self._resource_document = None
        self._datum_factory = None

        # self._resource_uids = []
        # self._datum_counter = None
        # TODO: rework to use datum ids dictionary.
        # self._datum_ids = DEFAULT_DATUM_DICT
        self._datum_ids = []
        self._first_file = None

        self._collection_dictionary = None

    def update_parameters(self, **kwargs):
        self.data_directory_name = kwargs.get("data_directory_name", "/nyx-data/test")
        self.file_prefix = kwargs.get("file_prefix", "test")
        self.num_images = kwargs.get("num_images", 1)
        self.file_number_start = kwargs.get("file_number_start", 1)

        super().update_parameters(**kwargs)
        self.zebra.pc.arm_signal.put(1)

    def kickoff(self):
        logger.debug(f"kickoff: flyer {self.name}")
        ttime.sleep(0.5)
        self.detector.stage()
        st = self.vector.move()
        return st

    def complete(self):
        logger.debug("complete: vector tracking")
        st_vector = self.vector.track_move()

        def detector_callback(value, old_value, **kwargs):
            logger.debug(f"DETECTOR status {old_value} ({type(old_value)}) -> {value} ({type(value)})")
            # if old_value == "Acquiring" and value == "Done":
            if old_value == 1 and value == 0:
                logger.debug(f"DETECTOR status successfully changed {old_value} -> {value}")
                return True
            else:
                logger.debug(f"DETECTOR status changing {old_value} -> {value}...")
                return False

        # token = self.detector.cam.acquire.subscribe(detector_callback)
        # st_detector = self.detector.cam.acquire._status

        logger.debug("complete: detector status")
        st_detector = SubscriptionStatus(self.detector.cam.acquire, detector_callback, run=True)

        return st_vector & st_detector

    def describe_collect(self):
        logger.debug("describe_collect: start")
        return_dict = {
            "primary": {
                f"{self.detector.name}_image": {
                    "source": f"{self.detector.name}_image",
                    "dtype": "array",
                    "shape": [
                        self.detector.cam.num_images.get(),
                        self.detector.cam.array_size.array_size_y.get(),
                        self.detector.cam.array_size.array_size_x.get(),
                    ],
                    "external": "FILESTORE:",
                }
            }
        }
        return return_dict

    def collect(self):
        logger.debug("collect: start")

        self.unstage()

        for datum_id in self._datum_ids:
            now = ttime.time()
            data = {
                # f"{self.detector.name}_image": self._datum_ids["data"],
                # "omega": self._datum_ids["omega"],
                f"{self.detector.name}_image": datum_id
            }
            yield {
                "data": data,
                "timestamps": {key: now for key in data},
                "time": now,
                "filled": {key: False for key in data},
            }
        logger.debug("collect: done")

    def collect_asset_docs(self):
        logger.debug("collect_asset_docs: start")
        # asset_docs_cache = []

        start_num = self.file_number_start
        end_num = self.file_number_start + self.num_images
        # ensure that the number format of resource_path below matches LSDC
        # daq_utils.create_filename and AreaDetector field FileTemplate
        for img in range(start_num, end_num):
            self._resource_document, self._datum_factory, _ = compose_resource(
                start={"uid": "needed for compose_resource() but will be discarded"},
                spec="AD_PILATUS_MX",
                root=self.data_directory_name,
                resource_path=f"{self.file_prefix}_{img:05d}.cbf",
                resource_kwargs={},
            )

            self._resource_document.pop("run_start")
            self._asset_docs_cache.append(("resource", self._resource_document))

            datum_document = self._datum_factory(datum_kwargs={})
            logger.debug(f"datum_document: {datum_document}")

            self._datum_ids.append(datum_document["datum_id"])

            self._asset_docs_cache.append(("datum", datum_document))

            self._resource_document = None
            self._datum_factory = None

            items = list(self._asset_docs_cache)
            self._asset_docs_cache.clear()
            for item in items:
                yield item

        # Get the Resource which was produced when the detector was staged.
        # ((name, resource),) = self.detector.file.collect_asset_docs()

        # asset_docs_cache.append(("resource", resource))
        # self._datum_ids = DEFAULT_DATUM_DICT
        # # Generate Datum documents from scratch here, because the detector was
        # # triggered externally by the DeltaTau, never by ophyd.
        # resource_uid = resource["uid"]
        # # num_points = int(math.ceil(self.detector.cam.num_images.get() /
        # #                 self.detector.cam.fw_num_images_per_file.get()))

        # # We are currently generating only one datum document for all frames, that's why
        # #   we use the 0th index below.
        # #
        # # Uncomment & update the line below if more datum documents are needed:
        # # for i in range(num_points):

        # self._first_file = f"{resource['root']}/{resource['resource_path']}_00001.cbf"
        # if not os.path.isfile(self._first_file):
        #     raise RuntimeError(f"File {self._first_file} does not exist")

        # # The pseudocode below is from Tom Caswell explaining the relationship
        # # between resource, datum, and events.
        # #
        # # resource = {
        # #     "resource_id": "RES",
        # #     "resource_kwargs": {},  # this goes to __init__
        # #     "spec": "AD-EIGER-MX",
        # #     ...: ...,
        # # }
        # # datum = {
        # #     "datum_id": "a",
        # #     "datum_kwargs": {"data_key": "data"},  # this goes to __call__
        # #     "resource": "RES",
        # #     ...: ...,
        # # }
        # # datum = {
        # #     "datum_id": "b",
        # #     "datum_kwargs": {"data_key": "omega"},
        # #     "resource": "RES",
        # #     ...: ...,
        # # }

        # # event = {...: ..., "data": {"detector_img": "a", "omega": "b"}}

        # for data_key in self._datum_ids.keys():
        #     datum_id = f"{resource_uid}/{data_key}"
        #     self._datum_ids[data_key] = datum_id
        #     datum = {
        #         "resource": resource_uid,
        #         "datum_id": datum_id,
        #         "datum_kwargs": {"data_key": data_key},
        #     }
        #     asset_docs_cache.append(("datum", datum))
        # return tuple(asset_docs_cache)

    def _extract_metadata(self, field="omega"):
        with fabio.open(self._first_file, "r") as cbf:
            return cbf.pilatus_headers("omega")

    def detector_arm(self, **kwargs):
        start = kwargs["angle_start"]
        width = kwargs["img_width"]
        num_images = kwargs["num_images"]
        exposure_period_per_image = kwargs["exposure_period_per_image"]
        file_prefix = kwargs["file_prefix"]
        x_beam = kwargs["x_beam"]
        y_beam = kwargs["y_beam"]
        wavelength = kwargs["wavelength"]
        det_distance_m = kwargs["det_distance_m"]
        transmission = kwargs["transmission"]

        # These components do not exist for Pilatus (copied from Eiger),
        # so commenting them out now:
        # self.detector.cam.save_files.put(1, wait=True)
        # self.detector.cam.file_owner.put(getpass.getuser(), wait=True)
        # self.detector.cam.file_owner_grp.put(grp.getgrgid(os.getgid())[0], wait=True)
        # self.detector.cam.file_perms.put(420, wait=True)

        file_prefix_minus_directory = str(file_prefix)
        file_prefix_minus_directory = file_prefix_minus_directory.split("/")[-1]

        self.detector.cam.acquire_time.put(exposure_period_per_image - 0.0024, wait=True)
        self.detector.cam.acquire_period.put(exposure_period_per_image, wait=True)
        self.detector.cam.num_images.put(num_images, wait=True)
        # self.detector.cam.file_path.put(data_directory_name, wait=True)
        # self.detector.cam.file_name.put(file_prefix_minus_directory, wait=True)

        # originally from detector_set_fileheader
        self.detector.cam.beam_x.put(x_beam, wait=True)
        self.detector.cam.beam_y.put(y_beam, wait=True)
        self.detector.cam.angle_incr.put(width, wait=True)
        self.detector.cam.start_angle.put(start, wait=True)
        self.detector.cam.wavelength.put(wavelength, wait=True)
        self.detector.cam.det_dist.put(det_distance_m * 1000, wait=True)
        self.detector.cam.filter_transm.put(transmission, wait=True)

        # Setting the file start number, etc.
        self.detector.file.file_path.put(self.data_directory_name)
        self.detector.file.file_name.put(self.file_prefix)
        self.detector.file.file_number.put(self.file_number_start)

        start_arm = ttime.monotonic()

        def armed_callback(value, old_value, **kwargs):
            if old_value == 0 and value == 1:
                return True
            return False

        status = SubscriptionStatus(self.detector.cam.armed, armed_callback, run=False)

        self.detector.cam.acquire.set(1)

        status.wait()
        logger.info(f"arm time = {ttime.monotonic() - start_arm}")

        # return status

    def configure_detector(self, **kwargs):
        # TODO: clean up in the base class.
        pass

    def configure_vector(self, **kwargs):
        angle_start = kwargs["angle_start"]
        scan_width = kwargs["scan_width"]
        exposure_ms = kwargs["exposure_period_per_image"] * 1.0e3
        num_images = kwargs["num_images"]
        x_mm = (kwargs["x_start_um"] / 1000, kwargs["x_start_um"] / 1000)
        y_mm = (kwargs["y_start_um"] / 1000, kwargs["y_start_um"] / 1000)
        z_mm = (kwargs["z_start_um"] / 1000, kwargs["z_start_um"] / 1000)
        o = (angle_start, angle_start + scan_width)
        buffer_time_ms = 0
        shutter_lag_time_ms = 2
        shutter_time_ms = 2
        self.vector.prepare_move(
            o,
            x_mm,
            y_mm,
            z_mm,
            exposure_ms,
            num_images,
            buffer_time_ms,
            shutter_lag_time_ms,
            shutter_time_ms,
        )

    def zebra_daq_prep(self):
        self.zebra.reset.put(1)
        ttime.sleep(2.0)
        self.zebra.out1.put(31)
        self.zebra.m1_set_pos.put(1)
        self.zebra.m2_set_pos.put(1)
        self.zebra.m3_set_pos.put(1)
        self.zebra.pc.arm.trig_source.put(0)  # Soft triggering for NYX
