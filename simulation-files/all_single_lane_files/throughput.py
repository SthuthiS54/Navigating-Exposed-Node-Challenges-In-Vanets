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

def calculate_throughput(num_exposed_nodes, total_time):
    return (20- num_exposed_nodes)/total_time 

# Define the path to the output.txt file
output_file_path = 'loopa.txt'

# Extract vehicle positions from the output.txt file
vehicle_positions = extract_vehicle_positions(output_file_path)

# Choose a vehicle and an initial transmission range
vehicle_id = 'f_0.7'
initial_transmission_range = 2.5
expose_percentage = 0.2  # 20% of nodes are exposed

# Calculate the density at each timestamp
timestamps = range(len(vehicle_positions[vehicle_id]))
num_exposed_within_range_initial = []
num_exposed_within_range_reduced = []
throughput_initial = []
throughput_reduced = []
total_time = len(timestamps)

for timestamp in timestamps:
    num_vehicles, num_exposed_initial = count_vehicles_within_range(vehicle_positions, vehicle_id, timestamp, initial_transmission_range, expose_percentage)
    num_exposed_within_range_initial.append(num_exposed_initial)

    # Calculate the reduced transmission range based on density
    density = calculate_density(num_vehicles, initial_transmission_range)
    reduced_transmission_range = initial_transmission_range * (1 - density)

    # Calculate the number of vehicles within the reduced transmission range at each timestamp
    num_vehicles_within_reduced_range, num_exposed_reduced = count_vehicles_within_range(vehicle_positions, vehicle_id, timestamp, reduced_transmission_range, expose_percentage)
    num_exposed_within_range_reduced.append(num_exposed_reduced)

# Calculate throughput for both cases
throughput_initial = [calculate_throughput(num_exposed, total_time) for num_exposed in num_exposed_within_range_initial]
throughput_reduced = [calculate_throughput(num_exposed, total_time) for num_exposed in num_exposed_within_range_reduced]

# Plot the throughput comparison
plt.plot(timestamps, throughput_initial, marker='o', label='Throughput with Initial Transmission Range')
plt.plot(timestamps, throughput_reduced, marker='o', label='Throughput with Reduced Transmission Range')
plt.xlabel('Time')
plt.ylabel('Throughput')
plt.legend()
plt.grid(True)
plt.show()
