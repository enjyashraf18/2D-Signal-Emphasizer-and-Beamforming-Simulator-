from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QComboBox, QSlider, QRadioButton, QButtonGroup
from ImageViewer import ImageViewer
from ComponentsMixer import ComponentsMixer


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ImageViewer")
        self.setGeometry(300, 200, 1200, 600)
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(main_layout)
        # horizontal layout for the image widget and for the ft and combo
        self.image_ft_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(self.image_ft_layout)

        # creation of widgets
        self.image_widgets = []
        self.ft_widgets = []
        self.combo_boxes = []
        self.image_event_handlers = []

        for i in range(4):  # Create 4 sets of widgets
            # vertical for each one
            v_layout = QtWidgets.QVBoxLayout()

            # image widget
            image_widget = QtWidgets.QLabel("Double-click me!")
            # image_widget.setObjectName(f"ImageWidget_{i}")
            image_widget.setAlignment(QtCore.Qt.AlignCenter)
            image_widget.setStyleSheet("background-color: black;")
            image_widget.setFixedSize(300, 200)
            v_layout.addWidget(image_widget)

            # ft  widget
            ft_widget = QtWidgets.QLabel("Fourier Transform")
            ft_widget.setStyleSheet("background-color: black;")
            ft_widget.setFixedSize(300, 200)
            ft_widget.setAlignment(QtCore.Qt.AlignCenter)
            v_layout.addWidget(ft_widget)

            # combo box
            combo_box = QComboBox(self)
            combo_box.addItem("None")
            combo_box.addItem("FT Magnitude")
            combo_box.addItem("FT Phase")
            combo_box.addItem("FT Imaginary")
            combo_box.addItem("FT Real")
            v_layout.addWidget(combo_box)
    # add the vertical to the horizontal
            self.image_ft_layout.addLayout(v_layout)

            #append/s
            self.image_widgets.append(image_widget)
            self.ft_widgets.append(ft_widget)
            self.combo_boxes.append(combo_box)

            image_events_handler = ImageViewer(image_widget, ft_widget, combo_box, i, self)
            self.image_event_handlers.append(image_events_handler)
            image_widget.installEventFilter(image_events_handler)

        self.sliders_values = [100]*4
        self.components_mixer = ComponentsMixer(self.image_event_handlers, self.combo_boxes, self.sliders_values)

        # sliders
        self.weight_sliders = []
        for i in range(0, 4):
            slider = QSlider()
            slider.setRange(0, 100)
            slider.setObjectName(f"slider_{i}")
            slider.valueChanged.connect(lambda value, index=i: self.components_mixer.change_weights(value, index))
            self.weight_sliders.append(slider)
            self.image_ft_layout.addWidget(slider)

        # mode selection
        self.real_img_mode = QRadioButton("Real/Imaginary")
        self.phase_mag_mode = QRadioButton("Phase/Magnitude")
        self.mode_selection = QButtonGroup()
        self.mode_selection.addButton(self.real_img_mode)
        self.mode_selection.addButton(self.phase_mag_mode)
        self.image_ft_layout.addWidget(self.real_img_mode)
        self.image_ft_layout.addWidget(self.phase_mag_mode)

        self.real_img_mode.toggled.connect(self.update_combobox)
        self.phase_mag_mode.toggled.connect(self.update_combobox)

    def update_combobox(self):
        is_real_img = self.real_img_mode.isChecked()
        for i in range(4):  # 4 combo boxes
            combobox = self.combo_boxes[i]
            for j in range(1, 5):  # 4 items per combobox
                if j == 3 or j == 4:
                    print("here")
                    combobox.model().item(j).setEnabled(is_real_img)
                else:
                    combobox.model().item(j).setEnabled(not is_real_img)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
