import csv
import heapq
import tkinter as tk
from tkinter import ttk


# -------------------------
# LOAD DATA
# -------------------------

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
            a = row["from_station_id"]
            b = row["to_station_id"]
            time = int(row["travel_time"])

            graph.setdefault(a, []).append((b, time))
            graph.setdefault(b, []).append((a, time))
    return graph


# -------------------------
# DIJKSTRA (Weighted Routing)
# -------------------------

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

        for neighbor, weight in graph.get(current, []):
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path))

    return None, None


# -------------------------
# APPLICATION LOGIC
# -------------------------

stations = load_stations("../data/stations.csv")
graph = load_graph("../data/connections.csv")

id_to_name = {sid: stations[sid]["name"] for sid in stations}
name_to_id = {stations[sid]["name"]: sid for sid in stations}
station_names = sorted(name_to_id.keys())


def check_route():
    output_text.delete("1.0", tk.END)

    start_name = start_var.get()
    end_name = end_var.get()

    if not start_name or not end_name:
        show_error("Please select both stations.")
        return

    if start_name == end_name:
        show_error("Start and destination must be different.")
        return

    start_id = name_to_id[start_name]
    end_id = name_to_id[end_name]

    path, total_time = dijkstra(graph, start_id, end_id)

    if not path:
        show_error("No route found.")
        return

    # Bike restriction check
    if bike_var.get():
        for sid in path:
            if stations[sid]["bikes_allowed"] == "No":
                alt_path, alt_time = find_bike_friendly_route(graph, stations, start_id, end_id)

                if alt_path:
                    show_alternative_route(path, total_time, alt_path, alt_time, sid)
                    return
                else:
                    show_blocked(path, total_time, sid)
                    return

    show_success(path, total_time)

def show_alternative_route(original_path, original_time, alt_path, alt_time, blocked_sid):
    output_text.insert(tk.END, "BIKE RESTRICTION DETECTED\n", "title")
    output_text.insert(tk.END, "-" * 45 + "\n\n")

    blocked_name = stations[blocked_sid]["name"]
    output_text.insert(tk.END, f"Original route blocked at: {blocked_name}\n\n", "error")

    output_text.insert(tk.END, "Alternative Bike-Friendly Route:\n\n", "success")
    output_text.insert(tk.END, f"Estimated Travel Time: {alt_time} minutes\n\n")

    for i, sid in enumerate(alt_path, 1):
        output_text.insert(tk.END, f"{i}. {id_to_name[sid]}\n")
        
def show_success(path, total_time):
    output_text.insert(tk.END, "ROUTE FOUND\n", "title")
    output_text.insert(tk.END, "-" * 45 + "\n\n")

    output_text.insert(tk.END, f"Estimated Travel Time: {total_time} minutes\n\n", "info")

    if bike_var.get():
        output_text.insert(tk.END, "Bike Allowed: YES\n\n", "success")
    else:
        output_text.insert(tk.END, "Bike Mode: OFF\n\n", "info")

    for i, sid in enumerate(path, 1):
        output_text.insert(tk.END, f"{i}. {id_to_name[sid]}\n")


def show_blocked(path, total_time, blocked_sid):
    output_text.insert(tk.END, "ROUTE FOUND (NOT BIKE FRIENDLY)\n", "title")
    output_text.insert(tk.END, "-" * 45 + "\n\n")

    blocked_name = stations[blocked_sid]["name"]

    output_text.insert(tk.END, f"Estimated Travel Time: {total_time} minutes\n\n", "info")
    output_text.insert(tk.END, f"Blocked at: {blocked_name}\n", "error")

    note = stations[blocked_sid]["notes"]
    if note:
        output_text.insert(tk.END, f"Reason: {note}\n\n")

    output_text.insert(tk.END, "Proposed Route:\n\n")

    for i, sid in enumerate(path, 1):
        output_text.insert(tk.END, f"{i}. {id_to_name[sid]}\n")


def show_error(message):
    output_text.insert(tk.END, "ERROR\n", "title")
    output_text.insert(tk.END, "-" * 45 + "\n\n")
    output_text.insert(tk.END, message + "\n", "error")


def find_bike_friendly_route(graph, stations, start, end):
    filtered_graph = {}

    for station in graph:
        if stations[station]["bikes_allowed"] == "No":
            continue

        filtered_graph[station] = []

        for neighbor, time in graph[station]:
            if stations[neighbor]["bikes_allowed"] == "Yes":
                filtered_graph[station].append((neighbor, time))

    return dijkstra(filtered_graph, start, end)

# -------------------------
# GUI SETUP
# -------------------------

root = tk.Tk()
root.title("Cycle + TfL Route Planner")
root.geometry("900x600")
root.resizable(False, False)

style = ttk.Style()
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10))
style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

header = ttk.Label(main_frame, text="Cycle + TfL Bike Route Planner", style="Header.TLabel")
header.pack(pady=(0, 20))

form_frame = ttk.Frame(main_frame)
form_frame.pack(fill="x", pady=(0, 15))

start_var = tk.StringVar()
end_var = tk.StringVar()
bike_var = tk.BooleanVar(value=True)

ttk.Label(form_frame, text="Start Station").grid(row=0, column=0, sticky="w")
ttk.Label(form_frame, text="Destination Station").grid(row=0, column=1, sticky="w")

start_box = ttk.Combobox(form_frame, textvariable=start_var, values=station_names, width=45, state="readonly")
end_box = ttk.Combobox(form_frame, textvariable=end_var, values=station_names, width=45, state="readonly")

start_box.grid(row=1, column=0, padx=5, pady=5)
end_box.grid(row=1, column=1, padx=5, pady=5)

ttk.Checkbutton(main_frame, text="Travelling with a bicycle", variable=bike_var).pack(anchor="w")

ttk.Button(main_frame, text="Calculate Route", command=check_route).pack(pady=10)

output_frame = ttk.Frame(main_frame)
output_frame.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(output_frame)
scrollbar.pack(side="right", fill="y")

output_text = tk.Text(
    output_frame,
    wrap="word",
    font=("Consolas", 11),
    yscrollcommand=scrollbar.set
)

output_text.pack(fill="both", expand=True)
scrollbar.config(command=output_text.yview)

# Text styling
output_text.tag_config("title", font=("Segoe UI", 13, "bold"))
output_text.tag_config("success", foreground="green")
output_text.tag_config("error", foreground="red")
output_text.tag_config("info", foreground="blue")

root.mainloop()