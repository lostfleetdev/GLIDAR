import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.optimize import fsolve

# Node positions and initial parameters
node_positions = np.array([[4, 4], [3, 7], [2, 6]])  # Example positions
speed_of_sound = 343  # m/s
initial_bullet_position = np.array([0, 0, 0])  # Bullet starts at origin
bullet_direction = np.array([1, 0.5, 0])  # Bullet moves diagonally
bullet_direction = bullet_direction / np.linalg.norm(bullet_direction)  # Normalize
time_factor = 0.1  # Speed scaling for animation
time_stamps = []  # To store detection timestamps

# Function to calculate distance between two points
def distance(point1, point2):
    return np.linalg.norm(np.array(point2) - np.array(point1))

# Function to perform trilateration
def trilateration(node_positions, timestamps, speed_of_sound=343):
    A, B, C = node_positions
    tA, tB, tC = timestamps
    delta_t_AB = tB - tA
    delta_t_AC = tC - tA
    delta_d_AB = speed_of_sound * delta_t_AB
    delta_d_AC = speed_of_sound * delta_t_AC

    def equations(S):
        xs, ys = S
        eq1 = (
            np.sqrt((xs - A[0])**2 + (ys - A[1])**2) -
            np.sqrt((xs - B[0])**2 + (ys - B[1])**2) -
            delta_d_AB
        )
        eq2 = (
            np.sqrt((xs - A[0])**2 + (ys - A[1])**2) -
            np.sqrt((xs - C[0])**2 + (ys - C[1])**2) -
            delta_d_AC
        )
        return [eq1, eq2]

    initial_guess = np.mean(node_positions, axis=0)
    try:
        xs, ys = fsolve(equations, initial_guess)
        return xs, ys
    except Exception as e:
        print(f"Error during trilateration: {e}")
        return None

# Create figure and axes
fig, ax = plt.subplots()
ax.set_xlim(-5, 20)
ax.set_ylim(-5, 20)
ax.set_aspect('equal', adjustable='box')

# Plot nodes
node_plots, = ax.plot(node_positions[:, 0], node_positions[:, 1], 'bo', label='GLM Nodes')
bullet_plot, = ax.plot([], [], 'ro', label='Bullet')
estimated_location_plot, = ax.plot([], [], 'g*', label='Estimated Location')

# Function for updating the animation
def update(frame):
    global time_stamps
    t = frame * time_factor
    current_bullet_position = initial_bullet_position + (bullet_direction * t)
    bullet_2d_position = current_bullet_position[:2]  # Extract 2D coordinates

    # Ensure bullet_2d_position is a sequence
    if len(bullet_2d_position) != 2 or not isinstance(bullet_2d_position, (np.ndarray, list, tuple)):
        print(f"Invalid bullet_2d_position: {bullet_2d_position}")
        return bullet_plot, estimated_location_plot

    # Update bullet position
    bullet_plot.set_data(bullet_2d_position[0], bullet_2d_position[1])

    # Check for detection
    for i, node_pos in enumerate(node_positions):
        dist = distance(bullet_2d_position, node_pos)
        if dist < 3:  # Simulate detection within a threshold distance
            if len(time_stamps) < 3 and all(ts[0] != i for ts in time_stamps):
                time_stamps.append((i, t + np.random.normal(0, 0.001)))  # Add timestamp with noise

    # Perform trilateration when all nodes have detected
    if len(time_stamps) == 3:
        sorted_stamps = sorted(time_stamps, key=lambda x: x[0])
        detection_times = [ts[1] for ts in sorted_stamps]

        estimated_location = trilateration(node_positions, detection_times)
        if estimated_location:
            estimated_location_plot.set_data(estimated_location[0], estimated_location[1])

    return bullet_plot, estimated_location_plot

# Create animation
ani = animation.FuncAnimation(fig, update, frames=200, repeat=False)
ax.legend(loc='upper left')
plt.show()
