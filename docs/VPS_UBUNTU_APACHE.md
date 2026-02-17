# Paso a paso: VPS Ubuntu 22.04 + Apache + Proyecto KPIs (Docker)

Guía para montar en un VPS con **Ubuntu 22.04** que ya tiene **Apache** instalado. Se instala **PostgreSQL** y la **API KPIs** usando **Docker** (un contenedor para la BD y otro para la app). Apache hace de proxy inverso hacia la app.

---

## Resumen

| Componente   | Dónde corre        | Puerto (interno) |
|-------------|--------------------|-------------------|
| Apache      | VPS (sistema)      | 80 / 443          |
| API KPIs    | Contenedor Docker  | 9000              |
| PostgreSQL  | Contenedor Docker  | 5432 (solo local) |

MySQL puede seguir instalado; PostgreSQL corre solo dentro de Docker.

---

## 1. Conectarte al VPS y usuario

```bash
ssh tu_usuario@IP_DEL_VPS
sudo -i
# o trabajar con tu usuario y usar sudo cuando haga falta
```

---

## 2. Instalar Docker y Docker Compose

```bash
# Actualizar e instalar requisitos
sudo apt update
sudo apt install -y ca-certificates curl gnupg

# Añadir clave y repo de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine y Compose
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Comprobar
sudo docker --version
sudo docker compose version
```

(Opcional) Para no usar `sudo` con Docker:

```bash
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar para que aplique
```

---

## 3. Clonar o subir el proyecto

**Opción A – Git**

```bash
sudo mkdir -p /var/www
cd /var/www
sudo git clone https://github.com/TU_ORG/kpis.git
cd kpis
```

**Opción B – Subir con SCP desde tu PC**

```bash
# Desde tu PC (Windows PowerShell o CMD)
scp -r C:\Users\Equipo\Documents\work\kpis tu_usuario@IP_DEL_VPS:/tmp/kpis
```

En el VPS:

```bash
sudo mkdir -p /var/www
sudo mv /tmp/kpis /var/www/kpis
cd /var/www/kpis
```

---

## 4. Configurar variables de entorno para Docker

```bash
cd /var/www/kpis
sudo cp .env.example .env
sudo nano .env
```

Rellena al menos:

- `POSTGRES_PASSWORD`: contraseña segura para PostgreSQL.
- `HUBSPOT_API_KEY`: token de la Private App de HubSpot.
- `ORIGIN_HOSTS`: dominio(s) desde los que se llamará a la API (ej. `https://api.tudominio.com,https://tudominio.com`).

Guarda (Ctrl+O, Enter, Ctrl+X en nano).

---

## 5. Levantar contenedores (app + PostgreSQL)

```bash
cd /var/www/kpis
sudo docker compose build --no-cache
sudo docker compose up -d
```

Comprobar que estén en marcha:

```bash
sudo docker compose ps
```

Deberías ver `kpis-postgres` y `kpis-app` en estado “Up”. Probar la API en el propio servidor:

```bash
curl -s http://127.0.0.1:9000/health
# Debe devolver: {"status":"ok"}
```

---

## 6. Configurar Apache como proxy inverso

La API escucha en `127.0.0.1:9000`. Apache redirigirá (por ejemplo) `https://api.tudominio.com` a ese puerto.

Habilitar módulos:

```bash
sudo a2enmod proxy proxy_http headers ssl rewrite
sudo systemctl reload apache2
```

Crear un virtualhost para la API (cambia `api.tudominio.com` por tu dominio):

```bash
sudo nano /etc/apache2/sites-available/kpis-api.conf
```

Contenido (con SSL; si aún no tienes certificado, quita el bloque `<VirtualHost *:443>` y usa solo el de :80 temporalmente):

```apache
# Redirigir HTTP -> HTTPS (opcional)
<VirtualHost *:80>
    ServerName api.tudominio.com
    Redirect permanent / https://api.tudominio.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName api.tudominio.com

    SSLEngine on
    SSLCertificateFile      /etc/ssl/certs/tu_certificado.crt
    SSLCertificateKeyFile   /etc/ssl/private/tu_clave.key
    # Si usas Let's Encrypt (certbot):
    # SSLCertificateFile /etc/letsencrypt/live/api.tudominio.com/fullchain.pem
    # SSLCertificateKeyFile /etc/letsencrypt/live/api.tudominio.com/privkey.pem

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:9000/
    ProxyPassReverse / http://127.0.0.1:9000/

    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-For "%{REMOTE_ADDR}s"
</VirtualHost>
```

Solo HTTP (sin SSL) para pruebas:

```apache
<VirtualHost *:80>
    ServerName api.tudominio.com
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:9000/
    ProxyPassReverse / http://127.0.0.1:9000/
    RequestHeader set X-Forwarded-Proto "http"
</VirtualHost>
```

Activar sitio y recargar Apache:

```bash
sudo a2ensite kpis-api.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

Comprobar desde fuera:

```bash
curl -s https://api.tudominio.com/health
```

---

## 7. Certificado SSL con Let's Encrypt (recomendado)

```bash
sudo apt install -y certbot python3-certbot-apache
sudo certbot --apache -d api.tudominio.com
```

Sigue el asistente. Certbot puede ajustar el virtualhost por ti. Luego:

```bash
sudo systemctl reload apache2
```

---

## 8. Persistencia y reinicio

- Los datos de PostgreSQL se guardan en el volumen Docker `postgres_data`. No se pierden al hacer `docker compose down` (sí con `docker compose down -v`).
- Para que los contenedores arranquen al reiniciar el VPS:

```bash
# Ya está con "restart: unless-stopped" en docker-compose
sudo systemctl enable docker
```

---

## 9. Comandos útiles

| Acción              | Comando |
|---------------------|--------|
| Ver logs de la app  | `sudo docker compose logs -f app` |
| Ver logs de Postgres | `sudo docker compose logs -f postgres` |
| Parar todo          | `sudo docker compose down` |
| Arrancar de nuevo   | `sudo docker compose up -d` |
| Reconstruir app     | `sudo docker compose build --no-cache app && sudo docker compose up -d app` |
| Entrar al contenedor de la app | `sudo docker compose exec app sh` |

---

## 10. Resumen mínimo

1. Instalar Docker y Docker Compose en Ubuntu 22.04.
2. Clonar o copiar el proyecto en `/var/www/kpis`.
3. Copiar `.env.example` a `.env` y rellenar `POSTGRES_PASSWORD`, `HUBSPOT_API_KEY`, `ORIGIN_HOSTS`.
4. Ejecutar `docker compose up -d` en `/var/www/kpis`.
5. Configurar Apache como proxy inverso a `http://127.0.0.1:9000` y (opcional) SSL con certbot.

Con esto tendrás la API KPIs y PostgreSQL en Docker, y Apache sirviendo la API en el puerto 80/443. MySQL puede seguir instalado en el mismo VPS sin conflicto.
