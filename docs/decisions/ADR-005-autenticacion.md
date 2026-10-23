# ADR-005: Autenticación con cookie httpOnly y seguimiento público por código

## Estado
Aprobado (23/10/2026)

## Fecha
23/10/2026

## Contexto

- Los usuarios internos (ADMIN, RECEPCION y MECANICO) acceden a datos personales protegidos por la Ley 1581.
- Cada mecánico tiene su propio usuario (P-7).
- Los clientes **no** tienen cuenta: consultan su orden con un enlace único (P-4).
- La aplicación web (SPA) y la API se sirven desde el mismo dominio (ADR-001).
- En el plan gratuito de hosting hay una sola instancia de la aplicación.

## Decisión

### Usuarios internos

- **Contraseñas:** se guardan con hash argon2id. Nunca se guardan ni se escriben en los logs en texto plano.
- **Inicio de sesión:** con correo y contraseña.
  - El correo es único en todo el sistema y se guarda en minúsculas.
  - Si los datos son incorrectos, el mensaje es genérico: no indica si falló el correo o la contraseña.
- **Sesión:** un JWT firmado con HS256, que contiene el identificador del usuario y la fecha de vencimiento.
  - Se guarda en una cookie con los atributos `HttpOnly`, `Secure` (en producción), `SameSite=Lax` y `Path=/`.
  - Dura 8 horas, una jornada de trabajo.
  - La clave de firma se lee de la variable de entorno `SECRET_KEY`.
- **Cada solicitud protegida vuelve a leer al usuario en la base de datos** para obtener su `taller_id`, su `rol` y si está `activo`. Así:
  - un usuario desactivado pierde el acceso de inmediato;
  - el rol y el taller **nunca** se toman de datos enviados por el cliente.
- **Autorización:** la verifica la capa de servicios en cada solicitud.
  - Que el rol tenga permiso (matriz del SPEC §3).
  - Que el recurso pertenezca al taller del usuario (ADR-006).
  - Si el usuario es mecánico, que la orden esté asignada a él.
- **Protección contra CSRF:** la cookie con `SameSite=Lax` no se envía en solicitudes POST, PATCH o DELETE que vienen de otros sitios. Además, las operaciones que modifican datos solo aceptan `application/json`. No se habilita CORS.
- **Límite de intentos de inicio de sesión:** unos 10 intentos cada 15 minutos por dirección IP y por correo.
  - El contador vive en memoria porque hay una sola instancia.
  - **Si algún día hay varias instancias, el contador debe pasar a un almacén compartido.**
- **Cabeceras de seguridad:**
  - CSP con `default-src 'self'`;
  - HSTS en producción;
  - `X-Content-Type-Options`;
  - `X-Frame-Options`.
- **Primer usuario de cada taller:** lo crea el desarrollador con un script. No existe registro público (ADR-006).

### Seguimiento público para clientes

- Cada orden tiene un `codigo_seguimiento` aleatorio, generado con un generador criptográfico: al menos 128 bits, codificado para poder ir en una URL.
- El enlace tiene la forma `ORIGEN_PUBLICO/seguimiento/{codigo}`.
- La página no pide inicio de sesión, tiene límite de solicitudes y es solo de lectura.
- **Muestra únicamente:**
  - nombre del taller;
  - número de orden;
  - placa enmascarada (ABC***);
  - marca y modelo;
  - estado y línea de tiempo;
  - liquidación.
- **Nunca muestra:** documento, teléfono, correo, notas internas ni el nombre completo del cliente.
- Si el código no existe, responde "no encontrado".
- El enlace no vence mientras exista la orden.

## Alternativas consideradas

| Alternativa | Decisión | Motivo |
|---|---|---|
| JWT guardado en `localStorage` | Rechazada | Cualquier fallo de XSS permitiría robar el token. Las buenas prácticas de seguridad lo prohíben. |
| Sesiones guardadas en una tabla del servidor | Rechazada por simplicidad | Necesita otra tabla y limpieza periódica. Releer al usuario en cada solicitud ya permite quitar el acceso de inmediato. |
| Cuentas de usuario para los clientes | Rechazada | Lo decidió el autor en P-4. |
| Seguimiento usando solo la placa | Rechazada | Una placa se puede adivinar y expondría los datos de otras personas. |

## Consecuencias

**Positivas:**
- Ningún token es accesible desde JavaScript.
- El acceso se revoca de inmediato.
- El cliente no tiene que recordar ninguna contraseña.
- Se expone el mínimo de datos personales.

**Negativas:**
- Cada solicitud hace una consulta adicional para leer al usuario. Con el volumen del piloto el costo es despreciable.
- Si el servicio se reinicia, se pierde el contador de intentos de inicio de sesión. Para el MVP es aceptable.

**Riesgo aceptado:** si el cliente reenvía su enlace, quien lo reciba puede ver el estado y la liquidación de la orden, pero ningún dato personal.

## Trazabilidad

- D1: glosario (Gestión de Usuarios, RBAC) y §3.6 (Ley 1581).
- Decisiones del autor: P-4 y P-7.
- SPEC: §3, §5 (RNF-04 y RNF-06) y §10.
