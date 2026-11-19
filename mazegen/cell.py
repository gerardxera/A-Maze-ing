#!/usr/bin/python3
from __future__ import annotations
from enum import IntFlag


class Wall(IntFlag):

    """Mascara de bits para las 4 paredes cardinales del laberinto."""

    NONE = 0
    NORTH = 1  # Bit 0 (LSB)
    EAST = 2   # Bit 1
    SOUTH = 4  # Bit 2
    WEST = 8   # Bit 3
    ALL = NORTH | EAST | SOUTH | WEST  # 15 (0xF)

    @property
    def opposite(self) -> Wall:
        """Devuelve la pared opuesta (util para coherencia entre celdas)."""
        mapping = {
            Wall.NORTH: Wall.SOUTH,
            Wall.SOUTH: Wall.NORTH,
            Wall.EAST: Wall.WEST,
            Wall.WEST: Wall.EAST,
        }
        return mapping[self]


class Cell:
    """Representacion de una casilla individual
    dentro de la rejilla del laberinto."""

    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
        self.walls: Wall = Wall.ALL
        self.visited: bool = False
        self.is_42_cell: bool = False

    def has_wall(self, direction: Wall) -> bool:
        """Comprueba y devuelve True si esa pared especifica esta cerrada."""
        return bool(self.walls & direction)

    def remove_wall(self, direction: Wall) -> None:
        """Derriba la pared indicada (operacion bitwise)."""
        self.walls &= ~direction

    def add_wall(self, direction: Wall) -> None:
        """Cierra la pared indicada."""
        self.walls |= direction

    @property
    def hex_value(self) -> str:
        """Devuelve el valor de las paredes(celda) en hexadecimal (0 a F)."""
        return format(int(self.walls), "X")

    def __repr__(self) -> str:
        """Define como se muestra la celda
        al imprimirla (util para depurar)."""
        return (
            f"Cell(x={self.x}, y={self.y}, walls=0x{self.hex_value}, "
            f"visited={self.visited}, is_42={self.is_42_cell})"
        )
