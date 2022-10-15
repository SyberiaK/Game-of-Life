import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from cell_painter import CellPainter
from field import Field
from simulation_view import SimulationView


class GameOfLife(QMainWindow):
    FACTOR = 1.5
    SIMULATION_WINDOW_SIZE = 500, 500

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Жизнь')
        self.setFixedSize(520, 550)

        # Поле
        self.field = Field(50, 50)
        self.field_size_x, self.field_size_y = self.field.get_size()

        # Переменные для рисования и работы симуляции
        self.simulation_active = False
        self.drag_start = None
        self.dragging_to_cell_state = None

        # Виджеты
        self._view = ...
        self._painter = ...
        self.loop_simulation_btn = ...
        self.step_simulation_btn = ...

        self.setup_ui()

        w, h = self._painter.width(), self._painter.height()
        self.field_cell_size = min(w // self.field_size_x, h // self.field_size_y)

        self.simulation_timer = QtCore.QTimer(self)
        self.simulation_timer.setInterval(100)
        self.simulation_timer.timeout.connect(self.update_field)

    def setup_ui(self):
        main_widget = QWidget(self)
        main_widget.setLayout(QVBoxLayout())

        scene = QtWidgets.QGraphicsScene(self)
        self._view = SimulationView(scene)

        self._painter = CellPainter(self)
        self._painter.setFixedSize(*self.SIMULATION_WINDOW_SIZE)

        scene.addWidget(self._painter)
        self._view.setFixedSize(self._view.sizeHint())
        self._painter.setMouseTracking(True)

        btns_holder = QWidget(self)
        btns_holder.setLayout(QHBoxLayout())
        btns_holder.layout().setContentsMargins(9, 9, 9, 0)

        self.loop_simulation_btn = QPushButton('Play / Pause')
        self.loop_simulation_btn.clicked.connect(self.loop_simulation)

        self.step_simulation_btn = QPushButton('Step')
        self.step_simulation_btn.clicked.connect(self.update_field)

        btns_holder.layout().addWidget(self.loop_simulation_btn)
        btns_holder.layout().addWidget(self.step_simulation_btn)

        main_widget.layout().addWidget(self._view)
        main_widget.layout().addWidget(btns_holder)

        self.setCentralWidget(main_widget)

        zoom_in_bind = QtWidgets.QShortcut(QtCore.Qt.Key_Equal, self._view)
        zoom_in_bind.activated.connect(self.simulation_zoom_in)
        zoom_out_bind = QtWidgets.QShortcut(QtCore.Qt.Key_Minus, self._view)
        zoom_out_bind.activated.connect(self.simulation_zoom_out)

    def mousePressEvent(self, event):
        # cursor_point = self.mapFromGlobal(self.cursor().pos())
        # cursor_pos = cursor_point.x(), cursor_point.y()

        if event.buttons() & QtCore.Qt.LeftButton and\
                self._view.underMouse() and not self.simulation_active:
            self.drag_start = event.pos()

            cell = self.get_hovered_cell()
            if cell.get_state() == Field.Cell.DEAD:
                self.dragging_to_cell_state = Field.Cell.ALIVE
            else:
                self.dragging_to_cell_state = Field.Cell.DEAD
            cell.set_state(self.dragging_to_cell_state)
            self._painter.update()

    def mouseReleaseEvent(self, event):
        if self._view.underMouse() and not self.simulation_active:
            self.drag_start = None
            self.dragging_to_cell_state = None

    def mouseMoveEvent(self, event):
        if (self.drag_start is not None and
                event.buttons() & QtCore.Qt.LeftButton and
                self._view.underMouse() and
                event.pos() != self.drag_start):
            cell = self.get_hovered_cell()
            if cell.get_state() != self.dragging_to_cell_state:
                cell.set_state(self.dragging_to_cell_state)
            self._painter.update()

    def loop_simulation(self):
        if self.simulation_active:
            self.simulation_timer.stop()
        else:
            self.simulation_timer.start()

        self.simulation_active = not self.simulation_active

    def get_hovered_cell(self):
        cursor_point = self._painter.mapFromGlobal(self.cursor().pos())

        cell_pos_x, cell_pos_y = int(cursor_point.x() / self.field_cell_size), \
                                 int(cursor_point.y() / self.field_cell_size)

        return self.field.matrix[cell_pos_y][cell_pos_x]

    @QtCore.pyqtSlot()
    def update_field(self):
        if self.sender() is self.step_simulation_btn:
            if self.simulation_active:
                return
        self.field.step()
        self._painter.update()

    @QtCore.pyqtSlot()
    def simulation_zoom_in(self):
        scale_tr = QtGui.QTransform().scale(self.FACTOR, self.FACTOR)

        tr = self._view.transform() * scale_tr
        if tr.m11() < 5:
            self._view.setTransform(tr)
            w, h = self._view.width(), self._view.height()
            self.field_cell_size = min(w * tr.m11() // self.field_size_x, h * tr.m11() // self.field_size_y)

    @QtCore.pyqtSlot()
    def simulation_zoom_out(self):
        scale_tr = QtGui.QTransform().scale(self.FACTOR, self.FACTOR)

        scale_inverted, invertible = scale_tr.inverted()

        if invertible:
            tr = self._view.transform() * scale_inverted
            if tr.m11() >= 1:
                self._view.setTransform(tr)
                w, h = self._view.width(), self._view.height()
                self.field_cell_size = min(w * tr.m11() // self.field_size_x, h * tr.m11() // self.field_size_y)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    ex = GameOfLife()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
