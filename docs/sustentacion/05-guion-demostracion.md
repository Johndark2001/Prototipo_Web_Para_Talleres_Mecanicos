# Guion de demostración del prototipo — Taller Digital

| Campo | Valor |
|---|---|
| Para quién | El autor, durante la sustentación |
| Duración | 14 minutos, más 1 minuto de reserva |
| Versión | Commit `e51d187` más los ajustes visuales del 05/11/2026, en local (el despliegue está pendiente) |
| Datos | Solo ficticios, de `semilla_demo` (decisión H-5) |

La historia de la demostración es **un solo carro que entra al taller, se repara, se entrega con su informe PDF y, después, la clienta pide borrar sus datos**. Así el jurado ve el flujo completo de punta a punta, sin saltos.

---

## 1. Preparación (el día anterior y 30 minutos antes)

### 1.1 Reiniciar la base de demostración

> **Atención:** estos comandos **borran todos los datos** de `taller_dev`. Úselos solo si esa base es de demostración.

En `backend/`:

```
uv run alembic downgrade base
uv run alembic upgrade head
uv run python -m app.scripts.semilla_demo
```

### 1.2 Arrancar el sistema

```
# Terminal 1 (backend/)
uv run uvicorn app.main:app --reload

# Terminal 2 (frontend/)
npm run dev
```

Verifique que `http://localhost:8000/api/v1/salud` responde y que `http://localhost:5173` muestra el login.

### 1.3 Ventanas preparadas

Cada navegador guarda su propia sesión, así que use **navegadores o perfiles distintos** para cada rol.

| Ventana | Navegador | Usuario | Uso |
|---|---|---|---|
| A — Recepción | Chrome normal | `recepcion@norte.demo.co` | Cliente, carro, orden, entrega |
| B — Mecánico | Chrome incógnito, **en vista de celular** (F12 → modo dispositivo, 360 px) | `mecanico@norte.demo.co` | Diagnóstico, repuestos, estados |
| C — Administrador | Edge (o Firefox) | `admin@norte.demo.co` | Inventario y anonimización |
| D — Cliente | Celular real o Firefox privado, en vista de celular | Sin sesión | Enlace de seguimiento |

Clave de todos los usuarios de demostración: `demo12345`.

Deje las ventanas A, B y C **en la pantalla de login**, para mostrar el inicio de sesión. Aumente el zoom del navegador al 125 % para que el jurado lea.

### 1.4 Datos que se usarán

| Dato | Valor |
|---|---|
| Cliente nuevo | Marta Ríos (demo) — teléfono 310 444 5566 — sin documento |
| Carro nuevo (en el mismo formulario del cliente) | Tipo **Carro** — placa escrita «dem-432» → el sistema la guarda como **DEM432** — Renault Sandero 2017, gris |
| Orden | Categoría **Problemas de frenos** (se busca escribiendo «fren») — observación «La clienta pide cambio de aceite y dice que los frenos chillan» — 65400 km — mecánico «Mecánico Norte» |
| Moto de la semilla (para el filtro) | JKL45D, Yamaha FZ 2.0 2019 |
| Repuestos (catálogo de la semilla) | Pastillas de freno delanteras (stock 0, **agotado**), Aceite 20W-50 (20 litros), Filtro Mann W712 (2 unidades, **bajo el mínimo de 3**) |
| Cliente con orden abierta (para el bloqueo) | Pedro Ruiz (demo), placa XYZ987 |

### 1.5 Plan B

- Si algo falla, la semilla ya trae órdenes en todos los estados: XYZ987 entregada (sirve para mostrar el **informe PDF**), ABC123 en diagnóstico, JKL45D esperando repuestos y XYZ987 recibida sin mecánico.
- Las órdenes de la semilla se crearon con el motivo libre, así que aparecen **«Sin categoría (orden registrada antes del catálogo)»**. Si el jurado pregunta, es la compatibilidad de la decisión O-6; las abiertas se pueden corregir con **Corregir datos de recepción**.
- Tenga capturas de pantalla de cada paso en una carpeta, por si falla el equipo.
- No improvise datos reales: solo los de esta tabla.

