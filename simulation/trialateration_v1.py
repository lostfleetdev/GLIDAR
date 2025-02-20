import numpy as np
from scipy.optimize import fsolve

def trilateration(node_positions, timestamps, speed_of_sound=343):
    """
    Estimates the sound source location using trilateration.

    Args:
        node_positions (list of list): A list of node positions as [[x1, y1], [x2, y2], [x3, y3]].
        timestamps (list of float): A list of timestamps when each node detected the sound.
        speed_of_sound (float): The speed of sound (default 343 m/s).

    Returns:
        tuple: The estimated sound source position (x, y) and the direction in degrees with respect to (0, 0).
    """
    # Validate inputs
    if len(node_positions) != 3 or len(timestamps) != 3:
        raise ValueError("node_positions and timestamps must each contain exactly three elements.")

    A, B, C = node_positions
    tA, tB, tC = timestamps

    # Calculate time differences and corresponding distance differences
    delta_t_AB = tB - tA
    delta_t_AC = tC - tA
    delta_d_AB = speed_of_sound * delta_t_AB
    delta_d_AC = speed_of_sound * delta_t_AC

    def equations(S):
        """
        System of equations representing distance differences.
        """
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

    # Use the average position of the nodes as the initial guess
    initial_guess = np.mean(node_positions, axis=0)

    try:
        xs, ys = fsolve(equations, initial_guess)

        # Calculate the angle relative to the positive Y-axis (North)
        angle_radians = np.arctan2(xs, ys)  # atan2(x, y) gives the angle from Y-axis
        angle_degrees = np.degrees(angle_radians)

        # Normalize angle to 0-360 degrees
        if angle_degrees < 0:
            angle_degrees += 360

        return (xs, ys), angle_degrees
    except Exception as e:
        print(f"Error solving equations: {e}")
        return None

# Example Usage
if __name__ == "__main__":
    node_positions = [[9, 9], [2, 10], [5, 11]]
    timestamps = [0.200, 0.215, 0.210]

    result = trilateration(node_positions, timestamps)

    if result:
        estimated_location, direction = result
        print(f"Estimated location: {estimated_location}")
        print(f"Direction relative to (0,0) and Y-axis (North): {direction:.2f}°")
    else:
        print("Could not estimate location")
