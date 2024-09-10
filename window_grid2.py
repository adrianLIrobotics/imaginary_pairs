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
        self.robot_position = (21, 1)  # Initial robot position
        self.destination_position = (height-1, width-1)  # Initial destination position
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

    def on_canvas_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= col < self.width and 0 <= row < self.height:
            self.canvas.itemconfig(self.grid[row][col], fill=self.current_color)
            self.original_colors[row][col] = self.current_color  # Save the color change

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
            for row in range(self.height):
                for col in range(self.width):
                    color = grid_data[row][col]
                    self.canvas.itemconfig(self.grid[row][col], fill=color)
                    self.original_colors[row][col] = color  # Store original colors

            # Reposition the robot and destination on the loaded grid
            self.place_robot()  # Ensure the robot appears after loading the grid
            self.place_destination()  # Ensure the destination appears

    def place_robot(self):
        row, col = self.robot_position
        self.canvas.itemconfig(self.grid[row][col], fill=self.robot_color)

    def place_destination(self):
        row, col = self.destination_position
        self.canvas.itemconfig(self.grid[row][col], fill=self.destination_color)

    def move_robot(self, direction):
        row, col = self.robot_position
        new_row, new_col = row, col

        if direction == "up" and row > 0:
            new_row = row - 1
        elif direction == "down" and row < self.height - 1:
            new_row = row + 1
        elif direction == "left" and col > 0:
            new_col = col - 1
        elif direction == "right" and col < self.width - 1:
            new_col = col + 1

        # Check if the new cell is not black (blocked)
        if self.canvas.itemcget(self.grid[new_row][new_col], "fill") != "black":
            # Restore the original color of the previous cell
            original_color = self.original_colors[row][col]
            self.canvas.itemconfig(self.grid[row][col], fill=original_color)
            
            # Update the robot's position and place it
            self.robot_position = (new_row, new_col)
            self.place_robot()

    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack()

        up_button = tk.Button(control_frame, text="Up", command=lambda: self.move_robot("up"))
        up_button.grid(row=0, column=1)

        left_button = tk.Button(control_frame, text="Left", command=lambda: self.move_robot("left"))
        left_button.grid(row=1, column=0)

        right_button = tk.Button(control_frame, text="Right", command=lambda: self.move_robot("right"))
        right_button.grid(row=1, column=2)

        down_button = tk.Button(control_frame, text="Down", command=lambda: self.move_robot("down"))
        down_button.grid(row=2, column=1)


def main():
    root = tk.Tk()
    root.title("Grid Editor")
    
    # Customize width and height here
    width = 50  # Adjust as needed
    height = 50 # Adjust as needed

    # Default map file to load
    default_map = "/Users/adrian/Desktop/traj2.txt"

    app = GridApp(root, width, height, default_map=default_map)
    root.mainloop()

if __name__ == "__main__":
    main()