---

## 2. Guion paso a paso

Formato: **⏱ tiempo acumulado** · **Hacer** (acciones exactas) · **Decir** (texto sugerido, en voz alta).

### Apertura — ⏱ 0:00 a 0:30

**Hacer:** muestre la ventana A en el login.

**Decir:**
> «Voy a mostrar el recorrido completo de un carro en un taller: llega una clienta nueva, recibimos su carro, el mecánico lo diagnostica, usamos repuestos del inventario, calculamos el cobro, lo entregamos y la clienta sigue todo desde su celular. Al final, la clienta pide que borremos sus datos y veremos cómo el sistema cumple la Ley 1581 sin perder la historia del taller. Todo lo que van a ver son datos ficticios.»

---

### Paso 1 — Login · ⏱ 0:30 a 1:30

**Hacer:**
1. En A, escriba `recepcion@norte.demo.co` y una clave **equivocada**, por ejemplo `demo1234`. Toque **Ingresar**.
2. Señale el mensaje «Correo o clave incorrectos».
3. Escriba la clave correcta `demo12345` e ingrese.
4. Señale arriba: el nombre del taller «Taller Demo Norte», «Recepción Norte · Recepción» y el menú.

**Decir:**
> «Cada persona del taller tiene su propio usuario; así sabemos quién hizo cada cosa. Si me equivoco, el sistema no dice si falló el correo o la clave: eso evita que alguien averigüe qué correos existen. La clave se guarda con argon2id, que es un hash, y la sesión viaja en una cookie que el código de la página no puede leer. El menú cambia según el rol: Recepción no ve Usuarios.»

---

### Paso 2 — Cliente con su vehículo · ⏱ 1:30 a 3:15

**Hacer:**
1. Menú **Clientes** → **+ Cliente**.
2. Nombre: `Marta Ríos (demo)`. Teléfono: `310 444 5566`. Deje vacíos el correo y el documento.
3. En **Información del vehículo**: tipo **Carro**; placa: escriba `dem-432` y pase al campo siguiente. Señale cómo se corrige sola a **DEM432**. Marca `Renault`, Modelo `Sandero`, Año `2017`, Color `Gris`.
4. **Sin marcar la autorización**, toque **Guardar cliente**. Señale el error en la casilla.
5. Marque **«El cliente autoriza el tratamiento de sus datos personales (Ley 1581 de 2012)»** y toque **Guardar cliente**.
6. Señale «Cliente Marta Ríos (demo) registrado con el vehículo DEM432», el teléfono sin espacios, «Autorizó el [fecha de hoy]» y el carro en **Vehículos asociados**.

**Decir:**
> «Registramos a la clienta y su carro en un solo formulario: se guardan juntos o no se guarda ninguno, así nunca queda un cliente a medias. Por la Ley 1581, el sistema no deja registrar a un cliente sin su autorización; esa regla también está en la base de datos con una restricción. Pedimos solo lo necesario: nombre y teléfono. La placa se normaliza, mayúsculas y sin guiones, y es única dentro del taller. Decimos "cliente" y no "dueño" porque quien trae el carro no siempre es el propietario.»

---

### Paso 3 — Vehículos: carros y motos · ⏱ 3:15 a 3:45

**Hacer:**
1. Menú **Vehículos**. Señale el fondo del módulo y, en cada fila, **Cliente: [nombre]** y la etiqueta Carro o Moto.
2. Toque **Motos**: queda la Yamaha **JKL45D**. Escriba `JKL` en la búsqueda: el filtro se combina con la placa.
3. Toque **Todos** para volver.

**Decir:**
> «El sistema maneja carros y motos. El filtro por tipo se combina con la búsqueda por placa y con los inactivos, y el tipo se muestra con ícono y texto, no solo con color.»

---

### Paso 4 — Orden · ⏱ 3:45 a 5:15

