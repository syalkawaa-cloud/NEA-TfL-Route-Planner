import csv
import random

NUM_STATIONS = 100

stations = []
connections = []

# Generate stations
for i in range(1, NUM_STATIONS + 1):
    station_id = f"S{i}"
    name = f"Station {i}"
    
    # 20% stations restrict bikes
    bikes_allowed = "No" if random.random() < 0.2 else "Yes"
    note = "Bicycles restricted at this station." if bikes_allowed == "No" else ""
    
    stations.append((station_id, name, bikes_allowed, note))

# Generate structured connections (chain for guaranteed connectivity)
for i in range(1, NUM_STATIONS):
    travel_time = random.randint(2, 8)
    connections.append((f"S{i}", f"S{i+1}", "LineA", travel_time))

# Add random cross connections
for _ in range(200):
    a = random.randint(1, NUM_STATIONS)
    b = random.randint(1, NUM_STATIONS)
    if a != b:
        travel_time = random.randint(2, 10)
        connections.append((f"S{a}", f"S{b}", "LineX", travel_time))

# Write stations.csv
with open("stations.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["station_id", "name", "bikes_allowed", "notes"])
    writer.writerows(stations)

# Write connections.csv (now includes travel_time)
with open("connections.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["from_station_id", "to_station_id", "line", "travel_time"])
    writer.writerows(connections)

print("100+ station realistic dataset generated successfully.")