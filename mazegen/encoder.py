#!/usr/bin/python3
"""Modulo para la codificacion y serializacion del laberinto."""

from mazegen.grid import Grid
from mazegen.solver import find_shortest_path, path_to_directions


def encode_grid_to_hex(grid: Grid) -> list[str]:
    """Convierte la cuadricula en una lista de cadenas hexadecimales.

    Args:
        grid: Cuadricula del laberinto generada.

    Returns:
        Lista de cadenas con los valores hexadecimales por fila.
    """
    hex_rows: list[str] = []
    for y in range(grid.height):
        row_chars: list[str] = []
        for x in range(grid.width):
            cell = grid.get_cell(x, y)
            if cell is not None:
                row_chars.append(cell.hex_value)
        hex_rows.append("".join(row_chars))
    return hex_rows


def serialize_maze(
    grid: Grid,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
) -> str:
    """Serializa el laberinto al formato oficial del subject.

    Args:
        grid: Cuadricula del laberinto generada.
        entry: Coordenadas de inicio (x, y).
        exit_pos: Coordenadas de destino (x, y).

    Returns:
        Cadena de texto lista para guardarse en el archivo de salida.
    """
    lines: list[str] = encode_grid_to_hex(grid)
    lines.append("")
    lines.append(f"{entry[0]},{entry[1]}")
    lines.append(f"{exit_pos[0]},{exit_pos[1]}")

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
    """Guarda la representacion serializada en un archivo de texto.

    Args:
        filepath: Ruta del archivo donde guardar la salida.
        grid: Cuadricula del laberinto.
        entry: Coordenada de entrada.
        exit_pos: Coordenada de salida.

    Raises:
        OSError: Si ocurre un error de permisos o escritura en disco.
    """
    content = serialize_maze(grid, entry, exit_pos)
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content + "\n")
    except OSError as exc:
        raise OSError(
            f"No se pudo escribir el archivo '{filepath}': {exc}"
        ) from exc