**Hacer:**
1. Abra **DEM432** (desde la ficha de Marta o con **Buscar placa**) y toque **Nueva orden para este carro**. Señale que el carro ya viene elegido.
2. En **Categoría del problema**, escriba `fren` (sin tilde): aparece **Problemas de frenos**. Presione Enter.
3. **Observación reportada por el cliente**: `La clienta pide cambio de aceite y dice que los frenos chillan`. Kilometraje: `65400`. Entrega estimada: mañana.
4. Mecánico: elija **Mecánico Norte**. Señale que la lista muestra cuántas órdenes abiertas tiene.
5. **Abrir orden**. Señale «Orden #5 abierta para DEM432», el estado **Recibido**, la categoría en **Información general** y el historial «Abrió la orden · Recepción Norte».
6. En **Enlace de seguimiento**, toque **Copiar enlace** y ábralo en la ventana D. Déjelo visible.

**Decir:**
> «Recibir un carro ya registrado toma tres pasos: elegirlo, escoger la categoría del problema y abrir la orden. La categoría sale de un catálogo distinto para carros y para motos; así, con los datos del piloto, podremos saber qué problemas son los más frecuentes. Lo que dice la clienta queda con sus palabras. El número es consecutivo por taller y lo asigna el servidor con un bloqueo. Un carro solo puede tener una orden abierta. Este enlace es lo que le mandamos a la clienta por WhatsApp: contiene un código aleatorio de 128 bits, imposible de adivinar.»

---

### Paso 5 — Mecánico · ⏱ 5:15 a 6:15

**Hacer:**
1. Pase a la ventana B (vista de celular). Ingrese como `mecanico@norte.demo.co`.
2. Señale el menú inferior y «Mis órdenes abiertas»: aparece la #5 de DEM432.
3. Abra la orden. Señale que se lee de arriba abajo: estado, acciones, información general (con la categoría y la observación), diagnóstico, trabajo realizado y costos. Toque **Iniciar diagnóstico**.
4. En la sección **Diagnóstico**, escriba `Pastillas delanteras gastadas al 90 %. Aceite vencido.` y toque **Guardar**.

**Decir:**
> «Así lo ve el mecánico, en su celular. La orden está en una sola columna, en el orden en que se trabaja. Solo ve las órdenes que le asignaron; si se la reasignan a otro, deja de verla. Puede leer la categoría y lo que dijo la clienta, pero no cambiarlos: eso es de recepción. Solo él o el administrador pueden iniciar el diagnóstico, y el sistema exige que haya un mecánico asignado. Todo cambio queda con su nombre, la fecha y la hora.»

---

### Paso 6 — Estados · ⏱ 6:15 a 7:15

**Hacer:**
1. En B, toque **Esperando repuestos**. En **Qué repuesto falta**, escriba `Pastillas de freno agotadas en bodega` → **Confirmar**.
2. Señale la línea de tiempo y el historial.
3. Pase a la ventana D (cliente) y toque **Actualizar**. Señale «Estamos esperando un repuesto para continuar» y la línea de tiempo.

**Decir:**
> «La orden tiene seis estados. Este, Esperando repuestos, lo agregamos al modelo de la tesis porque es donde más se pierde tiempo en los talleres, y queremos medirlo. Cada cambio guarda el estado anterior, el nuevo, quién y cuándo: de ahí saldrá el reporte de tiempo promedio por etapa, que es la evidencia de la pregunta de investigación. La clienta ya lo ve en su celular, sin llamar al taller.»

---

### Paso 7 — Inventario · ⏱ 7:15 a 8:30

**Hacer:**
1. Pase a la ventana C. Ingrese como `admin@norte.demo.co`.
2. En **Inicio**, señale los conteos por estado y la alerta **«N repuestos necesitan reposición»**: Filtro W712 con «Stock bajo» y Pastillas con «Agotado».
3. Abra **Pastillas de freno delanteras**. Toque **Registrar entrada**. Cantidad `2`. Nota `Factura demo 001` → **Registrar entrada**.
4. Señale «Stock de Pastillas de freno delanteras: 2 juego» y el movimiento ENTRADA con usuario, fecha y stock resultante.

**Decir:**
> «El administrador ve el resumen del taller y las alertas de stock: el sistema avisa cuando un repuesto llega a su mínimo. Solo el administrador mueve el stock. Cada entrada, salida, ajuste o devolución queda en un libro de movimientos que nunca se borra, con quién lo hizo y cuánto quedó.»

