"""Límite de solicitudes en memoria (ADR-005).

Sirve porque el plan gratuito corre una sola instancia. Si algún día hay varias, el
contador debe pasar a un almacén compartido: con memoria, cada instancia contaría aparte.
"""

import time
from collections import defaultdict, deque
from threading import Lock


class LimitadorSolicitudes:
    def __init__(self, maximo: int, ventana_segundos: float):
        self.maximo = maximo
        self.ventana = ventana_segundos
        self._registros: dict[str, deque[float]] = defaultdict(deque)
        self._candado = Lock()

    def permitir(self, clave: str) -> bool:
        """Ventana deslizante: cuenta las solicitudes de `clave` en los últimos segundos."""
        ahora = time.monotonic()
        with self._candado:
            registros = self._registros[clave]
            while registros and ahora - registros[0] > self.ventana:
                registros.popleft()
            if len(registros) >= self.maximo:
                return False
            registros.append(ahora)
            return True

    def reiniciar(self) -> None:
        with self._candado:
            self._registros.clear()
