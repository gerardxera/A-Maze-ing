#!/usr/bin/python3
"""Modulo que define la clase base abstracta para las estrategias."""

from abc import ABC, abstractmethod
from mazegen.grid import Grid


class GenerationStrategy(ABC):
    """Interfaz abstracta para los algoritmos de generacion."""

    @abstractmethod
    def generate(
        self,
        grid: Grid,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
    ) -> None:
        """Ejecuta el algoritmo de generacion sobre la cuadricula.

        Args:
            grid: Instancia de Grid sobre la cual derribar paredes.
            entry: Coordenadas (x, y) de entrada del laberinto.
            exit_pos: Coordenadas (x, y) de salida del laberinto.
        """
        pass
