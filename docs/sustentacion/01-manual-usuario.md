# Manual de usuario del taller — Taller Digital

| Campo | Valor |
|---|---|
| Para quién | Recepcionistas, administradores y mecánicos del taller |
| Versión del sistema | Commit `84f20f3` (28/10/2026) |
| Dispositivos | Celular (desde 360 px de ancho), tableta o computador, con conexión a internet |

---

## Antes de empezar

### Qué es Taller Digital

Taller Digital es el sistema donde el taller registra a sus clientes y sus carros, recibe cada carro con una **orden de trabajo**, asigna el mecánico, sigue el avance de la reparación, descuenta los repuestos del inventario y calcula lo que se cobra. El cliente sigue su carro desde un **enlace** sin tener que crear una cuenta.

### Quién hace qué

| Tarea | Administrador | Recepción | Mecánico |
|---|---|---|---|
| Crear usuarios, cambiar roles y desactivar personas | Sí | No | No |
| Registrar y editar clientes y carros | Sí | Sí | Solo consulta |
| Anonimizar a un cliente | Sí | No | No |
| Abrir órdenes y asignar o reasignar mecánico | Sí | Sí | No |
| Ver órdenes | Todas | Todas | Solo las asignadas a él |
| Escribir diagnóstico y trabajo realizado; agregar mano de obra y repuestos | Sí | Sí | Solo en sus órdenes |
| Iniciar diagnóstico, pasar a «Esperando repuestos», marcar reparado | Sí | No | Sí, en sus órdenes |
| Entregar el carro y cancelar órdenes | Sí | Sí | No |
| Devolver una orden al estado anterior | Sí | No | No |
| Crear repuestos, registrar entradas y ajustes | Sí | No | No |
| Consultar el inventario | Sí | Sí | Sí |
| Ver el resumen del taller en Inicio | Sí | Sí | No (ve «Mis órdenes abiertas») |
| Copiar el enlace de seguimiento para el cliente | Sí | Sí | No |

### Cómo se mueve uno por el sistema

- **En el computador**, el menú está a la izquierda.
- **En el celular**, el menú está abajo, al alcance del pulgar.
- Las opciones del menú son: **Inicio**, **Órdenes** (para el mecánico se llama **Mis órdenes**), **Clientes**, **Vehículos**, **Inventario** y **Usuarios** (esta última solo la ve el administrador).
- Arriba siempre está el nombre del taller, su nombre con su rol, el buscador **Buscar placa** y el botón **Salir**.

### Los estados de una orden

| Estado | Qué significa en el taller |
|---|---|
| **Recibido** | El carro llegó y se abrió la orden. |
| **En diagnóstico** | El mecánico lo está revisando. |
| **Esperando repuestos** | El trabajo está detenido porque falta un repuesto. Este paso es opcional. |
| **Reparado** | El trabajo terminó; el carro está listo para entregar. |
| **Entregado** | El cliente se llevó el carro. La orden queda cerrada. |
| **Cancelada** | La orden se cerró sin terminar el trabajo. No se cobra. |

Los caminos normales son:

```
Recibido → En diagnóstico → Reparado → Entregado
Recibido → En diagnóstico → Esperando repuestos → Reparado → Entregado
```

Una orden se puede cancelar desde cualquier estado excepto Entregado o Cancelada. **Entregado** y **Cancelada** son finales: la orden ya no se puede modificar.

### Cómo leer los mensajes del sistema

- Los mensajes **verdes** confirman que algo se guardó. Por ejemplo: «Cambios guardados».
- Los mensajes **rojos** explican qué falta o qué impide la acción. El campo con el problema queda marcado.
- Antes de las acciones delicadas (entregar, cancelar, desactivar, quitar un repuesto, anonimizar), el sistema **pide confirmación**.

---

## 1. Inicio de sesión

**Objetivo.** Entrar al sistema con su propio usuario. Cada acción que haga queda registrada a su nombre.

**Cuándo utilizarla.** Al comenzar la jornada, al cambiar de equipo o cuando el sistema le pida iniciar sesión de nuevo.

**Quién.** Todos los roles.

**Paso a paso**

1. Abra el navegador (Chrome, Edge, Firefox o Safari) en la dirección del sistema que le dio el administrador.
2. En la pantalla **Taller Digital — Ingrese con el correo que le dio su taller**, escriba su **Correo**.
3. Escriba su **Clave**. Si quiere comprobar lo que escribió, toque el ícono del ojo para mostrarla u ocultarla.
4. Toque **Ingresar**. El botón se activa cuando ambos campos tienen texto.
5. El sistema lo lleva a **Inicio**.

