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

BASE_PATH = Path(__file__).parent.parent.parent.parent.resolve() # Points at the lotr/ directory


def draw_origin_axes(scene, length=10000, width=2):
    # X-Axis (Red)
    # Line from (-length, 0) to (+length, 0)
    x_axis = QtWidgets.QGraphicsLineItem(-length, 0, length, 0)
    pen_x = QtGui.QPen(QtCore.Qt.red)
    pen_x.setWidth(width)
    x_axis.setPen(pen_x)
    
    # Y-Axis (Green)
    # Line from (0, -length) to (0, +length)
    y_axis = QtWidgets.QGraphicsLineItem(0, -length, 0, length)
    pen_y = QtGui.QPen(QtCore.Qt.green)
    pen_y.setWidth(width)
    y_axis.setPen(pen_y)

    # 4. Configure items (Z-order and Selection)
    # ZValue: -1 ensures it draws behind nodes (usually Z=0+) but in front of the grid
    x_axis.setZValue(-1)
    y_axis.setZValue(-1)
    
    # Disable selection so you don't accidentally grab the axes
    x_axis.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
    y_axis.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)

    # Add to scene
    scene.addItem(x_axis)
    scene.addItem(y_axis)


def main():
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication([])

    # create graph controller.
    graph = create_node_graph()

    focus_node_tree = FocusNodeTree(graph, BASE_PATH / "common/national_focus/vales.txt")
    graph.focus_tree = focus_node_tree

    context_menu = graph.get_context_menu('graph')
    main_window = create_main_window()
    main_window.setCentralWidget(graph.widget)
    #dock_widget = create_properties_panel(main_window, graph, focus_node_tree)

    setup_node_count_display(main_window, graph)

    properties_panel = PropertiesPanel(main_window, graph)
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, properties_panel)
    properties_panel.setFloating(True)
    properties_panel.resize(450, 800) 
    properties_panel.move(100, 100)


    graph_widget = graph.widget
    graph_widget.show()

    # 2. Access the internal QGraphicsScene
    # NodeGraphQt wraps the view inside a widget, so we find the view first.
    viewer = graph_widget.findChild(QtWidgets.QGraphicsView)
    scene = viewer.scene()

    draw_origin_axes(scene) # Use this to draw axes to position the entire tree nicely. Disable afterwards because it causes error-spam


    # Present
    main_window.show()
    graph.clear_selection()
    graph.fit_to_selection()
    graph.set_layout_direction(LayoutDirectionEnum.VERTICAL.value)
    graph.set_pipe_style(PipeLayoutEnum.ANGLE.value)


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
