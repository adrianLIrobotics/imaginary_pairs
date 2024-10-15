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



1. Inicializar cola_prioridad (min-heap) con el nodo inicial y costo 0
2. Inicializar diccionario de caminos 'came_from' con nodo_inicial: None
3. Inicializar diccionario de costos 'cost_so_far' con nodo_inicial: 0

4. Mientras la cola_prioridad no esté vacía:
    5. Sacar el nodo con menor costo de la cola (nodo_actual)
    
    6. Si nodo_actual es el destino:
        7. Reconstruir el camino usando 'came_from'
        8. Retornar el camino
    
    9. Para cada vecino del nodo_actual:
        10. Obtener el color de la celda vecina
        11. Asignar un costo de movimiento basado en el color:
            - Verde: 1 (prioritario)
            - Blanco: 2 (neutral)
            - Amarillo: 5 (evitar)

        12. Calcular el nuevo costo para el vecino (costo_actual + costo_movimiento)
        
        13. Si este nuevo costo es menor que el costo registrado:
            14. Actualizar 'cost_so_far' para este vecino
            15. Añadir el vecino a la cola_prioridad con el nuevo costo
            16. Actualizar 'came_from' para indicar que llegamos a este vecino desde nodo_actual

17. Si la cola_prioridad está vacía y no se encontró un camino:
    18. Mostrar "No path found"