**Para salir:** toque **Salir** en la barra superior. Hágalo siempre en equipos compartidos.

**Resultado esperado**

- Aparece la pantalla de Inicio con el saludo «Hola, [su nombre]» y el nombre del taller.
- En la barra superior se ven su nombre y su rol (Administrador, Recepción o Mecánico).
- La sesión dura **8 horas**. Después el sistema pide ingresar de nuevo.

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| «Correo o clave incorrectos» | El correo o la clave están mal escritos, o su usuario fue desactivado. Por seguridad, el sistema no dice cuál de las dos cosas falló. | Revise mayúsculas y espacios en la clave (en el correo no importan las mayúsculas). Si sigue igual, pida al administrador que revise su usuario. |
| «Su sesión no es válida. Inicie sesión de nuevo.» | Pasaron más de 8 horas o el administrador lo desactivó. | Ingrese de nuevo. Si no puede, hable con el administrador. |
| «No hay conexión con el servidor. Revise su internet e intente de nuevo.» | No hay internet o el servidor no responde. | Revise la conexión e intente de nuevo. |

---

## 2. Gestión de usuarios

**Objetivo.** Dar acceso a cada persona del taller con su propio usuario, definir su rol y quitar el acceso cuando ya no trabaje en el taller.

**Cuándo utilizarla.** Cuando entra una persona nueva, cuando alguien cambia de función o cuando alguien deja el taller.

**Quién.** Solo el **administrador**. El detalle está en el [Manual del administrador](02-manual-administrador.md).

**Paso a paso — crear un usuario**

1. En el menú, entre a **Usuarios**. Verá «Usuarios del taller».
2. Toque **+ Usuario**.
3. Complete el formulario **Nuevo usuario**:
   - **Nombre** de la persona.
   - **Correo** con el que va a ingresar. No puede estar registrado en ningún taller del sistema.
   - **Clave inicial**, de mínimo 8 caracteres. Entréguela a la persona en privado.
   - **Rol**: Administrador, Recepción o Mecánico.
4. Toque **Guardar usuario**.

**Paso a paso — cambiar el rol**

1. En la lista de usuarios, busque a la persona.
2. En la lista desplegable **Rol de [nombre]**, elija el nuevo rol. El cambio se guarda de inmediato.

**Paso a paso — desactivar o activar**

1. En la fila de la persona, toque **Desactivar** (o **Activar**).
2. Confirme en el cuadro «¿Desactivar este usuario?».

**Resultado esperado**

- Al crear: aparece «Usuario [nombre] creado» y la persona ya puede ingresar.
- Al cambiar el rol: aparece «[nombre] ahora es [rol]».
- Al desactivar: la persona **pierde el acceso de inmediato**, aunque tenga la sesión abierta. Su historial se conserva.

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| «Ya existe un usuario con el correo …» | El correo es único en todo el sistema. | Use otro correo. |
| «Debe tener al menos 8 caracteres» en Clave inicial | La clave inicial es muy corta. | Escriba una clave más larga. |
| «[nombre] tiene … órdenes abiertas…» al desactivar o cambiar el rol de un mecánico | Un mecánico con órdenes abiertas no se puede desactivar ni cambiar de rol (RN-16). | Reasigne primero sus órdenes abiertas a otro mecánico. |
| No aparece el botón Desactivar en su propia fila, o el rol está bloqueado | Nadie puede quitarse su propio acceso. | Pida a otro administrador que haga el cambio. |

---

## 3. Gestión de clientes

**Objetivo.** Tener en un solo lugar los datos de contacto de los dueños de los carros, con su autorización de tratamiento de datos (Ley 1581 de 2012).

**Cuándo utilizarla.** Cuando llega un cliente por primera vez, cuando cambia su teléfono o correo, o cuando hay que buscar a quién pertenece un carro.

**Quién.** Administrador y Recepción crean y editan. El mecánico solo consulta.

**Paso a paso — registrar un cliente**

1. Entre a **Clientes** y toque **+ Cliente**.
2. Complete **Nuevo cliente**:
   - **Nombre** (obligatorio).
   - **Teléfono** (obligatorio). Puede escribirlo con espacios, por ejemplo «300 123 4567»; el sistema los quita.
   - **Correo** (opcional).
   - **Documento** (opcional). Cédula o NIT; pídalo solo si el cliente lo quiere dar.
3. **Lea al cliente** la autorización y, si acepta, marque la casilla **«El cliente autoriza el tratamiento de sus datos personales (Ley 1581 de 2012)»**. Sin esta casilla el sistema no registra al cliente.
4. Toque **Guardar cliente**.

**Paso a paso — buscar un cliente**

