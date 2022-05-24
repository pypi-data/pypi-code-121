"""SatNOGS DB structured data for models"""

from django.contrib.sites.models import Site
from pyld import jsonld


class StructuredData:
    """Generic structered data class for models"""
    def __init__(self, data):
        self.context = {}
        self.data = data

    def get_jsonld(self):
        """Return JSONLD structure"""
        return {"@context": self.context, "@graph": self.data}

    def get_context(self):
        """Return the context of structured data"""
        return self.context

    def get_data(self):
        """Return the data of structured data"""
        return self.data

    def get_expanded(self):
        """Return expanded document form of JSONLD structure"""
        return jsonld.expand(self.get_jsonld())

    def get_compacted(self, context):
        """Return compacted document form of JSONLD structure given a context"""
        return jsonld.compact(self.get_jsonld(), context)

    def get_flattened(self):
        """Return flattened document form of JSONLD structure"""
        return jsonld.flatten(self.get_jsonld())

    def get_framed(self, frame):
        """Return framed document form of JSONLD structure given a frame"""
        return jsonld.frame(self.get_jsonld(), frame)


class ModeStructuredData(StructuredData):
    """Generic structered data class for Mode model"""
    def __init__(self, data):
        super().__init__(data)
        self.context = {"@vocab": "https://schema.space/metasat/", "name": "modulation"}
        structured_data = []

        for mode in data:
            structured_data.append({"name": mode['name']})
        self.data = structured_data


class SatelliteStructuredData(StructuredData):
    """Generic structered data class for Satellite model"""
    def __init__(self, data):
        super().__init__(data)
        self.context = {
            "@vocab": "https://schema.space/metasat/",
            "schema": "http://schema.org/",
            "satellite": "satellite",
            "sat_id": "schema:identifier",
            "name": "schema:name",
            "names": "schema:alternateName",
            "norad_cat_id": "noradID",
            "status": "status",
            "decoder": "decoder",
            "citation": "schema:citation",
        }
        self.frame = {
            "@context": self.context,
            'satellite': {
                "@requireAll": True,
                "name": {},
                "status": {},
                "citation": {},
            }
        }

        if isinstance(data, dict):
            self.data = self.structure_satellite_data(data)
            return

        structured_data = []
        for satellite in data:
            data_to_append = self.structure_satellite_data(satellite)
            structured_data.append(data_to_append)

        self.data = structured_data

    @staticmethod
    def structure_satellite_data(satellite):
        """Return structured data for one satellite.

        :param satellite: the satellite to be structured
        """
        satellite_id_domain = Site.objects.get_current().domain + '/satellite/'
        data_to_append = {
            "satellite": {
                "@id": satellite_id_domain + str(satellite['sat_id']),
                "sat_id": satellite['sat_id'],
                "norad_cat_id": satellite['norad_cat_id'],
                "name": satellite['name'],
                "status": satellite['status'],
                "citation": satellite['citation']
            }
        }

        if satellite['names']:
            data_to_append['satellite']['names'] = satellite['names'].replace('\r', '').split('\n')

        if satellite['telemetries']:
            data_to_append['satellite']['decoder'] = []
            for decoder in satellite['telemetries']:
                data_to_append['satellite']['decoder'].append(decoder["decoder"])

        return data_to_append


