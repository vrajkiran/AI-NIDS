class NetworkTraffic:
    """Simple model-style class for a network traffic row."""

    def __init__(self, source_ip, destination_ip, protocol, packet_count, byte_count, prediction, confidence):
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.protocol = protocol
        self.packet_count = packet_count
        self.byte_count = byte_count
        self.prediction = prediction
        self.confidence = confidence


class Alert:
    """Simple model-style class for an alert row."""

    def __init__(self, source_ip, destination_ip, attack_type, confidence, severity, status="OPEN"):
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.attack_type = attack_type
        self.confidence = confidence
        self.severity = severity
        self.status = status
