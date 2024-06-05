import matplotlib.pyplot as plt
import random

def calculate_distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def calculate_density(num_vehicles_within_range, transmission_range):
    area_covered = transmission_range ** 2 * 3.14159  # Assuming circular transmission range
    return num_vehicles_within_range / area_covered

def count_vehicles_within_range(vehicle_positions, reference_vehicle_id, timestamp, transmission_range, expose_percentage):
    total_exposed_nodes = 0
    total_nodes = 0
    if reference_vehicle_id not in vehicle_positions:
        print(f"Error: Reference vehicle '{reference_vehicle_id}' not found in vehicle_positions dictionary.")
        return 0, 0
    
    reference_positions = vehicle_positions[reference_vehicle_id]
    
    if timestamp >= len(reference_positions):
        print(f"Error: Timestamp '{timestamp}' is out of range for reference vehicle '{reference_vehicle_id}'.")
        return 0, 0
    
    x1, y1 = reference_positions[timestamp][1:]
    
    for vehicle_id, positions in vehicle_positions.items():
        if timestamp < len(positions):
            x2, y2 = positions[timestamp][1:]
            distance = calculate_distance(x1, y1, x2, y2)
            if distance <= transmission_range:
                total_nodes += 1
                # Check if the other vehicle becomes an exposed node
                if random.random() < expose_percentage:
                    total_exposed_nodes += 1
        else:
            print(f"Warning: Timestamp '{timestamp}' is out of range for vehicle '{vehicle_id}'. Skipping...")
    
    return total_nodes, total_exposed_nodes

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

def calculate_throughput(total_nodes, total_exposed_nodes):
    if total_nodes == 0:
        return 0
    return (total_nodes - total_exposed_nodes) / total_nodes

# Define the output files and their corresponding number of lanes
output_files = {
    'zigzagoutput.txt': 1,
    'zigzagoutput2.txt': 2,
    'zigzagoutput4.txt': 4
}

# Initialize lists to store throughput data
throughputs_initial_list = []
throughputs_reduced_list = []
num_lanes_list = []

# Iterate over each output file
for output_file, num_lanes in output_files.items():
    # Extract vehicle positions from the output file
    vehicle_positions = extract_vehicle_positions(output_file)
    
    # Choose a reference vehicle and an initial transmission range
    reference_vehicle_id = 'f_0.7'
    initial_transmission_range = 2.5

    # Calculate the density at each timestamp
    timestamps = range(len(vehicle_positions[reference_vehicle_id]))
    total_nodes = 0
    total_exposed_nodes_initial = 0
    total_exposed_nodes_reduced = 0

    # Calculate throughput for each timestamp
    for timestamp in timestamps:
        num_vehicles_initial, num_exposed_initial = count_vehicles_within_range(vehicle_positions, reference_vehicle_id, timestamp, initial_transmission_range, 0.7)
        total_nodes += num_vehicles_initial
        total_exposed_nodes_initial += num_exposed_initial

        density = calculate_density(num_vehicles_initial, initial_transmission_range)
        reduced_transmission_range = initial_transmission_range * (1 - density)
        _, num_exposed_reduced = count_vehicles_within_range(vehicle_positions, reference_vehicle_id, timestamp, reduced_transmission_range, 0.7)
        total_exposed_nodes_reduced += num_exposed_reduced

    # Calculate throughput
    throughput_initial = calculate_throughput(total_nodes, total_exposed_nodes_initial)
    throughput_reduced = calculate_throughput(total_nodes, total_exposed_nodes_reduced)
    
    # Append throughput and number of lanes to the lists
    throughputs_initial_list.append(throughput_initial)
    throughputs_reduced_list.append(throughput_reduced)
    num_lanes_list.append(num_lanes)

# Plot the comparison graph
plt.plot(num_lanes_list, throughputs_initial_list, marker='o', linestyle='-', color='b', label='Initial Transmission Range')
plt.plot(num_lanes_list, throughputs_reduced_list, marker='o', linestyle='-', color='r', label='Reduced Transmission Range')
plt.xlabel('Number of Lanes')
plt.ylabel('Network Efficiency')
plt.title('Comparison of efficiency for Different Number of Lanes')
plt.legend()
plt.grid(True)
plt.show()
