#!/usr/bin/python
# -*- coding: utf-8 -*-
import signal
from pathlib import Path

from focus_node_tree import FocusNodeTree

from core import *

from Qt import QtCore, QtWidgets

from properties_panel import *

from NodeGraphQt.constants import LayoutDirectionEnum
from NodeGraphQt.constants import PipeLayoutEnum

import networkx as nx

BASE_PATH = Path(__file__).parent.parent.parent.parent.resolve() # Points at the lotr/ directory


def apply_clustered_layout(graph, scale=200, component_padding=500):
    """
    Layouts connected clusters individually, then stacks them horizontally.
    Places isolated nodes in a grid to the far right.
    """
    nodes = graph.all_nodes()
    if not nodes:
        return

    # 1. Build the NetworkX Graph
    nx_graph = nx.Graph() # Undirected is usually better for component detection
    node_map = {node.id: node for node in nodes}
    
    for node in nodes:
        nx_graph.add_node(node.id)
        for port in node.output_ports():
            for connected_port in port.connected_ports():
                nx_graph.add_edge(node.id, connected_port.node().id)

    # 2. Identify Components (Clusters vs Isolated)
    # specific function to find groups of connected nodes
    components = list(nx.connected_components(nx_graph))
    
    clusters = [c for c in components if len(c) > 1]
    isolated = [c for c in components if len(c) == 1]

    # Sort clusters by size (largest first looks tidier)
    clusters.sort(key=len, reverse=True)

    graph.begin_undo("Auto Cluster Layout")
    
    # 3. Layout Connected Clusters
    current_x_offset = 0
    
    for comp_set in clusters:
        subgraph = nx_graph.subgraph(comp_set)
        
        # Layout ONLY this cluster
        # scale is smaller here to keep nodes tight within the cluster
        pos = nx.spring_layout(subgraph, k=0.5, seed=42) 
        
        # Calculate bounds to know how far to shift the next cluster
        min_x = min(p[0] for p in pos.values())
        max_x = max(p[0] for p in pos.values())
        cluster_width = (max_x - min_x) * scale
        
        # Apply positions
        for node_id, (x, y) in pos.items():
            node = node_map[node_id]
            # Shift by current global offset
            final_x = (x * scale) + current_x_offset
            final_y = (y * scale)
            node.set_pos(final_x, final_y)
            
        # Move the offset for the next cluster
        current_x_offset += cluster_width + component_padding

    # 4. Layout Isolated Nodes (Grid Pattern)
    # Place them to the right of the last cluster
    start_iso_x = current_x_offset + component_padding
    start_iso_y = -500 # Start slightly higher up
    
    grid_width = 4 # How many nodes per row
    cell_size = 250 # Pixel space between isolated nodes
    
    for i, comp_set in enumerate(isolated):
        node_id = list(comp_set)[0]
        node = node_map[node_id]
        
        # Grid math
        col = i % grid_width
        row = i // grid_width
        
        x = start_iso_x + (col * cell_size)
        y = start_iso_y + (row * cell_size)
        
        node.set_pos(x, y)

    graph.end_undo()


def main():
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication([])

    # create graph controller.
    graph = create_node_graph()

    focus_node_tree = FocusNodeTree(graph,
        BASE_PATH / r'events\MirkwoodStory.txt',
        #BASE_PATH / r'localisation\english\0_lotr_core\lotr_generic_events_l_english.yml'
        BASE_PATH / r'localisation\english\mirkwood\mirkwood_story_l_english.yml'
        #BASE_PATH / r'events\MorMenace.txt',
        #BASE_PATH / r'localisation\english\mordor\morm_events_l_english.yml'
        #BASE_PATH / r'events\rhunexpandedevents.txt',
        #BASE_PATH / r'localisation\english\rhun\rhun_country_events_l_english.yml'
    )
    graph.focus_tree = focus_node_tree

    context_menu = graph.get_context_menu('graph')
    main_window = create_main_window()
    main_window.setCentralWidget(graph.widget)
    #dock_widget = create_properties_panel(main_window, graph, focus_node_tree)

    properties_panel = PropertiesPanel(main_window, graph)
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, properties_panel)
    properties_panel.setFloating(True)
    properties_panel.resize(450, 800) 
    properties_panel.move(100, 100)


    # Present
    main_window.show()
    graph.clear_selection()
    graph.auto_layout_nodes()
    #apply_clustered_layout(graph)
    graph.fit_to_selection()
    #graph.set_layout_direction(LayoutDirectionEnum.VERTICAL.value)
    #graph.set_pipe_style(PipeLayoutEnum.ANGLE.value)

    focus_node_tree.load_positions() # Load positions after nodes are created and initialized


    # This code-block enables showing a properties widget on double clicking a node
    # create a node properties bin widget.
    #properties_bin = PropertiesBinWidget(node_graph=graph, parent=main_window)
    #properties_bin.setWindowFlags(QtCore.Qt.Tool)
    ## example show the node properties bin widget when a node is double-clicked.
    #def display_properties_bin(node):
    #    if not properties_bin.isVisible():
    #        properties_bin.show()
    ## wire function to "node_double_clicked" signal.
    #graph.node_double_clicked.connect(display_properties_bin)



    # Define your "update" function
    def update():
        if len(graph.selected_nodes()) > 0:
            print(graph.selected_nodes()[0].pos())

    # Use a QTimer to call the update function repeatedly
    timer = QtCore.QTimer()
    #timer.timeout.connect(update) # un-comment this to enable update function
    timer.start(16)  # roughly 60 FPS (1000 ms / 60 ≈ 16 ms)



    app.exec()


if __name__ == '__main__':
    main()
