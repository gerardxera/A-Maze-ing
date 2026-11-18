#!/usr/bin/python3
"""Modulo para la definicion e insercion del patron '42'."""

from mazegen.cell import Wall
from mazegen.grid import Grid

# Matriz binaria del '42' (1 = celda cerrada, 0 = espacio libre)
# Dimensiones: 5 filas x 7 columnas
PATTERN_42: list[list[int]] = [
    [1, 0, 0, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 1, 1],
]

PATTERN_HEIGHT: int = len(PATTERN_42)
PATTERN_WIDTH: int = len(PATTERN_42[0])


def apply_pattern_42(grid: Grid) -> bool:
    """Inserta el patron '42' centrado en la cuadricula.

    Marca las celdas del patron como visitadas y con sus 4 paredes
    cerradas para que los algoritmos las rodeen sin alterarlas.

    Args:
        grid: Instancia de la cuadricula donde aplicar el patron.

    Returns:
        True si el patron cabe y se aplica; False si es muy pequena.
    """
    min_width = PATTERN_WIDTH + 2
    min_height = PATTERN_HEIGHT + 2

    if grid.width < min_width or grid.height < min_height:
        print(
            f"Error: Cuadricula ({grid.width}x{grid.height}) demasiado "
            f"pequena para el patron '42' "
            f"(minimo: {min_width}x{min_height})."
        )
        return False

    start_x = (grid.width - PATTERN_WIDTH) // 2
    start_y = (grid.height - PATTERN_HEIGHT) // 2

    for py, row in enumerate(PATTERN_42):
        for px, val in enumerate(row):
            if val == 1:
                cell = grid.get_cell(start_x + px, start_y + py)
                if cell is not None:
                    cell.is_42_cell = True
                    cell.visited = True
                    cell.walls = Wall.ALL

    return True
