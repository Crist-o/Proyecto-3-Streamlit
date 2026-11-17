"""
Título: Proyecto 3 Streamlit
Nombre: Cristopher Altamirano Hernandez
Fecha: 16/11/2026
Materia: Programación 3
Maestro: Diego Alberto Ayala Vazquez

Descripción: Interfaz web para calcular rutas de transporte,
Gestiona rutas, conexiones y visualización del grafo.
"""

from pathlib import Path
import math

import pandas as pd
import streamlit as st

from grafo import Graph
from nuevas_conexiones import append_connection, read_connections


CSV_PATH = Path(__file__).resolve().with_name("nodos.csv")
TRANSPORTS = (
    "CAMINANDO",
    "BICI",
    "AUTO",
    "CAMION",
    "TREN",
    "OTRO",
)


def _initialize_session():
    """Carga el CSV una sola vez y conserva el grafo durante la sesión."""
    if "grafo" in st.session_state:
        return

    graph = Graph()
    connections = []
    load_message = None
    load_level = None
    can_register = True

    try:
        connections = read_connections(CSV_PATH)
        for connection in connections:
            graph.add_edge(
                connection["Origen"],
                connection["Destino"],
                connection["Peso"],
            )
    except FileNotFoundError:
        load_message = (
            "No se encontró nodos.csv. Puedes crear el archivo al "
            "registrar una conexión."
        )
        load_level = "warning"
    except PermissionError:
        load_message = "No hay permiso para leer nodos.csv."
        load_level = "error"
        can_register = False
    except ValueError as error:
        load_message = f"No se pudo validar nodos.csv: {error}"
        load_level = "error"
        can_register = False
    except OSError as error:
        load_message = f"No se pudo leer nodos.csv: {error}"
        load_level = "error"
        can_register = False

    st.session_state["grafo"] = graph
    st.session_state["conexiones"] = connections
    st.session_state["mensaje_carga"] = load_message
    st.session_state["nivel_carga"] = load_level
    st.session_state["puede_registrar"] = can_register


def _show_load_message():
    message = st.session_state["mensaje_carga"]
    if not message:
        return
    if st.session_state["nivel_carga"] == "warning":
        st.warning(message)
    else:
        st.error(message)


def _render_route_calculator():
    st.subheader("Calcular la ruta más corta")
    with st.form("route_form"):
        origin = st.text_input("Nodo de origen")
        destination = st.text_input("Nodo de destino")
        calculate = st.form_submit_button("Calcular ruta")

    if not calculate:
        return
    if not origin.strip() or not destination.strip():
        st.warning("Ingresa el nodo de origen y el nodo de destino.")
        return

    graph = st.session_state["grafo"]
    try:
        cost, route = graph.dijkstra(
            origin.strip().upper(),
            destination.strip().upper(),
        )
    except KeyError as error:
        st.warning(str(error).strip("'"))
        return

    if math.isinf(cost):
        st.warning("No existe una ruta posible entre esos nodos.")
        return

    st.success(f"Costo total mínimo: {cost:g}")
    st.write("Recorrido:", " → ".join(route))


def _render_connection_form():
    st.subheader("Registrar una conexión")
    if not st.session_state["puede_registrar"]:
        st.info(
            "Corrige el archivo nodos.csv antes de registrar conexiones."
        )

    with st.form("connection_form"):
        origin = st.text_input("Origen de la conexión")
        destination = st.text_input("Destino de la conexión")
        weight = st.number_input(
            "Peso o distancia",
            min_value=0.0,
            value=1.0,
            step=1.0,
        )
        transport = st.selectbox("Medio de transporte", TRANSPORTS)
        save = st.form_submit_button(
            "Guardar conexión",
            disabled=not st.session_state["puede_registrar"],
        )

    if not save:
        return

    try:
        connection = append_connection(
            CSV_PATH,
            origin,
            destination,
            weight,
            transport,
        )
    except ValueError as error:
        st.warning(str(error))
        return
    except PermissionError:
        st.error("No hay permiso para escribir en nodos.csv.")
        return
    except OSError as error:
        st.error(f"No se pudo guardar la conexión: {error}")
        return

    st.session_state["grafo"].add_edge(
        connection["Origen"],
        connection["Destino"],
        connection["Peso"],
    )
    st.session_state["conexiones"].append(connection)
    st.session_state["mensaje_carga"] = None
    st.session_state["nivel_carga"] = None
    st.session_state["puede_registrar"] = True
    st.success("Conexión guardada en nodos.csv y añadida al grafo.")


def _render_connection_table():
    st.subheader("Conexiones registradas")
    connections = st.session_state["conexiones"]
    rows = [
        {
            "Origen": connection["Origen"],
            "Destino": connection["Destino"],
            "Peso": connection["Peso"],
            "Medio de transporte": connection["Medio_Transporte"],
        }
        for connection in connections
    ]
    columns = (
        "Origen",
        "Destino",
        "Peso",
        "Medio de transporte",
    )
    st.dataframe(
        pd.DataFrame(rows, columns=columns),
        width="stretch",
        hide_index=True,
    )


def run_app():
    """Construye la interfaz Streamlit de la aplicación."""
    st.set_page_config(
        page_title="Rutas de transporte",
        page_icon="🗺️",
        layout="wide",
    )
    _initialize_session()

    st.title("Planificador de rutas")
    st.caption(
        "Red de transporte con persistencia CSV y rutas calculadas "
        "mediante Dijkstra."
    )
    _show_load_message()

    route_tab, connection_tab, network_tab = st.tabs(
        ("Calcular ruta", "Registrar conexión", "Ver red")
    )
    with route_tab:
        _render_route_calculator()
    with connection_tab:
        _render_connection_form()
    with network_tab:
        _render_connection_table()


run_app()
