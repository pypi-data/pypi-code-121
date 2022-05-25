# PSPTool - Display, extract and manipulate PSP firmware inside UEFI images
# Copyright (C) 2021 Christian Werling, Robert Buhren, Hans Niklas Jacob
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from binascii import hexlify
from .utils import NestedBuffer


class KeyId(NestedBuffer):

    @property
    def magic(self) -> str:
        return hexlify(self.get_bytes(0, 2)).upper().decode('ascii')

    def as_string(self) -> str:
        return hexlify(self.get_bytes()).upper().decode('ascii')

    def __repr__(self):
        return f'KeyId({self.as_string()})'


class Signature(NestedBuffer):
    @classmethod
    def from_nested_buffer(cls, nb):
        return Signature(nb.parent_buffer, nb.buffer_size, buffer_offset=nb.buffer_offset)


class ReversedSignature(Signature):
    def __getitem__(self, item):
        if isinstance(item, slice):
            new_slice = self._offset_slice(item)
            return self.parent_buffer[new_slice]
        else:
            assert (isinstance(item, int))
            assert item >= 0, "Negative index not supported for ReversedSignature"
            return self.parent_buffer[self.buffer_offset + self.buffer_size - item - 1]

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            new_slice = self._offset_slice(key)
            self.parent_buffer[new_slice] = value
        else:
            assert (isinstance(key, int))
            self.parent_buffer[self.buffer_offset + self.buffer_size - key - 1] = value

    def _offset_slice(self, item):
        return slice(
            self.buffer_offset + self.buffer_size - (item.start or 0) - 1,
            self.buffer_offset + self.buffer_size - (item.stop or self.buffer_size) - 1,
            -1
        )


# Reverse lookups with ENTRY_TYPE_NUM defined below
ENTRY_TYPES = {
        0x00: 'AMD_PUBLIC_KEY',
        0x01: 'PSP_FW_BOOT_LOADER',
        0x02: 'PSP_FW_TRUSTED_OS',
        0x03: 'PSP_FW_RECOVERY_BOOT_LOADER',
        0x04: 'PSP_NV_DATA',
        0x05: 'BIOS_PUBLIC_KEY',
        0x06: 'BIOS_RTM_FIRMWARE',
        0x07: 'BIOS_RTM_SIGNATURE',
        0x08: 'SMU_OFFCHIP_FW',
        0x09: 'SEC_DBG_PUBLIC_KEY',
        0x0A: 'OEM_PSP_FW_PUBLIC_KEY',
        0x0B: 'SOFT_FUSE_CHAIN_01',
        0x0C: 'PSP_BOOT_TIME_TRUSTLETS',
        0x0D: 'PSP_BOOT_TIME_TRUSTLETS_KEY',
        0x10: 'PSP_AGESA_RESUME_FW',
        0x12: 'SMU_OFF_CHIP_FW_2',
        0x13: 'DEBUG_UNLOCK',
        0x1A: 'PSP_S3_NV_DATA',
        0x21: 'WRAPPED_IKEK',
        0x22: 'TOKEN_UNLOCK',
        0x24: 'SEC_GASKET',
        0x25: 'MP2_FW',
        0x28: 'DRIVER_ENTRIES',
        0x2D: 'S0I3_DRIVER',
        0x30: 'ABL0',
        0x31: 'ABL1',
        0x32: 'ABL2',
        0x33: 'ABL3',
        0x34: 'ABL4',
        0x35: 'ABL5',
        0x36: 'ABL6',
        0x37: 'ABL7',
        0x3A: 'FW_PSP_WHITELIST',
        # 0x40: 'FW_L2_PTR',
        0x41: 'FW_IMC',
        0x42: 'FW_GEC',
        # 0x43: 'FW_XHCI',
        0x44: 'FW_INVALID',
        0x46: 'ANOTHER_FET',
        0x50: 'KEY_DATABASE',
        0x5f: 'FW_PSP_SMUSCS',
        0x60: 'FW_IMC',
        0x61: 'FW_GEC',
        0x62: 'FW_XHCI',
        0x63: 'FW_INVALID',
        0x108: 'PSP_SMU_FN_FIRMWARE',
        0x118: 'PSP_SMU_FN_FIRMWARE2',

        # Entry types named by us
        #   Custom names are denoted by a leading '!'
        0x14: '!PSP_MCLF_TRUSTLETS',  # very similiar to ~PspTrustlets.bin~ in coreboot blobs
        0x38: '!PSP_ENCRYPTED_NV_DATA',
        0x40: '!PL2_SECONDARY_DIRECTORY',
        0x43: '!KEY_UNKNOWN_1',
        0x4e: '!KEY_UNKNOWN_2',
        0x70: '!BL2_SECONDARY_DIRECTORY',
        0x15f: '!FW_PSP_SMUSCS_2',  # seems to be a secondary FW_PSP_SMUSCS (see above)
        0x112: '!SMU_OFF_CHIP_FW_3',  # seems to tbe a tertiary SMU image (see above)
        0x39: '!SEV_APP',
        0x10062: '!UEFI-IMAGE',
        0x30062: '!UEFI-IMAGE',
        0xdead: '!KEY_NOT_IN_DIR'
}

ENTRY_TYPE_NUM = {value: key for key, value in ENTRY_TYPES.items()}
