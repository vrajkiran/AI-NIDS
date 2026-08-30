"""Simple flow aggregation for live packet monitoring.

A flow groups packets that belong to the same network conversation. This module
stores only safe metadata and counters. It does not store packet payloads.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoint:
    """One side of a network conversation."""

    ip: str
    port: int


class Flow:
    """Track simple flow statistics that match selected CICIDS2017 features."""

    def __init__(self, source_ip: str, destination_ip: str, source_port: int, destination_port: int, protocol: int):
        self.source = Endpoint(source_ip, source_port)
        self.destination = Endpoint(destination_ip, destination_port)
        self.protocol = protocol

        self.start_time = None
        self.last_time = None

        self.forward_packet_count = 0
        self.backward_packet_count = 0
        self.forward_byte_count = 0
        self.backward_byte_count = 0

    def matches_reverse(self, source_ip: str, destination_ip: str, source_port: int, destination_port: int, protocol: int) -> bool:
        """Return True if a packet is the reverse direction of this flow."""
        return (
            self.source.ip == destination_ip
            and self.destination.ip == source_ip
            and self.source.port == destination_port
            and self.destination.port == source_port
            and self.protocol == protocol
        )

    def add_packet(self, timestamp: float, source_ip: str, source_port: int, packet_length: int) -> None:
        """Update flow counters using packet metadata only."""
        if self.start_time is None:
            self.start_time = timestamp

        self.last_time = timestamp

        is_forward = source_ip == self.source.ip and source_port == self.source.port
        if is_forward:
            self.forward_packet_count += 1
            self.forward_byte_count += packet_length
        else:
            self.backward_packet_count += 1
            self.backward_byte_count += packet_length

    @property
    def total_packets(self) -> int:
        return self.forward_packet_count + self.backward_packet_count

    @property
    def total_bytes(self) -> int:
        return self.forward_byte_count + self.backward_byte_count

    @property
    def duration_seconds(self) -> float:
        if self.start_time is None or self.last_time is None:
            return 0.0
        return max(self.last_time - self.start_time, 0.0)

    def to_ml_features(self) -> dict:
        """Return live features using the same names selected for ML training."""
        duration_seconds = self.duration_seconds
        duration_microseconds = duration_seconds * 1_000_000
        bytes_per_second = self.total_bytes / duration_seconds if duration_seconds > 0 else 0
        packets_per_second = self.total_packets / duration_seconds if duration_seconds > 0 else 0

        return {
            "Destination Port": self.destination.port,
            "Protocol": self.protocol,
            "Flow Duration": duration_microseconds,
            "Total Fwd Packets": self.forward_packet_count,
            "Total Backward Packets": self.backward_packet_count,
            "Total Length of Fwd Packets": self.forward_byte_count,
            "Total Length of Bwd Packets": self.backward_byte_count,
            "Fwd Packet Length Mean": self.forward_byte_count / self.forward_packet_count if self.forward_packet_count else 0,
            "Bwd Packet Length Mean": self.backward_byte_count / self.backward_packet_count if self.backward_packet_count else 0,
            "Flow Bytes/s": bytes_per_second,
            "Flow Packets/s": packets_per_second,
        }

    def summary(self) -> dict:
        """Return a beginner-friendly flow summary for terminal test mode."""
        features = self.to_ml_features()
        return {
            "source": f"{self.source.ip}:{self.source.port}",
            "destination": f"{self.destination.ip}:{self.destination.port}",
            "protocol": self.protocol,
            "duration_seconds": round(self.duration_seconds, 4),
            "total_packets": self.total_packets,
            "total_bytes": self.total_bytes,
            "avg_packet_size": round(self.total_bytes / self.total_packets, 2) if self.total_packets else 0,
            "packets_per_second": round(features["Flow Packets/s"], 2),
            "bytes_per_second": round(features["Flow Bytes/s"], 2),
            "forward_packets": self.forward_packet_count,
            "backward_packets": self.backward_packet_count,
        }


