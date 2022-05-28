import unittest
import yaml

from res import get_resource
from yog.host.manage_docker_utils import build_volumes_dict
from yog.host.necronomicon import load
from yog.host.manage import load_necronomicons_for_host
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join, dirname
from os import makedirs


class TestNecronomicon(unittest.TestCase):
    def test(self):
        n = load("test1", yaml.safe_load(get_resource("sample_necronomicon.yml")))
        self.assertEqual("mail-relay-postfix", n.docker.containers[0].image)
        self.assertEqual(2, len(n.docker.containers))
        self.assertEqual(1, len(n.cron.crons))
        self.assertEqual("/var/lib/memes", n.docker.containers[1].volumes['memebox'])
        self.assertEqual("test.txt", n.files.files[0].src)

        n = load("test2", yaml.safe_load(get_resource("sample_needs_tunnel_back.yml")))
        self.assertEqual("test.josh.cafe", n.tunnels.tunnels[0].host)
        self.assertEqual(5000, n.tunnels.tunnels[0].target_port)
        self.assertEqual(5000, n.tunnels.tunnels[0].local_port)

    def test_load_necronomicons(self):
        root_dir = mkdtemp()
        try:
            host_file_path = "domains/cafe/josh/clust/ofn/myhost.yml"
            clust_file_path = "domains/cafe/josh/clust.yml"
            hostname = "myhost.ofn.clust.josh.cafe"

            makedirs(dirname(join(root_dir, host_file_path)), exist_ok=True)

            with open(join(root_dir, clust_file_path), "w") as out:
                out.write(get_resource("sample_site_necronomicon.yml").decode("utf-8"))
            with open(join(root_dir, host_file_path), "w") as out:
                out.write(get_resource("sample_necronomicon.yml").decode("utf-8"))

            necronomicons = load_necronomicons_for_host(hostname, root_dir)
            self.assertEqual(2, len(necronomicons))
            self.assertEqual("test2.txt", necronomicons[0].files.files[0].src)
            self.assertEqual("test.txt", necronomicons[1].files.files[0].src)
        finally:
            rmtree(root_dir)

    def test_build_volumes_dist(self):
        n = load("test1", yaml.safe_load(get_resource("sample_necronomicon.yml")))
        self.assertEqual("/tmp/test+ro", n.docker.containers[1].volumes['/tmp/test'])
        d = build_volumes_dict(n.docker.containers[1].volumes)
        self.assertEqual("ro", d["/tmp/test"]["mode"])
        self.assertEqual("rw", d["memebox"]["mode"])


if __name__ == "__main__":
    unittest.main()
