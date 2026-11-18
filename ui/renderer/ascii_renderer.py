#!/usr/bin/python3
"""Modulo de renderizado ASCII con colores ANSI para la terminal."""

# ============================================================================
# CONSTANTES DE COLORES ANSI Y MÁSCARAS DE PAREDES
# Qué hacen: Definen los codigos de escape de terminal para colorear texto
# y los valores de bits (1, 2, 4, 8, 15) de cada pared.
# Cómo funcionan: Un codigo como '\033[96m' le dice a la terminal "pinta
# lo que sigue en cian brillante" hasta encontrar RESET ('\033[0m').
# Por qué: El Cap. V exige poder cambiar el color de las paredes y del
# patron '42' en tiempo real desde el menu interactivo.
# ============================================================================
RESET: str = "\033[0m"
BOLD: str = "\033[1m"

WALL_COLORS: dict[str, str] = {
    "Blanco": "\033[97m",
    "Cian": "\033[96m",
    "Verde": "\033[92m",
    "Amarillo": "\033[93m",
    "Magenta": "\033[95m",
    "Azul": "\033[94m",
}

PATTERN_42_COLORS: dict[str, str] = {
    "Magenta": "\033[95m",
    "Cian": "\033[96m",
    "Amarillo": "\033[93m",
    "Azul": "\033[94m",
    "Blanco": "\033[97m",
}

ENTRY_COLOR: str = "\033[1;92m"  # Verde brillante en negrita
EXIT_COLOR: str = "\033[1;91m"   # Rojo brillante en negrita
PATH_COLOR: str = "\033[1;93m"   # Amarillo brillante en negrita

WALL_NORTH: int = 1
WALL_EAST: int = 2
WALL_SOUTH: int = 4
WALL_WEST: int = 8
WALL_ALL: int = 15