1. Entre a **Clientes**.
2. Escriba en **Buscar por nombre, teléfono o documento**. La lista se filtra mientras escribe.
3. Para ver también los clientes desactivados, marque **Incluir inactivos**.
4. Toque el cliente para abrir su detalle: teléfono, correo, documento, fecha de autorización y sus carros.

**Paso a paso — editar o desactivar**

1. En el detalle del cliente, toque **Editar**, cambie los datos y toque **Guardar cambios**.
2. Para desactivarlo, toque **Desactivar** y confirme. Dejará de aparecer en las búsquedas y no se le podrán asociar carros nuevos. Sus datos y carros se conservan, y se puede **Activar** de nuevo.

**Resultado esperado**

- Aparece «Cliente [nombre] registrado» y se abre su detalle.
- El detalle muestra «Autorizó el [fecha]»: es la fecha en que el sistema registró la autorización.

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| Mensaje en la casilla de autorización: «Sin la autorización de tratamiento de datos (Ley 1581) no se puede registrar al cliente» | No se marcó la autorización. | Explíquele al cliente para qué se usan sus datos y marque la casilla solo si acepta. |
| «Escriba un teléfono de 7 a 15 dígitos» | El teléfono tiene letras o muy pocos números. | Escriba solo números; se admite un «+» al inicio. |
| «Correo no válido» | Falta la @ o el dominio. | Corrija el correo o déjelo vacío. |
| «Ya existe un cliente con ese documento en el taller» | Ese documento ya está registrado. | Busque al cliente por su documento: probablemente ya existe. |
| «Los datos de este cliente fueron anonimizados y ya no se pueden modificar» | El cliente fue anonimizado (ver sección 13). | Si la persona volvió, regístrela como cliente nuevo. |

> **Recuerde:** pida solo los datos necesarios. El correo y el documento son opcionales.

---

## 4. Gestión de vehículos

**Objetivo.** Registrar cada carro o moto a nombre de su dueño, con placa única, y consultar su historial de mantenimiento.

**Cuándo utilizarla.** Cuando un carro llega por primera vez, cuando cambia de dueño o cuando necesita ver qué se le ha hecho antes.

**Quién.** Administrador y Recepción registran y editan. El mecánico solo consulta.

**Paso a paso — registrar un carro**

1. Puede empezar de tres formas:
   - desde el detalle del cliente, con **+ Carro** (el dueño queda elegido);
   - desde **Vehículos**, con **+ Carro**;
   - desde **Nueva orden**, con el enlace **Registrar el carro** cuando la placa no existe.
2. Complete **Nuevo carro**:
   - **Placa** (obligatoria). Escríbala sin espacios ni guiones; si los pone, se corrige sola al salir del campo. Debe tener de 5 a 7 letras o números.
   - **Marca** y **Modelo** (obligatorios). Por ejemplo, «Mazda» y «3».
   - **Año** y **Color** (opcionales).
   - **Dueño**: busque y elija un cliente activo.
3. Toque **Guardar carro**.

**Paso a paso — buscar un carro**

- **Rápido:** escriba la placa en **Buscar placa**, arriba, y presione Enter. Si la placa existe, se abre el carro; si no, se ven las coincidencias parciales.
- **Desde Vehículos:** escriba la placa completa o una parte, por ejemplo «ABC» o «123».

**Paso a paso — cambiar el dueño (venta del carro)**

1. En el detalle del carro, toque **Editar**.
2. Cambie el dueño. Hágalo solo si el carro se vendió.
3. Toque **Guardar cambios**. Las órdenes anteriores conservan al dueño que tenían en su momento.

**Paso a paso — ver el historial de mantenimiento**

1. Abra el carro, desde la búsqueda o desde el cliente.
2. En **Historial de mantenimiento** verá todas sus órdenes: fecha, motivo, mecánico y estado.
3. Si el carro tiene una orden abierta, aparece un botón para ir a ella. Si no, aparece **Nueva orden para este carro**.

**Resultado esperado**

- Aparece «Carro [placa] registrado» y se abre el detalle **Carro de placa [placa]**, con su dueño y su historial.

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| «Ya existe un carro con la placa … en el taller» | La placa ya está registrada en este taller. | Búsquela con **Buscar placa**. |
| «El cliente está inactivo. Actívelo antes de asociarle un carro.» | El dueño elegido está desactivado. | Active al cliente o elija otro. |
| «La placa debe tener entre 5 y 7 letras o números, por ejemplo ABC123» | La placa es muy corta o muy larga. | Revise la placa. |
| «Elija el dueño del carro» | No se eligió el cliente. | Busque y elija al dueño. |

---

