#!/usr/bin/python3

from typing import Protocol
from ui.config_parser import MazeConfig
from ui.renderer.ascii_renderer import AsciiRenderer
import time


class MazeGeneratorProtocol(Protocol):
    """Contrato de metodos que debe cumplir el generador de laberintos."""

    def generate(self) -> None:
        """Genera o regenera el laberinto."""
        ...

    def get_grid(self) -> list[list[int]]:
        """Devuelve la matriz de enteros (0 a 15) de las paredes."""
        ...

    def get_shortest_path(self) -> list[tuple[int, int]]:
        """Devuelve la lista de coordenadas (x, y) del camino mas corto."""
        ...

    def write_output_file(self, path: str) -> None:
        """Guarda el laberinto codificado en hexadecimal en un archivo."""
        ...


def _clear_screen() -> None:
    print("\033c\033[H\033[2J\033[3J", end="", flush=True)


def _animate_path(
    renderer: AsciiRenderer,
    grid: list[list[int]],
    config: MazeConfig,
    path: list[tuple[int, int]],
) -> None:
    """Anima paso a paso el recorrido desde la entrada hasta la salida."""
    for step in range(1, len(path) + 1):
        _clear_screen()
        renderer.render(grid, config.entry, config.exit, path[:step])
        time.sleep(0.035)


def _print_menu_options(
    renderer: AsciiRenderer,
    config: MazeConfig,
    status_msg: str,
) -> None:
    path_state = "VISIBLE" if renderer.show_path else "OCULTA"
    mode_state = "Perfecto (1 camino)" if config.perfect else "Pac-Man"

    print("-" * 58)
    print(
        f"Tamano: {config.width}x{config.height} | "
        f"Modo: {mode_state} | Seed: {config.seed}"
    )
    print(
        f"Paredes: {renderer.wall_color_name} | "
        f"Color '42': {renderer.pattern42_color_name} | "
        f"Ruta: {path_state}"
    )
    print("-" * 58)
    print("  [1] Regenerar nuevo laberinto")
    print("  [2] Mostrar / Ocultar camino mas corto")
    print("  [3] Cambiar color de las paredes")
    print("  [4] Cambiar color del patron '42'")
    print("  [5] Salir")
    print("-" * 58)
    if status_msg:
        print(f">> {status_msg}")


def run_cli_menu(
    generator: MazeGeneratorProtocol,
    config: MazeConfig,
) -> None:
    renderer = AsciiRenderer()
    status_msg: str = f"Laberinto guardado en '{config.output_file}'."

    while True:
        _clear_screen()
        grid = generator.get_grid()
        path = generator.get_shortest_path()
        renderer.render(grid, config.entry, config.exit, path)
        _print_menu_options(renderer, config, status_msg)
        status_msg = ""

        try:
            choice = input("Elige una opcion (1-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo de A-Maze-ing. Hasta pronto!")
            break

        if choice == "1":
            generator.generate()
            generator.write_output_file(config.output_file)
            status_msg = (
                f"Nuevo laberinto generado y guardado en "
                f"'{config.output_file}'."
            )
        elif choice == "2":
            renderer.toggle_path()
            if renderer.show_path:
                _animate_path(renderer, grid, config, path)
                status_msg = "Visualizacion de ruta activada."
            else:
                status_msg = "Visualizacion de ruta oculto."
        elif choice == "3":
            renderer.next_wall_color()
            status_msg = f"Color de paredes: {renderer.wall_color_name}."
        elif choice == "4":
            renderer.next_42_color()
            status_msg = f"Color patron '42': {renderer.pattern42_color_name}."
        elif choice == "5" or choice.lower() in {"q", "exit", "salir"}:
            print("Cerrando visualizador. Hasta pronto!")
            break
        else:
            status_msg = "Opcion no valida. Introduce un numero del 1 al 5."
