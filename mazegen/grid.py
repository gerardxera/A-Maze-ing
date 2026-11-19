#!/usr/bin/python3
"""Modulo que define la clase Grid para gestionar la cuadricula."""

from typing import Iterator
from mazegen.cell import Cell, Wall


class Grid:
    """Modelo de la cuadricula bidimensional de celdas."""

    def __init__(self, width: int, height: int) -> None:
        """Inicializa la cuadricula con todas las celdas cerradas.

        Args:
            width: Ancho de la cuadricula (columnas).
            height: Alto de la cuadricula (filas).

        Raises:
            ValueError: Si el ancho o el alto no son positivos.
        """
        if width <= 0 or height <= 0:
            raise ValueError(
                "Las dimensiones de la cuadricula deben ser positivas."
            )

        self.width: int = width
        self.height: int = height
        self._matrix: list[list[Cell]] = [
            [Cell(x, y) for x in range(width)] for y in range(height)
        ]

    def get_cell(self, x: int, y: int) -> Cell | None:
        """Obtiene la celda en (x, y) si esta dentro de los limites."""
        if self.is_valid_coord(x, y):
            return self._matrix[y][x]
        return None

    def is_valid_coord(self, x: int, y: int) -> bool:
        """Verifica si las coordenadas (x, y) pertenecen a la rejilla."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_neighbors(self, cell: Cell) -> list[tuple[Cell, Wall]]:
        """Devuelve los vecinos adyacentes validos y su direccion.

        Args:
            cell: Celda de referencia.

        Returns:
            Lista de tuplas (celda_vecina, pared_hacia_el_vecino).
        """
        directions: list[tuple[int, int, Wall]] = [
            (0, -1, Wall.NORTH),
            (1, 0, Wall.EAST),
            (0, 1, Wall.SOUTH),
            (-1, 0, Wall.WEST),
        ]
        neighbors: list[tuple[Cell, Wall]] = []
        for dx, dy, direction in directions:
            neighbor = self.get_cell(cell.x + dx, cell.y + dy)
            if neighbor is not None:
                neighbors.append((neighbor, direction))
        return neighbors

    def remove_wall_between(
        self,
        cell_a: Cell,
        cell_b: Cell,
        direction: Wall,
    ) -> None:
        """Derriba simetricamente la pared entre dos celdas contiguas.

        Args:
            cell_a: Celda origen.
            cell_b: Celda destino adyacente.
            direction: Direccion desde cell_a hacia cell_b.
        """
        cell_a.remove_wall(direction)
        cell_b.remove_wall(direction.opposite)

    def to_int_matrix(self) -> list[list[int]]:
        """Exporta la cuadricula a una matriz de enteros (0 a 15)."""
        return [[int(cell.walls) for cell in row] for row in self._matrix]

    def __iter__(self) -> Iterator[Cell]:
        """Itera sobre todas las celdas de la cuadricula fila por fila."""
        for row in self._matrix:
            for cell in row:
                yield cell

    def __repr__(self) -> str:
        """Representacion textual basica para depuracion."""
        return f"Grid(width={self.width}, height={self.height})"
