from manim import *


class Scene1():
    def construct(self):

        intro = Text("Exibit A : Prototype", font_size=90).set_color_by_gradient("#02AABD","#00CDAC")
        self.play(Write(intro))
        self.play(FadeOut(intro))
        self.wait()

        img = ImageMobject('esp.png')
        img.scale(0.4)
        
        node_big = Circle(radius=1.5)
        node_big.set_fill(BLUE, opacity=0.5)
        node_big.set_stroke(BLUE)
        
        node_small_right = Circle(radius=0.4)
        node_small_right.set_fill(BLUE, opacity=0.5)
        node_small_right.set_stroke(BLUE)
        
        node_small_left = Circle(radius=0.4)
        node_small_left.set_fill(TEAL_E, opacity=0.5)
        node_small_left.set_stroke(TEAL_E)

        node_small_right.shift(3 * RIGHT)
        node_small_left.shift(3 * LEFT)

        # animate last
        self.play(FadeIn(img)) # image appears
        self.wait(2)
        
        node_big.surround(img) # circle around image
        self.play(Create(node_big)) 
        self.play(FadeOut(img)) # image out
        
        node_big_copy = node_big.copy()
        self.play(Transform(node_big, node_small_right), Transform(node_big_copy, node_small_left)) # circle split
        
        node_a = Text("Node A", font_size=20).set_color_by_gradient("#33ccff","#ff00ff") # text over nodes
        node_b = Text("Node B", font_size=20).set_color_by_gradient("#33ccff","#ff00ff")

        node_a.shift(node_small_left.get_center() + UP * 1)
        node_b.shift(node_small_right.get_center() + UP * 1)

        self.play(Write(node_a))
        self.play(Write(node_b)) # write NODE A and NOde B over nodes

        line = Line(node_small_right.get_center(), node_small_left.get_center())
        # print(node_small_right.get_left())
        self.play(Create(line))  # line from node a to nnode b
        self.wait()

        dashed_line_left = DashedLine(
            node_small_left.get_center(),
            node_small_left.get_center() + DOWN * 1
        )
        dashed_line_right = DashedLine(
            node_small_right.get_center(),
            node_small_right.get_center() + DOWN * 1
        )

        brace = DashedLine(dashed_line_left.get_end(), dashed_line_right.get_end()) # dashed line down from nodes

        self.play(create(dashed_line_left), ShowCreationThenDestruction(dashed_line_right), Create(brace)) # dashed line from bove dashed lines
        
        dist = Text("Distance x between nodes", font_size=20)
        dist.shift((dashed_line_left.get_end() + dashed_line_right.get_end())/2 + DOWN *1)
        self.play(Create(dist))
        self.wait(2)



class Scene2():
    def construct(self):
        # Step 1: Display "TDOA" with gradient color
        tdoa_title = Text("TDOA", font_size=50).set_color_by_gradient("#02AABD", "#00CDAC")
        self.play(FadeIn(tdoa_title, scale=1.2))
        self.wait(1)

        # Step 2: Display a small definition of TDOA appearing from below
        tdoa_def = Text("Time Difference of Arrival: The time delay between a sound reaching two sensors", font_size=24)
        tdoa_def.shift(DOWN * 2)
        self.play(tdoa_def.animate.shift(UP * 1.5), run_time=2)
        self.wait(1)

        self.clear()
        # Step 3: Show the two nodes (Right first, then Left)
        node_small_right = Circle(radius=0.4, color=BLUE).shift(3 * RIGHT)
        node_small_left = Circle(radius=0.4, color=TEAL_E).shift(3 * LEFT)

        label_right = Text("Sensor 1", font_size=20).next_to(node_small_right, DOWN)
        label_left = Text("Sensor 2", font_size=20).next_to(node_small_left, DOWN)

        self.play(FadeIn(node_small_right), Write(label_right))
        self.wait(0.5)
        self.play(FadeIn(node_small_left), Write(label_left))
        self.wait(1)

        # Step 4: Show a timer using ValueTracker for smooth update
        time_tracker = ValueTracker(0.00)  # Start at 0 seconds
        timer_display = DecimalNumber(0.00, num_decimal_places=2, font_size=30)
        timer_display.next_to(tdoa_title, DOWN * 1.5)
        timer_display.add_updater(lambda m: m.set_value(time_tracker.get_value()))
        self.add(timer_display)

        # Step 5: Show different timestamps above each sensor
        time_right = DecimalNumber(0.00, num_decimal_places=2, font_size=24).next_to(node_small_right, UP)
        time_left = DecimalNumber(0.00, num_decimal_places=2, font_size=24).next_to(node_small_left, UP)

        self.play(FadeIn(time_right), FadeIn(time_left))

        # Step 6: Show a soundwave moving from right to left with an arrow
        sound_wave = DashedLine(start=node_small_right.get_center(), end=node_small_left.get_center(), color=YELLOW)
        wave_arrow = Arrow(node_small_right.get_center(), node_small_left.get_center(), buff=0.2, color=YELLOW)

        # Animate soundwave traveling & update timer smoothly
        self.play(Create(sound_wave), Create(wave_arrow), 
                  time_tracker.animate.set_value(0.10), 
                  time_right.animate.set_value(0.00),
                  run_time=1)

        self.play(time_tracker.animate.set_value(0.20), 
                  time_left.animate.set_value(0.10),
                  run_time=1)

        self.wait(2)
