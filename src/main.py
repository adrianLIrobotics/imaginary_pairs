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
        self.red_color = "#ff2600"
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
        self.observation = [] # human observation

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
                learning_rate = 0.5 
                self.grid[row][col] = (rect_id, text_id, learning_rate) 



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
        self.file_menu.add_command(label="Learn", command=self.learn)
        self.file_menu.add_command(label="Info", command=self.info)

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


            rect_id, _ , _ = self.grid[row][col] 
            self.canvas.itemconfig(rect_id, fill=self.current_color)  
            self.original_colors[row][col] = self.current_color 
            
            if self.current_color == self.red_color:
                self.path.append((row, col))
                self.observation.append((row, col))

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

    def update_cell_color(self, new_cell_val, row, col):
        if new_cell_val <= 0.5:
            # change cell to green color.
            self.canvas.itemconfig(self.grid[row][col][0], fill="green")
        if new_cell_val >= 0.7:
            self.canvas.itemconfig(self.grid[row][col][0], fill="#fefb00")

    def update_text_g_local(self, new_g, h, row, col):
        
        self.canvas.itemconfig(self.grid[row][col][1], text=f"g: {new_g:.2f}\nh: {h}")

    def learn(self):
        import re
        def parse_g_value(g_string):
            g_values = re.findall(r'g:\s*([0-9]*\.?[0-9]+)', g_string)
      
    
            # Convertimos los valores encontrados a float
            return [float(value) for value in g_values]
        
        def parse_h_value(h_string):
  
            h_values = re.findall(r'h:\s*([0-9]*\.?[0-9]+)', h_string)
    
            # Convertimos los valores encontrados a float
            return [float(value) for value in h_values]
            
        self.observation: list
        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                color = self.get_cell_color(row, col)
                text_content = self.canvas.itemcget(self.grid[row][col][1], "text")
                g_local = parse_g_value(text_content)[0]
                h_local = parse_h_value(text_content)[0]
                if (color == self.red_color):
                 
                    updated_local_g = self.update_g_value(g_local, 0, 0.5)
                    print(updated_local_g)
                    self.update_cell_color(updated_local_g, row, col)
                    self.update_text_g_local(updated_local_g, h_local, row, col)
                

    def info(self):
        popup = tk.Toplevel()
        popup.title("Info")
        
        # Etiqueta de texto en la ventana popup
        texto_info = "Robot is blue cell, purple is destination. Red is observations. Yellow is danger. Green is safe. Orange is robot defined trajectory"
        label = tk.Label(popup, text=texto_info, padx=20, pady=20)
        label.pack()

        # Botón para cerrar la ventana popup
        btn_cerrar = tk.Button(popup, text="Cerrar", command=popup.destroy)
        btn_cerrar.pack(pady=(0, 20))

    
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
                    
                    rect_id, text_id, learning_rate = self.grid[row][col]
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
        rect_id, _ , _= self.grid[row][col] 
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

    def find_shortest_path_with_neighbor_distance(self, neighbor_distance=1): # policy 2
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
        local_costs = {}  # To store local costs for each cell
        chosen_neighbors = {}  # Stores the best neighbor for each cell

        # Define weights for each cell type
        weights = {
            "green": 1,    # Prioritize green cells
            "white": 3,    # Neutral cells
            "#fefb00": 5   # Avoid yellow cells
        }
        penalty_for_yellow_neighbors = 3  # Penalty for neighboring yellow cells
        min_g = 1
        max_g = 14  # Adjust based on your maximum expected cost

        def visit():    
                    neighbor_row, neighbor_col = neighbor

                    # Get the color of the neighbor cell
                    cell_color = self.canvas.itemcget(self.grid[neighbor_row][neighbor_col][0], "fill")

                    # Assign weight based on cell color
                    move_cost = weights.get(cell_color, weights["white"])

                    # Check neighbors within the specified distance for penalties
                    penalty = 0
                    for r in range(neighbor_row - neighbor_distance, neighbor_row + neighbor_distance + 1):
                        for c in range(neighbor_col - neighbor_distance, neighbor_col + neighbor_distance + 1):
                            if (r, c) != (neighbor_row, neighbor_col) and self.is_within_bounds(r, c):
                                neighbor_color = self.canvas.itemcget(self.grid[r][c][0], "fill")
                                if neighbor_color == "#fefb00":
                                    penalty += penalty_for_yellow_neighbors

                    # Add penalty if any yellow neighbors are found
                    move_cost += penalty

                    # Calculate local cost to reach this neighbor
                    new_cost = move_cost  # Local cost for this neighbor

                    # Heuristic cost to reach the goal
                    h_cost = self.heuristic(neighbor, goal)

                    # If the neighbor is yellow, set its local cost to 1 directly
                    if cell_color == "#fefb00":
                        local_costs[neighbor] = 1
                    else:
                        local_costs[neighbor] = move_cost  # Store the local g cost

                    # Calculate total priority (f = g + h)
                    priority = new_cost + h_cost

                    # If this path is shorter, or the neighbor hasn't been visited yet
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        heapq.heappush(open_list, (priority, neighbor))
                        came_from[neighbor] = current

                        # Record the chosen neighbor for this cell
                        chosen_neighbors[neighbor] = current


        while open_list:
            # Pop the node with the lowest f-score
            _, current = heapq.heappop(open_list)

            # If the robot reaches the goal, reconstruct and display the path
            if current == goal:
                self.reconstruct_path(came_from, start, goal)
                print("reconstruc" + str(came_from))
                for neighbor in self.get_all_cells():
                    visit()
                break

            # Get the current row and column
            current_row, current_col = current

            # Check all possible neighbors

            for neighbor in self.get_neighbors(current_row, current_col):
                visit()
                #for neighbor in self.get_all_cells():
           
        # No path found
        if current != goal:
            print("No path found!")

        # Normalize local costs and display g and h values
        for row in range(self.height):
            for col in range(self.width):
                cell_position = (row, col)

                # Calculate local g cost for the display
                if cell_position in local_costs:
                    g_cost = local_costs[cell_position]
                    # if yellow always 1
                    
                    # Normalize g cost between 0 and 1
                    normalized_g = (g_cost - min_g) / (max_g - min_g) if max_g > min_g else 0
                    if "#fefb00" == self.get_cell_color(row, col):
                        normalized_g = 1
                    if self.canvas.itemcget(self.grid[row][col][0], "fill") == "#fefb00":
                        normalized_g = 1 
                else:
                    # Set normalized g to 1 for yellow cells
                    if self.canvas.itemcget(self.grid[row][col][0], "fill") == "#fefb00":
                        normalized_g = 1  # Always show 1 for yellow cells
                    else:
                        normalized_g = 0  # If not reached and not yellow

                # Calculate heuristic cost to the goal
                h_cost = self.heuristic(cell_position, goal)

                # Update display with normalized g and h values
                self.canvas.itemconfig(self.grid[row][col][1], text=f"g: {normalized_g:.2f}\nh: {h_cost}")

    

    def is_within_bounds(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width
    
    def update_g_value(self, g_old, O, alpha=0.5):
        """
        Update the g value based on the equation:
        g_new(x, y) = g_old(x, y) * (1 - alpha) + alpha * O(x, y)

        Parameters:
        g_old (float): The old g value at (x, y)
        O (float): The O(x, y) value
        alpha (float): The alpha parameter (weighting factor)

        Returns:
        float: The updated g value
        """
        g_new = g_old * (1 - alpha) + alpha * O
        return g_new


    def find_shortest_path(self):
        start = self.robot_position
        goal = self.destination_position
        min_g = 1
        max_g = 5

        # Set up a priority queue (min-heap) for A* search
        open_list = []
        heapq.heappush(open_list, (0, start))  # (priority, (row, col))

        # Dictionaries to keep track of costs, paths, and chosen neighbors
        came_from = {start: None}
        cost_so_far = {start: 0}
        local_costs = {}  # To store local costs for each cell
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
                move_cost = weights.get(cell_color, weights["white"])

                # Calculate new cost to reach this neighbor
                new_cost = move_cost  # Local cost for this neighbor

                # Heuristic cost to reach the goal
                h_cost = self.heuristic(neighbor, goal)

                # Calculate total priority (f = g + h)
                priority = new_cost + h_cost

                # If this path is shorter, or the neighbor hasn't been visited yet
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    local_costs[neighbor] = move_cost  # Store the local g cost
                    heapq.heappush(open_list, (priority, neighbor))
                    came_from[neighbor] = current

                    # Record the chosen neighbor for this cell
                    chosen_neighbors[neighbor] = current

        # No path found
        if current != goal:
            print("No path found!")

        # Normalize local costs and display g and h values
        for row in range(self.height):
            for col in range(self.width):
                cell_position = (row, col)

                # Calculate local g cost for the display
                if cell_position in local_costs:
                    g_cost = local_costs[cell_position]
                    # Normalize g cost between 0 and 1
                    normalized_g = (g_cost - min_g) / (max_g - min_g) if max_g > min_g else 0
                    if "#fefb00" == self.get_cell_color(row, col):
                        normalized_g = 1
                    if self.canvas.itemcget(self.grid[row][col][0], "fill") == "#fefb00":
                        normalized_g = 1 
                else:
                    normalized_g = 0  # If the cell was never reached, set g to 0
                    if "#fefb00" == self.get_cell_color(row, col):
                        normalized_g = 1
                    if self.canvas.itemcget(self.grid[row][col][0], "fill") == "#fefb00":
                        normalized_g = 1 

                # Calculate heuristic cost to the goal
                h_cost = self.heuristic(cell_position, goal)

                # Update display with normalized g and h values
                self.canvas.itemconfig(self.grid[row][col][1], text=f"g: {normalized_g:.2f}\nh: {h_cost}")

        # Optionally, print the chosen neighbors for debugging
        print("====")
        print(chosen_neighbors)
        print("====")


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

    def display_final_costs_v2(self, cost_so_far, chosen_neighbors):
        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                cell_position = (row, col)

                # Check if the cell has a cost so far
                if cell_position in cost_so_far:
                    g_cost = cost_so_far[cell_position]
                    h_cost = self.heuristic(cell_position, self.destination_position)
                    f_cost = g_cost + h_cost
                    
                    # Display costs for all cells, including neighbors and non-neighbors
                    if cell_position in chosen_neighbors:
                        chosen_neighbor = chosen_neighbors[cell_position]
                        # If it's a chosen neighbor, you can choose to highlight it or display different info
                        self.canvas.itemconfig(self.grid[row][col][1], text=f"h: {h_cost}\n g: {g_cost}")
                    else:
                        self.canvas.itemconfig(self.grid[row][col][1], text=f"f: {f_cost}")
                else:
                    # If there's no cost for this cell, you can choose to clear the text or leave it as is
                    self.canvas.itemconfig(self.grid[row][col][1], text="")


    
    def place_destination(self):
        row, col = self.destination_position
        rect_id, _ , _ = self.grid[row][col]  
        self.canvas.itemconfig(rect_id, fill=self.destination_color) 
    
    def get_neighbors(self, row, col):
        neighbors = []
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  
            neighbor_row, neighbor_col = row + d_row, col + d_col
            if 0 <= neighbor_row < self.height and 0 <= neighbor_col < self.width:
                neighbors.append((neighbor_row, neighbor_col))
                print(f"Cell ({neighbor_row}, {neighbor_col}) color: {self.canvas.itemcget(self.grid[neighbor_row][neighbor_col], 'fill')}")
        return neighbors
    
    def get_all_cells(self):
        all_cells = []
        for row in range(self.height):
            for col in range(self.width):
                # Add the cell position to the list
                all_cells.append((row, col))
                # Print the color of the cell
                print(f"Cell ({row}, {col}) color: {self.canvas.itemcget(self.grid[row][col], 'fill')}")
        return all_cells

    def reconstruct_path(self, came_from, start, goal, clear_previous=True):
        current = goal
        if clear_previous:
            self.clear_previous_path()

        while current != start:
            self.path.append(current)
            current = came_from[current]

        self.path.reverse()  
        for row, col in self.path[0:-1]:
            rect_id, _ , _ = self.grid[row][col]  
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

        play_trajectory_2_button = tk.Button(control_frame, text="Play robot Trajectory", command=lambda: self.play_trajectory(self.path))
        play_trajectory_2_button.grid(row=4, column=1)

        play_trajectory_3_button = tk.Button(control_frame, text="Play observed Trajectory", command=lambda: self.play_trajectory(self.observation))
        play_trajectory_3_button.grid(row=5, column=1)

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
        print(trajectory)
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
        self.observation.clear()
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

    # ff2600 - rojo
