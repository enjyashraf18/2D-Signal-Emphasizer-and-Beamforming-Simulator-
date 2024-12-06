from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QHBoxLayout, QFileDialog, QPushButton, QSlider, QLabel,
                             QCheckBox, QComboBox)
import cv2
import numpy as np
from PyQt5.QtGui import QPixmap
class ImageViewer(QtCore.QObject):
    smallest_size = None
    instances = []
    def __init__(self, image_widget, ft_widget, combo_box):
        super().__init__()
        self.image_widget = image_widget
        self.combo_box = combo_box
        self.ft_component_dislayed = "selected none option"
        self.ft_widget = ft_widget
        self.combo_box.currentIndexChanged.connect(self.on_combo_box_changed)
        self.image = None
        self.size = None
        ImageViewer.instances.append(self)

    def eventFilter(self, obj, event):
        if obj == self.image_widget:  # Ensure it's the image widget
            if event.type() == QtCore.QEvent.MouseButtonDblClick:
                if event.button() == QtCore.Qt.LeftButton:
                    print("Image double-clicked!")
                    self.load_image()
                return True
        return super().eventFilter(obj, event)
    def load_image(self):
        filename, _ = QFileDialog.getOpenFileName(self.image_widget, "Open Image File", "","Image Files (*.jpeg *.jpg *.png)")

        print(f"iam after the image file path {filename}")
        self.image_file_path = filename
        print(f"the imag path is {self.image_file_path}")
        if self.image_file_path:
            if self.image_file_path.lower().endswith('.jpeg') or self.image_file_path.lower().endswith(
                    '.jpg') or self.image_file_path.lower().endswith('.png'):
                print("iam after the image file path")
                try:
                    self.ft_widget.clear()
                    self.image_widget.clear()
                    self.combo_box.setCurrentIndex(0)
                    self.image = cv2.imread(self.image_file_path)
                    print("i have read the image ")

                    if self.image is not None:
                        print("the image is not none")
                        if len(self.image.shape) == 3 :
                            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
                        self.fourier = fourierComponents(self.image)
                        self.height, self.width = self.image.shape
                        self.size = (self.width, self.height)
                        print(F"the image size before resizing is {self.size}")
                        self.update_smallest_size()
                        self.notify_all_instances()
                        self.reDisplay_image()
                        print(f"i set the image")


                except Exception as e:
                    print(f"Error. Couldn't upload: {e}")
    def on_combo_box_changed(self):
        print("iam here")
        if self.image is None :
            return
        selected_option = self.combo_box.currentText()
        if selected_option == "None selection" :
            self.ft_widget.clear()
            return
        print(f"the selected option is {selected_option}")
        ft_component = self.fourier.get_selected_ft_components(selected_option)
        print(f'the ft component return has shape of {ft_component.shape}')

        if ft_component is not None:
            height, width = ft_component.shape
            bytes_per_line = width
            q_image = QtGui.QImage(ft_component.data, width, height, bytes_per_line, QtGui.QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            self.ft_widget.setPixmap(pixmap.scaled(
                self.ft_widget.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            ))

    def reDisplay_image(self):
        if self.image is None:
            print("No image to display.")
            return
        try:
            q_image = QtGui.QImage(np.ascontiguousarray(self.image.data), self.size[0], self.size[1], self.size[0],
                                   QtGui.QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            self.image_widget.setPixmap(pixmap.scaled(
                self.image_widget.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            ))
        except Exception as e:
            print(f"Error in reDisplay_image: {e}")
    def update_smallest_size(self):
        if ImageViewer.smallest_size is None:
            ImageViewer.smallest_size = self.size
        else:
            if (self.size[0] < ImageViewer.smallest_size[0]) or (self.size[1] < ImageViewer.smallest_size[1]):
                ImageViewer.smallest_size = self.size

    def resize_to_smallest_image(self):
        if ImageViewer.smallest_size is not None:
            self.image = cv2.resize(self.image, ImageViewer.smallest_size, interpolation=cv2.INTER_AREA)
            self.size = ImageViewer.smallest_size
            print(f"after resizing is {self.size}")

    def notify_all_instances(self):
        for instance in ImageViewer.instances:
            if instance.image is not None:
                instance.resize_to_smallest_image()
                instance.reDisplay_image()


class fourierComponents(QtCore.QObject):
    def __init__(self, original_image):
        super().__init__()
        self.original_image = original_image
        self.fourier_shift = self.calculate_ft()
    def get_selected_ft_components(self, selected):
        try:
            print("iam here in the top of selected func call")
            if selected == "Ft Magnitude":
                return self.get_ft_magnitude()
            elif selected == "Ft phase":
                return self.get_ft_phase()
            elif selected == "Ft real":
                print("he select real")
                return self.get_ft_real()
            elif selected == "Ft imaginary":
                return self.get_ft_imaginary()

        except Exception as e:
            print(f"Error in getting FT components: {e}")



    def calculate_ft(self):
        if self.original_image.dtype != np.float32:
            self.original_image = np.float32(self.original_image)  # convert to 32-bit float to meet dft requ
        fourier = cv2.dft(self.original_image, flags=cv2.DFT_COMPLEX_OUTPUT)
        self.fourier_shift = np.fft.fftshift(fourier)
        return self.fourier_shift


    def get_ft_magnitude(self):
        magnitude = 20 * np.log(cv2.magnitude(self.fourier_shift[:, :, 0], self.fourier_shift[:, :, 1]) + 1)
        magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        return magnitude

    def get_ft_phase(self):
        phase = np.angle(self.fourier_shift[:, :, 0] + 1j * self.fourier_shift[:, :, 1])
        phase = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        return phase

    def get_ft_real(self):
        real = self.fourier_shift[:, :, 0]
        lower, upper = np.percentile(real, [2, 98])  # clip to remove outliers
        real_clipped = np.clip(real, lower, upper)
        real_normalized = cv2.normalize(real_clipped, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        return real_normalized

    def get_ft_imaginary(self):
        imaginary = self.fourier_shift[:, :, 1]
        lower, upper = np.percentile(imaginary, [2, 98])
        imaginary_clipped = np.clip(imaginary, lower, upper)
        imaginary_transformed = np.log(np.abs(imaginary_clipped) + 1)
        imaginary_normalized = cv2.normalize(imaginary_transformed, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

        return imaginary_normalized


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
            combo_box.addItem("None selection")
            combo_box.addItem("Ft Magnitude")
            combo_box.addItem("Ft phase")
            combo_box.addItem("Ft imaginary")
            combo_box.addItem("Ft real")
            v_layout.addWidget(combo_box)
    # add the veritcal to the horizontal
            self.image_ft_layout.addLayout(v_layout)

            #append/s
            self.image_widgets.append(image_widget)
            self.ft_widgets.append(ft_widget)
            self.combo_boxes.append(combo_box)

            image_events_handler = ImageViewer(image_widget, ft_widget, combo_box)
            self.image_event_handlers.append(image_events_handler)
            image_widget.installEventFilter(image_events_handler)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())