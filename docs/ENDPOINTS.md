# Endpoints disponibles y cómo consumirlos

Todos los endpoints de KPI usan la **primera organización** fija en código (`org_n74hvy7njcmb`).  
Base URL de ejemplo: `http://localhost:9000` (o la que uses).

---

## Autenticación

Todas las rutas bajo `/kpi/Producto/` exigen el header:

```http
Authorization: Bearer <TOKEN_GRAFANA>
```

El valor de `TOKEN_GRAFANA` es el que tienes en tu `.env`.  
`/health` no lleva token.

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio (sin token) |
| GET | `/kpi/Producto/test` | Prueba de conectividad |
| GET | `/kpi/Producto/sesiones-creadas` | KPI 4: Sesiones creadas por fecha |
| GET | `/kpi/Producto/dau` | KPI 5: Usuarios activos diarios (DAU) |
| GET | `/kpi/Producto/mau` | KPI 6: Usuarios activos mensuales (MAU) |
| GET | `/kpi/Producto/frecuencia-uso` | KPI 11: Media de sesiones por usuario activo |
| GET | `/kpi/Producto/exportaciones-generadas` | KPI 16: Exportaciones (PDF/Excel) por file |
| GET | `/kpi/Producto/porcentaje-usuarios-duplican-sesiones` | KPI 18: % usuarios con ≥2 sesiones |
| GET | `/kpi/Producto/duracion-media-sesion` | KPI 19: Duración media de sesión (con end_at) |

---

## Cómo consumirlos

### cURL

```bash
# Health (sin token)
curl -s http://localhost:9000/health

# Cualquier KPI (con token)
curl -s -H "Authorization: Bearer TU_TOKEN_GRAFANA" http://localhost:9000/kpi/Producto/test
curl -s -H "Authorization: Bearer TU_TOKEN_GRAFANA" http://localhost:9000/kpi/Producto/dau
curl -s -H "Authorization: Bearer TU_TOKEN_GRAFANA" http://localhost:9000/kpi/Producto/sesiones-creadas
```

Sustituye `TU_TOKEN_GRAFANA` por el valor de `TOKEN_GRAFANA` de tu `.env`.

### PowerShell

```powershell
$token = "TU_TOKEN_GRAFANA"
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:9000/kpi/Producto/dau" -Headers $headers
```

### JavaScript (fetch)

```javascript
const token = 'TU_TOKEN_GRAFANA';
const res = await fetch('http://localhost:9000/kpi/Producto/dau', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await res.json();
```

### Grafana (HTTP Data Source)

- **URL:** `http://localhost:9000` (o la URL de tu API)
- **Auth:** Custom header: `Authorization` = `Bearer <token>`
- **Query:** p. ej. `/kpi/Producto/dau` según el panel

---

## Respuesta típica

Todos los KPIs devuelven un objeto con `kpi` (nombre) y `datos` (resultado del servicio), por ejemplo:

```json
{
  "kpi": "DAU",
  "datos": [
    { "fecha": "2025-02-01", "dau": 12 },
    { "fecha": "2025-02-02", "dau": 8 }
  ]
}
```

`/health` devuelve:

```json
{ "status": "ok" }
```

---

## Organización usada

Por ahora **todos** los datos salen del schema de la **primera organización**, definido en código en `app.core.database` como `FIRST_ORG_SCHEMA = "org_n74hvy7njcmb"`. No se usa multi-tenant; cambiar de org implicaría cambiar esa constante o parametrizarla después.
