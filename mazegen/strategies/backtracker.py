#!/usr/bin/python3

"""Modulo que implementa la estrategia de generacion Recursive Backtracker."""

import random
from mazegen.cell import Cell, Wall
from mazegen.grid import Grid
from mazegen.strategies.base import GenerationStrategy

class RecursiveBacktracker(GenerationStrategy):
	"""Generador de laberintos perfectos mediante DFS con pila."""

	def generate(
		self,
		grid: Grid,
		entry: tuple[int, int],
		exit: tuple[int, int]
	) -> None:
		"""Genera un laberinto perfecto comenzando desde la celda de entrada.

		Args:
			grid: Instancia de Grid sobre la cual construir el laberinto.
			entry: Coordenadas (x, y) del punto de inicio.
			exit: Coordenadas (x, y) del punto de salida (para la firma).
		"""
		start_cell = grid.get_cell(entry[0], entry[1])
		if start_cell is None:
			start_cell = grid.get_cell(0, 0)
		
		if start_cell is None:
			return
		
		start_cell.visited = True
		stack: list[Cell] = [start_cell]

		while stack:
			current = stack[-1]
			unvisited_neighbors: list[tuple[Cell, Wall]] = [
				(neighbor, direction)
				for neighbor, direction in grid.get_neighbors(current)
				if not neighbor.visited and not neighbor.is_42_cell
			]

			if unvisited_neighbors:
				next_cell, direction = random.choice(unvisited_neighbors)
				grid.remove_wall_between(current, next_cell, direction)
				next_cell.visited = True
				stack.append(next_cell)
			else:
				stack.pop()
	


