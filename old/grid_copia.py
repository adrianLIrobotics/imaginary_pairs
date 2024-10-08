from collections import deque

# Configuración del grid
rows, cols = 8, 6

# Crear un grid vacío
grid = [[' ' for _ in range(cols)] for _ in range(rows)]

# Posiciones de los objetos
robot_pos = (4, 1)  # Robot en (fila 4, columna 1)
ball_pos = (4, 3)   # Ball en (fila 4, columna 3)
goal_pos = (4, 6)   # Goal en (fila 4, columna 6)

# Colocar los objetos en el grid
grid[robot_pos[0]-1][robot_pos[1]-1] = 'R'
grid[ball_pos[0]-1][ball_pos[1]-1] = 'O'
grid[goal_pos[0]-1][goal_pos[1]-1] = 'G'

# Direcciones posibles (arriba, abajo, izquierda, derecha)
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# BFS para encontrar la ruta más corta evitando la pelota
def bfs(grid, start, goal):
    queue = deque([(start, [])])
    visited = set()
    visited.add(start)
    
    while queue:
        (x, y), path = queue.popleft()
        
        if (x, y) == goal:
            return path + [(x, y)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                # Evitar la posición de la pelota
                if grid[nx][ny] != 'O':
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(x, y)]))

# Encontrar la ruta más corta evitando la pelota
shortest_path = bfs(grid, (robot_pos[0]-1, robot_pos[1]-1), (goal_pos[0]-1, goal_pos[1]-1))

# Marcar la trayectoria en el grid
for step, (x, y) in enumerate(shortest_path):
    grid[x][y] = str(step + 1)

# Función para imprimir el grid
def print_grid(grid):
    print("  " + "   ".join(map(str, range(1, cols+1))))
    print("  " + "-" * (3 * cols + 2))
    for i, row in enumerate(grid):
        print(f"{i+1} | " + " | ".join(row) + " |")
        print("  " + "-" * (3 * cols + 2))

# Imprimir el grid con la trayectoria
print_grid(grid)
