from PyQt5.QtCore import QRect, QLineF
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen
from PyQt5.QtWidgets import QWidget

from field import Field
Cell = Field.Cell


class CellPainter(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

    def paintEvent(self, event):
        p = self.parent
        matrix = p.field.matrix
        sz = p.field_cell_size

        qp = QPainter(self)

        qp.setBrush(QBrush(QColor(0, 0, 0, 255)))
        qp.drawRect(self.rect())
        w, h = self.width(), self.height()

        lines = []
        for x in range(1, p.field_size_x):
            lines.append(QLineF(sz * x, 0, sz * x, h))
        for y in range(1, p.field_size_y):
            lines.append(QLineF(0, sz * y, w, sz * y))
        qp.setPen(QPen(QColor(50, 50, 50, 255), 1))
        qp.drawLines(lines)

        qp.setBrush(QBrush(QColor(255, 255, 255, 255)))
        for y, row in enumerate(matrix):
            if all(c.get_state == Cell.DEAD for c in row):
                continue
            for x, cell in enumerate(row):
                if cell.get_state() == Cell.ALIVE:
                    qp.drawRect(QRect(sz * x, sz * y, sz, sz))
