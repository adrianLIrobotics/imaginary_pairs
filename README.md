# imaginary_pairs

### Policy 1
```
"""Finds the shortest path to the destination while maximizing visits to green cells and avoiding yellow cells."""
```

### Policy 2
```
"""
        Finds the shortest path to the destination while:
        - Staying away from yellow cells based on an input parameter yellow_cells_distance. 
        This needs to be an integer. The robot should generate a path that always follows the rule 
        of staying a minimum number of cells (in all directions: up, down, left, right) away from yellow cells.
        - Maximizing the use of green cells for the shortest path.
"""
```
### Policy 3
```
"""
        Finds the shortest path to the destination while:
        - Maximizing the use of green cells in the shortest path.
        - Exiting yellow cells immediately if the robot is on a yellow cell.
        - Ensuring the robot never revisits a cell it has already visited.
"""
```