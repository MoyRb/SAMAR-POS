# SAMAR-POS

Sistema de punto de venta y operación para pizzería con flujos de salón y reparto.

## Configuración
1. Crea un entorno virtual e instala dependencias:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Define tu configuración en variables de entorno o en un archivo `.env` en la raíz:
   ```ini
   DATABASE_URL=mysql+mysqlconnector://user:pass@localhost/samar_pos?charset=utf8mb4
   DB_POOL_SIZE=5
   DB_MAX_OVERFLOW=10
   DB_ECHO=false
   LOG_LEVEL=INFO
   APP_ENV=development
   ```
   De no existir, se usará una base SQLite local (`samar_pos.db`).
3. La aplicación crea automáticamente las tablas y un usuario administrador si no existen.
   - Usuario: `admin` (editable con `ADMIN_DEFAULT_USERNAME`)
   - Contraseña: `admin` (editable con `ADMIN_DEFAULT_PASSWORD`)
   - Si quieres forzar un reinicio de contraseña (útil cuando olvidaste la clave en tu BD local), define `ADMIN_FORCE_RESET=true` al iniciar la app.

## Uso rápido
- Ejecuta la aplicación de escritorio:
  ```bash
  python main.py
  ```
- El módulo `services/` contiene helpers para autenticación, pedidos/KDS y corte de caja.

## Pruebas y CI
- Ejecuta la suite de pruebas:
  ```bash
  pytest
  ```
- Un flujo de GitHub Actions (`.github/workflows/ci.yml`) instala dependencias y corre `pytest` sobre SQLite.
