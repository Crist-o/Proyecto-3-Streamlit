"""
Título: Grafo para rutas de transporte
Nombre: Cristopher Altamirano Hernandez
Fecha: 16/11/2026
Materia: Programación 3
Maestro: Diego Alberto Ayala Vazquez

Descripción: Modela conexiones y calcula rutas mínimas con Dijkstra.
"""

import heapq
import math


class Graph:
    """Representa un grafo ponderado y calcula rutas mínimas."""

    def __init__(self, directed=False):
        self.directed = directed
        self.adj_list = {}

    def add_node(self, node):
        """Añade un nodo al grafo si aún no existe."""
        if not isinstance(node, str) or not node.strip():
            raise ValueError("El nombre del nodo no puede estar vacío.")
        self.adj_list.setdefault(node, [])

    def add_edge(self, origin, destination, weight):
        """Añade una conexión con peso válido entre dos nodos."""
        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or not math.isfinite(weight)
            or weight < 0
        ):
            raise ValueError("El peso debe ser un número finito no negativo.")

        self.add_node(origin)
        self.add_node(destination)
        self.adj_list[origin].append((destination, float(weight)))
        if not self.directed:
            self.adj_list[destination].append((origin, float(weight)))

    def dijkstra(self, start_node, target_node):
        """Devuelve el costo mínimo y la ruta, o infinito si no hay ruta."""
        if start_node not in self.adj_list:
            raise KeyError(f"No existe el nodo de origen: {start_node}.")
        if target_node not in self.adj_list:
            raise KeyError(f"No existe el nodo de destino: {target_node}.")

        distances = {node: math.inf for node in self.adj_list}
        previous_nodes = {node: None for node in self.adj_list}
        distances[start_node] = 0.0
        pending = [(0.0, start_node)]

        while pending:
            current_distance, current_node = heapq.heappop(pending)
            if current_distance > distances[current_node]:
                continue
            if current_node == target_node:
                break

            for neighbor, weight in self.adj_list[current_node]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(pending, (distance, neighbor))

        if math.isinf(distances[target_node]):
            return math.inf, []

        path = []
        current_node = target_node
        while current_node is not None:
            path.append(current_node)
            current_node = previous_nodes[current_node]
        path.reverse()
        return distances[target_node], path
