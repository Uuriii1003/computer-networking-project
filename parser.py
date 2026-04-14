from scapy.all import sr1, ICMP, IP, TCP, UDP
import time
import socket

def send_and_parse(packet, timeout_val):
    start_time = time.perf_counter()
    reply = sr1(packet, timeout=timeout_val, verbose=0)
    end_time = time.perf_counter()
    
    rtt = (end_time - start_time) * 1000

    if reply is None:
        return {"ip": "*", "name": None, "rtt": None, "is_final": False, "type": None}

    # DNS Lookup
    # hostname = None
    # try:
    #     hostname = socket.gethostbyaddr(reply.src)[0]
    # except Exception:
    #     hostname = "Unknown"
    hostname = "Unknown"
    try:
        # gethostbyaddr returns a tuple, we just want the first element
        hostname = socket.gethostbyaddr(reply.src)[0]
    except (socket.herror, socket.gaierror, Exception):
        hostname = "Unknown"

    # Check if we reached the end
    # is_final = (reply.src == packet[IP].dst)
    is_final = False
    if reply.src == packet[IP].dst:
        is_final = True
    elif reply.haslayer(ICMP) and reply[ICMP].type == 3:
        is_final = True

    icmp_type = None
    if reply.haslayer(ICMP):
        icmp_type = reply[ICMP].type

    return {
        "ip": reply.src,
        "name": hostname,
        "rtt": round(rtt, 2),
        "is_final": is_final,
        # Capture the ICMP type if it exists
        # "icmp_type": reply[ICMP].type if reply.haslayer(ICMP) else "Other"
        "icmp_type": icmp_type
    }

def get_hostname(ip):
    if ip == "*":
        return None
    try:
        # This reaches out to the internet to find the name (e.g., google.com)
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except socket.herror:
        # If no name is found, just return the IP or None
        return None
    
if __name__ == "__main__":
    # Create a fake packet (Target Google, TTL 1 to hit your own router)
    from scapy.all import IP, ICMP
    test_packet = IP(dst="8.8.8.8", ttl=1)/ICMP()
    
    print("Testing parser...")
    print(send_and_parse(test_packet, 2))