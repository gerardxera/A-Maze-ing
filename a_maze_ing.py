#!/usr/bin/python3

import sys
from pydantic import ValidationError
from mazegen.generator import MazeGenerator, MazeResult
from ui.cli_menu import run_cli_menu
from ui.config_parser import parse_config_file


class MazeGeneratorAdapter:
    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        perfect: bool,
        seed: int | None = None,
    ) -> None:
        self._generator = MazeGenerator(
            width=width,
            height=height,
            entry=entry,
            exit_pos=exit,
            perfect=perfect,
            seed=seed,
        )
        self._result: MazeResult | None = None

    def generate(self) -> None:
        self._result = self._generator.generate()

    def get_grid(self) -> list[list[int]]:
        """Devuelve la matriz de paredes (0 a 15) para el renderizador."""
        if self._result is None:
            raise RuntimeError("El laberinto aun no ha sido generado.")
        return self._result.grid.to_int_matrix()

    def get_shortest_path(self) -> list[tuple[int, int]]:
        """Devuelve las coordenadas (x, y) del camino mas corto."""
        if self._result is None:
            raise RuntimeError("El laberinto aun no ha sido generado.")
        return list(self._result.path)

    def write_output_file(self, path: str) -> None:
        """Guarda el laberinto en disco con el formato oficial."""
        if self._result is None:
            raise RuntimeError("El laberinto aun no ha sido generado.")
        self._result.save(path)


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
        generator = MazeGeneratorAdapter(
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
    except (
        FileNotFoundError,
        ValueError,
        ValidationError,
        OSError,
        RuntimeError
    ) as err:
        print(f"Error de configuracion o ejecucion:\n{err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
