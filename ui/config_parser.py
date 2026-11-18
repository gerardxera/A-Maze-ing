#!/usr/bin/python3
"""Modulo de lectura y validacion estricta del archivo config.txt."""

# ============================================================================
# IMPORTACIONES
# Qué hacen: Traen herramientas para leer rutas de archivos (Path), anotar
# tipos (Any) y validar datos automaticamente (Pydantic v2).
# Por qué: El subject (Cap. IV.2) prohibe que el programa crashee si el
# usuario mete datos corruptos; Pydantic valida tipos y reglas de negocio.
# ============================================================================
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field, field_validator, model_validator


# ============================================================================
# CLASE: MazeConfig
# Qué hace: Define la "plantilla" exacta de datos que debe tener config.txt.
# Cómo funciona: Hereda de BaseModel (Pydantic). Al crear una instancia,
# convierte strings a int/bool/tuple y ejecuta las validaciones de abajo.
# Por qué: Centraliza todas las reglas del Cap. IV.3 en un solo objeto
# seguro e inmutable con tipado estricto para mypy.
# ============================================================================
class MazeConfig(BaseModel):
    """Modelo validado de configuracion para el generador de laberintos."""

    width: int = Field(ge=2, description="Ancho del laberinto (minimo 2)")
    height: int = Field(ge=2, description="Alto del laberinto (minimo 2)")
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str = Field(min_length=1)
    perfect: bool = False
    seed: int | None = None

    # ========================================================================
    # MÉTODO VALIDADOR: parse_coords
    # Qué hace: Transforma texto como "0,0" en una tupla de enteros (0, 0).
    # Cómo funciona: Se ejecuta ANTES (mode="before") de que Pydantic valide
    # el tipo tuple[int, int]. Corta por la coma y convierte cada lado a int.
    # Por qué: En config.txt todo se lee como texto plano, pero el backend
    # exige tuplas de dos enteros (x, y).
    # ========================================================================
    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coords(cls, value: Any) -> tuple[int, int]:
        """Convierte cadenas 'x,y' en una tupla de dos enteros."""
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

    # ========================================================================
    # MÉTODO VALIDADOR: parse_seed
    # Qué hace: Interpreta el campo opcional SEED (entero o None).
    # Cómo funciona: Si en config.txt dice SEED=None, SEED= o no esta, lo
    # convierte a None de Python. Si hay numero, lo pasa a int.
    # Por qué: El Cap. IV.4 exige reproducibilidad mediante semilla, pero
    # cuando no se especifica debe usar una semilla aleatoria (None).
    # ========================================================================
    @field_validator("seed", mode="before")
    @classmethod
    def parse_seed(cls, value: Any) -> int | None:
        """Permite valores enteros, None o la cadena 'None'."""
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

    # ========================================================================
    # MÉTODO VALIDADOR: check_bounds_and_points
    # Qué hace: Verifica coherencia cruzada entre WIDTH, HEIGHT, ENTRY y EXIT.
    # Cómo funciona: Se ejecuta DESPUÉS (mode="after") de validar cada campo
    # por separado, comparando los valores ya convertidos entre si.
    # Por qué: El Cap. IV.4 exige que entrada y salida esten dentro de los
    # limites del tablero (0 <= x < width) y que no sean la misma casilla.
    # ========================================================================
    @model_validator(mode="after")
    def check_bounds_and_points(self) -> "MazeConfig":
        """Verifica que entry y exit esten
        dentro del tablero y no coincidan."""
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


# ============================================================================
# FUNCIÓN: parse_config_file
# Qué hace: Lee el archivo de texto plano config.txt y devuelve MazeConfig.
# Cómo funciona: Abre el archivo con Path.read_text, salta lineas vacias y
# comentarios (#), divide cada linea por el primer '=' y pasa el diccionario
# resultante a MazeConfig.model_validate().
# Por qué: Separa la lectura del disco de la validacion logica y detecta
# errores de sintaxis (lineas sin '=', claves vacias o claves repetidas).
# ============================================================================
def parse_config_file(file_path: str) -> MazeConfig:
    """Lee un archivo KEY=VALUE y devuelve un objeto MazeConfig validado."""
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
