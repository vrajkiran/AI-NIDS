# Feature Compatibility List

These features were selected because they exist in the downloaded CICIDS2017 machine-learning flow file and can also be calculated later from live packets/flows using Scapy.

| Feature | Meaning | CICIDS2017 availability | Live Scapy calculation possibility |
|---|---|---|---|
| Destination Port | Destination service port used by the flow. | Available | Yes, from TCP/UDP destination port. |
| Flow Duration | Time between the first and latest packet in a flow. | Available | Yes, by saving first and last packet timestamps. |
| Total Fwd Packets | Number of packets in the forward direction. | Available | Yes, by counting packets from source to destination. |
| Total Backward Packets | Number of packets in the reverse direction. | Available | Yes, by counting packets from destination to source. |
| Total Length of Fwd Packets | Total bytes in forward packets. | Available | Yes, by summing forward packet lengths. |
| Total Length of Bwd Packets | Total bytes in backward packets. | Available | Yes, by summing backward packet lengths. |
| Fwd Packet Length Mean | Average size of forward packets. | Available | Yes, total forward bytes divided by forward packet count. |
| Bwd Packet Length Mean | Average size of backward packets. | Available | Yes, total backward bytes divided by backward packet count. |
| Flow Bytes/s | Average bytes transferred per second in a flow. | Available | Yes, total flow bytes divided by flow duration. |
| Flow Packets/s | Average packets transferred per second in a flow. | Available | Yes, total flow packets divided by flow duration. |

Note: Protocol is available from live Scapy packets, but it is not present in the downloaded machine-learning flow file used for this training run, so it is not used by the saved model.
