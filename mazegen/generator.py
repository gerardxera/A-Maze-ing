#!/usr/bin/python3

"""Módulo principal que proporciona la interfaz de alto nivel MazeGenerator."""

import random
from dataclasses import dataclass

from mazegen.grid import Grid
from mazegen.pattern42 import apply_pattern_42
from mazegen.strategies.base import GenerationStrategy
from mazegen.strategies.backtracker import RecursiveBacktracker
from mazegen.strategies.pacman_board import PacmanBoard
from mazegen.solver import find_shortest_path, path_to_directions
from mazegen.encoder import serialize_maze, save_maze_to_file


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
        width: int,
        height: int,
        entry: tuple[int, int] = (0, 0),
        exit_pos: tuple[int, int] | None = None,
        perfect: bool = True,
        seed: int | None = None,
        strategy: GenerationStrategy | None = None,
    ) -> None:
        """Inicializa el generador con los parámetros del laberinto.

        Args:
            width: Ancho de la cuadricula.
            height: Alto de la cuadricula.
            entry: Coordenadas de inicio.
            exit_pos: Coordenadas de fin. Si es None, se usa la esquina inferior derecha.
            perfect: True para laberinto perfecto, False para modo Pac-Man.
            seed: Semilla para reproducibilidad.
            strategy: Estrategia personalizada (opcional).
        """
        if width <= 0 or height <= 0:
            raise ValueError("Las dimensiones deben ser positivas.")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos if exit_pos is not None else (width - 1, height - 1)
        self.perfect = perfect
        self.seed = seed
        self.strategy = strategy

        if not (0 <= self.entry[0] < width and 0 <= self.entry[1] < height):
            raise ValueError(f"Entrada {entry} fuera de límites.")
        if not (0 <= self.exit_pos[0] < width and 0 <= self.exit_pos[1] < height):
            raise ValueError(f"Salida {self.exit_pos} fuera de límites.")

    def generate(self) -> MazeResult:
        """Genera y resuelve el laberinto con los parámetros configurados."""
        if self.seed is not None:
            random.seed(self.seed)

        grid = Grid(self.width, self.height)
        apply_pattern_42(grid)

        selected = self.strategy
        if selected is None:
            selected = RecursiveBacktracker() if self.perfect else PacmanBoard()

        selected.generate(grid, self.entry, self.exit_pos)

        path = find_shortest_path(grid, self.entry, self.exit_pos)
        solution = path_to_directions(path)

        return MazeResult(
            grid=grid,
            entry=self.entry,
            exit_pos=self.exit_pos,
            path=path,
            solution=solution,
        )
