from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    """Toda la configuración entra por variables de entorno (ADR-001, RNF-10)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    secret_key: str = Field(min_length=32)
    entorno: Literal["desarrollo", "produccion"] = "desarrollo"
    origen_publico: str = "http://localhost:5173"
    sesion_horas: int = Field(default=8, ge=1, le=24)

    @property
    def es_produccion(self) -> bool:
        return self.entorno == "produccion"


@lru_cache
def obtener_configuracion() -> Configuracion:
    return Configuracion()