class TransmitterStructuredData(StructuredData):
    """Generic structered data class for Transmitter model"""
    def __init__(self, data):
        super().__init__(data)
        self.context = {
            "@vocab": "https://schema.space/metasat/",
            "schema": "http://schema.org/",
            "transmitter": "transmitter",
            "uuid": "schema:identifier",
            "type": None,
            "description": "schema:description",
            "status": "status",
            "mode": "modulation",
            "frequency": "frequency",
            "minimum": "schema:minimum",
            "maximum": "schema:maximum",
            "drift": "drift",
            "downlink": "downlink",
            "uplink": "uplink",
            "invert": None,
            "baud": "baudRate",
            "satellite": "satellite",
            "norad_cat_id": "noradID",
            "citation": "schema:citation",
            "service": "service"
        }
        self.frame = {
            "@context": self.context,
            'transmitter': {
                "@requireAll": True,
                "description": {},
                "status": {},
                "citation": {},
                "service": {},
                "satellite": {
                    "@requireAll": True,
                    "norad_cat_id": {}
                },
            }
        }
        structured_data = []
        transmitter_id_domain = Site.objects.get_current().domain + '/transmitter/'
        satellite_id_domain = Site.objects.get_current().domain + '/satellite/'

        for transmitter in data:
            data_to_append = {
                "transmitter": {
                    "@id": transmitter_id_domain + transmitter['uuid'],
                    "uuid": transmitter['uuid'],
                    "description": transmitter['description'],
                    "type": transmitter['type'],
                    "satellite": {
                        "@id": satellite_id_domain + str(transmitter['sat_id']),
                        "norad_cat_id": transmitter['norad_cat_id']
                    },
                    "status": transmitter['status'],
                    "citation": transmitter['citation'],
                    "service": transmitter['service']
                }
            }

            if transmitter['downlink_low']:
                if transmitter['downlink_high']:
                    data_to_append['transmitter']['downlink'] = {
                        "frequency": {
                            "minimum": transmitter['downlink_low'],
                            "maximum": transmitter['downlink_high']
                        },
                        "mode": transmitter['mode']
                    }
                else:
                    data_to_append['transmitter']['downlink'] = {
                        "frequency": transmitter['downlink_low'],
                        "mode": transmitter['mode']
                    }
                if transmitter['downlink_drift']:
                    data_to_append['transmitter']['downlink']['drift'] = transmitter[
                        'downlink_drift']

            if transmitter['uplink_low']:
                if transmitter['uplink_high']:
                    data_to_append['transmitter']['uplink'] = {
                        "frequency": {
                            "minimum": transmitter['uplink_low'],
                            "maximum": transmitter['uplink_high']
                        },
                        "mode": transmitter['uplink_mode']
                    }
                else:
                    data_to_append['transmitter']['uplink'] = {
                        "frequency": transmitter['uplink_low'],
                        "mode": transmitter['uplink_mode']
                    }
                if transmitter['uplink_drift']:
                    data_to_append['transmitter']['uplink']['drift'] = transmitter['uplink_drift']

            if transmitter['invert']:
                data_to_append['transmitter']['invert'] = transmitter['invert']

            if transmitter['baud']:
                data_to_append['transmitter']['baud'] = transmitter['baud']

            structured_data.append(data_to_append)
        self.data = structured_data


class DemodDataStructuredData(StructuredData):
    """Generic structered data class for DemodData model"""
    def __init__(self, data):
        super().__init__(data)
        self.context = {
            "@vocab": "https://schema.space/metasat/",
            "schema": "http://schema.org/",
            "frame": "frame",
            "satellite": "satellite",
            "norad_cat_id": "noradID",
            "observer": "groundStation",
            "ground_station_locator": "maidenheadLocator",
            "ground_station_name": "schema:name",
            "status": "schema:status",
            "timestamp": "timestamp"
        }
        structured_data = []
        satellite_id_domain = Site.objects.get_current().domain + '/satellite/'

        for frame in data:

            observer_splitted = frame['observer'].split('-')
            ground_station_locator = observer_splitted.pop()
            ground_station_name = observer_splitted

            data_to_append = {
                "frame": frame['frame'],
                "satellite": {
                    "@id": satellite_id_domain + str(frame['sat_id']),
                    "norad_cat_id": frame['norad_cat_id']
                },
                "observer": {
                    "ground_station_name": ground_station_name,
                    "ground_station_locator": ground_station_locator
                },
                "timestamp": frame['timestamp']
            }

            if frame['decoded']:
                data_to_append['status'] = "decoded"

            structured_data.append(data_to_append)
        self.data = structured_data


def get_structured_data(basename, data):
    """Return structered data instance based on the given basename and given data"""
    if basename == "mode":
        return ModeStructuredData(data)
    if basename == "satellite":
        return SatelliteStructuredData(data)
    if basename == "transmitter":
        return TransmitterStructuredData(data)
    if basename == "demoddata":
        return DemodDataStructuredData(data)
    return None
