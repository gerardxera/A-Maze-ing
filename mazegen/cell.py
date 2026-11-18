#!/usr/bin/python3
"""Modulo que define el modelo de celda y mascara de bits de paredes."""

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
    def opposite(self) -> "Wall":
        """Devuelve la pared opuesta para mantener coherencia simetrica."""
        mapping: dict[Wall, Wall] = {
            Wall.NORTH: Wall.SOUTH,
            Wall.SOUTH: Wall.NORTH,
            Wall.EAST: Wall.WEST,
            Wall.WEST: Wall.EAST,
        }
        if self not in mapping:
            raise ValueError(
                f"La direccion {self!r} no tiene una unica pared opuesta."
            )
        return mapping[self]


class Cell:
    """Representacion de una casilla individual dentro de la rejilla."""

    def __init__(self, x: int, y: int) -> None:
        """Inicializa una celda en (x, y) con sus 4 paredes cerradas.

        Args:
            x: Coordenada horizontal (columna).
            y: Coordenada vertical (fila).
        """
        self.x: int = x
        self.y: int = y
        self.walls: Wall = Wall.ALL
        self.visited: bool = False
        self.is_42_cell: bool = False

    def has_wall(self, direction: Wall) -> bool:
        """Devuelve True si la pared indicada esta cerrada."""
        return bool(self.walls & direction)

    def remove_wall(self, direction: Wall) -> None:
        """Derriba la pared indicada mediante operacion bitwise."""
        self.walls &= ~direction

    def add_wall(self, direction: Wall) -> None:
        """Cierra la pared indicada mediante operacion bitwise."""
        self.walls |= direction

    @property
    def hex_value(self) -> str:
        """Devuelve el valor de las paredes en hexadecimal (0 a F)."""
        return format(int(self.walls), "X")

    def __repr__(self) -> str:
        """Representacion textual de la celda para depuracion."""
        return (
            f"Cell(x={self.x}, y={self.y}, walls=0x{self.hex_value}, "
            f"visited={self.visited}, is_42={self.is_42_cell})"
        )