# ============================================================================
# CLASE: AsciiRenderer
# Qué hace: Se encarga de traducir una matriz de numeros (0..15) en un
# dibujo visual legible en la consola con colores y ruta opcional.
# Cómo funciona: Guarda el estado visual actual (color de pared elegido,
# color del '42' y si la ruta esta visible o oculta) y construye el texto
# fila por fila (pared superior, interior de celda, pared inferior).
# Por qué: Desacopla totalmente la logica visual de la logica matematica;
# si manana cambias a MiniLibX, solo cambias el renderer sin tocar nada mas.
# ============================================================================
class AsciiRenderer:
    """Renderizador interactivo de laberintos en terminal usando ANSI."""

    # ========================================================================
    # MÉTODO: __init__
    # Qué hace: Inicializa el renderizador con los colores por defecto.
    # Cómo funciona: Guarda listas con los nombres de colores disponibles e
    # indices para poder rotar de color facil con next_wall_color().
    # Por qué: Permite alternar colores ciclicamente cada vez que el usuario
    # pulsa la opcion correspondiente en el menu.
    # ========================================================================
    def __init__(self) -> None:
        """Inicializa las opciones de color y el estado de visualizacion."""
        self._wall_names: list[str] = list(WALL_COLORS.keys())
        self._p42_names: list[str] = list(PATTERN_42_COLORS.keys())
        self._wall_idx: int = 0
        self._p42_idx: int = 0
        self.show_path: bool = False

    # ========================================================================
    # PROPIEDADES: wall_color_name y pattern42_color_name
    # Qué hacen: Devuelven el nombre legible del color activo (ej. "Cian").
    # Por qué: Sirven para mostrarle al usuario en el menu que color tiene
    # seleccionado actualmente.
    # ========================================================================
    @property
    def wall_color_name(self) -> str:
        """Devuelve el nombre del color activo para las paredes."""
        return self._wall_names[self._wall_idx]

    @property
    def pattern42_color_name(self) -> str:
        """Devuelve el nombre del color activo para el patron '42'."""
        return self._p42_names[self._p42_idx]

    # ========================================================================
    # MÉTODOS DE INTERACCIÓN: toggle_path, next_wall_color, next_42_color
    # Qué hacen: Modifican el estado visual del renderizador.
    # Cómo funciona: Usan modulo (%) para avanzar al siguiente color de la
    # lista y volver al principio cuando llegan al final.
    # Por qué: Implementan directamente las interacciones pedidas en Cap. V.
    # ========================================================================
    def toggle_path(self) -> None:
        """Alterna entre mostrar y ocultar la ruta solucion."""
        self.show_path = not self.show_path

    def next_wall_color(self) -> None:
        """Cambia al siguiente color disponible para las paredes."""
        self._wall_idx = (self._wall_idx + 1) % len(self._wall_names)

    def next_42_color(self) -> None:
        """Cambia al siguiente color disponible para el patron '42'."""
        self._p42_idx = (self._p42_idx + 1) % len(self._p42_names)

    # ========================================================================
    # MÉTODO PRIVADO: _format_cell_interior
    # Qué hace: Decide que 3 caracteres dibujar dentro de una casilla (x, y).
    # Cómo funciona: Evalua por prioridad: 1) Entrada (' E '), 2) Salida
    # (' X '), 3) Bloque '42' si value == 15 ('███'), 4) Camino resuelto
    # si show_path es True (' · '), 5) Pasillo vacio ('   ').
    # Por qué: Mantiene limpio el bucle principal de renderizado y asegura
    # que entrada y salida nunca queden tapadas por los puntos de la ruta.
    # ========================================================================
    def _format_cell_interior(
        self,
        coord: tuple[int, int],
        cell_val: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        path_set: set[tuple[int, int]],
    ) -> str:
        """Devuelve el contenido coloreado de 3 caracteres de una celda."""
        if coord == entry:
            return f"{ENTRY_COLOR} E {RESET}"
        if coord == exit_pos:
            return f"{EXIT_COLOR} X {RESET}"
        if cell_val == WALL_ALL:
            p42_ansi = PATTERN_42_COLORS[self.pattern42_color_name]
            return f"{p42_ansi}███{RESET}"
        if self.show_path and coord in path_set:
            return f"{PATH_COLOR} · {RESET}"
        return "   "

    # ========================================================================
    # MÉTODO PRINCIPAL: render
    # Qué hace: Construye e imprime en consola el laberinto completo.
    # Cómo funciona:
    #   1. Dibuja el borde superior (techo) mirando el bit WALL_NORTH de y=0.
    #   2. Por cada fila 'y', arma dos cadenas en paralelo:
    #      - body_line: pared izquierda, interior de cada celda y pared Este.
    #      - bottom_line: pared Sur de cada celda (cierre inferior de fila).
    # Por qué: Al trabajar solo con `grid: list[list[int]]`, no importa como
    # este programado el backend por dentro; solo necesita la matriz de ints.
    # ========================================================================
    def render(
        self,
        grid: list[list[int]],
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        path: list[tuple[int, int]],
    ) -> None:
        """Dibuja el laberinto completo en la terminal."""
        if not grid or not grid[0]:
            print("Error: Matriz del laberinto vacia.")
            return

        height = len(grid)
        width = len(grid[0])
        w_ansi = WALL_COLORS[self.wall_color_name]
        path_set = set(path)

        # 1. Linea superior (borde Norte de la fila 0)
        top_parts: list[str] = [f"{w_ansi}+"]
        for x in range(width):
            has_north = bool(grid[0][x] & WALL_NORTH)
            top_parts.append("---+" if has_north else "   +")
        top_parts.append(RESET)
        print("".join(top_parts))

        # 2. Filas interiores y bordes inferiores
        for y in range(height):
            body_parts: list[str] = []
            bottom_parts: list[str] = [f"{w_ansi}+"]

            for x in range(width):
                val = grid[y][x]
                if x == 0:
                    has_west = bool(val & WALL_WEST)
                    body_parts.append(
                        f"{w_ansi}|{RESET}" if has_west else " "
                    )

                interior = self._format_cell_interior(
                    (x, y), val, entry, exit_pos, path_set
                )
                body_parts.append(interior)

                has_east = bool(val & WALL_EAST)
                body_parts.append(
                    f"{w_ansi}|{RESET}" if has_east else " "
                )

                has_south = bool(val & WALL_SOUTH)
                bottom_parts.append("---+" if has_south else "   +")

            bottom_parts.append(RESET)
            print("".join(body_parts))
            print("".join(bottom_parts))
