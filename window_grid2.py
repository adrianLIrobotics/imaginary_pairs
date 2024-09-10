import tkinter as tk
from tkinter import filedialog, colorchooser
import json
import os

class GridApp:
    def __init__(self, root, width, height, default_map=None):
        self.root = root
        self.width = width
        self.height = height
        self.cell_size = 10
        self.current_color = "white"  # Default color
        self.robot_color = "orange"  # Robot color
        self.destination_color = "purple"  # Destination color
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.original_colors = [[self.current_color for _ in range(width)] for _ in range(height)]  # Store original colors
        self.robot_start_position = (21, 1)  # Store original robot position
        self.robot_position = self.robot_start_position  # Current robot position
        self.destination_position = (12, 45)  # Initial destination position
        self.trajectory_1 = []  # List for trajectory 1 (red)
        self.trajectory_2 = []  # List for trajectory 2 (blue)
        self.create_widgets()
        self.create_controls()

        # Automatically load the default map if provided
        if default_map and os.path.exists(default_map):
            self.load_grid(default_map)
        else:
            self.place_robot()  # Place the robot if no map is loaded
            self.place_destination()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=self.width*self.cell_size, height=self.height*self.cell_size)
        self.canvas.pack()

        for row in range(self.height):
            for col in range(self.width):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.grid[row][col] = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        
        # Create a label to display color and coordinates
        self.info_label = tk.Label(self.root, text="", bg="white")
        self.info_label.pack()

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save", command=self.save_grid)
        self.file_menu.add_command(label="Load", command=self.load_grid)

        self.color_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Color", menu=self.color_menu)
        self.color_menu.add_command(label="Choose Color", command=self.choose_color)
        self.color_menu.add_command(label="Fill with Green", command=self.fill_with_green)
        self.color_menu.add_command(label="Fill with White", command=self.fill_with_white)

    def reorder_trajectory(self, trajectory):
        def is_adjacent(p1, p2):
            return (p1[0] == p2[0] and abs(p1[1] - p2[1]) == 1) or (p1[1] == p2[1] and abs(p1[0] - p2[0]) == 1)

        # Create adjacency dictionary
        adjacency_dict = {}
        for i, point in enumerate(trajectory):
            adjacency_dict[point] = []
            for j, other_point in enumerate(trajectory):
                if i != j and is_adjacent(point, other_point):
                    adjacency_dict[point].append(other_point)

        # Find the starting point based on adjacency to robot position
        robot_row, robot_col = self.robot_position
        adjacent_cells = [
            (robot_row, robot_col - 1),  # left
            (robot_row, robot_col + 1),  # right
            (robot_row - 1, robot_col),  # up
            (robot_row + 1, robot_col)   # down
        ]
        
        # Filter adjacent cells that are within grid range
        adjacent_cells = [(row, col) for row, col in adjacent_cells if 0 <= row < self.height and 0 <= col < self.width]

        def distance(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        def find_closest_start_index():
            min_dist = float('inf')
            start_index = 0
            for i, point in enumerate(trajectory):
                for adj in adjacent_cells:
                    dist = distance(point, adj)
                    if dist < min_dist:
                        min_dist = dist
                        start_index = i
            return start_index

        start_index = find_closest_start_index()

        # Reorder trajectory starting from the closest point
        ordered_trajectory = trajectory[start_index:] + trajectory[:start_index]

        # Adjust trajectory according to adjacency
        ordered_trajectory_final = []
        used_points = set()
        current_point = ordered_trajectory[0]
        ordered_trajectory_final.append(current_point)
        used_points.add(current_point)

        while len(ordered_trajectory_final) < len(ordered_trajectory):
            next_point = None
            for adj in adjacency_dict[current_point]:
                if adj not in used_points:
                    next_point = adj
                    break
            if next_point:
                ordered_trajectory_final.append(next_point)
                used_points.add(next_point)
                current_point = next_point
            else:
                break

        # Add remaining points if there are any left
        for point in ordered_trajectory:
            if point not in used_points:
                ordered_trajectory_final.append(point)

        return ordered_trajectory_final

    def on_canvas_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= col < self.width and 0 <= row < self.height:
            self.canvas.itemconfig(self.grid[row][col], fill=self.current_color)
            self.original_colors[row][col] = self.current_color  # Save the color change

    def on_mouse_motion(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= col < self.width and 0 <= row < self.height:
            color = self.canvas.itemcget(self.grid[row][col], "fill")
            self.info_label.config(text=f"Coordinates: ({row}, {col}) - Color: {color}")

    def choose_color(self):
        color = colorchooser.askcolor()[1]  # Returns a tuple (color, hex code)
        if color:
            self.current_color = color

    def fill_with_green(self):
        self.fill_grid("green")

    def fill_with_white(self):
        self.fill_grid("white")

    def fill_grid(self, color):
        for row in range(self.height):
            for col in range(self.width):
                self.canvas.itemconfig(self.grid[row][col], fill=color)
                self.original_colors[row][col] = color  # Update original colors

    def save_grid(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            grid_data = [[self.canvas.itemcget(self.grid[row][col], "fill") for col in range(self.width)] for row in range(self.height)]
            with open(filename, 'w') as f:
                json.dump(grid_data, f)
    
    def load_grid(self, filepath=None):
        # If no filepath is provided, ask the user for one
        if not filepath:
            filepath = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        
        if filepath and os.path.exists(filepath):
            with open(filepath, 'r') as f:
                grid_data = json.load(f)
            
            # Clear previous trajectories
            self.trajectory_1 = []
            self.trajectory_2 = []

            for row in range(self.height):
                for col in range(self.width):
                    color = grid_data[row][col]
                    self.canvas.itemconfig(self.grid[row][col], fill=color)
                    self.original_colors[row][col] = color  # Store original colors

                    # Check and store trajectory colors
                    if color == "#ff2600":  # Hex code for red
                        self.trajectory_1.append((row, col))
                    elif color == "#0432ff":  # Hex code for blue
                        self.trajectory_2.append((row, col))

            # Reorder trajectories after loading grid
            self.trajectory_1 = self.reorder_trajectory(self.trajectory_1)
            self.trajectory_2 = self.reorder_trajectory(self.trajectory_2)

            # Place robot and destination after loading grid
            self.place_robot()
            self.place_destination()

    def place_robot(self):
        row, col = self.robot_position
        self.canvas.itemconfig(self.grid[row][col], fill=self.robot_color)

    def place_destination(self):
        row, col = self.destination_position
        self.canvas.itemconfig(self.grid[row][col], fill=self.destination_color)

    def move_robot(self, position):
        row, col = position
        # Check if the new cell is not black (blocked)
        if self.canvas.itemcget(self.grid[row][col], "fill") != "black":
            # Restore the original color of the previous cell
            original_color = self.original_colors[self.robot_position[0]][self.robot_position[1]]
            self.canvas.itemconfig(self.grid[self.robot_position[0]][self.robot_position[1]], fill=original_color)
            
            # Update the robot's position and place it
            self.robot_position = position
            self.place_robot()

    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack()

        up_button = tk.Button(control_frame, text="Up", command=lambda: self.move_robot((self.robot_position[0]-1, self.robot_position[1])) if self.robot_position[0] > 0 else None)
        up_button.grid(row=0, column=1)

        left_button = tk.Button(control_frame, text="Left", command=lambda: self.move_robot((self.robot_position[0], self.robot_position[1]-1)) if self.robot_position[1] > 0 else None)
        left_button.grid(row=1, column=0)

        right_button = tk.Button(control_frame, text="Right", command=lambda: self.move_robot((self.robot_position[0], self.robot_position[1]+1)) if self.robot_position[1] < self.width-1 else None)
        right_button.grid(row=1, column=2)

        down_button = tk.Button(control_frame, text="Down", command=lambda: self.move_robot((self.robot_position[0]+1, self.robot_position[1])) if self.robot_position[0] < self.height-1 else None)
        down_button.grid(row=2, column=1)

        reset_button = tk.Button(control_frame, text="Reset", command=self.reset_robot)
        reset_button.grid(row=3, column=1)

        play_trajectory_1_button = tk.Button(control_frame, text="Play Trajectory 1", command=lambda: self.play_trajectory(self.trajectory_1))
        play_trajectory_1_button.grid(row=4, column=0)

        play_trajectory_2_button = tk.Button(control_frame, text="Play Trajectory 2", command=lambda: self.play_trajectory(self.trajectory_2))
        play_trajectory_2_button.grid(row=4, column=2)

        print_trajectory_1_button = tk.Button(control_frame, text="Print Trajectory 1", command=self.print_trajectory_1)
        print_trajectory_1_button.grid(row=5, column=0)

        print_trajectory_2_button = tk.Button(control_frame, text="Print Trajectory 2", command=self.print_trajectory_2)
        print_trajectory_2_button.grid(row=5, column=2)

    def reset_robot(self):
        self.robot_position = self.robot_start_position
        self.place_robot()

    def play_trajectory(self, trajectory):
        self.current_trajectory = trajectory
        self.trajectory_index = 0
        self.move_next_position()

    def move_next_position(self):
        if self.trajectory_index < len(self.current_trajectory):
            next_position = self.current_trajectory[self.trajectory_index]
            self.move_robot(next_position)
            self.trajectory_index += 1
            self.root.after(500, self.move_next_position)  # Move robot every 500ms

    def print_trajectory_1(self):
        print("Trajectory 1 (Red):")
        for position in self.trajectory_1:
            print(position)

    def print_trajectory_2(self):
        print("Trajectory 2 (Blue):")
        for position in self.trajectory_2:
            print(position)

def main():
    root = tk.Tk()
    root.title("Grid Editor")
    
    # Customize width and height here
    width = 50  # Adjust as needed
    height = 50 # Adjust as needed
    
    app = GridApp(root, width, height, default_map="/Users/adrian/Desktop/traj2.txt")
    root.mainloop()

if __name__ == "__main__":
    main()
