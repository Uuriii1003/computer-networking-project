import time
from scapy.all import sr1
from packets import create_probe
from parser import send_and_parse


def traceroute(
    target_ip,
    min_ttl=1,
    max_ttl=30,
    num_series=1,
    timeout=2,
    wait_time=0.5,
    dport=33434,
    packet_size=60
):
    results = []

    print(f"Tracing route to {target_ip}...\n")

    # TTL loop (the staircase)
    for ttl in range(min_ttl, max_ttl + 1):
        print(f"TTL = {ttl}")

        ttl_results = []

        # Series loop
        for series in range(num_series):

            # Protocol loop
            for protocol in ["UDP", "TCP", "ICMP"]:

                # 🔹 Build packet (Person 1)
                packet = create_probe(
                    target_ip,
                    ttl,
                    protocol,
                    dport,
                    packet_size
                )

                # 🔹 Send + measure RTT
                start = time.perf_counter()
                response = sr1(packet, timeout=timeout, verbose=0)
                end = time.perf_counter()

                # RTT in ms
                rtt = (end - start) * 1000

                # 🔹 Parse response (Person 2)
                result = send_and_parse(
                    response=response,
                    protocol=protocol,
                    rtt=rtt,
                    ttl=ttl
                )

                ttl_results.append(result)

                # Print live output (like real traceroute)
                if result["ip"] is None:
                    print(f"  {protocol}: *")
                else:
                    print(f"  {protocol}: {result['ip']} ({result['name']}) - {result['rtt']:.2f} ms")

                # 🔹 Stop if destination reached
                if result["is_destination"]:
                    results.append(ttl_results)
                    print("\n✅ Destination reached!\n")
                    return results

                # 🔹 Wait between packets
                time.sleep(wait_time)

        results.append(ttl_results)

    print("\n⚠️ Max TTL reached without hitting destination.\n")
    return results


# 🚀 Entry point
if __name__ == "__main__":
    target = input("Enter target IP: ")
    results = traceroute(target)

    print("\nFinal Results:")
    for hop in results:
        print(hop)