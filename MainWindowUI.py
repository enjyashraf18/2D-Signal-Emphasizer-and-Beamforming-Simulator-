from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QComboBox, QSlider, QRadioButton, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QProgressBar
from PyQt5.QtGui import QIcon
from ImageViewer import ImageViewer
from ComponentsMixer import ComponentsMixer
import logging
import pyqtgraph as pg

# Configure logging to capture all log levels
logging.basicConfig(filemode="a", filename="Logging_Info.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Signal_Mixer.ui", self)
        self.setWindowTitle("Image Mixer")
        self.setWindowIcon(QIcon("Deliverables/icon.png"))
        self.setGeometry(450, 300, 1550, 950)
        self.central_widget = self.findChild(QWidget, "centralwidget")
        self.setCentralWidget(self.central_widget)

        #### LAYOUTS ####
        ##
        self.horizontalLayout_4 = self.findChild(QHBoxLayout, "horizontalLayout_8")
        # self.horizontalLayout_4.name = "horizontal_layout_4"
        self.viewer_layout_4 = self.findChild(QVBoxLayout, "viewer_layout_4")
        self.viewer_layout_4.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = self.findChild(QHBoxLayout, "horizontalLayout_6")
        # self.horizontalLayout_3.name = "horizontal_layout_3"
        self.viewer_layout_3 = self.findChild(QVBoxLayout, "viewer_layout_3")
        self.viewer_layout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = self.findChild(QHBoxLayout, "horizontalLayout_5")
        # self.horizontalLayout_2.name = "horizontal_layout_2"
        self.viewer_layout_2 = self.findChild(QVBoxLayout, "viewer_layout_2")
        self.viewer_layout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_1 = self.findChild(QHBoxLayout, "horizontalLayout_9")
        # self.horizontalLayout_1.name = "horizontal_layout_1"
        self.viewer_layout_1 = self.findChild(QVBoxLayout, "viewer_layout_1")
        self.viewer_layout_1.addLayout(self.horizontalLayout_1)

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
        self.ft_widgets = []
        # self.viewer_combo_boxes = []
        self.mixer_combo_boxes = []
        self.output_labels = []
        self.sliders_values = [100]*4
        self.slider_labels = []
        self.mode = "real_img"

        self.ROI_rectangles = []
        self.img_FtComponent = None

        ######### SETUP: DO NOT CHANGE THE ORDER OF ANYTHING #########

        # Progress Bar
        self.progress_bar = self.findChild(QProgressBar, "progress_bar")

        # Mixer Region Selection
        self.region_combobox = self.findChild(QComboBox, "mixer_region_combo_box")
        self.region_combobox.addItem("Inner Region")
        self.region_combobox.addItem("Outer Region")

        for i in range(1, 5):
            self.img_FtComponent = None
            detect_first_time = False
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
            viewer_combobox = self.findChild(QComboBox, f"viewer_combobox_{i}")
            # viewer_combobox.addItem("None")
            # viewer_combobox.addItem("FT Magnitude")
            # viewer_combobox.addItem("FT Phase")
            # viewer_combobox.addItem("FT Imaginary")
            # viewer_combobox.addItem("FT Real")
            # self.viewer_combo_boxes.append(viewer_combobox)

                # Component Viewers
            ft_widget = self.findChild(QWidget, f"ft_widget_{i}")

            if i == 1:
                self.horizontalLayout_1.removeWidget(ft_widget)
                self.horizontalLayout_1.removeWidget(viewer_combobox)
            elif i == 2:
                self.horizontalLayout_2.removeWidget(ft_widget)
                self.horizontalLayout_2.removeWidget(viewer_combobox)
            elif i == 3:
                self.horizontalLayout_3.removeWidget(ft_widget)
                self.horizontalLayout_3.removeWidget(viewer_combobox)
            else:
                self.horizontalLayout_4.removeWidget(ft_widget)
                self.horizontalLayout_4.removeWidget(viewer_combobox)

            ft_widget.deleteLater()
            viewer_combobox.deleteLater()
            ft_widget = pg.GraphicsLayoutWidget()
            ft_view = ft_widget.addViewBox()
            self.img_FtComponent = pg.ImageItem()
            ft_view.addItem(self.img_FtComponent)
            ft_widget.setFixedSize(250, 250)

            if i == 1:
                self.horizontalLayout_1.addWidget(ft_widget)
            elif i == 2:
                self.horizontalLayout_2.addWidget(ft_widget)
            elif i == 3:
                self.horizontalLayout_3.addWidget(ft_widget)
            else:
                self.horizontalLayout_4.addWidget(ft_widget)

            # Image Viewers
            image_label = self.findChild(QLabel, f"image_viewer_{i}")
            image_events_handler = ImageViewer(image_label, ft_widget, mixer_combo_box, i-1, self, detect_first_time, self.img_FtComponent, self.ROI_rectangles, self.region_combobox)
            self.image_labels.append(image_label)
            self.image_event_handlers.append(image_events_handler)
            self.ft_widgets.append(ft_widget)
            image_label.installEventFilter(image_events_handler)

            # OUTPUT VIEWERS
            self.output_label_one = self.findChild(QLabel, "output_label_one")
            self.output_label_two = self.findChild(QLabel, "output_label_two")
            self.output_labels.append(self.output_label_one)
            self.output_labels.append(self.output_label_two)

            self.components_mixer = ComponentsMixer(self.mode, self.image_event_handlers, self.mixer_combo_boxes,
                                                    self.output_labels, self.progress_bar, self.region_combobox)

            # Slider labels
            slider_label = self.findChild(QLabel, f"weight_{i}")
            self.slider_labels.append(slider_label)
            # Sliders
            slider = self.findChild(QSlider, f"horizontalSlider_{i}")
            slider.setRange(0, 100)
            slider.setValue(100)
            slider.setObjectName(f"slider_{i}")
            slider.valueChanged.connect(lambda value, index=i: self.update_sliders(value, index-1))
            self.weight_sliders.append(slider)


        # Mode Selection
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
            ft_widget = self.ft_widgets[i]
            for j in range(1, 5):  # 4 items per combobox
                item = mixer_combobox.model().item(j)
                if j == 3 or j == 4:
                    # viewer_combobox.model().item(j).setEnabled(is_real_img)
                    item.setEnabled(is_real_img)
                else:
                    # viewer_combobox.model().item(j).setEnabled(not is_real_img)
                    item.setEnabled(not is_real_img)

        # Change UI of disabled items (not working)
        #     mixer_combobox.setStyleSheet("""
        #     QComboBox {
        #         color: rgb(255, 255, 255);
        #         font-size: 18px;
        #         background-color: rgb(24, 24, 24);
        #         padding-left: 15px;
        #         border: 1px solid transparent;
        #         border-radius: 15px; /* Rounded corners */
        #     }
        #
        #     QComboBox:disabled {
        #     color: rgb(0, 0, 0); /* Change text color when disabled */
        #     background-color: rgb(50, 50, 50); /* Change background color when disabled */
        #     border: 1px solid rgb(100, 100, 100); /* Change border color when disabled */
        #     }
        #
        #
        #     QComboBox QAbstractItemView {
        #         background-color: #444444;    /* Dropdown list background */
        #         color: #ffffff;               /* Dropdown list text color */
        #         selection-background-color: #555555;  /* Highlight background */
        #         selection-color: #FF5757;     /* Highlighted text color */
        #     }
        #
        #     /* Remove the default arrow */
        #     QComboBox::drop-down {
        #         margin-right: 10px;
        #         border-top-right-radius: 15px; /* Apply radius to the top-right */
        #         border-bottom-right-radius: 15px; /* Apply radius to the bottom-right */
        #     }
        #
        #     /* Customize the arrow (triangle) */
        #     QComboBox::down-arrow {
        #         image: url(Deliverables/down-arrow.png); /* Optional: use a custom image for the arrow */
        #         width: 10px;
        #         height: 10px;
        #         margin-right: 10px; /* Moves the arrow more to the right */
        #     }
        #     QComboBox QAbstractItemView::item:disabled {
        #     color: rgb(0, 0, 0);
        #     }
        #     """)
            mixer_combobox.view().reset()

        # Reset Controls
            mixer_combobox.blockSignals(True)
            slider.blockSignals(True)
            mixer_combobox.setCurrentIndex(0)
            slider.setValue(100)
            mixer_combobox.blockSignals(False)
            slider.blockSignals(False)
            # ft_widget.clear()
            self.img_FtComponent.clear()
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

    def update_sliders(self, value, index):
        print(f"SLIDER INDEX IN UPDATE_SLIDERS: {index}")
        self.slider_labels[index].setText(str(value))
        self.components_mixer.change_weights(value, index)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
