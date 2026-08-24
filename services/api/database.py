"""
database.py — Inicialización de TinyDB

Ahora con 3 tablas:
- suppliers_table (YA EXISTE): datos de proveedores TrackFlow
- users_table (NUEVO): credenciales de usuario (email, password hasheado)
- profiles_table (NUEVO): datos de perfil (name, phone, address)
"""

from tinydb import TinyDB, Query

import os

db_dir = os.path.join(os.path.dirname(__file__), "tinydb")
os.makedirs(db_dir, exist_ok=True)
db = TinyDB(os.path.join(db_dir, "db.json"))

suppliers_table = db.table("suppliers")
users_table = db.table("users")
profiles_table = db.table("profiles")

# Queries reutilizables
Supplier = Query()
User = Query()
Profile = Query()
