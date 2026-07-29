#!/usr/bin/env python3
# scripts/seed_incidents.py
#
# Script de carga de datos historicos desde CSV a TinyDB.
# Lee el archivo incidents.csv, valida usando la logica compartida,
# aplica transformaciones CSV -> modelo e inserta en incidentes_db.json.
#
# IDEMPOTENTE: no duplica registros (usa incident_id como control).
# Los registros invalidos se reportan en stderr al final.
#
# Uso:
#   python3 scripts/seed_incidents.py [ruta_al_csv]

import sys
import csv
import os
from tinydb import TinyDB, Query

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages"))

from shared.validation import validate_and_transform_row


def load_csv(filepath: str) -> list[dict[str, str]]:
    """Lee el CSV y devuelve lista de diccionarios."""
    if not os.path.exists(filepath):
        print(f"Error: archivo no encontrado: {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"Error: archivo no encontrado: {filepath}", file=sys.stderr)
        sys.exit(1)
    except csv.Error as exc:
        print(f"Error: formato CSV invalido: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error inesperado al leer {filepath}: {exc}", file=sys.stderr)
        sys.exit(1)


def seed_database(csv_path: str, db_path: str = "incidentes_db.json"):
    """Procesa el CSV e inserta en TinyDB. Idempotente: controla duplicados por incident_id."""
    try:
        rows = load_csv(csv_path)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"Error al cargar CSV: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        db = TinyDB(db_path)
        table = db.table("incidents")
    except Exception as exc:
        print(f"Error al abrir base de datos {db_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    Incident = Query()

    inserted = 0
    duplicated = 0
    errors = []

    for row in rows:
        incident_id_raw = row.get("incident_id", "").strip()
        if not incident_id_raw.isdigit():
            errors.append(f"Fila sin incident_id valido: {dict(row)}")
            continue

        incident_id = int(incident_id_raw)

        try:
            if table.contains(Incident.incident_id == incident_id):
                duplicated += 1
                continue
        except Exception as exc:
            print(f"Error al verificar duplicado #{incident_id}: {exc}", file=sys.stderr)
            errors.append(f"Error BD #{incident_id}")
            continue

        try:
            valid, result = validate_and_transform_row(row)
        except Exception as exc:
            print(f"Error al validar fila #{incident_id}: {exc}", file=sys.stderr)
            errors.append(f"Error validacion #{incident_id}")
            continue

        if not valid:
            errors.append(f"Incidente #{incident_id}: {result}")
            continue

        try:
            table.insert(result)
            inserted += 1
        except Exception as exc:
            print(f"Error al insertar incidente #{incident_id}: {exc}", file=sys.stderr)
            errors.append(f"Error insercion #{incident_id}")

    print(f"Insertados: {inserted}, Invalidos: {len(errors)}, Duplicados: {duplicated}")
    if errors:
        print("\n--- Registros invalidos ---", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)

    return inserted, len(errors), duplicated, errors


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "incidents.csv"
    )
    try:
        result = seed_database(csv_path)
        if result[1] > 0:
            sys.exit(1)
    except Exception as exc:
        print(f"Error critico: {exc}", file=sys.stderr)
        sys.exit(1)
