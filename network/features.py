"""Packet metadata and live feature extraction helpers.

Only safe packet metadata is extracted. Raw payload data is never stored.
"""

from __future__ import annotations

from datetime import datetime

from scapy.layers.inet import ICMP, IP, TCP, UDP

PROTOCOL_NAMES = {
    1: "ICMP",
    6: "TCP",
    17: "UDP",
}


def extract_packet_metadata(packet) -> dict | None:
    """Extract safe metadata from one Scapy packet.

    Returns None for non-IP packets because the selected ML features are based
    on IP traffic flows.
    """
    if IP not in packet:
        return None

    ip_layer = packet[IP]
    protocol_number = int(ip_layer.proto)
    source_port = 0
    destination_port = 0

    if TCP in packet:
        source_port = int(packet[TCP].sport)
        destination_port = int(packet[TCP].dport)
    elif UDP in packet:
        source_port = int(packet[UDP].sport)
        destination_port = int(packet[UDP].dport)
    elif ICMP in packet:
        source_port = 0
        destination_port = 0

    timestamp = float(packet.time)

    return {
        "timestamp": timestamp,
        "time_text": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        "source_ip": ip_layer.src,
        "destination_ip": ip_layer.dst,
        "source_port": source_port,
        "destination_port": destination_port,
        "protocol": protocol_number,
        "protocol_name": PROTOCOL_NAMES.get(protocol_number, str(protocol_number)),
        "packet_length": len(packet),
    }


def metadata_to_flow_key(metadata: dict) -> tuple:
    """Create a normal 5-tuple key from packet metadata."""
    return (
        metadata["source_ip"],
        metadata["destination_ip"],
        metadata["source_port"],
        metadata["destination_port"],
        metadata["protocol"],
    )


def metadata_to_reverse_flow_key(metadata: dict) -> tuple:
    """Create the reverse 5-tuple key for bidirectional flow matching."""
    return (
        metadata["destination_ip"],
        metadata["source_ip"],
        metadata["destination_port"],
        metadata["source_port"],
        metadata["protocol"],
    )
