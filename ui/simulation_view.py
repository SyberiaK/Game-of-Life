from PyQt5.QtWidgets import QGraphicsView


# Данный класс нужен только для отслеживания ивентов мыши на поле и их передачи в основной класс
class SimulationView(QGraphicsView):
    def mousePressEvent(self, event):
        self.parent().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.parent().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.parent().mouseMoveEvent(event)