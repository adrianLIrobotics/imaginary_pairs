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
        self.cell_size = 50
        self.current_color = "white"  
        self.robot_color = "blue" 
        self.destination_color = "purple"  
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.original_colors = [[self.current_color for _ in range(width)] for _ in range(height)] 
        self.robot_start_position = (3, 2)
        self.robot_position = self.robot_start_position  
        self.destination_position = (8, 8)  
        self.trajectory_1 = [] 
        self.trajectory_2 = [] 
        self.create_widgets()
        self.create_controls()
        self.path = []
        self.default_map = default_map
        self.text_ids = []

        self.create_policy_dropdown()

        if default_map and os.path.exists(default_map):
            self.load_grid(default_map)
        else:
            self.place_robot() 
            self.place_destination()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=self.width*self.cell_size, height=self.height*self.cell_size)
        self.canvas.pack()
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        for row in range(self.height):
            row_items = []  
            for col in range(self.width):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                text_id = self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="", font=("Arial", 12))
                self.grid[row][col] = (rect_id, text_id) 


        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        
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


        adjacency_dict = {}
        for i, point in enumerate(trajectory):
            adjacency_dict[point] = []
            for j, other_point in enumerate(trajectory):
                if i != j and is_adjacent(point, other_point):
                    adjacency_dict[point].append(other_point)


        robot_row, robot_col = self.robot_position
        adjacent_cells = [
            (robot_row, robot_col - 1),  # left
            (robot_row, robot_col + 1),  # right
            (robot_row - 1, robot_col),  # up
            (robot_row + 1, robot_col)   # down
        ]
        

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


        ordered_trajectory = trajectory[start_index:] + trajectory[:start_index]


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


        for point in ordered_trajectory:
            if point not in used_points:
                ordered_trajectory_final.append(point)

        return ordered_trajectory_final

    def on_canvas_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= col < self.width and 0 <= row < self.height:


            rect_id, _ = self.grid[row][col] 
            self.canvas.itemconfig(rect_id, fill=self.current_color)  

            self.original_colors[row][col] = self.current_color 

    def get_cell_color(self, row, col):
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.canvas.itemcget(self.grid[row][col][0], "fill")
        else:
            return None 

    def on_mouse_motion(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= col < self.width and 0 <= row < self.height:
            color = self.canvas.itemcget(self.grid[row][col][0], "fill")
            text_content = self.canvas.itemcget(self.grid[row][col][1], "text")

            self.info_label.config(text=f"({row}, {col}) - {color} - {text_content}")

    def choose_color(self):
        color = colorchooser.askcolor()[1]  
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
                self.original_colors[row][col] = color 

    def save_grid(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:

            grid_data = [[self.canvas.itemcget(self.grid[row][col][0], "fill") for col in range(self.width)] for row in range(self.height)]
            with open(filename, 'w') as f:
                json.dump(grid_data, f)
    
    def load_grid(self, filepath=None):

        if not filepath:
            filepath = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        
        if filepath and os.path.exists(filepath):
            with open(filepath, 'r') as f:
                grid_data = json.load(f)
            self.trajectory_1 = []
            self.trajectory_2 = []

            for row in range(self.height):
                for col in range(self.width):
                    color = grid_data[row][col]
                    
                    rect_id, text_id = self.grid[row][col]
                    self.canvas.itemconfig(rect_id, fill=color) 
                    self.original_colors[row][col] = color  

                    if color == "#ff2600": 
                        self.trajectory_1.append((row, col))
                    elif color == "#0432ff": 
                        self.trajectory_2.append((row, col))

            try: 
                self.trajectory_1 = self.reorder_trajectory(self.trajectory_1)
                self.trajectory_2 = self.reorder_trajectory(self.trajectory_2)
            except Exception as e:
                print(f"Error reordering trajectories: {e}")

            self.place_robot()
            self.place_destination()

    def place_robot(self):
        row, col = self.robot_position
        rect_id, _ = self.grid[row][col] 
        self.canvas.itemconfig(rect_id, fill=self.robot_color) 

    def create_policy_dropdown(self):
        dropdown_frame = tk.Frame(self.root)
        dropdown_frame.pack()
        self.policy_var = tk.StringVar(self.root)
        self.policy_var.set("Policy 1")  
        policies = ["Policy 1", "Policy 2", "Policy 3"]
        self.policy_dropdown = tk.OptionMenu(dropdown_frame, self.policy_var, *policies, command=self.on_policy_change)
        self.policy_dropdown.pack()

    def on_policy_change(self, selection):
        if selection == "Policy 1":
            self.find_shortest_path()


        elif selection == "Policy 2":
            self.find_shortest_path_with_neighbor_distance(1) #1

        elif selection == "Policy 3":
            self.find_shortest_path_policy4()

    def heuristic(self, a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_shortest_path_with_neighbor_distance(self, neighbor_distance=1):
        """Finds the shortest path to the destination while maximizing visits to green cells 
        and avoiding yellow cells. Penalizes green cells near yellow cells."""
        
        start = self.robot_position
        goal = self.destination_position

        # Set up a priority queue (min-heap) for A* search
        open_list = []
        heapq.heappush(open_list, (0, start))  # (priority, (row, col))

        # Dictionaries to keep track of costs, paths, and chosen neighbors
        came_from = {start: None}
        cost_so_far = {start: 0}
        cost_so_far_normal = {start: 0}
        chosen_neighbors = {}  # Stores the best neighbor for each cell

        # Define weights for each cell type and penalties for neighbors
        weights = {
            "green": 1,    # Prioritize green cells
            "white": 3,    # Neutral cells
            "#fefb00": 5   # Avoid yellow cells
        }
        penalty_for_yellow_neighbors = 3  # Lower than the penalty for being in a yellow cell
        # 7 es el max para distancia 1 + 3 por cada nivel de distancia 
        max_g = 14 #14
        min_g = 1

        while open_list:
            # Pop the node with the lowest f-score
            _, current = heapq.heappop(open_list)

            # If the robot reaches the goal, reconstruct and display the path
            if current == goal:
                self.reconstruct_path(came_from, start, goal)
                break

            # Get the current row and column
            current_row, current_col = current

            # Check all four possible neighbors (up, down, left, right)
            for neighbor in self.get_neighbors(current_row, current_col):
                neighbor_row, neighbor_col = neighbor

                # Get the color of the neighbor cell
                cell_color = self.canvas.itemcget(self.grid[neighbor_row][neighbor_col][0], "fill")

                # Assign weight based on cell color
                if cell_color == "green":
                    move_cost = weights["green"]
                elif cell_color == "#fefb00":
                    move_cost = weights["#fefb00"]
                else:
                    move_cost = weights["white"]

                # Check neighbors within the specified distance
                penalty = 0
                for r in range(neighbor_row - neighbor_distance, neighbor_row + neighbor_distance + 1):
                    for c in range(neighbor_col - neighbor_distance, neighbor_col + neighbor_distance + 1):
                        if (r, c) != (neighbor_row, neighbor_col) and self.is_within_bounds(r, c):
                            neighbor_color = self.canvas.itemcget(self.grid[r][c][0], "fill")
                            if neighbor_color == "#fefb00":
                                penalty += penalty_for_yellow_neighbors

                # Add penalty if any yellow neighbors are found
                move_cost += penalty

                # Calculate new cost to reach this neighbor
                #new_cost = cost_so_far[current] + move_cost
                new_cost =  move_cost

                # Heuristic cost to reach the goal (for tie-breaking)
                h_cost = self.heuristic(neighbor, goal)

                # Calculate total priority (f = g + h)
                priority = new_cost + h_cost

                # If this path is shorter, or the neighbor hasn't been visited yet
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    cost_so_far_normal[neighbor] = round((new_cost - min_g) / (max_g - min_g), 1)
                    heapq.heappush(open_list, (priority, neighbor))
                    came_from[neighbor] = current

                    # Record the chosen neighbor for this cell
                    chosen_neighbors[neighbor] = current

            # After each step, update the grid with the latest costs and chosen paths
            # self.update_cost_display(cost_so_far, chosen_neighbors)

        # No path found
        if current != goal:
            print("No path found!")

        # After calculating the shortest path, display the total cost (g + h) for each cell
        self.display_final_costs(cost_so_far_normal, chosen_neighbors)

    def is_within_bounds(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width

    def find_shortest_path(self):
        """Finds the shortest path to the destination while maximizing visits to green cells and avoiding yellow cells."""
        start = self.robot_position
        goal = self.destination_position
        # 5 is max
        min_g = 1
        max_g = 5

        # Set up a priority queue (min-heap) for A* search
        open_list = []
        heapq.heappush(open_list, (0, start))  # (priority, (row, col))

        # Dictionaries to keep track of costs, paths, and chosen neighbors
        came_from = {start: None}
        cost_so_far = {start: 0}
        cost_so_far_normalized = {start: 0}
        chosen_neighbors = {}  # Stores the best neighbor for each cell

        # Define weights for each cell type
        weights = {
            "green": 1,  # Prioritize green cells
            "white": 3,  # Neutral cells
            "#fefb00": 5  # Avoid yellow cells
        }

        while open_list:
            # Pop the node with the lowest f-score
            _, current = heapq.heappop(open_list)

            # If the robot reaches the goal, reconstruct and display the path
            if current == goal:
                self.reconstruct_path(came_from, start, goal)
                break

            # Get the current row and column
            current_row, current_col = current

            # Check all four possible neighbors (up, down, left, right)
            for neighbor in self.get_neighbors(current_row, current_col):
                neighbor_row, neighbor_col = neighbor

                # Get the color of the neighbor cell
                cell_color = self.canvas.itemcget(self.grid[neighbor_row][neighbor_col][0], "fill")
                # Assign weight based on cell color
                if cell_color == "green":
                    move_cost = weights["green"]
                elif cell_color == "#fefb00":
                    move_cost = weights["#fefb00"]
                else:
                    move_cost = weights["white"]

                # Calculate new cost to reach this neighbor
                #new_cost = cost_so_far[current] + move_cost
                new_cost = move_cost

                # Heuristic cost to reach the goal (for tie-breaking)
                h_cost = self.heuristic(neighbor, goal)

                # Calculate total priority (f = g + h)
                priority = new_cost + h_cost

                # If this path is shorter, or the neighbor hasn't been visited yet
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    cost_so_far_normalized[neighbor] = (new_cost - min_g) / (max_g - min_g)
                    heapq.heappush(open_list, (priority, neighbor))
                    came_from[neighbor] = current

                    # Record the chosen neighbor for this cell
                    chosen_neighbors[neighbor] = current

            # After each step, update the grid with the latest costs and chosen paths
            #self.update_cost_display(cost_so_far, chosen_neighbors)

        # No path found
        if current != goal:
            print("No path found!")

        # After calculating the shortest path, display the total cost (g + h) for each cell
        self.display_final_costs(cost_so_far_normalized, chosen_neighbors)

    def update_cost_display(self, cost_so_far, chosen_neighbors):
        for row in range(self.height):
            for col in range(self.width):
                rect_id, text_id = self.grid[row][col]  # Extract both the rect_id and text_id

                # Get the f-cost (which is the sum of cumulative cost and heuristic)
                f_cost = cost_so_far.get((row, col), float('inf'))  # Default to infinity if the cell hasn't been visited
                
                # Update the text display for the cell
                self.canvas.itemconfig(text_id, text=f"{f_cost}")  # Update the text_id to display the f-cost
     
    def display_final_costs(self, cost_so_far, chosen_neighbors):

        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                cell_position = (row, col)
                if cell_position in cost_so_far:
                    g_cost = cost_so_far[cell_position]
                    h_cost = self.heuristic(cell_position, self.destination_position)
                    f_cost = g_cost + h_cost

                    if cell_position in chosen_neighbors:
                        chosen_neighbor = chosen_neighbors[cell_position]
                        self.canvas.itemconfig(self.grid[row][col][1], text=f"h: {h_cost}\n  g: {g_cost}")
                    else:
                        self.canvas.itemconfig(self.grid[row][col][1], text=f"{f_cost}")

    
    def place_destination(self):
        row, col = self.destination_position
        rect_id, _ = self.grid[row][col]  
        self.canvas.itemconfig(rect_id, fill=self.destination_color) 
    
    def get_neighbors(self, row, col):
        neighbors = []
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  
            neighbor_row, neighbor_col = row + d_row, col + d_col
            if 0 <= neighbor_row < self.height and 0 <= neighbor_col < self.width:
                neighbors.append((neighbor_row, neighbor_col))
                print(f"Cell ({neighbor_row}, {neighbor_col}) color: {self.canvas.itemcget(self.grid[neighbor_row][neighbor_col], 'fill')}")
        return neighbors

    def reconstruct_path(self, came_from, start, goal, clear_previous=True):
        current = goal
        if clear_previous:
            self.clear_previous_path()

        while current != start:
            self.path.append(current)
            current = came_from[current]

        self.path.reverse()  
        for row, col in self.path[0:-1]:
            rect_id, _ = self.grid[row][col]  
            self.canvas.itemconfig(rect_id, fill="orange")

        print("Path found:", self.path)

    def clear_previous_path(self):
        self.path.clear()

    def move_robot(self, position):
        if 0 <= position[0] < self.height and 0 <= position[1] < self.width:
            if self.canvas.itemcget(self.grid[position[0]][position[1]][0], "fill") != "black":  
                original_color = self.original_colors[self.robot_position[0]][self.robot_position[1]]
                self.canvas.itemconfig(self.grid[self.robot_position[0]][self.robot_position[1]][0], fill=original_color) 
                self.robot_position = position
                self.place_robot()
                self.get_neighbors(self.robot_position[0], self.robot_position[1])

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

        play_trajectory_2_button = tk.Button(control_frame, text="Play Trajectory", command=lambda: self.play_trajectory(self.path))
        play_trajectory_2_button.grid(row=4, column=1)

        self.clear_button = tk.Button(control_frame, text="Clear Path", command=self.clear_path)
        self.clear_button.grid(row=1, column=1)

    def reset_robot(self):
        
        self.robot_position = self.robot_start_position
        self.place_robot()
        self.load_grid(self.default_map)

    def clear_grid_text(self):
        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
               
                self.canvas.itemconfig(self.grid[row][col][1], text="")

    def display_delete(self):
        for text_id in self.text_ids:
            self.canvas.delete(text_id) 
        self.text_ids.clear()
        
    def play_trajectory(self, trajectory):
        self.current_trajectory = trajectory
        self.trajectory_index = 0
        self.move_next_position()

    def move_next_position(self):
        if self.trajectory_index < len(self.current_trajectory):
            next_position = self.current_trajectory[self.trajectory_index]
            self.move_robot(next_position)
            self.trajectory_index += 1
            self.root.after(500, self.move_next_position)  

    def clear_path(self):
        
        self.load_grid(self.default_map)
        self.path.clear() 
        self.clear_grid_text()


def main():
    root = tk.Tk()
    root.title("Grid Editor")
    width = 10 
    height = 10 
    app = GridApp(root, width, height, default_map="/Users/adrian/Desktop/a.txt")
    root.mainloop()

if __name__ == "__main__":
    main()
