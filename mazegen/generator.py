#!/usr/bin/python3
"""Modulo principal que proporciona la interfaz publica MazeGenerator."""

import random
from dataclasses import dataclass

from mazegen.encoder import (
    encode_grid_to_hex,
    save_maze_to_file,
    serialize_maze,
)
from mazegen.grid import Grid
from mazegen.pattern42 import apply_pattern_42
from mazegen.solver import find_shortest_path, path_to_directions
from mazegen.strategies.backtracker import RecursiveBacktracker
from mazegen.strategies.base import GenerationStrategy
from mazegen.strategies.pacman_board import PacmanBoard


@dataclass
class MazeResult:
    """Contenedor de resultados del laberinto generado."""

    grid: Grid
    entry: tuple[int, int]
    exit_pos: tuple[int, int]
    path: list[tuple[int, int]]
    solution: str

    def to_string(self) -> str:
        """Devuelve el laberinto serializado en el formato oficial."""
        return serialize_maze(self.grid, self.entry, self.exit_pos)

    def save(self, filepath: str) -> None:
        """Guarda el laberinto en un archivo de texto."""
        save_maze_to_file(filepath, self.grid, self.entry, self.exit_pos)


class MazeGenerator:
    """Fachada principal para la generacion y resolucion de laberintos."""

    def __init__(
        self,
        width: int = 20,
        height: int = 15,
        entry: tuple[int, int] = (0, 0),
        exit_pos: tuple[int, int] | None = None,
        perfect: bool = False,
        seed: int | None = None,
        strategy: GenerationStrategy | None = None,
    ) -> None:
        """Inicializa los parametros por defecto del generador.

        Args:
            width: Ancho del laberinto en celdas.
            height: Alto del laberinto en celdas.
            entry: Coordenadas (x, y) de entrada.
            exit_pos: Coordenadas (x, y) de salida.
            perfect: True para laberinto perfecto; False para modo Pac-Man.
            seed: Semilla opcional para reproducibilidad.
            strategy: Estrategia de generacion personalizada opcional.
        """
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit_pos: tuple[int, int] | None = exit_pos
        self.perfect: bool = perfect
        self.seed: int | None = seed
        self.strategy: GenerationStrategy | None = strategy
        self._result: MazeResult | None = None

    def generate(
        self,
        width: int | None = None,
        height: int | None = None,
        entry: tuple[int, int] | None = None,
        exit_pos: tuple[int, int] | None = None,
        perfect: bool | None = None,
        seed: int | None = None,
    ) -> MazeResult:
        """Genera y resuelve un laberinto completo.

        Args:
            width: Ancho de la cuadricula (sobrescribe el de __init__).
            height: Alto de la cuadricula (sobrescribe el de __init__).
            entry: Coordenadas (x, y) de inicio.
            exit_pos: Coordenadas (x, y) de fin.
            perfect: True para laberinto perfecto, False para imperfecto.
            seed: Semilla opcional para reproducibilidad estricta.

        Returns:
            MazeResult con la cuadricula, coordenadas, camino y solucion.

        Raises:
            ValueError: Si las dimensiones o coordenadas son invalidas.
        """
        w = width if width is not None else self.width
        h = height if height is not None else self.height
        ent = entry if entry is not None else self.entry
        ext_cfg = exit_pos if exit_pos is not None else self.exit_pos
        is_perf = perfect if perfect is not None else self.perfect
        active_seed = seed if seed is not None else self.seed

        if w <= 0 or h <= 0:
            raise ValueError("Las dimensiones deben ser positivas.")

        actual_exit = ext_cfg if ext_cfg is not None else (w - 1, h - 1)

        if not (0 <= ent[0] < w and 0 <= ent[1] < h):
            raise ValueError(f"Entrada {ent} fuera de limites.")
        if not (0 <= actual_exit[0] < w and 0 <= actual_exit[1] < h):
            raise ValueError(f"Salida {actual_exit} fuera de limites.")
        if ent == actual_exit:
            raise ValueError(
                "La entrada y la salida deben tener coordenadas distintas."
            )

        if active_seed is not None:
            random.seed(active_seed)
        else:
            random.seed()

        grid = Grid(w, h)
        apply_pattern_42(grid)

        ent_cell = grid.get_cell(ent[0], ent[1])
        ext_cell = grid.get_cell(actual_exit[0], actual_exit[1])
        if (ent_cell is not None and ent_cell.is_42_cell) or (
            ext_cell is not None and ext_cell.is_42_cell
        ):
            raise ValueError(
                "La entrada o la salida colisiona con una celda del '42'."
            )

        selected = self.strategy
        if selected is None:
            selected = RecursiveBacktracker() if is_perf else PacmanBoard()

        selected.generate(grid, ent, actual_exit)

        path = find_shortest_path(grid, ent, actual_exit)
        solution = path_to_directions(path)

        self._result = MazeResult(
            grid=grid,
            entry=ent,
            exit_pos=actual_exit,
            path=path,
            solution=solution,
        )
        return self._result

    def _require_result(self) -> MazeResult:
        """Verifica que generate() se haya ejecutado antes de consultar."""
        if self._result is None:
            raise RuntimeError(
                "Debe llamar a generate() antes de acceder al resultado."
            )
        return self._result

    def get_grid(self) -> list[list[int]]:
        """Retorna la matriz de enteros con los estados de cada celda."""
        return self._require_result().grid.to_int_matrix()

    def get_shortest_path(self) -> list[tuple[int, int]]:
        """Retorna la secuencia de coordenadas del camino mas corto."""
        return self._require_result().path

    def get_path_directions(self) -> str:
        """Retorna el camino mas corto serializado en texto ('NESW')."""
        return self._require_result().solution

    def to_hex_output(self) -> str:
        """Serializa la cuadricula completa a formato hexadecimal."""
        res = self._require_result()
        return "\n".join(encode_grid_to_hex(res.grid))

    def write_output_file(self, path: str) -> None:
        """Escribe el fichero de salida en el formato exigido."""
        self._require_result().save(path)
