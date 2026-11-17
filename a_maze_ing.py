#!/usr/bin/python3
"""Punto de entrada principal para ejecutar A-Maze-ing desde consola."""

# ============================================================================
# IMPORTACIONES
# Qué hacen: Traen sys (para leer argumentos de terminal y salir con codigos
# de error), random (para simular datos de prueba), ValidationError (para
# atrapar errores de Pydantic) y nuestros modulos de ui/.
# Por qué: El Cap. IV.2 exige ejecutar `python3 a_maze_ing.py config.txt` y
# manejar cualquier fallo sin que Python lance un traceback descontrolado.
# ============================================================================
import random
import sys
from pydantic import ValidationError
from ui.cli_menu import run_cli_menu
from ui.config_parser import parse_config_file


# ============================================================================
# CLASE TEMPORAL: MockMazeGenerator
# Qué hace: Simula el comportamiento de la clase MazeGenerator de tu compañero
# mientras el termina de juntar sus archivos en mazegen/generator.py.
# Cómo funciona: Construye una matriz de enteros con paredes exteriores,
# abre un camino aleatorio conectado, dibuja un bloque '42' en el centro (si
# cabe) y guarda el formato hexadecimal real exigido por el subject.
# Por qué: Te permite probar TODO tu trabajo (parser, colores, menu, ruta
# y archivo de salida) hoy mismo de forma totalmente independiente.
# ============================================================================
class MockMazeGenerator:
    """Simulador temporal del backend para probar la interfaz visual."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        perfect: bool,
        seed: int | None = None,
    ) -> None:
        """Inicializa los parametros del laberinto simulado."""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self._rng = random.Random(seed)
        self._grid: list[list[int]] = []
        self._path: list[tuple[int, int]] = []

    def generate(self) -> None:
        """Genera un tablero de prueba coherente con paredes y pasillos."""
        # Inicia todas las celdas con las 4 paredes cerradas (15)
        grid = [[15 for _ in range(self.width)] for _ in range(self.height)]

        # Abre pasillos simples tipo Binary Tree para tener paredes coherentes
        for y in range(self.height):
            for x in range(self.width):
                dirs: list[str] = []
                if x + 1 < self.width:
                    dirs.append("E")
                if y + 1 < self.height:
                    dirs.append("S")
                if dirs:
                    choice = self._rng.choice(dirs)
                    if choice == "E":
                        grid[y][x] &= ~2       # Quita pared Este (2)
                        grid[y][x + 1] &= ~8   # Quita pared Oeste vecino (8)
                    else:
                        grid[y][x] &= ~4       # Quita pared Sur (4)
                        grid[y + 1][x] &= ~1   # Quita pared Norte vecino (1)

        # Inserta un bloque '42' de prueba en el centro si el mapa es grande
        if self.width >= 11 and self.height >= 9:
            cx, cy = self.width // 2, self.height // 2
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    px, py = cx + dx, cy + dy
                    if (px, py) not in {self.entry, self.exit}:
                        grid[py][px] = 15

        self._grid = grid
        self._path = self._build_dummy_path()

    def _build_dummy_path(self) -> list[tuple[int, int]]:
        """Crea una ruta de ejemplo desde entry hasta exit para probar UI."""
        path: list[tuple[int, int]] = [self.entry]
        cx, cy = self.entry
        tx, ty = self.exit
        while cx != tx:
            cx += 1 if tx > cx else -1
            path.append((cx, cy))
        while cy != ty:
            cy += 1 if ty > cy else -1
            path.append((cx, cy))
        return path

    def get_grid(self) -> list[list[int]]:
        """Devuelve la matriz de enteros del laberinto."""
        return self._grid

    def get_shortest_path(self) -> list[tuple[int, int]]:
        """Devuelve la lista de coordenadas del camino."""
        return self._path

    def get_path_directions(self) -> str:
        """Convierte la ruta en letras N, E, S, W."""
        dirs: list[str] = []
        for i in range(len(self._path) - 1):
            x1, y1 = self._path[i]
            x2, y2 = self._path[i + 1]
            if x2 > x1:
                dirs.append("E")
            elif x2 < x1:
                dirs.append("W")
            elif y2 > y1:
                dirs.append("S")
            elif y2 < y1:
                dirs.append("N")
        return "".join(dirs)

    def to_hex_output(self) -> str:
        """Convierte la matriz de enteros a texto hexadecimal por filas."""
        rows = [
            "".join(format(val, "X") for val in row) for row in self._grid
        ]
        return "\n".join(rows)

    def write_output_file(self, path: str) -> None:
        """Escribe el archivo de salida en el formato oficial del subject."""
        lines = [
            self.to_hex_output(),
            "",
            f"{self.entry[0]},{self.entry[1]}",
            f"{self.exit[0]},{self.exit[1]}",
            self.get_path_directions(),
        ]
        with open(path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n")


# ============================================================================
# FUNCIÓN PRINCIPAL: main
# Qué hace: Orquesta todo el flujo de ejecucion del programa desde que se
# lanza en terminal hasta que se abre el menu interactivo.
# Cómo funciona:
#   1. Comprueba que haya exactamente 1 argumento (el archivo config.txt).
#   2. Valida la configuracion con parse_config_file().
#   3. Instancia el generador, crea el primer laberinto y lo guarda en disco.
#   4. Arranca el menu visual en consola.
#   5. Atrapa cualquier excepcion y muestra un mensaje limpio en stderr.
# Por qué: Garantiza tolerancia total a fallos (Cap. III.1 y IV.2).
# ============================================================================
def main() -> None:
    """Punto de entrada principal de la aplicacion A-Maze-ing."""
    if len(sys.argv) != 2:
        print(
            "Uso correcto: python3 a_maze_ing.py <archivo_config>",
            file=sys.stderr,
        )
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        config = parse_config_file(config_path)
        generator = MockMazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit,
            perfect=config.perfect,
            seed=config.seed,
        )
        generator.generate()
        generator.write_output_file(config.output_file)
        run_cli_menu(generator, config)
    except (FileNotFoundError, ValueError, ValidationError, OSError) as err:
        print(f"Error de configuracion o ejecucion:\n{err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
