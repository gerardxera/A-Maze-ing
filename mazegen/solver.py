#!/usr/bin/python3
"""Modulo para la resolucion de laberintos mediante busqueda en anchura (BFS)."""

from collections import deque
from mazegen.cell import Cell, Wall
from mazegen.grid import Grid

# Mapeo de paredes a direcciones cardinales en texto
WALL_TO_DIRECTION: dict[Wall, str] = {
	Wall.NORTH: "N",
	Wall.SOUTH: "S",
	Wall.EAST: "E",
	Wall.WEST: "W",
}


def find_shortest_path(
	grid: Grid,
	entry: tuple[int, int],
	exit_pos: tuple[int, int],
) -> list[tuple[int, int]]:
	"""Encuentra el camino mas corto entre entry y exit usando BFS.

	Args:
		grid: Cuadricula del laberinto ya generado.
		entry: Coordenadas (x, y) de inicio.
		exit_pos: Coordenadas (x, y) de destino.
	
	Return:
		Lista ordenada de coordenadas [(x1, y1), (x2, y2), ...] desde entry hasta exit.
		Retorna una lista vacia si no existe camino posible.
	"""
	start_cell = grid.get_cell(entry[0], entry[1])
	target_cell = grid.get_cell(exit_pos[0], exit_pos[1])

	if start_cell is None or target_cell is None:
		return[]
	
	if entry == exit_pos:
		return [entry]
	
	queue: deque[Cell] = deque([start_cell])  #  Cola de espera = queue
	visited: set[tuple[int, int]] = {(start_cell.x, start_cell.y)}
	parent: dict[tuple[int, int], tuple[int, int]] = {}

	reached = False  #  Estado de la ejecucion del analisis del programa

	while queue:
		current = queue.popleft()

		if (current.x, current.y) == exit_pos:
			reached = True
			break
		
		# Explorar celdas vecinas contiguos
		for neighbor, wall in grid.get_neighbors(current):
			# No debe ser celda del patron 42
			if neighbor.is_42_cell:
				continue
			
			# Solo se puede avanzar si NO hay pared en esa direccion
			if not current.has_wall(wall):
				coord = (neighbor.x, neighbor.y)
				if coord not in visited:
					visited.add(coord)
					parent[coord] = (current.x, current.y)
					queue.append(neighbor)

	if not reached:
		return []
		
	# Reconstruccion del camino desde exit_pos hacia entry
	path: list[tuple[int, int]] = []
	curr_coord: tuple[int, int] | None = exit_pos

	while curr_coord is not None:
		path.append(curr_coord)
		curr_coord = parent.get(curr_coord)
		
	path.reverse()
	return path


def path_to_directions(path: list[tuple[int, int]]) -> str:
	"""Convierte una secuencia de coordenadas en una cadena de direcciones (N, E, S, W).

	Args:
		path: Lista de tuplas (x, y) que forman el camino continuo.
	
	Returns:
		Cadena con las direcciones separadas por comas (ej. 'E, E, S, W').
	"""
	if len(path) < 2:
		return ""
	
	directions: list[str] = []

	for i in range(len(path) - 1):
		x1, y1 = path[i]
		x2, y2 = path[i + 1]

		dx = x2 - x1
		dy = y2 - y1

		if dx == 1 and dy == 0:
			directions.append("E")
		elif dx == -1 and dy == 0:
			directions.append("W")
		elif dx == 0 and dy == 1:
			directions.append("S")
		elif dx == 0 and dy == -1:
			directions.append("N")
	
	return "".join(directions)