---

### Paso 8 — Repuestos en la orden · ⏱ 8:30 a 10:00

**Hacer (ventana B, mecánico):**
1. En la orden #5, toque **+ Repuesto**. Busque `pastillas`, elija **Pastillas de freno delanteras**, cantidad `1` → **Agregar repuesto**. Señale «…agregado; se descontó del inventario».
2. **+ Repuesto** → `aceite` → **Aceite 20W-50 mineral**, cantidad `4` → **Agregar repuesto**.
3. **+ Repuesto** → `W712` → **Filtro de aceite Mann W712**, cantidad `5` → **Agregar repuesto**. Señale el error **«No hay suficiente Filtro de aceite Mann W712: quedan 2…»**.
4. Cambie la cantidad a `1` → **Agregar repuesto**.
5. **+ Mano de obra**: `Cambio de pastillas y aceite`, Valor `60.000` → **Agregar**.
6. En la sección **Trabajo realizado**, escriba `Cambio de pastillas delanteras, aceite y filtro.` Toque **Marcar reparado**.

**Decir:**
> «Al agregar un repuesto, el sistema lo descuenta del inventario en la misma operación. Si pido más de lo que hay, lo rechaza y me dice cuánto queda: el stock nunca queda negativo. Lo probamos incluso con dos personas registrando al mismo tiempo. El precio se copia en la orden: si mañana cambia en el catálogo, esta orden no cambia. Para marcar el carro como reparado, el mecánico tiene que escribir qué hizo; sin eso, el sistema no lo deja.»

---

### Paso 9 — Liquidación, entrega e informe PDF · ⏱ 10:00 a 11:15

**Hacer:**
1. En A (recepción), recargue la orden #5. Señale que en **Acciones** todavía no hay informe. En **Costos**, señale **Mano de obra, repuestos y total**:
   - Mano de obra: **$60.000**
   - Repuestos: pastillas $85.000 + aceite 4 × $32.000 = $128.000 + filtro $25.000 = **$238.000**
   - Total: **$298.000** — «Valores sin IVA.»
2. Toque **Entregar** → confirme **¿Entregar el carro DEM432?** → **Entregar**.
3. Señale el estado **Entregado**, la fecha de entrega y que ya no hay botones para modificar.
4. En **Acciones**, toque **Descargar informe PDF**. Abra `informe-orden-5.pdf` y recórralo: cliente, vehículo, categoría, observación, diagnóstico, trabajo, repuestos, total e historial sin nombres de empleados.

**Decir:**
> «El total no lo escribe nadie: lo calcula el servidor sumando cantidad por precio, con decimales exactos. Es sin IVA porque la facturación electrónica de la DIAN está fuera del alcance. Al entregar, la orden se cierra y ya no se puede modificar. Solo entonces aparece el informe final en PDF: lo genera el servidor, que es quien verifica que la orden esté entregada, y esa regla tiene pruebas automatizadas. No es una factura: es la constancia del servicio para la clienta.»

---

### Paso 10 — Seguimiento público · ⏱ 11:15 a 12:00

**Hacer:**
1. En D, toque **Actualizar**. Señale «Su carro ya fue entregado. Gracias por su confianza.», la línea de tiempo completa, el cobro y el botón **Descargar informe PDF**.
2. Señale la placa **DEM\*\*\***, y que no aparecen el nombre, el teléfono, el kilometraje ni la observación.
3. Descargue el PDF y señale «Datos personales protegidos (Ley 1581 de 2012)» y la placa enmascarada.

**Decir:**
> «Esto es lo que ve la clienta, sin crear una cuenta. La placa va enmascarada y no hay ningún dato personal, ni notas internas, ni nombres de empleados. El servidor solo envía una lista cerrada de campos, y tenemos una prueba automatizada que busca datos personales en esta respuesta. Su informe PDF tampoco tiene su nombre ni su teléfono; sí trae el diagnóstico y el trabajo, porque es la constancia del servicio ya terminado. Hay un límite de 30 consultas por minuto, para que nadie pruebe códigos al azar.»

