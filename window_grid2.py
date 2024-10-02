import tkinter as tk
from tkinter import filedialog, colorchooser
import json
import os
import heapq

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

        # Dropdown for policy selection
        self.create_policy_dropdown()

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

            try: 
                # Reorder trajectories
                self.trajectory_1 = self.reorder_trajectory(self.trajectory_1)
                self.trajectory_2 = self.reorder_trajectory(self.trajectory_2)
            except:
                pass

            # Place robot and destination after loading grid
            self.place_robot()
            self.place_destination()

    def place_robot(self):
        row, col = self.robot_position
        self.canvas.itemconfig(self.grid[row][col], fill=self.robot_color)

    def create_policy_dropdown(self):
        # Create a frame for dropdown
        dropdown_frame = tk.Frame(self.root)
        dropdown_frame.pack()

        # Define policies and create StringVar to store selected policy
        self.policy_var = tk.StringVar(self.root)
        self.policy_var.set("Policy 1")  # Default value

        # Create the OptionMenu widget
        policies = ["Policy 1", "Policy 2", "Policy 3"]
        self.policy_dropdown = tk.OptionMenu(dropdown_frame, self.policy_var, *policies, command=self.on_policy_change)
        self.policy_dropdown.pack()

    def on_policy_change(self, selection):
        # This function is called whenever a new option is selected in the dropdown
        if selection == "Policy 1":
            self.print_policy_1()
            '''
            Ejecutamos policy 1 - Sortest path & most green cells possible.
            '''
            self.find_shortest_path()

        elif selection == "Policy 2":
            self.print_policy_2()
            '''
            Ejecutamos policy 2
            '''
        elif selection == "Policy 3":
            self.print_policy_3()
            '''
            Ejecutamos policy 3
            '''

    def find_shortest_path(self):
        """Finds the shortest path to the destination while maximizing visits to green cells and avoiding yellow cells."""
        start = self.robot_position
        goal = self.destination_position

        # Set up a priority queue (min-heap) for A* search
        open_list = []
        heapq.heappush(open_list, (0, start))  # (priority, (row, col))

        # Dictionaries to keep track of costs and paths
        came_from = {start: None}
        cost_so_far = {start: 0}

        # Define weights for each cell type
        weights = {
            "green": 1,  # Prioritize green cells
            "white": 2,  # Neutral cells
            "yellow": 5  # Avoid yellow cells
        }

        while open_list:
            _, current = heapq.heappop(open_list)

            # If the robot reaches the goal, reconstruct and display the path
            if current == goal:
                self.reconstruct_path(came_from, start, goal)
                return

            # Get the current row and column
            current_row, current_col = current

            # Check all four possible neighbors (up, down, left, right)
            for neighbor in self.get_neighbors(current_row, current_col):
                neighbor_row, neighbor_col = neighbor

                # Get the color of the neighbor cell
                cell_color = self.canvas.itemcget(self.grid[neighbor_row][neighbor_col], "fill")

                # Assign weight based on cell color
                if cell_color == "green":
                    move_cost = weights["green"]
                elif cell_color == "yellow":
                    move_cost = weights["yellow"]
                else:
                    move_cost = weights["white"]

                # Calculate new cost to reach this neighbor
                new_cost = cost_so_far[current] + move_cost

                # If this path is shorter, or the neighbor hasn't been visited yet
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost
                    heapq.heappush(open_list, (priority, neighbor))
                    came_from[neighbor] = current

        print("No path found!")

    # Define three functions to print the policy names
    def print_policy_1(self):
        print("Policy 1 selected")

    def print_policy_2(self):
        print("Policy 2 selected")

    def print_policy_3(self):
        print("Policy 3 selected")

    def place_destination(self):
        row, col = self.destination_position
        self.canvas.itemconfig(self.grid[row][col], fill=self.destination_color)
    
    def get_neighbors(self, row, col):
        """Returns valid neighboring cells (up, down, left, right)."""
        neighbors = []
        if row > 0:  # Up
            neighbors.append((row - 1, col))
        if row < self.height - 1:  # Down
            neighbors.append((row + 1, col))
        if col > 0:  # Left
            neighbors.append((row, col - 1))
        if col < self.width - 1:  # Right
            neighbors.append((row, col + 1))
        return neighbors

    def reconstruct_path(self, came_from, start, goal):
        """Reconstructs the path from start to goal."""
        current = goal
        path = []

        while current != start:
            path.append(current)
            current = came_from[current]

        path.reverse()  # Reverse the path to get it from start to goal

        # Highlight the path on the grid
        for row, col in path:
            self.canvas.itemconfig(self.grid[row][col], fill="orange")

        print("Path found:", path)

    def move_robot(self, position):
        if 0 <= position[0] < self.height and 0 <= position[1] < self.width:
            # Check if the destination cell is not black
            if self.canvas.itemcget(self.grid[position[0]][position[1]], "fill") != "black":
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

        count_clusters_button = tk.Button(control_frame, text="Count Clusters", command=self.count_clusters)
        count_clusters_button.grid(row=6, column=1)

        # Add new buttons and entry fields
        self.amplify_button = tk.Button(control_frame, text="Amplify", command=self.amplify_trajectory)
        self.amplify_button.grid(row=7, column=0)

        self.reduce_button = tk.Button(control_frame, text="Reduce", command=self.reduce_trajectory)
        self.reduce_button.grid(row=7, column=2)

        tk.Label(control_frame, text="Multiply Factor").grid(row=7, column=1)
        self.integer_entry = tk.Entry(control_frame)
        self.integer_entry.grid(row=8, column=1)
        self.integer_entry.bind("<KeyRelease>", self.check_multiply_factor)

        tk.Label(control_frame, text="ID Cluster").grid(row=9, column=0)
        self.cluster_id_entry = tk.Entry(control_frame)
        self.cluster_id_entry.grid(row=9, column=1)

    def check_multiply_factor(self, event=None):
        # Check if the integer entry is not empty and contains a valid integer
        try:
            int(self.integer_entry.get())
            self.amplify_button.config(state=tk.NORMAL)  # Enable amplify_button
            self.reduce_button.config(state=tk.NORMAL)  # Enable reduce_button
        except ValueError:
            self.amplify_button.config(state=tk.DISABLED)  # Disable amplify_button
            self.reduce_button.config(state=tk.DISABLED)  # Disable reduce_button

    def amplify_trajectory(self):
        factor = int(self.integer_entry.get())
        # Implement amplification logic for trajectory

    def reduce_trajectory(self):
        factor = int(self.integer_entry.get())
        # Implement reduction logic for trajectory

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

    def count_clusters(self):
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        clusters = 0
        cluster_data = {}

        def dfs_black(row, col, cluster_id):
            stack = [(row, col)]
            black_cells = []
            while stack:
                r, c = stack.pop()
                if not (0 <= r < self.height and 0 <= c < self.width) or visited[r][c]:
                    continue
                if self.canvas.itemcget(self.grid[r][c], "fill") != "#000000":
                    continue
                visited[r][c] = True
                black_cells.append((r, c))

                # Check all 4 directions
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    stack.append((nr, nc))
            return black_cells

        def bfs_yellow(black_cells):
            yellow_cells = set()
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for r, c in black_cells:
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width and not visited[nr][nc]:
                        if self.canvas.itemcget(self.grid[nr][nc], "fill") == "#fefb00":
                            yellow_cells.add((nr, nc))
                            visited[nr][nc] = True
            return yellow_cells

        for row in range(self.height):
            for col in range(self.width):
                if not visited[row][col] and self.canvas.itemcget(self.grid[row][col], "fill") == "#000000":
                    black_cells = dfs_black(row, col, clusters)
                    if black_cells:
                        yellow_cells = bfs_yellow(black_cells)
                        if yellow_cells:
                            cluster_data[clusters] = {
                                'black': black_cells,
                                'yellow': list(yellow_cells)
                            }
                            clusters += 1

        # Print the cluster IDs and their cell contents
        for cluster_id, cells in cluster_data.items():
            print(f"Cluster ID: {cluster_id}")
            print(f"  Black cells: {cells['black']}")
            print(f"  Yellow cells: {cells['yellow']}")

        print(f"Number of clusters: {clusters}")

def main():
    root = tk.Tk()
    root.title("Grid Editor")
    
    # Customize width and height here
    width = 50  # Adjust as needed
    height = 50 # Adjust as needed
    
    #app = GridApp(root, width, height, default_map="/Users/adrian/Desktop/traj2.txt")
    app = GridApp(root, width, height, default_map="/Users/adrian/Desktop/map_final.txt")
    root.mainloop()

if __name__ == "__main__":
    main()
