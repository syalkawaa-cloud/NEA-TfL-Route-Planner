import csv
import heapq
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")

# If the script is not inside a project folder with ../data, fall back to current folder.
def resolve_path(filename):
    project_data_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(project_data_path):
        return project_data_path
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def load_stations(path):
    stations = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stations[row["station_id"]] = {
                "name": row["name"],
                "bikes_allowed": row["bikes_allowed"],
                "notes": row["notes"]
            }
    return stations


def load_graph(path):
    graph = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start = row["from_station_id"]
            end = row["to_station_id"]
            time = int(row["travel_time"])
            graph.setdefault(start, []).append((end, time))
            graph.setdefault(end, []).append((start, time))
    return graph


def dijkstra(graph, start, goal):
    queue = [(0, start, [])]
    visited = set()

    while queue:
        cost, current, path = heapq.heappop(queue)

        if current in visited:
            continue

        visited.add(current)
        path = path + [current]

        if current == goal:
            return path, cost

        for neighbour, weight in graph.get(current, []):
            if neighbour not in visited:
                heapq.heappush(queue, (cost + weight, neighbour, path))

    return None, None


def check_bike_route(path, stations):
    restricted = []
    for station_id in path:
        if stations[station_id]["bikes_allowed"] == "No":
            restricted.append(stations[station_id]["name"])
    return restricted


def run_tests():
    stations = load_stations(resolve_path("stations.csv"))
    graph = load_graph(resolve_path("connections.csv"))

    test_cases = [
        ("S1", "S10", "Valid route calculation"),
        ("S3", "S20", "Longer route calculation"),
        ("S5", "S15", "Bicycle validation check"),
        ("S2", "S25", "Alternative network section")
    ]

    for start, end, description in test_cases:
        print("-" * 60)
        print(f"Test: {description}")
        print(f"Input: {start} to {end}")

        path, total_time = dijkstra(graph, start, end)

        if path is None:
            print("Result: No route found")
            continue

        print("Route:", " -> ".join(path))
        print(f"Total travel time: {total_time} minutes")

        restricted_stations = check_bike_route(path, stations)

        if restricted_stations:
            print("Bike allowed: NO")
            print("Restricted station(s):", ", ".join(restricted_stations))
        else:
            print("Bike allowed: YES")


if __name__ == "__main__":
    run_tests()
