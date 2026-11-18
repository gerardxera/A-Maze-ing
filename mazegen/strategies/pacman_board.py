#!/usr/bin/python3
"""Modulo que implementa la estrategia de laberinto imperfecto Pac-Man."""

import random
from mazegen.cell import Cell, Wall
from mazegen.grid import Grid
from mazegen.strategies.base import GenerationStrategy
from mazegen.strategies.backtracker import RecursiveBacktracker


class PacmanBoard(GenerationStrategy):
    """Generador de laberintos imperfectos estilo Pac-Man (PERFECT=False).

    Garantiza conectividad total, las 4 esquinas y el centro abiertos,
    multiples rutas independientes (bucles), eliminacion de callejones sin
    salida evitables y prohibicion estricta de areas abiertas de 3x3.
    """

    def __init__(self, loop_factor: float = 0.15) -> None:
        """Inicializa la estrategia con el factor de bucles deseado.

        Args:
            loop_factor: Proporcion de paredes interiores a derribar.
        """
        self.loop_factor: float = loop_factor

    def generate(
        self,
        grid: Grid,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
    ) -> None:
        """Genera un tablero jugable cumpliendo las reglas de Pac-Man.

        Args:
            grid: Cuadricula del laberinto a modificar.
            entry: Coordenadas (x, y) de entrada.
            exit_pos: Coordenadas (x, y) de salida.
        """
        # 1. Base perfecta conexa (garantiza que no existan islas aisladas)
        RecursiveBacktracker().generate(grid, entry, exit_pos)

        # 2. Forzar las 4 esquinas y el centro como corredores abiertos
        self._ensure_open_corners_and_center(grid)

        # 3. Eliminar callejones sin salida (dead-ends)
        self._reduce_dead_ends(grid)

        # 4. Abrir bucles adicionales respetando la restriccion de no 3x3
        self._add_loops(grid)

        # 5. Segunda pasada de limpieza de dead-ends por seguridad
        self._reduce_dead_ends(grid)

    def _try_remove_wall(
        self,
        grid: Grid,
        cell_a: Cell,
        cell_b: Cell,
        direction: Wall,
    ) -> bool:
        """Derriba un muro solo si no genera un area abierta de 3x3.

        Args:
            grid: Cuadricula del laberinto.
            cell_a: Celda origen.
            cell_b: Celda vecina en la direccion indicada.
            direction: Direccion desde cell_a hacia cell_b.

        Returns:
            True si se derribo la pared; False si creaba un bloque 3x3.
        """
        if not cell_a.has_wall(direction):
            return True

        grid.remove_wall_between(cell_a, cell_b, direction)
        if self._has_open_3x3_near(grid, cell_a, cell_b):
            cell_a.add_wall(direction)
            cell_b.add_wall(direction.opposite)
            return False
        return True

    def _has_open_3x3_near(
        self,
        grid: Grid,
        cell_a: Cell,
        cell_b: Cell,
    ) -> bool:
        """Verifica si existe algun bloque 3x3 abierto cerca de las celdas."""
        min_x = max(0, min(cell_a.x, cell_b.x) - 2)
        max_x = min(grid.width - 3, max(cell_a.x, cell_b.x))
        min_y = max(0, min(cell_a.y, cell_b.y) - 2)
        max_y = min(grid.height - 3, max(cell_a.y, cell_b.y))

        for top_y in range(min_y, max_y + 1):
            for top_x in range(min_x, max_x + 1):
                if self._is_3x3_open(grid, top_x, top_y):
                    return True
        return False

    def _is_3x3_open(self, grid: Grid, top_x: int, top_y: int) -> bool:
        """Comprueba si la subcuadricula 3x3 en (top_x, top_y) esta abierta."""
        for dy in range(3):
            for dx in range(3):
                cell = grid.get_cell(top_x + dx, top_y + dy)
                if cell is None or cell.is_42_cell:
                    return False
                if dx < 2 and cell.has_wall(Wall.EAST):
                    return False
                if dy < 2 and cell.has_wall(Wall.SOUTH):
                    return False
        return True

    @staticmethod
    def _count_closed_walls(cell: Cell) -> int:
        """Cuenta cuantas de las 4 paredes cardinales estan cerradas."""
        cardinals = (Wall.NORTH, Wall.EAST, Wall.SOUTH, Wall.WEST)
        return sum(1 for w in cardinals if cell.has_wall(w))

    def _ensure_open_corners_and_center(self, grid: Grid) -> None:
        """Abre las 4 esquinas y asegura un corredor abierto en el centro."""
        corners: list[tuple[int, int]] = [
            (0, 0),
            (grid.width - 1, 0),
            (0, grid.height - 1),
            (grid.width - 1, grid.height - 1),
        ]

        for x, y in corners:
            corner_cell = grid.get_cell(x, y)
            if corner_cell is None or corner_cell.is_42_cell:
                continue
            for neighbor, direction in grid.get_neighbors(corner_cell):
                if not neighbor.is_42_cell:
                    self._try_remove_wall(
                        grid, corner_cell, neighbor, direction
                    )

        cx = grid.width // 2
        cy = grid.height // 2
        center_cell = grid.get_cell(cx, cy)

        if center_cell is None or center_cell.is_42_cell:
            valid_cells: list[Cell] = [
                cell for cell in grid if not cell.is_42_cell
            ]
            if valid_cells:
                center_cell = min(
                    valid_cells,
                    key=lambda c: abs(c.x - cx) + abs(c.y - cy),
                )

        if center_cell is None or center_cell.is_42_cell:
            return

        # Priorizar pasillo horizontal (E/W); si choca con el '42', usar N/S
        neighbors = grid.get_neighbors(center_cell)
        horiz = [
            (n, d) for n, d in neighbors
            if not n.is_42_cell and d in (Wall.EAST, Wall.WEST)
        ]
        vert = [
            (n, d) for n, d in neighbors
            if not n.is_42_cell and d in (Wall.NORTH, Wall.SOUTH)
        ]

        for neighbor, direction in horiz:
            self._try_remove_wall(grid, center_cell, neighbor, direction)

        # Garantizar al menos 2 salidas abiertas en la celda central
        if self._count_closed_walls(center_cell) >= 3:
            for neighbor, direction in vert:
                self._try_remove_wall(grid, center_cell, neighbor, direction)
                if self._count_closed_walls(center_cell) <= 2:
                    break

    def _reduce_dead_ends(self, grid: Grid) -> None:
        """Elimina callejones sin salida respetando el limite de 3x3."""
        for _ in range(3):
            changed = False
            for cell in grid:
                if cell.is_42_cell or self._count_closed_walls(cell) < 3:
                    continue

                candidates: list[tuple[Cell, Wall]] = [
                    (neighbor, direction)
                    for neighbor, direction in grid.get_neighbors(cell)
                    if not neighbor.is_42_cell and cell.has_wall(direction)
                ]
                random.shuffle(candidates)

                for neighbor, direction in candidates:
                    if self._try_remove_wall(grid, cell, neighbor, direction):
                        changed = True
                        break
            if not changed:
                break

    def _add_loops(self, grid: Grid) -> None:
        """Derriba un porcentaje de muros interiores sin crear bloques 3x3."""
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
        target = max(2, int(len(interior_walls) * self.loop_factor))
        removed = 0

        for cell_a, cell_b, direction in interior_walls:
            if removed >= target:
                break
            if self._try_remove_wall(grid, cell_a, cell_b, direction):
                removed += 1
