class RobotStateMachine:
    def __init__(self):
        self.state = "Green"  # Initial state is Green (Safe)

    def transition(self, distance_to_obstacle, turn_possible):
        if self.state == "Green":
            if distance_to_obstacle <= 0.5:
                self.state = "Red"  # Obstacle critically close
            elif distance_to_obstacle <= 1.5:
                self.state = "Yellow"  # Obstacle detected at caution distance
        
        elif self.state == "Yellow":
            if distance_to_obstacle <= 0.5:
                self.state = "Red"  # Obstacle critically close
            elif distance_to_obstacle > 1.5:
                self.state = "Green"  # Obstacle cleared
            elif turn_possible:
                self.state = "Yellow"  # Continue turning if necessary
        
        elif self.state == "Red":
            if distance_to_obstacle > 1.5:
                self.state = "Green"  # Obstacle cleared
            elif distance_to_obstacle <= 1.5 and turn_possible:
                self.state = "Yellow"  # Transition to Yellow if turning is possible
        
    def perform_action(self):
        if self.state == "Green":
            self.move_forward()
        elif self.state == "Yellow":
            self.continue_turning()
        elif self.state == "Red":
            self.stop()

    def move_forward(self):
        print("Moving forward: Safe zone (Green).")

    def continue_turning(self):
        print("Turning around: Obstacle detected (Yellow).")

    def stop(self):
        print("Stopping: Critical danger (Red).")

# Example usage
robot = RobotStateMachine()

# Simulated sensor readings with distances to obstacle and possibility of turning
readings = [
    (2.0, False),  # Green: Path is clear
    (1.2, True),   # Yellow: Obstacle detected, turning possible
    (0.4, True),   # Red: Obstacle critically close, turning possible
    (0.3, False),  # Red: Obstacle critically close, no turning possible
    (1.7, False),  # Green: Obstacle cleared
]

for distance, turn_possible in readings:
    print(f"\nDistance to obstacle: {distance} meters, Can turn: {turn_possible}")
    robot.transition(distance, turn_possible)
    robot.perform_action()

'''
stateDiagram-v2
    [*] --> Green
    Green --> Green: Path is clear\n**Action: Follow trajectory to desrtination**
    Green --> Yellow: Obstacle detected at precaution distance\n**Action: Turn Around**
    Green --> Black: Obstacle suddenly becomes critically close\n**Action: Stop**

    Yellow --> Yellow: Obstacle still present, adjusting\n**Action: Continue Turning**
    Yellow --> Green: Obstacle cleared\n**Action: Resume Movement**
    Yellow --> Red: Obstacle critically close\n**Action: Stop**

    Black --> Black: Obstacle still critically close\n**Action: Stop**
    Black --> Green: Obstacle cleared\n**Action: Resume Movement**
    Black --> Yellow: Obstacle at caution distance (if turning possible)\n**Action: Turn Around**


    RULES:
    *Inflation layer should have neibour that is an actual obstacle (black)
'''