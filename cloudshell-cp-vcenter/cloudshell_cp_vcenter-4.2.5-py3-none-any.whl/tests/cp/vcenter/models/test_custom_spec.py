import pytest

from cloudshell.cp.vcenter.models.custom_spec import Network


@pytest.mark.parametrize(
    ("ip_str", "ip", "subnet_mask", "def_gw"),
    (
        ("192.168.1.15/24", "192.168.1.15", "255.255.255.0", "192.168.1.1"),
        ("192.168.1.15", "192.168.1.15", "255.255.255.0", "192.168.1.1"),
        ("192.168.1.15/24:192.168.1.2", "192.168.1.15", "255.255.255.0", "192.168.1.2"),
        ("192.168.1.15:192.168.1.2", "192.168.1.15", "255.255.255.0", "192.168.1.2"),
    ),
)
def test_network_model(ip_str, ip, subnet_mask, def_gw):
    net = Network.from_str(ip_str)

    assert net.ipv4_address == ip
    assert net.subnet_mask == subnet_mask
    assert net.default_gateway == def_gw
