#!/usr/bin/python3
"""Modulo para la codificacion y serializacion del laberinto en formato estandar."""

from mazegen.grid import Grid
from mazegen.solver import find_shortest_path, path_to_directions


def encode_grid_to_hex(grid: Grid) -> list[str]:
    """Convierte la cuadricula del laberinto en una lista de cadenas hexadecimales.

    Cada linea representa una fila de celdas, donde cada caracter es el valor
    hexadecimal (0-F) del bitmask de paredes de esa celda.

    Args:
        grid: Cuadricula del laberinto generada.

    Returns:
        Lista de cadenas de texto con los valores hexadecimales por fila.
    """
    hex_rows: list[str] = []
    for y in range(grid.height):
        row_chars = []
        for x in range(grid.width):
            cell = grid.get_cell(x, y)
            if cell is not None:
                row_chars.append(cell.hex_value)
        hex_rows.append("".join(row_chars))
    return hex_rows


def serialize_maze(
    grid: Grid,
    entry: tuple[int, int],
    exit_pos: tuple[int, int]
) -> str:
    """Serializa el laberinto al formato oficial del subject.

    Estructura del archivo:
        1. Matriz de caracteres hexadecimales (una linea por fila).
        2. Linea en blanco.
        3. Coordenada de entrada.
        4. Coordenada de salida.
        5. Camino de solucion mas corto (NESW).

    Args:
        grid: Cuadricula del laberinto generada.
        entry: Coordenadas de inicio (x, y).
        exit_pos: Coordenadas de destino (x, y).

    Return:
        Cadena de texto lista para ser guardada en archivo o impresa por consola.
    """
    lines: list[str] = encode_grid_to_hex(grid)

    # 1. Linea vacia requerida tras la matriz hexadecimal
    lines.append("")

    # 2. Coordenadas de entrada (x,y)
    lines.append(f"{entry[0]},{entry[1]}")

    # 3. Coordenadas de salida (x,y)
    lines.append(f"{exit_pos[0]},{exit_pos[1]}")

    # 4. Solucion camino corto (ej. EENESS...)
    path = find_shortest_path(grid, entry, exit_pos)
    solution_str = path_to_directions(path)
    lines.append(solution_str)

    return "\n".join(lines)


def save_maze_to_file(
    filepath: str,
    grid: Grid,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
) -> None:
    """Guarda la representacion serializada del laberinto en un archivo de texto.

    Args:
        filepath: Ruta del archivo donde guardar la salida.
        grid: Cuadricula del laberinto.
        entry: Coordenada de entrada.
        exit_pos: Coordenada de salida.
    """
    content = serialize_maze(grid, entry, exit_pos)
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content + "\n")