## 5. Apertura de órdenes (recepción del carro)

**Objetivo.** Recibir el carro y dejar registrado por qué entra, con qué kilometraje y cuándo se espera entregar.

**Cuándo utilizarla.** Cada vez que un carro entra al taller para cualquier trabajo.

**Quién.** Administrador y Recepción.

**Paso a paso**

1. Toque **Nueva orden** en Inicio o en Órdenes. Si está viendo el carro, toque **Nueva orden para este carro**: así el carro ya queda elegido y se ahorra un paso.
2. En **Placa del carro**, escriba la placa. El sistema muestra los carros activos que coinciden; toque el correcto. Verá la placa, la marca, el modelo y el dueño.
   - Si el carro no existe, toque **Registrar el carro** (sección 4) y luego vuelva.
3. Escriba el **Motivo de ingreso**, con las palabras del cliente. Por ejemplo: «ruido en la suspensión».
4. Escriba el **Kilometraje** (opcional, recomendado).
5. Elija la **Entrega estimada** (opcional). No puede ser anterior a hoy.
6. Elija el **Mecánico** (opcional). Puede asignarlo después.
7. Toque **Abrir orden**.

**Resultado esperado**

- Aparece «Orden #[número] abierta para [placa]» y se abre el detalle de la orden en estado **Recibido**.
- El número es consecutivo dentro de su taller.
- El historial muestra «Abrió la orden», con su nombre, la fecha y la hora.

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| «El carro [placa] ya tiene una orden abierta» y el enlace **Ver la orden** | Un carro solo puede tener una orden abierta a la vez (RN-08). | Abra la orden existente. |
| «El carro está inactivo. Actívelo antes de recibirlo.» | El carro fue desactivado. | Actívelo desde su detalle (**Activar**). |
| «El dueño del carro está inactivo. Actívelo antes de abrir la orden.» | El cliente está desactivado o fue anonimizado. | Active al cliente. Si fue anonimizado, registre al nuevo dueño y cámbielo en el carro. |
| «Busque y elija el carro» | No se tocó ningún carro de la lista. | Escriba la placa y elija el carro. |
| «La fecha estimada de entrega no puede ser anterior a hoy» | Se eligió una fecha pasada. | Elija hoy o una fecha posterior. |

---

## 6. Asignación de mecánicos

**Objetivo.** Dejar claro qué mecánico responde por cada carro. Cada asignación queda registrada.

**Cuándo utilizarla.** Al abrir la orden, o después si no se asignó. Para **reasignar**, cuando el mecánico se ausenta o se reparte mejor el trabajo.

**Quién.** Administrador y Recepción.

**Paso a paso**

1. Abra la orden.
2. En el recuadro **Mecánico** verá el nombre asignado o «Sin asignar».
3. Toque **Asignar** (o **Reasignar**).
4. Elija el mecánico. La lista muestra los mecánicos activos y cuántas órdenes abiertas tiene cada uno, para repartir la carga.
5. Si reasigna, puede escribir el **Motivo de la reasignación (opcional)**.
6. Toque **Guardar**.

**Resultado esperado**

- Aparece «Orden asignada a [nombre]».
- En el historial queda «Asignó a …» o «Reasignó a …», con quién lo hizo y cuándo.
- La orden aparece en **Mis órdenes** del nuevo mecánico. El mecánico anterior deja de verla.

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| «Elija un mecánico» | No se eligió a nadie. | Elija un mecánico de la lista. |
| «La orden ya está asignada a [nombre]» | Eligió al mismo mecánico. | Elija otro o cancele. |
| «Elija un mecánico activo del taller» | El mecánico fue desactivado mientras usted elegía. | Recargue y elija otro. |
| No aparece el botón Asignar | La orden ya está entregada o cancelada, o usted es mecánico. | Solo se asigna en órdenes abiertas, y solo Recepción o el Administrador. |

---

## 7. Cambio de estados

**Objetivo.** Mostrar en qué va cada carro. Cada cambio queda registrado con fecha, hora, usuario y nota; con esa información se medirán los tiempos de cada etapa.

**Cuándo utilizarla.** Cada vez que el trabajo avanza, se detiene por un repuesto, termina o se cancela.

**Quién.** Depende del cambio:

| Cambio | Quién lo hace |
|---|---|
| Iniciar diagnóstico | Mecánico asignado o Administrador |
| Esperando repuestos | Mecánico asignado o Administrador |
| Marcar reparado | Mecánico asignado o Administrador |
| Entregar | Recepción o Administrador (sección 11) |
| Cancelar orden | Recepción o Administrador |
| Devolver a [estado anterior] | Solo el Administrador |

