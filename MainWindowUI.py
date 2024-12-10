from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QComboBox, QSlider, QRadioButton, QVBoxLayout, QLabel, QWidget, QHBoxLayout
from PyQt5.QtGui import QIcon
from ImageViewer import ImageViewer
from ComponentsMixer import ComponentsMixer
import logging

# Configure logging to capture all log levels
logging.basicConfig(filemode="a", filename="Logging_Info.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Signal_Mixer.ui", self)
        self.setWindowTitle("Image Mixer")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(450, 300, 1550, 950)
        self.central_widget = self.findChild(QWidget, "centralwidget")
        self.setCentralWidget(self.central_widget)

        #### LAYOUTS ####
        ##
        self.horizontalLayout_8 = self.findChild(QHBoxLayout, "horizontalLayout_8")
        self.viewer_layout_4 = self.findChild(QVBoxLayout, "viewer_layout_4")
        self.viewer_layout_4.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_6 = self.findChild(QHBoxLayout, "horizontalLayout_6")
        self.viewer_layout_3 = self.findChild(QVBoxLayout, "viewer_layout_3")
        self.viewer_layout_3.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_5 = self.findChild(QHBoxLayout, "horizontalLayout_5")
        self.viewer_layout_2 = self.findChild(QVBoxLayout, "viewer_layout_2")
        self.viewer_layout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_9 = self.findChild(QHBoxLayout, "horizontalLayout_9")
        self.viewer_layout_1 = self.findChild(QVBoxLayout, "viewer_layout_1")
        self.viewer_layout_1.addLayout(self.horizontalLayout_9)

        self.viewers_horizontal_layout = self.findChild(QHBoxLayout, "viewers_horizontal_layout")
        self.viewers_horizontal_layout.addLayout(self.viewer_layout_1)
        self.viewers_horizontal_layout.addLayout(self.viewer_layout_2)
        self.viewers_horizontal_layout.addLayout(self.viewer_layout_3)
        self.viewers_horizontal_layout.addLayout(self.viewer_layout_4)
        ##
        self.output_vertical_layout_1 = self.findChild(QVBoxLayout, "output_vertical_layout_1")
        self.output_vertical_layout_2 = self.findChild(QVBoxLayout, "output_vertical_layout_2")
        self.outputs_horizontal_layout = self.findChild(QHBoxLayout, "outputs_horizontal_layout")
        self.outputs_horizontal_layout.addLayout(self.output_vertical_layout_1)
        self.outputs_horizontal_layout.addLayout(self.output_vertical_layout_2)
        ##

        self.vertical_layout_3 = self.findChild(QVBoxLayout, "verticalLayout_3")
        self.vertical_layout_3.addLayout(self.viewers_horizontal_layout)
        self.vertical_layout_3.addLayout(self.outputs_horizontal_layout)

        self.horizontal_layout = self.findChild(QHBoxLayout, "horizontalLayout")
        self.horizontal_layout.addLayout(self.vertical_layout_3)

        self.mixer_vertical_layout = self.findChild(QVBoxLayout, "mixer_vertical_layout")

        self.central_widget.setLayout(self.mixer_vertical_layout)
        self.central_widget.setLayout(self.horizontal_layout)

        self.mixer_widget = self.findChild(QWidget, "mixer_widget")
        self.mixer_vertical_layout.addWidget(self.mixer_widget)

        #### LAYOUTS COMPLETE ####

        self.weight_sliders = []
        self.image_labels = []
        self.image_event_handlers = []
        self.ft_labels = []
        # self.viewer_combo_boxes = []
        self.mixer_combo_boxes = []
        self.output_labels = []
        self.sliders_values = [100]*4
        self.mode = "real_img"

        ######### SETUP: DO NOT CHANGE THE ORDER OF ANYTHING #########

        for i in range(1, 5):
            # MIXER
                # Mixer Combo Boxes
            mixer_combo_box = self.findChild(QComboBox, f"mixer_combobox_{i}")
            mixer_combo_box.addItem("None")
            mixer_combo_box.addItem("FT Magnitude")
            mixer_combo_box.addItem("FT Phase")
            mixer_combo_box.addItem("FT Imaginary")
            mixer_combo_box.addItem("FT Real")
            self.mixer_combo_boxes.append(mixer_combo_box)

            # IMAGE VIEWERS
                # Viewer Comboboxes
            # viewer_combobox = self.findChild(QComboBox, f"viewer_combobox_{i}")
            # viewer_combobox.addItem("None")
            # viewer_combobox.addItem("FT Magnitude")
            # viewer_combobox.addItem("FT Phase")
            # viewer_combobox.addItem("FT Imaginary")
            # viewer_combobox.addItem("FT Real")
            # self.viewer_combo_boxes.append(viewer_combobox)

                # Component Viewers
            ft_label = self.findChild(QLabel, f"ft_label_{i}")

                # Image Viewers
            image_label = self.findChild(QLabel, f"image_viewer_{i}")
            image_events_handler = ImageViewer(image_label, ft_label, mixer_combo_box, i-1, self)
            self.image_labels.append(image_label)
            self.image_event_handlers.append(image_events_handler)
            self.ft_labels.append(ft_label)
            image_label.installEventFilter(image_events_handler)

            # OUTPUT VIEWERS
            self.output_label_one = self.findChild(QLabel, "output_label_one")
            self.output_label_two = self.findChild(QLabel, "output_label_two")
            self.output_labels.append(self.output_label_one)
            self.output_labels.append(self.output_label_two)

            self.components_mixer = ComponentsMixer(self.mode, self.image_event_handlers, self.mixer_combo_boxes,
                                                    self.output_labels)

            # Sliders
            slider = self.findChild(QSlider, f"horizontalSlider_{i}")
            slider.setRange(0, 100)
            slider.setValue(100)
            slider.setObjectName(f"slider_{i}")
            slider.valueChanged.connect(lambda value, index=i: self.components_mixer.change_weights(value, index-1))
            self.weight_sliders.append(slider)

        # # Mode Selection
        self.real_img_mode = self.findChild(QRadioButton, "real_img_button")
        self.phase_mag_mode = self.findChild(QRadioButton, "mag_phase_button")
        self.real_img_mode.setChecked(True)  # default mode
        self.update_combobox(True)
        self.real_img_mode.toggled.connect(self.update_combobox)
        self.phase_mag_mode.toggled.connect(self.update_combobox)

        # Mixer Output Channel
        self.mixer_output_combobox = self.findChild(QComboBox, "mixer_output_combobox")
        self.mixer_output_combobox.addItem("Output 1")
        self.mixer_output_combobox.addItem("Output 2")
        self.mixer_output_combobox.currentIndexChanged.connect(self.change_output_channel)

    def update_combobox(self, on_start):
        is_real_img = self.real_img_mode.isChecked()
        if is_real_img:
            self.mode = "real_img"
            self.components_mixer.mode = "real_img"
        else:
            self.mode = "mag_phase"
            self.components_mixer.mode = "mag_phase"
        logging.info(f"Mode Changed: Real/Imaginary")
        for i in range(4):  # 4 combo boxes
            # viewer_combobox = self.viewer_combo_boxes[i]
            mixer_combobox = self.mixer_combo_boxes[i]
            slider = self.weight_sliders[i]
            ft_label = self.ft_labels[i]
            for j in range(1, 5):  # 4 items per combobox
                if j == 3 or j == 4:
                    # viewer_combobox.model().item(j).setEnabled(is_real_img)
                    mixer_combobox.model().item(j).setEnabled(is_real_img)
                else:
                    # viewer_combobox.model().item(j).setEnabled(not is_real_img)
                    mixer_combobox.model().item(j).setEnabled(not is_real_img)

        # Reset Controls
            mixer_combobox.blockSignals(True)
            slider.blockSignals(True)
            mixer_combobox.setCurrentIndex(0)
            slider.setValue(100)
            mixer_combobox.blockSignals(False)
            slider.blockSignals(False)
            ft_label.clear()
        self.output_label_one.clear()
        self.output_label_two.clear()
        if not on_start:
            try:
                self.components_mixer.set_mode(self.mode)
            except Exception as e:
                logging.error(f"Error setting mode in mixer: {e}")

    def change_output_channel(self):
        if self.mixer_output_combobox.currentText() == "Output 1":
            self.components_mixer.set_output(1)
        else:
            self.components_mixer.set_output(2)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())