# Ejecuta la API con uv y FastAPI en el puerto 9000.
# En Windows evita UnicodeEncodeError al imprimir emojis en la consola.
$env:PYTHONIOENCODING = "utf-8"
uv run --env-file .env fastapi run src/main.py --port 9000
