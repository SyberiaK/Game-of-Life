from PyQt5.QtWidgets import QGraphicsView


class SimulationView(QGraphicsView):
    def mousePressEvent(self, event):
        self.parent().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.parent().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.parent().mouseMoveEvent(event)