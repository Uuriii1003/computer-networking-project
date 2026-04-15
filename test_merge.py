# import packets  # Person 1's code
# import parser   # Your code

# # Generate a packet using Person 1's logic
# # (Assuming their function is named create_probe)
# pkt = packets.create_probe(target="8.8.8.8", ttl=1, proto="ICMP")

# # Parse it using your logic
# result = parser.send_and_parse(pkt, timeout_val=2)

# print(f"Integration Result: {result}")


# # What Person 3 is doing right now:
# import packets
# import parser

# target = "8.8.8.8"
# for hop in range(1, 31):
#     # Uses Person 1's code
#     pkt = packets.create_probe(target, ttl=hop) 
    
#     # Uses YOUR code
#     data = parser.send_and_parse(pkt, timeout=2) 
    
#     print(f"{hop}: {data['ip']} ({data['rtt']} ms)")
    
#     if data['is_final']:
#         print("Reached the end!")
#         break

import packets
import parser

target = "8.8.8.8"
hop = 1

print(f"--- Merged Test: Probing {target} ---")

# We have to provide proto, port, and size because 
# they aren't 'optional' in packets.py yet.
pkt = packets.create_probe(target, hop, "ICMP", 33434, 32)

result = parser.send_and_parse(pkt, 2)

print(f"Success! Reached: {result['ip']}")
print(f"Name: {result['name']}")
print(f"RTT: {result['rtt']}ms")