import socket
from scapy.all import IP, ICMP

def send_and_parse(response, protocol, rtt, ttl):
    if response is None:
        return {"ip": None, "name": "*", "rtt": 0.0, "is_destination": False}

    sender_ip = response.src
    
    # DNS Lookup with a fallback
    try:
        # socket.gethostbyaddr is what finds the "name" (e.g., google.com)
        hostname = socket.gethostbyaddr(sender_ip)[0]
    except:
        # If no name is found, use the IP as the name so the UI isn't empty
        hostname = f"Hop-{sender_ip}"

    is_destination = False
    if response.haslayer(ICMP):
        if response[ICMP].type in [0, 3]:
            is_destination = True
    else:
        is_destination = True

    return {
        "ip": sender_ip,
        "name": hostname,
        "rtt": round(rtt, 2),
        "is_destination": is_destination,
        "protocol": protocol,
        "ttl": ttl
    }