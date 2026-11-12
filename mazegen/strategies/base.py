#!/usr/bin/python3

"""Modulo que define la clase base abstracta para las estrategias de generación."""

from abc import ABC, abstractmethod
from mazegen.grid import Grid


class GenerationStrategy(ABC):
	"""Clase base abstracta (interfaz) para los algoritmos de generacion de laberintos."""

	@abstractmethod
	def generate(
		self,
		grid: Grid,
		entry: tuple[int, int],
		exit: tuple[int, int],
	) -> None:
		"""Ejecuta el algoritmo de generacion modificando la cuadricula proporcionada.
		
		Args: 
			grid: Instancia de la cuadricula sobre la cual derribar paredes.
			entry: Coordenadas (x, y) del punto de entrada del laberinto.
			exit: Coordenadas (x, y) del punto de salida del laberinto.
		"""
		pass