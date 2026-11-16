#!/usr/bin/python3

"""Modulo para la definicion e insercion del patron '42' en la cuadricula."""

from mazegen.grid import Grid
from mazegen.cell import Wall

# Matriz binaria que dibuja el 42 (1 = celda muro del patron, 0 = espacio libre)
# Dimensiones: 5 filas x 7 columnas
PATTERN_42: list[list[int]] = [
    [1, 0, 0, 0, 1, 1, 1],  # Fila 0: parte alta del 4 y techo del 2
    [1, 0, 0, 0, 0, 0, 1],  # Fila 1: baja la izquierda del 4 y la derecha del 2
    [1, 1, 1, 0, 1, 1, 1],  # Fila 2: puente central de ambos numeros
    [0, 0, 1, 0, 1, 0, 0],  # Fila 3: baja la derecha del 4 y la izquierda del 2
    [0, 0, 1, 0, 1, 1, 1],  # Fila 4: base del 4 y base del 2
]

PATTERN_HEIGHT: int = len(PATTERN_42)
PATTERN_WIDTH: int = len(PATTERN_42[0])


def apply_pattern_42(grid: Grid) -> bool:
    """Inserta el patron '42' centrado en la cuadricula.

    Marca las celdas del patron como visitadas y con todas las paredes cerradas
    para que los algoritmos de generacion las rodeen sin alterarlas.

    Args:
        grid: Instancia de la cuadricula donde aplicar el patron.

    Returns:
        True si el patron se pudo colocar, False si la cuadricula es demasiado pequenya.
    """
    # Requiere al menos un margen de 1 celda por cada lado (minimo PATTERN + 2)
    min_width = PATTERN_WIDTH + 2
    min_height = PATTERN_HEIGHT + 2

    if grid.width < min_width or grid.height < min_height:
        print(
            f"Aviso: La cuadricula ({grid.width}x{grid.height}) es demasiado "
            f"pequenya para el patron '42' (minimo requerido: {min_width}x{min_height})."
        )
        return False
    # Calcular desfase para centrar el patron
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
