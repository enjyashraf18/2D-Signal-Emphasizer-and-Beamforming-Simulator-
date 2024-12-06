from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
import cv2
import numpy as np
from FourierComponents import FourierComponents


class ImageViewer(QtCore.QObject):
    smallest_size = None
    instances = []
    def __init__(self, image_widget, ft_widget, combo_box, index, window):
        super().__init__()
        self.image_widget = image_widget
        self.combo_box = combo_box
        self.ft_component_dislayed = "selected none option"
        self.ft_widget = ft_widget
        self.combo_box.currentIndexChanged.connect(self.on_combo_box_changed)
        self.image = None
        self.size = None
        ImageViewer.instances.append(self)
        # by Nada
        self.main_window = window
        self.index = index
        self.ft_component = None

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
                        self.fourier = FourierComponents(self.image)
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
        if self.image is None:
            return
        selected_option = self.combo_box.currentText()
        if selected_option == "None":
            self.ft_widget.clear()
            return
        print(f"the selected option is {selected_option}")
        self.ft_component = self.fourier.get_selected_ft_components(selected_option)
        print(f'the ft component return has shape of {self.ft_component.shape}')

        if self.ft_component is not None:
            height, width = self.ft_component.shape
            bytes_per_line = width
            q_image = QtGui.QImage(self.ft_component.data, width, height, bytes_per_line, QtGui.QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            self.ft_widget.setPixmap(pixmap.scaled(
                self.ft_widget.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            ))

            # print(f"Image {self.index}: {self.ft_component}")
            try:
                self.main_window.components_mixer.set_component_type_and_value(self.fourier.fourier_shift, selected_option, self.ft_component,
                                                                               self.index)
            except Exception as e:
                print(f"Error in set_component_type_and_value: {e}")

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

