#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

# Test dependencies
import uuid

# Library dependencies
from fastybird_metadata.devices_module import DeviceAttributeName
from fastybird_metadata.routing import RoutingKey
from kink import inject

# Library libs
from fastybird_devices_module.entities.device import DeviceAttributeEntity
from fastybird_devices_module.repositories.device import DeviceAttributesRepository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestDeviceAttributesRepository(DbTestCase):
    @inject
    def test_repository_iterator(self, attribute_repository: DeviceAttributesRepository) -> None:
        self.assertEqual(10, len(attribute_repository.get_all()))

    # -----------------------------------------------------------------------------

    @inject
    def test_get_item(self, attribute_repository: DeviceAttributesRepository) -> None:
        entity = attribute_repository.get_by_id(
            attribute_id=uuid.UUID("03164a6d-9628-460c-95cc-90e6216332d9", version=4),
        )

        self.assertIsInstance(entity, DeviceAttributeEntity)
        self.assertEqual(DeviceAttributeName.HARDWARE_MANUFACTURER.value, entity.identifier)

    # -----------------------------------------------------------------------------

    @inject
    def test_transform_to_dict(self, attribute_repository: DeviceAttributesRepository) -> None:
        entity = attribute_repository.get_by_id(
            attribute_id=uuid.UUID("03164a6d-9628-460c-95cc-90e6216332d9", version=4),
        )

        self.assertIsInstance(entity, DeviceAttributeEntity)
        self.assertEqual(
            {
                "id": "03164a6d-9628-460c-95cc-90e6216332d9",
                "identifier": DeviceAttributeName.HARDWARE_MANUFACTURER.value,
                "name": None,
                "content": "itead",
                "device": "69786d15-fd0c-4d9f-9378-33287c2009fa",
                "owner": "455354e8-96bd-4c29-84e7-9f10e1d4db4b",
            },
            entity.to_dict(),
        )
        self.assertIsInstance(
            self.validate_exchange_data(
                routing_key=RoutingKey.DEVICE_ATTRIBUTE_ENTITY_REPORTED,
                data=entity.to_dict(),
            ),
            dict,
        )
