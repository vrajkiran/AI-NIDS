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
        self.assertEqual(flow.protocol, 6)
        self.assertEqual(len(features), 10)
        self.assertEqual(features["Destination Port"], 80)
        self.assertEqual(features["Total Fwd Packets"], 1)
        self.assertEqual(features["Total Backward Packets"], 1)

    def test_flow_expiration_and_finalization(self):
        saved = []
        capture = PacketCapture(
            enabled=False,
            prediction_enabled=False,
            on_detection=lambda meta, flow, res: saved.append((meta, flow, res)),
        )

        packet = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=5000, dport=443)
        capture.handle_packet(packet)

        flow = list(capture.flows.values())[0]
        self.assertFalse(flow.is_expired(current_time=flow.last_time + 5))
        self.assertTrue(flow.is_expired(current_time=flow.last_time + 20))

        # Finalize flows should call on_detection once per flow
        capture.finalize_all_flows()
        self.assertEqual(len(saved), 1)
        self.assertTrue(flow.is_finalized)
        self.assertEqual(saved[0][1].destination.port, 443)

    def test_single_packet_flow_rate_safety(self):
        capture = PacketCapture(enabled=False, prediction_enabled=False)
        single_pkt = IP(src="192.168.1.50", dst="192.168.1.1") / TCP(sport=44444, dport=53)
        capture.handle_packet(single_pkt)

        flow = list(capture.flows.values())[0]
        self.assertEqual(flow.duration_seconds, 0.0)
        features = flow.to_ml_features()
        self.assertEqual(features["Flow Bytes/s"], 0)
        self.assertEqual(features["Flow Packets/s"], 0)
        self.assertFalse(any(isinstance(v, float) and (v != v) for v in features.values()))

    def test_bidirectional_packet_and_byte_counters(self):
        from ml.preprocess import SELECTED_FEATURES

        capture = PacketCapture(enabled=False, prediction_enabled=False)
        p1 = IP(src="1.1.1.1", dst="2.2.2.2") / TCP(sport=1000, dport=80)
        p2 = IP(src="1.1.1.1", dst="2.2.2.2") / TCP(sport=1000, dport=80)
        p3 = IP(src="2.2.2.2", dst="1.1.1.1") / TCP(sport=80, dport=1000)

        capture.handle_packet(p1)
        capture.handle_packet(p2)
        capture.handle_packet(p3)

        flow = list(capture.flows.values())[0]
        self.assertEqual(flow.forward_packet_count, 2)
        self.assertEqual(flow.backward_packet_count, 1)
        self.assertEqual(flow.total_packets, 3)

        features = flow.to_ml_features()
        self.assertEqual(set(features.keys()), set(SELECTED_FEATURES))


if __name__ == "__main__":
    unittest.main()

