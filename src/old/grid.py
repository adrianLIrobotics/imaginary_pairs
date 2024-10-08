# Set up the grid dimensions
rows, cols = 8, 6

# Create an empty grid
grid = [[' ' for _ in range(cols)] for _ in range(rows)]

# Place the objects on the grid
grid[4-1][1-1] = 'R'  # Robot at (row 4, col 1)
grid[3-1][3-1] = 'B'  # Baby at (row 3, col 3)
grid[7-1][5-1] = 'O'  # Ball at (row 7, col 5)

# Function to print the grid
def print_grid(grid):
    print("  " + "   ".join(map(str, range(1, cols+1))))
    print("  " + "---" * cols)
    for i, row in enumerate(grid):
        print(f"{i+1} | " + " | ".join(row) + " |")
        print("  " + "---" * cols)

# Print the grid
print_grid(grid)
