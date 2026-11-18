#!/usr/bin/python3
"""Modulo para la resolucion de laberintos mediante BFS."""

from collections import deque
from mazegen.cell import Cell, Wall
from mazegen.grid import Grid

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
    """Encuentra el camino mas corto entre entry y exit_pos con BFS.

    Args:
        grid: Cuadricula del laberinto ya generado.
        entry: Coordenadas (x, y) de inicio.
        exit_pos: Coordenadas (x, y) de destino.

    Returns:
        Lista ordenada de coordenadas [(x, y), ...] desde entry hasta
        exit_pos, o lista vacia si no existe camino valido.
    """
    start_cell = grid.get_cell(entry[0], entry[1])
    target_cell = grid.get_cell(exit_pos[0], exit_pos[1])

    if start_cell is None or target_cell is None:
        return []

    if start_cell.is_42_cell or target_cell.is_42_cell:
        return []

    if entry == exit_pos:
        return [entry]

    queue: deque[Cell] = deque([start_cell])
    visited: set[tuple[int, int]] = {(start_cell.x, start_cell.y)}
    parent: dict[tuple[int, int], tuple[int, int]] = {}
    reached = False

    while queue:
        current = queue.popleft()

        if (current.x, current.y) == exit_pos:
            reached = True
            break

        for neighbor, wall in grid.get_neighbors(current):
            if neighbor.is_42_cell:
                continue

            if not current.has_wall(wall):
                coord = (neighbor.x, neighbor.y)
                if coord not in visited:
                    visited.add(coord)
                    parent[coord] = (current.x, current.y)
                    queue.append(neighbor)

    if not reached:
        return []

    path: list[tuple[int, int]] = []
    curr_coord: tuple[int, int] | None = exit_pos

    while curr_coord is not None:
        path.append(curr_coord)
        curr_coord = parent.get(curr_coord)

    path.reverse()
    return path


def path_to_directions(path: list[tuple[int, int]]) -> str:
    """Convierte una lista de coordenadas en direcciones (NESW).

    Args:
        path: Lista de tuplas (x, y) que forman el camino continuo.

    Returns:
        Cadena de texto con las direcciones (ej. 'EESW').
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
