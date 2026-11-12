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
from mazegen.encoder import serialize_maze, save_maze_to_file


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


def print_ascii_maze(
	grid: Grid,
	path: list[tuple[int, int]] | None = None
) -> None:
    """Imprime una representacion ASCII simetrica y resalta el camino resuelto."""
    path_set = set(path) if path else set()

    # 1. Techo superior del laberinto
    top_line = "+"
    for x in range(grid.width):
        cell = grid.get_cell(x, 0)
        top_line += "---+" if (cell and cell.has_wall(Wall.NORTH)) else "   +"
    print(top_line)

	# 2. Filas de celdas
    for y in range(grid.height):
        body_line = ""
        bottom_line = "+"

        for x in range(grid.width):
            cell = grid.get_cell(x, y)
            if cell is None:
                continue
			
			# Muro exterior izquierdo en la primera columna
            if x == 0:
                body_line += "|" if cell.has_wall(Wall.WEST) else " "

			# Contenido interior de la celda (3 caracteres de ancho)
            if cell.is_42_cell:
                body_line += "███"
            elif (x, y) in path_set:
                body_line += " * " # Resalta el camino resuelto con asterisco
            else:
                body_line += "   " # Espacio transitable vacio
			
			# Pared Este
            body_line += "|" if cell.has_wall(Wall.EAST) else " "

			# Pared Sur
            bottom_line += "---+" if cell.has_wall(Wall.SOUTH) else "   +"

        print(body_line)
        print(bottom_line)

def main() -> None: 
    # 1\. Fijar semilla para reproducibilidad (exigido por el sujeto)
    random.seed(4242)
    print("=== TEST DE GENERACIÓN: RecursiveBacktracker ===")
    width, height = 15, 15
    grid = Grid(width, height)
    entry = (0, 0)
    exit_pos = (width - 1, height - 1)

    generator = RecursiveBacktracker()
    apply_pattern_42(grid)  # Para aplicar el 42 en el laberinto
    generator.generate(grid, entry, exit_pos)
    
	# Resolver el laberinto
    path = find_shortest_path(grid, entry, exit_pos)
    print(f"Camino encontrado: {len(path)} pasos")
    print(f"Instrucciones: {path_to_directions(path)}")

	# Dibujar el laberinto con el camino trazado
    print("\nVisualizacion ASCII con el camino mas corto (*):")
    print_ascii_maze(grid, path=path)

    # 2\. Comprobacion 1: Conectividad
    unvisited = [cell for cell in grid if not cell.visited]
    print(f"1. Celdas sin visitar: {len(unvisited)} (Esperado: 0)")
    assert len(unvisited) == 0, "Hay celdas desconectadas o sin visitar!"

    # 3. Comprobacion 2: Coherencia de paredes compartidas
    coherent = verify_neighbor_coherence(grid)
    print(f"2. Coherencia Neighbor-to-Neighbor: {'OK' if coherent else 'FALLO'}")
    assert coherent, "Inconsistencia de muros entre celdas vecinas!"

    # 4. Comprobacion 3: Matriz Hexadecimal
    print("\n3. Matriz Hexadecimal (0x0 a 0xF):")
    for y in range(grid.height):
        row_hex = "".join(
            grid.get_cell(x, y).hex_value
            for x in range(grid.width)
            if grid.get_cell(x, y)
        )
        print(f"Fila {y:02d}: {row_hex}")

    print("\n4. Visualizacion ASCII del laberinto (10x10):")
    print_ascii_maze(grid)
    print("\nPrueba completada con exito!")

	# 5. Probar serializacion y guardado
    output_text = serialize_maze(grid, entry, exit_pos)
    print("\n--- SALIDA FORMAL (ENCODER) ---")
    print(output_text)

	# 6. Guardar en un archivo .txt para verificar
    save_maze_to_file("maze_output.txt", grid, entry, exit_pos)
    print("\nArchivo 'maze_output.txt' generado con exito!")

if __name__ == "__main__":
    main()
