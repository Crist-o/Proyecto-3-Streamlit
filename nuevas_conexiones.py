"""
Título: Nuevas conexiones
Nombre: Cristopher Altamirano Hernandez
Fecha: 16/11/2026
Materia: Programación 3
Maestro: Diego Alberto Ayala Vazquez

Descripción: Valida o guarda conexiones nuevas en el archivo CSV.
"""

import csv
import math
from pathlib import Path


CSV_FIELDS = ("Origen", "Destino", "Peso", "Medio_Transporte")


def _build_connection(origin, destination, weight, transport):
    """Valida y normaliza una conexión antes de usarla o guardarla."""
    origin = origin.strip().upper()
    destination = destination.strip().upper()
    transport = transport.strip().upper() or "SIN ESPECIFICAR"

    if not origin or not destination:
        raise ValueError("El origen y el destino son obligatorios.")
    if origin == destination:
        raise ValueError("El origen y el destino deben ser distintos.")

    try:
        parsed_weight = float(weight)
    except (TypeError, ValueError) as error:
        raise ValueError("El peso debe ser numérico.") from error

    if not math.isfinite(parsed_weight) or parsed_weight < 0:
        raise ValueError("El peso debe ser un número finito no negativo.")

    return {
        "Origen": origin,
        "Destino": destination,
        "Peso": parsed_weight,
        "Medio_Transporte": transport,
    }


def read_connections(csv_path):
    """Lee y valida todas las conexiones de un archivo CSV."""
    path = Path(csv_path)
    with path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None or not set(CSV_FIELDS).issubset(
            reader.fieldnames
        ):
            raise ValueError(
                "El CSV debe incluir Origen, Destino, Peso y "
                "Medio_Transporte."
            )

        connections = []
        for row_number, row in enumerate(reader, start=2):
            if not row or all(value is None for value in row.values()):
                continue
            try:
                connection = _build_connection(
                    row.get("Origen") or "",
                    row.get("Destino") or "",
                    row.get("Peso") or "",
                    row.get("Medio_Transporte") or "",
                )
            except ValueError as error:
                raise ValueError(
                    f"Fila {row_number}: {error}"
                ) from error
            connections.append(connection)
    return connections


def append_connection(
    csv_path, origin, destination, weight, transport
):
    """Añade una conexión y escribe encabezados si el archivo está vacío."""
    connection = _build_connection(
        origin, destination, weight, transport
    )
    path = Path(csv_path)
    needs_header = not path.exists() or path.stat().st_size == 0

    with path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        if needs_header:
            writer.writeheader()
        writer.writerow(connection)
    return connection
