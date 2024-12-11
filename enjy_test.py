
from PyQt5 import QtCore, QtGui, QtWidgets, sip
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QHBoxLayout, QFileDialog, QPushButton, QSlider, QLabel,
                             QCheckBox, QComboBox, QWidget)
import cv2
import numpy as np
from PyQt5.QtGui import QPixmap
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PIL import Image, ImageEnhance


class imageAdjuster(QWidget):
    def __int__(self, image):
        super().__init__()
        self.image = image
        self.original_image = image
        self.brightness= 0
        self.contrast =1.0
        self.final_mouse_pos = None


    def mouse_press_event(self, event):
        if event.button()== Qt.LeftButton:
            self.final_mouse_pos = event.pos()

    def mouse_move_event(self, event):
        if self.final_mouse_pos:
            print(f"here is current pos {event.pos()}")
            print(f"here is per pos {self.final_mouse_pos}")
            change = self.final_mouse_pos - event.pos()
            delta_x = -change.x()  # minus 3shan teb2a right to left (y3ni better direction)
            delta_y = change.y()
            print(f"here is delta y {delta_y}")
            print(f"here is delta x {delta_x}")

            self.brightness += delta_y
            self.contrast += delta_x
            print(f"here is b {self.brightness}")
            print(f"here is c {self.contrast}")

            self.final_mouse_pos = event.pos()

    def mouse_release_event(self, event):
        if event.button() ==Qt.LeftButton:
            self.final_mouse_pos = None

    def adjust_brightness(self):
        brightness_enhancer = ImageEnhance.Brightness(self.image)
        self.image =brightness_enhancer.enhance(self.brightness)

    def adjust_contrast(self):
        contrast_enhancer = ImageEnhance.Contrast(self.image)
        self.image =contrast_enhancer.enhance(self.brightness)



class ImageViewer(QtCore.QObject):
    smallest_size = None
    instances = []
    def __init__(self, image_widget, ft_widget, combo_box, detect_first_time, img_FtComponent, ROI_rectangles):
        super().__init__()
        self.image_widget = image_widget
        self.combo_box = combo_box
        self.ft_component_dislayed = "selected none option"
        self.ft_widget = ft_widget
        self.img_FtComponent = img_FtComponent
        self.ref_img_FtComponent = img_FtComponent
        self.detect_first_time = detect_first_time
        self.ROI_rectangles = ROI_rectangles
        self.combo_box.currentIndexChanged.connect(self.on_combo_box_changed)
        self.image = None
        self.size = None
        self.adjusted_img = None
        self.brightness = 0
        self.contrast = 1.0
        self.last_mouse_pos = None
        self.original_image = None

        ImageViewer.instances.append(self)

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

        print(f"iam after the image file path {filename}")
        self.image_file_path = filename
        print(f"the imag path is {self.image_file_path}")
        if self.image_file_path:
            if self.image_file_path.lower().endswith('.jpeg') or self.image_file_path.lower().endswith(
                    '.jpg') or self.image_file_path.lower().endswith('.png'):
                print("iam after the image file path")
                try:
                    # self.ft_widget.clear()

                    self.img_FtComponent  = self.ref_img_FtComponent
                    self.image_widget.clear()
                    self.combo_box.setCurrentIndex(0)
                    self.image = cv2.imread(self.image_file_path)
                    print("i have read the image ")

                    if self.image is not None:
                        print("the image is not none")
                        if len(self.image.shape) == 3 :
                            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

                        self.fourier = fourierComponents(self.image, self.ft_widget, self.ROI_rectangles)
                        self.height, self.width = self.image.shape
                        self.size = (self.width, self.height)
                        print(F"the image size before resizing is {self.size}")
                        self.update_smallest_size()
                        self.notify_all_instances()
                        self.original_image = self.image.copy()
                        self.reDisplay_image(self.image)
                        print(f"i set the image")


                except Exception as e:
                    print(f"Error. Couldn't upload: {e}")
    def on_combo_box_changed(self):
        if not self.detect_first_time:
            print(f"first --> {self.combo_box.currentText()}")
        print("iam here")
        if self.image is None :
            return
        selected_option = self.combo_box.currentText()
        if selected_option == "None selection" :
            # self.ft_widget.clear()
            self.fourier.remove_rectangle()

            return
        print(f"the selected option is {selected_option}")
        ft_component = self.fourier.get_selected_ft_components(selected_option)
        print(f"hena ft_comp {ft_component}")
        print(f'the ft component return has shape of {ft_component.shape}')


        if ft_component is not None:
            try:
                if ft_component.ndim == 2:
                    self.img_FtComponent.setImage(ft_component)
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

            if not self.detect_first_time:
                self.detect_first_time = self.fourier.draw_rectangle(self.detect_first_time)

            # self.fourier.rect_boundries()


    def reDisplay_image(self, adjusted_img):
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
            print(f"Error in reDisplay_image: {e}")

    def ajust_brightness_and_contrast(self):
        adjusted_img = cv2.convertScaleAbs(self.original_image, alpha=self.contrast, beta=self.brightness)
        self.reDisplay_image(adjusted_img)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()  # Save the initial mouse position

    # def mouseMoveEvent(self, event):
    #     if self.last_mouse_pos:
    #         print(f"here is current pos {event.pos()}")
    #         print(f"here is per pos {self.last_mouse_pos}")
    #         delta =  self.last_mouse_pos -event.pos()
    #         print(f"here is delta y {delta.y()}")
    #         print(f"here is delta x {delta.x()}")
    #         self.brightness += delta.y()  # Vertical movement adjusts brightness
    #         self.contrast += delta.x() / 100.0  # Horizontal movement adjusts contrast
    #         self.contrast = max(0.1, min(3.0, self.contrast))  # Clamp contrast to [0.1, 3.0]
    #         print(f"here is b {self.brightness}")
    #         print(f"here is c {self.contrast}")
    #
    #         self.ajust_brightness_and_contrast()
    #         self.last_mouse_pos = event.pos()  # Update last position

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
                instance.reDisplay_image(self.image)


