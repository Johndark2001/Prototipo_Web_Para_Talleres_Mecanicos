# Guía de skills de diseño para el frontend

Referencia de trabajo para las mejoras visuales de Taller Digital. Registra qué skills de diseño están instaladas, qué aporta cada una y cómo se combinan. No es documentación funcional: si algo aquí choca con `SPEC.md` o con un ADR (en especial ADR-004 y los tokens de SPEC §11), mandan esos documentos.

## Instalación

Instaladas el 03/11/2026 a nivel de proyecto en `.claude/skills/`, copiadas de sus repositorios oficiales (Claude Code las carga al iniciar sesión; tras instalarlas hay que recargar la ventana).

| Fuente | Commit | Licencia | Skills instaladas |
|---|---|---|---|
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `12af471` | MIT | `design-taste-frontend` |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | `9fadc41` (skill v4.8.0, motor 0.1.18) | Apache 2.0 | `impeccable` |
| [emilkowalski/skills](https://github.com/emilkowalski/skills) | `f1090be` | MIT | `emil-design-eng`, `animate`, `review-animations`, `improve-animations`, `find-animation-opportunities`, `remove-animations`, `animation-performance`, `animation-vocabulary`, `apple-design`, `break-ui`, `mobile-native`, `pick-ui-library`, `prototype` |

No se instalaron `write-swift`, `animate-expo` ni `ask-sonner` (Swift, React Native y la librería Sonner no forman parte del proyecto). Para actualizar: volver a clonar el repositorio y reemplazar la carpeta correspondiente.

## Qué aporta cada una

### Taste (`design-taste-frontend`): criterio visual

Dirección de arte contra lo "genérico hecho por IA". Tiene dos recorridos: páginas públicas y **pantallas de aplicación** (`references/app-screens.md`), que es el que aplica a Taller Digital. Principios de ese capítulo, medidos sobre productos reales:

- El color va en los datos, no en el marco (≈3 % de píxeles con color). Navegación discreta.
- Los KPI son tipografía, no tarjetas con icono en círculo ni sparklines.
- Superficies planas: separación con línea de 1px o un paso de tono, sin sombras.
- Tablas hechas de alineación: sin cebra, números alineados a la derecha.
- Estados honestos: cero se muestra como cero, lo ausente como guion, lo vacío conserva su marco.
- La pantalla debe tener identidad propia y el lenguaje del oficio ("Esperando repuesto", no "Registros").

Herramientas: `draw.mjs --app --kind <tipo>` reparte una dirección visual (para el taller encaja `smb-admin` o `support`, con `--keep palette,type` para respetar los tokens de SPEC §11) e `inspect.mjs --app` comprueba las reglas en el navegador.

### Impeccable (`impeccable`): pulcritud y refinamiento

Vocabulario de comandos para revisar y pulir interfaces existentes, más un detector determinista de 62 reglas. Taller Digital es una superficie en **modo Operate**: la ambición se expresa como precisión y contención, y los patrones conocidos son una virtud.

- **Revisar:** `critique` (heurísticas de usabilidad con puntuación) y `audit` (accesibilidad, rendimiento, responsive; hallazgos P0–P3).
- **Pulir:** `polish`, `harden` (errores, desbordes, casos límite), `clarify` (textos), `adapt` (tamaños de pantalla), `onboard` (estados vacíos).
- **Ajustar:** `layout`, `typeset`, `quieter`, `distill`, `animate`.
- **Piso de calidad** (`reference/craft-floor.md`): contraste ≥4.5:1, todos los estados de cada componente (hover, foco, activo, deshabilitado, cargando, error, vacío), esqueletos en lugar de spinners, nada de etiquetas "eyebrow" sobre títulos, ni bordes laterales de color >1px, ni texto con degradado, ni emojis como iconos.

### Emil Kowalski (`emil-design-eng` y afines): experiencia SaaS y movimiento

Criterio de ingeniería de diseño (Vercel, Linear), centrado en animación y detalles invisibles:

- **¿Debe animarse?** Lo que se usa cientos de veces al día o con teclado, no. Cada animación necesita un propósito (feedback, continuidad espacial, indicar estado).
- **Curvas y tiempos:** `ease-out` fuerte para entradas (`cubic-bezier(0.23, 1, 0.32, 1)`), nunca `ease-in`; interfaz por debajo de 300ms (botón 100–160ms, menús 150–250ms, diálogos 200–500ms).
- **Detalles:** `:active` con `scale(0.97)`, nada aparece desde `scale(0)`, transiciones con propiedades explícitas (no `transition: all`), respetar `prefers-reduced-motion`.
- **Formato de revisión obligatorio:** tabla Antes / Después / Por qué.
- Afines útiles: `break-ui` (probar con datos extremos: placas, nombres y cifras largas), `mobile-native` (el uso real en el taller es desde el celular), `animation-performance`.

## Cómo usarlas en el rediseño

Orden recomendado para cada pantalla o componente, con alcance acotado (una pantalla a la vez):

1. **Diagnóstico** (solo lectura): `/impeccable critique <pantalla>` y `/impeccable audit <pantalla>`; contrastar con las reglas de Taste para pantallas de aplicación.
2. **Plan**: proponer cambios y esperar aprobación antes de editar (método de trabajo por fases del proyecto).
3. **Ajuste visual**: aplicar con `layout`, `typeset`, `quieter` o `distill` de Impeccable y los criterios de Taste, respetando los tokens existentes.
4. **Movimiento**: `find-animation-opportunities` para proponer y `animate` para implementar; `review-animations` para revisar.
5. **Cierre**: `/impeccable polish`, `/impeccable harden`, `break-ui` con datos extremos y `impeccable detect` sobre lo modificado.

Cuando se contradigan, prevalece: SPEC/ADR → Impeccable en modo Operate (familiaridad y consistencia) → Taste app-screens (criterio estético) → Emil (movimiento y microinteracciones).

## Requisitos

- Node 22+ y Chrome/Edge/Chromium para los scripts de Taste y para escanear la app renderizada con Impeccable (verificado: Node 24, Edge instalado).
- El motor de Impeccable se descarga una vez en `~/.impeccable/bin/` y se valida con SHA-256.
- Frontend y backend en ejecución para revisar pantallas reales (`impeccable detect http://localhost:5173`).
- Pendiente de decisión antes del rediseño:
  - Ejecutar `/impeccable init` (crea `PRODUCT.md`) y `/impeccable document` (crea `DESIGN.md` a partir de los tokens actuales). Sin ellos Impeccable funciona, pero con menos contexto.
  - Activar o no el hook de diseño de Impeccable (escanea cada archivo de UI editado); modifica la configuración de Claude Code.
  - Añadir `.taste-skill/` al `.gitignore` (carpeta de trabajo que crean los scripts de Taste).
  - Cualquier librería nueva (por ejemplo Motion para animaciones con resortes) requiere aprobación y, si corresponde, actualizar ADR-004.
