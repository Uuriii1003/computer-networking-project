import time
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from scapy.all import sr1
from packets import create_probe
from parser import send_and_parse

# Permission check
if os.geteuid() != 0:
    print("Error: This script must be run with 'sudo'.")
    sys.exit(1)

def probe_task(target_ip, ttl, protocol, dport, packet_size, timeout):
    """The individual task for one protocol probe."""
    packet = create_probe(target_ip, ttl, protocol, dport, packet_size)
    
    start = time.perf_counter()
    response = sr1(packet, timeout=timeout, verbose=0)
    end = time.perf_counter()
    
    rtt = (end - start) * 1000
    
    result = send_and_parse(response, protocol, rtt, ttl)
    # Ensure metadata is attached for Person 3's UI
    result["protocol"] = protocol
    result["ttl"] = ttl
    return result

def traceroute(target_ip, max_ttl=30, timeout=0.8):
    results = []
    print(f"🚀 Fast-Tracing {target_ip}...")

    for ttl in range(1, max_ttl + 1):
        print(f"TTL {ttl}: Sending UDP, TCP, ICMP simultaneously...")
        
        # SENDS ALL 3 PROTOCOLS AT ONCE
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(probe_task, target_ip, ttl, proto, 33434, 60, timeout)
                for proto in ["UDP", "TCP", "ICMP"]
            ]
            ttl_results = [f.result() for f in futures]

        # Log results to terminal
        ips = [r['ip'] if r['ip'] else '*' for r in ttl_results]
        print(f"  Result: {ips}")

        results.append(ttl_results)

        # Stop if ANY of the three protocols hit the target
        if any(r["is_destination"] for r in ttl_results):
            print(f"✅ Destination reached at hop {ttl}!")
            return results

    return results

if __name__ == "__main__":
    targets_file = "targets.txt"
    if not os.path.exists(targets_file):
        print("❌ targets.txt not found!")
        sys.exit(1)
    
    with open(targets_file, "r") as f:
        targets = [line.strip() for line in f if line.strip()]

    all_data = {}
    for ip in targets:
        try:
            all_data[ip] = traceroute(ip)
        except Exception as e:
            print(f"Error on {ip}: {e}")

    with open("results.json", "w") as f:
        json.dump(all_data, f, indent=4)
    print("\n💾 Results saved to results.json")