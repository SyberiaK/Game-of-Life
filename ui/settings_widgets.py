from PyQt5 import QtCore, QtGui, QtWidgets


class SettingWidget(QtWidgets.QWidget):
    settingValueChanged = QtCore.pyqtSignal(int)

    def __init__(self, *args, setting_name: str, **kwargs):
        super(SettingWidget, self).__init__(*args, **kwargs)
        self.setting_name = QtWidgets.QLabel(setting_name, self)
        self.setting_value = QtWidgets.QWidget(self)

    def construct(self):
        self.setLayout(QtWidgets.QVBoxLayout())
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                           QtWidgets.QSizePolicy.Maximum)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.layout().addWidget(self.setting_name)
        self.layout().addWidget(self.setting_value)


class SliderSettingWidget(SettingWidget):
    def __init__(self, *args, **kwargs):
        super(SliderSettingWidget, self).__init__(*args, **kwargs)

        self.setting_value.setLayout(QtWidgets.QHBoxLayout())
        self.setting_value.setContentsMargins(0, 0, 0, 0)

        self.setting_value_slider = QtWidgets.QSlider(self.setting_value)
        self.setting_value_display_multiplier = 1
        self.setting_value_label = QtWidgets.QLabel(
            f'{self.value() * self.setting_value_display_multiplier:.2f}', self.setting_value
        )

        self.setting_value_slider.valueChanged.connect(self.setting_value_changed)

    def construct(self):
        self.setting_value.layout().addWidget(self.setting_value_slider)
        self.setting_value.layout().addWidget(self.setting_value_label)
        self.setting_value_slider.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                           QtWidgets.QSizePolicy.Minimum)

        super(SliderSettingWidget, self).construct()

    def setSettingValueDisplayMultiplier(self, mult: float):
        self.setting_value_display_multiplier = mult
        self.update_value_label()

    def setRange(self, start: int, end: int):
        self.setting_value_slider.setRange(start, end)

    def setPageStep(self, step: int):
        self.setting_value_slider.setPageStep(step)

    def setSingleStep(self, step: int):
        self.setting_value_slider.setSingleStep(step)

    def setValue(self, value: int):
        self.setting_value_slider.setValue(value)

    def setSliderOrientation(self, orientation: QtCore.Qt.Orientation):
        self.setting_value_slider.setOrientation(orientation)

    def setSliderInvertedAppearance(self, b: bool):
        self.setting_value_slider.setInvertedAppearance(b)

    @QtCore.pyqtSlot(int)
    def setting_value_changed(self):
        self.update_value_label()
        self.settingValueChanged.emit(self)

    def value(self):
        return self.setting_value_slider.value()

    def update_value_label(self):
        self.setting_value_label.setText(f'{self.value() * self.setting_value_display_multiplier:.2f}')


class ColorSettingWidget(SettingWidget):
    def __init__(self, *args, default_color: QtGui.QColor, **kwargs):
        super(ColorSettingWidget, self).__init__(*args, **kwargs)

        self.current_color = default_color

        self.setting_value.setLayout(QtWidgets.QHBoxLayout())
        self.setting_value.setContentsMargins(0, 0, 0, 0)

        self.setting_value_frame = QtWidgets.QFrame(self.setting_value)
        self.setting_value_frame.setMinimumSize(QtCore.QSize(25, 25))
        self.setting_value_frame.setMaximumSize(QtCore.QSize(50, 50))
        self.setting_value_frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.setting_value_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.setting_value_frame.sizePolicy().hasHeightForWidth())
        self.setting_value_frame.setSizePolicy(size_policy)
        self.updatePanelColor()

        self.setting_value_button = QtWidgets.QPushButton('Change color', self.setting_value)

        self.setting_value_button.clicked.connect(self.__new_color)

    def construct(self):
        self.setting_value.layout().addWidget(self.setting_value_frame)
        self.setting_value.layout().addWidget(self.setting_value_button)

        super(ColorSettingWidget, self).construct()

    def __new_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.current_color = color
            self.updatePanelColor()
            self.settingValueChanged.emit(self)

    def value(self):
        return self.current_color

    def updatePanelColor(self):
        self.setting_value_frame.setStyleSheet(
            "background-color: {}".format(self.current_color.name()))