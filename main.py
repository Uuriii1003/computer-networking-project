import time
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

    print(f"\nTracing route to {target_ip}...\n")

    # 🔁 TTL loop
    for ttl in range(min_ttl, max_ttl + 1):
        print(f"TTL = {ttl}")
        ttl_results = []

        # 🔁 Series loop
        for _ in range(num_series):

            # 🔁 Protocol loop
            for protocol in ["UDP", "TCP", "ICMP"]:

                # 🛠️ Build packet (Person 1)
                packet = create_probe(
                    target_ip,
                    ttl,
                    protocol,
                    dport,
                    packet_size
                )

                # 📡 Send + parse (Person 2)
                result = send_and_parse(packet, timeout)

                # 🧠 Add orchestrator-controlled fields
                result["ttl"] = ttl
                result["proto"] = protocol

                ttl_results.append(result)

                # 🖨️ Print output
                if result["ip"] == "*":
                    print(f"  {protocol}: *")
                else:
                    print(f"  {protocol}: {result['ip']} ({result['name']}) - {result['rtt']} ms")

                # 🛑 Stop if destination reached
                if result["is_final"]:
                    results.append(ttl_results)
                    print("\n✅ Destination reached!\n")
                    return results

                # ⏱️ Wait between packets
                time.sleep(wait_time)

        results.append(ttl_results)

    print("\n⚠️ Max TTL reached without reaching destination.\n")
    return results


# 🚀 Entry point
if __name__ == "__main__":
    target = input("Enter target IP: ")
    results = traceroute(target)

    print("\n📊 Final Results:")
    for hop in results:
        print(hop)