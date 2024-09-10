import tkinter as tk
from tkinter import filedialog, colorchooser
import json

class GridApp:
    def __init__(self, root, width, height):
        self.root = root
        self.width = width
        self.height = height
        self.cell_size = 30
        self.current_color = "white"  # Color por defecto
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.create_widgets()
        
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

    def on_canvas_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= col < self.width and 0 <= row < self.height:
            self.canvas.itemconfig(self.grid[row][col], fill=self.current_color)

    def choose_color(self):
        color = colorchooser.askcolor()[1]  # Devuelve una tupla (color, código hex)
        if color:
            self.current_color = color

    def save_grid(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            grid_data = [[self.canvas.itemcget(self.grid[row][col], "fill") for col in range(self.width)] for row in range(self.height)]
            with open(filename, 'w') as f:
                json.dump(grid_data, f)
    
    def load_grid(self):
        filename = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'r') as f:
                grid_data = json.load(f)
            for row in range(self.height):
                for col in range(self.width):
                    color = grid_data[row][col]
                    self.canvas.itemconfig(self.grid[row][col], fill=color)

def main():
    root = tk.Tk()
    root.title("Grid Editor")
    
    # Personaliza el ancho y alto aquí
    width = 10
    height = 10

    app = GridApp(root, width, height)
    root.mainloop()

if __name__ == "__main__":
    main()
