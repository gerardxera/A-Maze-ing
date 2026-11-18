#!/usr/bin/python3
"""Libreria backend mazegen para la generacion y gestion de laberintos."""

from mazegen.cell import Cell, Wall
from mazegen.grid import Grid
from mazegen.generator import MazeGenerator, MazeResult
from mazegen.solver import find_shortest_path, path_to_directions
from mazegen.encoder import (
    serialize_maze,
    save_maze_to_file,
    encode_grid_to_hex,
)
from mazegen.strategies import (
    GenerationStrategy,
    PacmanBoard,
    RecursiveBacktracker,
)
from mazegen.pattern42 import apply_pattern_42

__all__ = [
    "Cell",
    "Wall",
    "Grid",
    "MazeGenerator",
    "MazeResult",
    "find_shortest_path",
    "path_to_directions",
    "serialize_maze",
    "save_maze_to_file",
    "encode_grid_to_hex",
    "GenerationStrategy",
    "PacmanBoard",
    "RecursiveBacktracker",
    "apply_pattern_42",
]
