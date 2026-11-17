#!/usr/bin/python3

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

ENTRY_COLOR: str = "\033[1;92m"
EXIT_COLOR: str = "\033[1;91m"
PATH_COLOR: str = "\033[1;93m"

WALL_NORTH: int = 1
WALL_EAST: int = 2
WALL_SOUTH: int = 4
WALL_WEST: int = 8
WALL_ALL: int = 15


class AsciiRenderer:
    def __init__(self) -> None:
        self._wall_names: list[str] = list(WALL_COLORS.keys())
        self._p42_names: list[str] = list(PATTERN_42_COLORS.keys())
        self._wall_idx: int = 0
        self._p42_idx: int = 0
        self.show_path: bool = False

    @property
    def wall_color_name(self) -> str:
        return self._wall_names[self._wall_idx]

    @property
    def pattern42_color_name(self) -> str:
        return self._p42_names[self._p42_idx]

    def toggle_path(self) -> None:
        self.show_path = not self.show_path

    def next_wall_color(self) -> None:
        self._wall_idx = (self._wall_idx + 1) % len(self._wall_names)

    def next_42_color(self) -> None:
        self._p42_idx = (self._p42_idx + 1) % len(self._p42_names)

    def _format_cell_interior(
        self,
        coord: tuple[int, int],
        cell_val: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        path_set: set[tuple[int, int]],
    ) -> str:
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

    def render(
        self,
        grid: list[list[int]],
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        path: list[tuple[int, int]],
    ) -> None:
        if not grid or not grid[0]:
            print("Error: Matriz del laberinto vacia.")
            return

        height = len(grid)
        width = len(grid[0])
        w_ansi = WALL_COLORS[self.wall_color_name]
        path_set = set(path)

        top_parts: list[str] = [f"{w_ansi}+"]
        for x in range(width):
            has_north = bool(grid[0][x] & WALL_NORTH)
            top_parts.append("---+" if has_north else "   +")
        top_parts.append(RESET)
        print("".join(top_parts))

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
