import os
import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow

from field.field import Field
from ui.main_ui import UIForm
from file_handlers.settings_file_handler import SettingsFileHandler


class GameOfLife(QMainWindow, UIForm):
    FACTOR = 1.2
    SIMULATION_WINDOW_SIZE = 600, 600
    SETTINGS_FILE = 'settings.txt'

    def __init__(self):
        super().__init__()

        # Поле
        self.field = ...
        self.field_size_x, self.field_size_y = ..., ...

        self.sfh = ...

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
        self.setup_settings()
        self.setup_ui(self)
        self.setup_ui_logic()

        self.alive_cell_color_setting.current_color = QtGui.QColor(self.sfh.get_setting('alive_cell_color'))
        self.dead_cell_color_setting.current_color = QtGui.QColor(self.sfh.get_setting('dead_cell_color'))
        self.cell_border_color_setting.current_color = QtGui.QColor(self.sfh.get_setting('cell_border_color'))
        self.alive_cell_color_setting.updatePanelColor()
        self.dead_cell_color_setting.updatePanelColor()
        self.cell_border_color_setting.updatePanelColor()

        self.alive_cell_color = self.alive_cell_color_setting.value()
        self.dead_cell_color = self.dead_cell_color_setting.value()
        self.cell_border_color = self.cell_border_color_setting.value()

        w, h = self._painter.width(), self._painter.height()
        self.field_cell_size = min(w // self.field_size_x, h // self.field_size_y)

        self.simulation_timer = QtCore.QTimer(self)
        self.simulation_timer.setInterval(self.sfh.get_setting('simulation_update_delay'))
        self.simulation_timer.timeout.connect(self.update_field)

    def setup_settings(self):
        first_launch = False
        if not os.path.isfile(self.SETTINGS_FILE):
            first_launch = True

        self.sfh = SettingsFileHandler(self.SETTINGS_FILE)

        if not first_launch:
            self.sfh.read_settings()

        if not self.sfh.has_setting('simulation_update_delay'):
            self.sfh.set_setting('simulation_update_delay', 50)

        if not self.sfh.has_setting('alive_cell_color'):
            self.sfh.set_setting('alive_cell_color', '#ffffff')

        if not self.sfh.has_setting('dead_cell_color'):
            self.sfh.set_setting('dead_cell_color', '#000000')

        if not self.sfh.has_setting('cell_border_color'):
            self.sfh.set_setting('cell_border_color', '#323232')

        self.sfh.write_settings()

    def setup_ui_logic(self):
        self.simulation_update_delay_setting.settingValueChanged.connect(self.change_simulation_update_delay)
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

        self.field = Field(100, 100)
        self.field_size_x, self.field_size_y = self.field.get_size()

    def reload_simulation(self):
        if self.simulation_active:
            self.simulation_timer.stop()
            self.loop_simulation_btn.setText('Play')

        self.setup_simulation()
        self._painter.update()

    def mousePressEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton and
                self._view.underMouse() and
                not self.simulation_active):
            self.drag_start = event.pos()

            cell = self.get_hovered_cell()
            if cell is not None:
                if cell.get_state() == Field.Cell.DEAD:
                    self.dragging_to_cell_state = Field.Cell.ALIVE
                else:
                    self.dragging_to_cell_state = Field.Cell.DEAD
                cell.set_state(self.dragging_to_cell_state)
                self._painter.update()

    def mouseReleaseEvent(self, event):
        self.drag_start = None
        self.dragging_to_cell_state = None

    def mouseMoveEvent(self, event):
        if (self.drag_start is not None and
                self.dragging_to_cell_state is not None and
                event.buttons() & QtCore.Qt.LeftButton and
                self._view.underMouse() and
                event.pos() != self.drag_start):
            cell = self.get_hovered_cell()
            if cell is not None:
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
        if (cell_pos_x < 0 or cell_pos_x > self.field_size_x - 1 or
                cell_pos_y < 0 or cell_pos_y > self.field_size_y - 1):
            return

        return self.field.matrix[cell_pos_y][cell_pos_x]

    def change_simulation_update_delay(self):
        v = self.simulation_update_delay_setting.value()
        self.simulation_timer.setInterval(v)
        self.sfh.set_setting('simulation_update_delay', v)
        self.sfh.write_settings()

    def update_cell_colors(self):
        self.alive_cell_color = self.alive_cell_color_setting.value()
        self.dead_cell_color = self.dead_cell_color_setting.value()
        self.cell_border_color = self.cell_border_color_setting.value()

        self.sfh.set_setting('alive_cell_color', self.alive_cell_color.name())
        self.sfh.set_setting('dead_cell_color', self.dead_cell_color.name())
        self.sfh.set_setting('cell_border_color', self.cell_border_color.name())
        self.sfh.write_settings()

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
        if tr.m11() < 3:
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
