from scapy.all import sr1, ICMP, IP, TCP, UDP
import time
import socket

# def send_and_parse(response, protocol, rtt, ttl):
#     if response is None:
#         return {
#             "ip": None,
#             "name": "*",
#             "rtt": 0.0,
#             "is_destination": False
#         }
    
#     sender_ip = 
#     start_time = time.perf_counter()
#     reply = sr1(packet, timeout=timeout_val, verbose=0)
#     end_time = time.perf_counter()
    
#     rtt = (end_time - start_time) * 1000

#     if reply is None:
#         return {"ip": "*", "name": None, "rtt": None, "is_final": False, "type": None}

#     # DNS Lookup
#     # hostname = None
#     # try:
#     #     hostname = socket.gethostbyaddr(reply.src)[0]
#     # except Exception:
#     #     hostname = "Unknown"
#     hostname = "Unknown"
#     try:
#         # gethostbyaddr returns a tuple, we just want the first element
#         hostname = socket.gethostbyaddr(reply.src)[0]
#     except (socket.herror, socket.gaierror, Exception):
#         hostname = "Unknown"

#     # Check if we reached the end
#     # is_final = (reply.src == packet[IP].dst)
#     is_final = False
#     if reply.src == packet[IP].dst:
#         is_final = True
#     elif reply.haslayer(ICMP) and reply[ICMP].type == 3:
#         is_final = True

#     icmp_type = None
#     if reply.haslayer(ICMP):
#         icmp_type = reply[ICMP].type

#     return {
#         "ip": reply.src,
#         "name": hostname,
#         "rtt": round(rtt, 2),
#         "is_final": is_final,
#         # Capture the ICMP type if it exists
#         # "icmp_type": reply[ICMP].type if reply.haslayer(ICMP) else "Other"
#         "icmp_type": icmp_type
#     }

def send_and_parse(response, protocol, rtt, ttl):
    # 1. Handle No Response (Timeout)
    if response is None:
        return {
            "ip": None, 
            "name": "*", 
            "rtt": 0.0, 
            "is_destination": False
        }

    # 2. Get the IP address of the sender
    sender_ip = response.src

    # 3. DNS Lookup (Get the hostname)
    try:
        hostname = socket.gethostbyaddr(sender_ip)[0]
    except (socket.herror, socket.gaierror, Exception):
        hostname = "Unknown"

    # 4. Check if we reached the destination
    # We reached it if the sender's IP matches our target
    # OR if it's an ICMP Port Unreachable (Type 3)
    is_destination = False
    if response.haslayer(IP) and hasattr(response, 'dst_target'):
         if sender_ip == response.dst_target:
             is_destination = True

    if response.haslayer(ICMP):
        # Type 0: Echo Reply (Reached destination via ICMP)
        # Type 3: Port Unreachable (Reached destination via UDP/TCP)
        if response[ICMP].type in [0, 3]:
            is_destination = True
    elif not response.haslayer(ICMP):
        # If we got a direct TCP response (like a SYN/ACK), we are at the destination
        is_destination = True

    return {
        "ip": sender_ip,
        "name": hostname,
        "rtt": rtt,
        "is_destination": is_destination
    }

def get_hostname(ip):
    if ip is None or ip == "*":
        return None
    try:
        # This reaches out to the internet to find the name (e.g., google.com)
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except socket.herror:
        # If no name is found, just return the IP or None
        return "Unknown"
    
if __name__ == "__main__":
    # Create a fake packet (Target Google, TTL 1 to hit your own router)
    from scapy.all import IP, ICMP
    test_packet = IP(src="8.8.8.8")/ICMP(type=0)
    
    test_result = send_and_parse(test_packet, "ICMP", 15.55, 1)
    print(f"Test Result: {test_result}")