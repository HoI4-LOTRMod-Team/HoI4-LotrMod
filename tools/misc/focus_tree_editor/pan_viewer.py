#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Node viewer that pans with a plain left-click drag on the background.

The stock NodeGraphQt viewer only pans with the middle mouse button (or
ALT + left click), which is awkward on a laptop trackpad. Dragging the
background with the left mouse button now pans the view instead of drawing
the selection marquee. The marquee is still available with SHIFT + drag,
and everything else (node dragging, pipes, ALT/MMB panning) is untouched.
"""

from Qt import QtCore

from NodeGraphQt.widgets.viewer import NodeViewer
from NodeGraphQt.qgraphics.node_abstract import AbstractNodeItem
from NodeGraphQt.qgraphics.pipe import PipeItem
from NodeGraphQt.qgraphics.port import PortItem

# how far the mouse may travel before a press counts as a drag and not a click.
CLICK_THRESHOLD = 3


class PanNodeViewer(NodeViewer):

    def __init__(self, parent=None, undo_stack=None):
        super(PanNodeViewer, self).__init__(parent, undo_stack)
        self._lmb_panning = False

    def _clicked_on_graph_item(self, event):
        """
        Whether the click landed on something interactive (node, port or pipe)
        rather than on the empty background.

        Args:
            event (QtGui.QMouseEvent): mouse event.

        Returns:
            bool: True if a graph item is under/near the cursor.
        """
        map_pos = self.mapToScene(event.pos())
        items = self._items_near(map_pos, None, 20, 20)
        return any(
            isinstance(i, (AbstractNodeItem, PipeItem, PortItem))
            for i in items
        )

    # --- reimplemented events ---

    def mousePressEvent(self, event):
        pan_mode = all([
            event.button() == QtCore.Qt.LeftButton,
            event.modifiers() == QtCore.Qt.NoModifier,
            not self._LIVE_PIPE.isVisible(),
            not self._clicked_on_graph_item(event),
        ])
        if pan_mode:
            self._lmb_panning = True
            self.LMB_state = True
            self._origin_pos = event.pos()
            self._previous_pos = event.pos()
            (self._prev_selection_nodes,
             self._prev_selection_pipes) = self.selected_items()

            # close tab search
            if self._search_widget.isVisible():
                self.tab_search_toggle()

            self.setCursor(QtCore.Qt.ClosedHandCursor)
            return

        super(PanNodeViewer, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._lmb_panning:
            previous_pos = self.mapToScene(self._previous_pos)
            current_pos = self.mapToScene(event.pos())
            delta = previous_pos - current_pos
            self._set_viewer_pan(delta.x(), delta.y())
            self._previous_pos = event.pos()
            return

        super(PanNodeViewer, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._lmb_panning and event.button() == QtCore.Qt.LeftButton:
            self._lmb_panning = False
            self.LMB_state = False
            self.unsetCursor()
            self._previous_pos = event.pos()

            # a click without any drag still clears the selection, the same way
            # clicking the background normally would.
            travelled = (event.pos() - self._origin_pos).manhattanLength()
            if travelled <= CLICK_THRESHOLD:
                prev_ids = [n.id for n in self._prev_selection_nodes]
                self.scene().clearSelection()
                if prev_ids:
                    self.node_selection_changed.emit([], prev_ids)
            return

        super(PanNodeViewer, self).mouseReleaseEvent(event)
