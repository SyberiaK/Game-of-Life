from PyQt5 import QtCore, QtGui, QtWidgets

from ui.cell_painter import CellPainter
from ui.simulation_view import SimulationView
from ui.settings_widgets import SliderSettingWidget, ColorSettingWidget


class UIForm(object):
    def __init__(self):
        self._view = ...
        self._painter = ...
        self.loop_simulation_btn = ...
        self.step_simulation_btn = ...
        self.reset_simulation_btn = ...

    def setup_ui(self, form):
        form.setWindowTitle('Жизнь')

        main_widget = QtWidgets.QWidget(form)
        main_widget.setLayout(QtWidgets.QHBoxLayout())
        main_widget.layout().setContentsMargins(9, 9, 9, 9)

        # Зона настроек
        settings_group = QtWidgets.QGroupBox('Settings', form)
        settings_group.setLayout(QtWidgets.QVBoxLayout())
        settings_group.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        settings_group.setContentsMargins(0, 0, 0, 0)

        self.simulation_update_delay_setting = SliderSettingWidget(settings_group,
                                                                   setting_name='Simulation update delay')
        self.simulation_update_delay_setting.setRange(10, 500)
        self.simulation_update_delay_setting.setPageStep(10)
        self.simulation_update_delay_setting.setSingleStep(10)
        self.simulation_update_delay_setting.setValue(self.sfh.get_setting('simulation_update_delay'))
        self.simulation_update_delay_setting.setSettingValueDisplayMultiplier(.001)
        self.simulation_update_delay_setting.setSliderOrientation(QtCore.Qt.Horizontal)
        self.simulation_update_delay_setting.setSliderInvertedAppearance(True)
        self.simulation_update_delay_setting.construct()

        self.alive_cell_color_setting = ColorSettingWidget(settings_group, setting_name='Alive cells color',
                                                           default_color=QtGui.QColor(255, 255, 255, 255))
        self.alive_cell_color_setting.construct()

        self.dead_cell_color_setting = ColorSettingWidget(settings_group, setting_name='Dead cells color',
                                                          default_color=QtGui.QColor(0, 0, 0, 255))
        self.dead_cell_color_setting.construct()

        self.cell_border_color_setting = ColorSettingWidget(settings_group, setting_name='Cells border color',
                                                            default_color=QtGui.QColor(50, 50, 50, 255))
        self.cell_border_color_setting.construct()

        settings_group.layout().addWidget(self.simulation_update_delay_setting)
        settings_group.layout().addWidget(self.alive_cell_color_setting)
        settings_group.layout().addWidget(self.dead_cell_color_setting)
        settings_group.layout().addWidget(self.cell_border_color_setting)

        spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        settings_group.layout().addItem(spacer_item)

        # Зона симуляции
        simulation_widget = QtWidgets.QWidget(form)
        simulation_widget.setLayout(QtWidgets.QVBoxLayout())
        simulation_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                                        QtWidgets.QSizePolicy.Policy.Expanding)

        scene = QtWidgets.QGraphicsScene(form)
        self._view = SimulationView(scene)

        self._painter = CellPainter(form)
        self._painter.setFixedSize(*form.SIMULATION_WINDOW_SIZE)

        scene.addWidget(self._painter)
        self._view.setFixedSize(self._view.sizeHint())
        self._painter.setMouseTracking(True)

        btns_holder = QtWidgets.QWidget(form)
        btns_holder.setLayout(QtWidgets.QHBoxLayout())
        btns_holder.layout().setContentsMargins(9, 9, 9, 0)
        btns_holder.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum,
                                  QtWidgets.QSizePolicy.Policy.Maximum)

        # Кнопки зоны симуляции
        self.loop_simulation_btn = QtWidgets.QPushButton('Play')
        self.loop_simulation_btn.setFixedSize(50, 50)

        self.step_simulation_btn = QtWidgets.QPushButton('Step')
        self.step_simulation_btn.setFixedSize(50, 50)

        self.reset_simulation_btn = QtWidgets.QPushButton('Reset')
        self.reset_simulation_btn.setFixedSize(50, 50)

        # Расстановка виджетов
        btns_holder.layout().addWidget(self.loop_simulation_btn)
        btns_holder.layout().addWidget(self.step_simulation_btn)
        btns_holder.layout().addWidget(self.reset_simulation_btn)

        simulation_widget.layout().addWidget(self._view)
        simulation_widget.layout().addWidget(btns_holder)

        main_widget.layout().addWidget(settings_group)
        main_widget.layout().addWidget(simulation_widget)

        form.setCentralWidget(main_widget)
