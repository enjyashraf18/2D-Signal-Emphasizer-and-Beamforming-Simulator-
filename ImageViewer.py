from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import cv2
import numpy as np
from scipy import fftpack

from FourierComponents import FourierComponents
import logging
logging.basicConfig(filemode="a", filename="Logging_Info.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)


class ImageViewer(QtCore.QObject):
    smallest_size = None
    instances = []

    def __init__(self, image_widget, ft_widget, combo_box, index, window, detect_first_time, img_FtComponent, ROI_rectangles):
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
        self.img_ft = None

        self.img_FtComponent = img_FtComponent
        self.ref_img_FtComponent = img_FtComponent
        self.detect_first_time = detect_first_time
        self.ROI_rectangles = ROI_rectangles
        self.adjusted_img = None
        self.brightness = 0
        self.contrast = 1.0
        self.last_mouse_pos = None
        self.original_image = None
        self.detect_load_img = False

    def eventFilter(self, obj, event):
        if obj == self.image_widget:  # Ensure it's the image widget
            if event.type() == QtCore.QEvent.MouseButtonDblClick:
                if event.button() == QtCore.Qt.LeftButton:
                    print("Image double-clicked!")
                    self.load_image()
                return True

            elif event.type() == QtCore.QEvent.MouseButtonPress:
                self.mousePressEvent(event)
            elif event.type() == QtCore.QEvent.MouseMove:
                self.mouseMoveEvent(event)
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                self.mouseReleaseEvent(event)
        return super().eventFilter(obj, event)

    def load_image(self):
        filename, _ = QFileDialog.getOpenFileName(self.image_widget, "Open Image File", "","Image Files (*.jpeg *.jpg *.png)")
        self.image_file_path = filename
        if self.image_file_path:
            if self.image_file_path.lower().endswith('.jpeg') or self.image_file_path.lower().endswith(
                    '.jpg') or self.image_file_path.lower().endswith('.png'):
                try:
                    self.detect_load_img = True
                    # self.ft_widget.clear()
                    self.img_FtComponent.clear()
                    self.img_FtComponent = self.ref_img_FtComponent
                    self.image_widget.clear()
                    # self.img_FtComponent = pg.ImageItem()
                    # self.ft_widget.addItem(self.img_FtComponent)
                    self.combo_box.setCurrentIndex(0)
                    self.image = cv2.imread(self.image_file_path)
                    # print("i have read the image ")

                    if self.image is not None:
                        # print("the image is not none")
                        if len(self.image.shape) == 3 :
                            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

                        self.fourier = FourierComponents(self.image, self.ft_widget, self.ROI_rectangles)
                        self.height, self.width = self.image.shape
                        self.size = (self.width, self.height)
                        print(F"the image size before resizing is {self.size}")
                        self.update_smallest_size()
                        self.notify_all_instances()
                        self.original_image = self.image.copy()
                        self.redisplay_image(self.image)
                        # print(f"i set the image")
                except Exception as e:
                    print(f"Error. Couldn't upload: {e}")

    def on_combo_box_changed(self):
        try:
            if self.main_window.components_mixer.thread.is_alive():
                self.main_window.components_mixer.thread.stop()
        except Exception as e:
            logging.error(f"Error fetching thread info: {e}")
        # print("iam here")
        if self.image is None:
            return
        selected_option = self.combo_box.currentText()
        print(f"selected_option: {selected_option}")
        logging.info(f"Selected component for image {self.index} is {selected_option}")
        if selected_option == "None":
            # print(f"Inside none on_combobox changed")
            logging.warning(f"No component is selected for image {self.index}.")
            self.img_FtComponent.clear()
            # self.ft_widget.clear()
            self.fourier.remove_rectangle()
            self.detect_load_img = True
            self.main_window.components_mixer.set_component_type_and_value(None, np.zeros(self.size),
                                                                           self.index, self.size)
            return
        # print(f"the selected option is {selected_option}")
        self.ft_component = self.fourier.get_selected_ft_components(selected_option)
        # print(f'the ft component return has shape of {self.ft_component.shape}')

        if self.ft_component is not None:
            try:
                if self.ft_component.ndim == 2:
                    self.img_FtComponent.setImage(self.ft_component)
                else:
                    print("Error: ft_component is not a 2D array.")
            except Exception as e:
                print(f"Error setting image: {e}")
                # height, width = ft_component.shape
                # bytes_per_line = width
                # q_image = QtGui.QImage(ft_component.data, width, height, bytes_per_line, QtGui.QImage.Format_Grayscale8)
                # pixmap = QPixmap.fromImage(q_image)
                # self.ft_widget.setPixmap(pixmap.scaled(
                #     self.ft_widget.size(),
                #     QtCore.Qt.KeepAspectRatio,
                #     QtCore.Qt.SmoothTransformation
                # ))
                # self.img_FtComponent.setImage(ft_component)

            if not self.detect_first_time or self.detect_load_img:
                self.detect_first_time = self.fourier.draw_rectangle(self.detect_first_time)
                self.detect_load_img = False

            # self.fourier.rect_boundries()
            component_to_send = self.calc_components(selected_option)
            try:
                self.main_window.components_mixer.set_component_type_and_value(selected_option, component_to_send,
                                                                               self.index, self.size)
            except Exception as e:
                print(f"Error in set_component_type_and_value: {e}")
                logging.error(f"Error in set_component_type_and_value: {e}")
            self.calc_components(selected_option)

    def redisplay_image(self, adjusted_img):
        if self.image is None:
            print("No image to display.")
            return
        try:
            self.image = adjusted_img
            q_image = QtGui.QImage(np.ascontiguousarray(self.image.data), self.size[0], self.size[1], self.size[0],
                                   QtGui.QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            self.image_widget.setPixmap(pixmap.scaled(
                self.image_widget.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            ))
        except Exception as e:
            print(f"Error in redisplay_image: {e}")

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
                instance.redisplay_image(self.image)

    def calc_components(self, selected_option):
        if self.image is None:
            return
        # Compute the Fourier Transform
        self.img_ft = fftpack.fft2(self.image)
        self.img_ft = fftpack.fftshift(self.img_ft)
        # Calculate components
        magnitude = np.abs(self.img_ft)
        phase = np.angle(self.img_ft)
        real_part = np.real(self.img_ft)
        imaginary_part = np.imag(self.img_ft)
        # print(f"imaginary from calc: {imaginary_part}")
        # print(f"phase from calc: {phase}")
        # print(f"real new: {real_part}")
        # print(f"magnitude new: {magnitude}")
        if selected_option == "FT Real":
            return real_part
        elif selected_option == "FT Imaginary":
            return imaginary_part
        elif selected_option == "FT Magnitude":
            return magnitude
        elif selected_option == "FT Phase":
            return phase

    def ajust_brightness_and_contrast(self):
        adjusted_img = cv2.convertScaleAbs(self.original_image, alpha=self.contrast, beta=self.brightness)
        self.reDisplay_image(adjusted_img)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()  # Save the initial mouse position

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos:
            print(f"here is current pos {event.pos()}")
            print(f"here is per pos {self.last_mouse_pos}")
            change = self.last_mouse_pos - event.pos()
            delta_x = -change.x()  # minus 3shan teb2a right to left (y3ni better direction)
            delta_y = change.y()
            print(f"here is delta y {delta_y}")
            print(f"here is delta x {delta_x}")

            # self.brightness += delta_y
            # self.contrast += delta_x
            self.brightness += change.y()
            self.contrast -= change.x() / 100.0
            self.contrast = max(0.1, min(3.0, self.contrast))
            print(f"here is b {self.brightness}")
            print(f"here is c {self.contrast}")

            self.ajust_brightness_and_contrast()

            self.last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None
