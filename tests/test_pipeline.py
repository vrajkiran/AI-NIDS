"""Small controlled test for flow feature extraction and prediction wiring.

This test does not perform any attack and does not capture real traffic. It uses
synthetic Scapy packets only to verify that flow features are generated in the
same format expected by the trained model.
"""

import unittest
from scapy.layers.inet import IP, TCP
from network.packet_capture import PacketCapture


class TestPipeline(unittest.TestCase):
    def test_synthetic_flow_features(self):
        capture = PacketCapture(enabled=False, prediction_enabled=False)

        first_packet = IP(src="192.168.1.10", dst="192.168.1.20") / TCP(sport=1234, dport=80)
        second_packet = IP(src="192.168.1.20", dst="192.168.1.10") / TCP(sport=80, dport=1234)

        capture.handle_packet(first_packet)
        capture.handle_packet(second_packet)

        flow = list(capture.flows.values())[0]
        features = flow.to_ml_features()

        self.assertEqual(capture.packet_count, 2)
        self.assertEqual(len(capture.flows), 1)
        self.assertEqual(features["Destination Port"], 80)
        self.assertEqual(features["Protocol"], 6)
        self.assertEqual(features["Total Fwd Packets"], 1)
        self.assertEqual(features["Total Backward Packets"], 1)


if __name__ == "__main__":
    unittest.main()

