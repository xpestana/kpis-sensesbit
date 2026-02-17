# pgAdmin: acceder e importar un dump

Con Docker Compose ya incluye **pgAdmin** (interfaz web para PostgreSQL, similar a phpMyAdmin).

## 1. Arrancar los contenedores

```bash
docker compose up -d
```

pgAdmin queda en: **http://localhost:5050**

## 2. Entrar en pgAdmin

1. Abre **http://localhost:5050** en el navegador.
2. **Email:** el que tengas en `.env` como `PGADMIN_EMAIL` (por defecto `admin@example.com`).
3. **Password:** el que tengas en `PGADMIN_PASSWORD` (por defecto `admin`).

## 3. Registrar el servidor PostgreSQL

1. Clic derecho en **Servers** → **Register** → **Server**.
2. **General** → **Name:** por ejemplo `Kpis Postgres`.
3. **Connection:**
   - **Host:** `postgres` (nombre del servicio en Docker, no `localhost`).
   - **Port:** `5432`.
   - **Maintenance database:** `kpis` (o el valor de `POSTGRES_DB` en tu `.env`).
   - **Username:** `kpis` (o `POSTGRES_USER`).
   - **Password:** la de `POSTGRES_PASSWORD`.
4. Guardar (**Save**).

## 4. Importar un dump (restore)

### Opción A: Desde la interfaz (Backup/Restore)

1. Clic derecho en la base de datos **kpis** (o la que uses) → **Restore…**.
2. Pestaña **General:**
   - **Filename:** elegir tu archivo `.backup` o `.dump` (debe estar en una ruta accesible por el contenedor; si no, usa la Opción B).
3. Pestaña **Restore options** si quieres ajustar (por defecto suele bastar).
4. **Restore**.

### Opción B: Dump en formato SQL (`.sql`)

Si el dump es un `.sql` (por ejemplo de `pg_dump` sin formato custom):

1. Copia el `.sql` a una carpeta del host, por ejemplo `./backups/dump.sql`.
2. En el host:
   ```bash
   docker compose exec -T postgres psql -U kpis -d kpis < backups/dump.sql
   ```
   (Ajusta usuario y base si usas otros en `.env`.)

### Opción C: Subir el dump al contenedor y restaurar

Si pgAdmin no ve el archivo (por estar solo en tu PC), sube el dump al contenedor de Postgres y restaura desde ahí:

```bash
# Copiar el dump al contenedor
docker cp ruta/a/mi_dump.sql kpis-postgres:/tmp/mi_dump.sql

# Restaurar
docker compose exec postgres psql -U kpis -d kpis -f /tmp/mi_dump.sql

# (Opcional) Borrar el archivo dentro del contenedor
docker compose exec postgres rm /tmp/mi_dump.sql
```

Ajusta `kpis` si tu base tiene otro nombre.

## 5. Crear base de datos vacía antes del restore (opcional)

Si el dump incluye `CREATE DATABASE` y quieres una base nueva:

1. Clic derecho en **Databases** → **Create** → **Database**.
2. **Database:** nombre (ej. `kpis_importada`).
3. **Owner:** el usuario de Postgres (ej. `kpis`).
4. Luego usa **Restore** sobre esa base o el comando `psql ... -d kpis_importada -f ...`.

## Resumen de URLs (con Docker)

| Servicio   | URL / Uso                    |
|-----------|-------------------------------|
| API KPIs  | http://localhost:9000         |
| pgAdmin  | http://localhost:5050         |
| Postgres (interno) | host `postgres`, puerto `5432` |
