import matplotlib.pyplot as plt
import random

def calculate_distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def calculate_density(num_vehicles_within_range, transmission_range):
    area_covered = transmission_range ** 2 * 3.14159  # Assuming circular transmission range
    return num_vehicles_within_range / area_covered

def count_vehicles_within_range(vehicle_positions, vehicle_id, timestamp, transmission_range, expose_percentage):
    if vehicle_id not in vehicle_positions:
        print(f"Error: Vehicle '{vehicle_id}' not found in vehicle_positions dictionary.")
        return 0, 0
    
    positions = vehicle_positions[vehicle_id]
    
    if timestamp >= len(positions):
        print(f"Error: Timestamp '{timestamp}' is out of range for vehicle '{vehicle_id}'.")
        return 0, 0
    
    x1, y1 = positions[timestamp][1:]
    count = 0
    exposed_count = 0
    for other_vehicle_id, other_positions in vehicle_positions.items():
        if other_vehicle_id != vehicle_id:
            if timestamp < len(other_positions):
                x2, y2 = other_positions[timestamp][1:]
                distance = calculate_distance(x1, y1, x2, y2)
                if distance <= transmission_range:
                    count += 1
                    # Check if the other vehicle becomes an exposed node
                    if random.random() < expose_percentage:
                        exposed_count += 1
            else:
                print(f"Warning: Timestamp '{timestamp}' is out of range for vehicle '{other_vehicle_id}'. Skipping...")
    return count, exposed_count

def extract_vehicle_positions(xml_file):
    vehicle_positions = {}

    with open(xml_file, 'r') as f:
        timestep = None
        for line in f:
            if line.strip().startswith('<timestep'):
                timestep = int(float(line.split('time="')[1].split('"')[0]))
            elif line.strip().startswith('<vehicle'):
                try:
                    vehicle_id = line.split('id="')[1].split('"')[0]
                    x = float(line.split('x="')[1].split('"')[0])
                    y = float(line.split('y="')[1].split('"')[0])

                    if vehicle_id not in vehicle_positions:
                        vehicle_positions[vehicle_id] = []
                    vehicle_positions[vehicle_id].append((timestep, x, y))
                except IndexError:
                    print("Error: Malformed line in the XML file. Skipping...")
                    continue

    return vehicle_positions

# Define the output files and their corresponding number of lanes
output_files = {
    'zigzagoutput.txt': 1,
    'zigzagoutput2.txt': 2,
    'zigzagoutput4.txt': 4
}

# Initialize lists to store data
total_nodes_list = []
total_exposed_nodes_list = []
num_lanes_list = []

# Iterate over each output file
for output_file, num_lanes in output_files.items():
    # Extract vehicle positions from the output file
    vehicle_positions = extract_vehicle_positions(output_file)
    
    # Calculate total number of nodes
    total_nodes = len(vehicle_positions)
    
    # Calculate total number of exposed nodes
    total_exposed_nodes = sum(count_vehicles_within_range(vehicle_positions, vehicle_id, timestamp, 2.5, 0.7)[1] for vehicle_id in vehicle_positions for timestamp in range(len(vehicle_positions[vehicle_id])))
    
    # Ensure total exposed nodes does not exceed total nodes
    total_exposed_nodes = min(total_exposed_nodes, total_nodes)
    
    # Append data to lists
    total_nodes_list.append(total_nodes)
    total_exposed_nodes_list.append(total_exposed_nodes)
    num_lanes_list.append(num_lanes)

# Plot the comparison graph
plt.plot(num_lanes_list, total_nodes_list, marker='o', linestyle='-', color='b', label='Total Nodes')
plt.plot(num_lanes_list, total_exposed_nodes_list, marker='o', linestyle='-', color='r', label='Total Exposed Nodes')
plt.xlabel('Number of Lanes')
plt.ylabel('Number of Nodes')
plt.title('Comparison of Total Nodes and Total Exposed Nodes for Different Number of Lanes')
plt.legend()
plt.grid(True)
plt.show()
