#!/usr/bin/python3
"""Modulo que gestiona el bucle interactivo de consola (CLI) del proyecto."""

# ============================================================================
# IMPORTACIONES
# Qué hacen: Traen Protocol (para definir contratos entre clases), MazeConfig
# (nuestros datos validados) y AsciiRenderer (nuestro dibujante en consola).
# Por qué: Permiten que el menu sepa que metodos pedirle al generador sin
# importar si es el simulador temporal o el backend real de tu compañero.
# ============================================================================
from typing import Protocol
from ui.config_parser import MazeConfig
from ui.renderer.ascii_renderer import AsciiRenderer


# ============================================================================
# PROTOCOLO (INTERFAZ): MazeGeneratorProtocol
# Qué hace: Define la lista exacta de metodos que el menu espera que tenga
# cualquier generador de laberintos que le pasemos.
# Cómo funciona: En Python, un Protocol es como un "contrato": cualquier clase
# que tenga estos metodos es aceptada por mypy sin necesidad de herencia.
# Por qué: Te permite probar toda tu interfaz hoy con un Mock y conectarla
# despues con el backend real sin tocar ni una linea de este archivo.
# ============================================================================
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


# ============================================================================
# FUNCIÓN AUXILIAR: _clear_screen
# Qué hace: Limpia la pantalla de la terminal y mueve el cursor arriba.
# Cómo funciona: Imprime los codigos de escape ANSI '\033[2J' (borrar todo)
# y '\033[H' (ir a la esquina superior izquierda).
# Por qué: Hace que al cambiar de color o mostrar la ruta, el laberinto se
# actualice en el mismo sitio como un juego, sin llenar la consola de basura.
# ============================================================================
def _clear_screen() -> None:
    """Limpia la terminal usando secuencias de escape ANSI."""
    print("\033[2J\033[H", end="")


# ============================================================================
# FUNCIÓN AUXILIAR: _print_menu_options
# Qué hace: Muestra debajo del laberinto la barra de estado y las opciones.
# Cómo funciona: Recibe el renderer (para leer los colores activos y si la
# ruta esta visible) y la configuracion (para mostrar tamano y modo).
# Por qué: Cumple con el Capitulo V del subject, que exige controles claros
# para regenerar, mostrar/ocultar ruta y cambiar colores.
# ============================================================================
def _print_menu_options(
    renderer: AsciiRenderer,
    config: MazeConfig,
    status_msg: str,
) -> None:
    """Imprime la informacion actual y las opciones interactivas."""
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


# ============================================================================
# FUNCIÓN PRINCIPAL DEL MÓDULO: run_cli_menu
# Qué hace: Ejecuta el bucle infinito de interaccion con el usuario.
# Cómo funciona:
#   1. Limpia pantalla, dibuja el laberinto actual e imprime las opciones.
#   2. Lee lo que escribe el usuario con input().
#   3. Ejecuta la accion elegida (regenerar, alternar ruta, rotar colores).
#   4. Captura Ctrl+C (KeyboardInterrupt) y Ctrl+D (EOFError) para salir
#      limpiamente sin mostrar errores rojos en consola.
# Por qué: Es el corazon de la experiencia de usuario exigida en el Cap. V
# y garantiza que el programa nunca crashee por entradas inesperadas.
# ============================================================================
def run_cli_menu(
    generator: MazeGeneratorProtocol,
    config: MazeConfig,
) -> None:
    """Inicia el bucle interactivo en terminal para visualizar el laberinto."""
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
            estado = "activada" if renderer.show_path else "oculta"
            status_msg = f"Visualizacion de ruta {estado}."
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