---

### Paso 11 — Anonimización · ⏱ 12:00 a 13:30

**Hacer (ventana C, administrador):**
1. **Clientes** → abra **Pedro Ruiz (demo)** → **Anonimizar** → escriba `ANONIMIZAR` → **Anonimizar**. Señale el error **«El cliente tiene órdenes abiertas. Entréguelas o cancélelas antes de anonimizarlo.»** → **Volver**.
2. **Clientes** → abra **Marta Ríos (demo)** → **Anonimizar**.
3. Lea en voz alta el cuadro. Señale que el botón está gris. Escriba `ANONIMIZAR`: el botón se activa. Toque **Anonimizar**.
4. Señale:
   - el nombre «Cliente anonimizado N.º …», sin teléfono, correo ni documento;
   - el aviso «Datos personales anonimizados el [fecha y hora] por Admin Norte»;
   - que ya no hay botones Editar ni Activar;
   - que el carro DEM432 sigue en su lista.
5. Abra la orden #5 desde el carro: sigue completa, con el nombre anonimizado.
6. En D, toque **Actualizar**: el seguimiento sigue funcionando.

**Decir:**
> «La Ley 1581 permite al titular pedir que se eliminen sus datos. Pero el taller no puede borrar sus órdenes, sus cobros ni su inventario. La solución es anonimizar: el sistema borra el nombre, el teléfono, el correo y el documento, y conserva la historia. Solo el administrador puede hacerlo, tiene que escribir la palabra para confirmar, y no se permite si el cliente todavía tiene un carro en el taller. Queda registrado quién lo hizo y cuándo, y una restricción en la base de datos garantiza que eso siempre sea coherente. Es irreversible: si la clienta vuelve, se registra de nuevo con una nueva autorización.»

---

### Cierre — ⏱ 13:30 a 14:00

**Decir:**
> «En resumen: el flujo completo funciona, para carros y motos; cada acción queda registrada con su autor y su hora, el inventario no se descuadra y el cliente está informado y recibe su informe sin exponer sus datos. Esto está respaldado por 263 pruebas automatizadas contra PostgreSQL, que cubren el 91 % del backend. Lo que sigue es desplegarlo con HTTPS, construir el reporte de tiempos por etapa y hacer el piloto en talleres reales para medir el impacto.»

---

## 3. Si sobra tiempo o el jurado lo pide (opcional)

| Demostración | Cómo | Mensaje |
|---|---|---|
| Aislamiento entre talleres | En otro navegador, ingrese como `admin@chipichape.demo.co` y busque la placa `ABC123` | «Es otro carro, un Renault Logan. Cada taller ve solo lo suyo, aunque compartan la base de datos.» |
| Desactivación inmediata | En C, **Usuarios** → desactive a «Mecánico Norte» (fallará si tiene órdenes abiertas: muéstrelo) | RN-16: primero hay que reasignar sus órdenes |
| Devolver de estado | Administrador en una orden en Reparado → **Devolver a …** con nota | Solo el administrador, siempre con nota |
| Pruebas automatizadas | Terminal: `uv run pytest -q` | 263 pruebas pasan (tarda unos 110 segundos) |
| Documentación de la API | `http://localhost:8000/api/docs` | 38 operaciones documentadas automáticamente |
| Informe de una orden no entregada | En el navegador, abra `/api/v1/ordenes/{id}/informe.pdf` de una orden abierta | 409: «El informe PDF solo está disponible cuando la orden fue entregada» |
| Categoría «Otro» | Nueva orden → **Otro** sin describirlo | El sistema exige **Describa el problema** |

## 4. Lista de verificación final

- [ ] Base reiniciada con la semilla.
- [ ] Backend y frontend arrancados; `/api/v1/salud` responde.
- [ ] Ventanas A, B, C y D abiertas en el login (D se abre en el paso 4).
- [ ] Ventana B en vista de celular de 360 px.
- [ ] Zoom al 125 %.
- [ ] Notificaciones del sistema operativo silenciadas.
- [ ] Capturas del plan B a mano.
- [ ] Cronómetro visible.
