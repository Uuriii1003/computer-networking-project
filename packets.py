from scapy.all import IP, UDP, TCP, ICMP, Raw

def create_probe(target, ttl, proto, port, size):
    # Creates the payload based on the requested size
    payload = Raw(load="X" * size) 
    
    # Base IP layer
    ip_layer = IP(dst=target, ttl=ttl)

    if proto.upper() == "TCP":
        # Creating a SYN packet (flags="S")
        return ip_layer / TCP(dport=port, flags="S") / payload
    
    elif proto.upper() == "UDP":
        # Standard UDP datagram
        return ip_layer / UDP(dport=port) / payload
    
    elif proto.upper() == "ICMP":
        # Standard ICMP Echo Request (type 8)
        return ip_layer / ICMP() / payload
    
    else:
        raise ValueError(f"Unsupported protocol: {proto}")
    
probe = create_probe("8.8.8.8", 64, "TCP", 80, 10)
probe.show()