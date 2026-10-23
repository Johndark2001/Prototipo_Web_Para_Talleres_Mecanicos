# ADR-004: React + Vite + Tailwind CSS como frontend

## Estado
Aprobado (23/10/2026)

## Fecha
23/10/2026

## Contexto

Según D1 Tabla 2, D2 y D3, la interfaz debe:

- estar pensada primero para el celular;
- usar íconos y botones de acción rápida;
- usar el lenguaje propio del taller;
- respetar las heurísticas de Nielsen (D1 §3.5.3).

El sistema tendrá unas 12 pantallas con estado: formularios, filtros, sesión de usuario y listas paginadas.

La desarrolla una sola persona con nivel básico a intermedio en JavaScript (P-1). Por eso aprender React es el **mayor riesgo técnico** del proyecto.

## Decisión

Usar **React con Vite, JavaScript (sin TypeScript), Tailwind CSS y React Router**, sobre HTML5 semántico.

Para no sumar complejidad, las dependencias se limitan así:

- Las llamadas a la API usan `fetch` dentro de un único módulo. No se usan React Query ni Redux.
- El estado se maneja en cada componente, más un contexto para la sesión.
- Los reportes se muestran con barras hechas en CSS. Usar una librería de gráficos requiere consultarlo antes.
- Se usan los componentes reutilizables definidos en el SPEC §11.

**Punto de control el miércoles 28/10/2026, a mitad de la semana 1** (lo adelanta el plan de 4 semanas, SPEC §17.1). Para esa fecha deben funcionar:

1. la pantalla de inicio de sesión;
2. el diseño base (layout);
3. una lista protegida que consulte la API.

Si no se cumple, se activa el **plan B**:

- se usan plantillas Jinja servidas por FastAPI, con Tailwind y un poco de JavaScript;
- esta decisión se reemplaza con un ADR-007;
- el backend no cambia, porque la capa de servicios es la misma.

## Alternativas consideradas

| Alternativa | Por qué no se eligió |
|---|---|
| HTML, CSS y JavaScript sin framework | Con 12 pantallas con estado, el código se duplica y cuesta mantener la consistencia entre pantallas. Rechazada. |
| Plantillas Jinja en el servidor | Es lo más simple, pero da una experiencia menos fluida en el celular. Queda como plan B. |
| TypeScript | Suma una segunda curva de aprendizaje encima de React. Rechazada por ahora; se puede adoptar más adelante con un nuevo ADR. |

## Consecuencias

**Positivas:**
- Los componentes únicos (por ejemplo `ChipEstado` y `BotonPrimario`) garantizan que la interfaz se vea igual en todas las pantallas.
- Tailwind facilita aplicar una escala de espacios fija y diseñar primero para el celular.

**Negativas:**
- Hace falta Node.js para compilar el frontend.
- Hay una curva de aprendizaje, que el punto de control ayuda a controlar.

**Nivel de calidad exigido:**
- Accesibilidad WCAG 2.1 nivel AA básico.
- Pruebas en anchos de 360, 768, 1024 y 1440 px.
- Estados vacío, de carga y de error en todas las pantallas.
- El color nunca es la única forma de indicar un estado.

## Trazabilidad

- D1: Tabla 2 (Diseño UX/UI responsivo e intuitivo), §2.2.1 Interfaces de usuario y §3.5.3.
- D2: análisis cualitativo.
- SPEC: §11 y Anexo A.
- Riesgo asociado: R-04.
