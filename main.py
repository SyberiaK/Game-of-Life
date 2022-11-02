import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow

from field import Field
from ui.main_ui import UIForm


class GameOfLife(QMainWindow, UIForm):
    FACTOR = 1.5
    SIMULATION_WINDOW_SIZE = 600, 600

    def __init__(self):
        super().__init__()

        # Поле
        self.field = ...
        self.field_size_x, self.field_size_y = ..., ...

        # Переменные для рисования и работы симуляции
        self.simulation_active = ...
        self.drag_start = None
        self.dragging_to_cell_state = None

        # Виджеты
        self._view = ...
        self._painter = ...
        self.loop_simulation_btn = ...
        self.step_simulation_btn = ...
        self.reset_simulation_btn = ...

        self.alive_cell_color = ...
        self.dead_cell_color = ...
        self.cell_border_color = ...

        self.setup_simulation()
        self.setup_ui(self)
        self.setup_ui_logic()

        self.alive_cell_color = self.alive_cell_color_setting.value()
        self.dead_cell_color = self.dead_cell_color_setting.value()
        self.cell_border_color = self.cell_border_color_setting.value()

        w, h = self._painter.width(), self._painter.height()
        self.field_cell_size = min(w // self.field_size_x, h // self.field_size_y)

        self.simulation_timer = QtCore.QTimer(self)
        self.simulation_timer.setInterval(100)
        self.simulation_timer.timeout.connect(self.update_field)

    # noinspection PyUnresolvedReferences
    def setup_ui_logic(self):
        self.simulation_update_delay_setting.settingValueChanged.connect(self.change_simulation_step_speed)
        self.alive_cell_color_setting.settingValueChanged.connect(self.update_cell_colors)
        self.dead_cell_color_setting.settingValueChanged.connect(self.update_cell_colors)
        self.cell_border_color_setting.settingValueChanged.connect(self.update_cell_colors)

        self.step_simulation_btn.clicked.connect(self.update_field)
        self.loop_simulation_btn.clicked.connect(self.loop_simulation)
        self.reset_simulation_btn.clicked.connect(self.reload_simulation)

        zoom_in_bind = QtWidgets.QShortcut(QtCore.Qt.Key_Equal, self._view)
        zoom_in_bind.activated.connect(self.simulation_zoom_in)
        zoom_out_bind = QtWidgets.QShortcut(QtCore.Qt.Key_Minus, self._view)
        zoom_out_bind.activated.connect(self.simulation_zoom_out)

    def setup_simulation(self):
        self.simulation_active = False

        self.field = Field(60, 60)
        self.field_size_x, self.field_size_y = self.field.get_size()

    def reload_simulation(self):
        if self.simulation_active:
            self.simulation_timer.stop()
            self.loop_simulation_btn.setText('Play')

        self.setup_simulation()
        self._painter.update()

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
            self.loop_simulation_btn.setText('Play')
        else:
            self.simulation_timer.start()
            self.loop_simulation_btn.setText('Pause')

        self.simulation_active = not self.simulation_active

    def get_hovered_cell(self):
        cursor_point = self._painter.mapFromGlobal(self.cursor().pos())

        cell_pos_x, cell_pos_y = int(cursor_point.x() / self.field_cell_size), \
                                 int(cursor_point.y() / self.field_cell_size)

        return self.field.matrix[cell_pos_y][cell_pos_x]

    def change_simulation_step_speed(self):
        v = self.simulation_update_delay_setting.value()
        self.simulation_timer.setInterval(v)

    def update_cell_colors(self):
        self.alive_cell_color = self.alive_cell_color_setting.value()
        self.dead_cell_color = self.dead_cell_color_setting.value()
        self.cell_border_color = self.cell_border_color_setting.value()

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
