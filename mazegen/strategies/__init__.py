#!/usr/bin/python3
"""Paquete de estrategias de generacion de laberintos."""

from mazegen.strategies.base import GenerationStrategy
from mazegen.strategies.backtracker import RecursiveBacktracker
from mazegen.strategies.pacman_board import PacmanBoard

__all__ = [
    "GenerationStrategy",
    "RecursiveBacktracker",
    "PacmanBoard",
]
