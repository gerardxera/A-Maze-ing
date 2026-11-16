#!/usr/bin/python3

"""Módulo que implementa la estrategia de laberinto imperfecto tipo Pac-Man."""

import random
from mazegen.cell import Cell, Wall
from mazegen.grid import Grid
from mazegen.strategies.base import GenerationStrategy
from mazegen.strategies.backtracker import RecursiveBacktracker


class PacmanBoard(GenerationStrategy):
    """Generador de laberintos imperfectos con bucles, esquinas y centro abiertos.

    Cumple los requisitos del subject para PERFECT=False:
    - Conectividad total.
    - Las 4 esquinas y el centro son corredores abiertos.
    - Múltiples rutas independientes (bucles).
    - Minimización drástica de callejones sin salida (dead-ends).
    """

    def __init__(self, loop_factor: float = 0.20) -> None:
        """Inicializa la estrategia con el factor de bucles deseado..

        Args:
            loop_factor: Proporcion de paredes interiores a derribar para bucles.
        """
        self.loop_factor = loop_factor

    def generate(
        self,
        grid: Grid,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
    ) -> None:
        """Genera el tablero jugable aplicando las reglas del modo Pac-Man.

        Args:
            grid: Cuadrícula del laberinto.
            entry: Coordenada de inicio (x, y).
            exit_pos: Coordenada de fin (x, y).
        """
        # 1. Base perfecta conexa con Recursive Backtracker (ninguna celda queda aislada)
        RecursiveBacktracker().generate(grid, entry, exit_pos)

        # 2. Forzar esquinas y corredor central abiertos (requisito del subject)
        self._ensure_open_corners_and_center(grid)

        # 3. Reducir callejones sin salida (dead-ends)
        self._reduce_dead_ends(grid)

        # 4. Derribar paredes interiores adicionales para crear rutas alternativas (bucles)
        self._add_loops(grid)

    def _ensure_open_corners_and_center(self, grid: Grid) -> None:
        """Abre las 4 esquinas y un corredor en la zona central navegable."""
        # Las 4 esquinas
        corners = [
            (0, 0),
            (grid.width - 1, 0),
            (0, grid.height - 1),
            (grid.width - 1, grid.height - 1),
        ]

        for x, y in corners:
            cell = grid.get_cell(x, y)
            if cell is None or cell.is_42_cell:
                continue

            # Abrir hacia los vecinos interiores
            for neighbor, direction in grid.get_neighbors(cell):
                if not neighbor.is_42_cell and cell.has_wall(direction):
                    grid.remove_wall_between(cell, neighbor, direction)

        # Zona central: si el punto medio cae dentro del 42, buscar la fila transitable más próxima
        cx = grid.width // 2
        cy = grid.height // 2
        center_cell = grid.get_cell(cx, cy)

        if center_cell is None or center_cell.is_42_cell:
            valid_cells = []
            for y in range(grid.height):
                cell = grid.get_cell(cx, y)
                if cell is not None and not cell.is_42_cell:
                    valid_cells.append(cell)

            if valid_cells:
                center_cell = min(valid_cells, key=lambda c: abs(c.y - cy))

        # Abrir pasillo horizontal en el centro
        if center_cell is not None and not center_cell.is_42_cell:
            for neighbor, direction in grid.get_neighbors(center_cell):
                if not neighbor.is_42_cell and direction in (Wall.EAST, Wall.WEST):
                    if center_cell.has_wall(direction):
                        grid.remove_wall_between(center_cell, neighbor, direction)

    def _reduce_dead_ends(self, grid: Grid) -> None:
        """Abre una salida adicional en celdas que solo cuentan con una dirección abierta."""
        for cell in grid:
            if cell.is_42_cell:
                continue

            closed = [
                w for w in (Wall.NORTH, Wall.EAST, Wall.SOUTH, Wall.WEST)
                if cell.has_wall(w)
            ]

            # Si tiene 3 paredes cerradas, es un dead-end (solo 1 salida)
            if len(closed) == 3:
                candidates = [
                    (neighbor, direction)
                    for neighbor, direction in grid.get_neighbors(cell)
                    if not neighbor.is_42_cell and cell.has_wall(direction)
                ]
                if candidates:
                    chosen_neighbor, chosen_dir = random.choice(candidates)
                    grid.remove_wall_between(cell, chosen_neighbor, chosen_dir)

    def _add_loops(self, grid: Grid) -> None:
        """Derriba aleatoriamente un porcentaje de paredes interiores para crear bucles."""
        interior_walls: list[tuple[Cell, Cell, Wall]] = []

        for y in range(grid.height):
            for x in range(grid.width):
                cell = grid.get_cell(x, y)
                if cell is None or cell.is_42_cell:
                    continue

                for direction in (Wall.EAST, Wall.SOUTH):
                    if not cell.has_wall(direction):
                        continue

                    dx = 1 if direction == Wall.EAST else 0
                    dy = 1 if direction == Wall.SOUTH else 0
                    neighbor = grid.get_cell(x + dx, y + dy)

                    if neighbor is not None and not neighbor.is_42_cell:
                        interior_walls.append((cell, neighbor, direction))

        random.shuffle(interior_walls)
        target = int(len(interior_walls) * self.loop_factor)

        for cell_a, cell_b, direction in interior_walls[:target]:
            grid.remove_wall_between(cell_a, cell_b, direction)