El sistema **solo muestra los botones que usted puede usar** en el estado actual.

### 7.1 Para el mecánico: trabajar una orden

1. Entre a **Mis órdenes**, o mire «Mis órdenes abiertas» en Inicio, y abra la orden.
2. Toque **Iniciar diagnóstico**. Si el sistema muestra «Asigne un mecánico para iniciar el diagnóstico», la orden no tiene mecánico y debe asignarla Recepción.
3. En **Trabajo en el carro**, escriba el **Diagnóstico**: qué encontró al revisar el carro. Toque **Guardar**. Si ve «Cambios sin guardar», todavía no ha guardado.
4. Registre la mano de obra y los repuestos (secciones 9 y 10).
5. Si falta un repuesto, toque **Esperando repuestos**. En el cuadro puede escribir **Qué repuesto falta** (opcional) y luego tocar **Confirmar**.
6. Al terminar, escriba el **Trabajo realizado**: es obligatorio para marcar la orden como reparada.
7. Toque **Marcar reparado**. Si escribió algo sin guardar, el sistema lo guarda antes de cambiar el estado.

### 7.2 Cancelar una orden

1. En la orden, toque **Cancelar orden**.
2. Escriba el **Motivo de la cancelación**. Es obligatorio.
3. Toque **Cancelar orden** en el cuadro.

La orden se cierra, no se cobra y los repuestos que tenía **vuelven al inventario** automáticamente.

### 7.3 Devolver una orden al estado anterior (solo Administrador)

1. Toque **Devolver a [estado]**.
2. Escriba **Por qué la devuelve**. Es obligatorio.
3. Toque **Devolver**.

Desde Reparado, la orden vuelve al estado del que venía (En diagnóstico o Esperando repuestos). **No** se puede volver de Esperando repuestos a En diagnóstico.

**Resultado esperado**

- Aparece «Orden #[número]: [nuevo estado]».
- El indicador de estado y la **línea de tiempo** se actualizan.
- En **Historial** queda el cambio («En diagnóstico → Reparado»), con usuario, fecha, hora y nota.

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| «Asigne un mecánico antes de iniciar el diagnóstico» | La orden no tiene mecánico (RN-13). | Recepción o el Administrador asignan uno. |
| «Escriba el trabajo realizado antes de marcar la orden como reparada» | El campo Trabajo realizado está vacío (RN-17). | Escríbalo y vuelva a intentar. |
| «Este campo es obligatorio» en el cuadro de cancelación o devolución | Falta el motivo (RN-18). | Escriba el motivo. |
| «La orden #… ya fue entregada (o cancelada) y no se puede modificar» | La orden está cerrada (RN-07). | Si el carro vuelve, abra una orden nueva. |
| «Su rol no puede pasar la orden a …» | Su rol no tiene ese cambio. | Pida el cambio a la persona que corresponda. |
| La orden no aparece en Mis órdenes | Fue reasignada a otro mecánico. | Pregunte en recepción. |

---

## 8. Inventario

**Objetivo.** Saber cuánto hay de cada repuesto, recibir avisos antes de que se acabe y dejar rastro de cada entrada, salida y ajuste.

**Cuándo utilizarla.** Al consultar si hay un repuesto, al recibir mercancía, al hacer un conteo físico o cuando aparece una alerta de stock bajo.

**Quién.** Todos consultan la lista. Solo el **Administrador** abre el detalle, crea o edita repuestos y registra entradas y ajustes.

**Paso a paso — consultar**

1. Entre a **Inventario**.
2. Escriba en el buscador el nombre o el código, por ejemplo «filtro» o «W712».
3. Marque **Solo con stock bajo** para ver lo que hay que pedir. Marque **Incluir inactivos** para ver también los repuestos desactivados.
4. Cada repuesto muestra su stock. Si está en el mínimo o por debajo, aparece «Stock bajo: [cantidad]»; si se acabó, «Agotado». El aviso siempre tiene texto e ícono, no solo color.

**Paso a paso — registrar una entrada de mercancía (Administrador)**

1. Abra el repuesto en **Inventario**.
2. Toque **Registrar entrada**.
3. Escriba la **Cantidad que entró** en la unidad del repuesto. Se suma al stock actual.
4. En **Nota (opcional)** escriba el proveedor o el número de factura.
5. Toque **Registrar entrada**.

**Paso a paso — ajustar por conteo físico (Administrador)**

1. Abra el repuesto y toque **Ajustar por conteo**.
2. Escriba la **Cantidad contada en el estante**. El stock queda igual a lo que contó; el sistema calcula la diferencia y la registra.
3. Escriba el **Motivo del ajuste**. Es obligatorio; por ejemplo: «conteo de fin de mes», «daño» o «pérdida».
4. Toque **Guardar ajuste**.

