import kamzik3
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device


class MeasurementGroup(list):
    def __init__(self, group_id, measurement_group=None):
        self.group_id = group_id
        if measurement_group is not None:
            list.__init__(self)
            for device_id, attribute in measurement_group:
                self.append(device_id, attribute)
        else:
            list.__init__(self)
        kamzik3.session.add_measurement_group(self)

    def append(self, device_id, attribute):
        if isinstance(device_id, Device):
            device_id = device_id.device_id
        item = (device_id, Attribute.list_attribute(attribute))
        if item not in self:
            list.append(self, item)
