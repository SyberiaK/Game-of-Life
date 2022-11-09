import os
import sys
from typing import SupportsInt

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow

from field.field import Field
from ui.main_ui import UIForm
from ui.cell_painter import CellPainter
from ui.simulation_view import SimulationView
from file_handlers.settings_file_handler import SettingsFileHandler
from file_handlers.save_file_handler import SaveFileHandler


class GameOfLife(QMainWindow, UIForm):
    FACTOR = 1.5
    SIMULATION_WINDOW_SIZE = 600, 600
    FIELD_SIZE = 100, 100
    SETTINGS_FILE = 'settings.txt'

    def __init__(self):
        super().__init__()

        # Поле
        self.field: Field = ...
        self.field_size_x: int = ...
        self.field_size_y: int = ...

        # Обработчик настроек
        self.settingsfh: SettingsFileHandler = ...

        # Переменные для рисования и работы симуляции
        self.simulation_active: bool = ...
        self.drag_start: QtCore.QPoint = ...
        self.dragging_to_cell_state: SupportsInt = ...

        # Виджеты
        self._view: SimulationView = ...
        self._painter: CellPainter = ...
        self.loop_simulation_btn: QtWidgets.QPushButton = ...
        self.step_simulation_btn: QtWidgets.QPushButton = ...
        self.reset_simulation_btn: QtWidgets.QPushButton = ...

        # Цвета элементов поля
        self.alive_cell_color: str = ...
        self.dead_cell_color: str = ...
        self.field_grid_color: str = ...

        # Переменная для отслеживания масштабирования
        self.zoom_x: float = ...

        # Подготовка к работе вынесена в отдельные методы
        self.setup_simulation()
        self.setup_settings()
        self.setup_ui(self)
        self.setup_ui_logic()

        # Цвета подтягиваются из файла настроек в настройки внутри программы
        self.alive_cell_color_setting.current_color = QtGui.QColor(self.settingsfh.get_setting('alive_cell_color'))
        self.dead_cell_color_setting.current_color = QtGui.QColor(self.settingsfh.get_setting('dead_cell_color'))
        self.field_grid_color_setting.current_color = QtGui.QColor(self.settingsfh.get_setting('field_grid_color'))
        # Обновление цветных панелей в настройках
        self.alive_cell_color_setting.updatePanelColor()
        self.dead_cell_color_setting.updatePanelColor()
        self.field_grid_color_setting.updatePanelColor()

        # Цвета из настроек
        self.alive_cell_color = self.alive_cell_color_setting.value()
        self.dead_cell_color = self.dead_cell_color_setting.value()
        self.cell_border_color = self.field_grid_color_setting.value()

        w, h = self._painter.width(), self._painter.height()
        self.field_cell_size = min(w // self.field_size_x, h // self.field_size_y)

        # Таймер, по которому происходит цикличная симуляция
        self.simulation_timer = QtCore.QTimer(self)
        self.simulation_timer.setInterval(self.settingsfh.get_setting('simulation_update_delay'))
        self.simulation_timer.timeout.connect(self.update_field)

    def setup_settings(self):
        first_launch = False
        if not os.path.isfile(self.SETTINGS_FILE):
            first_launch = True

        self.settingsfh = SettingsFileHandler(self.SETTINGS_FILE)

        if not first_launch:
            # Если запуск не первый - значит, есть файл настроек, можно прочитать его
            self.settingsfh.read_settings()

        # Далее идут проверки настроек
        if not self.settingsfh.has_setting('simulation_update_delay'):
            self.settingsfh.set_setting('simulation_update_delay', 50)

        if not self.settingsfh.has_setting('alive_cell_color'):
            self.settingsfh.set_setting('alive_cell_color', '#ffffff')

        if not self.settingsfh.has_setting('dead_cell_color'):
            self.settingsfh.set_setting('dead_cell_color', '#000000')

        if not self.settingsfh.has_setting('field_grid_color'):
            self.settingsfh.set_setting('field_grid_color', '#323232')

        # Перезапись, если какая-то из настроек отсутствовала
        self.settingsfh.write_settings()

    def setup_ui_logic(self):
        self.zoom_x = 1

        # Подключаем изменение настроек к соответствующим методам
        self.simulation_update_delay_setting.settingValueChanged.connect(self.change_simulation_update_delay)
        self.alive_cell_color_setting.settingValueChanged.connect(self.update_cell_colors)
        self.dead_cell_color_setting.settingValueChanged.connect(self.update_cell_colors)
        self.field_grid_color_setting.settingValueChanged.connect(self.update_cell_colors)

        # По нажатию на Step (self.step_simulation_btn) функция вызывается один раз
        # По нажатию на Play (self.loop_simulation_btn) активируется QTimer, который через равные промежутки времени вызывает функцию
        # По нажатию на Stop (self.loop_simulation_btn) QTimer деактивируется
        self.step_simulation_btn.clicked.connect(self.update_field)
        self.loop_simulation_btn.clicked.connect(self.loop_simulation)
        self.reset_simulation_btn.clicked.connect(self.reload_simulation)

        # Создаём QShortcut для масштабирования
        zoom_in_bind = QtWidgets.QShortcut(QtCore.Qt.Key_Equal, self._view)
        zoom_in_bind.activated.connect(self.simulation_zoom_in)
        zoom_out_bind = QtWidgets.QShortcut(QtCore.Qt.Key_Minus, self._view)
        zoom_out_bind.activated.connect(self.simulation_zoom_out)

    def setup_simulation(self):
        self.simulation_active = False

        self.field = Field(*self.FIELD_SIZE)
        self.field_size_x, self.field_size_y = self.FIELD_SIZE

    def reload_simulation(self):
        # Сброс симуляции - очистка поля
        if self.simulation_active:
            self.simulation_timer.stop()
            self.loop_simulation_btn.setText('Play')

        self.setup_simulation()
        self._painter.update()

    def mousePressEvent(self, event):
        # При зажатии ЛКМ на поле мы запоминаем начальную позицию курсора
        # и состояние первой клетки, берём противоположное
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
        # При отжатии ЛКМ очищаем используемые переменные
        self.drag_start = None
        self.dragging_to_cell_state = None

    def mouseMoveEvent(self, event):
        # При движении с зажатым ЛКМ меняем состояние клеток на взятое, если они не находятся в нём
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
        # Главный костыль масштабирования
        # По какой-то необъяснимой причине получаемая позиция курсора относительно CellPainter
        # абсолютно не совпадает с действительной, поэтому приходится выдумывать, как находить нужную (нажатую) клетку
        cursor_point = self._view.mapFromGlobal(self.cursor().pos())
        if self._view.horizontalScrollBar().isVisible():
            h_offset, v_offset = self._view.horizontalScrollBar().value() / self._view.horizontalScrollBar().maximum(),\
                                 self._view.verticalScrollBar().value() / self._view.verticalScrollBar().maximum()
        else:
            h_offset, v_offset = 0, 0

        cell_pos_x, cell_pos_y = int((cursor_point.x() + 140 * self.zoom_x ** 2 * h_offset) / self.field_cell_size), \
                                 int((cursor_point.y() + 140 * self.zoom_x ** 2 * v_offset) / self.field_cell_size)
        if (cell_pos_x < 0 or cell_pos_x > self.field_size_x - 1 or
                cell_pos_y < 0 or cell_pos_y > self.field_size_y - 1):
            return
        return self.field.matrix[cell_pos_y][cell_pos_x]

    def change_simulation_update_delay(self):
        # Значение изменяется
        v = self.simulation_update_delay_setting.value()
        self.simulation_timer.setInterval(v)
        # Значение сохраняется
        self.settingsfh.set_setting('simulation_update_delay', v)
        # Настройки перезаписываются
        self.settingsfh.write_settings()

    def update_cell_colors(self):
        self.alive_cell_color = self.alive_cell_color_setting.value()
        self.dead_cell_color = self.dead_cell_color_setting.value()
        self.cell_border_color = self.field_grid_color_setting.value()

        self.settingsfh.set_setting('alive_cell_color', self.alive_cell_color.name())
        self.settingsfh.set_setting('dead_cell_color', self.dead_cell_color.name())
        self.settingsfh.set_setting('field_grid_color', self.cell_border_color.name())
        self.settingsfh.write_settings()

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
            self.zoom_x = tr.m11()
            self._view.setTransform(tr)
            w, h = self._view.width(), self._view.height()
            self.field_cell_size = int(min(w * tr.m11() / self.field_size_x, h * tr.m11() / self.field_size_y))
            print(self.field_cell_size)

    @QtCore.pyqtSlot()
    def simulation_zoom_out(self):
        scale_tr = QtGui.QTransform().scale(self.FACTOR, self.FACTOR)

        scale_inverted, invertible = scale_tr.inverted()

        if invertible:
            tr = self._view.transform() * scale_inverted
            if tr.m11() >= 1:
                self.zoom_x = tr.m11()
                self._view.setTransform(tr)
                w, h = self._view.width(), self._view.height()
                self.field_cell_size = int(min(w * tr.m11() / self.field_size_x, h * tr.m11() / self.field_size_y))
                print(self.field_cell_size)

    @QtCore.pyqtSlot()
    def create_save_file(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '', 'Save file (*.sav)')[0]
        if filename:
            SaveFileHandler.save_file(filename, self.field.matrix)

    @QtCore.pyqtSlot()
    def open_save_file(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose your save file', '', 'Save file (*.sav)')[0]
        if filename:
            self.field.matrix = SaveFileHandler.open_file(filename)


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