**Resultado esperado**

- Aparece «Stock de [repuesto]: [cantidad] [unidad]».
- En los **movimientos** del repuesto queda la entrada o el ajuste, con usuario, fecha, cantidad, stock resultante y nota.
- Si el repuesto estaba en alerta y ya superó el mínimo, la alerta desaparece de Inicio y del inventario.

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| «Escriba cuántas unidades entraron» o «Escriba cuántas unidades contó» | Falta la cantidad. | Escriba la cantidad. |
| «Escriba el motivo del ajuste» | El motivo es obligatorio en los ajustes. | Explique por qué cambia el stock. |
| «El stock ya es …: no hay nada que ajustar» | Lo contado es igual a lo registrado. | No hace falta ajustar. |
| «El repuesto está inactivo. Actívelo antes de moverle el stock.» | El repuesto fue desactivado. | Actívelo primero. |
| No puede abrir el detalle de un repuesto | Su rol no es Administrador. | Consulte el stock en la lista; los movimientos los hace el Administrador. |

---

## 9. Repuestos

Esta función tiene dos partes: el **catálogo** de repuestos (Administrador) y el **uso de repuestos en una orden** (Mecánico asignado, Recepción y Administrador).

### 9.1 Crear o editar un repuesto en el catálogo (Administrador)

**Objetivo.** Tener la lista de repuestos que maneja el taller, con precio de venta y stock mínimo.

**Cuándo utilizarla.** Cuando el taller empieza a manejar un repuesto nuevo, o cuando cambia el precio o el mínimo de uno existente.

**Paso a paso**

1. En **Inventario**, toque **+ Repuesto**.
2. Complete **Nuevo repuesto**:
   - **Nombre**, por ejemplo «Filtro de aceite Mann W712».
   - **Código**: la referencia del fabricante o la que use el taller. No se puede repetir.
   - **Precio de venta (pesos)** por unidad, por ejemplo «25.000». Cambiarlo después no altera las órdenes ya registradas.
   - **Unidad**: unidad, litro, galón, juego, kit, metro, par u otra que escriba.
   - **Stock mínimo**: al llegar a esta cantidad, el sistema avisa que hay que pedir más.
   - **Stock actual en el estante**: queda registrado como la primera entrada del repuesto.
3. Toque **Guardar repuesto**.

Para editarlo: abra el repuesto, toque **Editar** y luego **Guardar cambios**. Para retirarlo, use **Desactivar**: no se podrá agregar a nuevas órdenes, pero su historial y su stock se conservan.

**Errores comunes:** «Ya existe un repuesto con el código …»: el código ya está en el catálogo de su taller.

### 9.2 Usar un repuesto en una orden

**Objetivo.** Registrar lo que se instaló en el carro. El sistema lo descuenta del inventario y lo suma al cobro.

**Cuándo utilizarla.** Cada vez que se saca un repuesto del estante para un carro.

**Paso a paso**

1. En la orden, sección **Mano de obra, repuestos y total**, toque **+ Repuesto**.
2. En **Repuesto**, escriba el nombre o el código. La lista muestra el precio, la unidad y cuánto hay. Los repuestos agotados aparecen pero no se pueden elegir.
3. Elija el repuesto y escriba la **Cantidad**. Se admiten decimales, por ejemplo «4,5» litros de aceite.
4. Toque **Agregar repuesto**.

**Para quitar un repuesto** mal registrado: toque el ícono de la papelera en la línea y confirme con **Quitar**. El repuesto vuelve al inventario.

**Resultado esperado**

- Aparece «[repuesto] agregado; se descontó del inventario».
- La línea muestra la cantidad, el precio unitario, quién la registró y el subtotal.
- El total de la orden se recalcula.
- El precio queda **fijo en la orden**, aunque después cambie en el catálogo.

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| «No hay suficiente [repuesto]: quedan …» | La cantidad supera el stock. El sistema nunca deja el stock negativo (RN-02). | Use lo que hay, deje la orden en «Esperando repuestos» y avise al Administrador para registrar la entrada. |
| «Elija un repuesto» | No se eligió de la lista. | Escriba y toque el repuesto. |
| «El repuesto está inactivo» | Fue desactivado del catálogo. | Pida al Administrador que lo active o elija otro. |
| No aparecen los botones + Repuesto / + Mano de obra | La orden está cerrada, o usted es mecánico y la orden no es suya. | Solo se registran líneas en órdenes abiertas. |

---

## 10. Liquidación

