import numpy as np
import matplotlib.pyplot as plt

class Vehicle:
    def __init__(self, position, speed, transmission_range, power_level):
        self.position = position
        self.speed = speed
        self.transmission_range = transmission_range
        self.power_level = power_level

def load_positions(filename):
    positions = []
    with open(filename, 'r') as file:
        for line in file:
            positions.append(int(line.strip()))
    return positions

def initialize_road(length, density):
    road = np.zeros(length)
    num_vehicles = int(length * density)
    positions = load_positions('loopa.txt')
    for i in range(num_vehicles):
        position = positions[i]
        road[position] = 1
    return road

def update_vehicle_position(vehicle, road):
    new_position = (vehicle.position + vehicle.speed) % len(road)
    road[vehicle.position] = 0
    vehicle.position = new_position
    road[vehicle.position] = 1

def calculate_density(reference_vehicle, vehicles):
    num_nodes_in_range = 0
    for vehicle in vehicles:
        distance = abs(vehicle.position - reference_vehicle.position)
        if distance <= reference_vehicle.transmission_range:
            num_nodes_in_range += 1
    return num_nodes_in_range / len(vehicles)

def adjust_transmission_range(transmission_range, density, max_density):
    return transmission_range * (density / max_density)

def check_communication(vehicle, reference_vehicle):
    distance = abs(vehicle.position - reference_vehicle.position)
    if distance <= reference_vehicle.transmission_range:
        return True
    return False

def count_exposed_nodes(reference_vehicle, vehicles):
    exposed_nodes = 0
    for vehicle in vehicles:
        if not check_communication(vehicle, reference_vehicle):
            exposed_nodes += 1
    return exposed_nodes

def run_simulation(road, vehicles, time_steps, reference_vehicle, initial_transmission_range):
    initial_exposed_nodes = []
    final_exposed_nodes = []
    max_density = 0.5  # Maximum density for normalization
    for t in range(time_steps):
        density = calculate_density(reference_vehicle, vehicles)
        if t == time_steps // 2:
            reference_vehicle.transmission_range = adjust_transmission_range(initial_transmission_range, density, max_density)
        initial_exposed_nodes.append(count_exposed_nodes(reference_vehicle, vehicles))
        for vehicle in vehicles:
            update_vehicle_position(vehicle, road)
        final_exposed_nodes.append(count_exposed_nodes(reference_vehicle, vehicles))
    return initial_exposed_nodes, final_exposed_nodes

def plot_exposed_nodes(initial_exposed_nodes, final_exposed_nodes):
    plt.plot(range(len(initial_exposed_nodes)), initial_exposed_nodes, label='Initial Exposed Nodes')
    plt.plot(range(len(final_exposed_nodes)), final_exposed_nodes, label='Final Exposed Nodes')
    plt.xlabel('Time Slots')
    plt.ylabel('Number of Exposed Nodes')
    plt.title('Exposed Nodes with Modified Transmission Range')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    road_length = 100
    vehicle_density = 0.2
    num_vehicles = 20
    initial_transmission_range = 10
    power_level = 1
    time_steps = 50
    
    road = initialize_road(road_length, vehicle_density)
    reference_vehicle_position = 0  # Assuming the reference vehicle is at the beginning of the road
    reference_vehicle = Vehicle(reference_vehicle_position, 1, initial_transmission_range, power_level)
    vehicles = [Vehicle(position, 1, initial_transmission_range, power_level) for position, cell in enumerate(road) if cell == 1][:num_vehicles]
    
    initial_exposed_nodes, final_exposed_nodes = run_simulation(road, vehicles, time_steps, reference_vehicle, initial_transmission_range)
    plot_exposed_nodes(initial_exposed_nodes, final_exposed_nodes)

if __name__ == "__main__":
    main()