class fourierComponents(QtCore.QObject):
    def __init__(self, original_image, ft_widget, ROI_rectangles):
        super().__init__()
        self.original_image = original_image
        self.fourier_shift = self.calculate_ft()
        self.ft_widget = ft_widget


        self.final_mouse_pos = None
        self.roi = None
        self.x_start = None
        self.y_start = None
        self.x_end = None
        self.y_end = None
        self.ROI_rectangles= ROI_rectangles

        self.selected = None
        self.region_type = "inner"
        self.real_comp = None
        self.img_comp = None
        self.mag_comp = None
        self.phase_comp = None

    def get_selected_ft_components(self, selected):
        try:
            print("iam here in the top of selected func call")
            self.selected = selected
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


    def zero_out_component(self, new_comp):
        if self.region_type == "inner":
            new_comp[:self.x_start, :self.y_start] = 0
            new_comp[self.x_end:, self.y_end:] = 0
            return new_comp
        elif self.region_type == "outer":
            new_comp[self.x_start:self.x_end, self.y_start: self.y_end] = 0
            return new_comp



    def region_mixer_output(self):
        # if self.region_type == "inner":
        if self.selected == "Ft real":
            new_comp = self.real_comp.copy()
            self.zero_out_component(new_comp)

        elif self.selected == "Ft imaginary":
            new_comp = self.img_comp.copy()
            self.zero_out_component(new_comp)

        elif self.selected == "Ft Magnitude":
            new_comp = self.mag_comp.copy()
            self.zero_out_component(new_comp)

        elif self.selected == "Ft phase":
            new_comp = self.phase_comp.copy()
            self.zero_out_component(new_comp)




    def draw_rectangle(self, detect_first_time):
        if not detect_first_time:
            detect_first_time = True
        scale = 0.6
        roi_width = self.ft_widget.width()
        roi_height = self.ft_widget.height()

        roi_center_x = roi_width // 2
        roi_center_y = roi_height // 2
        pos_x = roi_center_x - roi_width /3
        pos_y = roi_center_y - roi_height /3
        # self.roi = pg.RectROI()

        self.roi = pg.RectROI(
            [pos_x, pos_y],
            [roi_width * scale, roi_height * scale],
            pen=pg.mkPen("b", width=2), resizable = True , movable=True, invertible= True, rotatable= False
        )

        self.roi.addScaleHandle([0, 0], [1, 1])
        # top right
        self.roi.addScaleHandle([1, 0], [0, 1])
        #bottom left
        self.roi.addScaleHandle([0, 1], [1, 0])
        #bottom right
        self.roi.addScaleHandle([1, 1], [0, 0])

        self.ft_widget.scene().addItem(self.roi)
        self.roi.sigRegionChanged.connect(self.rect_boundries)
        self.ROI_rectangles.append(self.roi)
        print(f"hena length el roi rects {len(self.ROI_rectangles)}")
        return detect_first_time

    def remove_rectangle(self):
        self.ft_widget.scene().removeItem(self.roi)
        self.roi =None

    def rect_boundries(self):
        if self.roi is None:
            return None
        pos = self.roi.pos()
        size = self.roi.size()
        self.x_start = int(pos[0])
        self.y_start = int(pos[1])
        self.x_end = int(pos[0] + size[0])
        self.y_end = int(pos[1] + size[1])
        for roi in self.ROI_rectangles:
            roi.setPos(pos)
            roi.setSize(size)
        print((self.x_start, self.x_end, self.y_start, self.y_end))
        return self.x_start, self.x_end,self.y_start, self.y_end



    # def mouse_press_event(self, event):
    #     if event.button()== Qt.LeftButton:
    #         self.rect_boundries()
    #
    #
    # def mouse_move_event(self, event):
    #     if self.final_mouse_pos:
    #         self.rect_boundries()
    #
    #
    # def mouse_release_event(self, event):
    #     if event.button() ==Qt.LeftButton:
    #         self.rect_boundries()





    def calculate_ft(self):
        if self.original_image.dtype != np.float32:
            self.original_image = np.float32(self.original_image)  # convert to 32-bit float to meet dft requ
        fourier = cv2.dft(self.original_image, flags=cv2.DFT_COMPLEX_OUTPUT)
        self.fourier_shift = np.fft.fftshift(fourier)
        return self.fourier_shift


    def get_ft_magnitude(self):
        magnitude = 20 * np.log(cv2.magnitude(self.fourier_shift[:, :, 0], self.fourier_shift[:, :, 1]) + 1)
        magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        self.mag_comp = magnitude
        return magnitude

    def get_ft_phase(self):
        phase = np.angle(self.fourier_shift[:, :, 0] + 1j * self.fourier_shift[:, :, 1])
        phase = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        self.phase_comp = phase
        return phase

    def get_ft_real(self):
        real = self.fourier_shift[:, :, 0]
        lower, upper = np.percentile(real, [2, 98])  # clip to remove outliers
        real_clipped = np.clip(real, lower, upper)
        real_normalized = cv2.normalize(real_clipped, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        self.real_comp = real_normalized
        return real_normalized

    def get_ft_imaginary(self):
        imaginary = self.fourier_shift[:, :, 1]
        lower, upper = np.percentile(imaginary, [2, 98])
        imaginary_clipped = np.clip(imaginary, lower, upper)
        imaginary_transformed = np.log(np.abs(imaginary_clipped) + 1)
        imaginary_normalized = cv2.normalize(imaginary_transformed, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        self.img_comp = imaginary_normalized

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
        self.ROI_rectangles = []

        for i in range(4):
            # Create 4 sets of widgets
            # vertical for each one
            v_layout = QtWidgets.QVBoxLayout()

            # image widget
            image_widget = QtWidgets.QLabel("Double-click me!")
            # image_widget.setObjectName(f"ImageWidget_{i}")
            image_widget.setAlignment(QtCore.Qt.AlignCenter)
            image_widget.setStyleSheet("background-color: black;")
            image_widget.setFixedSize(300, 200)
            v_layout.addWidget(image_widget)

            detect_first_time = False

            # ft  widget
            # ft_widget = QtWidgets.QLabel("Fourier Transform")
            # ft_widget.setStyleSheet("background-color: black;")
            # ft_widget.setFixedSize(300, 200)
            # ft_widget.setAlignment(QtCore.Qt.AlignCenter)
            # v_layout.addWidget(ft_widget)
            # ft_widget = pg.GraphicsLayoutWidget()
            # ft_img = pg.ImageItem()
            # ft_scene = pg.GraphicsScene()
            # ft_scene.addItem(ft_img)
            # ft_widget.setScene(ft_scene)
            # ft_widget.setFixedSize(300, 200)
            # v_layout.addWidget(ft_widget)

            # ft_widget = pg.GraphicsLayoutWidget()
            # ft_view = ft_widget.addViewBox()
            # # ft_view.setAspectLocked(True)
            # # ft_view.setMouseEnabled(x=False, y=False)
            # self.img_FtComponent = pg.ImageItem()
            # ft_view.addItem(self.img_FtComponent)
            # v_layout.addWidget(ft_widget)

            ft_widget = pg.GraphicsLayoutWidget()
            ft_view = ft_widget.addViewBox()
            self.img_FtComponent = pg.ImageItem()
            ft_view.addItem(self.img_FtComponent)
            ft_widget.setFixedSize(300, 200)
            v_layout.addWidget(ft_widget)
            self.image_event_handlers = []

            # combo box
            combo_box = QComboBox(self)
            combo_box.addItem("None selection")
            combo_box.addItem("Ft Magnitude")
            combo_box.addItem("Ft phase")
            combo_box.addItem("Ft imaginary")
            combo_box.addItem("Ft real")
            v_layout.addWidget(combo_box)
            # add the vertical to the horizontal
            self.image_ft_layout.addLayout(v_layout)

            #append/s
            self.image_widgets.append(image_widget)
            self.ft_widgets.append(ft_widget)
            self.combo_boxes.append(combo_box)

            image_events_handler = ImageViewer(image_widget, ft_widget, combo_box, detect_first_time, self.img_FtComponent, self.ROI_rectangles)
            self.image_event_handlers.append(image_events_handler)
            image_widget.installEventFilter(image_events_handler)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