**Objetivo.** Saber cuánto se cobra, con el detalle de mano de obra y repuestos. El total lo calcula el sistema, nadie lo escribe a mano.

**Cuándo utilizarla.** Durante el trabajo, para registrar la mano de obra; y antes de entregar, para revisar el cobro con el cliente.

**Quién.** Mecánico asignado, Recepción y Administrador registran líneas en órdenes abiertas. Todos los que ven la orden ven la liquidación.

**Paso a paso — agregar mano de obra**

1. En la orden, sección **Mano de obra, repuestos y total**, toque **+ Mano de obra**.
2. Escriba el **Trabajo realizado**, por ejemplo «Cambio de pastillas» o «Alineación».
3. Escriba el **Valor (pesos)** en pesos enteros, por ejemplo «40.000».
4. Cambie la **Cantidad** si aplica (por defecto es 1).
5. Toque **Agregar**.

> No escriba datos personales del cliente en la descripción: el cliente la ve en su enlace de seguimiento.

**Paso a paso — revisar la liquidación**

1. Mire el resumen al final de la sección:
   - **Mano de obra**: suma de las líneas de mano de obra.
   - **Repuestos**: suma de cantidad × precio de cada repuesto.
   - **Total**: la suma de las dos.
2. Debajo dice **«Valores sin IVA.»** El sistema no factura ni calcula impuestos.

**Resultado esperado**

- Aparece «Mano de obra agregada: [descripción]» y el total se actualiza.
- Si la orden se cancela, dice «Orden cancelada: no se cobra. Los repuestos volvieron al inventario.»

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| Error en Valor | El valor está vacío o no es un número. | Escriba solo números; el punto de miles es opcional. |
| Una mano de obra quedó mal escrita | No se puede editar una línea. | Quítela (papelera, **Quitar**) y agréguela de nuevo. |

**Importante:** la liquidación **no es una factura electrónica**. La facturación DIAN está fuera del alcance del sistema.

---

## 11. Entrega de vehículos

**Objetivo.** Cerrar la orden cuando el cliente se lleva el carro y dejar registrada la fecha de entrega.

**Cuándo utilizarla.** Cuando la orden está en **Reparado** y el cliente recoge el carro.

**Quién.** Recepción y Administrador.

**Paso a paso**

1. Abra la orden. Debe estar en **Reparado**.
2. Revise con el cliente la sección **Mano de obra, repuestos y total**.
3. Toque **Entregar**.
4. Confirme en el cuadro **«¿Entregar el carro [placa]?»**: la orden se cierra como entregada y ya no se podrá modificar.

**Resultado esperado**

- La orden pasa a **Entregado**, con fecha y hora en **Entregado**.
- Aparece en el historial de mantenimiento del carro.
- Cuenta en **Entregados hoy** en Inicio.
- El enlace del cliente muestra «Su carro ya fue entregado. Gracias por su confianza.»
- El carro ya puede recibir una orden nueva.

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| No aparece el botón Entregar | La orden no está en Reparado, o su rol es Mecánico. | El mecánico debe marcarla como reparada. |
| Entregó por error | Entregado es un estado final y no se deshace. | Si el carro vuelve, abra una orden nueva; deje la explicación en el motivo de ingreso. |

---

## 12. Seguimiento del cliente

**Objetivo.** Que el cliente vea el estado de su carro y lo que se le va a cobrar desde su celular, sin llamar al taller y sin crear una cuenta.

**Cuándo utilizarla.** Al abrir la orden, para enviarle el enlace al cliente, y cada vez que el cliente pregunte por su carro.

**Quién.** Recepción y Administrador comparten el enlace. El cliente lo abre sin usuario ni clave.

**Paso a paso — compartir el enlace (taller)**

1. Abra la orden.
2. En **Enlace para el cliente**, toque **Copiar enlace**. Aparece «Copiado».
3. Péguelo en su conversación de WhatsApp, SMS o correo con el cliente. **El sistema no envía mensajes por sí solo.**
4. Para ver lo mismo que ve el cliente, toque **Ver como el cliente**.

**Lo que ve el cliente**

- El nombre del taller, el número de orden y la **placa enmascarada** (por ejemplo, «ABC***»), la marca y el modelo.
- El estado actual con un mensaje claro, por ejemplo «Estamos revisando su carro» o «¡Su carro está listo! Puede pasar a recogerlo.»
- La línea de tiempo de los estados con fechas.
- La mano de obra, los repuestos y el total, con la nota «Valores sin IVA. Pueden cambiar mientras el carro esté en el taller.»
- Un botón **Actualizar**.

**Lo que el cliente NO ve:** su nombre, teléfono, documento o correo; la placa completa; el kilometraje; el motivo de ingreso; las notas internas; ni los nombres de los empleados.

