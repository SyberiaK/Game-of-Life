from PyQt5.QtCore import QRect, QLineF
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtWidgets import QWidget

from field.field import Field
Cell = Field.Cell


# Рисует поле.
class CellPainter(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

    def paintEvent(self, event):
        p = self.parent
        alives = p.field.get_alives()
        w, h = self.width(), self.height()
        sz = min(w // p.field_size_x, h // p.field_size_y)

        qp = QPainter(self)

        qp.setBrush(QBrush(p.dead_cell_color))
        qp.drawRect(self.rect())
        w, h = self.width(), self.height()

        lines = []
        for x in range(1, p.field_size_x):
            lines.append(QLineF(sz * x, 0, sz * x, h))
        for y in range(1, p.field_size_y):
            lines.append(QLineF(0, sz * y, w, sz * y))
        qp.setPen(QPen(p.cell_border_color, 1))
        qp.drawLines(lines)

        qp.setBrush(QBrush(p.alive_cell_color))

        if alives:
            for x, y in alives:
                qp.drawRect(QRect(sz * x, sz * y, sz, sz))

