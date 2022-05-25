"""Constants package for PyVSS."""
PACKAGE_NAME = "pyvss"

__version__ = '2022.5.0'


API_ENDPOINT_BASE = 'https://cloud-api.eis.utoronto.ca'

VSS_S3_URL = 'https://vskey-stor.eis.utoronto.ca'
VSS_S3_SVC_URL = '{s3_server}/s3/minio-svc/index.php'
VSS_S3_STS_URL = '{s3_svc_url}?status=json'

DEFAULT_TIMEOUT = 60
DEFAULT_DEBUG = False
DEFAULT_DRY_RUN = False
DATETIME_FMT = '%Y-%m-%d %H:%M'
VALID_VM_USAGE = [
    ('Production', 'Prod'),
    ('Testing', 'Test'),
    ('Development', 'Dev'),
    ('QA', 'QA'),
]
VALID_VM_BUILD_PROCESS = [
    {
        "description": "Empty virtual machine. OS must be installed.",
        "label": "OS Install",
        "type": "os_install",
    },
    {
        "description": "Clone from either running or stopped virtual machine.",
        "label": "VM Clone",
        "type": "clone",
    },
    {
        "description": "Deploy from virtual machine template.",
        "label": "VM Template",
        "type": "template",
    },
    {
        "description": "Deploy from OVF/OVA virtual machine template.",
        "label": "OVF/OVA Image",
        "type": "image",
    },
    {
        "description": "Deploy from content library "
        "item (VM template or OVF).",
        "label": "Content Library",
        "type": "contentlib",
    },
]
VALID_VM_NIC_TYPE = [
    {
        "description": "The VMXNET 3 adapter is the next generation of a "
        "paravirtualized NIC designed for performance, and "
        "is not related to VMXNET or VMXNET 2. It offers "
        "all the features available in VMXNET 2, and adds "
        "several new features like multi queue support (also "
        "known as Receive Side Scaling in Windows), IPv6 "
        "offloads, and MSI/MSI-X interrupt delivery.",
        "type": "vmxnet3",
    },
    {
        "description": "The VMXNET 2 adapter is based on the VMXNET adapter "
        "but provides some high-performance features commonly "
        "used on modern networks, such as jumbo frames and "
        "hardware offloads. This virtual network adapter is "
        "available only for some guest operating systems on "
        "ESXi/ESX 3.5 and later. ",
        "type": "vmxnet2",
    },
    {
        "description": "This feature emulates a newer model of Intel Gigabit "
        "NIC (number 82574) in the virtual hardware. ",
        "type": "e1000e",
    },
    {
        "description": "An emulated version of the Intel 82545EM Gigabit"
        " Ethernet NIC. A driver for this NIC is not included "
        "with all guest operating systems. Typically Linux "
        "versions 2.4.19 and later, Windows XP Professional "
        "x64 Edition and later, and Windows Server 2003 "
        "(32-bit) and later include the E1000 driver.",
        "type": "e1000",
    },
]
VALID_VM_SCSI_CONTROLLER = [
    {"description": "First of virtual SCSI Controllers", "type": "buslogic"},
    {
        "description": "Improved performance and works better "
        "with generic SCSI devices.",
        "type": "lsilogic",
    },
    {
        "description": "Improved performance with a serial interface "
        "and works better with generic SCSI devices.",
        "type": "lsilogicsas",
    },
    {
        "description": "Offers a significant reduction in CPU utilization "
        "as well as potentially increased throughput "
        "compared to the default virtual storage adapters, "
        "and is thus the best choice for environments with "
        "very I/O-intensive guest applications.",
        "type": "paravirtual",
    },
]
VALID_VM_DISK_MODE = [
    {
        "description": "Changes are appended to the redo log; "
        "you revoke changes by removing the undo log.",
        "type": "append",
    },
    {
        "description": "Same as nonpersistent, but not affected by snapshots.",
        "type": "independent_nonpersistent",
    },
    {
        "description": "Same as persistent, but not affected by snapshots.",
        "type": "independent_persistent",
    },
    {
        "description": "Changes to virtual disk are made to a redo log "
        "and discarded at power off.",
        "type": "nonpersistent",
    },
    {
        "description": "Changes are immediately and permanently written "
        "to the virtual disk.",
        "type": "persistent",
    },
    {
        "description": "Changes are made to a redo log, but you are given "
        "the option to commit or undo.",
        "type": "undoable",
    },
]
VALID_VM_DISK_SHARING = [
    {
        "type": "sharingmultiwriter",
        "description": "The virtual disk is shared between "
        "multiple virtual machines.",
    },
    {"type": "sharingnone", "description": "The virtual disk is not shared."},
]

VALID_VM_VMX = [
    {"description": "ESXi 6.5", "type": "vmx-13"},
    {
        "description": "Fusion 8.x/Workstation Pro 12.x/Workstation "
        "Player 12.x",
        "type": "vmx-12",
    },
    {
        "description": "ESXi 6.0/Fusion 7.x/Workstation 11.x/Player 7.x",
        "type": "vmx-11",
    },
    {
        "description": "ESXi 5.5/Fusion 6.x/Workstation 10.x/Player 6.x",
        "type": "vmx-10",
    },
    {
        "description": "ESXi 5.1/Fusion 5.x/Workstation 9.x/Player 5.x",
        "type": "vmx-9",
    },
    {
        "description": "ESXi 5.0/Fusion 4.x/Workstation 8.x/Player 4.x",
        "type": "vmx-8",
    },
    {
        "description": "ESXi/ESX 4.x/Fusion 3.x/Fusion 2.x/Workstation "
        "7.x/Workstation 6.5.x/Player 3.x/Server 2.x",
        "type": "vmx-7",
    },
]

VALID_VM_EXTRA_CFG = [
    {
        "description": "Enable disk UUID on virtual machines",
        "option": "disk.EnableUUID",
    },
    {
        "description": "Enable content Copy/Paste between "
        "VMRC client and Windows/Linux",
        "option": "isolation.tools.copy.disable",
    },
    {
        "description": "Enable content Copy/Paste between "
        "VMRC client and Windows/Linux",
        "option": "isolation.tools.paste.disable",
    },
    {
        "description": "Enable content Copy/Paste between "
        "VMRC client and Windows/Linux",
        "option": "isolation.tools.setGUIOptions.enable",
    },
    {
        "description": "You can use the guestinfo variables to "
        "query information such as version and build information.",
        "option": "guestinfo.",
    },
]

VALID_VM_FIRMWARE_TYPE = [
    {"description": "BIOS firmware", "type": "bios"},
    {"description": "Extensible Firmware Interface", "type": "efi"},
]
