import unittest
from compressnets.network import *


class TemporalNetworkTests(unittest.TestCase):
    def test_get_ordered_pairs_odd(self):
        temporal_net = TemporalNetwork(['a', 'b', 'c', 'd', 'e', 'f'])
        pairs = temporal_net.get_ordered_pairs()
        self.assertEqual(pairs[0], ('a', 'b'))
        self.assertEqual(pairs[1], ('b', 'c'))
        self.assertEqual(pairs[2], ('c', 'd'))
        self.assertEqual(pairs[3], ('d', 'e'))
        self.assertEqual(pairs[4], ('e', 'f'))
        self.assertEqual(len(pairs), 5)

    def test_get_ordered_pairs_even(self):
        temporal_net = TemporalNetwork(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
        pairs = temporal_net.get_ordered_pairs()
        self.assertEqual(pairs[0], ('a', 'b'))
        self.assertEqual(pairs[1], ('b', 'c'))
        self.assertEqual(pairs[2], ('c', 'd'))
        self.assertEqual(pairs[3], ('d', 'e'))
        self.assertEqual(pairs[4], ('e', 'f'))
        self.assertEqual(pairs[5], ('f', 'g'))
        self.assertEqual(len(pairs), 6)

    def test_equals(self):
        # SETUP
        A = Snapshot(1, 2, .5,
                  np.array([[0, 1, 0],
                            [1, 0, 1],
                            [0, 1, 0]]))
        B = Snapshot(2, 3, .5,
                  np.array([[0, 0, 0],
                            [0, 0, 1],
                            [0, 1, 0]]))
        temporal_net = TemporalNetwork([A, A, B, B])
        another_net = TemporalNetwork([A, B, A, B])

        # ACT / ASSERT
        self.assertTrue(temporal_net.equals(temporal_net))
        self.assertTrue(another_net.equals(another_net))
        self.assertFalse(another_net.equals(temporal_net))
        self.assertFalse(temporal_net.equals(another_net))

    def test_time_network_map(self):
        # SETUP
        A = Snapshot(1, 2, .5,
                  np.array([[0, 1, 0],
                            [1, 0, 1],
                            [0, 1, 0]]))
        B = Snapshot(2, 3, .5,
                  np.array([[0, 0, 0],
                            [0, 0, 1],
                            [0, 1, 0]]))
        C = Snapshot(3, 4, .5,
                  np.array([[0, 0, 0],
                            [0, 0, 1],
                            [0, 1, 0]]))
        temporal_net = TemporalNetwork([A, B, C])
        expected_map = {2: A.A, 3: B.A, 4: C.A}
        # ACT / ASSERT
        self.assertEqual(expected_map, temporal_net.get_time_network_map())


class TemporalDataTests(unittest.TestCase):
    def test_to_snapshot_list(self):
        A = np.array([[0, 1, 0],
                            [1, 0, 1],
                            [0, 1, 0]])
        B = np.array([[0, 1, 1],
                            [1, 0, 1],
                            [1, 1, 0]])
        C = np.array([[0, 0, 0],
                            [0, 0, 1],
                            [0, 1, 0]])

        my_data = TemporalData([A, B, C], interval=6, beta=0.2)
        my_snapshots = my_data.to_snapshot_list()

        self.assertTrue(np.array_equal(A, my_snapshots[0].A))
        self.assertTrue(np.array_equal(B, my_snapshots[1].A))
        self.assertTrue(np.array_equal(C, my_snapshots[2].A))

    def test_can_build_temporal_net_from_data(self):
        A = np.array([[0, 1, 0],
                            [1, 0, 1],
                            [0, 1, 0]])
        B = np.array([[0, 1, 1],
                            [1, 0, 1],
                            [1, 1, 0]])
        C = np.array([[0, 0, 0],
                            [0, 0, 1],
                            [0, 1, 0]])

        my_data = TemporalData([A, B, C], interval=6, beta=0.2)
        network_from_data = TemporalNetwork(my_data.to_snapshot_list())

        network_manual = TemporalNetwork([Snapshot(0, 6, 0.2, A),
                                          Snapshot(6, 12, 0.2, B),
                                          Snapshot(12, 18, 0.2, C)])

        self.assertTrue(network_from_data.equals(network_manual))
