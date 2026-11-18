#!/usr/bin/python3

"""Punto de entrada principal para ejecutar A-Maze-ing desde consola."""

import sys
from pydantic import ValidationError
from mazegen.generator import MazeGenerator, MazeResult
from ui.cli_menu import run_cli_menu
from ui.config_parser import MazeConfig, parse_config_file


class MazeAppAdapter:
    """Adapta MazeGenerator al MazeGeneratorProtocol esperado por la UI."""

    def __init__(self, config: MazeConfig) -> None:
        """Inicializa el generador real con los parámetros validados."""
        self.config = config
        self.generator = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit_pos=config.exit,
            perfect=config.perfect,
            seed=config.seed,
        )
        self.current_result: MazeResult = self.generator.generate()

    def generate(self) -> None:
        """Regenera un nuevo laberinto utilizando el motor algorítmico."""
        self.current_result = self.generator.generate()

    def get_grid(self) -> list[list[int]]:
        """Devuelve la matriz de enteros (0 a 15) para renderizador ASCII."""
        return self.current_result.grid.to_int_matrix()

    def get_shortest_path(self) -> list[tuple[int, int]]:
        """Devuelve las coordenadas del camino más corto hallado por BFS."""
        return self.current_result.path

    def write_output_file(self, path: str) -> None:
        """Serializa y guarda el archivo en formato oficial del subject."""
        self.current_result.save(path)


def main() -> None:
    """Punto de entrada principal con gestión de errores rigurosa."""
    if len(sys.argv) != 2:
        print(
            "Uso correcto: python3 a_maze_ing.py <config_file>",
            file=sys.stderr,
        )
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        # 1. Lectura y validación de config.txt con Pydantic
        config = parse_config_file(config_path)

        # 2. Instanciación del motor real conectado a la interfaz
        adapter = MazeAppAdapter(config)

        # 3. Guardado del primer laberinto (requisito del subject)
        adapter.write_output_file(config.output_file)

        # 4. Lanzar la interfaz interactiva en consola
        run_cli_menu(adapter, config)

    except (FileNotFoundError, ValueError, ValidationError, OSError) as err:
        print(f"Error de configuracion o ejecucion:\n{err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
