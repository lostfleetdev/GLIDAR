from manim import *
import numpy as np

class DynamicGraphTransformation(ThreeDScene):
    def construct(self):
        # Configuration
        num_nodes = 8
        node_radius = 0.15
        circle_radius = 3

        # Initial 2D positions (random but balanced distribution)
        np.random.seed(42)  # For reproducibility
        positions_2d = []
        for i in range(num_nodes):
            angle = i * (2 * PI / num_nodes) + np.random.uniform(-0.3, 0.3)
            radius = circle_radius * (0.7 + 0.3 * np.random.random())
            positions_2d.append([
                radius * np.cos(angle),
                radius * np.sin(angle),
                0
            ])

        # 3D positions using spherical coordinates with golden ratio
        golden_ratio = (1 + np.sqrt(5)) / 2
        positions_3d = []
        for i in range(num_nodes):
            t = i / num_nodes
            theta = 2 * PI * i * golden_ratio
            phi = np.arccos(1 - 2 * t)
            radius = circle_radius * (0.7 + 0.3 * np.random.random())
            
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)
            positions_3d.append([x, y, z])

        # Create initial two nodes and connect them
        first_node = Sphere(radius=node_radius, resolution=(16, 16)).set_color(BLUE)
        second_node = Sphere(radius=node_radius, resolution=(16, 16)).set_color(BLUE)
        
        first_node.move_to(positions_2d[0])
        second_node.move_to(positions_2d[1])

        initial_edge = Cylinder(
            radius=0.02,
            height=np.linalg.norm(
                np.array(positions_2d[1]) - np.array(positions_2d[0])
            )
        ).set_color(GRAY_D)

        # Position the initial edge
        mid = [(a + b) / 2 for a, b in zip(positions_2d[0], positions_2d[1])]
        initial_edge.move_to(mid)
        direction = np.array(positions_2d[1]) - np.array(positions_2d[0])
        axis = np.cross([0, 0, 1], direction)
        angle = np.arccos(direction[2] / np.linalg.norm(direction))
        if not np.allclose(axis, 0):
            initial_edge.rotate(angle, axis)

        # Lists to store all nodes and edges
        nodes = VGroup(first_node, second_node)
        edges = VGroup(initial_edge)

        # Initial camera setup
        self.set_camera_orientation(phi=0, theta=-90*DEGREES)
        self.renderer.camera.light_source.move_to(3*IN+7*OUT)

        # Step 1: Create first two nodes and connect them
        self.play(Create(first_node))
        self.play(Create(second_node))
        self.play(Create(initial_edge))
        self.wait(0.5)

        # Step 2: Create remaining nodes and edges in 2D
        remaining_nodes = VGroup(*[
            Sphere(radius=node_radius, resolution=(16, 16))
            .set_color(BLUE)
            .move_to(pos)
            for pos in positions_2d[2:]
        ])

        # Add remaining nodes with pop effect
        self.play(
            LaggedStart(*[
                AnimationGroup(
                    FadeIn(node, scale=0.1),
                    Flash(node.get_center(), color=BLUE, flash_radius=0.3),
                )
                for node in remaining_nodes
            ], lag_ratio=0.2),
            run_time=3
        )
        nodes.add(*remaining_nodes)

        # Create edges for all connections
        new_edges = VGroup()
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if i == 0 and j == 1:  # Skip the initial edge
                    continue
                    
                start, end = positions_2d[i], positions_2d[j]
                edge = Cylinder(
                    radius=0.02,
                    height=np.linalg.norm(np.array(end) - np.array(start))
                ).set_color(GRAY_D)
                
                mid = [(s + e) / 2 for s, e in zip(start, end)]
                edge.move_to(mid)
                
                direction = np.array(end) - np.array(start)
                axis = np.cross([0, 0, 1], direction)
                angle = np.arccos(direction[2] / np.linalg.norm(direction))
                if not np.allclose(axis, 0):
                    edge.rotate(angle, axis)
                
                new_edges.add(edge)

        # Add remaining edges with fade effect
        self.play(
            LaggedStart(*[
                Create(edge) for edge in new_edges
            ], lag_ratio=0.05),
            run_time=3
        )
        edges.add(*new_edges)

        self.wait(0.5)

        # Step 3: Transform to 3D view
        self.move_camera(phi=75*DEGREES, theta=30*DEGREES, run_time=2)
        
        # Create z-axis movement animations
        node_animations = []
        for node, end_pos in zip(nodes, positions_3d):
            node_animations.append(
                node.animate.move_to(end_pos)
            )

        # Update edges during the transformation
        edge_animations = []
        edge_idx = 0
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                start, end = positions_3d[i], positions_3d[j]
                edge = edges[edge_idx]
                
                new_height = np.linalg.norm(np.array(end) - np.array(start))
                mid = [(s + e) / 2 for s, e in zip(start, end)]
                
                direction = np.array(end) - np.array(start)
                axis = np.cross([0, 0, 1], direction)
                angle = np.arccos(direction[2] / np.linalg.norm(direction))
                
                edge_animations.append(
                    edge.animate.move_to(mid)
                        .set_height(new_height)
                        .rotate(angle, axis)
                )
                edge_idx += 1

        # Play 3D transformation
        self.play(
            *node_animations,
            *edge_animations,
            run_time=3
        )

        # Add some dynamic movement
        self.begin_ambient_camera_rotation(rate=0.15)
        
        # Create some oscillating movement in 3D
        def oscillate_position(pos, t):
            return [
                pos[0] + 0.2 * np.sin(t + pos[1]),
                pos[1] + 0.2 * np.cos(t + pos[0]),
                pos[2] + 0.2 * np.sin(t + pos[2])
            ]

        # Animate nodes moving in 3D space
        for t in range(2):
            new_positions = [oscillate_position(pos, t * PI) for pos in positions_3d]
            
            node_animations = [
                node.animate.move_to(pos)
                for node, pos in zip(nodes, new_positions)
            ]
            
            edge_animations = []
            edge_idx = 0
            for i in range(num_nodes):
                for j in range(i + 1, num_nodes):
                    start, end = new_positions[i], new_positions[j]
                    edge = edges[edge_idx]
                    
                    new_height = np.linalg.norm(np.array(end) - np.array(start))
                    mid = [(s + e) / 2 for s, e in zip(start, end)]
                    
                    direction = np.array(end) - np.array(start)
                    axis = np.cross([0, 0, 1], direction)
                    angle = np.arccos(direction[2] / np.linalg.norm(direction))
                    
                    edge_animations.append(
                        edge.animate.move_to(mid)
                            .set_height(new_height)
                            .rotate(angle, axis)
                    )
                    edge_idx += 1
            
            self.play(
                *node_animations,
                *edge_animations,
                run_time=2,
                rate_func=smooth
            )

        self.wait(2)
        self.stop_ambient_camera_rotation()