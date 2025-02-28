from manim import *
import numpy as np

class GraphTransformation(ThreeDScene):
    def construct(self):
        # Configuration
        num_nodes = 8
        node_radius = 0.15
        circle_radius = 2
        
        # Create 2D positions in a circle with slight z-variation
        angles = np.linspace(0, 2*PI, num_nodes)
        positions_2d = [
            [circle_radius*np.cos(angle), circle_radius*np.sin(angle), 0]
            for angle in angles
        ]

        # Create 3D positions using improved distribution
        golden_ratio = (1 + np.sqrt(5)) / 2
        positions_3d = []
        for i in range(num_nodes):
            t = i / num_nodes
            theta = 2 * PI * i * golden_ratio
            phi = np.arccos(1 - 2 * t)
            
            x = circle_radius * np.sin(phi) * np.cos(theta)
            y = circle_radius * np.sin(phi) * np.sin(theta)
            z = circle_radius * np.cos(phi)
            positions_3d.append([x, y, z])

        # Create nodes with better visual style
        nodes = VGroup(*[
            Sphere(radius=node_radius, resolution=(16, 16)).set_color(BLUE).move_to(pos)
            for pos in positions_2d
        ])

        # Create edges with better visual style
        edges = VGroup()
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                edge = Cylinder(
                    radius=0.02,
                    height=np.linalg.norm(
                        np.array(positions_2d[i]) - np.array(positions_2d[j])
                    )
                ).set_color(GRAY_D)
                
                # Position and rotate edge to connect nodes
                start, end = positions_2d[i], positions_2d[j]
                mid = [(s + e) / 2 for s, e in zip(start, end)]
                edge.move_to(mid)
                
                # Calculate rotation axis and angle
                direction = np.array(end) - np.array(start)
                axis = np.cross([0, 0, 1], direction)
                angle = np.arccos(direction[2] / np.linalg.norm(direction))
                if not np.allclose(axis, 0):
                    edge.rotate(angle, axis)
                
                edges.add(edge)

        # Initial setup
        self.set_camera_orientation(phi=0, theta=-90*DEGREES)
        self.renderer.camera.light_source.move_to(3*IN+7*OUT)

        # Fade in the 2D graph with smoother timing
        self.play(
            LaggedStart(*[FadeIn(node) for node in nodes], lag_ratio=0.1),
            run_time=2
        )
        self.play(
            LaggedStart(*[Create(edge) for edge in edges], lag_ratio=0.05),
            run_time=3
        )
        self.wait(0.5)

        # Smooth transition to 3D view with node movement
        node_animations = [node.animate.move_to(pos) for node, pos in zip(nodes, positions_3d)]
        self.move_camera(phi=75*DEGREES, theta=30*DEGREES, run_time=3)
        self.play(*node_animations, run_time=3)
        
        # Update edges smoothly
        edge_animations = []
        edge_count = 0
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                start, end = positions_3d[i], positions_3d[j]
                mid = [(s + e) / 2 for s, e in zip(start, end)]
                
                # Calculate new height and rotation for edge
                new_height = np.linalg.norm(np.array(end) - np.array(start))
                direction = np.array(end) - np.array(start)
                axis = np.cross([0, 0, 1], direction)
                angle = np.arccos(direction[2] / np.linalg.norm(direction))
                
                edge = edges[edge_count]
                edge_animations.append(
                    edge.animate.move_to(mid)
                        .set_height(new_height)
                        .rotate(angle, axis)
                )
                edge_count += 1

        self.play(
            *edge_animations,
            run_time=3
        )

        # Rotate the camera smoothly
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(5)

        # Update camera focal distance using set_camera_orientation
        self.move_camera(focal_distance=5, run_time=2)
        self.wait(3)

        # Stop rotation
        self.stop_ambient_camera_rotation()