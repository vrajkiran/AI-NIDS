"""Real packet capture using Scapy.

Safety rules for this academic project:
- Capture is disabled by default and starts only when explicitly enabled.
- Capture only on your own computer or an authorized lab network.
- Store only packet metadata and flow counters.
- Do not store raw packet payloads.
- Do not inject packets, attack systems, steal credentials, or block traffic.
"""

from __future__ import annotations

import argparse
import logging
import sys
import threading
from pathlib import Path

from scapy.all import conf, sniff

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import CAPTURE_DURATION, LOG_PATH, NETWORK_INTERFACE, PACKET_CAPTURE_ENABLED, PREDICTION_ENABLED
from network.features import extract_packet_metadata, metadata_to_flow_key, metadata_to_reverse_flow_key
from network.flow import Flow


def setup_logging() -> None:
    """Log the pipeline steps for viva/demo explanation."""
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


class PacketCapture:
    """Capture packets, build flows, and optionally predict BENIGN/ATTACK."""

    def __init__(
        self,
        interface: str = "",
        duration: int = 10,
        enabled: bool = False,
        prediction_enabled: bool = False,
        on_detection=None,
    ):
        self.interface = interface
        self.duration = duration
        self.enabled = enabled
        self.prediction_enabled = prediction_enabled
        self.on_detection = on_detection
        self.predictor = None
        self.packet_count = 0
        self.prediction_count = 0
        self.flows = {}
        self.stop_event = threading.Event()
        self.error_message = ""

    @property
    def is_running(self) -> bool:
        return self.enabled and not self.stop_event.is_set()

    def stop(self) -> None:
        """Ask Scapy sniffing to stop after the next packet or timeout."""
        self.stop_event.set()
        self.enabled = False
        logging.info("Monitoring stopped by user")

    def load_predictor(self) -> bool:
        """Load the trained model only when prediction is explicitly enabled."""
        if not self.prediction_enabled:
            return True

        try:
            from ml.predict import PredictionService

            self.predictor = PredictionService()
            print("ML prediction: enabled")
            logging.info("Prediction service loaded")
            return True
        except FileNotFoundError as error:
            self.error_message = str(error)
            print("ML prediction could not start.")
            print(str(error))
            logging.error("Prediction service failed: %s", error)
            return False

    def handle_packet(self, packet) -> None:
        """Process one packet captured by Scapy."""
        metadata = extract_packet_metadata(packet)
        if metadata is None:
            return

        self.packet_count += 1
        logging.debug("Packet captured: %s", metadata)

        flow, created = self._update_flow(metadata)
        if created:
            logging.info("Flow created: %s", flow.summary())

        if self.packet_count <= 5:
            print(
                f"Packet {self.packet_count}: "
                f"{metadata['source_ip']}:{metadata['source_port']} -> "
                f"{metadata['destination_ip']}:{metadata['destination_port']} "
                f"{metadata['protocol_name']} length={metadata['packet_length']}"
            )

        # Immediate alert detection: check on creation or every 25 packets
        if (created or (flow.total_packets % 25 == 0)) and self.predictor is not None:
            result = self.evaluate_flow(flow)
            if result.get("prediction") == "ATTACK" and not flow.alert_emitted:
                flow.alert_emitted = True
                if self.on_detection is not None:
                    self.on_detection(metadata, flow, result)

        # Periodically prune idle expired flows to bound memory
        if self.packet_count % 20 == 0:
            self.prune_expired_flows(metadata["timestamp"])

    def evaluate_flow(self, flow: Flow) -> dict:
        """Generate prediction for a flow."""
        if self.predictor is None:
            return {"prediction": "PENDING", "confidence": None, "severity": "No alert"}

        try:
            features = flow.to_ml_features()
            logging.debug("Features extracted: %s", features)
            result = self.predictor.predict(features)
            self.prediction_count += 1
            logging.debug("Prediction generated: %s", result)
            return result
        except ValueError as error:
            self.error_message = "Invalid flow features: " + str(error)
            logging.error(self.error_message)
            return {"prediction": "ERROR", "confidence": None, "severity": "No alert"}
        except Exception as error:
            self.error_message = "Prediction error: " + str(error)
            logging.exception(self.error_message)
            return {"prediction": "ERROR", "confidence": None, "severity": "No alert"}

    def finalize_flow(self, flow: Flow, is_final: bool = True) -> None:
        """Predict and notify flow detection to persistent storage."""
        if flow.is_finalized:
            return
        result = self.evaluate_flow(flow)
        if is_final:
            flow.is_finalized = True
        if self.on_detection is not None and flow.last_metadata is not None:
            self.on_detection(flow.last_metadata, flow, result)

    def prune_expired_flows(self, current_time: float) -> None:
        """Finalize and purge flows that have been idle past timeout."""
        expired_keys = [
            k for k, f in self.flows.items()
            if f.is_expired(current_time) and not f.is_finalized
        ]
        for key in expired_keys:
            flow = self.flows[key]
            self.finalize_flow(flow, is_final=True)
            del self.flows[key]

    def finalize_all_flows(self) -> None:
        """Finalize all remaining active flows when capture halts."""
        for flow in list(self.flows.values()):
            if not flow.is_finalized:
                self.finalize_flow(flow, is_final=True)

    def _update_flow(self, metadata: dict) -> tuple[Flow, bool]:
        """Add packet metadata to a forward or reverse flow."""
        flow_key = metadata_to_flow_key(metadata)
        reverse_key = metadata_to_reverse_flow_key(metadata)
        created = False

        if flow_key in self.flows:
            flow = self.flows[flow_key]
        elif reverse_key in self.flows:
            flow = self.flows[reverse_key]
        else:
            flow = Flow(
                metadata["source_ip"],
                metadata["destination_ip"],
                metadata["source_port"],
                metadata["destination_port"],
                metadata["protocol"],
            )
            self.flows[flow_key] = flow
            created = True

        flow.add_packet(
            metadata["timestamp"],
            metadata["source_ip"],
            metadata["source_port"],
            metadata["packet_length"],
            metadata=metadata,
        )
        return flow, created

    def start(self) -> None:
        """Start passive packet capture when explicitly enabled."""
        setup_logging()

        if not self.enabled:
            print("Packet capture is disabled. Use --enabled to start capture explicitly.")
            return

        if not self.load_predictor():
            self.enabled = False
            return

        print("Starting packet capture...")
        print(f"Interface: {self.interface or 'Scapy default interface'}")
        print(f"Duration: {self.duration} seconds")
        print("Payload storage: disabled")
        logging.info("Monitoring started on interface=%s duration=%s", self.interface, self.duration)

        try:
            sniff(
                iface=self.interface or None,
                prn=self.handle_packet,
                timeout=self.duration,
                store=False,
                stop_filter=lambda _: self.stop_event.is_set(),
            )
        except RuntimeError as error:
            if "winpcap is not installed" not in str(error).lower():
                self.error_message = "Scapy capture error: " + str(error)
                logging.error(self.error_message)
                self.enabled = False
                return
            print("Layer 2 capture is unavailable because Npcap/WinPcap is not installed.")
            print("Trying Scapy layer 3 capture fallback for IP packets...")
            try:
                socket = conf.L3socket(iface=self.interface or None)
                try:
                    sniff(
                        opened_socket=socket,
                        prn=self.handle_packet,
                        timeout=self.duration,
                        store=False,
                        stop_filter=lambda _: self.stop_event.is_set(),
                    )
                finally:
                    socket.close()
            except OSError as fallback_error:
                self.error_message = str(fallback_error)
                print("Packet capture could not start on this Windows setup.")
                print("Reason: " + str(fallback_error))
                print("Run as Administrator or install Npcap, then try again.")
                logging.error("Monitoring failed: %s", fallback_error)
                self.enabled = False
                return

        self.finalize_all_flows()
        self.enabled = False
        print("Packet capture completed.")
        print(f"Packets captured: {self.packet_count}")
        print(f"Flows generated: {len(self.flows)}")
        print(f"Predictions generated: {self.prediction_count}")
        logging.info("Monitoring finished packets=%s flows=%s", self.packet_count, len(self.flows))

        if self.flows:
            print("\nSample generated flow features:")
            for index, flow in enumerate(list(self.flows.values())[:5], start=1):
                print(f"Flow {index}: {flow.summary()}")