**Resultado esperado.** El cliente abre el enlace en su celular y ve el estado al momento.

**Errores comunes**

| Lo que ve el cliente | Por qué pasa | Qué hacer |
|---|---|---|
| «No encontramos esta orden — Revise que el enlace esté completo o pídale uno nuevo al taller.» | El enlace se copió incompleto. | Cópielo de nuevo desde la orden y reenvíelo. |
| «Demasiadas consultas seguidas. Espere un minuto.» | Se hicieron más de 30 consultas en un minuto desde la misma conexión. | Esperar un minuto. |

> Trate el enlace como información del cliente: quien lo tenga puede ver el estado de esa orden. Envíelo solo al dueño.

---

## 13. Anonimización de clientes

**Objetivo.** Cumplir la solicitud de un cliente que pide eliminar sus datos personales (Ley 1581 de 2012), **sin perder** la historia del taller: órdenes, carros, cobros e inventario.

**Cuándo utilizarla.** **Solo** cuando el cliente pide expresamente que se borren sus datos. Para dejar de ver a un cliente en las búsquedas, use **Desactivar**, que sí se puede deshacer.

**Quién.** Solo el **Administrador**.

**Antes de empezar, verifique que:**
- el cliente lo pidió y usted confirmó su identidad;
- el cliente **no tiene órdenes abiertas**: entréguelas o cancélelas primero;
- entiende que **no se puede deshacer**.

**Paso a paso**

1. Entre a **Clientes** y abra el cliente.
2. Toque **Anonimizar**.
3. Lea el cuadro **«¿Anonimizar a [nombre]?»**. Explica que:
   - se borran para siempre su nombre, teléfono, correo y documento;
   - sus carros, órdenes e historial se conservan y el enlace de seguimiento sigue funcionando;
   - el cliente queda inactivo y **esto no se puede deshacer**.
4. En **Escriba ANONIMIZAR para confirmar**, escriba la palabra **ANONIMIZAR**. El botón se activa solo cuando la palabra es correcta.
5. Toque **Anonimizar**. Si se arrepiente, toque **Volver**.

**Resultado esperado**

- Aparece «Los datos personales del cliente se anonimizaron».
- El cliente pasa a llamarse **«Cliente anonimizado N.º [número]»**, sin teléfono, correo ni documento, y queda **inactivo**.
- Un aviso indica **«Datos personales anonimizados el [fecha y hora] por [administrador]»**.
- Desaparecen los botones Editar y Activar.
- Sus órdenes, su historial y sus carros siguen visibles con el nombre anonimizado.
- Si la persona vuelve al taller, se registra como cliente nuevo, con una nueva autorización. Su documento puede usarse otra vez.

**Errores comunes**

| Lo que ve | Por qué pasa | Qué hacer |
|---|---|---|
| «El cliente tiene órdenes abiertas. Entréguelas o cancélelas antes de anonimizarlo.» | El taller todavía necesita contactarlo. | Cierre sus órdenes y vuelva a intentar. |
| El botón Anonimizar del cuadro está gris | La palabra no está bien escrita. | Escriba ANONIMIZAR (no importan las mayúsculas). |
| «Este cliente ya fue anonimizado» | La acción ya se hizo antes. | No hay que hacer nada más. |
| No aparece el botón Anonimizar | Su rol no es Administrador, o el cliente ya está anonimizado. | Pida la acción al Administrador. |

**Limitación conocida:** los textos libres de las órdenes (motivo de ingreso, diagnóstico, trabajo realizado y notas) **no se modifican**. Por eso nunca escriba datos personales del cliente en esos campos.

---

## Anexo — Preguntas rápidas

| Pregunta | Respuesta |
|---|---|
| ¿Se puede borrar un cliente, un carro o una orden? | No. Clientes, carros, repuestos y usuarios se **desactivan**; órdenes, historial y movimientos nunca se borran. Los datos personales de un cliente se pueden **anonimizar**. |
| ¿El sistema envía mensajes de WhatsApp? | No. Usted copia el enlace y lo envía. |
| ¿El sistema factura o calcula IVA? | No. La liquidación es sin IVA y no reemplaza la factura. |
| ¿Funciona sin internet? | No. |
| ¿Puedo cambiar mi clave? | En esta versión no hay una pantalla para hacerlo. Es una función pendiente. |
| ¿Puedo ver datos de otro taller? | No. Cada taller ve solo lo suyo. |
| ¿Hay reportes de tiempos? | Todavía no. Los datos se registran desde el primer cambio de estado; los reportes están pendientes (Semana 5). |
