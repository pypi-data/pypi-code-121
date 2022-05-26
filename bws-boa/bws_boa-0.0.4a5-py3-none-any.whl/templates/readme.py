template = """
# Micro - Servicio

Micro-servicio auto generado.

# Instalación
```bash
apt install python-venv
pip install -g bws-boa

boa init .
boa install

cat .env > .env.dev

# configura la db dentro de .env
boa db init

# para preparar la migración
boa db migrate -m "Initial database"

# ejecutar la migración
flask db upgrade

```

# Desarrollo

```bash
boa webdev
```
"""