def list_interfaces() -> None:
    """Print network interfaces detected by Scapy."""
    print("Available Scapy interfaces:")
    for iface in conf.ifaces.values():
        print(f"- {iface.name}")


def get_interface_names() -> list[str]:
    """Return interface names for the Flask dropdown."""
    return [iface.name for iface in conf.ifaces.values()]


def parse_args():
    parser = argparse.ArgumentParser(description="Passive packet capture test for AI-NIDS.")
    parser.add_argument("--enabled", action="store_true", help="Explicitly enable packet capture.")
    parser.add_argument("--predict", action="store_true", help="Load the trained model and predict each updated flow.")
    parser.add_argument("--interface", default=NETWORK_INTERFACE, help="Authorized interface name, for example Wi-Fi.")
    parser.add_argument("--duration", type=int, default=CAPTURE_DURATION, help="Capture duration in seconds.")
    parser.add_argument("--list-interfaces", action="store_true", help="Show Scapy interface names and exit.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_interfaces:
        list_interfaces()
        return

    enabled = bool(args.enabled or PACKET_CAPTURE_ENABLED)
    prediction_enabled = bool(args.predict or PREDICTION_ENABLED)
    capture = PacketCapture(
        interface=args.interface,
        duration=args.duration,
        enabled=enabled,
        prediction_enabled=prediction_enabled,
    )
    capture.start()


if __name__ == "__main__":
    main()

