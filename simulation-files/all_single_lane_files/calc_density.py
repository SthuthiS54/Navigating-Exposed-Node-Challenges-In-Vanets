import matplotlib.pyplot as plt

def calculate_distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def calculate_density(num_vehicles_within_range, transmission_range):
    area_covered = transmission_range ** 2 * 3.14159  # Assuming circular transmission range
    return num_vehicles_within_range / area_covered

def count_vehicles_within_range(vehicle_positions, vehicle_id, timestamp, transmission_range):
    if vehicle_id not in vehicle_positions:
        print(f"Error: Vehicle '{vehicle_id}' not found in vehicle_positions dictionary.")
        return 0
    
    positions = vehicle_positions[vehicle_id]
    
    if timestamp >= len(positions):
        print(f"Error: Timestamp '{timestamp}' is out of range for vehicle '{vehicle_id}'.")
        return 0
    
    x1, y1 = positions[timestamp][1:]
    count = 0
    for other_vehicle_id, other_positions in vehicle_positions.items():
        if other_vehicle_id != vehicle_id:
            if timestamp < len(other_positions):
                x2, y2 = other_positions[timestamp][1:]
                distance = calculate_distance(x1, y1, x2, y2)
                if distance <= transmission_range:
                    count += 1
            else:
                print(f"Warning: Timestamp '{timestamp}' is out of range for vehicle '{other_vehicle_id}'. Skipping...")
    return count

def extract_vehicle_positions(xml_file):
    vehicle_positions = {}

    with open(xml_file, 'r') as f:
        timestep = None
        for line in f:
            if line.strip().startswith('<timestep'):
                timestep = int(float(line.split('time="')[1].split('"')[0]))
            elif line.strip().startswith('<vehicle'):
                vehicle_id = line.split('id="')[1].split('"')[0]
                x = float(line.split('x="')[1].split('"')[0])
                y = float(line.split('y="')[1].split('"')[0])

                if vehicle_id not in vehicle_positions:
                    vehicle_positions[vehicle_id] = []
                vehicle_positions[vehicle_id].append((timestep, x, y))

    return vehicle_positions

# Define the path to the output.txt file
output_file_path = 'zigzagoutput.txt'

# Extract vehicle positions from the output.txt file
vehicle_positions = extract_vehicle_positions(output_file_path)

# Choose a vehicle and a transmission range
vehicle_id = 'f_0.7'
transmission_range = 2.5

# Calculate the density at each timestamp
timestamps = range(len(vehicle_positions[vehicle_id]))
num_vehicles_within_range = [count_vehicles_within_range(vehicle_positions, vehicle_id, timestamp, transmission_range) for timestamp in timestamps]
densities = [calculate_density(num_vehicles, transmission_range) for num_vehicles in num_vehicles_within_range]

# Plot the graph
plt.plot(timestamps, densities, marker='o')
plt.xlabel('Time')
plt.ylabel('Density of vehicle within TR of Node X')
#plt.title(f'Density of Vehicles within Transmission Range of selected vehicele')
plt.grid(True)
plt.show()
