#!/usr/bin/python3

"""Script de prueba para verificar RecursiveBacktracker y la coherencia de Grid."""
import random
import sys
from pathlib import Path
# Permite importar el paquete mazegen localmente
sys.path.insert(0, str(Path(__file__).parent))

from mazegen.grid import Grid
from mazegen.strategies import RecursiveBacktracker
from mazegen.cell import Wall
from mazegen.pattern42 import apply_pattern_42
from mazegen.solver import find_shortest_path, path_to_directions

def verify_neighbor_coherence(grid: Grid) -> bool:
    """Verifica la coherencia del bitmask entre celdas vecinas."""
    for cell in grid:
        # Verificar pared Este / Oeste del vecino contiguo
        if cell.x + 1 < grid.width:
            east_neighbor = grid.get_cell(cell.x + 1, cell.y)
            if east_neighbor:
                has_east = cell.has_wall(Wall.EAST)
                has_west = east_neighbor.has_wall(Wall.WEST)
                if has_east != has_west:
                    print(f"Error E-W en ({cell.x}, {cell.y}) -> ({east_neighbor.x}, {east_neighbor.y})")
                    return False
        # Verificar pared Sur / Norte del vecino contiguo
        if cell.y + 1 < grid.height:
            south_neighbor = grid.get_cell(cell.x, cell.y + 1)
            if south_neighbor:
                has_south = cell.has_wall(Wall.SOUTH)
                has_north = south_neighbor.has_wall(Wall.NORTH)
                if has_south != has_north:
                    print(f"Error S-N en ({cell.x}, {cell.y}) -> ({south_neighbor.x}, {south_neighbor.y})")
                    return False
    return True


def print_ascii_maze(grid: Grid) -> None:
    """Imprime una representación ASCII simple del laberinto."""
    # Linea superior
    print("+" + "---+" * grid.width)

    for y in range(grid.height):
        # Lineas de celdas (paredes Este/Oeste)
        line = "|"
        for x in range(grid.width):
            cell = grid.get_cell(x, y)
            # Dentro del bucle for x in range(grid.width):
            if cell.is_42_cell:
                line += "███" if (x % 2 == 0) else "███" # Resalta el glifo 42
            else:
                line += "   " # Pasillo normal
            # Paredes Este ( o borde derecho)
            if cell and cell.has_wall(Wall.EAST):
                line += "|"
            else:
                line += " "
        print(line)

        # Linea inferior (paredes Sud)
        line = "+"
        for x in range(grid.width):
            cell = grid.get_cell(x, y)
            if cell and cell.has_wall(Wall.SOUTH):
                line += "---+"
            else:
                line += "   +"
        print(line)

def main() -> None: 
    # 1\. Fijar semilla para reproducibilidad (exigido por el sujeto)
    random.seed(4242)
    print("=== TEST DE GENERACIÓN: RecursiveBacktracker ===")
    width, height = 9, 7
    grid = Grid(width, height)
    entry = (0, 0)
    exit_pos = (9, 9)

    generator = RecursiveBacktracker()
    apply_pattern_42(grid)  # Para aplicar el 42 en el laberinto
    generator.generate(grid, entry, exit_pos)
    """ Para que encuentre el camindod el laberinto """
    path = find_shortest_path(grid, entry, exit_pos)
    print(f"Camino encontrado: {len(path)} pasos")
    print(f"Instrucciones: {path_to_directions(path)}")

    # 2\. Comprobación 1: Conectividad
    unvisited = [cell for cell in grid if not cell.visited]
    print(f"1. Celdas sin visitar: {len(unvisited)} (Esperado: 0)")
    assert len(unvisited) == 0, "¡Hay celdas desconectadas o sin visitar!"

    # 3. Comprobación 2: Coherencia de paredes compartidas
    coherent = verify_neighbor_coherence(grid)
    print(f"2. Coherencia Neighbor-to-Neighbor: {'OK' if coherent else 'FALLO'}")
    assert coherent, "¡Inconsistencia de muros entre celdas vecinas!"

    # 4. Comprobación 3: Matriz Hexadecimal
    print("\n3. Matriz Hexadecimal (0x0 a 0xF):")
    for y in range(grid.height):
        row_hex = "".join(
            grid.get_cell(x, y).hex_value
            for x in range(grid.width)
            if grid.get_cell(x, y)
        )
        print(f"Fila {y:02d}: {row_hex}")

    print("\n4. Visualización ASCII del laberinto (10x10):")
    print_ascii_maze(grid)
    print("\n¡Prueba completada con éxito!")


if __name__ == "__main__":
    main()
