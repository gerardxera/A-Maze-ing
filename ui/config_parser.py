#!/usr/bin/python3

from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field, field_validator, model_validator


class MazeConfig(BaseModel):
    width: int = Field(ge=2, description="Ancho del laberinto (minimo 2)")
    height: int = Field(ge=2, description="Alto del laberinto (minimo 2)")
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str = Field(min_length=1)
    perfect: bool
    seed: int | None = None

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coords(cls, value: Any) -> tuple[int, int]:
        if isinstance(value, tuple) and len(value) == 2:
            return (int(value[0]), int(value[1]))
        if isinstance(value, str):
            parts = [p.strip() for p in value.split(",")]
            if len(parts) != 2:
                raise ValueError(
                    f"Coordenada invalida '{value}'. Formato esperado: x,y"
                )
            try:
                return (int(parts[0]), int(parts[1]))
            except ValueError as err:
                raise ValueError(
                    f"Las coordenadas deben ser enteros: '{value}'"
                ) from err
        raise ValueError(f"Tipo invalido para coordenada: {value}")

    @field_validator("seed", mode="before")
    @classmethod
    def parse_seed(cls, value: Any) -> int | None:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned == "" or cleaned.lower() == "none":
                return None
            try:
                return int(cleaned)
            except ValueError as err:
                raise ValueError(
                    f"SEED debe ser entero o None, recibido: '{value}'"
                ) from err
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        raise ValueError(f"SEED invalido: {value}")

    @model_validator(mode="after")
    def check_bounds_and_points(self) -> "MazeConfig":
        ex, ey = self.entry
        xx, xy = self.exit

        if not (0 <= ex < self.width and 0 <= ey < self.height):
            raise ValueError(
                f"ENTRY {self.entry} fuera de limites "
                f"({self.width}x{self.height})"
            )
        if not (0 <= xx < self.width and 0 <= xy < self.height):
            raise ValueError(
                f"EXIT {self.exit} fuera de limites "
                f"({self.width}x{self.height})"
            )
        if self.entry == self.exit:
            raise ValueError("ENTRY y EXIT no pueden ser la misma celda")
        return self


def parse_config_file(file_path: str) -> MazeConfig:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"No se encontro el archivo de configuracion: {file_path}"
        )

    raw_data: dict[str, str] = {}
    content = path.read_text(encoding="utf-8")

    for line_num, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(
                f"Error de sintaxis en linea {line_num}: '{raw_line}'. "
                "Se esperaba KEY=VALUE"
            )
        key, value = line.split("=", maxsplit=1)
        clean_key = key.strip().lower()
        clean_value = value.strip()
        if not clean_key:
            raise ValueError(f"Clave vacia en linea {line_num}")
        if clean_key in raw_data:
            raise ValueError(
                f"Clave duplicada '{key.strip()}' en linea {line_num}"
            )
        raw_data[clean_key] = clean_value

    return MazeConfig.model_validate(raw_data)
